"""
Atribución — Identidad Descentralizada (DID).

Genera DIDs bajo el método `kronos:` según W3C DID Core.
Tipos soportados: agent, human, robot, org.

Formato: did:kronos:<tipo>:0x<40_hex>
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Literal

from atribucion import crypto


# ─────────────────────────────────────────────────────────────
# TIPOS Y PATRONES
# ─────────────────────────────────────────────────────────────

DIDType = Literal["agent", "human", "robot", "org"]

DID_PATTERN = re.compile(
    r"^did:kronos:(agent|human|robot|org):0x[a-fA-F0-9]{40}$"
)

VALID_TYPES = ("agent", "human", "robot", "org")


# ─────────────────────────────────────────────────────────────
# CREACIÓN
# ─────────────────────────────────────────────────────────────

def create(
    method: str,
    type: DIDType,
    metadata: dict[str, Any],
) -> str:
    """
    Crea un DID determinístico a partir de metadata.

    El identificador se deriva del hash SHA-256 de:
    - tipo
    - metadata canónica
    - timestamp ISO (para unicidad)

    Formato: did:kronos:<tipo>:0x<40_hex>
    """
    if method != "kronos":
        raise ValueError(f"Método no soportado: {method}")

    if type not in VALID_TYPES:
        raise ValueError(f"Tipo de DID no soportado: {type}")

    payload = {
        "type": type,
        "metadata": metadata,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    h = hashlib.sha256(crypto.canonical_bytes(payload)).hexdigest()
    identifier = h[:40]

    return f"did:kronos:{type}:0x{identifier}"


# ─────────────────────────────────────────────────────────────
# VALIDACIÓN
# ─────────────────────────────────────────────────────────────

def validate(did: str) -> bool:
    """Verifica que un DID cumple el formato Kronos."""
    return bool(DID_PATTERN.match(did))


def parse(did: str) -> dict[str, str]:
    """Extrae las partes de un DID."""
    if not validate(did):
        raise ValueError(f"DID inválido: {did}")

    parts = did.split(":")
    return {
        "method": parts[1],
        "type": parts[2],
        "identifier": parts[3],
    }


# ─────────────────────────────────────────────────────────────
# DOCUMENTO DID (W3C DID Core)
# ─────────────────────────────────────────────────────────────

def build_document(
    did: str,
    public_key_pem: bytes,
    service_endpoint: str | None = None,
) -> dict[str, Any]:
    """
    Construye un DID Document compatible con W3C DID Core.

    Incluye:
    - @context
    - id
    - verificationMethod
    - authentication
    - assertionMethod
    - service (opcional)
    """
    if not validate(did):
        raise ValueError(f"DID inválido: {did}")

    doc: dict[str, Any] = {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/suites/ed25519-2020/v1",
        ],
        "id": did,
        "verificationMethod": [
            {
                "id": f"{did}#key-1",
                "type": "EcdsaSecp256k1VerificationKey2019",
                "controller": did,
                "publicKeyPem": public_key_pem.decode("utf-8"),
            }
        ],
        "authentication": [f"{did}#key-1"],
        "assertionMethod": [f"{did}#key-1"],
    }

    if service_endpoint:
        doc["service"] = [
            {
                "id": f"{did}#atribucion",
                "type": "AtribucionService",
                "serviceEndpoint": service_endpoint,
            }
        ]

    return doc