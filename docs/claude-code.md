# Claude Code

```bash
cd tu-repositorio
aplomo init --agents claude
aplomo doctor
```

Aplomo crea `.mcp.json`, `.claude/settings.json`, un bloque delimitado en `CLAUDE.md` y `.claude/skills/aplomo-review/SKILL.md`.

Reinicia Claude Code desde la raíz y acepta el servidor MCP del proyecto después de revisar su comando. Comprueba la conexión:

```text
Usa aplomo_find_existing_patterns para buscar el patrón de configuración actual.
```

Si `.mcp.json` o `.claude/settings.json` ya existían, Aplomo los marca como `skipped` para evitar perder tu configuración; combínalos manualmente si necesitas ambos.

```bash
aplomo doctor
aplomo eval
```
