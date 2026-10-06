"""
Atribución Payments — Cliente PSC (Prestador de Servicios de Certificación).

Integración con PSC acreditado por la Secretaría de Economía
para cumplir con NOM-151-SCFI-2016.

PSCs soportados:
- Incode
- Mifiel
- JAAK
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx


logger = logging.getLogger(__name__)


@dataclass
class PSCConfig:
    """Configuración del PSC."""

    provider: str = "mifiel"
    api_key: str = ""
    api_secret: str = ""
    sandbox: bool = True


class PSCClient:
    """Cliente para PSC acreditado."""

    ENDPOINTS = {
        "mifiel": {
            "prod": "https://app.mifiel.com/api/v1",
            "sandbox": "https://sandbox.mifiel.com/api/v1",
        },
        "incode": {
            "prod": "https://api.incode.com/v1",
            "sandbox": "https://sandbox.incode.com/v1",
        },
        "jaak": {
            "prod": "https://api.jaak.io/v1",
            "sandbox": "https://sandbox.jaak.io/v1",
        },
    }

    def __init__(self, config: PSCConfig | None = None) -> None:
        self.config = config or PSCConfig(
            provider=os.getenv("PSC_PROVIDER", "mifiel"),
            api_key=os.getenv("PSC_API_KEY", ""),
            api_secret=os.getenv("PSC_API_SECRET", ""),
        )

        env = "sandbox" if self.config.sandbox else "prod"
        base_url = self.ENDPOINTS.get(self.config.provider, {}).get(env)

        if not base_url:
            raise ValueError(f"PSC no soportado: {self.config.provider}")

        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "atribucion-psc/0.1.0",
            },
            timeout=30.0,
        )
        logger.info("PSC client listo: %s (%s)", self.config.provider, env)

    async def close(self) -> None:
        await self._client.aclose()

    # ─── API ───────────────────────────────────────────────────

    async def stamp_document(
        self,
        document_hash: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Sella un documento (envía hash al PSC).

        Devuelve constancia NOM-151.
        """
        payload = {
            "hash": document_hash,
            "hash_algorithm": "sha256",
            "metadata": metadata or {},
        }

        try:
            response = await self._client.post("/documents/stamp", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("Documento sellado: %s", data.get("id"))
            return data
        except httpx.RequestError as e:
            logger.error("Error sellando documento: %s", e)
            raise RuntimeError(f"PSC stamp error: {e}") from e

    async def verify_constancia(self, constancia_id: str) -> dict[str, Any]:
        """Verifica una constancia NOM-151."""
        response = await self._client.get(f"/documents/{constancia_id}")
        response.raise_for_status()
        return response.json()

    async def download_constancia(self, constancia_id: str) -> bytes:
        """Descarga el PDF de la constancia."""
        response = await self._client.get(f"/documents/{constancia_id}/pdf")
        response.raise_for_status()
        return response.content