# Use Aplomo with Codex

Run the [setup command](../README.md#install) from the repository root. Open the repository in Codex and describe the change.

> Add filtering to the projects list.

The installer adds the skill at `.agents/skills/aplomo-review/`. The entry in `AGENTS.md` tells Codex to load it for features, substantial refactors, shared contract changes, and code reviews. To request the skill directly, type `$aplomo-review`.

Add `--agents codex` to `aplomo init` to select Codex explicitly. If you install by copying the [skill folder](../skills/aplomo-review/) into `.agents/skills/`, use `$aplomo-review` to request a review. [Codex skills](https://learn.chatgpt.com/docs/build-skills)

Codex loads the [optional MCP adapter](../README.md#optional-mcp-and-hooks) from trusted project configuration.

## Codex Cloud

Commit the skill folder, `AGENTS.md`, and any guidance in `.engineering/`. Start the cloud task from a branch that contains those files. Install the CLI in the cloud environment if you also want the local analysis commands. [Codex Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
