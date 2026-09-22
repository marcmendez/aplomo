"""Dependency-free MCP stdio server exposing repository engineering tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import sys

from .repository import find_existing_patterns, review_diff, review_plan, understand_repo


TOOLS = [
    {
        "name": "aplomo_understand_repo",
        "description": "Detect technologies and summarize modules and symbols in the repository.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "aplomo_find_existing_patterns",
        "description": "Search source code for existing implementations before adding an abstraction.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "aplomo_review_plan",
        "description": "Check whether an implementation plan covers patterns, scope, compatibility, and validation.",
        "inputSchema": {
            "type": "object", "properties": {"plan": {"type": "string"}}, "required": ["plan"], "additionalProperties": False
        },
    },
    {
        "name": "aplomo_review_architecture",
        "description": "Summarize architecture configuration and repository structure for an architecture review.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "aplomo_review_diff",
        "description": "Review the current git diff for risky size, secrets, and missing test changes.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def run(root: Path) -> None:
    root = root.resolve()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = dispatch(root, request)
        except Exception as exc:  # MCP must return structured errors, not crash the process.
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()


def dispatch(root: Path, request: Dict[str, Any]):
    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _result(request_id, {
            "protocolVersion": request.get("params", {}).get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "aplomo", "version": "0.1.0"},
            "instructions": "Understand the repository and search existing patterns before reviewing plans or diffs.",
        })
    if method == "tools/list":
        return _result(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = request.get("params", {})
        value = call_tool(root, params.get("name", ""), params.get("arguments", {}))
        return _result(request_id, {"content": [{"type": "text", "text": json.dumps(value, indent=2)}]})
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def call_tool(root: Path, name: str, arguments: Dict[str, Any]):
    # The engineering_* aliases keep pre-Aplomo generated skills working during migration.
    if name in {"aplomo_understand_repo", "engineering_understand_repo"}:
        return understand_repo(root)
    if name in {"aplomo_find_existing_patterns", "engineering_find_existing_patterns"}:
        return find_existing_patterns(root, str(arguments.get("query", "")), int(arguments.get("limit", 20)))
    if name in {"aplomo_review_plan", "engineering_review_plan"}:
        return review_plan(str(arguments.get("plan", "")))
    if name in {"aplomo_review_architecture", "engineering_review_architecture"}:
        architecture = root / ".engineering" / "architecture.yaml"
        return {
            "repository": understand_repo(root),
            "architecture": architecture.read_text(encoding="utf-8") if architecture.exists() else None,
        }
    if name in {"aplomo_review_diff", "engineering_review_diff"}:
        return review_diff(root)
    raise ValueError(f"Unknown tool: {name}")


def _result(request_id: Any, value: Any):
    return {"jsonrpc": "2.0", "id": request_id, "result": value}
