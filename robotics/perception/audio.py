"""
Atribución Robotics — Percepción de audio.

Captura y procesamiento básico de audio.
Requiere `sounddevice` y `numpy` opcionalmente.

Uso:
    audio = AudioPerception(sample_rate=16000)
    data = audio.capture(duration_seconds=1.0)
    volume = audio.detect_volume(data)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import sounddevice as sd
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Configuración de audio."""

    sample_rate: int = 16000
    channels: int = 1
    dtype: str = "int16"
    device: int | None = None


class AudioPerception:
    """Percepción de audio del robot."""

    def __init__(self, config: AudioConfig | None = None) -> None:
        self.config = config or AudioConfig()
        logger.info(
            "AudioPerception lista (sample_rate=%dHz)",
            self.config.sample_rate,
        )

    # ─── CAPTURA ───────────────────────────────────────────────

    def capture(self, duration_seconds: float = 1.0) -> bytes:
        """Captura audio del micrófono."""
        if not SD_AVAILABLE:
            raise RuntimeError(
                "sounddevice no instalado. pip install sounddevice"
            )
        if not NUMPY_AVAILABLE:
            raise RuntimeError("numpy no instalado. pip install numpy")

        samples = int(self.config.sample_rate * duration_seconds)
        recording = sd.rec(
            samples,
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype=self.config.dtype,
            device=self.config.device,
        )
        sd.wait()
        return recording.tobytes()

    # ─── ANÁLISIS ──────────────────────────────────────────────

    def detect_volume(self, audio_bytes: bytes) -> float:
        """Nivel de volumen aproximado (0.0 a 1.0)."""
        if not audio_bytes:
            return 0.0
        total = sum(abs(b - 128) for b in audio_bytes)
        return min(1.0, total / len(audio_bytes) / 128.0)

    def detect_rms(self, audio_bytes: bytes) -> float:
        """Root Mean Square del audio."""
        if not audio_bytes:
            return 0.0
        if NUMPY_AVAILABLE:
            arr = np.frombuffer(audio_bytes, dtype=self.config.dtype)
            return float(np.sqrt(np.mean(arr.astype(float) ** 2)))
        squares = sum((b - 128) ** 2 for b in audio_bytes)
        return math.sqrt(squares / len(audio_bytes))

    def detect_silence(
        self,
        audio_bytes: bytes,
        threshold: float = 0.05,
    ) -> bool:
        """Verifica si el audio es silencio."""
        return self.detect_volume(audio_bytes) < threshold

    def detect_peaks(self, audio_bytes: bytes, num_peaks: int = 5) -> list[int]:
        """Detecta picos de volumen (índices)."""
        if not NUMPY_AVAILABLE or not audio_bytes:
            return []
        arr = np.frombuffer(audio_bytes, dtype=self.config.dtype)
        window = max(1, len(arr) // num_peaks)
        peaks = []
        for i in range(num_peaks):
            start = i * window
            end = min(start + window, len(arr))
            chunk = arr[start:end]
            if len(chunk) > 0:
                peaks.append(start + int(np.argmax(np.abs(chunk))))
        return peaks

    # ─── UTILIDADES ────────────────────────────────────────────

    def save_to_wav(
        self,
        audio_bytes: bytes,
        path: str,
    ) -> None:
        """Guarda audio en formato WAV."""
        import wave

        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(2)  # int16 = 2 bytes
            wf.setframerate(self.config.sample_rate)
            wf.writeframes(audio_bytes)

    def list_devices(self) -> list[dict[str, Any]]:
        """Lista dispositivos de audio disponibles."""
        if not SD_AVAILABLE:
            return []
        devices = sd.query_devices()
        return [
            {
                "index": i,
                "name": d["name"],
                "channels": d["max_input_channels"],
                "sample_rate": d["default_samplerate"],
            }
            for i, d in enumerate(devices)
        ]