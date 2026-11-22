---
name: aplomo-review
description: Find existing patterns and choose proportionate validation for meaningful code changes. Use for features, refactors, migrations, cross-module edits, or explicit code reviews. Skip routine requests that need only local verification.
---

# Aplomo review

## Decide what the change needs

- For a clear, contained edit, work in the affected area and run its focused checks. Skip a repository inventory, a formal plan, and separate reviewers.
- For a broader or uncertain change, identify the affected behavior, module boundaries, and caller contracts. Use the relevant review profiles below.

## Find a pattern before editing

1. Start with files named in the request or the current diff. Check relevant entries in `.engineering/patterns.md` and `.engineering/architecture.yaml` if the repository has them.
2. Search for exact symbols, terminology, and callers in the affected module. List matching paths first. Read only the relevant definitions, one real caller, and tests for the behavior in question. Follow concrete references into shared code before trying a repository-wide search.
3. Reuse the implementation that owns the behavior. Before adding a class, service, interface, or module, explain the distinct ownership or lifecycle. An incomplete search calls for a narrower query or the next relevant directory.

Prefer native search. For a short list of candidates from the local CLI, run `aplomo prepare "request" --query "specific symbol" --path path/to/module`. Add another `--path` when there is evidence to look in a second directory. Use `aplomo review-diff` when its advisory warnings would be useful. The same checks are available over optional MCP.

## Validate the change

Select only the profiles whose triggers apply. Open their instructions on demand:

- [Architecture](references/architecture.md) for new abstractions, cross-module dependencies, or ownership changes.
- [Correctness](references/correctness.md) for changed behavior, edge cases, or error handling.
- [Compatibility](references/compatibility.md) for public APIs, migrations, shared contracts, or overlap with nearby changes.

Run the repository's relevant tests and checks. Use any project skill that handles the selected area. For independent review on a substantial change, delegate selected profiles to read-only reviewers when delegation is authorized and supported. Give each reviewer the requirement, the same diff and its base, relevant paths, and only their profile. Otherwise, apply the profiles in the current session. Consolidate findings and re-run the affected checks after any fixes. Report results that were actually verified and any open questions.

Keep the final diff focused. Remove comments that repeat the code. Preserve comments that capture public contracts or constraints the code cannot express.

Treat `.engineering/` as authoritative when the repository contains it. Do not edit generated agent adapters directly; update `.engineering/config.yaml` and run `aplomo install`.
