"""
Atribución Payments — Webhooks de Mercado Pago.

Receptor y procesador de notificaciones IPN/Webhooks.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from payments.mercadopago.client import MercadoPagoClientBase
from payments.mercadopago.verify import verify_webhook_signature


logger = logging.getLogger(__name__)


@dataclass
class WebhookEvent:
    """Evento recibido de Mercado Pago."""

    id: str
    type: str
    action: str
    data_id: str
    live_mode: bool
    timestamp: str
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "action": self.action,
            "data_id": self.data_id,
            "live_mode": self.live_mode,
            "timestamp": self.timestamp,
        }


class WebhookHandler:
    """Manejador de webhooks de Mercado Pago."""

    def __init__(
        self,
        client: MercadoPagoClientBase,
        state_dir: Path | None = None,
    ) -> None:
        self.client = client
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "webhooks")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self.state_dir / "mercadopago-webhooks.jsonl"

        self._handlers: dict[str, Callable[[WebhookEvent], Any]] = {}
        logger.info("WebhookHandler listo")

    # ─── REGISTRO DE HANDLERS ──────────────────────────────────

    def on(self, event_type: str, handler: Callable[[WebhookEvent], Any]) -> None:
        """Registra un handler para un tipo de evento."""
        self._handlers[event_type] = handler

    # ─── PROCESAMIENTO ─────────────────────────────────────────

    async def handle(
        self,
        body: dict[str, Any],
        x_signature: str,
        x_request_id: str,
    ) -> dict[str, Any]:
        """Procesa un webhook entrante."""
        data_id = str(body.get("data", {}).get("id", ""))

        # 1. Verificar firma
        if not verify_webhook_signature(
            x_signature=x_signature,
            x_request_id=x_request_id,
            data_id=data_id,
        ):
            logger.warning("Webhook con firma inválida")
            return {"status": "error", "detail": "invalid signature"}

        # 2. Parsear evento
        event = WebhookEvent(
            id=f"wh_{uuid4().hex[:12]}",
            type=body.get("type", "unknown"),
            action=body.get("action", ""),
            data_id=data_id,
            live_mode=body.get("live_mode", False),
            timestamp=datetime.now(timezone.utc).isoformat(),
            raw=body,
        )

        # 3. Persistir para auditoría
        self._persist(event)

        # 4. Ejecutar handler
        handler = self._handlers.get(event.type)
        if handler:
            try:
                result = handler(event)
                if hasattr(result, "__await__"):
                    result = await result
                logger.info("Webhook %s procesado por handler", event.type)
                return {"status": "ok", "event_id": event.id}
            except Exception as e:
                logger.exception("Error procesando webhook %s: %s", event.type, e)
                return {"status": "error", "detail": str(e)}

        logger.info("Webhook sin handler: %s", event.type)
        return {"status": "ok", "event_id": event.id}

    # ─── PERSISTENCIA ──────────────────────────────────────────

    def _persist(self, event: WebhookEvent) -> None:
        try:
            with self._log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning("No se pudo persistir webhook: %s", e)

    def get_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Devuelve historial de webhooks."""
        if not self._log_file.exists():
            return []

        lines = self._log_file.read_text(encoding="utf-8").splitlines()
        events = []
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events