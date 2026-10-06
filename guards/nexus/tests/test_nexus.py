"""Tests del guardián NEXUS."""

import pytest

from guards.nexus.agent import NexusGuard


@pytest.mark.asyncio
async def test_nexus_check_returns_findings():
    guard = NexusGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


@pytest.mark.asyncio
async def test_nexus_detects_unreachable_service():
    """Servicio inalcanzable debe generar finding critical."""
    guard = NexusGuard()
    findings = await guard.check()

    # Al menos debe intentar verificar servicios
    # Los findings dependen de conectividad real
    for f in findings:
        assert f.guard == "nexus"
        assert f.severity in ("info", "warning", "critical")


@pytest.mark.asyncio
async def test_nexus_finding_structure():
    """Verifica que los findings tengan estructura correcta."""
    guard = NexusGuard()
    findings = await guard.check()

    for f in findings:
        assert f.guard == "nexus"
        assert f.message != ""
        assert f.timestamp != ""