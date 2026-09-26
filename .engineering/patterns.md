# Aplomo pattern catalog

## Agent adapter generation

- Responsibility: translate `.engineering/config.yaml` into native Cursor, Codex, and Claude Code files.
- Canonical implementation: `src/engineering_harness/generators.py`
- Extend when: adding an agent surface, instruction, hook, skill, or MCP adapter.
- Create a new abstraction only when: generation requires a separate lifecycle or ownership model.
- Validation: `tests/test_cli.py` and `aplomo eval`.

## Bounded repository analysis

- Responsibility: map source files, find existing implementations, validate abstractions, and review diffs within an explicit read budget.
- Canonical implementation: `src/engineering_harness/repository.py`
- Extend when: adding repository-derived context or a new static validation.
- Create a new abstraction only when: analysis needs persistent state or a non-local data source.
- Validation: `tests/test_repository.py`.

## MCP tool surface

- Responsibility: expose read-only repository analysis over stdio MCP.
- Canonical implementation: `src/engineering_harness/mcp_server.py`
- Extend when: exposing another deterministic repository check.
- Create a new abstraction only when: a capability requires a different transport or trust boundary.
- Validation: MCP protocol tests in `tests/test_cli.py` and read-only annotation tests in `tests/test_plugin.py`.

## Machine-local runtime launcher

- Responsibility: start Aplomo reliably from desktop and cloud agents without depending on their inherited `PATH`.
- Canonical implementation: `src/engineering_harness/runtime.py`
- Extend when: supporting another operating system or runtime health check.
- Create a new abstraction only when: the target cannot execute the existing Python launcher contract.
- Validation: the `agent runtime launch` acceptance check and packaged-runtime CI job.
