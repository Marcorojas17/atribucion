"""Tests del executor de tareas."""

import pytest

from engine.runtime.executor import Executor
from engine.runtime.scheduler import Scheduler


@pytest.mark.asyncio
async def test_executor_runs_simple_task():
    s = Scheduler()
    e = Executor()

    async def handler(params):
        return "resultado"

    e.register("test", handler)
    s.create("Tarea", "test")

    result = await e.run(s)
    assert result.tasks_executed == 1
    assert result.tasks_failed == 0


@pytest.mark.asyncio
async def test_executor_fails_without_handler():
    s = Scheduler()
    e = Executor()
    s.create("Tarea", "unknown")
    result = await e.run(s)
    assert result.tasks_failed == 1


@pytest.mark.asyncio
async def test_executor_handles_multiple_tasks():
    s = Scheduler()
    e = Executor()

    async def handler(params):
        return params.get("v", 0)

    e.register("test", handler)
    s.create("T1", "test", params={"v": 1})
    s.create("T2", "test", params={"v": 2})

    result = await e.run(s)
    assert result.tasks_executed == 2


@pytest.mark.asyncio
async def test_executor_handles_exception():
    s = Scheduler()
    e = Executor()

    async def handler(params):
        raise RuntimeError("boom")

    e.register("test", handler)
    s.create("Tarea", "test")

    result = await e.run(s)
    assert result.tasks_failed == 1
