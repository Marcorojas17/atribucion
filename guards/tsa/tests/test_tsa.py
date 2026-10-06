"""Tests del guardián TSA."""

import json

import pytest

from guards.tsa.agent import TSAGuard


@pytest.mark.asyncio
async def test_tsa_check_returns_findings():
    guard = TSAGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


@pytest.mark.asyncio
async def test_tsa_detects_missing_token(tmp_path):
    """Certificado sin sello TSA debe ser warning."""
    certs_file = tmp_path / "certificates.json"
    certs = {
        "cert_001": {
            "certificate_id": "cert_001",
            "tsa_token": "",
        },
    }
    certs_file.write_text(json.dumps(certs))

    guard = TSAGuard(certs_dir=tmp_path)
    findings = await guard.check()

    missing = [f for f in findings if "sin sello" in f.message.lower()]
    assert len(missing) >= 1


@pytest.mark.asyncio
async def test_tsa_detects_duplicates(tmp_path):
    """Tokens duplicados deben ser critical."""
    certs_file = tmp_path / "certificates.json"
    token = "0x" + "a" * 64
    certs = {
        "cert_001": {"certificate_id": "cert_001", "tsa_token": token},
        "cert_002": {"certificate_id": "cert_002", "tsa_token": token},
    }
    certs_file.write_text(json.dumps(certs))

    guard = TSAGuard(certs_dir=tmp_path)
    findings = await guard.check()

    dup = [f for f in findings if f.severity == "critical"]
    assert len(dup) >= 1