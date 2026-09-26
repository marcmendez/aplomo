"""Create and verify the project-local launcher used by GUI coding agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import os
import shlex
import subprocess
import sys


LAUNCHER = ".engineering/aplomo-runtime.cmd" if os.name == "nt" else ".engineering/aplomo-runtime"


def launcher_content() -> str:
    """Return a launcher pinned to the interpreter that installed Aplomo."""
    executable = str(Path(sys.executable).resolve())
    import_root = str(Path(__file__).resolve().parents[1])
    if os.name == "nt":
        return f'@echo off\r\nset "PYTHONPATH={import_root}"\r\n"{executable}" -m engineering_harness.cli %*\r\n'
    return (
        "#!/bin/sh\n"
        f"PYTHONPATH={shlex.quote(import_root)} exec {shlex.quote(executable)} "
        '-m engineering_harness.cli "$@"\n'
    )


def launcher_command() -> str:
    return f"./{LAUNCHER}"


def make_launcher_executable(path: Path) -> None:
    if os.name != "nt":
        path.chmod(path.stat().st_mode | 0o700)


def mcp_smoke_test(root: Path, timeout: float = 8.0) -> Dict[str, Any]:
    """Launch the generated runtime exactly as an agent does and exercise MCP."""
    launcher = root / LAUNCHER
    if not launcher.exists():
        return {"ok": False, "detail": f"missing {LAUNCHER}"}
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "aplomo_understand_repo", "arguments": {}},
        },
    ]
    try:
        completed = subprocess.run(
            [str(launcher), "mcp", "--root", str(root)],
            cwd=str(root),
            input="\n".join(json.dumps(request) for request in requests) + "\n",
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "detail": f"runtime launch failed: {exc}"}
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"runtime exited {completed.returncode}"
        return {"ok": False, "detail": detail.splitlines()[-1]}
    try:
        responses = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    except json.JSONDecodeError as exc:
        return {"ok": False, "detail": f"invalid MCP output: {exc}"}
    by_id = {response.get("id"): response for response in responses}
    if set(by_id) != {1, 2, 3} or any("error" in by_id[item] for item in (1, 2, 3)):
        return {"ok": False, "detail": "MCP initialize/list/call contract failed"}
    tools = {tool["name"] for tool in by_id[2]["result"]["tools"]}
    if "aplomo_understand_repo" not in tools:
        return {"ok": False, "detail": "MCP tool list is incomplete"}
    return {"ok": True, "detail": "launcher started MCP and completed initialize/list/call"}
