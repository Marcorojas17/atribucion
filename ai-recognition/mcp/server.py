"""
Atribución — Servidor MCP.

Implementa el protocolo MCP (Model Context Protocol) para que
cualquier IA compatible (Claude Desktop, Cursor, Continue)
lea automáticamente el contexto del proyecto.

Uso:
    python -m ai_recognition.mcp.server

O configurado en Claude Desktop / Cursor.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[1]  # ai-recognition/
CONTEXT_ROOT = ROOT


def _read_file(rel_path: str) -> str:
    """Lee un archivo del contexto."""
    path = CONTEXT_ROOT / rel_path
    if not path.exists():
        return f"[No encontrado: {rel_path}]"
    return path.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────

def whoami() -> str:
    """Devuelve el perfil de Marco."""
    return _read_file("profile/marco.md")


def get_state() -> str:
    """Estado actual del proyecto."""
    return _read_file("state/current-phase.md")


def get_roadmap() -> str:
    """Hoja de ruta a 12 meses."""
    return _read_file("state/roadmap.md")


def get_decisions() -> str:
    """Decisiones arquitectónicas."""
    return _read_file("state/decisions.md")


def get_pending() -> str:
    """Deuda pendiente."""
    return _read_file("state/pending.md")


def get_log() -> str:
    """Bitácora de sesiones."""
    return _read_file("state/log.md")


def get_protocols() -> str:
    """Protocolos de respuesta."""
    protocols = []
    protocols_dir = CONTEXT_ROOT / "protocols"
    if protocols_dir.exists():
        for f in sorted(protocols_dir.glob("*.md")):
            protocols.append(f"## {f.stem}\n\n{f.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(protocols)


def search_context(query: str) -> str:
    """Busca un string en todo el contexto."""
    results: list[str] = []
    for path in CONTEXT_ROOT.rglob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if query.lower() in content.lower():
            rel = path.relative_to(CONTEXT_ROOT)
            lines = [
                f"  L{i + 1}: {line.strip()}"
                for i, line in enumerate(content.splitlines())
                if query.lower() in line.lower()
            ]
            results.append(f"### {rel}\n" + "\n".join(lines[:5]))
    return "\n\n".join(results) if results else f"[Sin resultados para: {query}]"


TOOLS = {
    "whoami": whoami,
    "get_state": get_state,
    "get_roadmap": get_roadmap,
    "get_decisions": get_decisions,
    "get_pending": get_pending,
    "get_log": get_log,
    "get_protocols": get_protocols,
    "search_context": search_context,
}


# ─────────────────────────────────────────────────────────────
# MCP PROTOCOL (stdio)
# ─────────────────────────────────────────────────────────────

def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Maneja una request JSON-RPC del MCP."""
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": name,
                        "description": (func.__doc__ or "").strip().split("\n")[0],
                        "inputSchema": {"type": "object", "properties": {}},
                    }
                    for name, func in TOOLS.items()
                ]
            },
        }

    if method == "tools/call":
        tool_name = params.get("name")
        func = TOOLS.get(tool_name)
        if not func:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Tool no encontrado: {tool_name}"},
            }

        try:
            if tool_name == "search_context":
                result = func(params.get("arguments", {}).get("query", ""))
            else:
                result = func()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": result}],
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(e)},
            }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Method no soportado: {method}"},
    }


def main() -> None:
    """Loop de stdin/stdout para el protocolo MCP."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(
                json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                }),
                flush=True,
            )


if __name__ == "__main__":
    main()