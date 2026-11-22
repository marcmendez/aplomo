# Use Aplomo with Claude Code

Run the [setup command](../README.md#install) from the repository root. Open the repository in Claude Code and describe the change.

> Add an audit trail to account updates.

The installer adds the skill at `.claude/skills/aplomo-review/`. The entry in `CLAUDE.md` tells Claude Code when to load it. To request the skill directly, type `/aplomo-review`.

Add `--agents claude` to `aplomo init` to select Claude Code explicitly. If you install by copying the [skill folder](../skills/aplomo-review/) into `.claude/skills/`, use `/aplomo-review` to request a review. [Claude Code skills](https://code.claude.com/docs/en/skills)

If you enable the [optional MCP adapter](../README.md#optional-mcp-and-hooks), Claude Code may ask you to approve the server.
