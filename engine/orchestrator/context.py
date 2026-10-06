"""
Atribución Engine — Contexto de orquestación.

Construye el contexto que se pasa a cada agente en MADRE.
Incluye:
- Contexto canónico de la sala (últimos N mensajes).
- Contexto del agente específico (rol, capacidades).
- Contexto de tarea (objetivo, restricciones).
- Contexto de herramientas disponibles.
- Contexto de memoria (episódica, semántica, procedural).

Filosofía: cada agente recibe el mismo contexto base, pero
con un framing específico según su rol.

Uso:
    builder = ContextBuilder(agent_id="madre-001")
    ctx = builder.build(
        user_message="Diseñen pagos",
        agent=MotoAgent("Codex", role="arquitecto"),
        memory=canonical_memory,
        tools=["fetch_price", "execute_order"],
    )
    print(ctx.to_prompt())
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ─── MODELO ──────────────────────────────────────────────────

@dataclass
class AgentContext:
    """Contexto completo para un agente."""

    agent_name: str
    agent_role: str
    agent_capabilities: list[str]
    user_message: str
    conversation_context: str
    task_context: dict[str, Any]
    tools_available: list[str]
    memory_context: dict[str, Any]
    constraints: list[str]
    expected_output: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_prompt(self) -> str:
        """Convierte el contexto a prompt para LLM."""
        lines = [
            f"# Contexto para {self.agent_name}",
            "",
            f"**Rol:** {self.agent_role}",
        ]

        if self.agent_capabilities:
            lines.append(
                f"**Capacidades:** {', '.join(self.agent_capabilities)}"
            )

        lines.append("")
        lines.append("## Conversación previa")
        lines.append(self.conversation_context or "(sin conversación previa)")

        lines.append("")
        lines.append("## Mensaje del usuario")
        lines.append(self.user_message)

        if self.task_context:
            lines.append("")
            lines.append("## Contexto de tarea")
            for k, v in self.task_context.items():
                lines.append(f"- **{k}:** {v}")

        if self.tools_available:
            lines.append("")
            lines.append("## Herramientas disponibles")
            lines.append(", ".join(self.tools_available))

        if self.memory_context:
            lines.append("")
            lines.append("## Memoria relevante")
            for k, v in self.memory_context.items():
                if isinstance(v, list):
                    for item in v[:3]:
                        lines.append(f"- [{k}] {item}")
                else:
                    lines.append(f"- [{k}] {v}")

        if self.constraints:
            lines.append("")
            lines.append("## Restricciones")
            for c in self.constraints:
                lines.append(f"- {c}")

        lines.append("")
        lines.append("## Resultado esperado")
        lines.append(self.expected_output or "Respuesta como " + self.agent_name)

        return "\n".join(lines)


# ─── BUILDER ─────────────────────────────────────────────────

class ContextBuilder:
    """Constructor de contextos para agentes MADRE."""

    def __init__(
        self,
        session_id: str = "default",
        max_conversation_messages: int = 20,
        max_conversation_chars: int = 8000,
    ) -> None:
        self.session_id = session_id
        self.max_conversation_messages = max_conversation_messages
        self.max_conversation_chars = max_conversation_chars
        logger.info(
            "ContextBuilder listo (session=%s, max_msgs=%d)",
            session_id, max_conversation_messages,
        )

    # ─── BUILD ─────────────────────────────────────────────────

    def build(
        self,
        user_message: str,
        agent_name: str,
        agent_role: str = "general",
        agent_capabilities: list[str] | None = None,
        memory: Any | None = None,
        tools: list[str] | None = None,
        task_context: dict[str, Any] | None = None,
        constraints: list[str] | None = None,
        expected_output: str = "",
        episodic_memory: Any | None = None,
        semantic_memory: Any | None = None,
    ) -> AgentContext:
        """
        Construye el contexto completo para un agente.

        Cada parámetro tiene un valor por defecto sensato.
        """
        conversation = self._build_conversation_context(memory)
        memory_ctx = self._build_memory_context(
            episodic_memory, semantic_memory, user_message,
        )

        return AgentContext(
            agent_name=agent_name,
            agent_role=agent_role,
            agent_capabilities=agent_capabilities or [],
            user_message=user_message,
            conversation_context=conversation,
            task_context=task_context or {},
            tools_available=tools or [],
            memory_context=memory_ctx,
            constraints=constraints or self._default_constraints(),
            expected_output=expected_output,
        )

    # ─── CONVERSATION ──────────────────────────────────────────

    def _build_conversation_context(self, memory: Any | None) -> str:
        """Construye el contexto de la conversación previa."""
        if memory is None:
            return ""

        messages = getattr(memory, "messages", None)
        if not messages:
            return ""

        recent = messages[-self.max_conversation_messages:]

        lines: list[str] = []
        total_chars = 0

        for msg in recent:
            agent = getattr(msg, "agent", "?")
            content = getattr(msg, "content", "")

            line = f"[{agent}]: {content}"

            if total_chars + len(line) > self.max_conversation_chars:
                # Truncar
                remaining = self.max_conversation_chars - total_chars
                if remaining > 50:
                    lines.append(line[:remaining] + "...")
                break

            lines.append(line)
            total_chars += len(line)

        return "\n".join(lines)

    # ─── MEMORY ────────────────────────────────────────────────

    def _build_memory_context(
        self,
        episodic: Any | None,
        semantic: Any | None,
        query: str,
    ) -> dict[str, Any]:
        """Construye el contexto de memoria relevante."""
        ctx: dict[str, Any] = {}

        if episodic is not None:
            try:
                recent = episodic.get_recent(limit=3)
                if recent:
                    ctx["episodic"] = [
                        e.to_context_str() if hasattr(e, "to_context_str")
                        else str(e)[:200]
                        for e in recent
                    ]
            except Exception as e:
                logger.debug("Error extrayendo memoria episódica: %s", e)

        if semantic is not None:
            try:
                facts = semantic.search_facts(query, limit=5)
                if facts:
                    ctx["semantic_facts"] = [f.content for f in facts]
            except Exception as e:
                logger.debug("Error extrayendo memoria semántica: %s", e)

        return ctx

    # ─── DEFAULTS ──────────────────────────────────────────────

    def _default_constraints(self) -> list[str]:
        return [
            "Responde en el idioma del usuario.",
            "Sé específico y técnico.",
            "No inventes información.",
            "Si no sabes algo, dilo.",
        ]

    # ─── UTILITIES ─────────────────────────────────────────────

    def estimate_tokens(self, context: AgentContext) -> int:
        """
        Estima tokens aproximados del contexto.

        Regla: 1 token ≈ 4 caracteres en español/inglés.
        """
        prompt = context.to_prompt()
        return len(prompt) // 4

    def truncate_context(
        self,
        context: AgentContext,
        max_tokens: int = 4000,
    ) -> AgentContext:
        """Trunca el contexto si excede el límite de tokens."""
        prompt = context.to_prompt()
        estimated = len(prompt) // 4

        if estimated <= max_tokens:
            return context

        # Truncar conversación proporcionalmente
        excess_ratio = max_tokens / estimated
        new_max_chars = int(
            self.max_conversation_chars * excess_ratio * 0.9
        )

        return AgentContext(
            agent_name=context.agent_name,
            agent_role=context.agent_role,
            agent_capabilities=context.agent_capabilities,
            user_message=context.user_message,
            conversation_context=(
                context.conversation_context[:new_max_chars]
                + "..." if len(context.conversation_context) > new_max_chars
                else context.conversation_context
            ),
            task_context=context.task_context,
            tools_available=context.tools_available,
            memory_context=context.memory_context,
            constraints=context.constraints,
            expected_output=context.expected_output,
            timestamp=context.timestamp,
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "max_conversation_messages": self.max_conversation_messages,
            "max_conversation_chars": self.max_conversation_chars,
        }