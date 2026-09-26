import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from engineering_harness.detection import detect_repository
from engineering_harness.repository import find_existing_patterns, index_repository, review_diff, validate_new_abstraction


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
        self.assertLessEqual(result["read_summary"]["files_read"], 1)

    def test_pattern_search_respects_the_read_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(3):
                (root / f"module_{index}.py").write_text(f"class Service{index}:\n    pass\n", encoding="utf-8")
            result = find_existing_patterns(root, "Service", limit=10, max_files=1, max_chars=30)
        self.assertEqual(result["read_summary"]["files_read"], 1)
        self.assertLessEqual(result["read_summary"]["chars_read"], 30)
        self.assertTrue(result["read_summary"]["truncated"])

    def test_new_abstraction_requires_justification_when_a_candidate_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "retry.py").write_text("class RetryPolicy:\n    pass\n", encoding="utf-8")
            result = validate_new_abstraction(root, "InvoiceRetryPolicy", "retry failed invoices")
        self.assertEqual(result["status"], "needs_justification")
        self.assertTrue(result["candidates"])

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

    def test_diff_review_includes_untracked_code_and_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            source = root / "src/new_feature.py"
            test = root / "tests/test_new_feature.py"
            source.parent.mkdir()
            test.parent.mkdir()
            source.write_text("def new_feature():\n    return True\n", encoding="utf-8")
            test.write_text("def test_new_feature():\n    assert True\n", encoding="utf-8")
            result = review_diff(root)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["untracked"], ["src/new_feature.py", "tests/test_new_feature.py"])
        self.assertEqual(result["additions"], 4)

    def test_diff_review_includes_staged_files_before_the_first_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            source = root / "src/new_feature.py"
            test = root / "tests/test_new_feature.py"
            source.parent.mkdir()
            test.parent.mkdir()
            source.write_text("def new_feature():\n    return True\n", encoding="utf-8")
            test.write_text("def test_new_feature():\n    assert True\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            result = review_diff(root)
        self.assertEqual(result["status"], "pass")
        self.assertIn("src/new_feature.py", result["files"])
        self.assertEqual(result["untracked"], [])

    def test_diff_review_flags_a_duplicate_staged_abstraction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            existing = root / "src/retry.py"
            existing.parent.mkdir()
            existing.write_text("class RetryPolicy:\n    pass\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Tests", "-c", "user.email=tests@example.com", "commit", "-qm", "initial"],
                cwd=root,
                check=True,
            )
            duplicate = root / "src/invoice_retry.py"
            duplicate.write_text("class RetryPolicy:\n    pass\n", encoding="utf-8")
            test = root / "tests/test_retry.py"
            test.parent.mkdir()
            test.write_text("def test_retry():\n    assert True\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            result = review_diff(root)
        self.assertEqual(result["status"], "needs_attention")
        self.assertEqual(result["duplicate_abstractions"][0]["name"], "RetryPolicy")


if __name__ == "__main__":
    unittest.main()
