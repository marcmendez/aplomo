<p align="center"><img src="assets/aplomo-icon.svg" width="76" height="76" alt=""></p>

<h1 align="center">Aplomo</h1>

<p align="center"><strong>Give your coding agent the patterns your team already uses.</strong></p>

<p align="center">
  <a href="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/marcmendez/aplomo/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/marcmendez/aplomo"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.12 or later" src="https://img.shields.io/badge/Python-3.12%2B-3776AB"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-315C4A"></a>
</p>

Aplomo brings a repository's design patterns and review checks into **Cursor, Codex, and Claude Code**. When you ask for invoice retries, for example, the agent can find your shared retry policy, inspect where it is already used, and decide whether to extend it before writing another implementation.

## Quick start

Requires Python 3.12+, Git, and [uv](https://docs.astral.sh/uv/) or pipx.

```bash
uv tool install --python 3.12 git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init --agents codex
```

Choose the assistants you use. Run `aplomo init --agents cursor codex claude` to configure all three. Open the project again and approve its project-level configuration if your assistant prompts you. Add a real entry to `.engineering/patterns.md` that links a shared implementation and its tests.

Then ask for changes as usual:

> Add invoice retries for transient failures and cover the retry limits with tests.

| Assistant | What Aplomo installs | Setup |
| --- | --- | --- |
| Cursor | Project rule, MCP configuration, hooks | [Cursor and Cursor Cloud](docs/cursor.md) |
| Codex | `AGENTS.md` instructions, skill, MCP configuration, hooks | [Codex](docs/codex.md) |
| Claude Code | `CLAUDE.md` instructions, skill, MCP configuration, hooks | [Claude Code](docs/claude-code.md) |

## From request to diff

1. **Before editing**, the agent requests a repository summary and a bounded search for candidate patterns. The result includes file locations, the pattern catalog, and the project architecture notes.
2. **Before adding an abstraction**, the agent looks for an existing implementation to extend or explains why the new responsibility or lifecycle deserves its own implementation.
3. **Before handing back the change**, the agent reviews the diff and runs focused tests. Aplomo can flag duplicate declaration names, code changes without accompanying test edits, and possible secrets.

The checks are advisory. Candidate search is lexical, so equivalent implementations with different names can be missed. Architecture notes guide the agent. Use your existing tests and CI to enforce rules that must block a merge. [Patterns, statuses, and read budgets](docs/patterns-and-read-budgets.md)

The full integration runs a local MCP subprocess in the assistant's environment. Its tools analyze the checkout and return results to the assistant. Lifecycle hooks record events in a gitignored file. A portable [review skill](skills/aplomo-review/SKILL.md) also describes the workflow using native search, Git, and tests when MCP is unavailable. [Privacy](PRIVACY.md)

## Repository layout

| Path | Purpose |
| --- | --- |
| `.engineering/config.yaml` | Agents, integrations, and read budgets |
| `.engineering/patterns.md` | Canonical implementations and the conditions for extending them |
| `.engineering/architecture.yaml` | Project boundaries and engineering rules |
| [`src/engineering_harness/`](src/engineering_harness/) | Python CLI, repository analysis, and MCP adapter |
| [`tests/`](tests/) | Unit and integration tests |
| [`docs/`](docs/) | Setup and workflow guides |

Run `aplomo install` after changing project configuration. Machine-specific launchers and event logs stay out of Git. If an existing adapter belongs to your project, the installer reports the conflict so you can merge it.

## Development

```bash
uv sync --locked --python 3.12
uv run pytest -q
uv run aplomo eval
uv build
```

[CI](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml) tests the integration and installs the built wheel in a clean repository. [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/marcmendez/aplomo/issues) · [MIT license](LICENSE)
