from __future__ import annotations

from app.core.enums import QaSeverity
from app.core.models import QaFinding
from app.normalizers.placeholder_guard import placeholders_preserved


def run(entries: list[dict], project_id: int) -> list[QaFinding]:
    findings: list[QaFinding] = []
    for entry in entries:
        source = entry.get("source_text") or ""
        translated = entry.get("translated_text") or ""
        if translated and not placeholders_preserved(source, translated):
            findings.append(
                QaFinding(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    check_name="placeholders_mismatch",
                    severity=QaSeverity.WARNING,
                    message="Not all placeholders are preserved in translation",
                    details={"line_id": entry.get("line_id")},
                )
            )
    return findings
