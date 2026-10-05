"""
Tests del Contrato de Atribución.

Verifica:
- Creación con valores por defecto
- Validación de acciones
- Violaciones del contrato
"""

from dataclasses import dataclass
from typing import Any

import pytest

from atribucion import contract, did


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _make_dids() -> tuple[str, str, str]:
    return (
        did.create("kronos", "agent", {"name": "Test"}),
        did.create("kronos", "human", {"name": "Creator"}),
        did.create("kronos", "human", {"name": "Operator"}),
    )


@dataclass
class FakeAction:
    """Acción simulada para tests."""

    action: str = "test"
    input: dict[str, Any] = None  # type: ignore
    output: dict[str, Any] = None  # type: ignore
    autonomy_level: str = "semi-autonomo"
    reasoning: str | None = None
    human_approval: dict | None = None

    def __post_init__(self) -> None:
        if self.input is None:
            self.input = {}
        if self.output is None:
            self.output = {}

    def model_dump(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "input": self.input,
            "output": self.output,
            "autonomy_level": self.autonomy_level,
            "reasoning": self.reasoning,
            "human_approval": self.human_approval,
        }


# ─────────────────────────────────────────────────────────────
# CREACIÓN
# ─────────────────────────────────────────────────────────────

def test_create_default_semi_autonomo() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="semi-autonomo",
        proveedor_modelo="anthropic",
    )
    assert c.autonomy_level == "semi-autonomo"
    assert c.colateral_krn == 2_000
    assert c.limite_dano_krn == 10_000
    assert c.hash != ""


def test_create_default_autonomo() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="autonomo",
        proveedor_modelo="openai",
    )
    assert c.colateral_krn == 10_000
    assert c.limite_dano_krn == 50_000


def test_create_default_supervisado() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="supervisado",
        proveedor_modelo="local",
    )
    assert c.colateral_krn == 0
    assert c.limite_dano_krn == 5_000


def test_create_default_autonomia_invalida() -> None:
    agent, creator, operator = _make_dids()
    with pytest.raises(ValueError):
        contract.create_default(
            agent_did=agent,
            creator_did=creator,
            operator_did=operator,
            autonomy_level="superinteligente",  # type: ignore
            proveedor_modelo="otro",
        )


def test_create_default_proveedor_invalido() -> None:
    agent, creator, operator = _make_dids()
    with pytest.raises(ValueError):
        contract.create_default(
            agent_did=agent,
            creator_did=creator,
            operator_did=operator,
            autonomy_level="autonomo",
            proveedor_modelo="desconocido",
        )


# ─────────────────────────────────────────────────────────────
# VALIDACIÓN DE ACCIONES
# ─────────────────────────────────────────────────────────────

def test_validate_action_ok() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="semi-autonomo",
        proveedor_modelo="anthropic",
    )
    action = FakeAction(autonomy_level="semi-autonomo")
    contract.validate_action(c, action)  # no lanza


def test_validate_action_nivel_distinto() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="semi-autonomo",
        proveedor_modelo="anthropic",
    )
    action = FakeAction(autonomy_level="autonomo")
    with pytest.raises(contract.ContractViolation):
        contract.validate_action(c, action)


def test_validate_action_supervisado_sin_aprobacion() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="supervisado",
        proveedor_modelo="anthropic",
    )
    action = FakeAction(autonomy_level="supervisado", human_approval=None)
    with pytest.raises(contract.ContractViolation):
        contract.validate_action(c, action)


def test_validate_action_autonomo_sin_reasoning() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="autonomo",
        proveedor_modelo="openai",
    )
    action = FakeAction(autonomy_level="autonomo", reasoning=None)
    with pytest.raises(contract.ContractViolation):
        contract.validate_action(c, action)


def test_validate_action_autonomo_con_reasoning() -> None:
    agent, creator, operator = _make_dids()
    c = contract.create_default(
        agent_did=agent,
        creator_did=creator,
        operator_did=operator,
        autonomy_level="autonomo",
        proveedor_modelo="openai",
    )
    action = FakeAction(
        autonomy_level="autonomo",
        reasoning="Análisis completo",
    )
    contract.validate_action(c, action)  # no lanza