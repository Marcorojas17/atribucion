"""
Atribución Engine — Graph Store.

Grafo de conocimiento dirigido con nodos y relaciones.

Permite representar conocimiento estructurado:
- Nodos con tipo y atributos
- Aristas dirigidas con tipo y peso
- Queries por traversal, vecinos, caminos

Uso:
    g = GraphStore(agent_id="agt_123")
    g.add_node("user", "user", {"name": "Marco"})
    g.add_node("preference", "pref_1", {"value": "respuestas cortas"})
    g.add_edge("user", "pref_1", "has_preference")
    neighbors = g.get_neighbors("user")
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


@dataclass
class Node:
    """Nodo del grafo."""

    id: str
    type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Edge:
    """Arista del grafo."""

    source: str
    target: str
    relation: str
    weight: float = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GraphStore:
    """Grafo de conocimiento persistente."""

    def __init__(
        self,
        agent_id: str,
        state_dir: Path | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "memory")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self._file = self.state_dir / f"graph-{agent_id}.json"
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self._adjacency: dict[str, list[Edge]] = defaultdict(list)
        self._reverse: dict[str, list[Edge]] = defaultdict(list)

        self._load()
        logger.info(
            "GraphStore cargado: %d nodos, %d aristas",
            len(self.nodes), len(self.edges),
        )

    # ─── NODES ─────────────────────────────────────────────────

    def add_node(
        self,
        node_id: str,
        node_type: str,
        attributes: dict[str, Any] | None = None,
    ) -> Node:
        """Añade o actualiza un nodo."""
        node = Node(
            id=node_id,
            type=node_type,
            attributes=attributes or {},
        )
        self.nodes[node_id] = node
        self._save()
        return node

    def get_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str) -> bool:
        if node_id not in self.nodes:
            return False
        del self.nodes[node_id]
        self.edges = [
            e for e in self.edges
            if e.source != node_id and e.target != node_id
        ]
        self._rebuild_adjacency()
        self._save()
        return True

    # ─── EDGES ─────────────────────────────────────────────────

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float = 1.0,
        attributes: dict[str, Any] | None = None,
    ) -> Edge | None:
        """Añade una arista entre dos nodos."""
        if source not in self.nodes or target not in self.nodes:
            logger.warning(
                "Nodos no existen: %s → %s", source, target,
            )
            return None

        edge = Edge(
            source=source,
            target=target,
            relation=relation,
            weight=weight,
            attributes=attributes or {},
        )
        self.edges.append(edge)
        self._adjacency[source].append(edge)
        self._reverse[target].append(edge)
        self._save()
        return edge

    def remove_edge(self, source: str, target: str, relation: str) -> bool:
        before = len(self.edges)
        self.edges = [
            e for e in self.edges
            if not (
                e.source == source
                and e.target == target
                and e.relation == relation
            )
        ]
        if len(self.edges) < before:
            self._rebuild_adjacency()
            self._save()
            return True
        return False

    # ─── QUERIES ───────────────────────────────────────────────

    def get_neighbors(
        self,
        node_id: str,
        relation: str | None = None,
        direction: str = "out",
    ) -> list[dict[str, Any]]:
        """Devuelve vecinos de un nodo."""
        edges = []
        if direction in ("out", "both"):
            edges.extend(self._adjacency.get(node_id, []))
        if direction in ("in", "both"):
            edges.extend(self._reverse.get(node_id, []))

        if relation:
            edges = [e for e in edges if e.relation == relation]

        neighbors = []
        for e in edges:
            neighbor_id = e.target if e.source == node_id else e.source
            neighbor = self.nodes.get(neighbor_id)
            if neighbor:
                neighbors.append({
                    "node": neighbor.to_dict(),
                    "edge": e.to_dict(),
                    "direction": "out" if e.source == node_id else "in",
                })
        return neighbors

    def find_path(
        self,
        source: str,
        target: str,
        max_depth: int = 5,
    ) -> list[str] | None:
        """Encuentra un camino entre dos nodos (BFS)."""
        if source not in self.nodes or target not in self.nodes:
            return None
        if source == target:
            return [source]

        visited: set[str] = {source}
        queue: deque[list[str]] = deque([[source]])

        while queue:
            path = queue.popleft()
            if len(path) > max_depth:
                continue
            current = path[-1]
            for edge in self._adjacency.get(current, []):
                if edge.target in visited:
                    continue
                new_path = path + [edge.target]
                if edge.target == target:
                    return new_path
                visited.add(edge.target)
                queue.append(new_path)
        return None

    def find_by_type(self, node_type: str) -> list[Node]:
        return [n for n in self.nodes.values() if n.type == node_type]

    def find_by_relation(self, relation: str) -> list[Edge]:
        return [e for e in self.edges if e.relation == relation]

    # ─── STATS ─────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        from collections import Counter
        node_types = Counter(n.type for n in self.nodes.values())
        relations = Counter(e.relation for e in self.edges)
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types.most_common()),
            "relations": dict(relations.most_common()),
        }

    def clear(self) -> None:
        self.nodes = {}
        self.edges = []
        self._adjacency.clear()
        self._reverse.clear()
        self._save()

    # ─── PERSISTENCIA ──────────────────────────────────────────

    def _rebuild_adjacency(self) -> None:
        self._adjacency.clear()
        self._reverse.clear()
        for e in self.edges:
            self._adjacency[e.source].append(e)
            self._reverse[e.target].append(e)

    def _save(self) -> None:
        data = {
            "agent_id": self.agent_id,
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
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
            for node_id, n in data.get("nodes", {}).items():
                self.nodes[node_id] = Node(**n)
            for e in data.get("edges", []):
                edge = Edge(**e)
                self.edges.append(edge)
                self._adjacency[edge.source].append(edge)
                self._reverse[edge.target].append(edge)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Error cargando graph store: %s", e)