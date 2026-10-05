"""
Atribución — Esquemas Pydantic del endpoint de acciones.

Define el contrato HTTP del producto:
- ActionRequest  → lo que envía el cliente
- ActionResponse → lo que recibe el cliente

Cumple con EU AI Act Art. 12, 14, 22.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────────────────────
# REQUEST
# ─────────────────────────────────────────────────────────────

class HumanApproval(BaseModel):
    """Aprobación humana firmada (EU AI Act Art. 14)."""

    approver_did: str = Field(
        ...,
        pattern=r"^did:kronos:human:0x[a-fA-F0-9]{40}$",
        description="DID del humano que aprobó.",
    )
    approved_at: datetime = Field(..., description="Timestamp de la aprobación.")
    signature: str = Field(
        ...,
        pattern=r"^0x[a-fA-F0-9]+$",
        description="Firma del humano sobre el payload.",
    )


class ActionRequest(BaseModel):
    """Payload que envía el cliente en cada acción del agente."""

    action: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Identificador de la acción (ej. 'trade_executed').",
    )
    input: dict[str, Any] = Field(
        ...,
        description="Input de la acción (parámetros de entrada).",
    )
    output: dict[str, Any] = Field(
        ...,
        description="Output de la acción (resultado producido).",
    )
    reasoning: str | None = Field(
        default=None,
        max_length=4000,
        description="Razonamiento del agente (obligatorio si autonomy=autonomo).",
    )
    autonomy_level: Literal["supervisado", "semi-autonomo", "autonomo"] = Field(
        ...,
        description="Nivel de autonomía de la acción.",
    )
    human_approval: HumanApproval | None = Field(
        default=None,
        description="Aprobación humana (obligatorio si autonomy=supervisado).",
    )

    @field_validator("reasoning")
    @classmethod
    def reasoning_required_for_autonomous(cls, v: str | None, info: Any) -> str | None:
        """EU AI Act Art. 22: explicabilidad obligatoria si es autónomo."""
        autonomy = info.data.get("autonomy_level")
        if autonomy == "autonomo" and not v:
            raise ValueError(
                "reasoning es obligatorio cuando autonomy_level='autonomo' "
                "(EU AI Act Art. 22)."
            )
        return v


# ─────────────────────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────────────────────

class ComplianceStatus(BaseModel):
    """Estado de compliance con EU AI Act."""

    article_12: Literal["compliant", "not_applicable"] = "compliant"
    article_14: Literal["compliant", "not_applicable"] = "compliant"
    article_22: Literal["compliant", "not_applicable"] = "compliant"


class AnchorInfo(BaseModel):
    """Información del anclaje a Ethereum."""

    tx_hash: str
    block: int
    network: str
    merkle_root: str


class TimestampInfo(BaseModel):
    """Información del sellado RFC 3161."""

    authority: str
    sealed_at: str
    token: str


class SignatureInfo(BaseModel):
    """Firmas de la credencial (clásica + post-cuántica)."""

    classic: str
    pqc: str


class ActionResponse(BaseModel):
    """Respuesta del endpoint. Es el certificado de la acción."""

    certificate_id: str = Field(..., description="ID único del certificado.")
    proof_url: str = Field(..., description="URL pública para verificar el certificado.")
    compliance: dict[str, ComplianceStatus] = Field(
        ...,
        description="Estado de compliance por regulación.",
    )
    anchor: AnchorInfo = Field(..., description="Anclaje a Ethereum.")
    timestamp_rfc3161: TimestampInfo = Field(
        ...,
        description="Sello de tiempo RFC 3161.",
    )
    signature: SignatureInfo = Field(..., description="Firmas de la credencial.")