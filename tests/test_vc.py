"""
Tests de credenciales verificables (VC 2.0).

Verifica:
- Emisión de credenciales
- Firma híbrida
- Verificación
- Detección de manipulaciones
"""

from atribucion import crypto, did, vc


# ─────────────────────────────────────────────────────────────
# EMISIÓN
# ─────────────────────────────────────────────────────────────

def test_issue_basico() -> None:
    agent = did.create("kronos", "agent", {"name": "Test"})
    cred = vc.issue(
        credential_id="cert_test123",
        issuer=agent,
        subject=agent,
        action={"action": "test"},
        evidence={"cid": "bafy..."},
    )
    assert cred.id == "urn:atribucion:cert_test123"
    assert cred.issuer == agent
    assert cred.subject == agent
    assert len(cred.credential_type) == 2


def test_issue_prefija_cert() -> None:
    agent = did.create("kronos", "agent", {"name": "Test"})
    cred = vc.issue(
        credential_id="test123",  # sin prefijo
        issuer=agent,
        subject=agent,
        action={},
        evidence={},
    )
    assert cred.id == "urn:atribucion:cert_test123"


# ─────────────────────────────────────────────────────────────
# PROOF
# ─────────────────────────────────────────────────────────────

def test_attach_proof() -> None:
    agent = did.create("kronos", "agent", {"name": "Test"})
    cred = vc.issue(
        credential_id="cert_x",
        issuer=agent,
        subject=agent,
        action={"action": "test"},
        evidence={},
    )
    priv, _ = crypto.generate_ecdsa_keypair()
    cred = vc.attach_proof(cred, priv)
    assert "signatureClassic" in cred.proof
    assert "signaturePqc" in cred.proof


# ─────────────────────────────────────────────────────────────
# VERIFICACIÓN
# ─────────────────────────────────────────────────────────────

def test_verify_ok() -> None:
    agent = did.create("kronos", "agent", {"name": "Test"})
    cred = vc.issue(
        credential_id="cert_x",
        issuer=agent,
        subject=agent,
        action={"action": "test"},
        evidence={},
    )
    priv, pub = crypto.generate_ecdsa_keypair()
    cred = vc.attach_proof(cred, priv)
    assert vc.verify(cred, pub) is True


def test_verify_sin_proof() -> None:
    agent = did.create("kronos", "agent", {"name": "Test"})
    cred = vc.issue(
        credential_id="cert_x",
        issuer=agent,
        subject=agent,
        action={},
        evidence={},
    )
    _, pub = crypto.generate_ecdsa_keypair()
    assert vc.verify(cred, pub) is False


def test_verify_credencial_alterada() -> None:
    agent = did.create("kronos", "agent", {"name": "Test"})
    cred = vc.issue(
        credential_id="cert_x",
        issuer=agent,
        subject=agent,
        action={"action": "original"},
        evidence={},
    )
    priv, pub = crypto.generate_ecdsa_keypair()
    cred = vc.attach_proof(cred, priv)

    # Alterar la acción
    cred.action["action"] = "alterada"

    assert vc.verify(cred, pub) is False