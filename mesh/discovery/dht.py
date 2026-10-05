"""
Atribución Mesh — DHT (Distributed Hash Table).

Descubrimiento de peers sin servidor central.

Implementación simplificada del algoritmo Kademlia:
- Cada peer tiene un ID (SHA-256 hash).
- Los peers se organizan por XOR distance.
- El routing se hace por k-buckets.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any


logger = logging.getLogger(__name__)

K_BUCKET_SIZE = 20


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────

def hash_id(value: str) -> int:
    """Convierte un string a entero de 256 bits."""
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)


def xor_distance(a: int, b: int) -> int:
    """Distancia XOR entre dos IDs."""
    return a ^ b


# ─────────────────────────────────────────────────────────────
# KBUCKET
# ─────────────────────────────────────────────────────────────

@dataclass
class KBucket:
    """Bucket de hasta K peers."""

    peers: list[tuple[str, str, int]] = field(default_factory=list)

    def add(self, peer_id: str, host: str, port: int) -> None:
        """Añade un peer. Si excede K, elimina el más antiguo."""
        # Si ya existe, mover al final
        self.peers = [p for p in self.peers if p[0] != peer_id]
        self.peers.append((peer_id, host, port))

        if len(self.peers) > K_BUCKET_SIZE:
            self.peers.pop(0)

    def get_all(self) -> list[tuple[str, str, int]]:
        return list(self.peers)


# ─────────────────────────────────────────────────────────────
# DHT
# ─────────────────────────────────────────────────────────────

class DHT:
    """
    DHT simplificada (Kademlia).

    Uso:
        dht = DHT(node_id="peer_abc")
        dht.add_peer("peer_xyz", "192.168.1.5", 7777)
        closest = dht.find_closest(target_id="peer_target", k=5)
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.node_hash = hash_id(node_id)
        self.buckets: dict[int, KBucket] = {}

    def add_peer(self, peer_id: str, host: str, port: int) -> None:
        """Añade un peer a la DHT."""
        distance = xor_distance(self.node_hash, hash_id(peer_id))
        bucket_index = distance.bit_length()
        bucket = self.buckets.setdefault(bucket_index, KBucket())
        bucket.add(peer_id, host, port)
        logger.debug("Peer %s añadido al bucket %d", peer_id, bucket_index)

    def remove_peer(self, peer_id: str) -> None:
        """Elimina un peer de la DHT."""
        peer_hash = hash_id(peer_id)
        distance = xor_distance(self.node_hash, peer_hash)
        bucket_index = distance.bit_length()
        if bucket_index in self.buckets:
            bucket = self.buckets[bucket_index]
            bucket.peers = [p for p in bucket.peers if p[0] != peer_id]

    def find_closest(self, target_id: str, k: int = K_BUCKET_SIZE) -> list[tuple[str, str, int]]:
        """
        Encuentra los K peers más cercanos a un target_id.

        Devuelve lista de (peer_id, host, port).
        """
        target_hash = hash_id(target_id)

        all_peers: list[tuple[str, str, int]] = []
        for bucket in self.buckets.values():
            all_peers.extend(bucket.get_all())

        all_peers.sort(key=lambda p: xor_distance(target_hash, hash_id(p[0])))
        return all_peers[:k]

    def total_peers(self) -> int:
        """Total de peers conocidos."""
        return sum(len(b.get_all()) for b in self.buckets.values())

    def snapshot(self) -> dict[str, Any]:
        """Snapshot de la DHT."""
        return {
            "node_id": self.node_id,
            "total_peers": self.total_peers(),
            "buckets": {
                idx: [p[0] for p in b.get_all()]
                for idx, b in self.buckets.items()
            },
        }