"""
Atribución — Base de los 9 robots guardianes.

Todos los guardianes heredan de GuardAgent y comparten:
- Ciclo de vida (start/stop)
- Logging
- Reporte de hallazgos
- Persistencia de estado
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────────────────────

@dataclass
class Finding:
    """Hallazgo de un guardián."""

    guard: str
    severity: str  # info | warning | critical
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────
# BASE
# ─────────────────────────────────────────────────────────────

class GuardAgent(ABC):
    """
    Base común para los 9 guardianes de Atribución.

    Cada guardián implementa `check()` que corre periódicamente
    y devuelve una lista de Finding.
    """

    name: str = "guard"
    interval_seconds: int = 60

    def __init__(self, state_dir: Path | None = None) -> None:
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "guards")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._running = False
        self._task: asyncio.Task | None = None
        self.findings: list[Finding] = []

    # ─── CICLO DE VIDA ──────────────────────────────────────────

    async def start(self) -> None:
        """Arranca el guardián en background."""
        if self._running:
            logger.warning("%s ya está corriendo", self.name)
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("%s arrancado (interval=%ds)", self.name, self.interval_seconds)

    async def stop(self) -> None:
        """Detiene el guardián."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("%s detenido", self.name)

    async def _loop(self) -> None:
        """Loop principal."""
        while self._running:
            try:
                results = await self.check()
                for f in results:
                    self.findings.append(f)
                    logger.log(
                        logging.WARNING if f.severity == "critical" else logging.INFO,
                        "[%s] %s: %s",
                        f.guard, f.severity, f.message,
                    )
                self._persist_findings()
            except Exception as e:
                logger.exception("%s error en check: %s", self.name, e)
            await asyncio.sleep(self.interval_seconds)

    # ─── CONTRATO ───────────────────────────────────────────────

    @abstractmethod
    async def check(self) -> list[Finding]:
        """Ejecuta una verificación. Debe devolver hallazgos."""
        ...

    # ─── PERSISTENCIA ───────────────────────────────────────────

    def _persist_findings(self) -> None:
        path = self.state_dir / f"{self.name}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            for finding in self.findings[-50:]:
                f.write(json.dumps(finding.to_dict(), ensure_ascii=False) + "\n")

    def get_last_findings(self, limit: int = 50) -> list[Finding]:
        return self.findings[-limit:]