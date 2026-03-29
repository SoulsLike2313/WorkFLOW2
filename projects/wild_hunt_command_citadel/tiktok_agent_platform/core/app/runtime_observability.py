from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .prompt_lineage import build_prompt_lineage_snapshot


DEFAULT_RUNTIME_LOG_PATH = "runtime/logs/runtime_logs.jsonl"
DEFAULT_VERIFICATION_ROOT = "runtime/verification"
DEFAULT_RUNTIME_OBSERVABILITY_SNAPSHOT_PATH = "runtime/runtime_observability_snapshot.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _read_jsonl_tail(path: Path, *, limit: int = 24) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows[-limit:]


def _short_text(value: str, *, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return f"{text[: max(16, limit - 3)]}..."


def _event_summary(event_name: str, payload: dict[str, Any]) -> str:
    explicit = str(payload.get("summary", "")).strip()
    if explicit:
        return _short_text(explicit)
    pretty = event_name.replace("_", " ").strip() or "runtime event"
    return _short_text(pretty)


def _classify_process_state(*, event_name: str, level: str) -> tuple[str, str]:
    key = str(event_name or "").strip().lower()
    lvl = str(level or "").strip().upper()
    error_tokens = (
        "error",
        "failed",
        "exception",
        "not_ready",
        "degraded",
        "timeout",
        "abort",
    )
    active_tokens = (
        "started",
        "ready",
        "refresh",
        "switch_page",
        "validation",
        "verify",
        "connected",
        "open",
        "processing",
    )
    wait_tokens = (
        "waiting",
        "idle",
        "stopped",
        "shutdown",
    )

    if lvl in {"ERROR", "CRITICAL"} or any(token in key for token in error_tokens):
        return "ERROR", "runtime_error_signal_detected"
    if any(token in key for token in active_tokens):
        return "PROCESSING", "runtime_activity_signal_detected"
    if any(token in key for token in wait_tokens):
        return "WAIT", "runtime_wait_signal_detected"
    return "WAIT", "runtime_signal_not_classified"


def _latest_verify_dir(project_root: Path) -> Path | None:
    verification_root = project_root / DEFAULT_VERIFICATION_ROOT
    if not verification_root.exists():
        return None
    candidates = [item for item in verification_root.glob("verify-*") if item.is_dir()]
    if not candidates:
        return None
    candidates.sort(key=lambda item: item.name, reverse=True)
    return candidates[0]


def _normalize_recent_event(
    *,
    idx: int,
    record: dict[str, Any],
    log_path: Path,
    project_root: Path,
) -> dict[str, Any]:
    event_name = str(record.get("event", "runtime_event")).strip() or "runtime_event"
    level = str(record.get("level", "INFO")).strip().lower() or "info"
    payload = record.get("payload", {}) if isinstance(record.get("payload"), dict) else {}
    occurred_at_utc = str(record.get("timestamp", "")).strip() or _utc_now_iso()
    event_id = f"runtime_{event_name}_{idx:03d}"
    source_path = str(log_path)
    try:
        source_path = str(log_path.relative_to(project_root)).replace("\\", "/")
    except Exception:
        pass
    return {
        "event_id": event_id,
        "event_type": "runtime_activity",
        "occurred_at_utc": occurred_at_utc,
        "severity": level,
        "summary": _event_summary(event_name, payload),
        "event_name": event_name,
        "source_path": source_path,
        "truth_class": "SOURCE_EXACT",
    }


def build_runtime_observability_snapshot(*, project_root: Path, max_events: int = 12) -> dict[str, Any]:
    runtime_log_path = project_root / DEFAULT_RUNTIME_LOG_PATH
    log_tail = _read_jsonl_tail(runtime_log_path, limit=max(8, max_events * 3))
    prompt_lineage = build_prompt_lineage_snapshot(project_root=project_root)
    verify_dir = _latest_verify_dir(project_root)
    verification_summary = _read_json_if_exists(verify_dir / "verification_summary.json") if verify_dir else {}
    readiness_summary = _read_json_if_exists(verify_dir / "readiness_summary.json") if verify_dir else {}

    recent_events = [
        _normalize_recent_event(idx=idx, record=record, log_path=runtime_log_path, project_root=project_root)
        for idx, record in enumerate(log_tail[-max_events:], start=1)
    ]
    recent_events.sort(key=lambda item: _parse_iso(str(item.get("occurred_at_utc", ""))), reverse=True)

    latest_event = recent_events[0] if recent_events else {}
    latest_event_name = str(latest_event.get("event_name", "runtime_idle"))
    latest_level = str(latest_event.get("severity", "info"))
    process_state, process_reason = _classify_process_state(event_name=latest_event_name, level=latest_level)

    latest_payload = {}
    if log_tail and isinstance(log_tail[-1], dict):
        payload = log_tail[-1].get("payload")
        if isinstance(payload, dict):
            latest_payload = payload

    failure_reason = str(latest_payload.get("failure_reason", "")).strip()
    recovery_signal = str(latest_payload.get("recovery_signal", "")).strip()
    if not failure_reason:
        failure_reason = "none" if process_state != "ERROR" else process_reason
    if not recovery_signal:
        recovery_signal = "none" if process_state != "ERROR" else "inspect_runtime_logs"

    operation_code = latest_event_name.upper() if latest_event_name else "RUNTIME_IDLE"
    operation_ru_map = {
        "PROCESSING": "Идет активная операция агента",
        "WAIT": "Агент в ожидании следующей операции",
        "ERROR": "Обнаружен runtime-сбой агента",
    }

    source_paths = {
        "runtime_log_path": str(runtime_log_path),
        "verification_summary_path": str(verify_dir / "verification_summary.json") if verify_dir else "missing",
        "readiness_summary_path": str(verify_dir / "readiness_summary.json") if verify_dir else "missing",
    }

    return {
        "state_id": "tiktok_runtime_observability_v1",
        "generated_at_utc": _utc_now_iso(),
        "truth_class": "DERIVED_CANONICAL",
        "source_mode": "DERIVED_RUNTIME_LOG",
        "process_state": process_state,
        "process_reason": process_reason,
        "current_operation_code": operation_code,
        "current_operation_ru": operation_ru_map.get(process_state, "Состояние работы агента не классифицировано"),
        "latest_change_summary": str(latest_event.get("summary", "runtime log has no events yet")),
        "latest_event_at_utc": str(latest_event.get("occurred_at_utc", "")),
        "failure_reason": failure_reason,
        "recovery_signal": recovery_signal,
        "recent_events": recent_events,
        "prompt_lineage": {
            "active_prompt_state": str(prompt_lineage.get("active_prompt_state", "UNKNOWN")),
            "lineage_id": str(prompt_lineage.get("lineage_id", "UNKNOWN")),
            "trusted_boundary": str(prompt_lineage.get("trusted_boundary", "UNKNOWN")),
            "text_boundary": prompt_lineage.get("text_boundary", {}),
            "truth_class": "SOURCE_EXACT",
        },
        "verification_context": {
            "latest_verify_run_id": str(verification_summary.get("run_id") or readiness_summary.get("run_id") or "unknown"),
            "overall_gate_status": str(verification_summary.get("overall_gate_status", "UNKNOWN")),
            "readiness_status": str(readiness_summary.get("status", "UNKNOWN")),
            "runtime_readiness_stage": str(
                ((verification_summary.get("module_status", {}) or {}).get("runtime_readiness", "UNKNOWN"))
            ),
            "ui_backend_integration_stage": str(
                ((verification_summary.get("module_status", {}) or {}).get("ui_backend_integration", "UNKNOWN"))
            ),
            "service_status_classification_stage": str(
                ((verification_summary.get("module_status", {}) or {}).get("prompt_lineage_observability", "UNKNOWN"))
            ),
            "truth_class": "SOURCE_EXACT",
        },
        "source_paths": source_paths,
        "integrity": {
            "runtime_log_present": runtime_log_path.exists(),
            "runtime_log_events_count": len(log_tail),
            "recent_events_emitted": len(recent_events),
            "verification_context_available": bool(verification_summary) or bool(readiness_summary),
        },
    }


def write_runtime_observability_snapshot(
    *,
    project_root: Path,
    snapshot: dict[str, Any] | None = None,
    path: Path | None = None,
) -> Path:
    target = path or (project_root / DEFAULT_RUNTIME_OBSERVABILITY_SNAPSHOT_PATH)
    payload = snapshot or build_runtime_observability_snapshot(project_root=project_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
