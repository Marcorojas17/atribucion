"""
Atribución — Facturación.

Genera facturas en formato JSON + PDF.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4


@dataclass
class InvoiceLine:
    description: str
    quantity: int
    unit_price_eur: Decimal

    @property
    def total_eur(self) -> Decimal:
        return self.quantity * self.unit_price_eur


@dataclass
class Invoice:
    id: str
    tenant_id: str
    customer_email: str
    period_start: datetime
    period_end: datetime
    lines: list[InvoiceLine] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def subtotal_eur(self) -> Decimal:
        return sum(line.total_eur for line in self.lines)

    @property
    def tax_eur(self) -> Decimal:
        # IVA México 16%
        return (self.subtotal_eur * Decimal("0.16")).quantize(Decimal("0.01"))

    @property
    def total_eur(self) -> Decimal:
        return self.subtotal_eur + self.tax_eur

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "customer_email": self.customer_email,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "lines": [
                {
                    "description": line.description,
                    "quantity": line.quantity,
                    "unit_price_eur": str(line.unit_price_eur),
                    "total_eur": str(line.total_eur),
                }
                for line in self.lines
            ],
            "subtotal_eur": str(self.subtotal_eur),
            "tax_eur": str(self.tax_eur),
            "total_eur": str(self.total_eur),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


def create_invoice(
    tenant_id: str,
    customer_email: str,
    plan_name: str,
    plan_price_eur: Decimal,
    period_start: datetime,
    period_end: datetime,
) -> Invoice:
    """Crea una factura para un período de suscripción."""
    return Invoice(
        id=f"inv_{uuid4().hex}",
        tenant_id=tenant_id,
        customer_email=customer_email,
        period_start=period_start,
        period_end=period_end,
        lines=[
            InvoiceLine(
                description=f"Atribución — Plan {plan_name}",
                quantity=1,
                unit_price_eur=plan_price_eur,
            )
        ],
    )