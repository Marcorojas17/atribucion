"""
Atribución — Merkle Trees.

Permite agrupar N acciones en un solo root, y anclar
ese root a Ethereum. Cada acción puede probarse
individualmente con una Merkle proof.

Algoritmo:
- Doble SHA-256 por hoja (estándar Bitcoin/Ethereum)
- Duplicación del último nodo si el nivel es impar
- Raíz: 32 bytes = 64 hex chars
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from atribucion import crypto


# ─────────────────────────────────────────────────────────────
# HASHES INTERNOS
# ─────────────────────────────────────────────────────────────

def _leaf_hash(data: Any) -> bytes:
    """
    Hash de una hoja.

    Usa doble SHA-256 (estándar Merkle).
    """
    payload = crypto.canonical_bytes(data)
    return hashlib.sha256(hashlib.sha256(payload).digest()).digest()


def _node_hash(left: bytes, right: bytes) -> bytes:
    """Hash de un nodo interno."""
    return hashlib.sha256(left + right).digest()


# ─────────────────────────────────────────────────────────────
# MODELO DE PROOF
# ─────────────────────────────────────────────────────────────

@dataclass
class MerkleProof:
    """Prueba de inclusión de una hoja en un árbol."""

    leaf_index: int
    leaf_hash: str
    siblings: list[str]
    root: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "leaf_index": self.leaf_index,
            "leaf_hash": self.leaf_hash,
            "siblings": self.siblings,
            "root": self.root,
        }


# ─────────────────────────────────────────────────────────────
# CONSTRUCCIÓN
# ─────────────────────────────────────────────────────────────

def root_of(items: list[Any]) -> str:
    """
    Calcula la raíz Merkle de una lista de items.

    - Lista vacía → hash de string vacío
    - Un solo item → su hash como raíz
    - Nivel impar → duplica el último nodo (estándar Bitcoin)

    Devuelve hex con prefijo 0x.
    """
    if not items:
        return "0x" + hashlib.sha256(b"").hexdigest()

    level = [_leaf_hash(item) for item in items]

    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        next_level = []
        for i in range(0, len(level), 2):
            next_level.append(_node_hash(level[i], level[i + 1]))
        level = next_level

    return "0x" + level[0].hex()


# ─────────────────────────────────────────────────────────────
# PROOF
# ─────────────────────────────────────────────────────────────

def proof_for(items: list[Any], index: int) -> MerkleProof:
    """
    Genera la Merkle proof para un item en una posición.

    Lanza IndexError si el índice está fuera de rango.
    """
    if not items:
        raise ValueError("Lista vacía")

    if index < 0 or index >= len(items):
        raise IndexError(
            f"Índice {index} fuera de rango (len={len(items)})"
        )

    level = [_leaf_hash(item) for item in items]
    original_index = index
    siblings: list[bytes] = []

    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        # XOR con 1 alterna entre par e impar
        sibling_index = index ^ 1
        siblings.append(level[sibling_index])

        next_level = []
        for i in range(0, len(level), 2):
            next_level.append(_node_hash(level[i], level[i + 1]))
        level = next_level
        index = index // 2

    return MerkleProof(
        leaf_index=original_index,
        leaf_hash="0x" + _leaf_hash(items[original_index]).hex(),
        siblings=["0x" + s.hex() for s in siblings],
        root="0x" + level[0].hex(),
    )


# ─────────────────────────────────────────────────────────────
# VERIFICACIÓN
# ─────────────────────────────────────────────────────────────

def verify_proof(proof: MerkleProof) -> bool:
    """
    Verifica una Merkle proof contra su root.

    Reconstruye el camino desde la hoja hasta la raíz
    aplicando los hermanos en orden.
    """
    current = bytes.fromhex(proof.leaf_hash.removeprefix("0x"))
    index = proof.leaf_index

    for sibling_hex in proof.siblings:
        sibling = bytes.fromhex(sibling_hex.removeprefix("0x"))

        if index % 2 == 0:
            current = _node_hash(current, sibling)
        else:
            current = _node_hash(sibling, current)

        index = index // 2

    return ("0x" + current.hex()) == proof.root