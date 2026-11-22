# Use Aplomo with Codex

Install the CLI from the [quick start](../README.md#install), then run this from your repository:

```bash
aplomo init --agents codex
```

Open the project in Codex. Select `aplomo-review` from the `$` menu or name it in your request:

```text
$aplomo-review Add invoice retries using the existing retry policy. Test the retry limit.
```

Aplomo installs the skill at `.agents/skills/aplomo-review/SKILL.md` and adds a short section to `AGENTS.md` for non-trivial work. For a manual installation, copy the [standalone SKILL.md](../skills/aplomo-review/SKILL.md) to that skill path and invoke it explicitly.

The skill runs with native Codex tools and can call the local Aplomo CLI when available. If you enable the [optional MCP adapter](../README.md#optional-mcp-and-hooks), Codex loads its project configuration in trusted projects. [Codex skills](https://learn.chatgpt.com/docs/build-skills)
