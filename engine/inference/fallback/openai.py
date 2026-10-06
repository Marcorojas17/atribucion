"""
Atribución Engine — Fallback OpenAI.

Solo se usa cuando:
1. El usuario lo autoriza explícitamente.
2. La inferencia local no está disponible.
3. El router lo decide según política.

NUNCA se activa por defecto. Soberanía primero.

Requiere: pip install openai (ya en requirements)
Requiere: OPENAI_API_KEY en .env

Uso:
    backend = OpenAIBackend(model="gpt-4o-mini")
    response = backend.generate("Hola")
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator

try:
    from openai import OpenAI, APIError, RateLimitError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class OpenAIConfig:
    """Configuración del fallback OpenAI."""

    model: str = "gpt-4o-mini"
    api_key_env: str = "OPENAI_API_KEY"
    base_url: str | None = None
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 512
    timeout_seconds: float = 60.0
    organization: str | None = None


class OpenAIBackend:
    """Backend de inferencia con OpenAI (fallback)."""

    name = "openai"
    is_remote = True
    requires_authorization = True

    def __init__(self, config: OpenAIConfig | None = None) -> None:
        if not OPENAI_AVAILABLE:
            raise RuntimeError("openai no instalado. pip install openai")

        self.config = config or OpenAIConfig()

        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"{self.config.api_key_env} no configurado en .env"
            )

        kwargs: dict[str, Any] = {
            "api_key": api_key,
            "timeout": self.config.timeout_seconds,
        }
        if self.config.base_url:
            kwargs["base_url"] = self.config.base_url
        if self.config.organization:
            kwargs["organization"] = self.config.organization

        self._client = OpenAI(**kwargs)
        logger.info(
            "OpenAIBackend configurado: %s (REMOTO — requiere autorización)",
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
        """Genera texto con OpenAI."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temperature or self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=max_tokens or self.config.max_tokens,
            )
            return response.choices[0].message.content or ""
        except RateLimitError as e:
            logger.error("OpenAI rate limit: %s", e)
            raise RuntimeError(f"Rate limit: {e}") from e
        except APIError as e:
            logger.error("OpenAI API error: %s", e)
            raise RuntimeError(f"API error: {e}") from e

    def stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Streaming con OpenAI."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    # ─── INFO ──────────────────────────────────────────────────

    def is_available(self) -> bool:
        try:
            self._client.models.list()
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

    def close(self) -> None:
        self._client.close()