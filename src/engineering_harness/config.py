"""The .engineering source-of-truth configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
import json


@dataclass
class HarnessConfig:
    version: int = 1
    project_name: str = "project"
    agents: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    integrations: Dict[str, bool] = field(default_factory=lambda: {"hooks": True, "mcp": True, "skills": True})
    context: Dict[str, int] = field(default_factory=lambda: {"max_files": 80, "max_chars": 200_000, "max_matches": 12})

    @classmethod
    def load(cls, root: Path) -> "HarnessConfig":
        path = root / ".engineering" / "config.yaml"
        if not path.exists():
            raise FileNotFoundError("Missing .engineering/config.yaml; run 'aplomo init' first.")
        data = _parse_simple_yaml(path.read_text(encoding="utf-8"))
        return cls(
            version=int(data.get("version", 1)),
            project_name=str(data.get("project_name", root.name)),
            agents=list(data.get("agents", [])),
            technologies=list(data.get("technologies", [])),
            integrations=dict(data.get("integrations", {"hooks": True, "mcp": True, "skills": True})),
            context={key: int(value) for key, value in data.get("context", {"max_files": 80, "max_chars": 200_000, "max_matches": 12}).items()},
        )

    def dump(self) -> str:
        def quoted(values: List[str]) -> str:
            return "[" + ", ".join(json.dumps(value) for value in values) + "]"
        lines = [
            "# Source of truth for generated agent integrations.",
            f"version: {self.version}",
            f"project_name: {json.dumps(self.project_name)}",
            f"agents: {quoted(self.agents)}",
            f"technologies: {quoted(self.technologies)}",
            "integrations:",
        ]
        lines.extend(f"  {key}: {'true' if value else 'false'}" for key, value in self.integrations.items())
        lines.append("context:")
        lines.extend(f"  {key}: {value}" for key, value in self.context.items())
        return "\n".join(lines) + "\n"


def _parse_simple_yaml(text: str):
    result = {}
    section = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  ") and section:
            key, value = line.strip().split(":", 1)
            nested = value.strip()
            if nested.lower() in {"true", "false"}:
                parsed = nested.lower() == "true"
            else:
                parsed = int(nested) if nested.isdigit() else nested
            result.setdefault(section, {})[key] = parsed
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if not value:
            section = key
            result[key] = {}
        elif value.startswith("["):
            result[key] = json.loads(value)
            section = None
        elif value.startswith('"'):
            result[key] = json.loads(value)
            section = None
        else:
            result[key] = int(value) if value.isdigit() else value
            section = None
    return result
