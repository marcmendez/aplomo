# Codex

```bash
cd tu-repositorio
aplomo init --agents codex
aplomo doctor
```

Aplomo crea `.codex/config.toml`, `.codex/hooks.json`, un bloque delimitado en `AGENTS.md` y `.agents/skills/aplomo-review/SKILL.md`.

Abre o reinicia la tarea de Codex desde ese repositorio y confía en el proyecto cuando la aplicación lo solicite. Comprueba la conexión:

```text
Usa aplomo_understand_repo y después aplomo_review_architecture.
```

Aplomo solo gestiona el bloque comprendido entre `<!-- aplomo:start -->` y `<!-- aplomo:end -->`; el resto de `AGENTS.md` se conserva.

```bash
aplomo doctor
aplomo eval
```
