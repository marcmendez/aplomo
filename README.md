<p align="center"><img src="assets/aplomo-icon.svg" width="76" height="76" alt=""></p>

<h1 align="center">Aplomo</h1>

<p align="center"><strong>Help your coding agent build on the code you already have.</strong></p>

<p align="center">
  <a href="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-315C4A"></a>
</p>

An AI-generated change can pass its tests and still leave you with a second version of logic your project already has. Aplomo is a **free, open-source skill for Cursor, Codex, and Claude Code** that helps the agent find what your project already uses and decide how to build on it.

Set it up once in a repository, then ask your coding agent for changes as usual. Aplomo's project instructions guide the agent to use the skill for features, refactors, and other changes where reuse or review matters.

The skill guides the agent through three steps:

- **Find a precedent.** Search the affected part of the project first and read the relevant code and callers.
- **Choose where the change belongs.** Extend an existing implementation when it owns the same behavior. Explain why a separate implementation fits when responsibilities differ.
- **Review what changed.** Run focused checks for small edits. For bigger changes, choose the reviews that fit the risk: architecture, correctness, or compatibility.

You can start with an existing repo as it is. Teams can also point Aplomo at shared implementations and their tests so each assistant works from the same guidance. [Record your team's patterns](docs/patterns-and-read-budgets.md#pattern-catalog)

## Install

Run this once from your project root with Git and [uv](https://docs.astral.sh/uv/) available. The command uses Python 3.12.

```bash
uvx --python 3.12 --from git+https://github.com/marcmendez/aplomo.git aplomo init
```

`aplomo init` adds the skill and project instructions for the assistants it detects. If it finds none, it prepares all three. Commit the generated files to share the setup with your team or cloud agents. To refresh an existing setup, use the same command with `install` in place of `init`.

Setup guides for [Codex and Codex Cloud](docs/codex.md), [Cursor and Cursor Cloud](docs/cursor.md), and [Claude Code](docs/claude-code.md).

## Make your next request as usual

Open the project in your assistant and describe the change in your own words:

> Add filtering to the projects list.

The project instructions prompt the agent to look for existing filters and use the relevant checks. Routine edits can stay on the assistant's regular path. [How review and scoped search work](docs/patterns-and-read-budgets.md#choose-reviews)

## Optional MCP and hooks

MCP and local event logging are opt-in. See [how to enable them or migrate an older installation](docs/patterns-and-read-budgets.md#optional-integrations).

[Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/marcmendez/aplomo/issues) · [Privacy](PRIVACY.md) · [MIT license](LICENSE)
