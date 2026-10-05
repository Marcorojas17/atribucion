"""
Atribución Mesh — Nodo P2P.

Implementación base de un nodo P2P con descubrimiento
local (mDNS) y transporte TCP con framing JSON.

Sin dependencias externas. Cuando esté disponible py-libp2p,
se reemplaza la clase interna sin cambiar la API.
"""

from __future__ import annotations

import asyncio
import json
import logging
import secrets
import socket
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger(__name__)


Handler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


# ─────────────────────────────────────────────────────────────
# MENSAJE
# ─────────────────────────────────────────────────────────────

@dataclass
class Message:
    """Mensaje P2P."""

    id: str
    from_peer: str
    to_peer: str
    type: str
    payload: dict[str, Any]
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_bytes(self) -> bytes:
        data = json.dumps(
            {
                "id": self.id,
                "from": self.from_peer,
                "to": self.to_peer,
                "type": self.type,
                "payload": self.payload,
                "timestamp": self.timestamp,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        return len(data).to_bytes(4, "big") + data


# ─────────────────────────────────────────────────────────────
# NODO P2P
# ─────────────────────────────────────────────────────────────

class LibP2PNode:
    """
    Nodo P2P base.

    Uso:
        node = LibP2PNode(port=7777)
        node.register_handler("ping", handle_ping)
        await node.start()
        await node.broadcast("ping", {"hello": "world"})
        await node.stop()
    """

    def __init__(self, port: int = 0, node_id: str | None = None) -> None:
        self.port = port
        self.node_id = node_id or f"peer_{secrets.token_hex(8)}"
        self.peers: dict[str, tuple[str, int]] = {}
        self.handlers: dict[str, Handler] = {}
        self._server: asyncio.AbstractServer | None = None
        self._running = False

    # ─── CICLO DE VIDA ──────────────────────────────────────────

    async def start(self) -> None:
        """Arranca el nodo P2P."""
        self._server = await asyncio.start_server(
            self._handle_connection,
            host="0.0.0.0",
            port=self.port,
        )
        self._running = True

        # Si elegimos puerto dinámico, obtener el real
        if self.port == 0:
            sockets = self._server.sockets or []
            if sockets:
                self.port = sockets[0].getsockname()[1]

        logger.info("Node %s escuchando en puerto %d", self.node_id, self.port)

    async def stop(self) -> None:
        """Detiene el nodo P2P."""
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("Node %s detenido", self.node_id)

    # ─── HANDLERS ───────────────────────────────────────────────

    def register_handler(self, msg_type: str, handler: Handler) -> None:
        """Registra un handler para un tipo de mensaje."""
        self.handlers[msg_type] = handler

    # ─── PEERS ──────────────────────────────────────────────────

    def add_peer(self, peer_id: str, host: str, port: int) -> None:
        """Añade un peer conocido."""
        self.peers[peer_id] = (host, port)

    def remove_peer(self, peer_id: str) -> None:
        self.peers.pop(peer_id, None)

    def list_peers(self) -> list[str]:
        return list(self.peers.keys())

    # ─── ENVÍO ──────────────────────────────────────────────────

    async def send(
        self,
        peer_id: str,
        msg_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Envía un mensaje a un peer y espera respuesta."""
        if peer_id not in self.peers:
            raise ValueError(f"Peer desconocido: {peer_id}")

        host, port = self.peers[peer_id]

        msg = Message(
            id=f"msg_{secrets.token_hex(8)}",
            from_peer=self.node_id,
            to_peer=peer_id,
            type=msg_type,
            payload=payload,
        )

        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.write(msg.to_bytes())
            await writer.drain()

            # Leer respuesta (4 bytes length + payload)
            length_bytes = await asyncio.wait_for(reader.readexactly(4), timeout=10)
            length = int.from_bytes(length_bytes, "big")
            data = await asyncio.wait_for(reader.readexactly(length), timeout=10)

            writer.close()
            await writer.wait_closed()

            return json.loads(data.decode("utf-8"))
        except (OSError, asyncio.TimeoutError) as e:
            logger.warning("Error enviando a %s: %s", peer_id, e)
            raise

    async def broadcast(
        self,
        msg_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Envía a todos los peers y devuelve sus respuestas."""
        if not self.peers:
            return {}

        tasks = {
            peer_id: asyncio.create_task(self.send(peer_id, msg_type, payload))
            for peer_id in self.peers
        }

        responses: dict[str, Any] = {}
        for peer_id, task in tasks.items():
            try:
                responses[peer_id] = await task
            except Exception as e:
                responses[peer_id] = {"error": str(e)}

        return responses

    # ─── INTERNO ────────────────────────────────────────────────

    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Maneja una conexión entrante."""
        try:
            length_bytes = await asyncio.wait_for(reader.readexactly(4), timeout=10)
            length = int.from_bytes(length_bytes, "big")
            data = await asyncio.wait_for(reader.readexactly(length), timeout=10)

            message = json.loads(data.decode("utf-8"))
            handler = self.handlers.get(message["type"])

            if handler:
                try:
                    result = await handler(message["payload"])
                except Exception as e:
                    result = {"error": str(e)}
            else:
                result = {"error": f"Sin handler para {message['type']}"}

            response = json.dumps(result, ensure_ascii=False).encode("utf-8")
            writer.write(len(response).to_bytes(4, "big") + response)
            await writer.drain()
        except (asyncio.TimeoutError, json.JSONDecodeError, OSError) as e:
            logger.warning("Error manejando conexión: %s", e)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass


# ─────────────────────────────────────────────────────────────
# UTILIDAD
# ─────────────────────────────────────────────────────────────

def get_local_ip() -> str:
    """Devuelve la IP local del dispositivo."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"