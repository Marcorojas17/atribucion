"""
Atribución Engine — Vector Store.

Búsqueda semántica por similitud de embeddings.

Sin dependencias externas obligatorias: usa hashing de features
como fallback. Si hay sentence-transformers disponible, lo usa.

Uso:
    store = VectorStore(agent_id="agt_123", dim=384)
    store.add("El usuario prefiere respuestas cortas", {"tag": "preference"})
    results = store.search("preferencias del usuario", top_k=5)
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class VectorEntry:
    """Una entrada en el vector store."""

    id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VectorStore:
    """Vector store con búsqueda por similitud coseno."""

    def __init__(
        self,
        agent_id: str,
        state_dir: Path | None = None,
        dim: int = 384,
        model_name: str = "all-MiniLM-L6-v2",
        use_transformers: bool = True,
    ) -> None:
        self.agent_id = agent_id
        self.dim = dim
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "memory")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self._file = self.state_dir / f"vectors-{agent_id}.json"
        self.entries: list[VectorEntry] = []

        self._use_transformers = use_transformers and ST_AVAILABLE
        self._model: Any = None

        if self._use_transformers:
            try:
                self._model = SentenceTransformer(model_name)
                self.dim = self._model.get_sentence_embedding_dimension()
                logger.info("VectorStore con sentence-transformers (dim=%d)", self.dim)
            except Exception as e:
                logger.warning("Fallo cargando sentence-transformers: %s", e)
                self._use_transformers = False

        if not self._use_transformers:
            logger.info("VectorStore con hashing de features (dim=%d)", self.dim)

        self._load()

    # ─── EMBEDDINGS ────────────────────────────────────────────

    def _embed(self, text: str) -> list[float]:
        """Genera embedding de un texto."""
        if self._use_transformers and self._model:
            emb = self._model.encode(text, convert_to_numpy=True)
            return emb.tolist()

        return self._hash_embedding(text)

    def _hash_embedding(self, text: str) -> list[float]:
        """Embedding por hashing de features (fallback)."""
        vec = [0.0] * self.dim
        tokens = re.findall(r"\w+", text.lower())

        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign

        # Normalizar
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Similitud coseno entre dos vectores."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
        norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (norm_a * norm_b)

    # ─── ADD ───────────────────────────────────────────────────

    def add(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> VectorEntry:
        """Añade una entrada al store."""
        entry = VectorEntry(
            id=f"vec_{uuid4().hex[:12]}",
            text=text,
            embedding=self._embed(text),
            metadata=metadata or {},
        )
        self.entries.append(entry)
        self._save()
        return entry

    def add_batch(
        self,
        items: list[tuple[str, dict[str, Any] | None]],
    ) -> list[VectorEntry]:
        """Añade varias entradas."""
        added = []
        for text, meta in items:
            entry = VectorEntry(
                id=f"vec_{uuid4().hex[:12]}",
                text=text,
                embedding=self._embed(text),
                metadata=meta or {},
            )
            self.entries.append(entry)
            added.append(entry)
        self._save()
        return added

    # ─── SEARCH ────────────────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.0,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Busca las entradas más similares a un query."""
        if not self.entries:
            return []

        query_emb = self._embed(query)
        results = []

        for entry in self.entries:
            if filter_metadata:
                if not all(
                    entry.metadata.get(k) == v
                    for k, v in filter_metadata.items()
                ):
                    continue

            sim = self._cosine_similarity(query_emb, entry.embedding)
            if sim >= min_similarity:
                results.append({
                    "id": entry.id,
                    "text": entry.text,
                    "similarity": round(sim, 4),
                    "metadata": entry.metadata,
                    "timestamp": entry.timestamp,
                })

        results.sort(key=lambda r: r["similarity"], reverse=True)
        return results[:top_k]

    def search_by_vector(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Busca por un vector directo."""
        results = []
        for entry in self.entries:
            sim = self._cosine_similarity(embedding, entry.embedding)
            results.append({
                "id": entry.id,
                "text": entry.text,
                "similarity": round(sim, 4),
                "metadata": entry.metadata,
            })
        results.sort(key=lambda r: r["similarity"], reverse=True)
        return results[:top_k]

    # ─── DELETE ────────────────────────────────────────────────

    def remove(self, entry_id: str) -> bool:
        """Elimina una entrada por ID."""
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.id != entry_id]
        if len(self.entries) < before:
            self._save()
            return True
        return False

    def clear(self) -> None:
        self.entries = []
        self._save()

    # ─── STATS ─────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_entries": len(self.entries),
            "dim": self.dim,
            "backend": "sentence-transformers" if self._use_transformers else "hash",
        }

    # ─── PERSISTENCIA ──────────────────────────────────────────

    def _save(self) -> None:
        data = {
            "agent_id": self.agent_id,
            "dim": self.dim,
            "entries": [e.to_dict() for e in self.entries],
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        self._file.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load(self) -> None:
        if not self._file.exists():
            return
        try:
            data = json.loads(self._file.read_text(encoding="utf-8"))
            self.dim = data.get("dim", self.dim)
            for e in data.get("entries", []):
                self.entries.append(VectorEntry(**e))
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Error cargando vector store: %s", e)