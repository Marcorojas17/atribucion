"""
Atribución Engine — Memoria semántica.

Almacena conocimiento estructurado del agente:
- Hechos (facts)
- Conceptos
- Relaciones entre conceptos
- Reglas

Es la memoria de "qué sé", no "qué hice".

Persistencia: JSON en disco.

Uso:
    mem = SemanticMemory(agent_id="agt_123")
    mem.add_fact("El usuario prefiere respuestas cortas", source="feedback")
    mem.add_concept("trading", definition="Compra/venta de activos")
    facts = mem.get_facts(limit=10)
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


logger = logging.getLogger(__name__)


@dataclass
class Fact:
    """Un hecho conocido."""

    id: str
    content: str
    source: str
    confidence: float
    timestamp: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Concept:
    """Un concepto con definición y relaciones."""

    name: str
    definition: str
    relations: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SemanticMemory:
    """Memoria semántica persistente."""

    def __init__(
        self,
        agent_id: str,
        state_dir: Path | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "memory")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self._file = self.state_dir / f"semantic-{agent_id}.json"
        self.facts: list[Fact] = []
        self.concepts: dict[str, Concept] = {}

        self._load()
        logger.info(
            "SemanticMemory cargada: %d hechos, %d conceptos (%s)",
            len(self.facts), len(self.concepts), agent_id,
        )

    # ─── FACTS ─────────────────────────────────────────────────

    def add_fact(
        self,
        content: str,
        source: str = "user",
        confidence: float = 1.0,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Fact:
        """Añade un hecho."""
        fact = Fact(
            id=f"fact_{uuid4().hex[:12]}",
            content=content,
            source=source,
            confidence=max(0.0, min(1.0, confidence)),
            timestamp=datetime.now(timezone.utc).isoformat(),
            tags=tags or [],
            metadata=metadata or {},
        )
        self.facts.append(fact)
        self._save()
        logger.debug("Hecho añadido: %s", fact.id)
        return fact

    def get_facts(
        self,
        limit: int = 20,
        min_confidence: float = 0.0,
        tag: str | None = None,
    ) -> list[Fact]:
        """Devuelve hechos filtrados."""
        filtered = [
            f for f in self.facts
            if f.confidence >= min_confidence
            and (tag is None or tag in f.tags)
        ]
        return filtered[-limit:]

    def search_facts(self, query: str, limit: int = 10) -> list[Fact]:
        """Busca hechos que contengan el query."""
        q = query.lower()
        matches = [f for f in self.facts if q in f.content.lower()]
        return sorted(matches, key=lambda f: f.confidence, reverse=True)[:limit]

    def remove_fact(self, fact_id: str) -> bool:
        """Elimina un hecho por ID."""
        before = len(self.facts)
        self.facts = [f for f in self.facts if f.id != fact_id]
        if len(self.facts) < before:
            self._save()
            return True
        return False

    # ─── CONCEPTS ──────────────────────────────────────────────

    def add_concept(
        self,
        name: str,
        definition: str,
        metadata: dict[str, Any] | None = None,
    ) -> Concept:
        """Añade o actualiza un concepto."""
        concept = Concept(
            name=name.lower().strip(),
            definition=definition,
            metadata=metadata or {},
        )
        self.concepts[concept.name] = concept
        self._save()
        return concept

    def add_relation(
        self,
        from_concept: str,
        relation_type: str,
        to_concept: str,
    ) -> bool:
        """Añade una relación entre conceptos."""
        from_key = from_concept.lower().strip()
        if from_key not in self.concepts:
            return False

        self.concepts[from_key].relations.append({
            "type": relation_type,
            "target": to_concept.lower().strip(),
        })
        self._save()
        return True

    def get_concept(self, name: str) -> Concept | None:
        return self.concepts.get(name.lower().strip())

    def get_related(self, name: str, depth: int = 1) -> list[str]:
        """Devuelve conceptos relacionados (BFS simple)."""
        key = name.lower().strip()
        if key not in self.concepts:
            return []

        visited: set[str] = {key}
        to_visit = [key]
        related: list[str] = []

        for _ in range(depth):
            next_visit = []
            for current in to_visit:
                concept = self.concepts.get(current)
                if not concept:
                    continue
                for rel in concept.relations:
                    target = rel["target"]
                    if target not in visited:
                        visited.add(target)
                        related.append(target)
                        next_visit.append(target)
            to_visit = next_visit

        return related

    # ─── STATS ─────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas."""
        sources = Counter(f.source for f in self.facts)
        tags = Counter(t for f in self.facts for t in f.tags)
        return {
            "total_facts": len(self.facts),
            "total_concepts": len(self.concepts),
            "avg_confidence": (
                sum(f.confidence for f in self.facts) / len(self.facts)
                if self.facts else 0.0
            ),
            "by_source": dict(sources),
            "top_tags": dict(tags.most_common(5)),
        }

    # ─── CLEAR ─────────────────────────────────────────────────

    def clear(self) -> None:
        self.facts = []
        self.concepts = {}
        self._save()

    # ─── PERSISTENCIA ──────────────────────────────────────────

    def _save(self) -> None:
        data = {
            "agent_id": self.agent_id,
            "facts": [asdict(f) for f in self.facts],
            "concepts": {k: v.to_dict() for k, v in self.concepts.items()},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        self._file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load(self) -> None:
        if not self._file.exists():
            return
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
            self.facts = [Fact(**f) for f in data.get("facts", [])]
            self.concepts = {
                k: Concept(**v)
                for k, v in data.get("concepts", {}).items()
            }
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Error cargando memoria semántica: %s", e)