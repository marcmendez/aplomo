"""The Aplomo command-line interface."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Iterable, Optional
import json
import sys

from . import __version__
from .config import HarnessConfig
from .detection import detect_repository
from .events import EventNormalizer
from .evaluations import run_evaluations
from .generators import generated_files, install_integrations
from .mcp_server import run as run_mcp
from .repository import index_repository
from .runtime import mcp_smoke_test


ARCHITECTURE_TEMPLATE = """# Repository architecture model. Extend this file; generated integrations read it indirectly.
version: 1
layers: {}
rules:
  forbid_cycles: true
  require_tests_for_code_changes: true
  prefer_existing_patterns: true
"""


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="aplomo", description="One engineering standard across coding agents")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Analyze a repository and initialize .engineering")
    init.add_argument("--root", type=Path, default=Path.cwd())
    init.add_argument("--agents", nargs="*", choices=["cursor", "claude", "codex"])
    init.add_argument("--no-install", action="store_true")
    init.set_defaults(handler=command_init)

    install = subparsers.add_parser("install", help="Regenerate integrations from .engineering/config.yaml")
    install.add_argument("--root", type=Path, default=Path.cwd())
    install.set_defaults(handler=command_install)

    doctor = subparsers.add_parser("doctor", help="Validate core, configuration, integrations, and repository index")
    doctor.add_argument("--root", type=Path, default=Path.cwd())
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(handler=command_doctor)

    hook = subparsers.add_parser("hook", help="Normalize one agent hook payload from stdin")
    hook.add_argument("--source", required=True)
    hook.add_argument("--root", type=Path, default=Path.cwd())
    hook.add_argument("--dry-run", action="store_true")
    hook.set_defaults(handler=command_hook)

    evaluate = subparsers.add_parser("eval", help="Run Aplomo's deterministic acceptance checks")
    evaluate.add_argument("--json", action="store_true")
    evaluate.set_defaults(handler=command_eval)

    mcp = subparsers.add_parser("mcp", help="Run the Aplomo MCP server over stdio")
    mcp.add_argument("--root", type=Path, default=Path.cwd())
    mcp.set_defaults(handler=command_mcp)
    return parser


def command_init(args: Namespace) -> int:
    root = args.root.resolve()
    profile = detect_repository(root)
    selected = args.agents if args.agents is not None else [name for name, detected in profile.agents.items() if detected]
    config = HarnessConfig(project_name=root.name, agents=selected, technologies=profile.technologies)
    engineering = root / ".engineering"
    engineering.mkdir(parents=True, exist_ok=True)
    config_path = engineering / "config.yaml"
    if config_path.exists():
        print("Already initialized: .engineering/config.yaml exists", file=sys.stderr)
        return 2
    config_path.write_text(config.dump(), encoding="utf-8")
    (engineering / "architecture.yaml").write_text(ARCHITECTURE_TEMPLATE, encoding="utf-8")
    (engineering / "decisions").mkdir(exist_ok=True)
    (engineering / "events.jsonl").touch(exist_ok=True)

    print("Aplomo\n")
    print("Repository detected:")
    print(" / ".join(profile.technologies))
    print("\nCoding agents configured:")
    for agent in ("cursor", "claude", "codex"):
        print(f"{'✓' if agent in selected else '○'} {agent.title()}")
    if not args.no_install:
        print("\nInstalling integrations...")
        for path, status in install_integrations(root, config).items():
            print(f"  {path}: {status}")
    print("\nDone. .engineering/ is the source of truth.")
    return 0


def command_install(args: Namespace) -> int:
    root = args.root.resolve()
    try:
        config = HarnessConfig.load(root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for path, status in install_integrations(root, config).items():
        print(f"{path}: {status}")
    return 0


def command_doctor(args: Namespace) -> int:
    root = args.root.resolve()
    checks = {"core": {"ok": True, "detail": __version__}}
    try:
        config = HarnessConfig.load(root)
        checks["repository_config"] = {"ok": True, "detail": ".engineering/config.yaml"}
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        config = None
        checks["repository_config"] = {"ok": False, "detail": str(exc)}
    architecture = root / ".engineering" / "architecture.yaml"
    checks["architecture_model"] = {"ok": architecture.exists(), "detail": str(architecture.relative_to(root))}
    if config:
        expected = generated_files(config)
        for relative, content in expected.items():
            path = root / relative
            checks[f"integration:{relative}"] = {
                "ok": path.exists() and path.read_text(encoding="utf-8") == content,
                "detail": "installed and current" if path.exists() and path.read_text(encoding="utf-8") == content else "missing or stale",
            }
        runtime = mcp_smoke_test(root)
        checks["runtime_launch"] = runtime
    profile = detect_repository(root)
    index = index_repository(root)
    checks["git"] = {"ok": profile.is_git, "detail": "repository" if profile.is_git else "not initialized"}
    checks["repository_index"] = {"ok": True, "detail": f"{index['symbols']} symbols, {index['modules']} modules, {index['files']} files"}
    ok = all(check["ok"] for key, check in checks.items() if key != "git")
    if args.json:
        print(json.dumps({"ok": ok, "checks": checks}, indent=2))
    else:
        print("Aplomo\n")
        for name, check in checks.items():
            print(f"{'✓' if check['ok'] else '✗'} {name:<42} {check['detail']}")
    return 0 if ok else 1


def command_hook(args: Namespace) -> int:
    raw = sys.stdin.read().strip() or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Invalid hook JSON: {exc}", file=sys.stderr)
        return 2
    event = EventNormalizer().normalize(args.source, payload)
    encoded = json.dumps(event.to_dict(), ensure_ascii=False)
    if args.dry_run:
        print(encoded)
        return 0
    path = args.root.resolve() / ".engineering" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(encoded + "\n")
    return 0


def command_mcp(args: Namespace) -> int:
    run_mcp(args.root)
    return 0


def command_eval(args: Namespace) -> int:
    report = run_evaluations()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Aplomo evaluation\n")
        for check in report["checks"]:
            print(f"{'✓' if check['ok'] else '✗'} {check['name']:<34} {check['detail']}")
        print(f"\n{report['passed']}/{report['total']} checks passed")
    return 0 if report["ok"] else 1


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
