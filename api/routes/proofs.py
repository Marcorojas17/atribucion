"""
Atribución — Endpoint de verificación de certificados.

GET /v1/proofs/{certificate_id}

Permite a cualquiera (sin autenticación) verificar la autenticidad
de un certificado emitido por Atribución.

Devuelve:
- Estado del certificado (válido / inválido / revocado)
- Datos públicos de la acción
- Prueba criptográfica (hashes, anclajes, sellos)
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field


router = APIRouter(prefix="/v1", tags=["proofs"])


# ─────────────────────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────────────────────

class ProofResponse(BaseModel):
    """Prueba pública de un certificado."""

    certificate_id: str = Field(..., description="ID del certificado.")
    status: str = Field(
        ...,
        description="Estado: válido | inválido | revocado | no_encontrado.",
    )
    issued_at: datetime = Field(..., description="Fecha de emisión.")
    agent_did: str = Field(..., description="DID del agente emisor.")
    action: str = Field(..., description="Nombre de la acción registrada.")
    autonomy_level: str = Field(..., description="Nivel de autonomía.")
    hashes: dict[str, str] = Field(
        ...,
        description="Hashes del payload (sha256 + sha3).",
    )
    anchor: dict[str, str] = Field(
        ...,
        description="Anclaje a Ethereum (tx_hash + network).",
    )
    timestamp: dict[str, str] = Field(
        ...,
        description="Sello de tiempo RFC 3161 (authority + sealed_at).",
    )
    verification_url: str = Field(..., description="URL canónica de verificación.")


# ─────────────────────────────────────────────────────────────
# ENDPOINT
# ─────────────────────────────────────────────────────────────

@router.get(
    "/proofs/{certificate_id}",
    response_model=ProofResponse,
    summary="Verificar un certificado",
    description=(
        "Verificación pública de un certificado. No requiere autenticación. "
        "Cualquiera puede consultar si un certificado es válido."
    ),
)
async def get_proof(certificate_id: str) -> ProofResponse:
    """
    Devuelve la prueba pública de un certificado.

    En producción, consulta la base de datos.
    Por ahora, devuelve datos determinísticos derivados del ID.
    """
    if not certificate_id.startswith("cert_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="certificate_id inválido. Formato esperado: cert_<hex>.",
        )

    # Derivar datos determinísticos del ID (mock)
    h = hashlib.sha256(certificate_id.encode()).hexdigest()

    agent_did = f"did:kronos:agent:0x{h[:40]}"
    sha256 = hashlib.sha256(certificate_id.encode()).hexdigest()
    sha3 = hashlib.sha3_256(certificate_id.encode()).hexdigest()

    return ProofResponse(
        certificate_id=certificate_id,
        status="válido",
        issued_at=datetime.now(timezone.utc),
        agent_did=agent_did,
        action="action_recorded",
        autonomy_level="semi-autonomo",
        hashes={"sha256": sha256, "sha3": sha3},
        anchor={
            "tx_hash": "0x" + h,
            "network": "mock",
            "merkle_root": "0x" + h,
        },
        timestamp={
            "authority": "mock-tsa",
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "token": "0x" + h,
        },
        verification_url=f"https://atribucion.io/verify/{certificate_id}",
    )