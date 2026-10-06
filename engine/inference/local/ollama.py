"""
Atribución Engine — Backend Ollama.

Ollama es la forma más fácil de correr LLMs localmente:
- Instala con un comando
- Descarga modelos con `ollama pull llama3`
- API HTTP local en http://localhost:11434

Requiere: pip install httpx (ya en requirements)
Requiere: Ollama instalado y corriendo

Uso:
    backend = OllamaBackend(model="llama3")
    response = backend.generate("Hola")
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Iterator

import httpx


logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Configuración del backend Ollama."""

    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 512
    timeout_seconds: float = 120.0


class OllamaBackend:
    """Backend de inferencia con Ollama."""

    name = "ollama"

    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds,
        )
        logger.info(
            "OllamaBackend configurado: %s @ %s",
            self.config.model,
            self.config.base_url,
        )

    # ─── HEALTH ────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Verifica que Ollama esté corriendo."""
        try:
            r = self._client.get("/api/tags")
            return r.status_code == 200
        except httpx.RequestError:
            return False

    def list_models(self) -> list[str]:
        """Lista modelos disponibles en Ollama."""
        try:
            r = self._client.get("/api/tags")
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except (httpx.RequestError, KeyError):
            return []

    # ─── GENERATE ──────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Genera texto con Ollama."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": max_tokens or self.config.max_tokens,
            },
        }

        try:
            r = self._client.post("/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
            return data["message"]["content"]
        except (httpx.RequestError, KeyError) as e:
            logger.error("Error en Ollama: %s", e)
            raise RuntimeError(f"Ollama error: {e}") from e

    def stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Streaming con Ollama."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": max_tokens or self.config.max_tokens,
            },
        }

        with self._client.stream("POST", "/api/chat", json=payload) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    # ─── LIFECYCLE ─────────────────────────────────────────────

    def pull_model(self, model: str) -> None:
        """Descarga un modelo (bloqueante)."""
        logger.info("Descargando modelo %s...", model)
        try:
            r = self._client.post("/api/pull", json={"name": model})
            r.raise_for_status()
        except httpx.RequestError as e:
            raise RuntimeError(f"Error descargando {model}: {e}") from e

    def close(self) -> None:
        self._client.close()

    def get_info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "base_url": self.config.base_url,
            "model": self.config.model,
            "available": self.is_available(),
            "models_installed": self.list_models(),
        }