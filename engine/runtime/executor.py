"""
Atribución Engine — Executor.

Ejecuta tareas del scheduler, llamando a las acciones registradas.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from engine.runtime.scheduler import Scheduler, Task


ActionHandler = Callable[[dict[str, Any]], Awaitable[Any]]


@dataclass
class ExecutionResult:
    """Resultado de una ejecución completa."""

    tasks_executed: int
    tasks_failed: int
    duration_seconds: float
    results: dict[str, Any]


class Executor:
    """
    Ejecutor de tareas del scheduler.

    Uso:
        executor = Executor()
        executor.register("trade", handle_trade)
        executor.register("notify", handle_notify)

        result = await executor.run(scheduler)
    """

    def __init__(self) -> None:
        self._handlers: dict[str, ActionHandler] = {}

    def register(self, action: str, handler: ActionHandler) -> None:
        """Registra un handler para una acción."""
        self._handlers[action] = handler

    def unregister(self, action: str) -> None:
        self._handlers.pop(action, None)

    async def run(self, scheduler: Scheduler, max_iterations: int = 1000) -> ExecutionResult:
        """
        Ejecuta el plan hasta completarlo.

        Itera sobre `scheduler.next_task()` ejecutando cada handler.
        """
        import time

        start = time.time()
        executed = 0
        failed = 0
        results: dict[str, Any] = {}
        iterations = 0

        while not scheduler.is_complete() and iterations < max_iterations:
            iterations += 1
            task = scheduler.next_task()
            if task is None:
                # No hay tareas ejecutables (bloqueo o dependencia circular)
                break

            scheduler.mark_running(task.id)

            handler = self._handlers.get(task.action)
            if handler is None:
                scheduler.mark_failed(task.id, f"No handler para acción: {task.action}")
                failed += 1
                continue

            try:
                result = await handler(task.params)
                scheduler.mark_done(task.id, result)
                results[task.id] = result
                executed += 1
            except Exception as e:
                scheduler.mark_failed(task.id, str(e))
                failed += 1

        return ExecutionResult(
            tasks_executed=executed,
            tasks_failed=failed,
            duration_seconds=time.time() - start,
            results=results,
        )