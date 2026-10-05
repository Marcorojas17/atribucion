"""
Atribución Engine — MADRE.

Orquestador multi-agente con:
- Memoria canónica compartida
- Handoff real entre agentes
- Contexto persistente
- Broadcasting + orquestación secuencial

Uso:
    madre = MADRE(session_id="proyecto-x")
    madre.register(MotoAgent("Codex", call_codex))
    madre.register(MotoAgent("Claude Code", call_claude))
    madre.register(MotoAgent("Gemini CLI", call_gemini))

    result = await madre.broadcast("Diseñen un endpoint de pagos")
    # Todos los agentes leen el mismo contexto y contribuyen.

    result = await madre.sequence(
        task="Refactorizar crypto.py",
        order=["Codex", "Claude Code", "Gemini CLI"],
    )
    # Handoff real: Codex propone → Claude refina → Gemini ejecuta.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from engine.orchestrator.canonical_memory import CanonicalMemory
from engine.orchestrator.handoff import Handoff, HandoffResult


AgentCallable = Callable[[str], Awaitable[str]]


# ─────────────────────────────────────────────────────────────
# AGENTE REGISTRADO
# ─────────────────────────────────────────────────────────────

@dataclass
class MotoAgent:
    """Agente registrado en MADRE."""

    name: str
    call: AgentCallable
    role: str = "general"
    capabilities: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────
# MADRE
# ─────────────────────────────────────────────────────────────

class MADRE:
    """Orquestador multi-agente con memoria canónica."""

    def __init__(self, session_id: str = "default") -> None:
        self.session_id = session_id
        self.memory = CanonicalMemory(session_id=session_id)
        self.agents: dict[str, MotoAgent] = {}
        self.handoffs: list[HandoffResult] = []

    # ─── REGISTRO ───────────────────────────────────────────────

    def register(self, agent: MotoAgent) -> None:
        """Registra un agente en MADRE."""
        self.agents[agent.name] = agent

    def unregister(self, name: str) -> None:
        self.agents.pop(name, None)

    # ─── BROADCAST ──────────────────────────────────────────────

    async def broadcast(self, user_message: str) -> dict[str, str]:
        """
        Envía un mensaje a todos los agentes en paralelo.

        Cada agente lee el contexto canónico y responde.
        Todas las respuestas se añaden a la memoria.
        """
        import asyncio

        self.memory.add("Usuario", user_message, role="user")
        context = self.memory.get_context()

        async def call_agent(agent: MotoAgent) -> tuple[str, str]:
            prompt = self._build_prompt(agent, context, user_message)
            try:
                response = await agent.call(prompt)
            except Exception as e:
                response = f"[ERROR] {e}"
            return (agent.name, response)

        results = await asyncio.gather(
            *[call_agent(a) for a in self.agents.values()],
            return_exceptions=False,
        )

        responses: dict[str, str] = {}
        for agent_name, response in results:
            self.memory.add(agent_name, response)
            responses[agent_name] = response

        return responses

    # ─── SECUENCIA (HANDOFF) ────────────────────────────────────

    async def sequence(
        self,
        task: str,
        order: list[str],
    ) -> dict[str, str]:
        """
        Ejecuta la tarea en secuencia, con handoff real.

        Cada agente recibe:
        - La tarea original.
        - Las respuestas de los agentes anteriores.
        - Su rol específico.
        """
        self.memory.add("Usuario", task, role="user")
        responses: dict[str, str] = {}
        previous_output = ""

        for agent_name in order:
            agent = self.agents.get(agent_name)
            if not agent:
                responses[agent_name] = f"[ERROR] Agente no registrado: {agent_name}"
                continue

            # Construir handoff si hay output previo
            handoff_context = ""
            if previous_output:
                handoff = Handoff(
                    from_agent=order[order.index(agent_name) - 1],
                    to_agent=agent_name,
                    reason="Continuar con la tarea en secuencia",
                    context={"previous_output": previous_output[:2000]},
                    expected_result=f"Mejorar/refinar para: {task}",
                )
                handoff_context = handoff.to_prompt()

            prompt = self._build_prompt(
                agent,
                self.memory.get_context(),
                f"{task}\n\n{handoff_context}" if handoff_context else task,
            )

            try:
                response = await agent.call(prompt)
            except Exception as e:
                response = f"[ERROR] {e}"

            self.memory.add(agent_name, response)
            responses[agent_name] = response
            previous_output = response

        return responses

    # ─── INTERNO ────────────────────────────────────────────────

    def _build_prompt(
        self,
        agent: MotoAgent,
        context: str,
        user_message: str,
    ) -> str:
        """Construye el prompt específico para un agente."""
        return (
            f"Eres {agent.name} (rol: {agent.role}).\n"
            f"Capacidades: {', '.join(agent.capabilities) or 'generales'}.\n\n"
            f"Contexto de la sala:\n{context}\n\n"
            f"Mensaje del usuario:\n{user_message}\n\n"
            f"Responde como {agent.name}."
        )

    # ─── INTROSPECCIÓN ──────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        """Resumen del estado de MADRE."""
        ok, errors = self.memory.verify_integrity()
        return {
            "session_id": self.session_id,
            "agents": list(self.agents.keys()),
            "messages": len(self.memory.messages),
            "handoffs": len(self.handoffs),
            "integrity_ok": ok,
            "integrity_errors": errors,
        }