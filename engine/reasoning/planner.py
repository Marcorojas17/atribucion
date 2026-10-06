"""
Atribución Engine — Planner.

Planificación jerárquica de objetivos en subtareas.

Descompone un goal complejo en un árbol de tareas ejecutables
con dependencias, prioridades y criterios de éxito.

Uso:
    planner = Planner()
    plan = planner.plan("Maximizar rendimiento del portafolio")
    print(plan.to_dict())
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, Callable
from uuid import uuid4


logger = logging.getLogger(__name__)


class PlanPriority(IntEnum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PlanStep:
    """Un paso del plan."""

    id: str
    description: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    priority: PlanPriority = PlanPriority.NORMAL
    depends_on: list[str] = field(default_factory=list)
    success_criteria: str = ""
    estimated_effort: str = "medium"
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["priority"] = int(self.priority)
        return d


@dataclass
class Plan:
    """Un plan completo."""

    id: str
    goal: str
    steps: list[PlanStep]
    created_at: str
    strategy: str = "hierarchical"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "strategy": self.strategy,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at,
            "metadata": self.metadata,
            "total_steps": len(self.steps),
            "critical_steps": sum(
                1 for s in self.steps if s.priority == PlanPriority.CRITICAL
            ),
        }

    def get_step(self, step_id: str) -> PlanStep | None:
        for s in self.steps:
            if s.id == step_id:
                return s
        return None

    def next_executable(self) -> PlanStep | None:
        """Próximo paso ejecutable (dependencias satisfechas)."""
        for step in self.steps:
            if step.status != "pending":
                continue
            deps_ok = all(
                (self.get_step(d) or PlanStep("", "", "", {})).status == "done"
                for d in step.depends_on
            )
            if deps_ok:
                return step
        return None


class Planner:
    """Planificador jerárquico."""

    def __init__(self) -> None:
        self.plans: dict[str, Plan] = {}
        logger.info("Planner listo")

    # ─── PLAN ──────────────────────────────────────────────────

    def plan(
        self,
        goal: str,
        metadata: dict[str, Any] | None = None,
        custom_steps: list[dict[str, Any]] | None = None,
    ) -> Plan:
        """
        Crea un plan para alcanzar un objetivo.

        Si custom_steps está definido, los usa. Si no, aplica
        una descomposición genérica en 4 fases.
        """
        if custom_steps:
            steps = self._build_from_custom(custom_steps)
        else:
            steps = self._default_decomposition(goal)

        plan = Plan(
            id=f"plan_{uuid4().hex[:12]}",
            goal=goal,
            steps=steps,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self.plans[plan.id] = plan
        logger.info("Plan creado: %s (%d pasos)", plan.id, len(steps))
        return plan

    def _default_decomposition(self, goal: str) -> list[PlanStep]:
        """Descomposición genérica en 4 fases."""
        analyze = PlanStep(
            id=f"step_{uuid4().hex[:8]}",
            description=f"Analizar objetivo: {goal}",
            action="analyze",
            priority=PlanPriority.HIGH,
            success_criteria="Objetivo descompuesto y comprendido",
        )
        plan = PlanStep(
            id=f"step_{uuid4().hex[:8]}",
            description="Planificar estrategia",
            action="plan",
            priority=PlanPriority.HIGH,
            depends_on=[analyze.id],
            success_criteria="Estrategia definida",
        )
        execute = PlanStep(
            id=f"step_{uuid4().hex[:8]}",
            description="Ejecutar estrategia",
            action="execute",
            priority=PlanPriority.CRITICAL,
            depends_on=[plan.id],
            success_criteria="Tareas ejecutadas",
        )
        verify = PlanStep(
            id=f"step_{uuid4().hex[:8]}",
            description="Verificar resultado",
            action="verify",
            priority=PlanPriority.NORMAL,
            depends_on=[execute.id],
            success_criteria="Resultado validado",
        )
        return [analyze, plan, execute, verify]

    def _build_from_custom(self, custom: list[dict[str, Any]]) -> list[PlanStep]:
        """Construye pasos desde definición custom."""
        steps = []
        for c in custom:
            steps.append(PlanStep(
                id=c.get("id") or f"step_{uuid4().hex[:8]}",
                description=c.get("description", ""),
                action=c.get("action", ""),
                params=c.get("params", {}),
                priority=PlanPriority(c.get("priority", 2)),
                depends_on=c.get("depends_on", []),
                success_criteria=c.get("success_criteria", ""),
                estimated_effort=c.get("estimated_effort", "medium"),
            ))
        return steps

    # ─── STATUS ────────────────────────────────────────────────

    def mark_done(self, plan_id: str, step_id: str) -> None:
        plan = self.plans.get(plan_id)
        if not plan:
            return
        step = plan.get_step(step_id)
        if step:
            step.status = "done"

    def mark_failed(self, plan_id: str, step_id: str) -> None:
        plan = self.plans.get(plan_id)
        if not plan:
            return
        step = plan.get_step(step_id)
        if step:
            step.status = "failed"

    def is_complete(self, plan_id: str) -> bool:
        plan = self.plans.get(plan_id)
        if not plan:
            return False
        return all(s.status in ("done", "failed") for s in plan.steps)

    # ─── INFO ──────────────────────────────────────────────────

    def get_plan(self, plan_id: str) -> Plan | None:
        return self.plans.get(plan_id)

    def list_plans(self) -> list[dict[str, Any]]:
        return [
            {
                "id": p.id,
                "goal": p.goal,
                "steps": len(p.steps),
                "created_at": p.created_at,
            }
            for p in self.plans.values()
        ]