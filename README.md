# Aplomo

> One repository standard for Cursor, Codex, and Claude Code.

[![CI](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg)](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB)](https://www.python.org/downloads/)
[![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Coding agents are good at writing code. They are less reliable at remembering which boundary matters in *this* repository, whether a pattern already exists, and what must be checked before a change is finished.

Aplomo gives Cursor, Codex, and Claude Code the same repository-aware workflow. You describe the change normally; Aplomo supplies the relevant structure, conventions, architecture rules, and a final diff review through each agent's native integration.

```text
"Add invoice retries and tests"
              │
              ▼
     Cursor / Codex / Claude Code
              │
              ├─ one repository preflight
              │  modules · existing patterns · architecture
              ├─ implementation with focused tests
              └─ one final diff review
                         │
                         ▼
              your repository remains in control
```

Aplomo does not proxy prompts, choose a model, or upload repository contents. Its current MCP tools are read-only and its hook events stay in a local, gitignored file.

## Why teams use it

- **One source of truth.** Put engineering rules in `.engineering/`; Aplomo generates the native files each supported agent expects.
- **Normal requests.** No prompt prefix, wrapper chat, or new task syntax.
- **Less integration drift.** The same preflight and final review follow a request when a developer changes coding assistants.
- **Pattern reuse first.** The agent sees relevant implementations before inventing another abstraction.
- **Safe adoption.** Existing configuration that Aplomo does not own is preserved and reported instead of silently overwritten.
- **Local by default.** Repository analysis and lifecycle metadata stay on the machine or cloud agent running the task.

## Install in a repository

Requirements: Python 3.12 or newer, Git, and either `uv` or `pipx`.

```bash
uv tool install git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init --agents cursor codex claude
```

With `pipx`, replace the first command with:

```bash
pipx install git+https://github.com/marcmendez/aplomo.git
```

Restart or reopen the coding assistant so it loads the new project integration. From then on, make the same requests you already make:

```text
Add pagination to the users endpoint and cover the edge cases with tests.
```

The generated launcher is pinned to Aplomo's isolated Python environment. It does not rely on the `PATH` inherited by a desktop app.

### Choose only the agents you use

```bash
aplomo init --agents cursor
aplomo init --agents codex claude
```

| Agent | Native integration | Guide |
|---|---|---|
| Cursor | project rule, MCP server, lifecycle hooks | [Cursor setup](docs/cursor.md) |
| Codex | `AGENTS.md`, skill, MCP server, lifecycle hooks | [Codex setup](docs/codex.md) |
| Claude Code | `CLAUDE.md`, skill, MCP server, lifecycle hooks | [Claude Code setup](docs/claude-code.md) |

## Cursor Cloud

Cursor Cloud runs in its own VM. It does not inherit the Aplomo installation or MCP process from your laptop.

1. Commit `.engineering/` and the generated Cursor files.
2. In the cloud environment setup, install Aplomo and regenerate the machine-local launcher:

   ```bash
   uv tool install git+https://github.com/marcmendez/aplomo.git
   aplomo install
   ```

3. Add an stdio MCP server in the Cursor dashboard or Cloud Agent API with:

   ```text
   command: ./.engineering/aplomo-runtime
   args:    mcp --root .
   ```

The command runs inside the Cloud VM and reads that checkout only. Cursor documents the VM model and supported MCP transports in its [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities) and [Cloud Agent API](https://prod.cursor.com/docs/cloud-agent/api/endpoints).

## What gets installed

`.engineering/config.yaml` is the source of truth; everything else is a native adapter or local runtime file.

```text
your-repository/
├── .engineering/
│   ├── config.yaml              # agents and enabled integrations
│   ├── architecture.yaml        # boundaries and repository rules
│   ├── decisions/               # architecture decisions
│   ├── aplomo-runtime           # machine-local launcher, gitignored
│   └── events.jsonl             # local lifecycle events, gitignored
├── .cursor/                     # Cursor adapters
├── .codex/                      # Codex adapters
├── .claude/                     # Claude Code adapters
├── .agents/skills/              # portable agent skill
├── AGENTS.md                    # managed Aplomo section for Codex
└── CLAUDE.md                    # managed Aplomo section for Claude Code
```

Change `.engineering/config.yaml`, then regenerate rather than editing generated adapters:

```bash
aplomo install
```

## Plugin and CLI

This repository includes a portable Agent Plugin manifest and Aplomo review skill. The skill can fall back to an agent's native search, test, and diff tools. The CLI installation above adds the full local experience: native project configuration, the repository-aware MCP server, hooks, and the PATH-independent runtime launcher.

The split is deliberate. A public hosted MCP server would require sending repository context to a remote service; Aplomo 1.0 keeps that context where the coding agent is already running.

## Evidence, not promises

The release gate currently covers:

- 31 automated tests on Python 3.12 and 3.13;
- 6 deterministic acceptance checks for three-agent configuration, safe installation, byte-for-byte regeneration, MCP initialize/list/call, real subprocess startup, and real hook persistence;
- a clean-wheel installation into a fresh Git repository in CI;
- manifest/version synchronization and read-only tool annotations.

We also publish the first paired Codex pilot instead of turning it into a marketing claim. Across three small tasks, baseline and Aplomo both passed all 10 hidden checks. Aplomo used two MCP review calls per task, 23% more uncached-plus-output tokens, and 44% more wall time in this single-run sample. It did **not** establish token savings or a quality uplift. The useful conclusion is narrower: the workflow reached parity while enforcing the same repository checks, and its overhead is now measured. See the [benchmark method and pilot result](benchmarks/results/2026-09-26-codex-pilot.md).

That benchmark is intentionally reproducible:

```bash
uv run python benchmarks/run_codex.py --repetitions 3 --output benchmark-results.json
```

We will only claim productivity or quality improvements after repeated, representative tasks show them.

## Commands

```text
aplomo init      Detect the stack, create .engineering/, and install adapters
aplomo install   Regenerate managed adapters from .engineering/config.yaml
aplomo doctor    Check configuration, generated files, and the real MCP runtime
aplomo eval      Run deterministic acceptance checks
aplomo hook      Normalize one lifecycle event
aplomo mcp       Run the repository-aware MCP server over stdio
```

## Development and support

```bash
git clone https://github.com/marcmendez/aplomo.git
cd aplomo
uv sync --python 3.12
uv run pytest -q
uv run aplomo eval
uv build
```

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing generated integrations. Bugs and feature requests belong in [GitHub Issues](https://github.com/marcmendez/aplomo/issues); security reports follow [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
