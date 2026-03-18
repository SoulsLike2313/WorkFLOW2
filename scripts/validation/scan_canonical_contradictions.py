#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "runtime" / "repo_control_center" / "validation" / "canonical_contradiction_scan.json"
SCHEMA_VERSION = "canonical_contradiction_scan.v1.0.0"

CANONICAL_SURFACES = [
    "docs/CURRENT_PLATFORM_STATE.md",
    "docs/NEXT_CANONICAL_STEP.md",
    "README.md",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    "docs/INSTRUCTION_INDEX.md",
]

STALE_PATTERNS = [
    "next-step-operator-mission-layer-v1",
    "next active layer: `work package / mission layer v1`",
    "next active layer: work package / mission layer v1",
]

PHASE_PATTERNS = [
    re.compile(r"current canonical phase:\s*`?([^`\n]+)`?", re.IGNORECASE),
    re.compile(r"current phase:\s*`?([^`\n]+)`?", re.IGNORECASE),
]

ALLOWED_PHASES = {
    "constitution-first",
    "constitution-v1-finalized",
}

NEXT_STEP_ID_PATTERN = re.compile(r"step_id:\s*`([^`]+)`", re.IGNORECASE)
NEXT_STEP_LABEL_PATTERN = re.compile(r"canonical next execution step is:\s*[\r\n]+\s*`([^`]+)`", re.IGNORECASE)
MISSION_ACCEPTED_PATTERN = re.compile(r"(mission layer|work package / mission layer).*accepted", re.IGNORECASE)
MISSION_PENDING_PATTERN = re.compile(
    r"(next active layer|next execution step).*(mission layer|work package / mission layer v1|operator mission layer v1)",
    re.IGNORECASE,
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_value(value: str) -> str:
    return " ".join(value.strip().lower().split())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def find_phase_claim(text: str) -> str | None:
    for pattern in PHASE_PATTERNS:
        m = pattern.search(text)
        if m:
            return normalize_value(m.group(1))
    return None


def find_next_step_claim(text: str) -> str | None:
    m = NEXT_STEP_ID_PATTERN.search(text)
    if m:
        return normalize_value(m.group(1))
    m = NEXT_STEP_LABEL_PATTERN.search(text)
    if m:
        return normalize_value(m.group(1))
    return None


def mission_status_claim(text: str) -> str | None:
    accepted = bool(MISSION_ACCEPTED_PATTERN.search(text))
    pending = bool(MISSION_PENDING_PATTERN.search(text))
    if accepted and pending:
        return "mixed"
    if accepted:
        return "accepted"
    if pending:
        return "pending"
    return None


def find_stale_hits(text: str) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in STALE_PATTERNS if phrase.lower() in lower]


def add_finding(findings: list[dict[str, Any]], severity: str, cls: str, file_path: str, message: str) -> None:
    findings.append(
        {
            "severity": severity,
            "class": cls,
            "file": file_path,
            "message": message,
        }
    )


def run_scan() -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    claims: dict[str, Any] = {
        "phase_claims_by_file": {},
        "next_step_claims_by_file": {},
        "mission_layer_status_by_file": {},
        "stale_phrase_hits": {},
    }

    for rel in CANONICAL_SURFACES:
        path = ROOT / rel
        if not path.exists():
            add_finding(findings, "FAIL", "missing_surface", rel, "canonical surface file is missing")
            continue
        text = read_text(path)

        phase = find_phase_claim(text)
        if phase:
            claims["phase_claims_by_file"][rel] = phase
        else:
            add_finding(findings, "WARNING", "phase_claim_missing", rel, "no explicit current phase claim detected")

        next_step = find_next_step_claim(text)
        if next_step:
            claims["next_step_claims_by_file"][rel] = next_step

        mstatus = mission_status_claim(text)
        if mstatus:
            claims["mission_layer_status_by_file"][rel] = mstatus

        stale_hits = find_stale_hits(text)
        if stale_hits:
            claims["stale_phrase_hits"][rel] = stale_hits
            add_finding(findings, "FAIL", "stale_phrase_detected", rel, f"stale phrase(s): {', '.join(stale_hits)}")

    phase_values = sorted(set(claims["phase_claims_by_file"].values()))
    if len(phase_values) > 1:
        add_finding(findings, "FAIL", "phase_conflict", "*", f"conflicting phase claims: {phase_values}")
    if len(phase_values) == 1 and phase_values[0] not in ALLOWED_PHASES:
        add_finding(findings, "WARNING", "phase_not_allowed", "*", f"detected phase '{phase_values[0]}' not in allowed set")

    next_step_values = sorted(set(claims["next_step_claims_by_file"].values()))
    if len(next_step_values) > 1:
        add_finding(findings, "FAIL", "next_step_conflict", "*", f"conflicting next-step claims: {next_step_values}")

    mission_states = sorted(set(claims["mission_layer_status_by_file"].values()))
    if "mixed" in mission_states:
        add_finding(findings, "FAIL", "mission_status_mixed", "*", "mission layer status contains mixed accepted/pending claim")
    if "accepted" in mission_states and "pending" in mission_states:
        add_finding(findings, "FAIL", "mission_status_conflict", "*", "mission layer status conflicts: accepted and pending")

    fail_count = sum(1 for f in findings if f["severity"] == "FAIL")
    warn_count = sum(1 for f in findings if f["severity"] == "WARNING")
    verdict = "FAIL" if fail_count > 0 else ("WARNING" if warn_count > 0 else "PASS")

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "files_scanned": CANONICAL_SURFACES,
        "claims": claims,
        "findings": findings,
        "summary": {
            "fail_count": fail_count,
            "warning_count": warn_count,
            "verdict": verdict,
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scan canonical narrative surfaces for contradiction classes.")
    p.add_argument("--output", default=str(DEFAULT_OUTPUT.relative_to(ROOT)), help="Path to JSON output report.")
    p.add_argument("--strict-warning", action="store_true", help="Return non-zero for WARNING verdict as well.")
    return p


def main() -> int:
    args = build_parser().parse_args()
    out = Path(args.output).expanduser()
    if not out.is_absolute():
        out = (ROOT / out).resolve()

    payload = run_scan()
    write_json(out, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    verdict = payload["summary"]["verdict"]
    if verdict == "FAIL":
        return 1
    if verdict == "WARNING" and args.strict_warning:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
