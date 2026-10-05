"""
Atribución SDK — Utilidades criptográficas.

Firma payloads con ECDSA secp256k1.
Compatible con el core de Atribución.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def canonical_json(data: Any) -> str:
    """Serializa a JSON determinístico (claves ordenadas)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_bytes(data: Any) -> bytes:
    return canonical_json(data).encode("utf-8")


def generate_keypair() -> tuple[bytes, bytes]:
    """
    Genera par de claves ECDSA secp256k1.

    Devuelve (private_key_pem, public_key_pem).
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


def sign_payload(private_key_pem: bytes, payload: Any) -> str:
    """
    Firma un payload con ECDSA.

    Devuelve la firma en hex con prefijo 0x.
    """
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    signature = private_key.sign(canonical_bytes(payload), ec.ECDSA(hashes.SHA256()))
    return "0x" + signature.hex()


def sign_hybrid_pqc_placeholder(payload: Any) -> str:
    """
    Placeholder para firma post-cuántica.

    Cuando liboqs esté disponible en el cliente, se reemplaza
    por ML-DSA real. Por ahora devuelve un hash determinístico.
    """
    h = hashlib.sha3_256(canonical_bytes(payload) + b"pqc-pending").hexdigest()
    return "0x" + h
"""
Atribución SDK — Utilidades criptográficas.

Firma payloads con ECDSA secp256k1.
Compatible con el core de Atribución.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def canonical_json(data: Any) -> str:
    """Serializa a JSON determinístico (claves ordenadas)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_bytes(data: Any) -> bytes:
    """Versión en bytes de canonical_json."""
    return canonical_json(data).encode("utf-8")


def generate_keypair() -> tuple[bytes, bytes]:
    """
    Genera par de claves ECDSA secp256k1.

    Devuelve (private_key_pem, public_key_pem).
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


def sign_payload(private_key_pem: bytes, payload: Any) -> str:
    """
    Firma un payload con ECDSA.

    Devuelve la firma en hex con prefijo 0x.
    """
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    signature = private_key.sign(canonical_bytes(payload), ec.ECDSA(hashes.SHA256()))
    return "0x" + signature.hex()


def sign_hybrid_pqc_placeholder(payload: Any) -> str:
    """
    Placeholder para firma post-cuántica.

    Cuando liboqs esté disponible, se reemplaza por ML-DSA real.
    """
    h = hashlib.sha3_256(canonical_bytes(payload) + b"pqc-pending").hexdigest()
    return "0x" + h