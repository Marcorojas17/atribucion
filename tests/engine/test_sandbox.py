"""Tests del sandbox de ejecución."""

import pytest

from engine.runtime.sandbox import Sandbox, SandboxConfig


def test_sandbox_runs_simple_code():
    sandbox = Sandbox()
    result = sandbox.run("print(2 + 2)")
    assert result.success
    assert "4" in result.stdout


def test_sandbox_blocks_import_os():
    sandbox = Sandbox()
    result = sandbox.run("import os")
    assert not result.success
    assert "prohibido" in result.error.lower() or "no permitido" in result.error.lower()


def test_sandbox_blocks_eval():
    sandbox = Sandbox()
    result = sandbox.run("eval('1+1')")
    assert not result.success


def test_sandbox_blocks_forbidden_attribute():
    sandbox = Sandbox()
    result = sandbox.run("(1).__class__")
    assert not result.success


def test_sandbox_timeout():
    config = SandboxConfig(timeout_seconds=1)
    sandbox = Sandbox(config)
    result = sandbox.run("while True: pass")
    assert not result.success
    assert "timeout" in result.error.lower()


def test_sandbox_stats():
    sandbox = Sandbox()
    sandbox.run("print('a')")
    sandbox.run("print('b')")
    stats = sandbox.get_stats()
    assert stats["total_executions"] == 2
    assert stats["successful"] == 2
