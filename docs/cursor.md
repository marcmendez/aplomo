# Use Aplomo with Cursor

Run the [one-time setup](../README.md#install) from your project root, then reopen the project in Cursor. Describe the change in Agent chat:

> Add pagination to the users endpoint.

Aplomo installs the skill at `.cursor/skills/aplomo-review/` and adds a project rule that tells Cursor when to use it. You can also select `aplomo-review` from the `/` menu for an explicit review. To select Cursor explicitly on first setup, append `--agents cursor`. For a manual installation, copy the [standalone skill folder](../skills/aplomo-review/) to the project skill directory. [Cursor skills](https://cursor.com/docs/skills)

## Cursor Cloud

Commit the project skill, rule, and `.engineering/` settings so they are available in the cloud checkout. If you want the local analysis commands, install the CLI in the Cloud Agent environment.

For an [optional stdio MCP integration](../README.md#optional-mcp-and-hooks), run `aplomo install` in the VM to regenerate its launcher, then configure the server for the Cloud Agent using `./.engineering/aplomo-runtime` with arguments `mcp --root .`. [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities)
