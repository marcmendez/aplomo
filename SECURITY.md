# Security Policy

## Supported versions

Security fixes are provided for the latest tagged release.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not open a public issue for an unpatched vulnerability.

Include the affected version, operating system, agent, reproduction steps, impact, and any suggested mitigation. Please avoid including real credentials or private repository content.

## Security model

- Aplomo runs locally and has the same filesystem visibility as the coding agent that launches it.
- All current MCP tools are read-only and declare read-only, closed-world, non-destructive annotations.
- Generated hooks record normalized lifecycle metadata locally; they do not transmit it.
- Existing unowned agent configuration is preserved instead of overwritten.
- Agent and hook trust prompts must be reviewed by the user.
