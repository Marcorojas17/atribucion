"""
Atribución Payments — Oráculo de tipo de cambio.

Obtiene tasa EUR/MXN desde Banxico o fallback.
Cachea por 6 horas.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx


logger = logging.getLogger(__name__)

BANXICO_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno"
CACHE_TTL_HOURS = 6
FALLBACK_RATE = 20.1


async def get_eur_mxn_rate() -> float:
    """
    Obtiene la tasa EUR/MXN actual.

    Orden de preferencia:
    1. Cache local (si es < 6h)
    2. Banxico API (si hay token)
    3. Fallback fijo
    """
    cached = _read_cache()
    if cached:
        return cached

    try:
        rate = await _fetch_from_banxico()
        if rate > 0:
            _write_cache(rate)
            return rate
    except Exception as e:
        logger.warning("No se pudo obtener tasa de Banxico: %s", e)

    logger.warning("Usando tasa fallback: %.2f", FALLBACK_RATE)
    return FALLBACK_RATE


async def _fetch_from_banxico() -> float:
    """Consulta la API de Banxico."""
    token = os.getenv("BANXICO_TOKEN", "")
    if not token:
        raise RuntimeError("BANXICO_TOKEN no configurado")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            BANXICO_URL,
            headers={"Bmx-Token": token},
        )
        response.raise_for_status()
        data = response.json()

    try:
        rate = float(data["bmx"]["series"][0]["datos"][0]["dato"])
        logger.info("Tasa EUR/MXN obtenida de Banxico: %.4f", rate)
        return rate
    except (KeyError, IndexError, ValueError) as e:
        raise RuntimeError(f"Respuesta de Banxico inválida: {e}") from e


def _cache_path() -> Path:
    path = Path.home() / ".atribucion" / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path / "eur_mxn_rate.json"


def _read_cache() -> float | None:
    path = _cache_path()
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cached_at = datetime.fromisoformat(data["timestamp"])
        if datetime.now(timezone.utc) - cached_at < timedelta(hours=CACHE_TTL_HOURS):
            return data["rate"]
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return None
    return None


def _write_cache(rate: float) -> None:
    path = _cache_path()
    data = {
        "rate": rate,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(data), encoding="utf-8")