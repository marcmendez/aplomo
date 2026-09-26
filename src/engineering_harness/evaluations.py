"""Deterministic acceptance checks users can run without external agent accounts."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Dict, List
import json
import subprocess
import tomllib

from .config import HarnessConfig
from .events import EventNormalizer, EventType
from .generators import install_integrations
from .mcp_server import dispatch
from .runtime import LAUNCHER, launcher_command, mcp_smoke_test


def run_evaluations() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    cases: list[tuple[str, Callable[[], str]]] = [
        ("event normalization", _evaluate_events),
        ("native agent configurations", _evaluate_agent_configs),
        ("safe installation", _evaluate_safe_installation),
        ("idempotent regeneration", _evaluate_idempotency),
        ("MCP protocol contract", _evaluate_mcp),
        ("agent runtime launch", _evaluate_runtime_launch),
    ]
    for name, evaluate in cases:
        try:
            detail = evaluate()
            checks.append({"name": name, "ok": True, "detail": detail})
        except (AssertionError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            checks.append({"name": name, "ok": False, "detail": str(exc) or exc.__class__.__name__})
    passed = sum(bool(check["ok"]) for check in checks)
    return {"ok": passed == len(checks), "passed": passed, "total": len(checks), "checks": checks}


def _evaluate_events() -> str:
    normalizer = EventNormalizer()
    fixtures = [
        ("cursor", {"hook_event_name": "afterFileEdit", "file_path": "src/a.py"}),
        ("claude", {"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": "src/a.py"}}),
        ("codex", {"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": "src/a.py"}}),
    ]
    for source, payload in fixtures:
        assert normalizer.normalize(source, payload).event is EventType.FILE_WRITE, f"{source} write was not normalized"
    unknown = {"event": "future.event", "value": 42}
    assert normalizer.normalize("future", unknown).payload == unknown, "unknown payload was not preserved"
    return "3 agents + lossless unknown events"


def _evaluate_agent_configs() -> str:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / ".engineering").mkdir()
        config = HarnessConfig(project_name="eval", agents=["cursor", "claude", "codex"])
        install_integrations(root, config)
        cursor = json.loads((root / ".cursor/mcp.json").read_text(encoding="utf-8"))
        claude = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
        codex = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
        assert cursor["mcpServers"]["aplomo"]["command"] == launcher_command()
        assert claude["mcpServers"]["aplomo"]["command"] == launcher_command()
        assert codex["mcp_servers"]["aplomo"]["command"] == launcher_command()
        assert (root / LAUNCHER).exists()
        assert (root / ".cursor/rules/aplomo.mdc").exists()
        assert (root / ".claude/skills/aplomo-review/SKILL.md").exists()
        assert (root / ".agents/skills/aplomo-review/SKILL.md").exists()
    return "Cursor, Claude Code, and Codex parse successfully"


def _evaluate_safe_installation() -> str:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        path = root / ".cursor/hooks.json"
        path.parent.mkdir(parents=True)
        path.write_text('{"owned_by":"user"}\n', encoding="utf-8")
        (root / ".engineering").mkdir()
        statuses = install_integrations(root, HarnessConfig(project_name="eval", agents=["cursor"]))
        assert "skipped" in statuses[".cursor/hooks.json"]
        assert path.read_text(encoding="utf-8") == '{"owned_by":"user"}\n'
    return "unmanaged configuration preserved"


def _evaluate_idempotency() -> str:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / ".engineering").mkdir()
        config = HarnessConfig(project_name="eval", agents=["cursor", "claude", "codex"])
        install_integrations(root, config)
        first = {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}
        install_integrations(root, config)
        second = {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}
        assert first == second, "second installation changed generated output"
        assert (root / "AGENTS.md").read_text(encoding="utf-8").count("<!-- aplomo:start -->") == 1
    return "second installation is byte-for-byte stable"


def _evaluate_mcp() -> str:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        initialized = dispatch(root, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        assert initialized["result"]["serverInfo"]["name"] == "aplomo"
        listed = dispatch(root, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = {tool["name"] for tool in listed["result"]["tools"]}
        assert {"aplomo_prepare_change", "aplomo_understand_repo", "aplomo_find_existing_patterns", "aplomo_review_plan", "aplomo_review_diff"} <= names
        called = dispatch(root, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "aplomo_review_plan", "arguments": {"plan": "Search existing patterns, change one module compatibly, and run tests."}}})
        assert json.loads(called["result"]["content"][0]["text"])["status"] == "pass"
    return "initialize, list, and call succeed"


def _evaluate_runtime_launch() -> str:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / ".engineering").mkdir()
        install_integrations(root, HarnessConfig(project_name="eval", agents=["codex"]))
        result = mcp_smoke_test(root)
        assert result["ok"], result["detail"]
        hook = subprocess.run(
            [str(root / LAUNCHER), "hook", "--source", "codex", "--root", str(root)],
            cwd=str(root),
            input=json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": "src/a.py"}}),
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        assert hook.returncode == 0, hook.stderr.strip() or f"hook exited {hook.returncode}"
        event = json.loads((root / ".engineering/events.jsonl").read_text(encoding="utf-8"))
        assert event["event"] == "FILE_WRITE"
        assert event["path"] == "src/a.py"
    return "generated launcher starts MCP and records a hook event"
