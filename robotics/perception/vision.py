"""
Atribución Robotics — Percepción visual.

Wrapper para OpenCV. Requiere `opencv-python` instalado.

Uso:
    vision = VisionPerception(camera_id=0)
    frame = vision.capture_frame()
    objects = vision.detect_objects(frame)
    vision.release()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class VisionConfig:
    """Configuración de la cámara."""

    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    min_object_area: int = 500


class VisionPerception:
    """Percepción visual del robot."""

    def __init__(self, config: VisionConfig | None = None) -> None:
        if not CV2_AVAILABLE:
            raise RuntimeError(
                "opencv-python no instalado. pip install opencv-python"
            )

        self.config = config or VisionConfig()
        self._cap: Any = None
        logger.info("VisionPerception lista (camera=%d)", self.config.camera_id)

    # ─── CAPTURE ───────────────────────────────────────────────

    def _ensure_capture(self) -> None:
        if self._cap is None or not self._cap.isOpened():
            self._cap = cv2.VideoCapture(self.config.camera_id)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self._cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            if not self._cap.isOpened():
                raise RuntimeError(
                    f"No se pudo abrir cámara {self.config.camera_id}"
                )

    def capture_frame(self) -> Any:
        """Captura un frame de la cámara."""
        self._ensure_capture()
        ret, frame = self._cap.read()
        if not ret:
            raise RuntimeError("No se pudo capturar frame")
        return frame

    # ─── DETECTION ─────────────────────────────────────────────

    def detect_objects(self, frame: Any) -> list[dict[str, Any]]:
        """
        Detección básica de objetos por contornos.

        Devuelve lista de dicts con:
        - area: área del contorno
        - bbox: (x, y, w, h)
        - center: (cx, cy)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(
            blurred, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        objects: list[dict[str, Any]] = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < self.config.min_object_area:
                continue
            x, y, w, h = cv2.boundingRect(c)
            objects.append({
                "area": float(area),
                "bbox": (int(x), int(y), int(w), int(h)),
                "center": (int(x + w / 2), int(y + h / 2)),
            })
        return objects

    def detect_faces(self, frame: Any) -> list[dict[str, Any]]:
        """Detección de rostros con Haar cascade."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        cascade = cv2.CascadeClassifier(cascade_path)

        faces = cascade.detectMultiScale(gray, 1.1, 4)
        return [
            {"bbox": (int(x), int(y), int(w), int(h))}
            for x, y, w, h in faces
        ]

    # ─── UTILITIES ─────────────────────────────────────────────

    def save_frame(self, frame: Any, path: str) -> None:
        """Guarda un frame en disco."""
        cv2.imwrite(path, frame)

    def resize(self, frame: Any, width: int, height: int) -> Any:
        """Redimensiona un frame."""
        return cv2.resize(frame, (width, height))

    def release(self) -> None:
        """Libera la cámara."""
        if self._cap:
            self._cap.release()
            self._cap = None
        logger.info("VisionPerception liberada")