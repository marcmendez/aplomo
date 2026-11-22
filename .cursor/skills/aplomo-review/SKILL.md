---
name: aplomo-review
description: Review non-trivial repository plans, architecture choices, pattern reuse, tests, and final diffs before completion. Use when implementing or reviewing a feature, refactor, migration, or architectural change. Do not use for trivial text-only edits.
---

# Aplomo review

Use this workflow for non-trivial code changes. Use the smallest amount of repository context needed for the task.

1. Read the relevant entries in `.engineering/patterns.md` and `.engineering/architecture.yaml` when they exist. Search for an implementation and a real caller before writing code.
2. Extend the canonical implementation when it owns the same behavior. Before creating a class, service, interface, or module, identify its owner and explain any difference in responsibility or lifecycle.
3. Make a focused change through the existing entry points. Preserve caller contracts and test behavior that could regress.
4. Review the diff for duplicated responsibilities, layer violations, and unrelated changes. Remove comments that repeat the code. Keep comments that capture public contracts or non-obvious constraints. Run the repository's relevant checks.

Use native search, file inspection, Git, and tests. When the Aplomo CLI is available, use `aplomo prepare "request" --query "specific terms"`, `aplomo validate-abstraction "Name" "responsibility"`, or `aplomo review-diff` for focused, advisory evidence. If MCP is already configured, its corresponding tools run the same checks. Treat incomplete searches as inconclusive and refine the query before widening the budget.

Treat `.engineering/` as authoritative when the repository contains it. Do not edit generated agent adapters directly; update `.engineering/config.yaml` and run `aplomo install`.

Keep the workflow proportional. A typo or documentation correction does not require a full architecture review.
