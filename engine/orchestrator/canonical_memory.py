"""
Atribución Engine — Memoria canónica de MADRE.

Cada mensaje en una sala MADRE se persiste con:
- Agente autor
- Contenido
- Timestamp
- Hash SHA-256 (para verificación)

La memoria es append-only. Nadie puede modificar el pasado.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────
# MENSAJE
# ─────────────────────────────────────────────────────────────

@dataclass
class Message:
    """Mensaje canónico en la sala MADRE."""

    agent: str
    content: str
    role: str = "agent"  # user | agent | system
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            payload = f"{self.agent}|{self.content}|{self.timestamp}"
            self.hash = hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_context_str(self) -> str:
        """Formato para incluir en prompts."""
        return f"[{self.agent}] {self.content}"


# ─────────────────────────────────────────────────────────────
# MEMORIA
# ─────────────────────────────────────────────────────────────

class CanonicalMemory:
    """
    Memoria canónica persistente en JSONL.

    Uso:
        mem = CanonicalMemory(session_id="sala-1")
        mem.add("Codex", "Propongo usar Redis", role="agent")
        mem.add("Claude Code", "De acuerdo, refactorizo", role="agent")
        context = mem.get_context(limit=10)
    """

    def __init__(
        self,
        session_id: str = "default",
        state_dir: Path | None = None,
    ) -> None:
        self.session_id = session_id
        self.state_dir = state_dir or (Path.home() / ".atribucion" / "madre")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.state_dir / f"session-{session_id}.jsonl"
        self.messages: list[Message] = self._load()

    def add(
        self,
        agent: str,
        content: str,
        role: str = "agent",
    ) -> Message:
        """Añade un mensaje a la memoria canónica."""
        msg = Message(agent=agent, content=content, role=role)
        self.messages.append(msg)
        self._persist(msg)
        return msg

    def get_context(self, limit: int = 50) -> str:
        """Devuelve el contexto como string (para prompts)."""
        return "\n".join(m.to_context_str() for m in self.messages[-limit:])

    def last_from(self, agent: str) -> Message | None:
        """Último mensaje de un agente específico."""
        for msg in reversed(self.messages):
            if msg.agent == agent:
                return msg
        return None

    def clear(self) -> None:
        """Borra la memoria (irreversible)."""
        self.messages = []
        if self._file.exists():
            self._file.unlink()

    def verify_integrity(self) -> tuple[bool, list[str]]:
        """
        Verifica la integridad de todos los hashes.

        Devuelve (ok, lista_de_errores).
        """
        errors: list[str] = []
        for i, msg in enumerate(self.messages):
            payload = f"{msg.agent}|{msg.content}|{msg.timestamp}"
            expected = hashlib.sha256(payload.encode()).hexdigest()
            if msg.hash != expected:
                errors.append(f"Mensaje {i} alterado (hash no coincide)")
        return (len(errors) == 0, errors)

    # ─── PERSISTENCIA ───────────────────────────────────────────

    def _persist(self, msg: Message) -> None:
        with self._file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(msg.to_dict(), ensure_ascii=False) + "\n")

    def _load(self) -> list[Message]:
        if not self._file.exists():
            return []
        messages: list[Message] = []
        with self._file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    messages.append(Message(**data))
                except (json.JSONDecodeError, TypeError):
                    continue
        return messages