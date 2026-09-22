# Cursor

```bash
cd tu-repositorio
aplomo init --agents cursor
aplomo doctor
```

Aplomo crea `.cursor/mcp.json`, `.cursor/hooks.json` y `.cursor/rules/aplomo.mdc`. Reabre el proyecto; en **Settings → Tools & MCP**, `aplomo` debe aparecer habilitado. Prueba:

```text
Usa aplomo_understand_repo y resume los módulos principales.
```

Si uno de esos archivos ya existía y Aplomo no era su propietario, la instalación lo marca como `skipped` y no lo reemplaza. Combina ambos contenidos manualmente si necesitas ambas configuraciones.

```bash
aplomo doctor
aplomo eval
```
