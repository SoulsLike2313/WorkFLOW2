from __future__ import annotations

import json
from pathlib import Path

from app.runtime_observability import build_runtime_observability_snapshot


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in rows), encoding="utf-8")


def test_runtime_observability_classifies_latest_error_event(tmp_path: Path):
    (tmp_path / "PROJECT_MANIFEST.json").write_text(
        json.dumps(
            {
                "schema_version": "2.1.0",
                "name": "TikTok Agent Platform",
                "slug": "tiktok_agent_platform",
                "notes": ["runtime observability test"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "PROMPT_FOR_CODEX.txt").write_text("prompt baseline", encoding="utf-8")

    _write_jsonl(
        tmp_path / "runtime" / "logs" / "runtime_logs.jsonl",
        [
            {
                "timestamp": "2026-03-25T07:00:00+00:00",
                "level": "INFO",
                "channel": "runtime_logs",
                "event": "internal_backend_ready",
                "payload": {"summary": "backend ready"},
            },
            {
                "timestamp": "2026-03-25T07:01:00+00:00",
                "level": "ERROR",
                "channel": "runtime_logs",
                "event": "internal_backend_not_ready",
                "payload": {
                    "summary": "backend readiness probe failed",
                    "failure_reason": "backend_probe_timeout",
                    "recovery_signal": "restart_backend_and_validate_port_binding",
                },
            },
        ],
    )

    snapshot = build_runtime_observability_snapshot(project_root=tmp_path, max_events=8)
    assert snapshot["process_state"] == "ERROR"
    assert snapshot["failure_reason"] == "backend_probe_timeout"
    assert snapshot["recovery_signal"] == "restart_backend_and_validate_port_binding"
    assert snapshot["prompt_lineage"]["trusted_boundary"] == "PARTIAL_TEXT_ONLY"
    assert snapshot["prompt_lineage"]["text_boundary"]["full_prompt_text_exposed"] is False
    assert len(snapshot["recent_events"]) >= 2


def test_runtime_observability_returns_wait_when_log_missing(tmp_path: Path):
    snapshot = build_runtime_observability_snapshot(project_root=tmp_path, max_events=6)
    assert snapshot["process_state"] == "WAIT"
    assert snapshot["integrity"]["runtime_log_present"] is False
    assert snapshot["integrity"]["recent_events_emitted"] == 0
