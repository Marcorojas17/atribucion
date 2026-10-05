"""Atribución — Esquemas de pago."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class CheckoutRequest(BaseModel):
    """Solicitud de checkout."""

    plan_id: Literal["pro", "bank"]
    customer_email: EmailStr
    back_url_success: str
    back_url_failure: str
    back_url_pending: str


class CheckoutResponse(BaseModel):
    """Respuesta de checkout."""

    preference_id: str
    checkout_url: str
    sandbox_url: str


class WebhookPayload(BaseModel):
    """Payload de webhook de Mercado Pago."""

    id: int | None = None
    live_mode: bool | None = None
    type: str | None = None
    action: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class SubscriptionInfo(BaseModel):
    """Información de suscripción."""

    preapproval_id: str
    tenant_id: str
    plan_id: str
    status: str
    next_payment_date: datetime | None = None
    amount_mxn: float