"""
Atribución Robotics — Control de seguridad.

Kill switch, límites de velocidad, detección de colisiones,
parada de emergencia. La capa más importante de un robot.

Uso:
    safety = SafetyController()
    if safety.check_obstacle(distance_m=0.3):
        print("¡Peligro!")
    safety.trigger_emergency("Colisión inminente")
    safety.reset()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


class SafetyState(str, Enum):
    """Estado del sistema de seguridad."""

    NORMAL = "normal"
    WARNING = "warning"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"


@dataclass
class SafetyLimits:
    """Límites de seguridad del robot."""

    max_speed: float = 0.8
    max_acceleration: float = 0.5
    min_obstacle_distance_m: float = 0.5
    max_temperature_c: float = 70.0
    min_battery_percent: float = 15.0
    max_tilt_degrees: float = 30.0


@dataclass
class SafetyEvent:
    """Evento de seguridad registrado."""

    timestamp: str
    state: str
    reason: str
    severity: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "state": self.state,
            "reason": self.reason,
            "severity": self.severity,
            "metadata": self.metadata,
        }


class SafetyController:
    """Controlador de seguridad del robot."""

    def __init__(self, limits: SafetyLimits | None = None) -> None:
        self.limits = limits or SafetyLimits()
        self.state = SafetyState.NORMAL
        self.events: list[SafetyEvent] = []
        self.last_emergency_reason: str | None = None
        self.emergency_count = 0
        logger.info(
            "SafetyController listo (max_speed=%.2f, min_distance=%.2fm)",
            self.limits.max_speed,
            self.limits.min_obstacle_distance_m,
        )

    # ─── CHECKS ────────────────────────────────────────────────

    def check_speed(self, requested_speed: float) -> float:
        """Limita la velocidad al máximo permitido."""
        limited = max(
            -self.limits.max_speed,
            min(self.limits.max_speed, requested_speed),
        )
        if limited != requested_speed:
            logger.warning(
                "Velocidad limitada: %.2f → %.2f",
                requested_speed, limited,
            )
        return limited

    def check_obstacle(self, distance_m: float) -> bool:
        """
        Verifica si hay obstáculo peligroso.

        Retorna True si hay peligro (y activa emergencia).
        """
        if distance_m < self.limits.min_obstacle_distance_m:
            self.trigger_emergency(
                f"Obstáculo a {distance_m:.2f}m",
                metadata={"distance_m": distance_m},
            )
            return True
        if distance_m < self.limits.min_obstacle_distance_m * 2:
            self.state = SafetyState.WARNING
            logger.warning("Obstáculo cercano a %.2fm", distance_m)
        return False

    def check_temperature(self, temperature_c: float) -> bool:
        """Verifica si la temperatura es segura."""
        if temperature_c > self.limits.max_temperature_c:
            self.trigger_emergency(
                f"Temperatura alta: {temperature_c:.1f}°C",
                metadata={"temperature_c": temperature_c},
            )
            return True
        return False

    def check_battery(self, battery_percent: float) -> bool:
        """Verifica si la batería es suficiente."""
        if battery_percent < self.limits.min_battery_percent:
            self.state = SafetyState.WARNING
            logger.warning("Batería baja: %.1f%%", battery_percent)
            return True
        return False

    def check_tilt(self, tilt_degrees: float) -> bool:
        """Verifica si la inclinación es segura."""
        if abs(tilt_degrees) > self.limits.max_tilt_degrees:
            self.trigger_emergency(
                f"Inclinación excesiva: {tilt_degrees:.1f}°",
                metadata={"tilt_degrees": tilt_degrees},
            )
            return True
        return False

    # ─── EMERGENCY ─────────────────────────────────────────────

    def trigger_emergency(
        self,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Activa parada de emergencia."""
        self.state = SafetyState.EMERGENCY
        self.last_emergency_reason = reason
        self.emergency_count += 1

        event = SafetyEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            state=SafetyState.EMERGENCY.value,
            reason=reason,
            severity="critical",
            metadata=metadata or {},
        )
        self.events.append(event)

        logger.critical("🚨 EMERGENCIA: %s", reason)

    def reset(self) -> None:
        """Reactiva el robot tras emergencia."""
        if self.state == SafetyState.EMERGENCY:
            logger.info("Reseteando emergencia: %s", self.last_emergency_reason)
        self.state = SafetyState.NORMAL
        self.last_emergency_reason = None

    def enter_maintenance(self) -> None:
        """Modo mantenimiento (sin movimiento)."""
        self.state = SafetyState.MAINTENANCE
        logger.info("Modo mantenimiento activado")

    # ─── INFO ──────────────────────────────────────────────────

    def is_safe_to_move(self) -> bool:
        """Verifica si es seguro moverse."""
        return self.state == SafetyState.NORMAL

    def get_status(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "last_emergency": self.last_emergency_reason,
            "emergency_count": self.emergency_count,
            "limits": {
                "max_speed": self.limits.max_speed,
                "min_obstacle_distance_m": self.limits.min_obstacle_distance_m,
                "max_temperature_c": self.limits.max_temperature_c,
                "min_battery_percent": self.limits.min_battery_percent,
            },
            "recent_events": [e.to_dict() for e in self.events[-10:]],
        }

    def get_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.events[-limit:]]