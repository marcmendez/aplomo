# Use Aplomo with Claude Code

Run the [one-time setup](../README.md#install) from your project root. Then open the project in Claude Code and make a normal request:

> Add an audit trail to account updates.

Aplomo installs the skill at `.claude/skills/aplomo-review/` and adds instructions to `CLAUDE.md` so Claude Code knows when to use it. You can also type `/aplomo-review` for an explicit review. To select Claude Code explicitly on first setup, append `--agents claude`. For a manual installation, copy the [standalone skill folder](../skills/aplomo-review/) to the project skill directory.

Claude Code can use native tools and the local Aplomo CLI. If you enable the [optional MCP adapter](../README.md#optional-mcp-and-hooks), review and approve the server if prompted. [Claude Code skills](https://code.claude.com/docs/en/skills)
