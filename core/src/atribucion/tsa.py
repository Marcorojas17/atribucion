"""
Atribución — TSA (Time-Stamp Authority).

Sellado de tiempo RFC 3161.

Modos:
- mock: token determinístico reproducible (desarrollo)
- real: llamada HTTP a FreeTSA o DigiCert (producción)

El sello de tiempo es legalmente reconocido en:
- UE: eIDAS 2.0 (Art. 41, 42)
- México: NOM-151-SCFI-2016
- Internacional: RFC 3161
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from atribucion import crypto


# ─────────────────────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────────────────────

@dataclass
class TSAResult:
    """Resultado de un sellado de tiempo."""

    authority: str
    sealed_at: str
    token: str
    hash_algorithm: str
    mode: str  # "mock" o "real"

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority": self.authority,
            "sealed_at": self.sealed_at,
            "token": self.token,
            "hash_algorithm": self.hash_algorithm,
            "mode": self.mode,
        }


# ─────────────────────────────────────────────────────────────
# SELLADO
# ─────────────────────────────────────────────────────────────

async def seal(
    payload: bytes,
    hash_algorithm: str = "sha256",
) -> TSAResult:
    """
    Sella un payload con RFC 3161.

    Por ahora modo mock. Cuando tengamos acceso a FreeTSA real,
    se cambia a llamada HTTP sin cambiar la API pública.
    """
    return _mock_seal(payload, hash_algorithm)


def _mock_seal(payload: bytes, hash_algorithm: str) -> TSAResult:
    """
    Sello mock determinístico.

    Se reemplaza por FreeTSA real cuando estemos listos.
    El token es reproducibble a partir del payload + timestamp.
    """
    now = datetime.now(timezone.utc)

    h = hashlib.new(hash_algorithm)
    h.update(payload)
    payload_hash = h.digest()

    # Token mock: hash del payload + timestamp + autoridad
    token_material = (
        payload_hash + now.isoformat().encode() + b"mock-tsa"
    )
    token_hash = hashlib.sha256(token_material).hexdigest()

    return TSAResult(
        authority="mock-tsa",
        sealed_at=now.isoformat(),
        token="0x" + token_hash,
        hash_algorithm=hash_algorithm,
        mode="mock",
    )


# ─────────────────────────────────────────────────────────────
# VERIFICACIÓN
# ─────────────────────────────────────────────────────────────

def verify_seal(
    payload: bytes,
    tsa_result: TSAResult,
    hash_algorithm: str = "sha256",
) -> bool:
    """
    Verifica un sello mock.

    Con TSA real, verifica el token criptográfico contra la
    autoridad emisora.
    """
    if tsa_result.mode == "mock":
        h = hashlib.new(hash_algorithm)
        h.update(payload)
        payload_hash = h.digest()

        token_material = (
            payload_hash
            + tsa_result.sealed_at.encode()
            + b"mock-tsa"
        )
        expected = "0x" + hashlib.sha256(token_material).hexdigest()

        return tsa_result.token == expected

    # Modo real: verificación criptográfica con la TSA
    # (se implementa cuando se integre FreeTSA real)
    return False