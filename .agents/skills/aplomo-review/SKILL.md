---
name: aplomo-review
description: Review plans, architecture choices, and diffs against repository conventions.
---

# Aplomo review

Use this workflow before introducing a new abstraction or completing a non-trivial change:

1. Call `aplomo_understand_repo`.
2. Call `aplomo_find_existing_patterns` for the concept being introduced.
3. Call `aplomo_review_plan` before implementation.
4. Call `aplomo_review_diff` before declaring completion.

The repository's `.engineering/` directory is authoritative. Agent-specific files are generated adapters.
