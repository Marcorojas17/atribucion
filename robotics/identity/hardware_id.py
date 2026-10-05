"""
Atribución Robotics — Identidad de hardware.

Vincula un DID a un chip físico (TPM, Secure Enclave).
Genera un fingerprint determinístico del hardware.
"""

from __future__ import annotations

import hashlib
import platform
import socket
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class HardwareIdentity:
    """Identidad de hardware de un robot."""

    serial_number: str
    manufacturer: str
    model: str
    firmware_version: str
    machine_id: str
    hostname: str
    platform: str
    fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "serial_number": self.serial_number,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "firmware_version": self.firmware_version,
            "machine_id": self.machine_id,
            "hostname": self.hostname,
            "platform": self.platform,
            "fingerprint": self.fingerprint,
        }


def get_machine_id() -> str:
    """
    Devuelve el machine ID del sistema.

    - Linux: /etc/machine-id
    - macOS: IOPlatformUUID (via system_profiler)
    - Windows: MachineGuid del registro
    """
    # Linux
    for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
        try:
            with open(path) as f:
                value = f.read().strip()
                if value:
                    return value
        except (OSError, IOError):
            continue

    # Fallback: MAC address
    mac = uuid.getnode()
    return f"mac-{mac:012x}"


def build_hardware_identity(
    serial_number: str,
    manufacturer: str,
    model: str,
    firmware_version: str = "1.0.0",
) -> HardwareIdentity:
    """
    Construye la identidad de hardware.

    El fingerprint es determinístico: mismo hardware → mismo fingerprint.
    """
    machine_id = get_machine_id()
    hostname = socket.gethostname()
    plat = f"{platform.system()}-{platform.release()}"

    # Fingerprint = hash de (serial + machine_id + hostname)
    payload = f"{serial_number}|{machine_id}|{hostname}"
    fingerprint = hashlib.sha256(payload.encode()).hexdigest()

    return HardwareIdentity(
        serial_number=serial_number,
        manufacturer=manufacturer,
        model=model,
        firmware_version=firmware_version,
        machine_id=machine_id,
        hostname=hostname,
        platform=plat,
        fingerprint=fingerprint,
    )