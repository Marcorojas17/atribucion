"""
Atribución Payments — Suscripciones recurrentes.

Maneja preapproval (suscripciones mensuales).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from payments.mercadopago.client import MercadoPagoClientBase


logger = logging.getLogger(__name__)


@dataclass
class Subscription:
    """Suscripción recurrente."""

    id: str
    init_point: str
    status: str
    external_reference: str
    amount: float
    currency: str
    frequency_months: int


class SubscriptionService:
    """Servicio de suscripciones."""

    def __init__(self, client: MercadoPagoClientBase) -> None:
        self.client = client

    async def create(
        self,
        *,
        reason: str,
        amount: float,
        currency: str,
        frequency_months: int,
        customer_email: str,
        back_url: str,
        external_reference: str,
        start_date: datetime | None = None,
    ) -> Subscription:
        """Crea una suscripción recurrente."""
        payload = {
            "reason": reason,
            "auto_recurring": {
                "frequency": frequency_months,
                "frequency_type": "months",
                "transaction_amount": float(amount),
                "currency_id": currency,
                "start_date": (start_date.isoformat() if start_date else None),
            },
            "payer_email": customer_email,
            "back_url": back_url,
            "status": "pending",
            "external_reference": external_reference,
        }

        data = await self.client.post("/preapproval", json=payload)
        logger.info("Suscripción creada: %s", data["id"])

        return Subscription(
            id=data["id"],
            init_point=data["init_point"],
            status=data["status"],
            external_reference=external_reference,
            amount=amount,
            currency=currency,
            frequency_months=frequency_months,
        )

    async def get(self, subscription_id: str) -> dict:
        return await self.client.get(f"/preapproval/{subscription_id}")

    async def update(self, subscription_id: str, updates: dict) -> dict:
        return await self.client.put(f"/preapproval/{subscription_id}", json=updates)

    async def cancel(self, subscription_id: str) -> dict:
        """Cancela una suscripción."""
        data = await self.client.put(
            f"/preapproval/{subscription_id}",
            json={"status": "cancelled"},
        )
        logger.info("Suscripción cancelada: %s", subscription_id)
        return data

    async def pause(self, subscription_id: str) -> dict:
        return await self.client.put(
            f"/preapproval/{subscription_id}",
            json={"status": "paused"},
        )

    async def resume(self, subscription_id: str) -> dict:
        return await self.client.put(
            f"/preapproval/{subscription_id}",
            json={"status": "authorized"},
        )