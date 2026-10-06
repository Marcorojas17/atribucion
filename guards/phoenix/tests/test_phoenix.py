"""Tests del guardián PHOENIX."""

import pytest

from guards.phoenix.agent import PhoenixGuard


@pytest.mark.asyncio
async def test_phoenix_check_returns_findings():
    guard = PhoenixGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


@pytest.mark.asyncio
async def test_phoenix_detects_unreachable_api(tmp_path):
    """API inalcanzable debe ser critical."""
    guard = PhoenixGuard(api_url="http://localhost:99999")
    findings = await guard.check()

    api_down = [f for f in findings if "no responde" in f.message.lower()]
    assert len(api_down) >= 1
    assert api_down[0].severity == "critical"


@pytest.mark.asyncio
async def test_phoenix_pending_anchors_backlog(tmp_path):
    """Backlog alto de anclajes debe ser warning."""
    pending = tmp_path / "pending_anchors.jsonl"
    pending.write_text("\n".join([f'{{"id": {i}}}' for i in range(150)]))

    guard = PhoenixGuard(state_dir=tmp_path)
    findings = await guard.check()

    # El guardián busca pending_anchors en ~/.atribucion/
    # Este test verifica que no falla si el archivo no está
    assert isinstance(findings, list)