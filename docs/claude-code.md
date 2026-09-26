# Use Aplomo with Claude Code

## Install

Install the Aplomo CLI once, then initialize the repository:

```bash
uv tool install git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init --agents claude
```

Start a new Claude Code session from the repository root. Review and approve the project MCP server if Claude Code asks for confirmation.

## Use

Send normal requests to Claude Code. Aplomo does not require a prefix:

```text
Add an audit trail to account updates and follow the repository's existing pattern.
```

Claude Code reads the managed section in `CLAUDE.md`. `.mcp.json` exposes the Aplomo MCP server, `.claude/skills/aplomo-review/SKILL.md` provides the review workflow, and `.claude/settings.json` records configured lifecycle events. For a non-trivial request, the normal path is one `aplomo_prepare_change` preflight and one `aplomo_review_diff` call before completion.

To check the MCP connection explicitly, ask:

```text
Use aplomo_find_existing_patterns to find the current configuration pattern.
```

## Generated files

```text
.
├── .claude/
│   ├── settings.json
│   └── skills/aplomo-review/SKILL.md
├── .mcp.json
└── CLAUDE.md
```

Aplomo only manages the section between `<!-- aplomo:start -->` and `<!-- aplomo:end -->` in `CLAUDE.md`. If `.mcp.json` or `.claude/settings.json` already exists and is not owned by Aplomo, installation reports it as `skipped` instead of overwriting it.
