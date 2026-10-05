"""
Atribución — Rate limiting por tenant.

Limita requests por API key usando sliding window.
- Free: 100 req/min
- Pro: 1.000 req/min
- Bank: 10.000 req/min

Sin dependencias externas: usa memoria con deque.
En producción, reemplazar por Redis.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import HTTPException, Request, status


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────

LIMITS_BY_PLAN: dict[str, int] = {
    "free": 100,
    "pro": 1_000,
    "bank": 10_000,
}

WINDOW_SECONDS = 60


# ─────────────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────────────

@dataclass
class Window:
    """Sliding window de timestamps."""

    timestamps: deque[float]


_windows: dict[str, Window] = defaultdict(lambda: Window(deque()))


# ─────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────

def check_rate_limit(
    identifier: str,
    plan: str = "free",
) -> tuple[bool, int, int]:
    """
    Verifica el rate limit para un identifier.

    Devuelve (allowed, remaining, reset_in_seconds).
    """
    limit = LIMITS_BY_PLAN.get(plan, LIMITS_BY_PLAN["free"])
    now = time.time()
    window = _windows[identifier]

    # Limpiar timestamps viejos
    cutoff = now - WINDOW_SECONDS
    while window.timestamps and window.timestamps[0] < cutoff:
        window.timestamps.popleft()

    remaining = max(0, limit - len(window.timestamps))

    if len(window.timestamps) >= limit:
        reset_in = int(window.timestamps[0] + WINDOW_SECONDS - now) + 1
        return (False, 0, reset_in)

    window.timestamps.append(now)
    return (True, remaining - 1, WINDOW_SECONDS)


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware FastAPI para aplicar rate limiting.

    Usa el header Authorization como identifier.
    """
    # Endpoints públicos sin rate limit
    if request.url.path in {"/", "/v1/health", "/docs", "/redoc", "/openapi.json"}:
        return await call_next(request)

    # Identifier = API key o IP
    auth = request.headers.get("authorization", "")
    identifier = auth or request.client.host if request.client else "unknown"

    allowed, remaining, reset_in = check_rate_limit(identifier, plan="pro")

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit excedido. Reintenta en {reset_in}s.",
            headers={
                "X-RateLimit-Limit": str(LIMITS_BY_PLAN["pro"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + reset_in),
                "Retry-After": str(reset_in),
            },
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(LIMITS_BY_PLAN["pro"])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + reset_in)
    return response