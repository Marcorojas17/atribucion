"""
Atribución Engine — Backend MLX.

MLX es el framework de Apple para Apple Silicon (M1/M2/M3/M4).
Optimizado para memoria unificada, ideal para MacBooks y iPads.

Requiere: pip install mlx-lm (solo en macOS con Apple Silicon)
Modelos: se descargan automáticamente de HuggingFace

Uso:
    backend = MLXBackend(model="mlx-community/Llama-3.2-3B-Instruct-4bit")
    response = backend.generate("Hola")
"""

from __future__ import annotations

import logging
import platform
from dataclasses import dataclass
from typing import Any, Iterator

try:
    import mlx.core as mx
    from mlx_lm import generate as mlx_generate
    from mlx_lm import load as mlx_load
    from mlx_lm import stream_generate as mlx_stream
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class MLXConfig:
    """Configuración del backend MLX."""

    model: str = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    repetition_penalty: float = 1.1
    trust_remote_code: bool = False


class MLXBackend:
    """Backend de inferencia con MLX (Apple Silicon)."""

    name = "mlx"

    def __init__(self, config: MLXConfig | None = None) -> None:
        if not MLX_AVAILABLE:
            raise RuntimeError(
                "mlx-lm no instalado. Requiere Apple Silicon. "
                "pip install mlx-lm"
            )

        if platform.system() != "Darwin":
            raise RuntimeError(
                f"MLX solo funciona en macOS. Detectado: {platform.system()}"
            )

        self.config = config or MLXConfig()
        self._model: Any = None
        self._tokenizer: Any = None
        self._loaded = False

        logger.info("MLXBackend configurado: %s", self.config.model)

    # ─── LIFECYCLE ─────────────────────────────────────────────

    def load(self) -> None:
        """Carga el modelo en memoria."""
        if self._loaded:
            return

        logger.info("Cargando modelo MLX: %s", self.config.model)
        self._model, self._tokenizer = mlx_load(
            self.config.model,
            trust_remote_code=self.config.trust_remote_code,
        )
        self._loaded = True
        logger.info("Modelo MLX cargado")

    def unload(self) -> None:
        """Libera el modelo."""
        self._model = None
        self._tokenizer = None
        self._loaded = False
        if MLX_AVAILABLE:
            mx.metal.clear_cache()
        logger.info("Modelo MLX descargado")

    # ─── GENERATE ──────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Genera texto con MLX."""
        self.load()

        formatted = self._format_prompt(prompt, system)

        response = mlx_generate(
            self._model,
            self._tokenizer,
            prompt=formatted,
            max_tokens=max_tokens or self.config.max_tokens,
            temp=temperature or self.config.temperature,
            top_p=self.config.top_p,
            repetition_penalty=self.config.repetition_penalty,
            verbose=False,
        )
        return response.strip()

    def stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Streaming con MLX."""
        self.load()

        formatted = self._format_prompt(prompt, system)

        for response in mlx_stream(
            self._model,
            self._tokenizer,
            prompt=formatted,
            max_tokens=max_tokens or self.config.max_tokens,
            temp=self.config.temperature,
            top_p=self.config.top_p,
        ):
            text = response.text
            if text:
                yield text

    # ─── HELPERS ───────────────────────────────────────────────

    def _format_prompt(self, prompt: str, system: str | None) -> str:
        """Formatea el prompt según el chat template del modelo."""
        if system:
            return f"<|system|>\n{system}\n<|user|>\n{prompt}\n<|assistant|>\n"
        return f"<|user|>\n{prompt}\n<|assistant|>\n"

    # ─── INFO ──────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self._loaded

    def get_info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "model": self.config.model,
            "loaded": self._loaded,
            "platform": platform.system(),
            "available": MLX_AVAILABLE,
        }