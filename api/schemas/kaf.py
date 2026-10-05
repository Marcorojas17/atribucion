"""Atribución — Esquemas de KAF."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class KAFLevel(BaseModel):
    """Un nivel del estándar KAF."""

    id: Literal["KAF-1", "KAF-2", "KAF-3", "KAF-4"]
    name: str
    description: str
    requires_iso_27001: bool
    requires_soc2: bool
    requires_pqc: bool


class KAFAssessRequest(BaseModel):
    """Solicitud de auditoría KAF."""

    agent_id: str = Field(..., pattern=r"^agt_[a-fA-F0-9]+$")


class KAFAssessResponse(BaseModel):
    """Resultado de la auditoría KAF."""

    agent_id: str
    level_achieved: Literal["KAF-1", "KAF-2", "KAF-3", "KAF-4", "none"]
    controls_passed: int
    controls_total: int
    timestamp: str


class KAFVerifyResponse(BaseModel):
    """Verificación de un certificado KAF."""

    certificate_id: str
    agent_id: str
    level: str
    status: Literal["válido", "inválido", "revocado", "expirado"]
    issued_at: str
    expires_at: str


class KAFControlResult(BaseModel):
    """Resultado de un control individual."""

    control_id: str
    name: str
    passed: bool
    severity: Literal["info", "low", "medium", "high", "critical"]
    auto_auditable: bool
    evidence: str = ""