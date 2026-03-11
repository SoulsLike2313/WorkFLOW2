from __future__ import annotations

from app.core.enums import QaSeverity
from app.core.models import QaFinding
from app.normalizers.tag_guard import tags_preserved


def run(entries: list[dict], project_id: int) -> list[QaFinding]:
    findings: list[QaFinding] = []
    for entry in entries:
        source = entry.get("source_text") or ""
        translated = entry.get("translated_text") or ""
        if translated and not tags_preserved(source, translated):
            findings.append(
                QaFinding(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    check_name="tags_mismatch",
                    severity=QaSeverity.WARNING,
                    message="HTML-like tags changed or removed",
                    details={"line_id": entry.get("line_id")},
                )
            )
    return findings
