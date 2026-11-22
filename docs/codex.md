# Use Aplomo with Codex

Install the CLI from the [quick start](../README.md#install), then run this from your repository:

```bash
aplomo init
```

Open the project in Codex. Select `aplomo-review` from the `$` menu or name it in your request:

```text
$aplomo-review Add invoice retries using the existing retry policy. Test the retry limit.
```

Aplomo installs the skill at `.agents/skills/aplomo-review/` and adds a short section to `AGENTS.md` for non-trivial work. If Codex is missing from the detected assistants, use `aplomo init --agents codex` on first setup. For a manual installation, copy the [standalone skill folder](../skills/aplomo-review/) to that directory and invoke it explicitly.

The skill runs with native Codex tools and can call the local Aplomo CLI when available. If you enable the [optional MCP adapter](../README.md#optional-mcp-and-hooks), Codex loads its project configuration in trusted projects. [Codex skills](https://learn.chatgpt.com/docs/build-skills)

## Codex Cloud

Commit the project skill folder and your repository guidance, then start the cloud task from a checkout that includes them. Ask Codex to use `aplomo-review` with the task. The same `aplomo init` command can prepare a repository in a cloud task if the CLI is available there. For recurring tasks that need the optional local checks, install the CLI in the shared cloud environment. [Codex Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
