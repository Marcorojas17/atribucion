```markdown
# AI-MCP-SERVER.md

**Servidor MCP (Model Context Protocol) de reconocimiento IA.**

Permite que cualquier IA compatible (Claude Desktop, Cursor,
Continue, Copilot) lea automáticamente el contexto del proyecto
sin que tengas que explicarlo cada vez.

---

## Qué expone

| Tool | Función |
|---|---|
| `whoami` | Devuelve el perfil del owner |
| `get_state` | Estado actual del proyecto |
| `get_roadmap` | Hoja de ruta |
| `get_decisions` | Decisiones arquitectónicas |
| `get_pending` | Deuda abierta |
| `log_session` | Registra una sesión |
| `search_context` | Busca en todo el contexto |

---

## Instalación

```bash
pip install mcp
```

---

Configuración en Claude Desktop

Edita ~/Library/Application Support/Claude/claude_desktop_config.json
(macOS) o %APPDATA%\Claude\claude_desktop_config.json (Windows):

```json
{
  "mcpServers": {
    "atribucion": {
      "command": "python",
      "args": ["-m", "ai_recognition.mcp.server"],
      "cwd": "/ruta/a/atribucion"
    }
  }
}
```

---

Configuración en Cursor

En .cursor/mcp.json:

```json
{
  "mcpServers": {
    "atribucion": {
      "command": "python",
      "args": ["-m", "ai_recognition.mcp.server"]
    }
  }
}
```

---

Configuración en Continue

En ~/.continue/config.json:

```json
{
  "experimental": {
    "mcpServers": {
      "atribucion": {
        "command": "python",
        "args": ["-m", "ai_recognition.mcp.server"]
      }
    }
  }
}
```

---

Cómo funciona

1. La IA se conecta al servidor MCP.
2. Consulta whoami para saber quién eres.
3. Consulta get_state para saber en qué fase estás.
4. Pregunta "¿en qué trabajamos hoy?".
5. Tú respondes y arrancan sin repetir contexto.

Ahorro: 15-30 minutos por sesión.

---

Estado

🔴 En desarrollo. El servidor completo se implementa en
ai-recognition/mcp/server.py.

---

Marco Antonio Rojas Valdovinos

```
