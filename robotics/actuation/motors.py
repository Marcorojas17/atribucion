"""
Atribución Robotics — Control de motores.

Interfaz genérica para motores DC, steppers y brushless.
Abstrae el hardware subyacente.

Uso:
    motors = MotorController(motor_count=2)
    motors.move(Direction.FORWARD, speed=0.5)
    motors.stop_all()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


class Direction(str, Enum):
    """Dirección de movimiento."""

    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"


class MotorType(str, Enum):
    """Tipo de motor."""

    DC = "dc"
    STEPPER = "stepper"
    BRUSHLESS = "brushless"
    SERVO = "servo"


@dataclass
class MotorConfig:
    """Configuración de un motor."""

    motor_id: int
    motor_type: MotorType = MotorType.DC
    max_speed: float = 1.0
    min_speed: float = 0.0
    inverted: bool = False
    gpio_pin_pwm: int | None = None
    gpio_pin_dir: int | None = None


class MotorController:
    """Controlador genérico de motores."""

    def __init__(
        self,
        motor_count: int = 2,
        motor_configs: list[MotorConfig] | None = None,
    ) -> None:
        self.motor_count = motor_count
        self._configs: dict[int, MotorConfig] = {}

        if motor_configs:
            for cfg in motor_configs:
                self._configs[cfg.motor_id] = cfg
        else:
            for i in range(motor_count):
                self._configs[i] = MotorConfig(motor_id=i)

        self._speeds: dict[int, float] = {i: 0.0 for i in range(motor_count)}
        self._directions: dict[int, Direction] = {
            i: Direction.STOP for i in range(motor_count)
        }
        self._last_update = None
        logger.info("MotorController listo (%d motores)", motor_count)

    # ─── CONFIG ────────────────────────────────────────────────

    def set_motor_config(self, config: MotorConfig) -> None:
        """Configura un motor individual."""
        self._configs[config.motor_id] = config

    def get_motor_config(self, motor_id: int) -> MotorConfig:
        return self._configs[motor_id]

    # ─── SPEED ─────────────────────────────────────────────────

    def set_speed(self, motor_id: int, speed: float) -> None:
        """
        Establece velocidad de un motor.

        Speed: -1.0 a 1.0 (negativo = backward).
        """
        if motor_id not in self._configs:
            raise ValueError(f"Motor {motor_id} no existe")

        cfg = self._configs[motor_id]
        if cfg.inverted:
            speed = -speed

        speed = max(-cfg.max_speed, min(cfg.max_speed, speed))
        self._speeds[motor_id] = speed

        if speed > 0:
            self._directions[motor_id] = Direction.FORWARD
        elif speed < 0:
            self._directions[motor_id] = Direction.BACKWARD
        else:
            self._directions[motor_id] = Direction.STOP

        logger.debug(
            "Motor %d → %.2f (dirección: %s)",
            motor_id, speed, self._directions[motor_id].value,
        )

    def get_speed(self, motor_id: int) -> float:
        return self._speeds[motor_id]

    def get_all_speeds(self) -> dict[int, float]:
        return dict(self._speeds)

    # ─── MOVEMENT ──────────────────────────────────────────────

    def move(self, direction: Direction, speed: float) -> None:
        """Mueve todos los motores en una dirección."""
        if direction == Direction.STOP:
            self.stop_all()
            return

        if direction == Direction.FORWARD:
            signed = abs(speed)
        elif direction == Direction.BACKWARD:
            signed = -abs(speed)
        elif direction == Direction.LEFT:
            self._turn(left=True, speed=abs(speed))
            return
        elif direction == Direction.RIGHT:
            self._turn(left=False, speed=abs(speed))
            return
        else:
            signed = 0.0

        for motor_id in range(self.motor_count):
            self.set_speed(motor_id, signed)

    def _turn(self, left: bool, speed: float) -> None:
        """Gira el robot (motores opuestos)."""
        for motor_id in range(self.motor_count):
            if motor_id % 2 == 0:
                self.set_speed(motor_id, speed if left else -speed)
            else:
                self.set_speed(motor_id, -speed if left else speed)

    def stop_all(self) -> None:
        """Detiene todos los motores (parada de emergencia)."""
        for motor_id in range(self.motor_count):
            self._speeds[motor_id] = 0.0
            self._directions[motor_id] = Direction.STOP
        logger.warning("MotorController: STOP ALL")

    # ─── STATUS ────────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        return {
            "motor_count": self.motor_count,
            "speeds": self._speeds,
            "directions": {k: v.value for k, v in self._directions.items()},
        }