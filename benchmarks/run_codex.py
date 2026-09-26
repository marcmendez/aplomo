#!/usr/bin/env python3
"""Run a small, reproducible A/B benchmark with and without Aplomo."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Case:
    name: str
    prompt: str
    files: dict[str, str]
    score: Callable[[Path], dict[str, bool]]


def _run(command: list[str], cwd: Path, *, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)


def _write_files(root: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _python_import(root: Path, expression: str) -> bool:
    result = _run([sys.executable, "-c", expression], root)
    return result.returncode == 0


def _has_new_test(root: Path, needle: str) -> bool:
    return any(needle.lower() in path.read_text(encoding="utf-8", errors="ignore").lower() for path in root.rglob("test*.py"))


def _module_with_symbol(root: Path, symbol: str) -> str | None:
    for path in (root / "src").rglob("*.py"):
        if f"class {symbol}" in path.read_text(encoding="utf-8", errors="ignore") or f"def {symbol}" in path.read_text(encoding="utf-8", errors="ignore"):
            return ".".join(path.relative_to(root).with_suffix("").parts)
    return None


def _retry_score(root: Path) -> dict[str, bool]:
    candidates = list(root.rglob("*.py"))
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in candidates)
    module = _module_with_symbol(root, "InvoiceRetryService")
    return {
        "behavior": bool(module) and _python_import(
            root,
            f"from {module} import InvoiceRetryService as S; "
            "assert S().should_retry(1, 503); assert not S().should_retry(3, 503); assert not S().should_retry(1, 400)",
        ),
        "reuses_retry_policy": "from src.shared.retry import RetryPolicy" in text and text.count("class RetryPolicy") == 1,
        "adds_regression_test": _has_new_test(root, "InvoiceRetryService"),
    }


def _summary_score(root: Path) -> dict[str, bool]:
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in root.rglob("*.py"))
    domain = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in (root / "src/shop/domain").rglob("*.py"))
    module = _module_with_symbol(root, "summarize_order")
    return {
        "behavior": bool(module) and _python_import(
            root,
            "from decimal import Decimal; from src.shop.domain.order import Order; "
            f"from {module} import summarize_order; "
            "assert summarize_order(Order('A12', Decimal('12.5'))) == 'Order #A12: €12.50'",
        ),
        "reuses_money_formatter": "from src.shop.presentation.money import format_money" in text,
        "preserves_layer_boundary": "application" not in domain and "presentation" not in domain,
        "adds_regression_test": _has_new_test(root, "summarize_order"),
    }


def _email_score(root: Path) -> dict[str, bool]:
    return {
        "behavior": _python_import(
            root,
            "from src.accounts.email import normalize_email; "
            "assert normalize_email('  Ada@Example.COM ') == 'ada@example.com'; "
            "\ntry: normalize_email('a da@example.com')\nexcept ValueError: pass\nelse: raise AssertionError('internal whitespace accepted')",
        ),
        "adds_regression_test": _has_new_test(root, "whitespace"),
        "keeps_public_api": (root / "src/accounts/email.py").exists()
        and "def normalize_email" in (root / "src/accounts/email.py").read_text(encoding="utf-8", errors="ignore"),
    }


CASES = [
    Case(
        name="reuse-existing-policy",
        prompt="Add invoice retry support matching the existing payment retry behavior. Keep the public API InvoiceRetryService.should_retry(attempt, status_code) and add tests.",
        files={
            "pyproject.toml": "[project]\nname='bench-retry'\nversion='0.1.0'\nrequires-python='>=3.12'\n[tool.pytest.ini_options]\npythonpath=['.']\n",
            "src/__init__.py": "",
            "src/shared/__init__.py": "",
            "src/shared/retry.py": "class RetryPolicy:\n    def __init__(self, max_attempts: int = 3):\n        self.max_attempts = max_attempts\n\n    def allows(self, attempt: int, status_code: int) -> bool:\n        return attempt < self.max_attempts and status_code >= 500\n",
            "src/payments/__init__.py": "",
            "src/payments/payment_retry.py": "from src.shared.retry import RetryPolicy\n\nclass PaymentRetryService:\n    def __init__(self):\n        self.policy = RetryPolicy()\n\n    def should_retry(self, attempt: int, status_code: int) -> bool:\n        return self.policy.allows(attempt, status_code)\n",
            "tests/test_payment_retry.py": "from src.payments.payment_retry import PaymentRetryService\n\ndef test_server_error_is_retried():\n    assert PaymentRetryService().should_retry(1, 503)\n",
        },
        score=_retry_score,
    ),
    Case(
        name="respect-layer-boundary",
        prompt="Add a public summarize_order(order) API returning `Order #<id>: €<amount>` while respecting the current layer boundaries and patterns. Add tests.",
        files={
            "pyproject.toml": "[project]\nname='bench-layers'\nversion='0.1.0'\nrequires-python='>=3.12'\n[tool.pytest.ini_options]\npythonpath=['.']\n",
            "src/__init__.py": "",
            "src/shop/__init__.py": "",
            "src/shop/domain/__init__.py": "",
            "src/shop/domain/order.py": "from dataclasses import dataclass\nfrom decimal import Decimal\n\n@dataclass(frozen=True)\nclass Order:\n    id: str\n    total: Decimal\n",
            "src/shop/presentation/__init__.py": "",
            "src/shop/presentation/money.py": "from decimal import Decimal\n\ndef format_money(value: Decimal) -> str:\n    return f'€{value:.2f}'\n",
            "tests/test_money.py": "from decimal import Decimal\nfrom src.shop.presentation.money import format_money\n\ndef test_format_money():\n    assert format_money(Decimal('2')) == '€2.00'\n",
            ".engineering/architecture.yaml": "version: 1\nlayers:\n  domain:\n    may_import: []\n  presentation:\n    may_import: [domain]\nrules:\n  prefer_existing_patterns: true\n",
        },
        score=_summary_score,
    ),
    Case(
        name="targeted-regression-fix",
        prompt="Fix normalize_email so surrounding whitespace is accepted but internal whitespace remains invalid. Add regression tests and preserve the existing API.",
        files={
            "pyproject.toml": "[project]\nname='bench-email'\nversion='0.1.0'\nrequires-python='>=3.12'\n[tool.pytest.ini_options]\npythonpath=['.']\n",
            "src/__init__.py": "",
            "src/accounts/__init__.py": "",
            "src/accounts/email.py": "def normalize_email(value: str) -> str:\n    if any(char.isspace() for char in value):\n        raise ValueError('email cannot contain whitespace')\n    return value.lower()\n",
            "tests/test_email.py": "import pytest\nfrom src.accounts.email import normalize_email\n\ndef test_lowercases_email():\n    assert normalize_email('Ada@Example.COM') == 'ada@example.com'\n\ndef test_rejects_internal_whitespace():\n    with pytest.raises(ValueError):\n        normalize_email('a da@example.com')\n",
        },
        score=_email_score,
    ),
]


def _parse_events(stdout: str) -> dict[str, int]:
    usage = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "tool_calls": 0, "aplomo_calls": 0}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed":
            raw = event.get("usage", {})
            for key in ("input_tokens", "cached_input_tokens", "output_tokens"):
                usage[key] = int(raw.get(key, usage[key]) or 0)
        item = event.get("item", {})
        if event.get("type") == "item.completed" and item.get("type") in {"command_execution", "mcp_tool_call", "function_call"}:
            usage["tool_calls"] += 1
            if item.get("type") == "mcp_tool_call" and "aplomo" in json.dumps(item).lower():
                usage["aplomo_calls"] += 1
    return usage


def run_case(case: Case, treatment: str, repetition: int, keep: Path | None) -> dict[str, object]:
    temporary = Path(tempfile.mkdtemp(prefix=f"aplomo-{case.name}-{treatment}-"))
    try:
        _write_files(temporary, case.files)
        _run(["git", "init", "-q"], temporary)
        _run(["git", "config", "user.email", "benchmark@aplomo.dev"], temporary)
        _run(["git", "config", "user.name", "Aplomo benchmark"], temporary)
        if treatment == "aplomo":
            init = _run([sys.executable, "-m", "engineering_harness.cli", "init", "--root", str(temporary), "--agents", "codex"], temporary)
            if init.returncode:
                raise RuntimeError(init.stderr or init.stdout)
            # Restore fixture-owned files such as the case-specific architecture model.
            _write_files(temporary, case.files)
        _run(["git", "add", "."], temporary)
        _run(["git", "commit", "-qm", "benchmark fixture"], temporary)
        started = time.monotonic()
        command = [
            "codex", "exec", "--ephemeral", "--approve-for-me", "--json", "-C", str(temporary),
            case.prompt,
        ]
        completed = _run(command, temporary)
        elapsed = round(time.monotonic() - started, 2)
        checks = case.score(temporary)
        result: dict[str, object] = {
            "case": case.name,
            "treatment": treatment,
            "repetition": repetition,
            "agent_exit_code": completed.returncode,
            "elapsed_seconds": elapsed,
            "checks": checks,
            "score": sum(checks.values()),
            "max_score": len(checks),
            **_parse_events(completed.stdout),
        }
        if completed.returncode:
            result["agent_error"] = completed.stderr.strip()[-1000:]
        if keep:
            destination = keep / f"{case.name}-{treatment}-{repetition}"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(temporary, destination)
        return result
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--keep-runs", type=Path)
    parser.add_argument("--case", choices=[case.name for case in CASES], action="append")
    parser.add_argument("--treatment", choices=["baseline", "aplomo"], action="append")
    args = parser.parse_args()
    if shutil.which("codex") is None:
        parser.error("codex CLI is required")
    version = _run(["codex", "--version"], Path.cwd()).stdout.strip()
    results = []
    for repetition in range(1, args.repetitions + 1):
        for case in (case for case in CASES if not args.case or case.name in args.case):
            for treatment in (args.treatment or ("baseline", "aplomo")):
                print(f"Running {case.name} / {treatment} / {repetition}", file=sys.stderr, flush=True)
                results.append(run_case(case, treatment, repetition, args.keep_runs))
    report = {"schema_version": 1, "codex_version": version, "repetitions": args.repetitions, "results": results}
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if all(result["agent_exit_code"] == 0 for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
