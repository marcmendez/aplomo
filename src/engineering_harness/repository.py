"""Small, deterministic repository-analysis primitives used by CLI and MCP."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List
import ast
import re
import subprocess

from .detection import detect_repository


IGNORED_DIRS = {".git", ".engineering", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php"}


def source_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in SOURCE_SUFFIXES and not any(part in IGNORED_DIRS for part in path.parts):
            yield path


def index_repository(root: Path) -> Dict[str, Any]:
    files = list(source_files(root))
    symbols = 0
    modules = set()
    languages: Dict[str, int] = {}
    for path in files:
        modules.add(str(path.parent.relative_to(root)))
        languages[path.suffix] = languages.get(path.suffix, 0) + 1
        if path.suffix == ".py":
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
                symbols += sum(isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
            except (OSError, SyntaxError, UnicodeDecodeError):
                pass
        else:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                symbols += len(re.findall(r"\b(?:class|function|interface|type|def|fn)\s+[A-Za-z_$][\w$]*", text))
            except OSError:
                pass
    return {"files": len(files), "modules": len(modules), "symbols": symbols, "languages": languages}


def understand_repo(root: Path) -> Dict[str, Any]:
    profile = detect_repository(root)
    return {"profile": profile.to_dict(), "index": index_repository(root)}


def find_existing_patterns(root: Path, query: str, limit: int = 20) -> Dict[str, Any]:
    if not query.strip():
        return {"query": query, "matches": []}
    needle = query.lower()
    matches: List[Dict[str, Any]] = []
    for path in source_files(root):
        relative = path.relative_to(root).as_posix()
        if needle in path.name.lower():
            matches.append({"path": relative, "line": 1, "text": "filename match"})
        try:
            for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if needle in line.lower():
                    matches.append({"path": relative, "line": line_number, "text": line.strip()[:240]})
                    if len(matches) >= limit:
                        return {"query": query, "matches": matches}
        except OSError:
            continue
    return {"query": query, "matches": matches[:limit]}


def review_plan(plan: str) -> Dict[str, Any]:
    lowered = plan.lower()
    checks = {
        "tests": any(word in lowered for word in ("test", "prueba", "verify", "validar")),
        "existing_patterns": any(word in lowered for word in ("existing", "existente", "pattern", "patrón", "search", "buscar")),
        "rollback_or_compatibility": any(word in lowered for word in ("rollback", "compatib", "migration", "migración")),
        "scope": any(word in lowered for word in ("file", "module", "archivo", "módulo", "component")),
    }
    missing = [name for name, present in checks.items() if not present]
    return {"status": "pass" if not missing else "needs_attention", "checks": checks, "missing": missing}


def review_diff(root: Path) -> Dict[str, Any]:
    completed = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0"],
        cwd=str(root), text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        error_lines = completed.stderr.strip().splitlines()
        return {
            "status": "unavailable",
            "files": [],
            "additions": 0,
            "warnings": [error_lines[0] if error_lines else "Git diff is unavailable"],
        }
    diff = completed.stdout
    changed = re.findall(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)
    additions = [line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
    warnings = []
    secret_pattern = re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]+")
    if any(secret_pattern.search(line) for line in additions):
        warnings.append("Possible secret introduced in added lines")
    if len(additions) > 500:
        warnings.append("Large diff: more than 500 added lines")
    code_changed = any(Path(path).suffix in SOURCE_SUFFIXES for path in changed)
    tests_changed = any("test" in Path(path).name.lower() for path in changed)
    if code_changed and not tests_changed:
        warnings.append("Code changed without an accompanying test change")
    return {"status": "pass" if not warnings else "needs_attention", "files": changed, "additions": len(additions), "warnings": warnings}
