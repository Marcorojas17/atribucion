"""
Atribución Engine — Agent.

Ciclo de vida completo de un agente:
1. Recibe un objetivo.
2. Planifica tareas (Scheduler).
3. Ejecuta (Executor).
4. Reflexiona.
5. Reporta resultado.

Cada paso transita por la StateMachine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine.runtime.executor import Executor, ExecutionResult
from engine.runtime.scheduler import Priority, Scheduler
from engine.runtime.state_machine import AgentState, StateMachine


# ─────────────────────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────────────────────

@dataclass
class AgentConfig:
    """Configuración del agente."""

    agent_id: str
    name: str
    autonomy_level: str = "semi-autonomo"
    proveedor_modelo: str = "local"
    max_iterations: int = 1000


@dataclass
class AgentResult:
    """Resultado de una ejecución del agente."""

    goal: str
    state: str
    tasks_executed: int
    tasks_failed: int
    duration_seconds: float
    results: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


# ─────────────────────────────────────────────────────────────
# AGENT
# ─────────────────────────────────────────────────────────────

class Agent:
    """
    Agente autónomo con ciclo de vida completo.

    Uso:
        agent = Agent(AgentConfig(agent_id="agt_1", name="Trader"))
        agent.executor.register("trade", handle_trade)

        result = await agent.run("Maximizar rendimiento del portafolio")
    """

    def __init__(
        self,
        config: AgentConfig,
        state_dir: Path | None = None,
    ) -> None:
        self.config = config
        self.state_machine = StateMachine(
            agent_id=config.agent_id,
            state_dir=state_dir,
        )
        self.scheduler = Scheduler()
        self.executor = Executor()

    # ─── CICLO DE VIDA ──────────────────────────────────────────

    async def run(self, goal: str) -> AgentResult:
        """Ejecuta el ciclo completo del agente."""
        import time

        start = time.time()

        try:
            # 1. IDLE → PLANNING
            self.state_machine.transition(
                AgentState.PLANNING,
                reason=f"Objetivo recibido: {goal}",
            )
            await self._plan(goal)

            # 2. PLANNING → EXECUTING
            self.state_machine.transition(
                AgentState.EXECUTING,
                reason=f"{len(self.scheduler.tasks)} tareas planificadas",
            )
            result: ExecutionResult = await self.executor.run(
                self.scheduler,
                max_iterations=self.config.max_iterations,
            )

            # 3. EXECUTING → REFLECTING
            self.state_machine.transition(
                AgentState.REFLECTING,
                reason="Ejecución terminada",
            )
            await self._reflect(result)

            # 4. REFLECTING → COMPLETED
            self.state_machine.transition(
                AgentState.COMPLETED,
                reason="Ciclo completado",
            )

            return AgentResult(
                goal=goal,
                state=self.state_machine.state.value,
                tasks_executed=result.tasks_executed,
                tasks_failed=result.tasks_failed,
                duration_seconds=time.time() - start,
                results=result.results,
            )

        except Exception as e:
            self.state_machine.transition(
                AgentState.ERROR,
                reason=f"Error: {e}",
            )
            return AgentResult(
                goal=goal,
                state=self.state_machine.state.value,
                tasks_executed=0,
                tasks_failed=0,
                duration_seconds=time.time() - start,
                error=str(e),
            )

    # ─── PLANIFICACIÓN ──────────────────────────────────────────

    async def _plan(self, goal: str) -> None:
        """
        Planifica tareas para un objetivo.

        En producción, esto consultaría un LLM. Aquí es un
        placeholder extensible.
        """
        # Placeholder: el agente concreto sobreescribe este método
        # o registra un planner específico.
        self.scheduler.create(
            name="Analizar objetivo",
            action="analyze",
            params={"goal": goal},
            priority=Priority.HIGH,
        )

    # ─── REFLEXIÓN ──────────────────────────────────────────────

    async def _reflect(self, result: ExecutionResult) -> None:
        """Reflexiona sobre el resultado (extensible)."""
        # Placeholder: el agente concreto sobreescribe.
        pass

    # ─── INTROSPECCIÓN ──────────────────────────────────────────

    def snapshot(self) -> dict[str, Any]:
        """Estado actual del agente (para API/dashboard)."""
        return {
            "agent_id": self.config.agent_id,
            "name": self.config.name,
            "state": self.state_machine.state.value,
            "history": [t.to_dict() for t in self.state_machine.history],
            "plan": self.scheduler.snapshot(),
        }