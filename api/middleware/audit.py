"""
Atribución — Audit log middleware.

Registra cada request en un log inmutable (JSONL).
Cumple con EU AI Act Art. 12 (registro automático de eventos).
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request


AUDIT_DIR = Path.home() / ".atribucion" / "logs"
AUDIT_FILE = AUDIT_DIR / "access.jsonl"


# ─────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────

async def audit_middleware(request: Request, call_next):
    """
    Middleware FastAPI que registra cada request.

    Formato: JSONL (una línea por request).
    """
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000

    # Registrar
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "ip": _get_client_ip(request),
        "user_agent": request.headers.get("user-agent", "")[:200],
        "has_auth": bool(request.headers.get("authorization")),
    }

    _persist(entry)

    # Añadir header de trazabilidad
    response.headers["X-Audit-Logged"] = "true"
    return response


def _get_client_ip(request: Request) -> str:
    """Extrae la IP del cliente (considerando proxies)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _persist(entry: dict[str, Any]) -> None:
    """Persiste una entrada en el log."""
    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        # No fallar la request si el log falla
        pass