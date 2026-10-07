"""Tests de memoria canónica de MADRE."""

from engine.orchestrator.canonical_memory import CanonicalMemory, Message


def test_add_message():
    mem = CanonicalMemory(session_id="test-mem-1")
    msg = mem.add("Codex", "Hola", role="agent")
    assert msg.agent == "Codex"
    assert msg.content == "Hola"
    assert msg.hash != ""


def test_get_context():
    mem = CanonicalMemory(session_id="test-mem-2")
    mem.add("Codex", "Mensaje 1")
    mem.add("Claude", "Mensaje 2")
    ctx = mem.get_context()
    assert "Mensaje 1" in ctx
    assert "Mensaje 2" in ctx


def test_last_from():
    mem = CanonicalMemory(session_id="test-mem-3")
    mem.add("Codex", "Primero")
    mem.add("Claude", "Segundo")
    mem.add("Codex", "Tercero")
    last = mem.last_from("Codex")
    assert last.content == "Tercero"


def test_verify_integrity_ok():
    mem = CanonicalMemory(session_id="test-mem-4")
    mem.add("Codex", "Test 1")
    mem.add("Claude", "Test 2")
    ok, errors = mem.verify_integrity()
    assert ok
    assert errors == []


def test_verify_integrity_detects_tampering():
    mem = CanonicalMemory(session_id="test-mem-5")
    mem.add("Codex", "Original")
    # Alterar el mensaje
    mem.messages[0].content = "Alterado"
    ok, errors = mem.verify_integrity()
    assert not ok
    assert len(errors) > 0
