"""Tests del orquestador MADRE."""

import pytest

from engine.orchestrator.madre import MADRE, MotoAgent


@pytest.mark.asyncio
async def test_madre_register():
    m = MADRE(session_id="test-madre-1")

    async def call(p):
        return "respuesta"

    agent = MotoAgent("TestAgent", call)
    m.register(agent)
    assert "TestAgent" in m.agents


@pytest.mark.asyncio
async def test_madre_broadcast():
    m = MADRE(session_id="test-madre-2")

    async def codex(p):
        return "Respuesta Codex"

    async def claude(p):
        return "Respuesta Claude"

    m.register(MotoAgent("Codex", codex))
    m.register(MotoAgent("Claude", claude))

    responses = await m.broadcast("Test message")
    assert len(responses) == 2
    assert responses["Codex"] == "Respuesta Codex"


@pytest.mark.asyncio
async def test_madre_sequence():
    m = MADRE(session_id="test-madre-3")

    async def codex(p):
        return "Paso 1"

    async def claude(p):
        return "Paso 2"

    m.register(MotoAgent("Codex", codex))
    m.register(MotoAgent("Claude", claude))

    responses = await m.sequence("Test", ["Codex", "Claude"])
    assert responses["Codex"] == "Paso 1"
    assert responses["Claude"] == "Paso 2"


@pytest.mark.asyncio
async def test_madre_summary():
    m = MADRE(session_id="test-madre-4")

    async def call(p):
        return "ok"

    m.register(MotoAgent("A", call))
    m.register(MotoAgent("B", call))
    await m.broadcast("Test")

    summary = m.summary()
    assert summary["session_id"] == "test-madre-4"
    assert len(summary["agents"]) == 2
    assert summary["integrity_ok"]
