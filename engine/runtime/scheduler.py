"""
Atribución Engine — Scheduler.

Planifica tareas del agente y las ordena por prioridad,
deadline y dependencias.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any
from uuid import uuid4


# ─────────────────────────────────────────────────────────────
# PRIORIDAD
# ─────────────────────────────────────────────────────────────

class Priority(IntEnum):
    """Prioridad de una tarea. Mayor = más urgente."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


# ─────────────────────────────────────────────────────────────
# TAREA
# ─────────────────────────────────────────────────────────────

@dataclass
class Task:
    """Tarea planificada por el agente."""

    id: str
    name: str
    action: str
    params: dict[str, Any]
    priority: Priority = Priority.NORMAL
    depends_on: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    status: str = "pending"  # pending | running | done | failed | blocked
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "action": self.action,
            "params": self.params,
            "priority": int(self.priority),
            "depends_on": self.depends_on,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


# ─────────────────────────────────────────────────────────────
# SCHEDULER
# ─────────────────────────────────────────────────────────────

class Scheduler:
    """
    Planificador de tareas del agente.

    Ordena tareas por prioridad + dependencias resueltas.
    """

    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        """Añade una tarea al plan."""
        self.tasks[task.id] = task

    def create(
        self,
        name: str,
        action: str,
        params: dict[str, Any] | None = None,
        priority: Priority = Priority.NORMAL,
        depends_on: list[str] | None = None,
    ) -> Task:
        """Crea y añade una tarea."""
        task = Task(
            id=f"task_{uuid4().hex[:12]}",
            name=name,
            action=action,
            params=params or {},
            priority=priority,
            depends_on=depends_on or [],
        )
        self.add(task)
        return task

    def next_task(self) -> Task | None:
        """
        Devuelve la próxima tarea ejecutable.

        Criterio:
        - status == 'pending'
        - todas las dependencias están 'done'
        - mayor prioridad primero
        - si empate, la más antigua
        """
        ready = [
            t for t in self.tasks.values()
            if t.status == "pending" and self._deps_satisfied(t)
        ]
        if not ready:
            return None
        return sorted(
            ready,
            key=lambda t: (-int(t.priority), t.created_at),
        )[0]

    def _deps_satisfied(self, task: Task) -> bool:
        """Verifica que todas las dependencias estén completas."""
        return all(
            self.tasks.get(dep_id, Task("", "", "", {})).status == "done"
            for dep_id in task.depends_on
        )

    def mark_running(self, task_id: str) -> None:
        task = self.tasks[task_id]
        task.status = "running"
        task.started_at = datetime.now(timezone.utc).isoformat()

    def mark_done(self, task_id: str, result: Any = None) -> None:
        task = self.tasks[task_id]
        task.status = "done"
        task.result = result
        task.completed_at = datetime.now(timezone.utc).isoformat()

    def mark_failed(self, task_id: str, error: str) -> None:
        task = self.tasks[task_id]
        task.status = "failed"
        task.error = error
        task.completed_at = datetime.now(timezone.utc).isoformat()

    def is_complete(self) -> bool:
        """True si todas las tareas están done o failed."""
        return all(t.status in {"done", "failed"} for t in self.tasks.values())

    def snapshot(self) -> list[dict[str, Any]]:
        """Snapshot serializable del plan."""
        return [t.to_dict() for t in self.tasks.values()]