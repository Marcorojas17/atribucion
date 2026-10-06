"""
Atribución Engine — Fallback Gemini.

Solo se usa cuando el usuario lo autoriza explícitamente.

Requiere: pip install google-generativeai
Requiere: GOOGLE_API_KEY en .env

Uso:
    backend = GeminiBackend(model="gemini-1.5-pro")
    response = backend.generate("Hola")
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class GeminiConfig:
    """Configuración del fallback Gemini."""

    model: str = "gemini-1.5-pro"
    api_key_env: str = "GOOGLE_API_KEY"
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 1024


class GeminiBackend:
    """Backend de inferencia con Gemini (fallback)."""

    name = "gemini"
    is_remote = True
    requires_authorization = True

    def __init__(self, config: GeminiConfig | None = None) -> None:
        if not GEMINI_AVAILABLE:
            raise RuntimeError(
                "google-generativeai no instalado. "
                "pip install google-generativeai"
            )

        self.config = config or GeminiConfig()

        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"{self.config.api_key_env} no configurado en .env"
            )

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(self.config.model)

        logger.info(
            "GeminiBackend configurado: %s (REMOTO — requiere autorización)",
            self.config.model,
        )

    # ─── GENERATE ──────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Genera texto con Gemini."""
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        generation_config = {
            "temperature": temperature or self.config.temperature,
            "top_p": self.config.top_p,
            "top_k": self.config.top_k,
            "max_output_tokens": max_tokens or self.config.max_tokens,
        }

        try:
            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
            )
            return response.text
        except Exception as e:
            logger.error("Gemini error: %s", e)
            raise RuntimeError(f"Gemini error: {e}") from e

    def stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Streaming con Gemini."""
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        generation_config = {
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_output_tokens": max_tokens or self.config.max_tokens,
        }

        response = self._model.generate_content(
            full_prompt,
            generation_config=generation_config,
            stream=True,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    # ─── INFO ──────────────────────────────────────────────────

    def is_available(self) -> bool:
        try:
            self._model.generate_content("ping")
            return True
        except Exception:
            return False

    def get_info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "model": self.config.model,
            "is_remote": self.is_remote,
            "requires_authorization": self.requires_authorization,
        }