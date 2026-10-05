"""
Atribución Engine — Máquina de estados del agente.

Define los estados canónicos de un agente y las transiciones válidas.
Cada transición se persiste en disco para auditoría (EU AI Act Art. 12).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────
# ESTADOS
# ─────────────────────────────────────────────────────────────

class AgentState(str, Enum):
    """Estados posibles de un agente."""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"          # esperando aprobación humana
    REFLECTING = "reflecting"
    ERROR = "error"
    COMPLETED = "completed"
    PAUSED = "paused"


# Transiciones válidas
VALID_TRANSITIONS: dict[AgentState, set[AgentState]] = {
    AgentState.IDLE: {AgentState.PLANNING, AgentState.PAUSED, AgentState.COMPLETED},
    AgentState.PLANNING: {AgentState.EXECUTING, AgentState.WAITING, AgentState.ERROR},
    AgentState.EXECUTING: {AgentState.REFLECTING, AgentState.WAITING, AgentState.ERROR, AgentState.COMPLETED},
    AgentState.WAITING: {AgentState.EXECUTING, AgentState.ERROR, AgentState.PAUSED},
    AgentState.REFLECTING: {AgentState.PLANNING, AgentState.COMPLETED, AgentState.ERROR},
    AgentState.ERROR: {AgentState.PLANNING, AgentState.PAUSED, AgentState.COMPLETED},
    AgentState.PAUSED: {AgentState.IDLE, AgentState.PLANNING, AgentState.COMPLETED},
    AgentState.COMPLETED: {AgentState.IDLE},
}


# ─────────────────────────────────────────────────────────────
# TRANSICIÓN
# ─────────────────────────────────────────────────────────────

@dataclass
class Transition:
    """Registro de una transición de estado."""

    from_state: str
    to_state: str
    reason: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_state,
            "to": self.to_state,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


# ─────────────────────────────────────────────────────────────
# MÁQUINA
# ─────────────────────────────────────────────────────────────

class StateMachine:
    """
    Máquina de estados con historial persistente.

    Uso:
        sm = StateMachine(agent_id="agt_123", state_dir=Path("~/.atribucion"))
        sm.transition(AgentState.PLANNING, reason="Tarea recibida")
        sm.transition(AgentState.EXECUTING, reason="Plan aprobado")
        print(sm.history)
    """

    def __init__(
        self,
        agent_id: str,
        initial: AgentState = AgentState.IDLE,
        state_dir: Path | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.state = initial
        self.history: list[Transition] = []
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "engine")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self.state_dir / f"agent-{agent_id}-states.jsonl"

    def can_transition(self, to: AgentState) -> bool:
        """Verifica si la transición es válida."""
        return to in VALID_TRANSITIONS.get(self.state, set())

    def transition(self, to: AgentState, reason: str = "") -> None:
        """
        Ejecuta una transición.

        Lanza ValueError si la transición no es válida.
        """
        if not self.can_transition(to):
            raise ValueError(
                f"Transición inválida: {self.state.value} → {to.value}. "
                f"Válidas: {[s.value for s in VALID_TRANSITIONS[self.state]]}"
            )

        transition = Transition(
            from_state=self.state.value,
            to_state=to.value,
            reason=reason,
        )
        self.history.append(transition)
        self._persist(transition)
        self.state = to

    def _persist(self, transition: Transition) -> None:
        """Persiste la transición en JSONL (append-only)."""
        with self._log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(transition.to_dict(), ensure_ascii=False) + "\n")

    def is_terminal(self) -> bool:
        """True si el agente terminó o está pausado."""
        return self.state in {AgentState.COMPLETED, AgentState.PAUSED}

    def reset(self) -> None:
        """Vuelve al estado IDLE (sin borrar historial)."""
        self.transition(AgentState.IDLE, reason="reset")