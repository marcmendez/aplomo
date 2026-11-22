<p align="center"><img src="assets/aplomo-icon.svg" width="76" height="76" alt=""></p>

<h1 align="center">Aplomo</h1>

<p align="center"><strong>Help your coding agent build on the code you already have.</strong></p>

<p align="center">
  <a href="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-315C4A"></a>
</p>

An AI-generated change can pass its tests and still leave you with a second version of logic your project already has. Aplomo is a **free, open-source skill for Cursor, Codex, and Claude Code** that helps the agent find what your project already uses and decide how to build on it.

Use it when you ask an agent to add a feature, refactor existing code, or review a change. It adds three steps to the work:

- **Find a precedent.** Search the affected part of the project first and read the relevant code and callers.
- **Choose where the change belongs.** Extend an existing implementation when it owns the same behavior. Explain why a separate implementation fits when responsibilities differ.
- **Review what changed.** Run focused checks for small edits. For bigger changes, choose the reviews that fit the risk: architecture, correctness, or compatibility.

You can start with an existing repo as it is. Teams can also point Aplomo at shared implementations and their tests so each assistant works from the same guidance. [Record your team's patterns](docs/patterns-and-read-budgets.md#pattern-catalog)

## Install

The CLI installer requires Python 3.12+, Git, and [uv](https://docs.astral.sh/uv/). Run the following, replacing `your-repository` with your project path:

```bash
uv tool install --python 3.12 git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init
```

`aplomo init` is a one-time terminal command for any supported assistant. It detects assistants from the checkout and available commands, and installs portable skills for all three if it finds none. Use `--agents codex` or another explicit list when you want to choose.

For a project already set up with Aplomo, update the CLI and run `aplomo install` to refresh the skill.

| Assistant | Invoke the project skill | Guide |
| --- | --- | --- |
| Codex | `$aplomo-review` | [Codex and Codex Cloud](docs/codex.md) |
| Cursor | Select `aplomo-review` from the `/` menu | [Cursor and Cursor Cloud](docs/cursor.md) |
| Claude Code | `/aplomo-review` | [Claude Code](docs/claude-code.md) |

The guides also show how to copy the [standalone skill folder](skills/aplomo-review/) into a project without installing the CLI.

## Use it on your next change

Open the project, select the skill and describe the work in your own words:

> Add filtering to this list. Follow the approach used in similar screens and test the new behavior.

For that request, the agent looks for a screen with working filters, checks whether its code fits the new screen, and runs the relevant tests after the edit. A change that also touches a shared API can get a separate compatibility review. Where the assistant supports authorized delegation, independent reviewers can take the selected checks. [How review and scoped search work](docs/patterns-and-read-budgets.md#choose-reviews)

## Optional MCP and hooks

MCP and local event logging are opt-in. See [how to enable them or migrate an older installation](docs/patterns-and-read-budgets.md#optional-integrations).

[Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/marcmendez/aplomo/issues) · [Privacy](PRIVACY.md) · [MIT license](LICENSE)
