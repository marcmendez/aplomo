import tempfile
import unittest
from pathlib import Path

from engineering_harness.config import HarnessConfig


class HarnessConfigTests(unittest.TestCase):
    def test_dump_and_load_round_trip(self):
        expected = HarnessConfig(
            version=1,
            project_name="project: alpha",
            agents=["cursor", "codex"],
            technologies=["Python", "FastAPI", "PostgreSQL"],
            integrations={"hooks": True, "mcp": True, "skills": False},
            context={"max_files": 40, "max_chars": 100_000, "max_matches": 8},
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_dir = root / ".engineering"
            config_dir.mkdir()
            (config_dir / "config.yaml").write_text(expected.dump(), encoding="utf-8")
            actual = HarnessConfig.load(root)
        self.assertEqual(actual, expected)

    def test_load_missing_config_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(FileNotFoundError, "aplomo init"):
                HarnessConfig.load(Path(directory))


if __name__ == "__main__":
    unittest.main()
