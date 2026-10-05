"""
Atribución Robotics — Proof of Physical Presence.

Prueba criptográfica de que un robot estuvo en un lugar
y momento determinados.

Combina:
- DID del robot
- Timestamp firmado
- Geolocalización (con precisión reducida por privacidad)
- Prueba de sensor (IMU, cámara)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class ProofOfPresence:
    """Prueba de presencia física."""

    proof_id: str
    robot_did: str
    timestamp: str
    geohash: str          # ubicación con precisión reducida
    sensor_data_hash: str  # hash de sensores (no datos crudos)
    signature: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "robot_did": self.robot_did,
            "timestamp": self.timestamp,
            "geohash": self.geohash,
            "sensor_data_hash": self.sensor_data_hash,
            "signature": self.signature,
            "metadata": self.metadata,
        }


def create_proof_of_presence(
    robot_did: str,
    latitude: float,
    longitude: float,
    sensor_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> ProofOfPresence:
    """
    Crea una prueba de presencia física.

    La latitud/longitud se convierte a geohash de precisión 5
    (~4.9 km) para preservar privacidad.
    """
    # Geohash simple (precisión 5)
    geohash = _encode_geohash(latitude, longitude, precision=5)

    # Hash de datos de sensores (no los datos crudos)
    sensor_bytes = str(sorted(sensor_data.items())).encode()
    sensor_hash = hashlib.sha256(sensor_bytes).hexdigest()

    return ProofOfPresence(
        proof_id=f"pop_{uuid4().hex}",
        robot_did=robot_did,
        timestamp=datetime.now(timezone.utc).isoformat(),
        geohash=geohash,
        sensor_data_hash=sensor_hash,
        metadata=metadata or {},
    )


def _encode_geohash(lat: float, lon: float, precision: int = 5) -> str:
    """
    Codifica lat/lon a geohash (implementación simple).

    Base32: 0123456789bcdefghjkmnpqrstuvwxyz
    """
    BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]

    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    even = True

    while len(geohash) < precision:
        if even:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon > mid:
                ch |= bits[bit]
                lon_range[0] = mid
            else:
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat > mid:
                ch |= bits[bit]
                lat_range[0] = mid
            else:
                lat_range[1] = mid

        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash.append(BASE32[ch])
            bit = 0
            ch = 0

    return "".join(geohash)