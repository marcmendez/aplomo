"""Dependency-free MCP stdio server exposing repository engineering tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import sys

from . import __version__
from .config import context_budget
from .repository import (
    find_existing_patterns, prepare_change, read_metadata, review_diff, review_plan,
    understand_repo, validate_new_abstraction,
)


TOOLS = [
    {
        "name": "aplomo_prepare_change",
        "description": "Prepare one coding request with repository structure, relevant existing patterns, and architecture rules in a single call.",
        "inputSchema": {
            "type": "object",
            "properties": {"request": {"type": "string"}, "query": {"type": "string"}},
            "required": ["request"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
    },
    {
        "name": "aplomo_understand_repo",
        "description": "Detect technologies and summarize modules and symbols in the repository.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
    },
    {
        "name": "aplomo_find_existing_patterns",
        "description": "Search a bounded set of source files for existing implementations before adding an abstraction.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
    },
    {
        "name": "aplomo_validate_abstraction",
        "description": "Require reuse or an explicit responsibility/lifecycle justification before adding an abstraction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "proposed_name": {"type": "string"},
                "responsibility": {"type": "string"},
                "justification": {"type": "string"},
            },
            "required": ["proposed_name", "responsibility"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
    },
    {
        "name": "aplomo_review_plan",
        "description": "Check whether an implementation plan covers patterns, scope, compatibility, and validation.",
        "inputSchema": {
            "type": "object", "properties": {"plan": {"type": "string"}}, "required": ["plan"], "additionalProperties": False
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
    },
    {
        "name": "aplomo_review_architecture",
        "description": "Summarize architecture configuration and repository structure for an architecture review.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
    },
    {
        "name": "aplomo_review_diff",
        "description": "Review the current git diff for risky size, secrets, and missing test changes.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False, "idempotentHint": True},
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
            "serverInfo": {"name": "aplomo", "version": __version__},
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
    if name == "aplomo_prepare_change":
        return prepare_change(root, str(arguments.get("request", "")), str(arguments.get("query", "")))
    if name in {"aplomo_understand_repo", "engineering_understand_repo"}:
        budget = context_budget(root)
        return understand_repo(root, budget["max_files"], budget["max_chars"])
    if name in {"aplomo_find_existing_patterns", "engineering_find_existing_patterns"}:
        budget = context_budget(root)
        limit = min(int(arguments.get("limit", budget["max_matches"])), budget["max_matches"])
        return find_existing_patterns(
            root, str(arguments.get("query", "")), limit, budget["max_files"], budget["max_chars"]
        )
    if name == "aplomo_validate_abstraction":
        budget = context_budget(root)
        return validate_new_abstraction(
            root,
            str(arguments.get("proposed_name", "")),
            str(arguments.get("responsibility", "")),
            str(arguments.get("justification", "")),
            budget["max_files"],
            budget["max_chars"],
            budget["max_matches"],
        )
    if name in {"aplomo_review_plan", "engineering_review_plan"}:
        return review_plan(str(arguments.get("plan", "")))
    if name in {"aplomo_review_architecture", "engineering_review_architecture"}:
        architecture = root / ".engineering" / "architecture.yaml"
        return {
            "repository": understand_repo(root),
            "architecture": read_metadata(architecture, 20_000),
        }
    if name in {"aplomo_review_diff", "engineering_review_diff"}:
        budget = context_budget(root)
        return review_diff(root, budget["max_files"], budget["max_chars"])
    raise ValueError(f"Unknown tool: {name}")


def _result(request_id: Any, value: Any):
    return {"jsonrpc": "2.0", "id": request_id, "result": value}
