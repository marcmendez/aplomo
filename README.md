<p align="center"><img src="assets/aplomo-icon.svg" width="76" height="76" alt=""></p>

<h1 align="center">Aplomo</h1>

<p align="center"><strong>Reuse existing code in AI-assisted changes.</strong></p>

<p align="center">
  <a href="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-315C4A"></a>
</p>

A change can pass its tests and still duplicate logic that already exists in the codebase. **Aplomo is an open-source skill for Cursor, Codex, and Claude Code** that asks the agent to look for an existing implementation before writing another.

## What it checks

- **Reuse.** Search the affected module first. Read the existing implementation and its callers before deciding whether to extend it.
- **Design.** Identify which module should own the new behavior and which callers rely on the current contract.
- **Validation.** Review the diff and run the relevant tests. Changes that affect module boundaries or shared contracts can get a separate architecture or compatibility review.

The skill starts with the code in your repository. If your team has a preferred implementation, [record it in a pattern catalog](docs/patterns-and-read-budgets.md#pattern-catalog).

## Install

Run this once from the repository root. It requires Git and [uv](https://docs.astral.sh/uv/) and runs with Python 3.12.

```bash
uvx --python 3.12 --from git+https://github.com/marcmendez/aplomo.git aplomo init
```

`aplomo init` writes the skill and project instructions for the assistants it detects. If it finds none, it writes the files for all three. Commit those files so teammates and cloud agents can use them from the checkout. To refresh an existing setup, replace `init` with `install`.

[Codex and Codex Cloud](docs/codex.md) · [Cursor and Cursor Cloud](docs/cursor.md) · [Claude Code](docs/claude-code.md)

## Use it in your assistant

Open the project and ask for a change.

> Add filtering to the projects list.

The project instructions tell the assistant when to load Aplomo. For this request, the skill directs it to find an existing filter and check how it is used before adding one. Routine edits can use the usual local checks. [Review and search details](docs/patterns-and-read-budgets.md#choose-reviews)

## Optional MCP and hooks

MCP and event logging are opt-in. See [how to enable them or update an older installation](docs/patterns-and-read-budgets.md#optional-integrations).

[Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/marcmendez/aplomo/issues) · [Privacy](PRIVACY.md) · [MIT license](LICENSE)
