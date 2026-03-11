from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


def build_project_summary(
    *,
    entries: list[dict[str, Any]],
    translations: list[dict[str, Any]],
    translation_report: dict[str, Any],
    voice_attempts: list[dict[str, Any]],
    voice_history: list[dict[str, Any]],
    speaker_groups: list[dict[str, Any]],
    qa_findings: list[dict[str, Any]],
    export_jobs: list[dict[str, Any]],
    companion_sessions: list[dict[str, Any]],
    watched_events: list[dict[str, Any]],
    asset_index: list[dict[str, Any]],
) -> dict[str, Any]:
    language_report = _build_language_report(entries)
    voice_report = _build_voice_report(voice_attempts, voice_history, speaker_groups)
    qa_dashboard = _build_qa_dashboard(qa_findings, entries, export_jobs, translations)
    companion_report = _build_companion_report(companion_sessions, watched_events)
    quality_dashboard = {
        "translation_coverage_rate": translation_report.get("translation_coverage_rate", 0.0),
        "low_quality_translations": translation_report.get("low_quality_count", 0),
        "uncertain_language_rate": translation_report.get("uncertain_language_rate", 0.0),
        "voice_avg_alignment": voice_report.get("avg_alignment_ratio", 0.0),
        "voice_avg_quality": voice_report.get("avg_quality_score", 0.0),
        "qa_error_count": qa_dashboard.get("errors", 0),
        "qa_warning_count": qa_dashboard.get("warnings", 0),
    }

    return {
        "totals": {
            "entries": len(entries),
            "translations": len(translations),
            "voice_attempts": len(voice_attempts),
            "assets": len(asset_index),
        },
        "translation": translation_report,
        "voice": voice_report,
        "language": language_report,
        "qa_dashboard": qa_dashboard,
        "companion": companion_report,
        "quality_dashboard": quality_dashboard,
    }


def _build_language_report(entries: list[dict[str, Any]]) -> dict[str, Any]:
    distribution = Counter(str(row.get("detected_lang") or "unknown") for row in entries)
    by_type = Counter(str(row.get("context_type") or "unknown") for row in entries)
    by_status = Counter(str(row.get("translation_status") or "pending") for row in entries)

    uncertain_lines = [
        {
            "entry_id": row.get("id"),
            "line_id": row.get("line_id"),
            "detected_lang": row.get("detected_lang"),
            "confidence": row.get("language_confidence", 0),
            "file_path": row.get("file_path", ""),
        }
        for row in entries
        if str(row.get("detected_lang") or "unknown") in {"unknown", "mixed"}
        or float(row.get("language_confidence") or 0.0) < 0.75
    ]
    return {
        "distribution": dict(sorted(distribution.items())),
        "by_type": dict(sorted(by_type.items())),
        "by_status": dict(sorted(by_status.items())),
        "uncertain_count": len(uncertain_lines),
        "uncertain_lines": uncertain_lines[:120],
    }


def _build_voice_report(
    attempts: list[dict[str, Any]],
    history: list[dict[str, Any]],
    speaker_groups: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts = Counter(str(row.get("status") or "unknown") for row in attempts)
    synthesis_mode_usage = Counter(
        str((row.get("metadata_json") or {}).get("synthesis_mode") or "unknown") for row in attempts
    )
    alignments = [float((row.get("metadata_json") or {}).get("alignment", {}).get("ratio") or 0.0) for row in attempts]
    qualities = [float(row.get("quality_score") or 0.0) for row in attempts]

    per_speaker = []
    for group in speaker_groups:
        per_speaker.append(
            {
                "speaker_id": group.get("speaker_id"),
                "line_count": group.get("line_count", 0),
                "linked_count": group.get("linked_count", 0),
                "broken_links": group.get("broken_links", 0),
                "avg_confidence": group.get("avg_confidence", 0.0),
            }
        )

    return {
        "attempts_total": len(attempts),
        "history_total": len(history),
        "status_counts": dict(sorted(status_counts.items())),
        "avg_alignment_ratio": round(float(mean(alignments)), 3) if alignments else 0.0,
        "avg_quality_score": round(float(mean(qualities)), 3) if qualities else 0.0,
        "synthesis_mode_usage": dict(sorted(synthesis_mode_usage.items())),
        "per_speaker": per_speaker,
        "success_count": int(status_counts.get("generated", 0)),
        "failure_count": int(status_counts.get("failed", 0)),
    }


def _build_qa_dashboard(
    qa_findings: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    export_jobs: list[dict[str, Any]],
    translations: list[dict[str, Any]],
) -> dict[str, Any]:
    severity_counter = Counter(str(item.get("severity") or "unknown") for item in qa_findings)
    check_counter = Counter(str(item.get("check_name") or "unknown") for item in qa_findings)

    problematic_files = Counter(
        str(item.get("details_json", {}).get("file_path") or item.get("details_json", {}).get("line_id") or "")
        for item in qa_findings
    )
    problematic_files = [(path, count) for path, count in problematic_files.items() if path]
    problematic_files.sort(key=lambda item: (-item[1], item[0]))

    untranslated_lines = len(
        [
            row
            for row in entries
            if not (row.get("translated_text") or "").strip()
            or str(row.get("translation_status") or "") in {"", "pending"}
        ]
    )
    broken_placeholders = int(check_counter.get("placeholders_mismatch", 0))
    broken_tags = int(check_counter.get("tags_mismatch", 0))
    latest_export = export_jobs[0] if export_jobs else None
    export_integrity = _export_integrity(latest_export)

    return {
        "total_findings": len(qa_findings),
        "errors": int(severity_counter.get("error", 0)),
        "warnings": int(severity_counter.get("warning", 0)),
        "info": int(severity_counter.get("info", 0)),
        "broken_placeholders": broken_placeholders,
        "broken_tags": broken_tags,
        "untranslated_lines": untranslated_lines,
        "export_integrity": export_integrity,
        "problematic_files": problematic_files[:60],
    }


def _export_integrity(latest_export: dict[str, Any] | None) -> dict[str, Any]:
    if not latest_export:
        return {"status": "missing", "manifest_exists": False, "diff_exists": False}
    manifest_path = Path(str(latest_export.get("manifest_path") or ""))
    diff_path = Path(str(latest_export.get("diff_report_path") or ""))
    manifest_exists = manifest_path.exists() if str(manifest_path) else False
    diff_exists = diff_path.exists() if str(diff_path) else False
    status = "ok" if manifest_exists and diff_exists else "incomplete"
    return {
        "status": status,
        "job_status": latest_export.get("status", "unknown"),
        "manifest_exists": manifest_exists,
        "diff_exists": diff_exists,
    }


def _build_companion_report(companion_sessions: list[dict[str, Any]], watched_events: list[dict[str, Any]]) -> dict[str, Any]:
    status_counter = Counter(str(item.get("process_status") or "unknown") for item in companion_sessions)
    event_counter = Counter(str(item.get("event_type") or "unknown") for item in watched_events)
    return {
        "sessions_total": len(companion_sessions),
        "session_statuses": dict(sorted(status_counter.items())),
        "watched_events_total": len(watched_events),
        "event_types": dict(sorted(event_counter.items())),
    }

