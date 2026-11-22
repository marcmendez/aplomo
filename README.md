<p align="center"><img src="assets/aplomo-icon.svg" width="76" height="76" alt=""></p>

<h1 align="center">Aplomo</h1>

<p align="center"><strong>Help your coding agent build on the code you already have.</strong></p>

<p align="center">
  <a href="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-315C4A"></a>
</p>

An AI-generated change can pass its tests and still leave you with a second version of logic your project already has. Aplomo is a **free, open-source skill for Cursor, Codex, and Claude Code** that helps the agent find what your project already uses and decide how to build on it.

Use it when you ask an agent to add a feature, refactor existing code, or review a change. It adds three steps to the work:

- **Find a precedent.** Look for similar code and read how real callers use it before editing.
- **Choose where the change belongs.** Extend an existing implementation when it owns the same behavior. Explain why a separate implementation fits when responsibilities differ.
- **Review what changed.** Check the diff for duplicated logic and unrelated edits, then run the project's relevant tests.

You can start with an existing repo as it is. Teams can also point Aplomo at shared implementations and their tests so each assistant works from the same guidance. [Record your team's patterns](docs/patterns-and-read-budgets.md#pattern-catalog)

## Install

The CLI installer requires Python 3.12+, Git, and [uv](https://docs.astral.sh/uv/). Run the following, replacing `your-repository` with your project path:

```bash
uv tool install --python 3.12 git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init --agents codex
```

Replace `codex` with `cursor` or `claude` for your assistant. You can pass multiple names to set up a shared repository.

| Assistant | Invoke the project skill | Guide |
| --- | --- | --- |
| Codex | `$aplomo-review` | [Codex](docs/codex.md) |
| Cursor | Select `aplomo-review` from the `/` menu | [Cursor and Cursor Cloud](docs/cursor.md) |
| Claude Code | `/aplomo-review` | [Claude Code](docs/claude-code.md) |

The guides also show how to copy the [standalone skill](skills/aplomo-review/SKILL.md) into a project without installing the CLI.

## Use it on your next change

Open the project, select the skill and describe the work in your own words:

> Add filtering to this list. Follow the approach used in similar screens and test the new behavior.

For that request, the agent looks for a screen with working filters, checks whether its code fits the new screen, and runs the relevant tests after the edit. The skill uses the assistant's existing search, Git, and test tools. [Local checks and their limits](docs/patterns-and-read-budgets.md#run-local-checks)

## Optional MCP and hooks

MCP and local event logging are opt-in. See [how to enable them or migrate an older installation](docs/patterns-and-read-budgets.md#optional-integrations).

[Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/marcmendez/aplomo/issues) · [Privacy](PRIVACY.md) · [MIT license](LICENSE)
