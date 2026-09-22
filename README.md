# Aplomo

> One engineering standard for Cursor, Codex, and Claude Code.

[![CI](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg)](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB)](https://www.python.org/downloads/)
[![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Aplomo keeps your repository's engineering rules independent from the coding agent you use. It installs native project instructions, MCP tools, and lifecycle hooks so Cursor, Codex, and Claude Code work from the same repository context.

## Quick start

Install Aplomo once:

```bash
uv tool install git+https://github.com/marcmendez/aplomo.git
```

You can use `pipx` instead:

```bash
pipx install git+https://github.com/marcmendez/aplomo.git
```

Initialize it inside a repository:

```bash
cd your-repository
aplomo init --agents cursor codex claude
```

Reopen the project in your coding agent. That is all the setup required.

## Use it

There is no special prompt syntax and no wrapper command for your requests. Ask the agent normally:

```text
Add rate limiting to the public API and cover it with tests.
```

When the project opens, the agent loads Aplomo's generated project instructions and MCP configuration. During the task it can inspect the repository, search for existing patterns, review the plan, and review the final diff using the same tools regardless of which supported agent is running.

```text
Your prompt
    │
    ▼
Cursor / Codex / Claude Code
    │ loads native project instructions
    │ uses Aplomo MCP tools when needed
    │ emits lifecycle events through hooks
    ▼
Your repository + .engineering/ rules
```

Aplomo does not proxy prompts or replace the agent. The agent remains responsible for the implementation; Aplomo supplies shared repository context, a consistent workflow, and portable review tools.

## Agent integrations

| Agent | Native files installed | What happens when you open the project |
|---|---|---|
| [Cursor](docs/cursor.md) | `.cursor/mcp.json`, `.cursor/hooks.json`, `.cursor/rules/aplomo.mdc` | The always-on project rule is loaded, the Aplomo MCP server becomes available, and edit/shell events are recorded. |
| [Codex](docs/codex.md) | `.codex/config.toml`, `.codex/hooks.json`, `AGENTS.md`, `.agents/skills/aplomo-review/SKILL.md` | Codex reads the repository instructions and can use the Aplomo review skill and MCP tools throughout the task. |
| [Claude Code](docs/claude-code.md) | `.mcp.json`, `.claude/settings.json`, `CLAUDE.md`, `.claude/skills/aplomo-review/SKILL.md` | Claude Code reads the project memory, discovers the skill and MCP server, and records configured lifecycle events. |

See the linked guides for exact setup, generated files, and a first prompt for each agent.

## What Aplomo asks the agent to do

Before introducing a new abstraction, the generated workflow asks the agent to:

1. Understand the repository and its module boundaries.
2. Search for an existing implementation or pattern.
3. Explain why the existing pattern cannot be extended.
4. Review the implementation plan.
5. Review the final diff before declaring completion.

The MCP server exposes the same five tools everywhere:

- `aplomo_understand_repo`
- `aplomo_find_existing_patterns`
- `aplomo_review_plan`
- `aplomo_review_architecture`
- `aplomo_review_diff`

## Repository layout

```text
.
├── .engineering/
│   ├── config.yaml              # source of truth for agent integrations
│   ├── architecture.yaml        # repository boundaries and engineering rules
│   ├── decisions/               # architecture decision records
│   ├── events.jsonl             # local normalized hook events (gitignored)
│   └── generated-manifest.json  # files currently owned by Aplomo
├── .cursor/                     # generated Cursor adapters
├── .codex/                      # generated Codex adapters
├── .claude/                     # generated Claude Code adapters
├── .agents/skills/              # portable generated skills
├── docs/                        # agent-specific setup guides
├── src/engineering_harness/     # dependency-free Python runtime
└── tests/                       # unit and integration tests
```

`.engineering/` is the source of truth. Agent-specific files are generated outputs and should not be edited directly.

## Configuration

The generated `.engineering/config.yaml` selects the agents and integration surfaces:

```yaml
version: 1
project_name: "your-project"
agents: ["cursor", "codex", "claude"]
technologies: ["Python"]
integrations:
  hooks: true
  mcp: true
  skills: true
```

After changing it, regenerate the native adapters:

```bash
aplomo install
```

Aplomo preserves an existing agent configuration that it does not own and reports it as `skipped`, so it will not silently overwrite project setup.

## Commands

```text
aplomo init      Detect the stack, create .engineering/, and install adapters
aplomo install   Regenerate managed agent files from .engineering/config.yaml
aplomo doctor    Report missing or stale integrations
aplomo hook      Normalize one agent lifecycle event
aplomo mcp       Run the repository-aware MCP server over stdio
```

The original `eng` command remains available as a compatibility alias.

## Requirements

- Python 3.12 or newer
- Git for diff review and installation from GitHub
- `uv` or `pipx` for isolated installation

## Development

```bash
git clone https://github.com/marcmendez/aplomo.git
cd aplomo
uv sync --python 3.12
uv run pytest -q
uv build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor workflow.

## Status

Aplomo 0.1.0 is an early local-first release. It provides lightweight repository analysis, event normalization, native integration generation, and heuristic plan and diff reviews. It does not enforce policy outside the capabilities exposed by each agent.

## License

[MIT](LICENSE)
