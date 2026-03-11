from __future__ import annotations

from app.core.enums import QaSeverity
from app.core.models import QaFinding


def run(entries: list[dict], project_id: int) -> list[QaFinding]:
    findings: list[QaFinding] = []
    for entry in entries:
        source = (entry.get("source_text") or "").strip()
        if not source:
            findings.append(
                QaFinding(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    check_name="missing_source",
                    severity=QaSeverity.ERROR,
                    message="Source text is empty",
                    details={"line_id": entry.get("line_id")},
                )
            )
    return findings
