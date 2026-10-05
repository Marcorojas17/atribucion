"""
Atribución — Onboarding del cliente.

Flujo completo en 4 pasos:
1. Crear cuenta (email + DID).
2. Elegir plan (free / pro / bank).
3. Registrar primer agente (DID + Contrato de Atribución).
4. Emitir API key y completar.

Cada paso es idempotente. El cliente puede reanudar donde lo dejó.
"""

from __future__ import annotations

import hashlib
import secrets
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

# Añadir core/src al path
CORE_SRC = Path(__file__).resolve().parents[2] / "core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from atribucion import did as did_module  # noqa: E402
from atribucion.billing.plans import PLANS, get_plan  # noqa: E402


# ─────────────────────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────────────────────

class OnboardingStep(str, Enum):
    ACCOUNT = "account"
    PLAN = "plan"
    FIRST_AGENT = "first_agent"
    COMPLETE = "complete"


@dataclass
class Tenant:
    id: str
    email: str
    did: str
    plan_id: str
    created_at: str
    onboarding_step: str
    api_key: str | None = None
    api_key_created_at: str | None = None
    metadata: dict = field(default_factory=dict)


class StartOnboardingRequest(BaseModel):
    email: EmailStr
    company_name: str = Field(..., min_length=1, max_length=120)
    country: str = Field(..., min_length=2, max_length=2)


class StartOnboardingResponse(BaseModel):
    tenant_id: str
    did: str
    next_step: str


class RegisterAgentRequest(BaseModel):
    tenant_id: str
    agent_name: str = Field(..., min_length=1, max_length=120)
    autonomy_level: Literal["supervisado", "semi-autonomo", "autonomo"]
    operator_did: str
    proveedor_modelo: Literal[
        "openai", "anthropic", "google", "meta", "mistral", "local", "otro"
    ]


class RegisterAgentResponse(BaseModel):
    agent_id: str
    agent_did: str
    contract_id: str
    contract_url: str
    api_key: str
    next_step: str


# ─────────────────────────────────────────────────────────────
# PASO 1 — CREAR CUENTA
# ─────────────────────────────────────────────────────────────

async def start_onboarding(
    req: StartOnboardingRequest,
) -> StartOnboardingResponse:
    """Crea un tenant (cuenta) y genera su DID."""
    tenant_id = f"tnt_{secrets.token_hex(12)}"

    tenant_did = did_module.create(
        method="kronos",
        type="org",
        metadata={
            "email": str(req.email),
            "company_name": req.company_name,
            "country": req.country,
        },
    )

    tenant = Tenant(
        id=tenant_id,
        email=str(req.email),
        did=tenant_did,
        plan_id="free",
        created_at=datetime.now(timezone.utc).isoformat(),
        onboarding_step=OnboardingStep.PLAN.value,
        metadata={"company_name": req.company_name, "country": req.country},
    )

    await _save_tenant(tenant)

    return StartOnboardingResponse(
        tenant_id=tenant_id,
        did=tenant_did,
        next_step=OnboardingStep.PLAN.value,
    )


# ─────────────────────────────────────────────────────────────
# PASO 2 — ELEGIR PLAN
# ─────────────────────────────────────────────────────────────

