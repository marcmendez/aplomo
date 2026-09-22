"""Canonical events and adapter-independent normalization."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import uuid


class EventType(str, Enum):
    SESSION_START = "SESSION_START"
    PROMPT_RECEIVED = "PROMPT_RECEIVED"
    FILE_READ = "FILE_READ"
    FILE_WRITE = "FILE_WRITE"
    FILE_CREATED = "FILE_CREATED"
    COMMAND_EXECUTED = "COMMAND_EXECUTED"
    PLAN_READY = "PLAN_READY"
    TASK_COMPLETE = "TASK_COMPLETE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EngineeringEvent:
    event: EventType
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path: Optional[str] = None
    command: Optional[str] = None
    session_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        value = asdict(self)
        value["event"] = self.event.value
        return {key: item for key, item in value.items() if item is not None}


class EventNormalizer:
    """Normalize different agent payloads into one stable event contract."""

    _MAPPINGS = {
        "cursor": {
            "afterfileedit": EventType.FILE_WRITE,
            "beforefileedit": EventType.FILE_READ,
            "sessionstart": EventType.SESSION_START,
            "afteragentresponse": EventType.TASK_COMPLETE,
            "aftershellexecution": EventType.COMMAND_EXECUTED,
        },
        "claude": {
            "sessionstart": EventType.SESSION_START,
            "userpromptsubmit": EventType.PROMPT_RECEIVED,
            "pretooluse:read": EventType.FILE_READ,
            "posttooluse:write": EventType.FILE_WRITE,
            "posttooluse:edit": EventType.FILE_WRITE,
            "stop": EventType.TASK_COMPLETE,
        },
        "codex": {
            "session_start": EventType.SESSION_START,
            "sessionstart": EventType.SESSION_START,
            "user_prompt_submit": EventType.PROMPT_RECEIVED,
            "pre_tool_use:read": EventType.FILE_READ,
            "pretooluse:read": EventType.FILE_READ,
            "post_tool_use:write": EventType.FILE_WRITE,
            "post_tool_use:edit": EventType.FILE_WRITE,
            "posttooluse:write": EventType.FILE_WRITE,
            "posttooluse:edit": EventType.FILE_WRITE,
            "stop": EventType.TASK_COMPLETE,
        },
    }

    def normalize(self, source: str, payload: Mapping[str, Any]) -> EngineeringEvent:
        source_key = source.lower().strip()
        raw_name = self._event_name(source_key, payload)
        event_type = self._lookup(source_key, raw_name, payload)
        path = self._first(payload, "path", "file_path", "filePath", "tool_input.file_path", "tool.input.path")
        command = self._first(payload, "command", "tool_input.command", "tool.input.command")
        session_id = self._first(payload, "session_id", "sessionId", "conversation_id")
        return EngineeringEvent(
            event=event_type,
            source=source_key,
            path=self._safe_path(path),
            command=str(command) if command is not None else None,
            session_id=str(session_id) if session_id is not None else None,
            payload=dict(payload),
        )

    def _lookup(self, source: str, name: str, payload: Mapping[str, Any]) -> EventType:
        mapping = self._MAPPINGS.get(source, {})
        candidates = [name, name.lower(), name.replace("_", "").lower()]
        tool = str(self._first(payload, "tool_name", "tool", "tool.name") or "").lower()
        if tool:
            candidates.insert(0, f"{name}:{tool}")
            candidates.insert(1, f"{name.lower()}:{tool}")
        normalized_mapping = {key.lower(): value for key, value in mapping.items()}
        for candidate in candidates:
            if candidate in mapping:
                return mapping[candidate]
            if candidate.lower() in normalized_mapping:
                return normalized_mapping[candidate.lower()]
        try:
            return EventType(name.upper())
        except ValueError:
            return EventType.UNKNOWN

    @staticmethod
    def _event_name(source: str, payload: Mapping[str, Any]) -> str:
        keys = {
            "cursor": ("hook_event_name", "hook", "event", "type"),
            "claude": ("hook_event_name", "event", "type"),
            "codex": ("hook_event_name", "event", "type"),
        }.get(source, ("event", "type", "hook"))
        return str(next((payload[key] for key in keys if payload.get(key)), "UNKNOWN"))

    @staticmethod
    def _first(payload: Mapping[str, Any], *paths: str) -> Any:
        for path in paths:
            value: Any = payload
            for part in path.split("."):
                if not isinstance(value, Mapping) or part not in value:
                    value = None
                    break
                value = value[part]
            if value is not None:
                return value
        return None

    @staticmethod
    def _safe_path(value: Any) -> Optional[str]:
        if value is None:
            return None
        return Path(str(value)).as_posix()
