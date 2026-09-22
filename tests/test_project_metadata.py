import tomllib
import unittest
from pathlib import Path


class ProjectMetadataTests(unittest.TestCase):
    def test_python_312_is_the_declared_minimum(self):
        root = Path(__file__).resolve().parents[1]
        metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["project"]["requires-python"], ">=3.12")
        self.assertIn("Programming Language :: Python :: 3.12", metadata["project"]["classifiers"])
        self.assertNotIn("Programming Language :: Python :: 3.11", metadata["project"]["classifiers"])

    def test_runtime_has_no_third_party_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertNotIn("dependencies", metadata["project"])
        self.assertIn("pytest", metadata["dependency-groups"]["dev"][0])

    def test_aplomo_is_the_package_and_primary_command(self):
        root = Path(__file__).resolve().parents[1]
        metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(metadata["project"]["name"], "aplomo")
        self.assertEqual(metadata["project"]["scripts"]["aplomo"], "engineering_harness.cli:main")
        self.assertEqual(metadata["project"]["scripts"]["eng"], "engineering_harness.cli:main")


if __name__ == "__main__":
    unittest.main()
