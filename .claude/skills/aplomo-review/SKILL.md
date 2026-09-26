---
name: aplomo-review
description: Prepare and review non-trivial code changes against repository conventions.
---

# Aplomo review

Use this workflow for non-trivial code changes:

1. Call `aplomo_prepare_change` once with the user's request and a focused pattern query.
2. Prefer the canonical patterns in `.engineering/patterns.md` and respect the reported boundaries.
3. Before adding a class, service, interface, or module, call `aplomo_validate_abstraction`; reuse a candidate or justify a materially different responsibility or lifecycle.
4. Implement the smallest compatible change and add focused tests without exceeding the context budget unless a wider read is necessary.
5. Call `aplomo_review_diff` once before declaring completion and resolve duplicate-abstraction warnings.

The repository's `.engineering/` directory is authoritative. Agent-specific files are generated adapters. Keep the workflow proportional: trivial documentation or formatting edits do not need the full review.
