"""
Atribución — Integración con Mercado Pago.

Implementa:
- Checkout Pro (pago único)
- Suscripciones recurrentes (preapproval)
- Validación de webhooks con HMAC-SHA256

Referencia: https://www.mercadopago.com.mx/developers
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from atribucion.billing.plans import Plan


logger = logging.getLogger(__name__)

MP_API_BASE = "https://api.mercadopago.com"


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────

def _get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# ─────────────────────────────────────────────────────────────
# RESULTADO
# ─────────────────────────────────────────────────────────────

@dataclass
class CheckoutResult:
    preference_id: str
    init_point: str
    sandbox_init_point: str


@dataclass
class SubscriptionResult:
    preapproval_id: str
    init_point: str
    status: str


# ─────────────────────────────────────────────────────────────
# CLIENTE
# ─────────────────────────────────────────────────────────────

class MercadoPagoClient:
    """Cliente HTTP para la API de Mercado Pago."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token or _get_env("MERCADOPAGO_ACCESS_TOKEN")
        if not self.access_token:
            raise RuntimeError(
                "MERCADOPAGO_ACCESS_TOKEN no configurado."
            )
        self._client = httpx.AsyncClient(
            base_url=MP_API_BASE,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def __aenter__(self) -> "MercadoPagoClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    # ─── Checkout Pro ───────────────────────────────────────────

    async def create_preference(
        self,
        *,
        plan: Plan,
        tenant_id: str,
        customer_email: str,
        back_urls: dict[str, str],
        notification_url: str,
    ) -> CheckoutResult:
        """Crea una preferencia de pago (Checkout Pro)."""
        payload = {
            "items": [
                {
                    "id": plan.id,
                    "title": f"Atribución — Plan {plan.name}",
                    "description": plan.description,
                    "category_id": "services",
                    "quantity": 1,
                    "currency_id": "MXN",
                    "unit_price": float(plan.price_mxn),
                }
            ],
            "payer": {"email": customer_email},
            "back_urls": back_urls,
            "auto_return": "approved",
            "notification_url": notification_url,
            "external_reference": f"{tenant_id}:{plan.id}",
            "statement_descriptor": "ATRIBUCION",
            "metadata": {"tenant_id": tenant_id, "plan_id": plan.id},
        }

        response = await self._client.post("/checkout/preferences", json=payload)
        response.raise_for_status()
        data = response.json()

        return CheckoutResult(
            preference_id=data["id"],
            init_point=data["init_point"],
            sandbox_init_point=data.get("sandbox_init_point", data["init_point"]),
        )

    # ─── Suscripciones ──────────────────────────────────────────

    async def create_subscription(
        self,
        *,
        plan: Plan,
        tenant_id: str,
        customer_email: str,
        back_url: str,
    ) -> SubscriptionResult:
        """Crea una suscripción recurrente (preapproval)."""
        payload = {
            "reason": f"Atribución — Plan {plan.name}",
            "auto_recurring": {
                "frequency": 1,
                "frequency_type": "months",
                "transaction_amount": float(plan.price_mxn),
                "currency_id": "MXN",
            },
            "payer_email": customer_email,
            "back_url": back_url,
            "status": "pending",
            "external_reference": f"{tenant_id}:{plan.id}",
        }

        response = await self._client.post("/preapproval", json=payload)
        response.raise_for_status()
        data = response.json()

        return SubscriptionResult(
            preapproval_id=data["id"],
            init_point=data["init_point"],
            status=data["status"],
        )

    # ─── Consultas ──────────────────────────────────────────────

    async def get_payment(self, payment_id: str) -> dict[str, Any]:
        response = await self._client.get(f"/v1/payments/{payment_id}")
        response.raise_for_status()
        return response.json()

    async def get_subscription(self, preapproval_id: str) -> dict[str, Any]:
        response = await self._client.get(f"/preapproval/{preapproval_id}")
        response.raise_for_status()
        return response.json()


# ─────────────────────────────────────────────────────────────
# VALIDACIÓN DE WEBHOOKS
# ─────────────────────────────────────────────────────────────

def verify_webhook_signature(
    *,
    x_signature: str,
    x_request_id: str,
    data_id: str,
    secret: str | None = None,
) -> bool:
    """
    Verifica la firma HMAC-SHA256 de un webhook de Mercado Pago.

    Formato del header:
        x-signature: ts=<ts>,v1=<hash>
        x-request-id: <uuid>

    Manifest a firmar:
        id:<data_id>;request-id:<x_request_id>;ts:<ts>;
    """
    secret = secret or _get_env("MERCADOPAGO_WEBHOOK_SECRET")
    if not secret:
        logger.error("MERCADOPAGO_WEBHOOK_SECRET no configurado.")
        return False

    parts: dict[str, str] = {}
    for p in x_signature.split(","):
        if "=" in p:
            k, v = p.strip().split("=", 1)
            parts[k] = v

    ts = parts.get("ts")
    v1 = parts.get("v1")
    if not ts or not v1:
        logger.warning("x-signature malformada: %s", x_signature)
        return False

    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    expected = hmac.new(
        secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, v1)


# ─────────────────────────────────────────────────────────────
# CONVERSIÓN EUR ↔ MXN
# ─────────────────────────────────────────────────────────────

async def eur_to_mxn(amount_eur: float) -> float:
    """
    Convierte EUR a MXN usando tasa cacheada.

    En producción consulta Banxico. Aquí usa fallback fijo.
    """
    rate = 20.1  # fallback
    return round(amount_eur * rate, 2)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()