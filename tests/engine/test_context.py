"""Tests del context builder."""

from engine.orchestrator.context import AgentContext, ContextBuilder


def test_context_builder_basic():
    b = ContextBuilder(session_id="test-ctx")
    ctx = b.build(user_message="Hola", agent_name="Codex", agent_role="arquitecto")
    assert ctx.agent_name == "Codex"
    assert ctx.agent_role == "arquitecto"
    assert ctx.user_message == "Hola"


def test_context_to_prompt():
    ctx = AgentContext(
        agent_name="Codex",
        agent_role="arquitecto",
        agent_capabilities=["refactor"],
        user_message="Test",
        conversation_context="",
        task_context={},
        tools_available=["pytest"],
        memory_context={},
        constraints=["Responde en español"],
        expected_output="Respuesta",
    )
    prompt = ctx.to_prompt()
    assert "Codex" in prompt
    assert "Test" in prompt
    assert "pytest" in prompt
    assert "español" in prompt


def test_context_estimate_tokens():
    b = ContextBuilder()
    ctx = b.build(user_message="Test", agent_name="A")
    tokens = b.estimate_tokens(ctx)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_context_truncate():
    b = ContextBuilder(max_conversation_chars=100)
    ctx = AgentContext(
        agent_name="A",
        agent_role="test",
        agent_capabilities=[],
        user_message="Test",
        conversation_context="x" * 1000,
        task_context={},
        tools_available=[],
        memory_context={},
        constraints=[],
        expected_output="",
    )
    truncated = b.truncate_context(ctx, max_tokens=50)
    assert len(truncated.conversation_context) < len(ctx.conversation_context)
