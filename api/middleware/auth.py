"""
Atribución — Middleware de autenticación.

Autenticación por API key:
    Authorization: Bearer ak_live_<32_hex>

En producción, consulta la base de datos para validar la key
y cargar el TenantContext. Por ahora, valida el formato y
devuelve un contexto mock para permitir desarrollo local.

Cumple con:
- OWASP ASVS V2 (autenticación)
- Zero Trust (verificar cada request)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Header, HTTPException, status


# ─────────────────────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TenantContext:
    """Contexto del tenant autenticado."""

    id: str
    email: str
    plan_id: str
    created_at: datetime


# ─────────────────────────────────────────────────────────────
# VALIDACIÓN
# ─────────────────────────────────────────────────────────────

API_KEY_PATTERN = re.compile(r"^Bearer\s+(ak_(live|test)_[a-fA-F0-9]{64})$")


def verify_api_key(authorization: str) -> str:
    """
    Valida el formato de la API key.

    Formato esperado:
        Authorization: Bearer ak_live_<64_hex>
        Authorization: Bearer ak_test_<64_hex>

    Devuelve la key extraída (sin el "Bearer ").
    Lanza HTTPException 401 si el formato no es válido.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    match = API_KEY_PATTERN.match(authorization)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key con formato inválido. Esperado: ak_live_<64_hex>.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return match.group(1)


# ─────────────────────────────────────────────────────────────
# DEPENDENCIA FASTAPI
# ─────────────────────────────────────────────────────────────

async def get_current_tenant(
    authorization: str = Header(..., description="Bearer <api_key>"),
) -> TenantContext:
    """
    Dependencia FastAPI: extrae y valida el tenant.

    En producción:
        1. Verifica la key contra la base de datos (hash).
        2. Carga el tenant y sus permisos.
        3. Aplica rate limiting por tenant.

    Por ahora (mock):
        - Valida el formato.
        - Deriva un tenant_id determinístico del hash de la key.
        - Devuelve un plan 'pro' por defecto.
    """
    api_key = verify_api_key(authorization)

    # Tenant determinístico derivado de la key (para desarrollo)
    tenant_hash = hashlib.sha256(api_key.encode()).hexdigest()[:24]
    tenant_id = f"tnt_{tenant_hash}"

    # Plan por defecto (en producción vendría de la DB)
    plan_id = "pro"

    return TenantContext(
        id=tenant_id,
        email="dev@atribucion.io",
        plan_id=plan_id,
        created_at=datetime.now(timezone.utc),
    )