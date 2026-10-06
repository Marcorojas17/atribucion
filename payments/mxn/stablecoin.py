"""
Atribución Payments — Integración con MXNB.

MXNB es la stablecoin regulada de Bitso, anclada 1:1 al MXN.
Permite pagos en pesos sin fricción bancaria.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx


logger = logging.getLogger(__name__)


@dataclass
class MXNBConfig:
    """Configuración de la integración con Bitso."""

    api_url: str = "https://api.bitso.com/v3"
    api_key: str = ""
    api_secret: str = ""
    network: str = "xrpl"


class MXNBService:
    """Servicio de integración con MXNB."""

    def __init__(self, config: MXNBConfig | None = None) -> None:
        self.config = config or MXNBConfig(
            api_key=os.getenv("BITSO_API_KEY", ""),
            api_secret=os.getenv("BITSO_API_SECRET", ""),
        )
        self._client = httpx.AsyncClient(
            base_url=self.config.api_url,
            timeout=30.0,
        )
        logger.info("MXNB service listo (network=%s)", self.config.network)

    async def close(self) -> None:
        await self._client.aclose()

    # ─── CONVERSIÓN MXN ↔ MXNB ─────────────────────────────────

    async def mxn_to_mxnb(self, amount_mxn: float) -> float:
        """MXN → MXNB (1:1, sin comisión)."""
        return amount_mxn

    async def mxnb_to_mxn(self, amount_mxnb: float) -> float:
        """MXNB → MXN (1:1, sin comisión)."""
        return amount_mxnb

    # ─── BALANCE ───────────────────────────────────────────────

    async def get_balance(self) -> dict[str, Any]:
        """Consulta el balance de MXNB."""
        try:
            response = await self._client.get("/balance")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error("Error consultando balance MXNB: %s", e)
            return {"error": str(e)}

    # ─── TRANSFERENCIAS ────────────────────────────────────────

    async def send(
        self,
        *,
        to_address: str,
        amount_mxnb: float,
        note: str = "",
    ) -> dict[str, Any]:
        """Envía MXNB a una dirección."""
        payload = {
            "currency": "mxnb",
            "amount": str(amount_mxnb),
            "address": to_address,
            "network": self.config.network,
            "note": note,
        }

        try:
            response = await self._client.post("/withdrawals", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("MXNB enviado: %s", data.get("id"))
            return data
        except httpx.RequestError as e:
            logger.error("Error enviando MXNB: %s", e)
            raise RuntimeError(f"MXNB send error: {e}") from e