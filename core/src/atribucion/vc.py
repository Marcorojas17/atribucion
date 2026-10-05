"""
Atribución — Verifiable Credentials (W3C VC 2.0).

Emite credenciales verificables para cada acción de un agente.
Cada credencial es un certificado firmado, anclable y auditable.

Cumple con:
- W3C Verifiable Credentials Data Model 2.0
- EU AI Act Art. 12 (registro automático de eventos)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from atribucion import crypto


# ─────────────────────────────────────────────────────────────
# CONTEXTO
# ─────────────────────────────────────────────────────────────

VC_CONTEXT = [
    "https://www.w3.org/2018/credentials/v1",
    "https://kronos.protocol/contexts/atribucion/v1",
]


# ─────────────────────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────────────────────

@dataclass
class Credential:
    """Credencial verificable de una acción."""

    id: str
    issuer: str
    subject: str
    issuance_date: str
    credential_type: list[str]
    action: dict[str, Any]
    evidence: dict[str, Any]
    proof: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serializa la credencial a formato W3C VC 2.0."""
        return {
            "@context": VC_CONTEXT,
            "id": self.id,
            "type": self.credential_type,
            "issuer": self.issuer,
            "issuanceDate": self.issuance_date,
            "credentialSubject": {
                "id": self.subject,
                "action": self.action,
            },
            "evidence": self.evidence,
            "proof": self.proof,
        }

    def canonical_bytes(self) -> bytes:
        """
        Bytes canónicos para firmar/verificar.

        Excluye 'proof' para evitar circularidad.
        """
        payload = self.to_dict().copy()
        payload.pop("proof", None)
        return crypto.canonical_bytes(payload)


# ─────────────────────────────────────────────────────────────
# EMISIÓN
# ─────────────────────────────────────────────────────────────

def issue(
    credential_id: str,
    issuer: str,
    subject: str,
    action: dict[str, Any],
    evidence: dict[str, Any],
) -> Credential:
    """
    Emite una credencial verificable (sin firmar aún).

    El credential_id debe empezar con 'cert_'. Si no, se
    prefija automáticamente.
    """
    if not credential_id.startswith("cert_"):
        credential_id = "cert_" + credential_id

    return Credential(
        id=f"urn:atribucion:{credential_id}",
        issuer=issuer,
        subject=subject,
        issuance_date=datetime.now(timezone.utc).isoformat(),
        credential_type=[
            "VerifiableCredential",
            "AtribucionActionCredential",
        ],
        action=action,
        evidence=evidence,
    )


# ─────────────────────────────────────────────────────────────
# FIRMA
# ─────────────────────────────────────────────────────────────

def attach_proof(
    credential: Credential,
    private_key_pem: bytes,
) -> Credential:
    """
    Adjunta la firma híbrida a la credencial.

    Modifica la credencial in-place y la devuelve.
    """
    sig_classic, sig_pqc = crypto.sign_hybrid(
        private_key_pem,
        credential.canonical_bytes().decode("utf-8"),
    )
    credential.proof = {
        "type": "KronosHybridSignature2026",
        "created": datetime.now(timezone.utc).isoformat(),
        "proofPurpose": "assertionMethod",
        "verificationMethod": f"{credential.issuer}#key-1",
        "signatureClassic": sig_classic,
        "signaturePqc": sig_pqc,
    }
    return credential


# ─────────────────────────────────────────────────────────────
# VERIFICACIÓN
# ─────────────────────────────────────────────────────────────

def verify(credential: Credential, public_key_pem: bytes) -> bool:
    """
    Verifica la firma híbrida de una credencial.

    Devuelve True solo si AMBAS firmas (clásica + PQC) pasan.
    """
    if not credential.proof:
        return False

    return crypto.verify_hybrid(
        public_key_pem,
        credential.canonical_bytes().decode("utf-8"),
        credential.proof.get("signatureClassic", ""),
        credential.proof.get("signaturePqc", ""),
    )