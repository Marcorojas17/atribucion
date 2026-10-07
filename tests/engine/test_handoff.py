"""Tests del handoff entre agentes."""

from engine.orchestrator.handoff import Handoff, HandoffResult


def test_handoff_creation():
    h = Handoff(
        from_agent="Codex",
        to_agent="Claude",
        reason="Refactorizar",
        context={"file": "crypto.py"},
        expected_result="Código limpio",
    )
    assert h.from_agent == "Codex"
    assert h.to_agent == "Claude"
    assert h.reason == "Refactorizar"


def test_handoff_to_dict():
    h = Handoff(
        from_agent="A",
        to_agent="B",
        reason="Test",
    )
    d = h.to_dict()
    assert d["from"] == "A"
    assert d["to"] == "B"


def test_handoff_to_prompt():
    h = Handoff(
        from_agent="Codex",
        to_agent="Claude",
        reason="Refactorizar crypto.py",
        expected_result="Tests pasando",
        tools_available=["pytest", "ruff"],
    )
    prompt = h.to_prompt()
    assert "Codex" in prompt
    assert "Claude" in prompt
    assert "Refactorizar" in prompt
    assert "pytest" in prompt


def test_handoff_result():
    h = Handoff(from_agent="A", to_agent="B", reason="test")
    result = HandoffResult(handoff=h, accepted=True, response="ok")
    assert result.accepted
    assert result.response == "ok"
    assert result.handoff.from_agent == "A"
