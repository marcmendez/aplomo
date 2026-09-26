---
name: aplomo-review
description: Review non-trivial repository plans, architecture choices, pattern reuse, tests, and final diffs before completion. Use when implementing or reviewing a feature, refactor, migration, or architectural change. Do not use for trivial text-only edits.
---

# Aplomo review

Use the smallest amount of repository context needed for the task.

1. Prepare the request with the relevant modules, boundaries, and existing patterns.
2. Prefer an existing implementation or convention that can be extended.
3. Implement or review the smallest compatible change with focused tests.
4. Inspect the final diff and run the relevant validation.

When the Aplomo MCP server is available, call `aplomo_prepare_change` once before implementation and `aplomo_review_diff` once before completion. Use the more granular tools only when deeper analysis is needed. When MCP is not available, perform the same workflow with the agent's native repository search, file inspection, Git diff, and test tools.

Treat `.engineering/` as authoritative when the repository contains it. Do not edit generated agent adapters directly; update `.engineering/config.yaml` and run `aplomo install`.

Keep the workflow proportional. A typo or documentation correction does not require a full architecture review.
