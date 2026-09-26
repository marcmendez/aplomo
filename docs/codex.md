# Use Aplomo with Codex

## Install

Install the Aplomo CLI once, then initialize the repository:

```bash
uv tool install git+https://github.com/marcmendez/aplomo.git
cd your-repository
aplomo init --agents codex
```

Open a new Codex task from the repository and trust the project if Codex asks. Project-level MCP configuration is loaded only for trusted projects.

## Use

Send normal requests to Codex. Aplomo does not require a prefix:

```text
Extract the payment retry logic without duplicating the existing service pattern.
```

Codex reads the managed Aplomo section in `AGENTS.md`. `.codex/config.toml` starts the Aplomo MCP server for the project, `.codex/hooks.json` records configured lifecycle events, and `.agents/skills/aplomo-review/SKILL.md` provides the review workflow. For a non-trivial request, the normal path is one `aplomo_prepare_change` preflight and one `aplomo_review_diff` call before completion.

To check the MCP connection explicitly, ask:

```text
Use aplomo_understand_repo, then aplomo_review_architecture.
```

## Generated files

```text
.
├── .agents/skills/aplomo-review/SKILL.md
├── .codex/
│   ├── config.toml
│   └── hooks.json
└── AGENTS.md
```

Aplomo only manages the section between `<!-- aplomo:start -->` and `<!-- aplomo:end -->` in `AGENTS.md`. Other repository instructions remain untouched.
