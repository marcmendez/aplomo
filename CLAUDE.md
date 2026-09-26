<!-- aplomo:start -->
## Aplomo

Treat `.engineering/` as the repository's engineering source of truth. For a non-trivial code change, call `aplomo_prepare_change` once before implementation and `aplomo_review_diff` once before completion. Prefer existing patterns, respect the reported boundaries, and add focused tests. Keep the workflow proportional; trivial documentation or formatting edits do not need it. Edit `.engineering/config.yaml` and run `aplomo install` instead of editing generated integrations.
<!-- aplomo:end -->
