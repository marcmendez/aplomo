# Use Aplomo with Claude Code

Install the CLI from the [quick start](../README.md#install), then run this from your repository:

```bash
aplomo init
```

Open the project in Claude Code and invoke the skill:

```text
/aplomo-review Add an audit trail to account updates using the existing event pattern.
```

Aplomo installs the skill at `.claude/skills/aplomo-review/` and adds a short section to `CLAUDE.md` for non-trivial work. To select Claude Code explicitly on first setup, pass `--agents claude`. For a manual installation, copy the [standalone skill folder](../skills/aplomo-review/) to that directory and invoke it explicitly.

Claude Code can use native tools and the local Aplomo CLI. If you enable the [optional MCP adapter](../README.md#optional-mcp-and-hooks), review and approve the server if prompted. [Claude Code skills](https://code.claude.com/docs/en/skills)
