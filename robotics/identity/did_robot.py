"""
Atribución Robotics — DID del robot.

Crea un DID bajo el método kronos:robot, vinculado al hardware
del robot mediante su fingerprint.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

# Añadir core/src al path
CORE_SRC = Path(__file__).resolve().parents[2] / "core" / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from atribucion import crypto, did as did_module  # noqa: E402

from robotics.identity.hardware_id import HardwareIdentity  # noqa: E402


def create_robot_did(
    hardware: HardwareIdentity,
    operator_did: str,
) -> str:
    """
    Crea un DID para un robot a partir de su hardware.

    El DID se deriva del fingerprint del hardware, por lo que
    es determinístico: mismo robot → mismo DID.
    """
    metadata = {
        "serial_number": hardware.serial_number,
        "manufacturer": hardware.manufacturer,
        "model": hardware.model,
        "fingerprint": hardware.fingerprint,
        "operator_did": operator_did,
    }
    return did_module.create("kronos", "robot", metadata)


def build_robot_did_document(
    did: str,
    public_key_pem: bytes,
    hardware: HardwareIdentity,
    service_endpoint: str | None = None,
) -> dict[str, Any]:
    """
    Construye el DID Document del robot, incluyendo la prueba
    de hardware.
    """
    doc = did_module.build_document(did, public_key_pem, service_endpoint)

    # Añadir hardware fingerprint al documento
    doc["hardware"] = {
        "fingerprint": hardware.fingerprint,
        "serial_number": hardware.serial_number,
        "manufacturer": hardware.manufacturer,
        "model": hardware.model,
        "firmware_version": hardware.firmware_version,
    }

    return doc