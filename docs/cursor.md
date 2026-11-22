# Use Aplomo with Cursor

Run the [setup command](../README.md#install) from the repository root. Reopen the repository in Cursor and describe the change in Agent chat.

> Add pagination to the users endpoint.

The installer adds the skill at `.cursor/skills/aplomo-review/` and a project rule that tells Cursor when to load it. To request the skill directly, select `aplomo-review` from the `/` menu.

Add `--agents cursor` to `aplomo init` to select Cursor explicitly. If you install by copying the [skill folder](../skills/aplomo-review/) into `.cursor/skills/`, use the menu to request a review. [Cursor skills](https://cursor.com/docs/skills)

## Cursor Cloud

Commit the skill folder, project rule, and any guidance in `.engineering/`. Start the cloud task from a branch that contains those files. Install the CLI in the Cloud Agent environment if you also want the local analysis commands.

For the [optional MCP adapter](../README.md#optional-mcp-and-hooks), run `aplomo install` in the VM to regenerate the launcher. Configure the Cloud Agent to run `./.engineering/aplomo-runtime` with arguments `mcp --root .`. [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities)
