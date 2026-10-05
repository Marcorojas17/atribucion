"""
Atribución Mesh — Storage local con SQLite.

Persistencia local para el nodo. Sin dependencias externas
(usa sqlite3 de la stdlib).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    from_peer TEXT NOT NULL,
    to_peer TEXT NOT NULL,
    type TEXT NOT NULL,
    payload TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_peer);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);

CREATE TABLE IF NOT EXISTS peers (
    peer_id TEXT PRIMARY KEY,
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS certificates (
    certificate_id TEXT PRIMARY KEY,
    agent_did TEXT NOT NULL,
    payload TEXT NOT NULL,
    anchor_tx TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_certs_agent ON certificates(agent_did);
"""


# ─────────────────────────────────────────────────────────────
# STORAGE
# ─────────────────────────────────────────────────────────────

class SQLiteStorage:
    """
    Storage local del nodo.

    Uso:
        storage = SQLiteStorage()
        storage.save_message({...})
        msgs = storage.get_messages(limit=10)
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or (Path.home() / ".atribucion" / "mesh.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # ─── MENSAJES ───────────────────────────────────────────────

    def save_message(self, message: dict[str, Any]) -> None:
        """Guarda un mensaje P2P."""
        self._conn.execute(
            "INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?)",
            (
                message["id"],
                message.get("from", ""),
                message.get("to", ""),
                message["type"],
                json.dumps(message.get("payload", {})),
                message.get("timestamp", datetime.now(timezone.utc).isoformat()),
            ),
        )
        self._conn.commit()

    def get_messages(self, limit: int = 100) -> list[dict[str, Any]]:
        """Devuelve los últimos mensajes."""
        cursor = self._conn.execute(
            "SELECT id, from_peer, to_peer, type, payload, timestamp "
            "FROM messages ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        return [
            {
                "id": row[0],
                "from": row[1],
                "to": row[2],
                "type": row[3],
                "payload": json.loads(row[4]),
                "timestamp": row[5],
            }
            for row in cursor.fetchall()
        ]

    # ─── PEERS ──────────────────────────────────────────────────

    def save_peer(self, peer_id: str, host: str, port: int) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO peers VALUES (?, ?, ?, ?)",
            (peer_id, host, port, datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def get_peers(self) -> list[dict[str, Any]]:
        cursor = self._conn.execute(
            "SELECT peer_id, host, port, last_seen FROM peers"
        )
        return [
            {"peer_id": r[0], "host": r[1], "port": r[2], "last_seen": r[3]}
            for r in cursor.fetchall()
        ]

    # ─── CERTIFICADOS ───────────────────────────────────────────

    def save_certificate(
        self,
        certificate_id: str,
        agent_did: str,
        payload: dict[str, Any],
        anchor_tx: str | None = None,
    ) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO certificates VALUES (?, ?, ?, ?, ?)",
            (
                certificate_id,
                agent_did,
                json.dumps(payload),
                anchor_tx,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self._conn.commit()

    def get_certificate(self, certificate_id: str) -> dict[str, Any] | None:
        cursor = self._conn.execute(
            "SELECT certificate_id, agent_did, payload, anchor_tx, created_at "
            "FROM certificates WHERE certificate_id = ?",
            (certificate_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "certificate_id": row[0],
            "agent_did": row[1],
            "payload": json.loads(row[2]),
            "anchor_tx": row[3],
            "created_at": row[4],
        }

    def count_certificates(self) -> int:
        cursor = self._conn.execute("SELECT COUNT(*) FROM certificates")
        return cursor.fetchone()[0]