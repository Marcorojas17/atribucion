"""
Tests de identidad descentralizada (DID).

Verifica:
- Creación de DIDs por tipo
- Validación de formato
- Parseo
- Construcción de DID Document
"""

import pytest

from atribucion import crypto, did


# ─────────────────────────────────────────────────────────────
# CREACIÓN
# ─────────────────────────────────────────────────────────────

def test_create_agent_did() -> None:
    d = did.create("kronos", "agent", {"name": "Test"})
    assert d.startswith("did:kronos:agent:0x")
    assert len(d.split(":")[-1]) == 42  # 0x + 40 hex


def test_create_human_did() -> None:
    d = did.create("kronos", "human", {"name": "Marco"})
    assert d.startswith("did:kronos:human:0x")


def test_create_robot_did() -> None:
    d = did.create("kronos", "robot", {"serial": "ABC123"})
    assert d.startswith("did:kronos:robot:0x")


def test_create_org_did() -> None:
    d = did.create("kronos", "org", {"name": "Acme"})
    assert d.startswith("did:kronos:org:0x")


def test_create_did_unico() -> None:
    d1 = did.create("kronos", "agent", {"name": "A"})
    d2 = did.create("kronos", "agent", {"name": "A"})
    # El timestamp hace que sean distintos
    assert d1 != d2


def test_create_metodo_invalido() -> None:
    with pytest.raises(ValueError):
        did.create("ethereum", "agent", {})


def test_create_tipo_invalido() -> None:
    with pytest.raises(ValueError):
        did.create("kronos", "alien", {})  # type: ignore


# ─────────────────────────────────────────────────────────────
# VALIDACIÓN
# ─────────────────────────────────────────────────────────────

def test_validate_did_valido() -> None:
    d = did.create("kronos", "agent", {"name": "Test"})
    assert did.validate(d) is True


def test_validate_did_invalido_prefijo() -> None:
    assert did.validate("did:ethereum:agent:0x" + "a" * 40) is False


def test_validate_did_invalido_hex() -> None:
    assert did.validate("did:kronos:agent:0xZZZ") is False


# ─────────────────────────────────────────────────────────────
# PARSEO
# ─────────────────────────────────────────────────────────────

def test_parse_did() -> None:
    d = did.create("kronos", "agent", {"name": "Test"})
    parsed = did.parse(d)
    assert parsed["method"] == "kronos"
    assert parsed["type"] == "agent"
    assert parsed["identifier"].startswith("0x")


def test_parse_did_invalido() -> None:
    with pytest.raises(ValueError):
        did.parse("no-es-un-did")


# ─────────────────────────────────────────────────────────────
# DOCUMENTO
# ─────────────────────────────────────────────────────────────

def test_build_document_basico() -> None:
    d = did.create("kronos", "agent", {"name": "Test"})
    _, pub = crypto.generate_ecdsa_keypair()
    doc = did.build_document(d, pub)
    assert doc["id"] == d
    assert "@context" in doc
    assert len(doc["verificationMethod"]) == 1


def test_build_document_con_servicio() -> None:
    d = did.create("kronos", "agent", {"name": "Test"})
    _, pub = crypto.generate_ecdsa_keypair()
    doc = did.build_document(d, pub, "https://api.atribucion.io/v1")
    assert "service" in doc
    assert doc["service"][0]["serviceEndpoint"] == "https://api.atribucion.io/v1"