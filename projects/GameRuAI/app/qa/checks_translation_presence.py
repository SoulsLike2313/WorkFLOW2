from __future__ import annotations

from app.core.enums import QaSeverity
from app.core.models import QaFinding


def run(entries: list[dict], project_id: int) -> list[QaFinding]:
    findings: list[QaFinding] = []
    for entry in entries:
        if not (entry.get("translated_text") or "").strip():
            findings.append(
                QaFinding(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    check_name="translation_missing",
                    severity=QaSeverity.ERROR,
                    message="Translation is missing",
                    details={"line_id": entry.get("line_id")},
                )
            )
    return findings
