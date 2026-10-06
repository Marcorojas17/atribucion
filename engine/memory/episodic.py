"""
Atribución Engine — Memoria episódica.

Registra eventos concretos vividos por el agente:
- Qué pasó
- Cuándo pasó
- Con quién pasó
- En qué contexto

Es la memoria de "qué hice", no "qué sé".

Persistencia: JSONL append-only.
Retención: configurable (default 365 días).

Uso:
    mem = EpisodicMemory(agent_id="agt_123")
    mem.record(event_type="action", data={"action": "trade"})
    recent = mem.get_recent(limit=10)
    by_type = mem.get_by_type("action", limit=5)
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """Un evento concreto vivido por el agente."""

    id: str
    agent_id: str
    event_type: str
    data: dict[str, Any]
    timestamp: str
    context: dict[str, Any] = field(default_factory=dict)
    outcome: str | None = None
    tags: list[str] = field(default_factory=list)
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            payload = f"{self.id}|{self.agent_id}|{self.event_type}|{self.timestamp}"
            self.hash = hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_context_str(self) -> str:
        """Formato para incluir en prompts."""
        data_preview = json.dumps(self.data, ensure_ascii=False)[:100]
        return f"[{self.timestamp}] {self.event_type}: {data_preview}"


class EpisodicMemory:
    """Memoria episódica persistente."""

    def __init__(
        self,
        agent_id: str,
        state_dir: Path | None = None,
        retention_days: int = 365,
    ) -> None:
        self.agent_id = agent_id
        self.retention_days = retention_days
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "memory")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self._file = self.state_dir / f"episodic-{agent_id}.jsonl"
        self.episodes: list[Episode] = self._load()

        logger.info(
            "EpisodicMemory cargada: %d episodios (%s)",
            len(self.episodes), agent_id,
        )

    # ─── RECORD ────────────────────────────────────────────────

    def record(
        self,
        event_type: str,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
        outcome: str | None = None,
        tags: list[str] | None = None,
    ) -> Episode:
        """Registra un nuevo episodio."""
        episode = Episode(
            id=f"ep_{uuid4().hex[:12]}",
            agent_id=self.agent_id,
            event_type=event_type,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat(),
            context=context or {},
            outcome=outcome,
            tags=tags or [],
        )
        self.episodes.append(episode)
        self._persist(episode)
        logger.debug("Episodio registrado: %s", episode.id)
        return episode

    # ─── QUERY ─────────────────────────────────────────────────

    def get_recent(self, limit: int = 10) -> list[Episode]:
        """Devuelve los últimos N episodios."""
        return self.episodes[-limit:]

    def get_by_type(self, event_type: str, limit: int = 10) -> list[Episode]:
        """Episodios de un tipo específico."""
        filtered = [e for e in self.episodes if e.event_type == event_type]
        return filtered[-limit:]

    def get_by_tag(self, tag: str, limit: int = 10) -> list[Episode]:
        """Episodios con un tag específico."""
        filtered = [e for e in self.episodes if tag in e.tags]
        return filtered[-limit:]

    def get_by_date_range(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Episode]:
        """Episodios en un rango de fechas."""
        start_str = start.isoformat()
        end_str = end.isoformat()
        return [
            e for e in self.episodes
            if start_str <= e.timestamp <= end_str
        ]

    def search(self, query: str, limit: int = 10) -> list[Episode]:
        """Busca en el contenido de los episodios."""
        q = query.lower()
        matches = []
        for e in self.episodes:
            data_str = json.dumps(e.data, ensure_ascii=False).lower()
            if q in data_str or q in e.event_type.lower():
                matches.append(e)
        return matches[-limit:]

    # ─── STATS ─────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas de la memoria episódica."""
        if not self.episodes:
            return {"total": 0, "by_type": {}, "oldest": None, "newest": None}

        types = Counter(e.event_type for e in self.episodes)
        return {
            "total": len(self.episodes),
            "by_type": dict(types.most_common()),
            "oldest": self.episodes[0].timestamp,
            "newest": self.episodes[-1].timestamp,
        }

    # ─── CLEANUP ───────────────────────────────────────────────

    def cleanup_old(self) -> int:
        """Elimina episodios mayores a retention_days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        cutoff_str = cutoff.isoformat()

        before = len(self.episodes)
        self.episodes = [e for e in self.episodes if e.timestamp >= cutoff_str]
        removed = before - len(self.episodes)

        if removed > 0:
            self._rewrite()
            logger.info("Cleanup: %d episodios eliminados", removed)

        return removed

    def clear(self) -> None:
        """Borra toda la memoria episódica."""
        self.episodes = []
        if self._file.exists():
            self._file.unlink()

    # ─── PERSISTENCIA ──────────────────────────────────────────

    def _persist(self, episode: Episode) -> None:
        with self._file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(episode.to_dict(), ensure_ascii=False) + "\n")

    def _load(self) -> list[Episode]:
        if not self._file.exists():
            return []

        episodes: list[Episode] = []
        for line in self._file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                episodes.append(Episode(**data))
            except (json.JSONDecodeError, TypeError):
                continue
        return episodes

    def _rewrite(self) -> None:
        """Reescribe el archivo con los episodios actuales."""
        with self._file.open("w", encoding="utf-8") as f:
            for e in self.episodes:
                f.write(json.dumps(e.to_dict(), ensure_ascii=False) + "\n")