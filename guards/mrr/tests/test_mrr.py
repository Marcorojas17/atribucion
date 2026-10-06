"""Tests del guardián MRR."""

import json

import pytest

from guards.mrr.agent import MRRGuard


@pytest.mark.asyncio
async def test_mrr_check_returns_findings():
    guard = MRRGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


@pytest.mark.asyncio
async def test_mrr_counts_certificates(tmp_path):
    """Debe contar certificados totales."""
    certs_file = tmp_path / "certificates.json"
    certs = {f"cert_{i}": {"certificate_id": f"cert_{i}"} for i in range(10)}
    certs_file.write_text(json.dumps(certs))

    guard = MRRGuard(data_dir=tmp_path)
    findings = await guard.check()

    count_findings = [f for f in findings if "certificados" in f.message.lower()]
    assert len(count_findings) >= 1


@pytest.mark.asyncio
async def test_mrr_detects_inactive_tenants(tmp_path):
    """Tenants sin API key > 30 días deben aparecer."""
    tenants_file = tmp_path / "tenants.json"
    tenants = {
        "tnt_001": {
            "id": "tnt_001",
            "created_at": "2020-01-01T00:00:00+00:00",
            "api_key": None,
        },
    }
    tenants_file.write_text(json.dumps(tenants))

    guard = MRRGuard(data_dir=tmp_path)
    findings = await guard.check()

    inactive = [f for f in findings if "inactivos" in f.message.lower()]
    assert len(inactive) >= 1