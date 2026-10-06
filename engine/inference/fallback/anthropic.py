"""
Atribución Engine — Fallback Anthropic.

Solo se usa cuando el usuario lo autoriza explícitamente.

Requiere: pip install anthropic
Requiere: ANTHROPIC_API_KEY en .env

Uso:
    backend = AnthropicBackend(model="claude-3-5-sonnet-20241022")
    response = backend.generate("Hola")
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator

try:
    from anthropic import Anthropic, APIError, RateLimitError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class AnthropicConfig:
    """Configuración del fallback Anthropic."""

    model: str = "claude-3-5-sonnet-20241022"
    api_key_env: str = "ANTHROPIC_API_KEY"
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 1024
    timeout_seconds: float = 60.0


class AnthropicBackend:
    """Backend de inferencia con Anthropic (fallback)."""

    name = "anthropic"
    is_remote = True
    requires_authorization = True

    def __init__(self, config: AnthropicConfig | None = None) -> None:
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("anthropic no instalado. pip install anthropic")

        self.config = config or AnthropicConfig()

        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"{self.config.api_key_env} no configurado en .env"
            )

        self._client = Anthropic(
            api_key=api_key,
            timeout=self.config.timeout_seconds,
        )
        logger.info(
            "AnthropicBackend configurado: %s (REMOTO — requiere autorización)",
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
        """Genera texto con Anthropic."""
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        try:
            response = self._client.messages.create(**kwargs)
            return response.content[0].text
        except RateLimitError as e:
            logger.error("Anthropic rate limit: %s", e)
            raise RuntimeError(f"Rate limit: {e}") from e
        except APIError as e:
            logger.error("Anthropic API error: %s", e)
            raise RuntimeError(f"API error: {e}") from e

    def stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Streaming con Anthropic."""
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        with self._client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text

    # ─── INFO ──────────────────────────────────────────────────

    def is_available(self) -> bool:
        try:
            self._client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
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