import json
import tomllib
from pathlib import Path

from engineering_harness import __version__
from engineering_harness.mcp_server import TOOLS


ROOT = Path(__file__).resolve().parents[1]


def test_release_versions_are_synchronized():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    assert project["project"]["version"] == portable["version"] == codex["version"] == __version__


def test_plugin_assets_and_skill_are_packaged():
    portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    interface = portable["extensions"]["com.openai"]["interface"]
    assert (ROOT / interface["composerIcon"]).is_file()
    assert (ROOT / interface["logo"]).is_file()
    assert (ROOT / "skills/aplomo-review/SKILL.md").is_file()
    assert portable["license"] == "MIT"


def test_every_mcp_tool_is_declared_read_only():
    assert TOOLS
    for tool in TOOLS:
        assert tool["annotations"] == {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
            "idempotentHint": True,
        }
