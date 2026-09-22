<!-- aplomo:start -->
## Aplomo

The engineering source of truth is `.engineering/`. Before adding an abstraction:

1. Search the repository for an existing equivalent.
2. Understand the relevant module boundaries.
3. Explain why extending the existing pattern is insufficient.
4. Review the plan and final diff with the `aplomo` MCP tools when available.

Do not edit generated agent integrations directly. Update `.engineering/config.yaml` and run `aplomo install`.
<!-- aplomo:end -->
