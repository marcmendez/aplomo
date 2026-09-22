"""Repository technology and coding-agent detection."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import shutil


@dataclass(frozen=True)
class RepositoryProfile:
    root: str
    technologies: List[str]
    agents: Dict[str, bool]
    is_git: bool

    def to_dict(self):
        return asdict(self)


TECH_MARKERS = {
    "Python": ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile"),
    "Node.js": ("package.json",),
    "TypeScript": ("tsconfig.json",),
    "Go": ("go.mod",),
    "Rust": ("Cargo.toml",),
    "Java": ("pom.xml", "build.gradle", "build.gradle.kts"),
    "Ruby": ("Gemfile",),
    "PHP": ("composer.json",),
    "Docker": ("Dockerfile", "docker-compose.yml", "compose.yaml"),
}

FRAMEWORK_MARKERS = {
    "FastAPI": ("fastapi",),
    "Django": ("django",),
    "Flask": ("flask",),
    "React": ('"react"',),
    "Next.js": ('"next"',),
    "Vue": ('"vue"',),
    "PostgreSQL": ("postgresql", "psycopg", "pg8000"),
}

AGENT_MARKERS = {
    "cursor": (".cursor",),
    "claude": (".claude", "CLAUDE.md"),
    "codex": (".codex", "AGENTS.md"),
}


def detect_repository(root: Path) -> RepositoryProfile:
    root = root.resolve()
    technologies = [name for name, markers in TECH_MARKERS.items() if any((root / marker).exists() for marker in markers)]
    searchable = []
    for filename in ("pyproject.toml", "requirements.txt", "package.json", "compose.yaml", "docker-compose.yml"):
        path = root / filename
        if path.is_file() and path.stat().st_size < 2_000_000:
            searchable.append(path.read_text(encoding="utf-8", errors="ignore").lower())
    combined = "\n".join(searchable)
    technologies.extend(name for name, needles in FRAMEWORK_MARKERS.items() if any(needle.lower() in combined for needle in needles))
    agents = {
        name: any((root / marker).exists() for marker in markers) or shutil.which(name) is not None
        for name, markers in AGENT_MARKERS.items()
    }
    return RepositoryProfile(str(root), list(dict.fromkeys(technologies)) or ["Unknown"], agents, (root / ".git").exists())
