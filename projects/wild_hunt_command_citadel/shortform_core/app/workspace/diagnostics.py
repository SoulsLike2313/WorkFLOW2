from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class LogRecord:
    timestamp: str
    level: str
    channel: str
    event: str
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "channel": self.channel,
            "event": self.event,
            "payload": self.payload,
        }


class StructuredDiagnostics:
    def __init__(self, base_dir: Path, *, debug: bool = False) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.debug_enabled = debug
        self._lock = Lock()

    def log(
        self,
        channel: str,
        event: str,
        *,
        level: str = "INFO",
        payload: dict[str, Any] | None = None,
    ) -> None:
        if level.upper() == "DEBUG" and not self.debug_enabled:
            return
        record = LogRecord(
            timestamp=_utc_now_iso(),
            level=level.upper(),
            channel=channel,
            event=event,
            payload=payload or {},
        )
        target = self.base_dir / f"{channel}.jsonl"
        line = json.dumps(record.as_dict(), ensure_ascii=False)
        with self._lock:
            with target.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")

    def file_for(self, channel: str) -> Path:
        return self.base_dir / f"{channel}.jsonl"


_DEFAULT_DIAGNOSTICS: StructuredDiagnostics | None = None


def configure_diagnostics(base_dir: Path, *, debug: bool = False) -> StructuredDiagnostics:
    global _DEFAULT_DIAGNOSTICS
    _DEFAULT_DIAGNOSTICS = StructuredDiagnostics(base_dir=base_dir, debug=debug)
    return _DEFAULT_DIAGNOSTICS


def get_diagnostics() -> StructuredDiagnostics:
    global _DEFAULT_DIAGNOSTICS
    if _DEFAULT_DIAGNOSTICS is None:
        fallback = Path(__file__).resolve().parents[2] / "runtime" / "logs"
        _DEFAULT_DIAGNOSTICS = StructuredDiagnostics(fallback, debug=False)
    return _DEFAULT_DIAGNOSTICS


def diag_log(
    channel: str,
    event: str,
    *,
    level: str = "INFO",
    payload: dict[str, Any] | None = None,
) -> None:
    get_diagnostics().log(channel=channel, event=event, level=level, payload=payload)
