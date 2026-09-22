# Contributing

You need Python 3.12 or newer and `uv`.

```bash
uv sync --python 3.12
uv run pytest -q
uv run aplomo eval
uv run python -m compileall -q src tests
uv build
```

`.engineering/` is the source of truth. Do not edit generated adapters directly: change the configuration or generator and run `uv run aplomo install`.

Before adding an abstraction, search for an existing equivalent, review the module boundary, and explain why the current pattern cannot be extended. Every functional change must include tests and preserve safe, idempotent installation.
