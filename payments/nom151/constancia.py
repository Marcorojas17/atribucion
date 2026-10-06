"""
Atribución Payments — Constancias NOM-151.

Genera y gestiona constancias de conservación.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from payments.nom151.psc_client import PSCClient


logger = logging.getLogger(__name__)


@dataclass
class Constancia:
    """Constancia de conservación NOM-151."""

    id: str
    document_hash: str
    psc_provider: str
    psc_constancia_id: str
    issued_at: str
    verified_at: str | None
    pdf_url: str | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ConstanciaService:
    """Servicio de constancias NOM-151."""

    def __init__(
        self,
        psc_client: PSCClient,
        state_dir: Path | None = None,
    ) -> None:
        self.psc = psc_client
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "nom151")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.state_dir / "constancias.jsonl"

    async def create(
        self,
        document: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Constancia:
        """Crea una constancia a partir de un documento."""
        # Calcular hash del documento
        canonical = json.dumps(document, sort_keys=True, separators=(",", ":"))
        document_hash = hashlib.sha256(canonical.encode()).hexdigest()

        # Enviar al PSC
        psc_response = await self.psc.stamp_document(
            document_hash=document_hash,
            metadata=metadata,
        )

        constancia = Constancia(
            id=f"cons_{uuid4().hex[:12]}",
            document_hash=document_hash,
            psc_provider=self.psc.config.provider,
            psc_constancia_id=psc_response.get("id", ""),
            issued_at=datetime.now(timezone.utc).isoformat(),
            verified_at=None,
            pdf_url=psc_response.get("pdf_url"),
            metadata=metadata or {},
        )

        self._persist(constancia)
        logger.info("Constancia creada: %s", constancia.id)
        return constancia

    async def verify(self, constancia_id: str) -> bool:
        """Verifica una constancia con el PSC."""
        constancia = self.get(constancia_id)
        if not constancia:
            return False

        try:
            result = await self.psc.verify_constancia(constancia.psc_constancia_id)
            is_valid = result.get("status") == "valid"
            if is_valid:
                constancia.verified_at = datetime.now(timezone.utc).isoformat()
                self._persist(constancia)
            return is_valid
        except Exception as e:
            logger.error("Error verificando constancia: %s", e)
            return False

    def get(self, constancia_id: str) -> Constancia | None:
        """Recupera una constancia por ID."""
        if not self._file.exists():
            return None
        for line in self._file.read_text(encoding="utf-8").splitlines():
            try:
                data = json.loads(line)
                if data["id"] == constancia_id:
                    return Constancia(**data)
            except (json.JSONDecodeError, KeyError):
                continue
        return None

    def _persist(self, constancia: Constancia) -> None:
        with self._file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(constancia.to_dict(), ensure_ascii=False) + "\n")