"""
Atribución Mesh — CRDT.

Conflict-free Replicated Data Types.

Permiten que múltiples nodos modifiquen datos sin coordinación,
y que se reconcilien automáticamente sin conflictos.

Implementa:
- LWWRegister (Last-Write-Wins)
- GCounter (Grow-only Counter)
- ORSet (Observed-Remove Set)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar


T = TypeVar("T")


# ─────────────────────────────────────────────────────────────
# LWW REGISTER
# ─────────────────────────────────────────────────────────────

@dataclass
class LWWRegister(Generic[T]):
    """
    Last-Write-Wins Register.

    Cada valor tiene un timestamp. El valor más reciente gana.
    """

    value: T | None = None
    timestamp: float = 0.0

    def set(self, value: T, timestamp: float | None = None) -> None:
        ts = timestamp if timestamp is not None else time.time()
        if ts > self.timestamp:
            self.value = value
            self.timestamp = ts

    def get(self) -> T | None:
        return self.value

    def merge(self, other: "LWWRegister[T]") -> None:
        """Merge con otra instancia."""
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp


# ─────────────────────────────────────────────────────────────
# G-COUNTER
# ─────────────────────────────────────────────────────────────

@dataclass
class GCounter:
    """
    Grow-only Counter.

    Cada nodo mantiene su propio contador. El valor total es la suma.
    """

    node_id: str
    counters: dict[str, int] = field(default_factory=dict)

    def increment(self, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("GCounter solo incrementa")
        self.counters[self.node_id] = self.counters.get(self.node_id, 0) + amount

    def value(self) -> int:
        return sum(self.counters.values())

    def merge(self, other: "GCounter") -> None:
        """Toma el máximo por nodo."""
        for node, count in other.counters.items():
            self.counters[node] = max(self.counters.get(node, 0), count)


# ─────────────────────────────────────────────────────────────
# OR-SET
# ─────────────────────────────────────────────────────────────

@dataclass
class ORSet(Generic[T]):
    """
    Observed-Remove Set.

    Cada add genera un tag único. Cada remove elimina los tags
    observados. Permite adds y removes concurrentes sin conflictos.
    """

    elements: dict[T, set[str]] = field(default_factory=dict)
    _counter: int = 0

    def add(self, element: T) -> str:
        """Añade un elemento. Devuelve el tag."""
        self._counter += 1
        tag = f"tag_{self._counter}_{time.time_ns()}"
        self.elements.setdefault(element, set()).add(tag)
        return tag

    def remove(self, element: T) -> None:
        """Elimina un elemento (borra todos sus tags)."""
        self.elements.pop(element, None)

    def contains(self, element: T) -> bool:
        return element in self.elements and len(self.elements[element]) > 0

    def value(self) -> set[T]:
        """Elementos presentes."""
        return {e for e, tags in self.elements.items() if tags}

    def merge(self, other: "ORSet[T]") -> None:
        """Union de tags para cada elemento."""
        for element, tags in other.elements.items():
            self.elements.setdefault(element, set()).update(tags)
        # Eliminar elementos sin tags
        self.elements = {e: t for e, t in self.elements.items() if t}