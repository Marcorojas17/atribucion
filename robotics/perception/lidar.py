"""
Atribución Robotics — Percepción LiDAR.

Procesamiento de datos de LiDAR 2D (scan) y 3D (point cloud).

Uso:
    lidar = LidarPerception(max_range_m=100)
    points = lidar.scan_to_points(ranges, angle_increment=0.0174)
    obstacles = lidar.detect_obstacles(ranges, threshold_m=1.0)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any


logger = logging.getLogger(__name__)


@dataclass
class LidarConfig:
    """Configuración del LiDAR."""

    max_range_m: float = 100.0
    min_range_m: float = 0.05
    angle_min_rad: float = -math.pi
    angle_max_rad: float = math.pi
    angle_increment_rad: float = 0.0174  # ~1 grado
    cluster_distance_m: float = 0.5
    min_cluster_size: int = 3


class LidarPerception:
    """Percepción LiDAR del robot."""

    def __init__(self, config: LidarConfig | None = None) -> None:
        self.config = config or LidarConfig()
        logger.info("LidarPerception lista (max_range=%.1fm)", self.config.max_range_m)

    # ─── CONVERSIÓN ────────────────────────────────────────────

    def scan_to_points(
        self,
        ranges: list[float],
        angle_increment: float | None = None,
        angle_min: float | None = None,
    ) -> list[tuple[float, float]]:
        """
        Convierte un scan (lista de distancias) a coordenadas
        cartesianas (x, y).
        """
        inc = angle_increment or self.config.angle_increment_rad
        amin = angle_min if angle_min is not None else self.config.angle_min_rad

        points: list[tuple[float, float]] = []
        angle = amin
        for r in ranges:
            if self.config.min_range_m < r < self.config.max_range_m:
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                points.append((x, y))
            angle += inc
        return points

    # ─── DETECCIÓN ─────────────────────────────────────────────

    def detect_obstacles(
        self,
        ranges: list[float],
        threshold_m: float = 1.0,
    ) -> list[dict[str, Any]]:
        """
        Detecta obstáculos dentro de un umbral de distancia.

        Devuelve lista de dicts con índice, distancia y ángulo.
        """
        obstacles: list[dict[str, Any]] = []
        angle = self.config.angle_min_rad

        for i, r in enumerate(ranges):
            if self.config.min_range_m < r < threshold_m:
                obstacles.append({
                    "index": i,
                    "distance_m": float(r),
                    "angle_rad": float(angle),
                    "angle_deg": float(math.degrees(angle)),
                })
            angle += self.config.angle_increment_rad

        return obstacles

    def cluster_obstacles(
        self,
        points: list[tuple[float, float]],
    ) -> list[list[tuple[float, float]]]:
        """
        Agrupa puntos cercanos en clusters (objetos).

        Algoritmo simple: distancia euclidiana entre puntos
        consecutivos.
        """
        if not points:
            return []

        clusters: list[list[tuple[float, float]]] = [[points[0]]]
        for prev, curr in zip(points, points[1:]):
            dist = math.sqrt((curr[0] - prev[0]) ** 2 + (curr[1] - prev[1]) ** 2)
            if dist < self.config.cluster_distance_m:
                clusters[-1].append(curr)
            else:
                clusters.append([curr])

        return [
            c for c in clusters
            if len(c) >= self.config.min_cluster_size
        ]

    def cluster_center(self, cluster: list[tuple[float, float]]) -> tuple[float, float]:
        """Centro de un cluster."""
        if not cluster:
            return (0.0, 0.0)
        x = sum(p[0] for p in cluster) / len(cluster)
        y = sum(p[1] for p in cluster) / len(cluster)
        return (x, y)

    # ─── ANÁLISIS ──────────────────────────────────────────────

    def distance_to_nearest_obstacle(self, ranges: list[float]) -> float:
        """Distancia al obstáculo más cercano."""
        valid = [
            r for r in ranges
            if self.config.min_range_m < r < self.config.max_range_m
        ]
        return min(valid) if valid else self.config.max_range_m

    def is_path_clear(
        self,
        ranges: list[float],
        front_angle_range_deg: float = 30.0,
        min_distance_m: float = 1.0,
    ) -> bool:
        """Verifica si el camino al frente está despejado."""
        half_range = front_angle_range_deg / 2
        half_range_rad = math.radians(half_range)

        angle = self.config.angle_min_rad
        for r in ranges:
            if -half_range_rad <= angle <= half_range_rad:
                if self.config.min_range_m < r < min_distance_m:
                    return False
            angle += self.config.angle_increment_rad
        return True