"""Tests del guardián ORACLE."""

import json

import pytest

from guards.oracle.agent import OracleGuard


@pytest.mark.asyncio
async def test_oracle_check_returns_findings():
    guard = OracleGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


@pytest.mark.asyncio
async def test_oracle_detects_invalid_did(tmp_path):
    """DID inválido debe generar warning."""
    certs_file = tmp_path / "certificates.json"
    certs = {
        "cert_001": {
            "certificate_id": "cert_001",
            "agent_did": "did:invalid:format",
            "credential": {"issuer": "test"},
        },
    }
    certs_file.write_text(json.dumps(certs))

    guard = OracleGuard(data_dir=tmp_path)
    findings = await guard.check()

    invalid = [f for f in findings if "DID inválido" in f.message]
    assert len(invalid) >= 1


@pytest.mark.asyncio
async def test_oracle_detects_missing_credential(tmp_path):
    """Certificado sin credencial debe ser warning."""
    certs_file = tmp_path / "certificates.json"
    certs = {
        "cert_001": {
            "certificate_id": "cert_001",
            "agent_did": "did:kronos:agent:0x" + "a" * 40,
            "credential": None,
        },
    }
    certs_file.write_text(json.dumps(certs))

    guard = OracleGuard(data_dir=tmp_path)
    findings = await guard.check()

    missing = [f for f in findings if "sin credencial" in f.message]
    assert len(missing) >= 1