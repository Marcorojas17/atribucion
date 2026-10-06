"""
Atribución Engine — Backend llama.cpp.

llama.cpp es la forma más portable de correr LLMs localmente:
- CPU sin GPU (funciona en Termux, Android, Linux, macOS)
- Cuantización 4-bit, 5-bit, 8-bit
- Sin dependencias pesadas

Requiere: pip install llama-cpp-python
Modelo: archivo .gguf descargado localmente

Uso:
    backend = LlamaCppBackend(model_path="~/models/llama-3-8b-q4.gguf")
    response = backend.generate("Hola")
    backend.unload()
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class LlamaCppConfig:
    """Configuración del backend llama.cpp."""

    model_path: str = ""
    n_ctx: int = 4096
    n_threads: int = 4
    n_gpu_layers: int = 0
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    repeat_penalty: float = 1.1
    max_tokens: int = 512
    verbose: bool = False


class LlamaCppBackend:
    """Backend de inferencia con llama.cpp."""

    name = "llama_cpp"

    def __init__(self, config: LlamaCppConfig | None = None) -> None:
        if not LLAMA_CPP_AVAILABLE:
            raise RuntimeError(
                "llama-cpp-python no instalado. "
                "pip install llama-cpp-python"
            )

        self.config = config or LlamaCppConfig()
        self._model: Any = None
        self._loaded = False

        if not self.config.model_path:
            raise ValueError("model_path es obligatorio")

        model_path = Path(os.path.expanduser(self.config.model_path))
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")

        self._model_path = str(model_path)
        logger.info("LlamaCppBackend configurado: %s", model_path.name)

    # ─── LIFECYCLE ─────────────────────────────────────────────

    def load(self) -> None:
        """Carga el modelo en memoria."""
        if self._loaded:
            return

        logger.info("Cargando modelo llama.cpp...")
        self._model = Llama(
            model_path=self._model_path,
            n_ctx=self.config.n_ctx,
            n_threads=self.config.n_threads,
            n_gpu_layers=self.config.n_gpu_layers,
            verbose=self.config.verbose,
        )
        self._loaded = True
        logger.info("Modelo cargado")

    def unload(self) -> None:
        """Libera el modelo de memoria."""
        if self._model is not None:
            del self._model
            self._model = None
        self._loaded = False
        logger.info("Modelo descargado")

    # ─── GENERATE ──────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Genera texto a partir de un prompt."""
        self.load()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._model.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature or self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            repeat_penalty=self.config.repeat_penalty,
        )

        return response["choices"][0]["message"]["content"]

    def stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ):
        """Genera texto en streaming."""
        self.load()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = self._model.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=self.config.temperature,
            stream=True,
        )

        for chunk in stream:
            delta = chunk["choices"][0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content

    # ─── INFO ──────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self._loaded

    def get_info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "model_path": self._model_path,
            "loaded": self._loaded,
            "config": {
                "n_ctx": self.config.n_ctx,
                "n_threads": self.config.n_threads,
                "n_gpu_layers": self.config.n_gpu_layers,
            },
        }