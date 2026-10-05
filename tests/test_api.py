"""
Tests del API FastAPI.

Verifica:
- Healthcheck
- Root
- Endpoint de acciones (happy path)
- Validaciones (reasoning obligatorio, aprobación humana)
- Autenticación
"""

import sys
from pathlib import Path

# Añadir raíz del repo al path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402


client = TestClient(app)

API_KEY = "Bearer ak_test_" + "a" * 64
AGENT_ID = "agt_test123"


# ─────────────────────────────────────────────────────────────
# HEALTHCHECK
# ─────────────────────────────────────────────────────────────

def test_root() -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "atribucion"


def test_health() -> None:
    r = client.get("/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ─────────────────────────────────────────────────────────────
# ACCIONES
# ─────────────────────────────────────────────────────────────

def _valid_action() -> dict:
    return {
        "action": "trade_executed",
        "input": {"symbol": "AAPL", "quantity": 100},
        "output": {"order_id": "ord_1", "status": "filled"},
        "reasoning": "Señal alcista confirmada.",
        "autonomy_level": "semi-autonomo",
    }


def _headers() -> dict:
    return {
        "Authorization": API_KEY,
        "X-Agent-Signature": "0x" + "a" * 130,
        "X-Agent-Signature-PQC": "0x" + "b" * 130,
    }


def test_record_action_happy_path() -> None:
    r = client.post(
        f"/v1/agents/{AGENT_ID}/actions",
        json=_valid_action(),
        headers=_headers(),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["certificate_id"].startswith("cert_")
    assert "proof_url" in data
    assert data["compliance"]["eu_ai_act"]["article_12"] == "compliant"
    assert data["anchor"]["merkle_root"].startswith("0x")
    assert data["timestamp_rfc3161"]["authority"] == "mock-tsa"
    assert data["signature"]["classic"].startswith("0x")
    assert data["signature"]["pqc"].startswith("0x")


def test_record_action_sin_auth() -> None:
    r = client.post(
        f"/v1/agents/{AGENT_ID}/actions",
        json=_valid_action(),
    )
    assert r.status_code == 422  # falta Authorization


def test_record_action_auth_invalida() -> None:
    r = client.post(
        f"/v1/agents/{AGENT_ID}/actions",
        json=_valid_action(),
        headers={
            "Authorization": "Bearer invalid_format",
            "X-Agent-Signature": "0xabc",
            "X-Agent-Signature-PQC": "0xdef",
        },
    )
    assert r.status_code == 401


def test_record_action_autonomo_sin_reasoning() -> None:
    body = _valid_action()
    body["autonomy_level"] = "autonomo"
    del body["reasoning"]
    r = client.post(
        f"/v1/agents/{AGENT_ID}/actions",
        json=body,
        headers=_headers(),
    )
    assert r.status_code == 422


def test_record_action_supervisado_sin_aprobacion() -> None:
    body = _valid_action()
    body["autonomy_level"] = "supervisado"
    r = client.post(
        f"/v1/agents/{AGENT_ID}/actions",
        json=body,
        headers=_headers(),
    )
    assert r.status_code == 422