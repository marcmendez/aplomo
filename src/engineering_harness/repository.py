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
DEFAULT_MAX_FILES = 80
DEFAULT_MAX_CHARS = 200_000


def source_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix in SOURCE_SUFFIXES and not any(part in IGNORED_DIRS for part in path.parts):
            yield path


def index_repository(
    root: Path,
    max_files: int = DEFAULT_MAX_FILES,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> Dict[str, Any]:
    files = list(source_files(root))
    symbols = 0
    modules = {str(path.parent.relative_to(root)) for path in files}
    languages: Dict[str, int] = {}
    for path in files:
        languages[path.suffix] = languages.get(path.suffix, 0) + 1
    chars_read = 0
    files_read = 0
    for path in files[:max_files]:
        remaining = max_chars - chars_read
        if remaining <= 0:
            break
        text = _read_bounded(path, remaining)
        chars_read += len(text)
        files_read += 1
        if path.suffix == ".py":
            try:
                tree = ast.parse(text)
                symbols += sum(isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
            except SyntaxError:
                pass
        else:
            symbols += len(re.findall(r"\b(?:class|function|interface|type|def|fn)\s+[A-Za-z_$][\w$]*", text))
    return {
        "files": len(files),
        "modules": len(modules),
        "symbols": symbols,
        "languages": languages,
        "read_summary": _read_summary(len(files), files_read, chars_read, max_files, max_chars),
    }


def understand_repo(
    root: Path,
    max_files: int = DEFAULT_MAX_FILES,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> Dict[str, Any]:
    profile = detect_repository(root)
    return {"profile": profile.to_dict(), "index": index_repository(root, max_files, max_chars)}


def find_existing_patterns(
    root: Path,
    query: str,
    limit: int = 20,
    max_files: int = DEFAULT_MAX_FILES,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> Dict[str, Any]:
    if not query.strip():
        return {"query": query, "matches": [], "read_summary": _read_summary(0, 0, 0, max_files, max_chars)}
    tokens = _query_tokens(query)
    matches: List[Dict[str, Any]] = []
    files = list(source_files(root))
    ranked = sorted(
        files,
        key=lambda path: (-sum(token in path.relative_to(root).as_posix().lower() for token in tokens), path.as_posix()),
    )
    files_read = 0
    chars_read = 0
    for path in ranked[:max_files]:
        relative = path.relative_to(root).as_posix()
        path_lower = relative.lower()
        file_matches = 0
        if any(token in path_lower for token in tokens):
            matches.append({"path": relative, "line": 1, "text": "filename match"})
            file_matches += 1
        remaining = max_chars - chars_read
        if remaining <= 0 or len(matches) >= limit:
            break
        text = _read_bounded(path, remaining)
        files_read += 1
        chars_read += len(text)
        for line_number, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            if any(token in lowered for token in tokens):
                matches.append({"path": relative, "line": line_number, "text": line.strip()[:240]})
                file_matches += 1
                if len(matches) >= limit or file_matches >= 3:
                    break
        if len(matches) >= limit:
            break
    if len(matches) >= limit:
        stop_reason = "match_limit"
    elif chars_read >= max_chars:
        stop_reason = "character_budget"
    elif files_read >= max_files and files_read < len(files):
        stop_reason = "file_budget"
    else:
        stop_reason = "complete"
    return {
        "query": query,
        "matches": matches[:limit],
        "read_summary": _read_summary(len(files), files_read, chars_read, max_files, max_chars, stop_reason),
    }


def validate_new_abstraction(
    root: Path,
    proposed_name: str,
    responsibility: str,
    justification: str = "",
    max_files: int = DEFAULT_MAX_FILES,
    max_chars: int = DEFAULT_MAX_CHARS,
    max_matches: int = 12,
) -> Dict[str, Any]:
    query = " ".join(part for part in (proposed_name, responsibility) if part.strip())
    patterns = find_existing_patterns(root, query, max_matches, max_files, max_chars)
    candidates = patterns["matches"]
    if not candidates:
        status = "pass"
        decision = "No matching implementation was found inside the configured read budget."
    elif not justification.strip():
        status = "needs_justification"
        decision = "Reuse or extend a candidate, or explain the materially different responsibility or lifecycle."
    else:
        status = "review_required"
        decision = "Candidates exist; review the justification against them before adding the abstraction."
    return {
        "status": status,
        "proposed_name": proposed_name,
        "responsibility": responsibility,
        "justification": justification,
        "candidates": candidates,
        "decision": decision,
        "read_summary": patterns["read_summary"],
    }


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


def review_diff(
    root: Path,
    max_files: int = DEFAULT_MAX_FILES,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> Dict[str, Any]:
    completed = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0", "HEAD"],
        cwd=str(root), text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        staged = subprocess.run(
            ["git", "diff", "--cached", "--no-ext-diff", "--unified=0"],
            cwd=str(root), text=True, capture_output=True, check=False,
        )
        unstaged = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--unified=0"],
            cwd=str(root), text=True, capture_output=True, check=False,
        )
        completed = subprocess.CompletedProcess(
            args=["git", "diff"],
            returncode=0 if staged.returncode == 0 and unstaged.returncode == 0 else 1,
            stdout=staged.stdout + unstaged.stdout,
            stderr=staged.stderr or unstaged.stderr,
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
    untracked_result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(root), text=True, capture_output=True, check=False,
    )
    untracked = untracked_result.stdout.splitlines() if untracked_result.returncode == 0 else []
    untracked_chars = 0
    for relative in untracked[:max_files]:
        text = _read_bounded(root / relative, max_chars - untracked_chars)
        additions.extend(text.splitlines())
        untracked_chars += len(text)
        if untracked_chars >= max_chars:
            break
    changed = list(dict.fromkeys([*changed, *untracked]))
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
    duplicate_abstractions, duplicate_reads = _find_duplicate_abstractions(
        root, diff, untracked, max_files, max_chars
    )
    for duplicate in duplicate_abstractions:
        warnings.append(
            f"Possible duplicate abstraction '{duplicate['name']}' added in {duplicate['added_in']}; "
            f"existing declaration in {duplicate['existing_in']}"
        )
    return {
        "status": "pass" if not warnings else "needs_attention",
        "files": changed,
        "untracked": untracked,
        "additions": len(additions),
        "duplicate_abstractions": duplicate_abstractions,
        "read_summary": duplicate_reads,
        "warnings": warnings,
    }


def _find_duplicate_abstractions(
    root: Path,
    diff: str,
    untracked: List[str],
    max_files: int,
    max_chars: int,
) -> tuple[List[Dict[str, str]], Dict[str, Any]]:
    declaration = re.compile(r"^\s*(?:export\s+)?(?:abstract\s+)?(?:class|interface|type)\s+([A-Za-z_$][\w$]*)")
    added: List[tuple[str, str]] = []
    current = ""
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif current and line.startswith("+") and not line.startswith("+++"):
            match = declaration.match(line[1:])
            if match:
                added.append((match.group(1), current))
    for relative in untracked:
        if Path(relative).suffix not in SOURCE_SUFFIXES:
            continue
        for line in _read_bounded(root / relative, max_chars).splitlines():
            match = declaration.match(line)
            if match:
                added.append((match.group(1), relative))

    files = list(source_files(root))
    files_read = 0
    chars_read = 0
    declarations: Dict[str, List[str]] = {}
    for path in files[:max_files]:
        remaining = max_chars - chars_read
        if remaining <= 0:
            break
        text = _read_bounded(path, remaining)
        files_read += 1
        chars_read += len(text)
        relative = path.relative_to(root).as_posix()
        if "test" in Path(relative).name.lower():
            continue
        for line in text.splitlines():
            match = declaration.match(line)
            if match:
                declarations.setdefault(match.group(1), []).append(relative)

    duplicates: List[Dict[str, str]] = []
    for name, added_in in dict.fromkeys(added):
        existing = next((path for path in declarations.get(name, []) if path != added_in), None)
        if existing:
            duplicates.append({"name": name, "added_in": added_in, "existing_in": existing})
    return duplicates, _read_summary(len(files), files_read, chars_read, max_files, max_chars)


def _query_tokens(query: str) -> List[str]:
    expanded = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", query)
    tokens = [token.lower() for token in re.findall(r"[A-Za-z_$][\w$]{2,}", expanded)]
    ignored = {"add", "new", "the", "and", "for", "with", "from", "into", "existing", "implementation"}
    useful = [token for token in tokens if token not in ignored]
    return useful or [query.strip().lower()]


def _read_bounded(path: Path, limit: int) -> str:
    if limit <= 0:
        return ""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as stream:
            return stream.read(limit)
    except OSError:
        return ""


def _read_summary(
    files_available: int,
    files_read: int,
    chars_read: int,
    max_files: int,
    max_chars: int,
    stop_reason: str | None = None,
) -> Dict[str, Any]:
    if stop_reason is None:
        if chars_read >= max_chars:
            stop_reason = "character_budget"
        elif files_read >= max_files and files_read < files_available:
            stop_reason = "file_budget"
        else:
            stop_reason = "complete"
    return {
        "files_available": files_available,
        "files_read": files_read,
        "chars_read": chars_read,
        "max_files": max_files,
        "max_chars": max_chars,
        "truncated": stop_reason != "complete",
        "stop_reason": stop_reason,
    }
