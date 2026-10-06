"""Tests del guardián SHA."""

import json
from pathlib import Path

import pytest

from guards.sha.agent import SHAGuard


@pytest.mark.asyncio
async def test_sha_check_returns_findings():
    guard = SHAGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


def test_sha_valid_format():
    assert SHAGuard._is_valid_sha256("a" * 64) is True
    assert SHAGuard._is_valid_sha256("0" * 64) is True


def test_sha_invalid_format():
    assert SHAGuard._is_valid_sha256("a" * 63) is False
    assert SHAGuard._is_valid_sha256("a" * 65) is False
    assert SHAGuard._is_valid_sha256("Z" * 64) is False
    assert SHAGuard._is_valid_sha256("") is False


@pytest.mark.asyncio
async def test_sha_detects_duplicates(tmp_path):
    """Verifica que detecte hashes duplicados (replay)."""
    certs_file = tmp_path / "certificates.json"
    dup_hash = "a" * 64
    certs = {
        "cert_001": {
            "certificate_id": "cert_001",
            "credential": {"evidence": {"sha256": dup_hash}},
        },
        "cert_002": {
            "certificate_id": "cert_002",
            "credential": {"evidence": {"sha256": dup_hash}},
        },
    }
    certs_file.write_text(json.dumps(certs))

    guard = SHAGuard(certs_dir=tmp_path)
    findings = await guard.check()

    replay = [f for f in findings if "duplicado" in f.message.lower()]
    assert len(replay) >= 1