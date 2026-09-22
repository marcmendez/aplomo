import unittest

from engineering_harness.events import EventNormalizer, EventType


class EventNormalizerTests(unittest.TestCase):
    def setUp(self):
        self.normalizer = EventNormalizer()

    def test_cursor_file_edit(self):
        event = self.normalizer.normalize("cursor", {"hook_event_name": "afterFileEdit", "file_path": "src/service.py"})
        self.assertEqual(event.event, EventType.FILE_WRITE)
        self.assertEqual(event.path, "src/service.py")

    def test_claude_nested_tool_payload(self):
        event = self.normalizer.normalize(
            "claude",
            {"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": "src/a.py"}},
        )
        self.assertEqual(event.event, EventType.FILE_WRITE)
        self.assertEqual(event.path, "src/a.py")

    def test_codex_nested_tool_payload(self):
        event = self.normalizer.normalize(
            "codex",
            {"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": "src/b.py"}},
        )
        self.assertEqual(event.event, EventType.FILE_WRITE)
        self.assertEqual(event.path, "src/b.py")

    def test_cursor_shell_observation(self):
        event = self.normalizer.normalize("cursor", {"hook": "afterShellExecution", "command": "pytest"})
        self.assertEqual(event.event, EventType.COMMAND_EXECUTED)
        self.assertEqual(event.command, "pytest")

    def test_unknown_event_is_preserved_in_payload(self):
        payload = {"event": "future.agent.event", "answer": 42}
        event = self.normalizer.normalize("future-agent", payload)
        self.assertEqual(event.event, EventType.UNKNOWN)
        self.assertEqual(event.payload, payload)


if __name__ == "__main__":
    unittest.main()
