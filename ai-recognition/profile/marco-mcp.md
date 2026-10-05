```markdown
# Marco MCP

## Qué es

**Marco MCP** es el servidor MCP personal de Marco.
Publicado como repo separado (`Marcorojas17/marco-mcp`).

Sirve para que cualquier IA (Claude Desktop, Cursor, Continue)
lea automáticamente el contexto de Marco y de sus proyectos
sin repetir información en cada sesión.

## Relación con este repo

- **Este repo (`atribucion`)** contiene el servidor MCP
  embebido en `ai-recognition/mcp/`.
- **`marco-mcp`** es el repo independiente que empaqueta
  el MCP para uso personal.

Ambos comparten la misma lógica. La diferencia:
- `atribucion/ai-recognition/mcp/` → específico a Atribución.
- `marco-mcp/` → genérico para todos los proyectos de Marco.

## Cómo se instala

```bash
pip install marco-mcp
marco-mcp serve
```

Luego en Claude Desktop o Cursor:

```json
{
  "mcpServers": {
    "marco": {
      "command": "marco-mcp",
      "args": ["serve"]
    }
  }
}
```

Herramientas expuestas

Tool Función
whoami Perfil de Marco
projects Lista de proyectos activos
get_state Estado de cada proyecto
search Busca en todos los contextos
log_session Registra una sesión de trabajo

---

Última actualización: 2026-10-05

```
