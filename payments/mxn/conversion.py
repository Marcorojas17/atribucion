"""
Atribución Payments — Conversión EUR ↔ MXN.

Conversión de divisas con tasa cacheada.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from payments.mxn.oracle import get_eur_mxn_rate


logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Resultado de conversión."""

    amount_in: float
    currency_in: str
    amount_out: float
    currency_out: str
    rate: float
    timestamp: str


async def eur_to_mxn(amount_eur: float) -> float:
    """Convierte EUR a MXN."""
    rate = await get_eur_mxn_rate()
    return round(amount_eur * rate, 2)


async def mxn_to_eur(amount_mxn: float) -> float:
    """Convierte MXN a EUR."""
    rate = await get_eur_mxn_rate()
    if rate == 0:
        raise ValueError("Tasa EUR/MXN inválida")
    return round(amount_mxn / rate, 2)


async def convert(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> ConversionResult:
    """Convierte entre EUR y MXN."""
    if from_currency == to_currency:
        return ConversionResult(
            amount_in=amount,
            currency_in=from_currency,
            amount_out=amount,
            currency_out=to_currency,
            rate=1.0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    rate = await get_eur_mxn_rate()

    if from_currency == "EUR" and to_currency == "MXN":
        result = round(amount * rate, 2)
    elif from_currency == "MXN" and to_currency == "EUR":
        result = round(amount / rate, 2)
    else:
        raise ValueError(f"Par no soportado: {from_currency}/{to_currency}")

    return ConversionResult(
        amount_in=amount,
        currency_in=from_currency,
        amount_out=result,
        currency_out=to_currency,
        rate=rate,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )