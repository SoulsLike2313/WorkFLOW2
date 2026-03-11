from __future__ import annotations

from app.core.enums import QaSeverity
from app.core.models import QaFinding


def run(entries: list[dict], project_id: int) -> list[QaFinding]:
    findings: list[QaFinding] = []
    for entry in entries:
        lang = entry.get("detected_lang")
        conf = float(entry.get("language_confidence") or 0.0)
        if not lang or lang == "unknown":
            findings.append(
                QaFinding(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    check_name="language_unknown",
                    severity=QaSeverity.WARNING,
                    message="Language could not be confidently detected",
                    details={"line_id": entry.get("line_id"), "confidence": conf},
                )
            )
        elif conf < 0.45:
            findings.append(
                QaFinding(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    check_name="language_low_confidence",
                    severity=QaSeverity.INFO,
                    message="Language confidence is low",
                    details={"line_id": entry.get("line_id"), "language": lang, "confidence": conf},
                )
            )
    return findings
