```markdown
# Mesh — Malla P2P

**Soberanía de red: sin servidores centrales.**

---

## Filosofía

Los nodos de Atribución se descubren entre sí.
No dependen de un servidor de directorio.
No hay punto único de fallo.

---

## Componentes

| Componente | Propósito |
|---|---|
| **transport/** | Transporte P2P (libp2p, QUIC, WebRTC) |
| **discovery/** | Descubrimiento (mDNS, DHT, rendezvous) |
| **consensus/** | Consenso (Raft, BFT, CRDT, gossip) |
| **storage/** | Almacenamiento (SQLite, IPFS, Arweave) |
| **sync/** | Sincronización (delta, conflict, merkle) |

---

## Implementación actual

| Archivo | Estado | Descripción |
|---|---|---|
| `transport/libp2p.py` | ✅ | Nodo P2P con framing JSON |
| `discovery/dht.py` | ✅ | DHT Kademlia simplificada |
| `consensus/crdt.py` | ✅ | LWWRegister + GCounter + ORSet |
| `storage/sqlite.py` | ✅ | Persistencia local |

**Roadmap:** QUIC, WebRTC, Nostr, Raft, BFT, IPFS, Arweave.

---

## Uso básico

### Crear nodo

```python
from mesh.transport.libp2p import LibP2PNode

node = LibP2PNode(port=7777)
node.register_handler("ping", lambda p: {"pong": True})
await node.start()
```

Añadir peers

```python
node.add_peer("peer_abc", "192.168.1.5", 7778)
responses = await node.broadcast("ping", {"hello": "world"})
```

DHT

```python
from mesh.discovery.dht import DHT

dht = DHT(node_id="peer_me")
dht.add_peer("peer_a", "127.0.0.1", 8001)
closest = dht.find_closest(target_id="peer_target", k=5)
```

CRDT

```python
from mesh.consensus.crdt import GCounter, ORSet

counter = GCounter(node_id="n1")
counter.increment(5)
counter.merge(other_counter)  # CRDT merge

orset = ORSet()
orset.add("x")
orset.remove("x")
```

---

Roadmap

Fase Mes Componentes
1 1-3 libp2p + DHT + CRDT + SQLite ✅
2 4-6 QUIC + mDNS + Raft
3 7-12 WebRTC + Nostr + IPFS
4 13+ Arweave + replication + sync

---

Cuándo usar Mesh

Sí usar:

· Múltiples nodos propios.
· Alta disponibilidad sin cloud.
· Casos de privacidad extrema.
· Clientes que exigen soberanía.

No usar:

· MVP con 1 nodo.
· Sin tráfico significativo.
· Antes de tener 10+ clientes.

Regla: Mesh es para el año 2+, no para hoy.

```