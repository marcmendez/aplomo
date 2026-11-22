# Patterns, abstraction gates, and read budgets

Aplomo uses a reuse-before-create contract for non-trivial code changes. The objective is not to ban new abstractions; it is to make the decision visible before another implementation enters the repository.

## Request lifecycle

1. The skill reads the relevant project patterns and searches for candidates. `aplomo prepare` can provide a repository summary and a bounded candidate search.
2. The agent starts from a canonical implementation in `.engineering/patterns.md` when one applies.
3. `aplomo validate-abstraction` looks for candidates for a proposed class, service, interface, or module.
4. A matching candidate produces `needs_justification`. The agent must reuse it or explain the different responsibility or lifecycle.
5. `aplomo review-diff` checks tracked and untracked changes for duplicate declarations, test file changes, possible secrets, and excessive size.

## Pattern catalog

The skill can work with the code and guidance already in your repository. If your team has a preferred implementation, a short entry in `.engineering/patterns.md` points the agent to it. Each entry should answer:

- What responsibility does the pattern own?
- Which implementation is canonical?
- When should it be extended?
- What difference is sufficient to create something new?
- Which tests or commands validate compatibility?

Do not turn the catalog into general architecture documentation. Link to an ADR when the reasoning needs more space.

For example, a project might document its shared retry policy:

```markdown
## Retry policy

- Responsibility: decide which failures to retry and when to stop.
- Canonical implementation: `src/shared/retry.py`.
- Existing caller: `src/payments/charge.py`.
- Extend when: the workflow uses the same failure classification and retry limits.
- Validation: `pytest tests/test_retry.py`.
```

## Run local checks

The skill can run these optional commands, or you can run them yourself from the repository:

```bash
aplomo prepare "Add retries to a new workflow" --query "RetryPolicy"
aplomo validate-abstraction "NewRetryPolicy" "Retry transient failures"
aplomo review-diff
```

Commands return JSON. Candidate search is lexical and diff warnings are advisory. Architecture notes guide the agent. Use project tests or CI for rules that must block a merge.

## Abstraction decisions

`aplomo validate-abstraction` returns one of four states:

| Status | Meaning | Expected action |
|---|---|---|
| `pass` | The scoped search completed without a candidate. | Check whether the query covered the expected names and responsibilities. |
| `inconclusive` | The search stopped at a limit without returning a candidate. | Refine the query or widen the budget deliberately. |
| `needs_justification` | Candidates exist and no exception was supplied. | Reuse a candidate or provide a concrete responsibility/lifecycle difference. |
| `review_required` | Candidates and a justification both exist. | Compare them before accepting the new abstraction. |

The gate is lexical and deterministic. It surfaces evidence; it does not claim to prove semantic equivalence.

## Read budgets

Configure source reads in `.engineering/config.yaml`:

```yaml
context:
  max_files: 80
  max_chars: 200000
  max_matches: 12
```

The preflight divides the file and character allowance between repository mapping and candidate discovery. Results report actual consumption and a `stop_reason`:

- `complete`: every candidate file in scope was read;
- `match_limit`: enough evidence was found and returned;
- `file_budget`: the file allowance was exhausted;
- `character_budget`: the character allowance was exhausted.

When a no-match result is truncated, refine the query before increasing the budget. For monorepos, prefer a module-specific query or run the task from the relevant checkout rather than setting an unlimited global budget.

The budget applies to source content read by Aplomo. Small repository-owned metadata files such as `.engineering/architecture.yaml` and `.engineering/patterns.md` are returned separately. Diff review applies the limits separately to untracked content and existing declarations, reports both summaries, and warns when a pass is incomplete. Git's tracked diff is processed separately from these source-read budgets.

## Known limits

- Similar behavior under unrelated names may not be detected.
- Common names can produce false-positive candidates.
- Duplicate declaration checks currently focus on classes, interfaces, and named types.
- Generated or vendored directories are excluded from source discovery.
- A truncated no-match result is never evidence that the repository contains no equivalent.

## Optional integrations

To register the local analysis as MCP tools in a new project, use `aplomo init --agents codex --mcp`. Add `--hooks` if you want lifecycle events recorded in a local, gitignored log. These flags are independent.

For an existing project, edit `.engineering/config.yaml` and run `aplomo install`. To switch an older installation to the skill-based setup, set `integrations.mcp` and `integrations.hooks` to `false`. Aplomo removes unchanged adapters it owns and reports customized files for manual migration. Restart the assistant after changing its integrations. [Privacy](../PRIVACY.md)
