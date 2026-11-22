# Use Aplomo with Codex

Run the [one-time setup](../README.md#install) from your project root. Then open the project in Codex and make a normal request:

> Add filtering to the projects list.

Aplomo installs the skill at `.agents/skills/aplomo-review/` and adds instructions to `AGENTS.md` so Codex knows when to use it. For an explicit review, you can also type `$aplomo-review`. On first setup, append `--agents codex` if you want to select Codex regardless of detection. For a manual installation, copy the [standalone skill folder](../skills/aplomo-review/) to the project skill directory.

The skill runs with native Codex tools and can call the local Aplomo CLI when available. If you enable the [optional MCP adapter](../README.md#optional-mcp-and-hooks), Codex loads its project configuration in trusted projects. [Codex skills](https://learn.chatgpt.com/docs/build-skills)

## Codex Cloud

Commit the skill folder, `AGENTS.md`, and project guidance, then start a cloud task from a checkout that includes them. Codex can use those files with a normal request. Install the optional CLI in the cloud environment if you want the local analysis commands there. [Codex Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments)
