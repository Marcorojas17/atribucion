"""
Atribución Payments — Verificación de webhooks.

Valida la firma HMAC-SHA256 de webhooks de Mercado Pago.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os


logger = logging.getLogger(__name__)


def verify_webhook_signature(
    *,
    x_signature: str,
    x_request_id: str,
    data_id: str,
    secret: str | None = None,
) -> bool:
    """
    Verifica la firma HMAC-SHA256 de un webhook.

    Formato del header:
        x-signature: ts=<ts>,v1=<hash>
        x-request-id: <uuid>

    Manifest a firmar:
        id:<data_id>;request-id:<x_request_id>;ts:<ts>;
    """
    secret = secret or os.getenv("MERCADOPAGO_WEBHOOK_SECRET", "")
    if not secret:
        logger.error("MERCADOPAGO_WEBHOOK_SECRET no configurado")
        return False

    # Parsear x-signature
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

    # Construir manifest
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

    # Calcular HMAC
    expected = hmac.new(
        secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Comparación en tiempo constante
    is_valid = hmac.compare_digest(expected, v1)

    if not is_valid:
        logger.warning(
            "Firma inválida (data_id=%s, ts=%s)",
            data_id[:12], ts,
        )

    return is_valid


def verify_ipn_id(ipn_id: str, expected: str) -> bool:
    """Verifica un ID de IPN."""
    return hmac.compare_digest(ipn_id, expected)