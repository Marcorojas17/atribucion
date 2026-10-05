"""
Atribución — Endpoints de certificación KAF.

POST /v1/kaf/assess/{agent_id}   → auditar agente contra KAF
GET  /v1/kaf/verify/{cert_id}    → verificar certificado KAF (público)
GET  /v1/kaf/levels              → listar niveles KAF
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Añadir raíz al path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.middleware.auth import TenantContext, get_current_tenant  # noqa: E402
from kaf.certification.auditor import KAFAuditor  # noqa: E402


router = APIRouter(prefix="/v1/kaf", tags=["kaf"])


# ─────────────────────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────────────────────

class KAFLevel(BaseModel):
    id: str
    name: str
    description: str
    requires_iso_27001: bool
    requires_soc2: bool
    requires_pqc: bool


class KAFAssessResponse(BaseModel):
    agent_id: str
    level_achieved: str
    controls_passed: int
    controls_total: int
    timestamp: str


class KAFVerifyResponse(BaseModel):
    certificate_id: str
    agent_id: str
    level: str
    status: str
    issued_at: str
    expires_at: str


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.post(
    "/assess/{agent_id}",
    response_model=KAFAssessResponse,
    summary="Auditar un agente contra KAF",
)
async def assess_agent(
    agent_id: str,
    tenant: TenantContext = Depends(get_current_tenant),
) -> KAFAssessResponse:
    """
    Ejecuta la auditoría automática contra los 47 controles KAF.

    Devuelve el nivel alcanzado y el conteo de controles.
    """
    auditor = KAFAuditor()
    assessment = await auditor.assess(agent_id)

    return KAFAssessResponse(
        agent_id=assessment.agent_id,
        level_achieved=assessment.level_achieved,
        controls_passed=assessment.controls_passed,
        controls_total=assessment.controls_total,
        timestamp=assessment.timestamp,
    )


@router.get(
    "/verify/{certificate_id}",
    response_model=KAFVerifyResponse,
    summary="Verificar un certificado KAF (público)",
)
async def verify_kaf_certificate(certificate_id: str) -> KAFVerifyResponse:
    """
    Verificación pública de un certificado KAF.

    No requiere autenticación.
    """
    if not certificate_id.startswith("kaf_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="certificate_id inválido. Formato: kaf_<hex>.",
        )

    # Mock: en producción consulta la DB
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    return KAFVerifyResponse(
        certificate_id=certificate_id,
        agent_id="agt_mock",
        level="KAF-2",
        status="válido",
        issued_at=now.isoformat(),
        expires_at=now.isoformat(),
    )


@router.get(
    "/levels",
    response_model=list[KAFLevel],
    summary="Listar niveles KAF",
)
async def list_kaf_levels() -> list[KAFLevel]:
    """Devuelve los 4 niveles del estándar KAF."""
    return [
        KAFLevel(
            id="KAF-1",
            name="Verified",
            description="DID + firma + log inmutable",
            requires_iso_27001=False,
            requires_soc2=False,
            requires_pqc=False,
        ),
        KAFLevel(
            id="KAF-2",
            name="Compliant",
            description="+ Contrato de Atribución + anclaje Ethereum + TSA",
            requires_iso_27001=False,
            requires_soc2=False,
            requires_pqc=False,
        ),
        KAFLevel(
            id="KAF-3",
            name="Assured",
            description="+ ISO 27001 + SOC 2 Type II + HSM",
            requires_iso_27001=True,
            requires_soc2=True,
            requires_pqc=False,
        ),
        KAFLevel(
            id="KAF-4",
            name="Sovereign",
            description="+ PQC completo + NOM-151 + ISO 42001",
            requires_iso_27001=True,
            requires_soc2=True,
            requires_pqc=True,
        ),
    ]