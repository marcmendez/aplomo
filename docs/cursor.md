# Use Aplomo with Cursor

Install the CLI from the [quick start](../README.md#install), then run this from your repository:

```bash
aplomo init --agents cursor
```

Reopen the project in Cursor. In Agent chat, type `/` and select `aplomo-review`. Then describe the change:

> Add pagination to the users endpoint. Reuse the existing pagination pattern and update its tests.

Aplomo installs the skill at `.cursor/skills/aplomo-review/SKILL.md` and adds a short project rule for non-trivial work. For a manual installation, copy the [standalone SKILL.md](../skills/aplomo-review/SKILL.md) to that skill path and invoke it explicitly. [Cursor skills](https://cursor.com/docs/skills)

## Cursor Cloud

Commit the project skill, rule, and `.engineering/` settings so they are available in the cloud checkout. If you want the local analysis commands, install the CLI in the Cloud Agent environment.

For an [optional stdio MCP integration](../README.md#optional-mcp-and-hooks), run `aplomo install` in the VM to regenerate its launcher, then configure the server for the Cloud Agent using `./.engineering/aplomo-runtime` with arguments `mcp --root .`. [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities)
