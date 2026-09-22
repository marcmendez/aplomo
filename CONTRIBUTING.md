# Contribuir

Necesitas Python 3.12+ y `uv`.

```bash
uv sync --python 3.12
uv run pytest -q
uv run aplomo eval
uv run python -m compileall -q src tests
uv build
```

`.engineering/` es la fuente de verdad. No edites los adaptadores generados directamente: cambia la configuración o el generador y ejecuta `uv run aplomo install`.

Antes de añadir una abstracción, busca un equivalente, revisa el límite del módulo y explica por qué el patrón existente no se puede ampliar. Todo cambio funcional debe incluir pruebas y mantener la instalación segura e idempotente.
