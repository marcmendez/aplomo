import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from engineering_harness.detection import detect_repository
from engineering_harness.repository import find_existing_patterns, index_repository, review_diff


class RepositoryAnalysisTests(unittest.TestCase):
    def test_detects_languages_frameworks_database_and_agents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "demo"\ndependencies = ["fastapi", "psycopg"]\n', encoding="utf-8"
            )
            (root / "package.json").write_text(json.dumps({"dependencies": {"react": "latest"}}), encoding="utf-8")
            (root / "tsconfig.json").write_text("{}\n", encoding="utf-8")
            (root / ".cursor").mkdir()
            profile = detect_repository(root)
        self.assertTrue({"Python", "Node.js", "TypeScript", "FastAPI", "React", "PostgreSQL"}.issubset(profile.technologies))
        self.assertTrue(profile.agents["cursor"])

    def test_index_counts_symbols_and_ignores_dependency_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src"
            source.mkdir()
            (source / "service.py").write_text("class Service:\n    def run(self):\n        pass\n", encoding="utf-8")
            (source / "ui.ts").write_text("export function render() {}\ninterface Props {}\n", encoding="utf-8")
            dependency = root / "node_modules/pkg"
            dependency.mkdir(parents=True)
            (dependency / "ignored.js").write_text("function ignored() {}\n", encoding="utf-8")
            result = index_repository(root)
        self.assertEqual(result["files"], 2)
        self.assertEqual(result["symbols"], 4)
        self.assertEqual(result["languages"], {".py": 1, ".ts": 1})

    def test_pattern_search_is_case_insensitive_and_limited(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "service.py").write_text("class PaymentService:\n    payment_service = True\n", encoding="utf-8")
            result = find_existing_patterns(root, "PAYMENT", limit=1)
        self.assertEqual(len(result["matches"]), 1)
        self.assertIn("PaymentService", result["matches"][0]["text"])

    def test_diff_review_flags_code_without_tests_and_possible_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            source = root / "service.py"
            source.write_text("VALUE = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "service.py"], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Tests", "-c", "user.email=tests@example.com", "commit", "-qm", "initial"],
                cwd=root,
                check=True,
            )
            secret_fixture = 'VALUE = 2\napi_' + 'key = "not-a-real-secret"\n'
            source.write_text(secret_fixture, encoding="utf-8")
            result = review_diff(root)
        self.assertEqual(result["status"], "needs_attention")
        self.assertIn("service.py", result["files"])
        self.assertTrue(any("secret" in warning.lower() for warning in result["warnings"]))
        self.assertTrue(any("test" in warning.lower() for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
