"""
Atribución — Contrato de Atribución.

Define los límites, responsabilidades y nivel de autonomía
de cada agente. Es la base legal del producto.

Cumple con:
- Art. VIII de la Konstitution de Kronos
- EU AI Act Art. 12 (registro), 14 (supervisión), 22 (explicabilidad)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from atribucion import crypto


# ─────────────────────────────────────────────────────────────
# EXCEPCIONES
# ─────────────────────────────────────────────────────────────

class ContractViolation(Exception):
    """Se lanza cuando una acción viola el Contrato de Atribución."""
    pass


# ─────────────────────────────────────────────────────────────
# TIPOS Y CONSTANTES
# ─────────────────────────────────────────────────────────────

AutonomyLevel = Literal["supervisado", "semi-autonomo", "autonomo"]

VALID_AUTONOMY_LEVELS = ("supervisado", "semi-autonomo", "autonomo")

VALID_PROVIDERS = (
    "openai",
    "anthropic",
    "google",
    "meta",
    "mistral",
    "local",
    "otro",
)

# Colateral mínimo en KRN según nivel de autonomía
COLLATERAL_BY_AUTONOMY: dict[str, int] = {
    "supervisado": 0,
    "semi-autonomo": 2_000,
    "autonomo": 10_000,
}

# Límite de daño máximo en KRN según nivel de autonomía
LIABILITY_BY_AUTONOMY: dict[str, int] = {
    "supervisado": 5_000,
    "semi-autonomo": 10_000,
    "autonomo": 50_000,
}


# ─────────────────────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────────────────────

@dataclass
class Contract:
    """Contrato de Atribución firmado por agente, creador y operador."""

    id: str
    version: str
    agent_did: str
    creator_did: str
    operator_did: str
    autonomy_level: AutonomyLevel
    proveedor_modelo: str
    limite_dano_krn: int
    colateral_krn: int
    created_at: str
    hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.hash:
            self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Hash SHA-256 del contrato (sin el campo hash)."""
        payload = {
            "version": self.version,
            "agent_did": self.agent_did,
            "creator_did": self.creator_did,
            "operator_did": self.operator_did,
            "autonomy_level": self.autonomy_level,
            "proveedor_modelo": self.proveedor_modelo,
            "limite_dano_krn": self.limite_dano_krn,
            "colateral_krn": self.colateral_krn,
            "created_at": self.created_at,
        }
        return hashlib.sha256(crypto.canonical_bytes(payload)).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serializa el contrato a diccionario."""
        return {
            "id": self.id,
            "version": self.version,
            "agent_did": self.agent_did,
            "creator_did": self.creator_did,
            "operator_did": self.operator_did,
            "autonomy_level": self.autonomy_level,
            "proveedor_modelo": self.proveedor_modelo,
            "limite_dano_krn": self.limite_dano_krn,
            "colateral_krn": self.colateral_krn,
            "created_at": self.created_at,
            "hash": self.hash,
        }


# ─────────────────────────────────────────────────────────────
# CREACIÓN
# ─────────────────────────────────────────────────────────────

def create_default(
    *,
    agent_did: str,
    creator_did: str,
    operator_did: str,
    autonomy_level: AutonomyLevel,
    proveedor_modelo: str,
    version: str = "1.0.0",
) -> Contract:
    """
    Crea un Contrato de Atribución con valores por defecto
    según el nivel de autonomía del agente.

    Lanza ValueError si el nivel de autonomía o el proveedor
    no son válidos.
    """
    if autonomy_level not in VALID_AUTONOMY_LEVELS:
        raise ValueError(
            f"Nivel de autonomía no válido: {autonomy_level}. "
            f"Válidos: {VALID_AUTONOMY_LEVELS}"
        )

    if proveedor_modelo not in VALID_PROVIDERS:
        raise ValueError(
            f"Proveedor no válido: {proveedor_modelo}. "
            f"Válidos: {VALID_PROVIDERS}"
        )

    contract_id = "ctr_" + hashlib.sha256(
        crypto.canonical_bytes({
            "agent_did": agent_did,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    ).hexdigest()[:24]

    return Contract(
        id=contract_id,
        version=version,
        agent_did=agent_did,
        creator_did=creator_did,
        operator_did=operator_did,
        autonomy_level=autonomy_level,
        proveedor_modelo=proveedor_modelo,
        limite_dano_krn=LIABILITY_BY_AUTONOMY[autonomy_level],
        colateral_krn=COLLATERAL_BY_AUTONOMY[autonomy_level],
        created_at=datetime.now(timezone.utc).isoformat(),
    )


# ─────────────────────────────────────────────────────────────
# VALIDACIÓN DE ACCIONES
# ─────────────────────────────────────────────────────────────

def validate_action(contract: Contract, action: Any) -> None:
    """
    Valida que una acción cumple el Contrato de Atribución.

    Reglas:
    1. El nivel de autonomía de la acción debe coincidir
       con el del contrato.
    2. Autonomía 'supervisado' → requiere aprobación humana.
    3. Autonomía 'autonomo' → requiere razonamiento (Art. 22).
    4. La acción debe incluir 'input' y 'output'.

    Lanza ContractViolation si algo falla.
    """
    action_dict = (
        action.model_dump() if hasattr(action, "model_dump") else dict(action)
    )

    # Regla 1: nivel de autonomía coincide
    if action_dict.get("autonomy_level") != contract.autonomy_level:
        raise ContractViolation(
            f"Nivel de autonomía no coincide: "
            f"acción={action_dict.get('autonomy_level')}, "
            f"contrato={contract.autonomy_level}"
        )

    # Regla 2: supervisado requiere aprobación humana
    if contract.autonomy_level == "supervisado":
        if not action_dict.get("human_approval"):
            raise ContractViolation(
                "Autonomía 'supervisado' requiere aprobación humana "
                "(EU AI Act Art. 14)."
            )

    # Regla 3: autónomo requiere razonamiento
    if contract.autonomy_level == "autonomo":
        if not action_dict.get("reasoning"):
            raise ContractViolation(
                "Autonomía 'autonomo' requiere reasoning "
                "(EU AI Act Art. 22)."
            )

    # Regla 4: input y output obligatorios
    if "input" not in action_dict or "output" not in action_dict:
        raise ContractViolation(
            "La acción debe incluir 'input' y 'output'."
        )


# ─────────────────────────────────────────────────────────────
# PERSISTENCIA (stub)
# ─────────────────────────────────────────────────────────────

async def load(agent_did: str) -> Contract | None:
    """
    Carga el Contrato de Atribución de un agente.

    En producción consulta la base de datos del tenant.
    Placeholder: devuelve None (no hay persistencia aún).
    """
    return None