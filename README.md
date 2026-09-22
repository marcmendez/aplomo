# Aplomo

> Un mismo criterio de ingeniería, uses el agente que uses.

[![CI](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg)](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB)](https://www.python.org/downloads/)
[![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Aplomo mantiene las reglas de ingeniería dentro del repositorio y genera adaptadores finos para **Cursor**, **Codex** y **Claude Code**. Normaliza sus eventos, les ofrece las mismas herramientas MCP y evita que las instrucciones de arquitectura diverjan entre agentes.

```text
                         .engineering/
                         source of truth
                                │
                ┌───────────────┼───────────────┐
                │               │               │
              Hooks            MCP       Rules / skills
                │               │               │
                └───────────────┼───────────────┘
                                │
                  Cursor · Codex · Claude Code
```

## Qué resuelve

- Una única configuración versionable en `.engineering/`.
- Reglas equivalentes en los formatos nativos de cada agente.
- Cinco herramientas MCP para entender el repo, buscar patrones y revisar planes, arquitectura y diffs.
- Un contrato común de eventos para hooks incompatibles entre proveedores.
- Instalación conservadora: un archivo existente que Aplomo no posee se conserva.
- Evaluaciones locales y reproducibles, más un protocolo para medir comportamiento real.

## Requisitos

- Python **3.12 o superior**.
- Git para revisar diffs y para instalar directamente desde GitHub.
- `uv` recomendado; `pipx` es una alternativa válida.

## Instalar

Con `uv`:

```bash
uv tool install git+https://github.com/marcmendez/aplomo.git
```

O con `pipx`:

```bash
pipx install git+https://github.com/marcmendez/aplomo.git
```

Después, desde el repositorio que quieras preparar:

```bash
aplomo init --agents cursor codex claude
aplomo doctor
aplomo eval
```

Reinicia el agente para que vuelva a cargar sus archivos de proyecto. Si solicita confianza o aprobación para el MCP o los hooks, revisa el comando generado (`aplomo ...`) y acéptalo.

## Uso por agente

| Agente | Aplomo genera | Guía |
|---|---|---|
| Cursor | `.cursor/mcp.json`, hooks y una regla de proyecto | [Cursor](docs/cursor.md) |
| Codex | `.codex/config.toml`, hooks, `AGENTS.md` y skill | [Codex](docs/codex.md) |
| Claude Code | `.mcp.json`, hooks, `CLAUDE.md` y skill | [Claude Code](docs/claude-code.md) |

Cuando cambies `.engineering/config.yaml`, regenera los adaptadores:

```bash
aplomo install
aplomo doctor
```

## Cómo saber si funciona

Hay tres niveles de evidencia, y no conviene mezclarlos:

1. `pytest` valida las unidades y los casos límite del código.
2. `aplomo eval` comprueba normalización, configuración nativa, seguridad al instalar, idempotencia y MCP.
3. El benchmark A/B descrito en [Evaluación](docs/evaluation.md) mide si un agente comete menos errores en tareas reales con Aplomo que sin él.

```bash
aplomo eval
aplomo eval --json
```

Un resultado verde demuestra que Aplomo está correctamente instalado y que sus contratos funcionan. No demuestra por sí solo que cualquier modelo vaya a razonar mejor; esa afirmación requiere el benchmark de comportamiento.

## Comandos

```text
aplomo init      Detecta el stack, crea .engineering/ e instala adaptadores
aplomo install   Regenera los archivos gestionados
aplomo doctor    Detecta archivos ausentes u obsoletos
aplomo eval      Ejecuta las pruebas de aceptación del producto
aplomo hook      Normaliza y registra un evento de agente
aplomo mcp       Sirve las herramientas MCP por stdio
```

El antiguo comando `eng` permanece como alias de compatibilidad durante la transición.

## Herramientas MCP

- `aplomo_understand_repo`
- `aplomo_find_existing_patterns`
- `aplomo_review_plan`
- `aplomo_review_architecture`
- `aplomo_review_diff`

Los nombres `engineering_*` del primer prototipo siguen aceptándose internamente durante la migración, aunque ya no se anuncian a clientes nuevos.

## Desarrollo

```bash
git clone https://github.com/marcmendez/aplomo.git
cd aplomo
uv sync --python 3.12
uv run pytest -q
uv run aplomo eval
uv build
```

La CI repite estas comprobaciones en Python 3.12 y 3.13. Consulta [CONTRIBUTING.md](CONTRIBUTING.md).

## Alcance actual

Aplomo `0.1.0` es un MVP local: detecta tecnologías, indexa símbolos de forma ligera, normaliza eventos, genera integraciones y realiza revisiones heurísticas. No es todavía un compilador exhaustivo de arquitectura ni garantiza que un modelo obedezca cada regla. Los siguientes agentes se añadirán cuando exista una integración y una evaluación equivalentes, no solo una entrada más en una lista.

## Licencia

[MIT](LICENSE)
