"""
Atribución Payments — Cliente base de Mercado Pago.

Wrapper HTTP con retries, timeouts y logging.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx


logger = logging.getLogger(__name__)

MP_API_BASE = "https://api.mercadopago.com"


@dataclass
class MPConfig:
    """Configuración del cliente Mercado Pago."""

    access_token: str = ""
    base_url: str = MP_API_BASE
    timeout_seconds: float = 30.0
    max_retries: int = 3
    sandbox: bool = True

    def __post_init__(self) -> None:
        if not self.access_token:
            self.access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
        if not self.access_token:
            raise RuntimeError("MERCADOPAGO_ACCESS_TOKEN no configurado")


class MercadoPagoClientBase:
    """Cliente base HTTP para Mercado Pago."""

    def __init__(self, config: MPConfig | None = None) -> None:
        self.config = config or MPConfig()
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
                "User-Agent": "atribucion-mp/0.1.0",
            },
            timeout=self.config.timeout_seconds,
        )
        logger.info("MP client listo (sandbox=%s)", self.config.sandbox)

    async def __aenter__(self) -> "MercadoPagoClientBase":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    # ─── REQUEST CON RETRIES ───────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Request con retries exponenciales."""
        import asyncio

        last_error: Exception | None = None

        for attempt in range(self.config.max_retries):
            try:
                response = await self._client.request(
                    method=method,
                    url=path,
                    json=json,
                    params=params,
                )

                if response.status_code >= 500:
                    raise RuntimeError(f"MP error {response.status_code}: {response.text[:200]}")

                if response.status_code >= 400:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    raise ValueError(
                        f"MP error {response.status_code}: "
                        f"{error_data.get('message', response.text[:200])}"
                    )

                return response.json()

            except (httpx.RequestError, RuntimeError) as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning("MP retry %d/%d en %ds: %s", attempt + 1, self.config.max_retries, wait, e)
                    await asyncio.sleep(wait)

        raise RuntimeError(f"MP falló tras {self.config.max_retries} intentos: {last_error}")

    async def get(self, path: str, params: dict | None = None) -> dict:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict | None = None) -> dict:
        return await self._request("POST", path, json=json)

    async def put(self, path: str, json: dict | None = None) -> dict:
        return await self._request("PUT", path, json=json)

    async def delete(self, path: str) -> dict:
        return await self._request("DELETE", path)