"""Tests del ciclo de vida del agente."""

import pytest

from engine.runtime.agent import Agent, AgentConfig


@pytest.mark.asyncio
async def test_agent_runs_cycle():
    config = AgentConfig(agent_id="agt_test", name="TestAgent")
    agent = Agent(config)

    async def analyze(params):
        return {"analyzed": True}

    agent.executor.register("analyze", analyze)
    agent.executor.register("plan", analyze)
    agent.executor.register("execute", analyze)
    agent.executor.register("verify", analyze)

    result = await agent.run("Test goal")
    assert result.goal == "Test goal"
    assert result.state == "completed"
    assert result.tasks_executed >= 1


@pytest.mark.asyncio
async def test_agent_snapshot():
    config = AgentConfig(agent_id="agt_snap", name="Snapshot")
    agent = Agent(config)
    snapshot = agent.snapshot()
    assert snapshot["agent_id"] == "agt_snap"
    assert snapshot["name"] == "Snapshot"
    assert "state" in snapshot
    assert "history" in snapshot


@pytest.mark.asyncio
async def test_agent_state_machine_progression():
    config = AgentConfig(agent_id="agt_prog", name="Progress")
    agent = Agent(config)

    async def handler(params):
        return True

    agent.executor.register("analyze", handler)
    agent.executor.register("plan", handler)
    agent.executor.register("execute", handler)
    agent.executor.register("verify", handler)

    await agent.run("Progression test")
    assert agent.state_machine.is_terminal()
