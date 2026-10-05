"""
Atribución — Mesh.

Malla P2P sin servidores.

Módulos:
    transport  → libp2p, QUIC, WebRTC, Nostr
    discovery  → mDNS, DHT, rendezvous, bootstrap
    consensus  → Raft, BFT, CRDT, gossip
    storage    → SQLite, Dexie, IPFS, Arweave
    sync       → delta, conflict, merkle_sync

Filosofía: soberanía de red. Los nodos se descubren entre sí,
no dependen de un servidor central.
"""

__version__ = "0.1.0"