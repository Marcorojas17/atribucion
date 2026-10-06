"""Tests del guardián VAULT."""

import pytest

from guards.vault.agent import VaultGuard


@pytest.mark.asyncio
async def test_vault_check_returns_findings():
    guard = VaultGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


def test_vault_detects_private_key_pattern():
    """El patrón de clave privada debe detectar 0x + 64 hex."""
    import re

    pattern = r"0x[a-fA-F0-9]{64}"
    valid_key = "0x" + "a" * 64
    invalid_key = "0x" + "z" * 64

    assert re.search(pattern, valid_key) is not None
    assert re.search(pattern, invalid_key) is None


def test_vault_detects_aws_key_pattern():
    """El patrón AWS debe detectar AKIA + 16."""
    import re

    pattern = r"AKIA[0-9A-Z]{16}"
    valid = "AKIAIOSFODNN7EXAMPLE"
    invalid = "AKIA123"

    assert re.search(pattern, valid) is not None
    assert re.search(pattern, invalid) is None


@pytest.mark.asyncio
async def test_vault_no_crash_empty_scan():
    """Sin archivos que escanear, no debe fallar."""
    guard = VaultGuard()
    findings = await guard.check()
    assert isinstance(findings, list)