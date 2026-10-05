"""
Atribución Engine — Handoff entre agentes.

Permite que un agente pase el control a otro con contexto real:
- Mensaje
- Estado
- Herramientas disponibles
- Objetivos pendientes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ─────────────────────────────────────────────────────────────
# HANDOFF
# ─────────────────────────────────────────────────────────────

@dataclass
class Handoff:
    """
    Contrato de traspaso entre dos agentes.

    Uso:
        h = Handoff(
            from_agent="Codex",
            to_agent="Claude Code",
            reason="Necesito refactorización arquitectónica",
            context={"file": "core/crypto.py", "issue": "acoplamiento"},
            expected_result="Código refactorizado + tests",
        )
    """

    from_agent: str
    to_agent: str
    reason: str
    context: dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""
    tools_available: list[str] = field(default_factory=list)
    deadline: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_agent,
            "to": self.to_agent,
            "reason": self.reason,
            "context": self.context,
            "expected_result": self.expected_result,
            "tools_available": self.tools_available,
            "deadline": self.deadline,
            "timestamp": self.timestamp,
        }

    def to_prompt(self) -> str:
        """Formato humano para incluir en el prompt del agente receptor."""
        lines = [
            f"🔀 Handoff de {self.from_agent} a {self.to_agent}",
            f"Razón: {self.reason}",
            f"Resultado esperado: {self.expected_result}",
        ]
        if self.context:
            lines.append("Contexto:")
            for k, v in self.context.items():
                lines.append(f"  - {k}: {v}")
        if self.tools_available:
            lines.append(f"Herramientas: {', '.join(self.tools_available)}")
        if self.deadline:
            lines.append(f"Deadline: {self.deadline}")
        return "\n".join(lines)


@dataclass
class HandoffResult:
    """Resultado de un handoff."""

    handoff: Handoff
    accepted: bool
    response: str = ""
    error: str | None = None
    completed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "handoff": self.handoff.to_dict(),
            "accepted": self.accepted,
            "response": self.response,
            "error": self.error,
            "completed_at": self.completed_at,
        }