async def choose_plan(
    *,
    tenant_id: str,
    plan_id: str,
) -> dict[str, str | None]:
    """
    Asigna un plan al tenant.

    - Free: activación inmediata.
    - Pro/Bank: se genera link de Mercado Pago.
    """
    tenant = await _load_tenant(tenant_id)
    if not tenant:
        raise ValueError(f"Tenant {tenant_id} no encontrado.")

    plan = get_plan(plan_id)

    if plan.is_free:
        tenant.plan_id = "free"
        tenant.onboarding_step = OnboardingStep.FIRST_AGENT.value
        await _save_tenant(tenant)
        return {
            "checkout_url": None,
            "next_step": OnboardingStep.FIRST_AGENT.value,
        }

    # Plan de pago: crear preferencia
    from atribucion.billing.mercadopago import MercadoPagoClient

    async with MercadoPagoClient() as mp:
        checkout = await mp.create_preference(
            plan=plan,
            tenant_id=tenant_id,
            customer_email=tenant.email,
            back_urls={
                "success": "https://atribucion.io/checkout/success",
                "failure": "https://atribucion.io/checkout/failure",
                "pending": "https://atribucion.io/checkout/pending",
            },
            notification_url="https://api.atribucion.io/v1/payments/webhook",
        )

    tenant.plan_id = plan_id
    tenant.onboarding_step = OnboardingStep.FIRST_AGENT.value
    await _save_tenant(tenant)

    return {
        "checkout_url": checkout.init_point,
        "preference_id": checkout.preference_id,
        "next_step": OnboardingStep.FIRST_AGENT.value,
    }


# ─────────────────────────────────────────────────────────────
# PASO 3 — REGISTRAR AGENTE
# ─────────────────────────────────────────────────────────────

async def register_first_agent(
    req: RegisterAgentRequest,
) -> RegisterAgentResponse:
    """Registra el primer agente del cliente."""
    from atribucion import contract as contract_module

    tenant = await _load_tenant(req.tenant_id)
    if not tenant:
        raise ValueError(f"Tenant {req.tenant_id} no encontrado.")

    plan = get_plan(tenant.plan_id)
    current_agents = await _count_agents(req.tenant_id)
    if current_agents >= plan.agent_limit:
        raise ValueError(
            f"Tu plan {plan.name} permite máximo {plan.agent_limit} agentes. "
            "Actualiza a Pro para añadir más."
        )

    agent_did = did_module.create(
        method="kronos",
        type="agent",
        metadata={
            "agent_name": req.agent_name,
            "tenant_id": tenant.id,
            "operator_did": req.operator_did,
        },
    )

    contrato = contract_module.create_default(
        agent_did=agent_did,
        creator_did=tenant.did,
        operator_did=req.operator_did,
        autonomy_level=req.autonomy_level,
        proveedor_modelo=req.proveedor_modelo,
    )

    agent_id = f"agt_{secrets.token_hex(12)}"
    await _save_agent(
        agent_id=agent_id,
        agent_did=agent_did,
        tenant_id=tenant.id,
        contract_id=contrato.id,
    )

    api_key = _generate_api_key()
    tenant.api_key = api_key
    tenant.api_key_created_at = datetime.now(timezone.utc).isoformat()
    tenant.onboarding_step = OnboardingStep.COMPLETE.value
    await _save_tenant(tenant)

    return RegisterAgentResponse(
        agent_id=agent_id,
        agent_did=agent_did,
        contract_id=contrato.id,
        contract_url=f"https://api.atribucion.io/v1/contracts/{contrato.id}",
        api_key=api_key,
        next_step=OnboardingStep.COMPLETE.value,
    )


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _generate_api_key() -> str:
    """Genera API key formato ak_live_<64_hex>."""
    return f"ak_live_{secrets.token_hex(32)}"


async def _save_tenant(tenant: Tenant) -> None:
    from atribucion.dashboard.repository import TenantRepository
    repo = TenantRepository()
    await repo.save(tenant)


async def _load_tenant(tenant_id: str) -> Tenant | None:
    from atribucion.dashboard.repository import TenantRepository
    repo = TenantRepository()
    return await repo.get(tenant_id)


async def _count_agents(tenant_id: str) -> int:
    from atribucion.dashboard.repository import AgentRepository
    repo = AgentRepository()
    return await repo.count_by_tenant(tenant_id)


async def _save_agent(
    agent_id: str,
    agent_did: str,
    tenant_id: str,
    contract_id: str,
) -> None:
    from atribucion.dashboard.repository import AgentRepository
    repo = AgentRepository()
    await repo.save({
        "agent_id": agent_id,
        "agent_did": agent_did,
        "tenant_id": tenant_id,
        "contract_id": contract_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })