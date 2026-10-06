"""
Atribución Payments — Sellado de tiempo.

Combina RFC 3161 + PSC para sellado legal en México.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from payments.nom151.psc_client import PSCClient


logger = logging.getLogger(__name__)


@dataclass
class Sello:
    """Sello de tiempo legal."""

    id: str
    document_hash: str
    tsa_authority: str
    tsa_token: str
    psc_constancia_id: str | None
    sealed_at: str
    expires_at: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "document_hash": self.document_hash,
            "tsa_authority": self.tsa_authority,
            "tsa_token": self.tsa_token,
            "psc_constancia_id": self.psc_constancia_id,
            "sealed_at": self.sealed_at,
            "expires_at": self.expires_at,
        }


class SelloService:
    """Servicio de sellado de tiempo legal."""

    def __init__(self, psc_client: PSCClient | None = None) -> None:
        self.psc = psc_client

    async def seal(
        self,
        document_hash: str,
        use_psc: bool = True,
    ) -> Sello:
        """
        Sella un documento con RFC 3161 + opcionalmente PSC.

        - Siempre usa TSA interna (mock o real).
        - Si use_psc=True, también sella con PSC acreditado.
        """
        from core.src.atribucion import tsa

        # 1. Sello RFC 3161 interno
        tsa_result = await tsa.seal(document_hash.encode())

        # 2. Sello PSC (si aplica)
        psc_constancia_id = None
        if use_psc and self.psc:
            try:
                psc_response = await self.psc.stamp_document(document_hash)
                psc_constancia_id = psc_response.get("id")
            except Exception as e:
                logger.warning("PSC sellado falló: %s", e)

        from uuid import uuid4

        sello = Sello(
            id=f"sello_{uuid4().hex[:12]}",
            document_hash=document_hash,
            tsa_authority=tsa_result.authority,
            tsa_token=tsa_result.token,
            psc_constancia_id=psc_constancia_id,
            sealed_at=datetime.now(timezone.utc).isoformat(),
            expires_at=None,
        )

        logger.info("Documento sellado: %s", sello.id)
        return sello