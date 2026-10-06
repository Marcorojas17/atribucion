"""
Atribución Robotics — Control de servos.

Interfaz para servos con ángulos 0-180°.
Permite movimientos suaves (interpolación).

Uso:
    servos = ServoController(servo_count=3)
    servos.set_angle(0, 45.0)
    servos.smooth_move(1, from_angle=0, to_angle=180, duration_ms=500)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any


logger = logging.getLogger(__name__)


@dataclass
class ServoConfig:
    """Configuración de un servo."""

    servo_id: int
    min_angle: float = 0.0
    max_angle: float = 180.0
    center_angle: float = 90.0
    inverted: bool = False
    gpio_pin: int | None = None


class ServoController:
    """Controlador de servos."""

    def __init__(
        self,
        servo_count: int = 1,
        servo_configs: list[ServoConfig] | None = None,
    ) -> None:
        self.servo_count = servo_count
        self._configs: dict[int, ServoConfig] = {}

        if servo_configs:
            for cfg in servo_configs:
                self._configs[cfg.servo_id] = cfg
        else:
            for i in range(servo_count):
                self._configs[i] = ServoConfig(servo_id=i)

        self._angles: dict[int, float] = {
            i: cfg.center_angle for i, cfg in self._configs.items()
        }
        logger.info("ServoController listo (%d servos)", servo_count)

    # ─── SET ANGLE ─────────────────────────────────────────────

    def set_angle(self, servo_id: int, angle: float) -> None:
        """Establece el ángulo de un servo."""
        if servo_id not in self._configs:
            raise ValueError(f"Servo {servo_id} no existe")

        cfg = self._configs[servo_id]
        if cfg.inverted:
            angle = 180.0 - angle

        angle = max(cfg.min_angle, min(cfg.max_angle, angle))
        self._angles[servo_id] = angle
        logger.debug("Servo %d → %.1f°", servo_id, angle)

    def get_angle(self, servo_id: int) -> float:
        return self._angles[servo_id]

    def get_all_angles(self) -> dict[int, float]:
        return dict(self._angles)

    # ─── BULK ──────────────────────────────────────────────────

    def center_all(self) -> None:
        """Centra todos los servos."""
        for servo_id, cfg in self._configs.items():
            self.set_angle(servo_id, cfg.center_angle)

    def set_all(self, angle: float) -> None:
        """Establece el mismo ángulo a todos los servos."""
        for servo_id in self._configs:
            self.set_angle(servo_id, angle)

    # ─── SMOOTH MOVE ───────────────────────────────────────────

    def smooth_move(
        self,
        servo_id: int,
        from_angle: float,
        to_angle: float,
        duration_ms: int = 500,
        steps: int = 20,
    ) -> None:
        """
        Mueve un servo suavemente entre dos ángulos.

        Interpola linealmente y duerme entre pasos.
        """
        if servo_id not in self._configs:
            raise ValueError(f"Servo {servo_id} no existe")

        if steps <= 0:
            raise ValueError("steps debe ser > 0")

        step_duration = (duration_ms / 1000.0) / steps
        delta = (to_angle - from_angle) / steps

        for i in range(steps + 1):
            angle = from_angle + delta * i
            self.set_angle(servo_id, angle)
            time.sleep(step_duration)

    # ─── STATUS ────────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        return {
            "servo_count": self.servo_count,
            "angles": self._angles,
            "configs": {
                k: {
                    "min": v.min_angle,
                    "max": v.max_angle,
                    "center": v.center_angle,
                    "inverted": v.inverted,
                }
                for k, v in self._configs.items()
            },
        }