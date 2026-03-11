from __future__ import annotations

from app.core.enums import QaSeverity
from app.core.models import QaFinding


def run(entries: list[dict], project_id: int) -> list[QaFinding]:
    findings: list[QaFinding] = []
    for entry in entries:
        has_voice = bool(entry.get("has_voice_link"))
        voice_status = entry.get("voice_status", "pending")
        if has_voice and voice_status in {"pending", "failed", "skipped"}:
            findings.append(
                QaFinding(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    check_name="voice_not_generated",
                    severity=QaSeverity.INFO,
                    message="Voice link exists but Russian voice attempt is not ready",
                    details={"line_id": entry.get("line_id"), "voice_status": voice_status},
                )
            )
    return findings
