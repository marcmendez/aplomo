---
name: aplomo-review
description: Prepare and review non-trivial code changes against repository conventions.
---

# Aplomo review

Use this workflow for non-trivial code changes:

1. Call `aplomo_prepare_change` once with the user's request and a focused pattern query.
2. Prefer extending a matching implementation and respect the reported boundaries.
3. Implement the smallest compatible change and add focused tests.
4. Call `aplomo_review_diff` once before declaring completion.

The repository's `.engineering/` directory is authoritative. Agent-specific files are generated adapters. Keep the workflow proportional: trivial documentation or formatting edits do not need the full review.
