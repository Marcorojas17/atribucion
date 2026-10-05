"""
Atribución — Esquemas Pydantic para registro de agentes.

Define el contrato HTTP del endpoint de registro:

    POST /v1/agents

Un cliente llama a este endpoint una vez por agente, y recibe
el agent_id y el Contrato de Atribución asociado.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# REQUEST
# ─────────────────────────────────────────────────────────────

class AgentRegistrationRequest(BaseModel):
    """Payload de registro de un nuevo agente."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Nombre del agente (ej. 'MiAgenteTrading').",
    )
    autonomy_level: Literal["supervisado", "semi-autonomo", "autonomo"] = Field(
        ...,
        description="Nivel de autonomía del agente.",
    )
    proveedor_modelo: Literal[
        "openai", "anthropic", "google", "meta", "mistral", "local", "otro"
    ] = Field(
        ...,
        description="Proveedor del modelo LLM subyacente.",
    )
    operator_did: str = Field(
        ...,
        pattern=r"^did:kronos:human:0x[a-fA-F0-9]{40}$",
        description="DID del humano que operará el agente.",
    )
    public_key_pem: str = Field(
        ...,
        min_length=100,
        description="Clave pública PEM del agente para verificar firmas.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata adicional (versión, descripción, etc.).",
    )


# ─────────────────────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────────────────────

class AgentRegistrationResponse(BaseModel):
    """Respuesta del registro de un agente."""

    agent_id: str = Field(..., description="ID único del agente.")
    agent_did: str = Field(..., description="DID del agente (W3C).")
    contract_id: str = Field(..., description="ID del Contrato de Atribución.")
    contract_url: str = Field(..., description="URL del contrato firmado.")
    created_at: datetime = Field(..., description="Fecha de registro.")
    autonomy_level: str = Field(..., description="Nivel de autonomía.")
    colateral_krn: int = Field(..., description="Colateral depositado en KRN.")
    limite_dano_krn: int = Field(..., description="Límite de daño en KRN.")


class AgentInfo(BaseModel):
    """Información pública de un agente."""

    agent_id: str
    agent_did: str
    name: str
    autonomy_level: str
    proveedor_modelo: str
    created_at: datetime
    active: bool