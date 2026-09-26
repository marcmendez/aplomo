# Use Aplomo with Cursor

## Local installation

Install the Aplomo CLI once, then initialize the repository:

```bash
uv tool install git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init --agents cursor
```

Reopen the project in Cursor. Open **Settings → Tools & MCP** and confirm that `aplomo` is enabled.

## Use

Write normal requests in Cursor Agent. You do not need to mention Aplomo:

```text
Add pagination to the users endpoint and update its tests.
```

The always-on rule in `.cursor/rules/aplomo.mdc` gives Cursor the repository workflow. The MCP definition in `.cursor/mcp.json` makes Aplomo's repository tools available, and `.cursor/hooks.json` records configured session, edit, and shell events.

To check the MCP connection explicitly, ask:

```text
Use aplomo_understand_repo and summarize the main modules.
```

## Generated files

```text
.cursor/
├── hooks.json
├── mcp.json
└── rules/
    └── aplomo.mdc
```

If one of these files already exists and is not owned by Aplomo, installation reports it as `skipped` instead of overwriting it. Merge the configurations manually if you need both.

## Cursor Cloud

Cloud Agents run in a separate VM and do not inherit a desktop installation or desktop MCP process.

Commit `.engineering/` and the generated `.cursor/` files. In the Cloud Agent environment setup, install Aplomo and recreate the machine-local launcher for that VM:

```bash
uv tool install git+https://github.com/marcmendez/aplomo.git
aplomo install
```

Then configure an stdio MCP server in the Cursor dashboard or Cloud Agent API:

```text
command: ./.engineering/aplomo-runtime
args:    mcp --root .
```

The stdio process runs inside the Cloud VM and reads its checkout. A local MCP entry on your laptop is not a substitute for this cloud-side setup. See Cursor's [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities) and [Cloud Agent API](https://prod.cursor.com/docs/cloud-agent/api/endpoints).
