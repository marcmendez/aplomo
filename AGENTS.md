<!-- aplomo:start -->
## Aplomo

The engineering source of truth is `.engineering/`. For non-trivial code changes:

1. Call `aplomo_prepare_change` once with the request and a focused search query.
2. Prefer extending a matching implementation over adding another abstraction.
3. Keep the change inside the reported module boundaries and add focused tests.
4. Call `aplomo_review_diff` once before completion.

Keep this proportional: trivial documentation or formatting edits do not need the full workflow.

Do not edit generated agent integrations directly. Update `.engineering/config.yaml` and run `aplomo install`.
<!-- aplomo:end -->
