<p align="center"><img src="assets/aplomo-icon.svg" width="76" height="76" alt=""></p>

<h1 align="center">Aplomo</h1>

<p align="center"><strong>Give your coding agent the patterns your team already uses.</strong></p>

<p align="center">
  <a href="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/marcmendez/aplomo/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/marcmendez/aplomo/releases"><img alt="GitHub release" src="https://img.shields.io/github/v/release/marcmendez/aplomo"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.12 or later" src="https://img.shields.io/badge/Python-3.12%2B-3776AB"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-315C4A"></a>
</p>

Aplomo is a review skill with optional local checks for **Cursor, Codex, and Claude Code**. It helps an agent find the code your team already relies on, extend it where it fits, and review the resulting diff.

## Install

With Python 3.12+, Git, and [uv](https://docs.astral.sh/uv/), install the CLI and initialize the project:

```bash
uv tool install --python 3.12 git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init --agents codex
```

Replace `codex` with `cursor` or `claude`, or pass all three. Open the repository in your assistant and select the Aplomo review skill.

| Assistant | Invoke the project skill | Guide |
| --- | --- | --- |
| Codex | `$aplomo-review` | [Codex](docs/codex.md) |
| Cursor | Select `aplomo-review` from the `/` menu | [Cursor and Cursor Cloud](docs/cursor.md) |
| Claude Code | `/aplomo-review` | [Claude Code](docs/claude-code.md) |

If you only want the workflow, copy the [standalone skill](skills/aplomo-review/SKILL.md) into your assistant's project skill directory, as shown in the guides. It uses the assistant's native search, Git, and test commands. The CLI adds installation and repeatable local checks.

## Example: add invoice retries

In `.engineering/patterns.md`, record a shared implementation your project actually uses. For example:

```markdown
## Retry policy

- Responsibility: decide which failures to retry and when to stop.
- Canonical implementation: `src/shared/retry.py`.
- Existing caller: `src/payments/charge.py`.
- Extend when: the new workflow uses the same failure classification and retry limits.
- Validation: `pytest tests/test_retry.py`.
```

Select the skill and ask:

> Add invoice retries for transient failures. Preserve payment retry behavior and test that invoice retries stop at the configured limit.

Before editing, the skill directs the agent to find the policy and a real caller. If the invoice workflow shares the same rules, the agent can extend or reuse the policy. If it needs a different lifecycle, the agent explains where that logic belongs. Before finishing, it reviews the diff for duplicate responsibilities, unrelated changes, and redundant comments, then runs the project's relevant tests.

## Run local checks

The skill can call these commands from the checkout. You can also run them yourself:

```bash
aplomo prepare "Add invoice retries" --query "RetryPolicy"
aplomo validate-abstraction "InvoiceRetryPolicy" "Handle transient invoice failures"
aplomo review-diff
```

The commands return JSON with the evidence they found. Candidate search is lexical and diff warnings are advisory. Repository architecture notes guide the agent. Use project tests or CI for rules that must block a merge. See [patterns and read budgets](docs/patterns-and-read-budgets.md) for status meanings and limits.

## Optional MCP and hooks

The default installation uses the skill and local commands. To register Aplomo's analysis as MCP tools in a new project, use `aplomo init --agents codex --mcp`. Add `--hooks` if you want lifecycle events recorded in a local, gitignored log. These flags are independent.

For an existing project, edit `.engineering/config.yaml` and run `aplomo install`. To switch an older installation to the skill-based setup, set `integrations.mcp` and `integrations.hooks` to `false`. Aplomo removes unchanged adapters it owns. If a file has been customized, it is preserved and the installer reports it so you can remove the obsolete Aplomo entry yourself. Restart the assistant after changing its integrations. [Privacy](PRIVACY.md)

## Repository layout

| Path | Purpose |
| --- | --- |
| `.engineering/` | Project patterns, architecture notes, and integration settings |
| [`skills/aplomo-review/`](skills/aplomo-review/) | Shared review workflow for all three assistants |
| [`src/engineering_harness/`](src/engineering_harness/) | Python CLI, local analysis, and optional MCP adapter |
| [`tests/`](tests/) and [`docs/`](docs/) | Tests and assistant setup guides |

## Development

```bash
uv sync --locked --python 3.12
uv run pytest -q
uv run aplomo eval
uv build
```

[CI](https://github.com/marcmendez/aplomo/actions/workflows/ci.yml) tests the integration and installs the built wheel in a clean repository. [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/marcmendez/aplomo/issues) · [MIT license](LICENSE)
