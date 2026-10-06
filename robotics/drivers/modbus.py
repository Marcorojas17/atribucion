"""
Atribución Robotics — Driver Modbus TCP.

Comunicación industrial con PLCs y robots vía Modbus.
Requiere `pymodbus` instalado (pip install pymodbus).

Uso:
    driver = ModbusDriver(host="192.168.1.10", port=502)
    registers = driver.read_register(100, count=5)
    driver.write_register(100, 42)
    driver.shutdown()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

try:
    from pymodbus.client import ModbusTcpClient
    MODBUS_AVAILABLE = True
except ImportError:
    MODBUS_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class ModbusConfig:
    """Configuración del cliente Modbus."""

    host: str = "localhost"
    port: int = 502
    unit_id: int = 1
    timeout: float = 3.0
    retries: int = 3


class ModbusDriver:
    """Driver para Modbus TCP."""

    def __init__(self, config: ModbusConfig | None = None) -> None:
        if not MODBUS_AVAILABLE:
            raise RuntimeError(
                "pymodbus no instalado. pip install pymodbus"
            )

        self.config = config or ModbusConfig()
        self.client = ModbusTcpClient(
            host=self.config.host,
            port=self.config.port,
            timeout=self.config.timeout,
            retries=self.config.retries,
        )

        if not self.client.connect():
            raise ConnectionError(
                f"No se pudo conectar a Modbus {self.config.host}:{self.config.port}"
            )

        logger.info(
            "Modbus conectado a %s:%d",
            self.config.host,
            self.config.port,
        )

    # ─── READ ──────────────────────────────────────────────────

    def read_holding_registers(
        self,
        address: int,
        count: int = 1,
    ) -> list[int]:
        """Lee registros holding."""
        result = self.client.read_holding_registers(
            address,
            count,
            slave=self.config.unit_id,
        )
        if result.isError():
            raise RuntimeError(f"Error leyendo registros en {address}")
        return list(result.registers)

    def read_input_registers(
        self,
        address: int,
        count: int = 1,
    ) -> list[int]:
        """Lee registros de input."""
        result = self.client.read_input_registers(
            address,
            count,
            slave=self.config.unit_id,
        )
        if result.isError():
            raise RuntimeError(f"Error leyendo input registers en {address}")
        return list(result.registers)

    def read_coils(self, address: int, count: int = 1) -> list[bool]:
        """Lee coils (bits)."""
        result = self.client.read_coils(address, count, slave=self.config.unit_id)
        if result.isError():
            raise RuntimeError(f"Error leyendo coils en {address}")
        return list(result.bits)

    def read_discrete_inputs(self, address: int, count: int = 1) -> list[bool]:
        """Lee discrete inputs."""
        result = self.client.read_discrete_inputs(
            address, count, slave=self.config.unit_id
        )
        if result.isError():
            raise RuntimeError(f"Error leyendo discrete inputs en {address}")
        return list(result.bits)

    # ─── WRITE ─────────────────────────────────────────────────

    def write_register(self, address: int, value: int) -> None:
        """Escribe un registro."""
        result = self.client.write_register(
            address, value, slave=self.config.unit_id
        )
        if result.isError():
            raise RuntimeError(f"Error escribiendo registro {address}")

    def write_registers(self, address: int, values: list[int]) -> None:
        """Escribe múltiples registros."""
        result = self.client.write_registers(
            address, values, slave=self.config.unit_id
        )
        if result.isError():
            raise RuntimeError(f"Error escribiendo registros en {address}")

    def write_coil(self, address: int, value: bool) -> None:
        """Escribe un coil."""
        result = self.client.write_coil(
            address, value, slave=self.config.unit_id
        )
        if result.isError():
            raise RuntimeError(f"Error escribiendo coil {address}")

    # ─── LIFECYCLE ─────────────────────────────────────────────

    def is_connected(self) -> bool:
        return self.client.connected

    def shutdown(self) -> None:
        """Cierra la conexión Modbus."""
        self.client.close()
        logger.info("Modbus cerrado")