# Changelog

All notable changes are documented here. Aplomo follows Semantic Versioning.

## Unreleased

- Install the shared review skill by default for Cursor, Codex, and Claude Code. MCP and lifecycle hooks are opt-in.
- Expose the same repository analysis through local `prepare`, `validate-abstraction`, and `review-diff` commands.
- Remove unchanged optional adapters owned by Aplomo when they are disabled and preserve customized files for manual migration.
- Report inconclusive searches when a read limit is reached without a reuse candidate.
- Bound and report untracked diff reads, and reuse that content to detect duplicate declarations.
- Skip symlinked files when reading repository source and metadata.

## 1.1.0 - 2026-09-26

- Add a repository-owned design-pattern catalog at `.engineering/patterns.md`.
- Add configurable file, character, and match budgets with consumption and truncation reporting.
- Add `aplomo_validate_abstraction` to require reuse or an explicit justification.
- Detect duplicate class, interface, and type declarations in tracked and untracked changes.
- Make reuse-before-create and read management the primary documented workflow.

## 1.0.0 - 2026-09-26

- Add a portable Agent Plugin manifest and reusable review skill.
- Replace PATH-dependent agent commands with a project-local pinned runtime launcher.
- Add a real subprocess MCP acceptance test and runtime health check.
- Combine repository, pattern, and architecture context into one proportional request preflight.
- Add read-only MCP tool annotations.
- Publish a reproducible paired Codex benchmark and its first honest baseline.
- Document the security, privacy, support, and release contracts.
- Support Cursor, Codex, and Claude Code project integrations.
