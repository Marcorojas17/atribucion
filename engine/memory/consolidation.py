"""
Atribución Engine — Consolidación de memoria.

Convierte memoria a corto plazo (episódica) en memoria a largo
plazo (semántica), extrayendo patrones y hechos recurrentes.

Proceso:
    1. Analizar episodios recientes.
    2. Detectar patrones (eventos recurrentes).
    3. Extraer hechos implícitos.
    4. Añadirlos a la memoria semántica.
    5. Marcar episodios procesados.

Uso:
    consolidator = MemoryConsolidator(agent_id="agt_123")
    result = consolidator.consolidate()
    print(f"Consolidados: {result['facts_added']} hechos")
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from engine.memory.episodic import EpisodicMemory, Episode
from engine.memory.semantic import SemanticMemory


logger = logging.getLogger(__name__)


@dataclass
class ConsolidationResult:
    """Resultado de una consolidación."""

    episodes_analyzed: int
    patterns_detected: int
    facts_added: int
    duration_seconds: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "episodes_analyzed": self.episodes_analyzed,
            "patterns_detected": self.patterns_detected,
            "facts_added": self.facts_added,
            "duration_seconds": round(self.duration_seconds, 2),
            "timestamp": self.timestamp,
        }


class MemoryConsolidator:
    """Consolidador de memoria episódica → semántica."""

    def __init__(
        self,
        agent_id: str,
        min_recurrence: int = 3,
        lookback_days: int = 7,
    ) -> None:
        self.agent_id = agent_id
        self.min_recurrence = min_recurrence
        self.lookback_days = lookback_days

        self.episodic = EpisodicMemory(agent_id=agent_id)
        self.semantic = SemanticMemory(agent_id=agent_id)

        logger.info(
            "MemoryConsolidator listo (min_recurrence=%d, lookback=%dd)",
            min_recurrence, lookback_days,
        )

    # ─── CONSOLIDATE ───────────────────────────────────────────

    def consolidate(self) -> ConsolidationResult:
        """
        Ejecuta el proceso de consolidación.

        1. Obtiene episodios del período de lookback.
        2. Detecta patrones recurrentes.
        3. Los convierte en hechos semánticos.
        """
        import time
        start = time.time()

        cutoff = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)
        recent = [
            e for e in self.episodic.episodes
            if e.timestamp >= cutoff.isoformat()
        ]

        if not recent:
            logger.info("Sin episodios recientes para consolidar")
            return ConsolidationResult(
                episodes_analyzed=0,
                patterns_detected=0,
                facts_added=0,
                duration_seconds=time.time() - start,
            )

        patterns = self._detect_patterns(recent)
        facts_added = self._persist_patterns(patterns)

        result = ConsolidationResult(
            episodes_analyzed=len(recent),
            patterns_detected=len(patterns),
            facts_added=facts_added,
            duration_seconds=time.time() - start,
        )

        logger.info(
            "Consolidación: %d episodios, %d patrones, %d hechos",
            len(recent), len(patterns), facts_added,
        )
        return result

    # ─── PATTERN DETECTION ─────────────────────────────────────

    def _detect_patterns(self, episodes: list[Episode]) -> list[dict[str, Any]]:
        """Detecta patrones recurrentes en episodios."""
        patterns: list[dict[str, Any]] = []

        # Patrón 1: tipos de evento recurrentes
        type_counts = Counter(e.event_type for e in episodes)
        for event_type, count in type_counts.items():
            if count >= self.min_recurrence:
                patterns.append({
                    "type": "recurring_event",
                    "event_type": event_type,
                    "count": count,
                    "content": (
                        f"El evento '{event_type}' ocurre frecuentemente "
                        f"({count} veces en {self.lookback_days} días)"
                    ),
                    "confidence": min(1.0, count / 10),
                })

        # Patrón 2: tags recurrentes
        tag_counts: Counter[str] = Counter()
        for e in episodes:
            for tag in e.tags:
                tag_counts[tag] += 1

        for tag, count in tag_counts.most_common(5):
            if count >= self.min_recurrence:
                patterns.append({
                    "type": "recurring_tag",
                    "tag": tag,
                    "count": count,
                    "content": f"El tag '{tag}' aparece frecuentemente ({count} veces)",
                    "confidence": min(1.0, count / 10),
                })

        # Patrón 3: outcomes recurrentes
        outcome_counts = Counter(
            e.outcome for e in episodes if e.outcome
        )
        for outcome, count in outcome_counts.items():
            if count >= self.min_recurrence:
                patterns.append({
                    "type": "recurring_outcome",
                    "outcome": outcome,
                    "count": count,
                    "content": f"Outcome '{outcome}' recurrente ({count} veces)",
                    "confidence": min(1.0, count / 10),
                })

        return patterns

    # ─── PERSIST PATTERNS ──────────────────────────────────────

    def _persist_patterns(self, patterns: list[dict[str, Any]]) -> int:
        """Convierte patrones en hechos semánticos."""
        existing_facts = {f.content for f in self.semantic.facts}
        added = 0

        for p in patterns:
            content = p["content"]
            if content in existing_facts:
                continue

            self.semantic.add_fact(
                content=content,
                source="consolidation",
                confidence=p["confidence"],
                tags=["auto", p["type"]],
                metadata={k: v for k, v in p.items() if k != "content"},
            )
            added += 1

        return added

    # ─── STATS ─────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        return {
            "episodic": self.episodic.get_stats(),
            "semantic": self.semantic.get_stats(),
            "config": {
                "min_recurrence": self.min_recurrence,
                "lookback_days": self.lookback_days,
            },
        }