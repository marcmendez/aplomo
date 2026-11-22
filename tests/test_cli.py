import io
import json
import tempfile
import tomllib
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from engineering_harness.cli import main
from engineering_harness.config import HarnessConfig
from engineering_harness.generators import install_integrations
from engineering_harness.runtime import LAUNCHER, launcher_command, mcp_smoke_test


class CliTests(unittest.TestCase):
    def test_init_install_and_doctor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text('[project]\nname="demo"\ndependencies=["fastapi"]\n', encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = main(["init", "--root", str(root), "--agents", "cursor", "codex", "--mcp", "--hooks"])
            self.assertEqual(code, 0)
            self.assertTrue((root / ".engineering/config.yaml").exists())
            self.assertTrue((root / ".engineering/patterns.md").exists())
            self.assertTrue((root / ".cursor/hooks.json").exists())
            self.assertTrue((root / ".codex/hooks.json").exists())
            self.assertIn("aplomo:start", (root / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertEqual(
                tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))["mcp_servers"]["aplomo"]["command"],
                launcher_command(),
            )
            self.assertTrue((root / LAUNCHER).exists())
            self.assertTrue(mcp_smoke_test(root)["ok"])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["doctor", "--root", str(root)]), 0)

    def test_installer_does_not_overwrite_unowned_agent_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / ".cursor/hooks.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"user": true}\n', encoding="utf-8")
            (root / ".engineering").mkdir()
            config = HarnessConfig(project_name="demo", agents=["cursor"], integrations={"hooks": True})
            statuses = install_integrations(root, config)
            self.assertIn("skipped", statuses[".cursor/hooks.json"])
            self.assertEqual(existing.read_text(encoding="utf-8"), '{"user": true}\n')

    def test_init_refuses_to_replace_existing_source_of_truth(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["init", "--root", str(root), "--agents", "codex"]), 0)
            error = io.StringIO()
            with redirect_stdout(io.StringIO()), patch("sys.stderr", error):
                self.assertEqual(main(["init", "--root", str(root), "--agents", "cursor"]), 2)
            self.assertIn("Already initialized", error.getvalue())
            self.assertIn('agents: ["codex"]', (root / ".engineering/config.yaml").read_text(encoding="utf-8"))

    def test_install_is_idempotent_and_keeps_one_agents_section(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".engineering").mkdir()
            config = HarnessConfig(project_name="demo", agents=["cursor", "claude", "codex"])
            first = install_integrations(root, config)
            snapshots = {
                relative: (root / relative).read_text(encoding="utf-8")
                for relative, status in first.items()
                if status in {"installed", "updated"}
            }
            second = install_integrations(root, config)
            self.assertTrue(all(status in {"installed", "updated"} for status in second.values()))
            for relative, content in snapshots.items():
                self.assertEqual((root / relative).read_text(encoding="utf-8"), content)
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8").count("aplomo:start"), 1)
            self.assertEqual((root / "CLAUDE.md").read_text(encoding="utf-8").count("aplomo:start"), 1)

    def test_install_migrates_an_existing_repository_with_a_pattern_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_dir = root / ".engineering"
            config_dir.mkdir()
            (config_dir / "config.yaml").write_text(
                HarnessConfig(project_name="demo", agents=["codex"]).dump(), encoding="utf-8"
            )
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["install", "--root", str(root)]), 0)
            catalog = config_dir / "patterns.md"
            self.assertTrue(catalog.exists())
            self.assertIn("Canonical implementation", catalog.read_text(encoding="utf-8"))

    def test_legacy_agents_marker_is_migrated_without_duplication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".engineering").mkdir()
            (root / "AGENTS.md").write_text(
                "User content\n\n<!-- engineering-harness:start -->\nOld block\n<!-- engineering-harness:end -->\n",
                encoding="utf-8",
            )
            install_integrations(root, HarnessConfig(project_name="demo", agents=["codex"]))
            content = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("User content", content)
            self.assertNotIn("engineering-harness:start", content)
            self.assertEqual(content.count("aplomo:start"), 1)

    def test_hook_persists_normalized_event(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = '{"hook_event_name":"afterFileEdit","file_path":"src/service.py"}'
            with patch("sys.stdin", io.StringIO(payload)):
                self.assertEqual(main(["hook", "--source", "cursor", "--root", str(root)]), 0)
            event = json.loads((root / ".engineering/events.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(event["event"], "FILE_WRITE")
            self.assertEqual(event["path"], "src/service.py")
            self.assertIn("event_id", event)
            self.assertIn("timestamp", event)

    def test_doctor_json_reports_stale_generated_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["init", "--root", str(root), "--agents", "cursor"]), 0)
            (root / ".cursor/skills/aplomo-review/SKILL.md").write_text("stale\n", encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["doctor", "--root", str(root), "--json"]), 1)
            report = json.loads(output.getvalue())
            self.assertFalse(report["ok"])
            self.assertEqual(report["checks"]["integration:.cursor/skills/aplomo-review/SKILL.md"]["detail"], "missing or stale")

    def test_skill_only_init_and_doctor_do_not_require_a_server(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with redirect_stdout(io.StringIO()), patch("engineering_harness.cli.mcp_smoke_test") as smoke:
                self.assertEqual(main(["init", "--root", str(root), "--agents", "cursor", "codex", "claude"]), 0)
                self.assertEqual(main(["doctor", "--root", str(root)]), 0)
                smoke.assert_not_called()
            self.assertFalse((root / LAUNCHER).exists())
            self.assertFalse((root / ".engineering/events.jsonl").exists())
            self.assertIn("Aplomo review skill", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_init_without_assistant_markers_installs_portable_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with redirect_stdout(io.StringIO()), patch("engineering_harness.detection.shutil.which", return_value=None):
                self.assertEqual(main(["init", "--root", str(root)]), 0)
            self.assertEqual(HarnessConfig.load(root).agents, ["cursor", "claude", "codex"])
            for location in (".cursor", ".claude", ".agents"):
                skill = root / location / "skills/aplomo-review"
                for name in ("architecture", "correctness", "compatibility"):
                    self.assertTrue((skill / "references" / f"{name}.md").is_file())

    def test_disabling_mcp_removes_unmodified_adapters_and_preserves_custom_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agents = ["cursor", "codex", "claude"]
            install_integrations(root, HarnessConfig(agents=agents, integrations={"mcp": True}))
            custom = root / ".cursor/mcp.json"
            custom.write_text('{"mcpServers":{"team":{"command":"team-tool"}}}\n', encoding="utf-8")
            statuses = install_integrations(root, HarnessConfig(agents=agents))
            self.assertIn("preserved", statuses[".cursor/mcp.json"])
            self.assertIn("team-tool", custom.read_text(encoding="utf-8"))
            self.assertFalse((root / ".codex/config.toml").exists())
            self.assertFalse((root / ".mcp.json").exists())
            self.assertFalse((root / LAUNCHER).exists())
            self.assertNotIn("aplomo_prepare_change", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_local_analysis_commands_match_mcp_results(self):
        import subprocess
        from engineering_harness.mcp_server import call_tool

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "retry.py").write_text("class RetryPolicy:\n    pass\n", encoding="utf-8")
            (root / "retry_elsewhere.py").write_text("class RetryPolicy:\n    pass\n", encoding="utf-8")
            cases = [
                (["prepare", "Add retries", "--query", "RetryPolicy"], "aplomo_prepare_change",
                 {"request": "Add retries", "query": "RetryPolicy"}),
                (["prepare", "Add retries", "--query", "RetryPolicy", "--path", "retry.py"], "aplomo_prepare_change",
                 {"request": "Add retries", "query": "RetryPolicy", "paths": ["retry.py"]}),
                (["validate-abstraction", "InvoiceRetryPolicy", "retry invoices"], "aplomo_validate_abstraction",
                 {"proposed_name": "InvoiceRetryPolicy", "responsibility": "retry invoices"}),
                (["review-diff"], "aplomo_review_diff", {}),
            ]
            for command, tool, arguments in cases:
                with self.subTest(command=command):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        self.assertEqual(main([*command, "--root", str(root)]), 0)
                    self.assertEqual(json.loads(output.getvalue()), call_tool(root, tool, arguments))

    def test_mcp_protocol(self):
        from engineering_harness.mcp_server import dispatch

        with tempfile.TemporaryDirectory() as directory:
            result = dispatch(Path(directory), {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            names = {tool["name"] for tool in result["result"]["tools"]}
            self.assertIn("aplomo_review_diff", names)
            self.assertIn("aplomo_understand_repo", names)

    def test_mcp_initialize_and_tool_call(self):
        from engineering_harness.mcp_server import dispatch

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialized = dispatch(
                root,
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
            )
            self.assertEqual(initialized["result"]["serverInfo"]["name"], "aplomo")
            reviewed = dispatch(
                root,
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "aplomo_review_plan",
                        "arguments": {"plan": "Search existing patterns, update a module compatibly, and run tests."},
                    },
                },
            )
            content = json.loads(reviewed["result"]["content"][0]["text"])
            self.assertEqual(content["status"], "pass")

    def test_prepare_change_combines_repository_context(self):
        from engineering_harness.mcp_server import call_tool

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src/retry.py"
            source.parent.mkdir()
            source.write_text("class RetryPolicy:\n    pass\n", encoding="utf-8")
            architecture = root / ".engineering/architecture.yaml"
            architecture.parent.mkdir()
            architecture.write_text("version: 1\n", encoding="utf-8")
            (root / ".engineering/patterns.md").write_text("# Retry pattern\n", encoding="utf-8")
            result = call_tool(
                root,
                "aplomo_prepare_change",
                {"request": "Add invoice retries", "query": "RetryPolicy"},
            )
            self.assertEqual(result["existing_patterns"]["matches"][0]["path"], "src/retry.py")
            self.assertEqual(result["architecture"], "version: 1\n")
            self.assertEqual(result["pattern_catalog"], "# Retry pattern\n")
            self.assertEqual(result["read_budget"]["max_files"], 80)

    def test_validate_abstraction_tool_requires_reuse_or_justification(self):
        from engineering_harness.mcp_server import call_tool

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "retry.py").write_text("class RetryPolicy:\n    pass\n", encoding="utf-8")
            result = call_tool(
                root,
                "aplomo_validate_abstraction",
                {"proposed_name": "InvoiceRetryPolicy", "responsibility": "retry failed invoices"},
            )
            self.assertEqual(result["status"], "needs_justification")

    def test_eval_command_reports_all_acceptance_checks(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["eval", "--json"]), 0)
        report = json.loads(output.getvalue())
        self.assertTrue(report["ok"])
        self.assertEqual(report["passed"], report["total"])
        self.assertGreaterEqual(report["total"], 5)

    def test_mcp_unknown_method_returns_json_rpc_error(self):
        from engineering_harness.mcp_server import dispatch

        response = dispatch(Path.cwd(), {"jsonrpc": "2.0", "id": 9, "method": "missing/method"})
        self.assertEqual(response["id"], 9)
        self.assertEqual(response["error"]["code"], -32601)

    def test_diff_review_reports_non_git_repository(self):
        from engineering_harness.repository import review_diff

        with tempfile.TemporaryDirectory() as directory:
            result = review_diff(Path(directory))
            self.assertEqual(result["status"], "unavailable")
            self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main()
