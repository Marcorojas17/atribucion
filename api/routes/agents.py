"""
Atribución — Endpoint de registro de agentes.

POST /v1/agents

Registra un nuevo agente y crea su Contrato de Atribución.
Devuelve el agent_id que el cliente usará en cada acción.

Cumple con:
- Art. VIII de la Konstitution de Kronos
- EU AI Act Art. 12 (trazabilidad), 14 (supervisión)
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

# Añadir core/src al path
CORE_SRC = Path(__file__).resolve().parents[2] / "core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from atribucion import contract as contract_module  # noqa: E402
from atribucion import did as did_module  # noqa: E402

from api.middleware.auth import TenantContext, get_current_tenant  # noqa: E402
from api.schemas.agent import (  # noqa: E402
    AgentInfo,
    AgentRegistrationRequest,
    AgentRegistrationResponse,
)


router = APIRouter(prefix="/v1", tags=["agents"])


# ─────────────────────────────────────────────────────────────
# REGISTRO
# ─────────────────────────────────────────────────────────────

@router.post(
    "/agents",
    response_model=AgentRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo agente",
    description=(
        "Registra un agente y crea su Contrato de Atribución. "
        "Devuelve el agent_id que se usará en cada acción."
    ),
)
async def register_agent(
    body: AgentRegistrationRequest,
    tenant: TenantContext = Depends(get_current_tenant),
) -> AgentRegistrationResponse:
    """
    Registra un agente.

    Flujo:
    1. Validar API key + tenant.
    2. Crear DID del agente (W3C).
    3. Crear Contrato de Atribución.
    4. Calcular colateral requerido.
    5. Devolver agent_id, DID y contrato.
    """

    # ─── 1. Validar clave pública (formato) ─────────────────────
    if "BEGIN PUBLIC KEY" not in body.public_key_pem:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="public_key_pem debe estar en formato PEM.",
        )

    # ─── 2. Crear DID del agente ────────────────────────────────
    agent_did = did_module.create(
        method="kronos",
        type="agent",
        metadata={
            "name": body.name,
            "tenant_id": tenant.id,
            "operator_did": body.operator_did,
            "proveedor_modelo": body.proveedor_modelo,
        },
    )

    # ─── 3. Crear Contrato de Atribución ────────────────────────
    try:
        contrato = contract_module.create_default(
            agent_did=agent_did,
            creator_did=tenant.id,
            operator_did=body.operator_did,
            autonomy_level=body.autonomy_level,
            proveedor_modelo=body.proveedor_modelo,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    # ─── 4. Generar agent_id ────────────────────────────────────
    agent_id = f"agt_{uuid4().hex}"

    # ─── 5. Devolver respuesta ──────────────────────────────────
    return AgentRegistrationResponse(
        agent_id=agent_id,
        agent_did=agent_did,
        contract_id=contrato.id,
        contract_url=f"https://api.atribucion.io/v1/contracts/{contrato.id}",
        created_at=datetime.now(timezone.utc),
        autonomy_level=contrato.autonomy_level,
        colateral_krn=contrato.colateral_krn,
        limite_dano_krn=contrato.limite_dano_krn,
    )


# ─────────────────────────────────────────────────────────────
# CONSULTA
# ─────────────────────────────────────────────────────────────

@router.get(
    "/agents/{agent_id}",
    response_model=AgentInfo,
    summary="Obtener información de un agente",
)
async def get_agent(
    agent_id: str,
    tenant: TenantContext = Depends(get_current_tenant),
) -> AgentInfo:
    """
    Devuelve información pública del agente.

    En producción, consulta la base de datos del tenant.
    Por ahora, deriva los datos del agent_id de forma determinística.
    """
    if not agent_id.startswith("agt_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="agent_id inválido. Formato esperado: agt_<hex>.",
        )

    agent_did = "did:kronos:agent:0x" + hashlib.sha256(
        agent_id.encode()
    ).hexdigest()[:40]

    return AgentInfo(
        agent_id=agent_id,
        agent_did=agent_did,
        name="Agente registrado",
        autonomy_level="semi-autonomo",
        proveedor_modelo="otro",
        created_at=datetime.now(timezone.utc),
        active=True,
    )