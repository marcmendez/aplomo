<!-- aplomo:start -->
## Aplomo

The engineering source of truth is `.engineering/`. For non-trivial code changes:

1. Call `aplomo_prepare_change` once with the request and a focused search query.
2. Read `.engineering/patterns.md` from that result and prefer its canonical implementations.
3. Before adding a class, service, interface, or module, call `aplomo_validate_abstraction`. Reuse a candidate or record why the responsibility or lifecycle is materially different.
4. Keep the change inside the reported module boundaries and add focused tests.
5. Call `aplomo_review_diff` once before completion and resolve duplicate-abstraction warnings.

Respect the configured context budget. Widen a search deliberately only when the bounded result is insufficient. Keep this proportional: trivial documentation or formatting edits do not need the full workflow.

Do not edit generated agent integrations directly. Update `.engineering/config.yaml` and run `aplomo install`.
<!-- aplomo:end -->
