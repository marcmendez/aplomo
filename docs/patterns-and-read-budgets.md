# Patterns, abstraction gates, and read budgets

Aplomo uses a reuse-before-create contract for non-trivial code changes. The objective is not to ban new abstractions; it is to make the decision visible before another implementation enters the repository.

## Request lifecycle

1. `aplomo_prepare_change` maps the repository, reads its architecture and pattern catalog, and performs a bounded candidate search.
2. The agent starts from a canonical implementation in `.engineering/patterns.md` when one applies.
3. `aplomo_validate_abstraction` evaluates a proposed class, service, interface, or module.
4. A matching candidate produces `needs_justification`. The agent must reuse it or explain the different responsibility or lifecycle.
5. `aplomo_review_diff` checks tracked and untracked changes for duplicate declarations, tests, possible secrets, and excessive size.

## Pattern catalog

Keep `.engineering/patterns.md` short and operational. Each entry should answer:

- What responsibility does the pattern own?
- Which implementation is canonical?
- When should it be extended?
- What difference is sufficient to create something new?
- Which tests or commands validate compatibility?

Do not turn the catalog into general architecture documentation. Link to an ADR when the reasoning needs more space.

## Abstraction decisions

`aplomo_validate_abstraction` returns one of three states:

| Status | Meaning | Expected action |
|---|---|---|
| `pass` | No candidate was found inside the read budget. | Confirm whether the search completed; implement only if the scoped evidence is sufficient. |
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

The budget applies to source content read by Aplomo. Small repository-owned metadata files such as `.engineering/architecture.yaml` and `.engineering/patterns.md` are returned separately.

## Known limits

- Similar behavior under unrelated names may not be detected.
- Common names can produce false-positive candidates.
- Duplicate declaration checks currently focus on classes, interfaces, and named types.
- Generated or vendored directories are excluded from source discovery.
- A truncated no-match result is never evidence that the repository contains no equivalent.
