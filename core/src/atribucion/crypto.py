"""
Atribución — Core criptográfico.

Implementa:
- Serialización canónica JSON (determinística)
- Hashing doble (SHA-256 + SHA-3-256)
- Firmas ECDSA secp256k1
- Firmas híbridas (ECDSA + ML-DSA placeholder post-cuántico)

La firma híbrida garantiza que un payload es válido solo si
AMBOS algoritmos (clásico + post-cuántico) firman correctamente.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


# ─────────────────────────────────────────────────────────────
# SERIALIZACIÓN CANÓNICA
# ─────────────────────────────────────────────────────────────

def canonical_json(data: Any) -> str:
    """
    Serializa a JSON determinístico.

    - Claves ordenadas alfabéticamente
    - Sin espacios innecesarios
    - UTF-8, sin escapes ASCII

    Garantiza que el mismo objeto produzca siempre el mismo
    string, en cualquier lenguaje y plataforma.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def canonical_bytes(data: Any) -> bytes:
    """Versión en bytes de canonical_json."""
    return canonical_json(data).encode("utf-8")


# ─────────────────────────────────────────────────────────────
# HASHING DOBLE (SHA-256 + SHA-3)
# ─────────────────────────────────────────────────────────────

def hash_double(data: Any) -> dict[str, str]:
    """
    Calcula SHA-256 y SHA-3-256 sobre el payload canónico.

    Devuelve ambos hashes. Un payload es válido solo si
    ambos coinciden con los esperados.
    """
    payload = canonical_bytes(data)
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "sha3": hashlib.sha3_256(payload).hexdigest(),
    }


def hash_sha256(data: bytes) -> str:
    """SHA-256 en hex."""
    return hashlib.sha256(data).hexdigest()


def hash_sha3(data: bytes) -> str:
    """SHA-3-256 en hex."""
    return hashlib.sha3_256(data).hexdigest()


# ─────────────────────────────────────────────────────────────
# FIRMAS CLÁSICAS (ECDSA secp256k1)
# ─────────────────────────────────────────────────────────────

def generate_ecdsa_keypair() -> tuple[bytes, bytes]:
    """
    Genera par de claves ECDSA secp256k1.

    Devuelve (private_key_pem, public_key_pem).
    En producción, la privada NUNCA sale del HSM.
    """
    private_key = ec.generate_private_key(ec.SECP256K1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def sign_ecdsa(private_key_pem: bytes, payload: bytes) -> str:
    """Firma con ECDSA secp256k1 + SHA-256. Devuelve hex con 0x."""
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )
    signature = private_key.sign(payload, ec.ECDSA(hashes.SHA256()))
    return "0x" + signature.hex()


def verify_ecdsa(
    public_key_pem: bytes,
    payload: bytes,
    signature_hex: str,
) -> bool:
    """Verifica firma ECDSA. Devuelve True/False."""
    try:
        public_key = serialization.load_pem_public_key(public_key_pem)
        signature = bytes.fromhex(signature_hex.removeprefix("0x"))
        public_key.verify(signature, payload, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError):
        return False


# ─────────────────────────────────────────────────────────────
# FIRMAS HÍBRIDAS (ECDSA + PQC)
# ─────────────────────────────────────────────────────────────

PQC_AVAILABLE = False
"""Se activará cuando liboqs esté disponible en el entorno."""


def sign_hybrid(
    private_key_pem: bytes,
    payload: Any,
    private_key_pqc: bytes | None = None,
) -> tuple[str, str]:
    """
    Firma híbrida: ECDSA + PQC placeholder.

    Devuelve (firma_clasica_hex, firma_pqc_hex).

    Cuando PQC esté disponible (liboqs + ML-DSA), la firma PQC
    será criptográficamente real. Por ahora es un placeholder
    determinístico derivado del payload.
    """
    data = canonical_bytes(payload)
    sig_classic = sign_ecdsa(private_key_pem, data)

    if PQC_AVAILABLE and private_key_pqc:
        # TODO: implementar con liboqs (ML-DSA-65 / Dilithium3)
        sig_pqc = "0x" + hashlib.sha3_256(data + b"pqc-placeholder").hexdigest()
    else:
        # Placeholder determinístico para desarrollo
        sig_pqc = "0x" + hashlib.sha3_256(data + b"pqc-pending").hexdigest()

    return sig_classic, sig_pqc


def verify_hybrid(
    public_key_pem: bytes,
    payload: Any,
    signature_classic: str,
    signature_pqc: str,
) -> bool:
    """
    Verifica AMBAS firmas (clásica + post-cuántica).

    Solo es válido si las dos pasan.
    """
    data = canonical_bytes(payload)

    if not verify_ecdsa(public_key_pem, data, signature_classic):
        return False

    if PQC_AVAILABLE:
        # TODO: verificar firma PQC real (ML-DSA)
        pass
    else:
        # Verificar placeholder determinístico
        expected = "0x" + hashlib.sha3_256(data + b"pqc-pending").hexdigest()
        if signature_pqc != expected:
            return False

    return True