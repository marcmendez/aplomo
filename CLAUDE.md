<!-- aplomo:start -->
## Aplomo

Treat `.engineering/` as the repository's engineering source of truth. For a non-trivial code change, call `aplomo_prepare_change` once before implementation. Prefer the canonical patterns in `.engineering/patterns.md`; before adding a class, service, interface, or module, call `aplomo_validate_abstraction` and reuse a candidate or justify the different responsibility or lifecycle. Respect the context budget, reported boundaries, and add focused tests. Call `aplomo_review_diff` once before completion and resolve duplicate-abstraction warnings. Keep the workflow proportional; trivial documentation or formatting edits do not need it. Edit `.engineering/config.yaml` and run `aplomo install` instead of editing generated integrations.
<!-- aplomo:end -->
