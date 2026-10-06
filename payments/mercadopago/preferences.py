"""
Atribución Payments — Preferencias de checkout.

Crea preferencias para Checkout Pro.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from payments.mercadopago.client import MercadoPagoClientBase


logger = logging.getLogger(__name__)


@dataclass
class Preference:
    """Preferencia de checkout."""

    id: str
    init_point: str
    sandbox_init_point: str
    external_reference: str


class PreferenceService:
    """Servicio de preferencias de checkout."""

    def __init__(self, client: MercadoPagoClientBase) -> None:
        self.client = client

    async def create(
        self,
        *,
        title: str,
        description: str,
        amount: float,
        currency: str,
        external_reference: str,
        customer_email: str,
        back_urls: dict[str, str],
        notification_url: str,
        metadata: dict[str, Any] | None = None,
        expires_minutes: int = 30,
    ) -> Preference:
        """Crea una preferencia de Checkout Pro."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)

        payload = {
            "items": [{
                "id": external_reference,
                "title": title,
                "description": description,
                "category_id": "services",
                "quantity": 1,
                "currency_id": currency,
                "unit_price": float(amount),
            }],
            "payer": {"email": customer_email},
            "back_urls": back_urls,
            "auto_return": "approved",
            "notification_url": notification_url,
            "external_reference": external_reference,
            "statement_descriptor": "ATRIBUCION",
            "expires": True,
            "expiration_date_from": now.isoformat(),
            "expiration_date_to": (now + timedelta(minutes=expires_minutes)).isoformat(),
            "metadata": metadata or {},
        }

        data = await self.client.post("/checkout/preferences", json=payload)
        logger.info("Preferencia creada: %s", data["id"])

        return Preference(
            id=data["id"],
            init_point=data["init_point"],
            sandbox_init_point=data.get("sandbox_init_point", data["init_point"]),
            external_reference=external_reference,
        )

    async def get(self, preference_id: str) -> dict:
        return await self.client.get(f"/checkout/preferences/{preference_id}")

    async def update(self, preference_id: str, updates: dict) -> dict:
        return await self.client.put(f"/checkout/preferences/{preference_id}", json=updates) 