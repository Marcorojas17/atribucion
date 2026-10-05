"""
Tests del core criptográfico.

Verifica:
- Serialización canónica JSON
- Hashing doble (SHA-256 + SHA-3)
- Firmas ECDSA
- Firmas híbridas
"""

from atribucion import crypto


# ─────────────────────────────────────────────────────────────
# CANONICAL JSON
# ─────────────────────────────────────────────────────────────

def test_canonical_json_ordena_claves() -> None:
    data = {"b": 2, "a": 1}
    assert crypto.canonical_json(data) == '{"a":1,"b":2}'


def test_canonical_json_sin_espacios() -> None:
    data = {"x": [1, 2, 3]}
    assert crypto.canonical_json(data) == '{"x":[1,2,3]}'


def test_canonical_json_deterministico() -> None:
    data = {"z": 1, "a": {"y": 2, "b": 3}}
    assert crypto.canonical_json(data) == crypto.canonical_json(data)


# ─────────────────────────────────────────────────────────────
# HASHING DOBLE
# ─────────────────────────────────────────────────────────────

def test_hash_double_devuelve_sha256_y_sha3() -> None:
    h = crypto.hash_double({"test": 1})
    assert "sha256" in h
    assert "sha3" in h
    assert len(h["sha256"]) == 64
    assert len(h["sha3"]) == 64


def test_hash_double_cambia_con_payload() -> None:
    h1 = crypto.hash_double({"a": 1})
    h2 = crypto.hash_double({"a": 2})
    assert h1["sha256"] != h2["sha256"]
    assert h1["sha3"] != h2["sha3"]


# ─────────────────────────────────────────────────────────────
# ECDSA
# ─────────────────────────────────────────────────────────────

def test_generate_ecdsa_keypair() -> None:
    priv, pub = crypto.generate_ecdsa_keypair()
    assert b"BEGIN PRIVATE KEY" in priv
    assert b"BEGIN PUBLIC KEY" in pub


def test_sign_verify_ecdsa() -> None:
    priv, pub = crypto.generate_ecdsa_keypair()
    payload = b"test payload"
    sig = crypto.sign_ecdsa(priv, payload)
    assert crypto.verify_ecdsa(pub, payload, sig) is True


def test_verify_ecdsa_payload_alterado() -> None:
    priv, pub = crypto.generate_ecdsa_keypair()
    sig = crypto.sign_ecdsa(priv, b"original")
    assert crypto.verify_ecdsa(pub, b"alterado", sig) is False


def test_verify_ecdsa_firma_invalida() -> None:
    _, pub = crypto.generate_ecdsa_keypair()
    assert crypto.verify_ecdsa(pub, b"payload", "0xdeadbeef") is False


# ─────────────────────────────────────────────────────────────
# HÍBRIDAS
# ─────────────────────────────────────────────────────────────

def test_sign_hybrid_devuelve_dos_firmas() -> None:
    priv, _ = crypto.generate_ecdsa_keypair()
    sig_c, sig_p = crypto.sign_hybrid(priv, {"test": 1})
    assert sig_c.startswith("0x")
    assert sig_p.startswith("0x")
    assert sig_c != sig_p


def test_verify_hybrid_valida() -> None:
    priv, pub = crypto.generate_ecdsa_keypair()
    data = {"action": "test"}
    sig_c, sig_p = crypto.sign_hybrid(priv, data)
    assert crypto.verify_hybrid(pub, data, sig_c, sig_p) is True


def test_verify_hybrid_falla_si_pqc_invalida() -> None:
    priv, pub = crypto.generate_ecdsa_keypair()
    data = {"action": "test"}
    sig_c, _ = crypto.sign_hybrid(priv, data)
    assert crypto.verify_hybrid(pub, data, sig_c, "0xdeadbeef") is False