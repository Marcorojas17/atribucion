"""Tipos de respuesta del SDK."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ActionResponse:
    """Respuesta de registrar una acción."""

    certificate_id: str
    proof_url: str
    compliance: dict[str, dict[str, str]]
    anchor: dict[str, Any]
    timestamp_rfc3161: dict[str, Any]
    signature: dict[str, str]


@dataclass
class AgentRegistrationResponse:
    """Respuesta de registrar un agente."""

    agent_id: str
    agent_did: str
    contract_id: str
    contract_url: str
    created_at: datetime
    autonomy_level: str
    colateral_krn: int
    limite_dano_krn: int


@dataclass
class AgentInfo:
    """Información de un agente."""

    agent_id: str
    agent_did: str
    name: str
    autonomy_level: str
    proveedor_modelo: str
    created_at: datetime
    active: bool


@dataclass
class ProofResponse:
    """Prueba pública de un certificado."""

    certificate_id: str
    status: str
    issued_at: datetime
    agent_did: str
    action: str
    autonomy_level: str
    hashes: dict[str, str]
    anchor: dict[str, str]
    timestamp: dict[str, str]
    verification_url: str