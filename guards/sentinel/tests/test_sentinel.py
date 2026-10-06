"""Tests del guardián SENTINEL."""

import json
from datetime import datetime, timezone

import pytest

from guards.sentinel.agent import SentinelGuard


@pytest.mark.asyncio
async def test_sentinel_check_returns_findings():
    guard = SentinelGuard()
    findings = await guard.check()
    assert isinstance(findings, list)


@pytest.mark.asyncio
async def test_sentinel_detects_auth_bruteforce(tmp_path):
    """Muchos 401 desde misma IP = critical."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    errors_file = logs_dir / "errors.log"

    entries = []
    for _ in range(50):
        entries.append(json.dumps({
            "ip": "1.2.3.4",
            "status": 401,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))
    errors_file.write_text("\n".join(entries))

    guard = SentinelGuard(logs_dir=logs_dir)
    findings = await guard.check()

    bruteforce = [f for f in findings if "401" in f.message]
    assert len(bruteforce) >= 1
    assert bruteforce[0].severity == "critical"


@pytest.mark.asyncio
async def test_sentinel_detects_fuzzing(tmp_path):
    """Muchos 422 desde misma IP = warning."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    errors_file = logs_dir / "errors.log"

    entries = []
    for _ in range(100):
        entries.append(json.dumps({
            "ip": "5.6.7.8",
            "status": 422,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))
    errors_file.write_text("\n".join(entries))

    guard = SentinelGuard(logs_dir=logs_dir)
    findings = await guard.check()

    fuzzing = [f for f in findings if "422" in f.message]
    assert len(fuzzing) >= 1
    assert fuzzing[0].severity == "warning"


@pytest.mark.asyncio
async def test_sentinel_no_findings_clean_logs(tmp_path):
    """Logs vacíos no deben generar findings."""
    guard = SentinelGuard(logs_dir=tmp_path)
    findings = await guard.check()
    assert findings == []