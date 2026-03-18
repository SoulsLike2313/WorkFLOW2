#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON = ROOT / "runtime" / "repo_control_center" / "constitution_status.json"
DEFAULT_MD = ROOT / "runtime" / "repo_control_center" / "constitution_status.md"

SCAN_OUTPUT = ROOT / "runtime" / "repo_control_center" / "validation" / "canonical_contradiction_scan.json"
DRIFT_OUTPUT = ROOT / "runtime" / "repo_control_center" / "validation" / "registry_doc_drift_report.json"
RCC_STATUS = ROOT / "runtime" / "repo_control_center" / "repo_control_status.json"

VOCAB_PATH = ROOT / "docs" / "governance" / "WORKFLOW2_CANONICAL_VOCABULARY_V1.md"
TRUTH_SCHEMA_PATH = ROOT / "workspace_config" / "schemas" / "truth_state_schema.json"
PROOF_POLICY_PATH = ROOT / "docs" / "governance" / "PROOF_OUTPUT_NAMING_POLICY_V1.md"
HYGIENE_PATH = ROOT / "docs" / "governance" / "CONSTITUTION_PHASE_HYGIENE_CHECKLIST_V1.md"
NEXT_STEP_PATH = ROOT / "docs" / "NEXT_CANONICAL_STEP.md"

REQUIRED_TRUTH_STATES = {
    "fact",
    "hypothesis",
    "proposal",
    "decision",
    "certified_result",
    "stale",
    "rejected",
    "superseded",
    "unknown",
}

PHASE_PATTERN = re.compile(r"current canonical phase:\s*`?([^`\n]+)`?", re.IGNORECASE)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_cmd(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return {
        "cmd": cmd,
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def git_head() -> str | None:
    result = run_cmd(["git", "rev-parse", "HEAD"])
    if result["exit_code"] != 0:
        return None
    return str(result["stdout_tail"]).strip().splitlines()[-1].strip() if str(result["stdout_tail"]).strip() else None


def detect_phase() -> str:
    if not NEXT_STEP_PATH.exists():
        return "unknown"
    text = NEXT_STEP_PATH.read_text(encoding="utf-8-sig")
    m = PHASE_PATTERN.search(text)
    if not m:
        return "unknown"
    return m.group(1).strip().lower()


def check_truth_schema() -> tuple[str, list[str]]:
    warnings: list[str] = []
    if not TRUTH_SCHEMA_PATH.exists():
        return "MISSING", ["truth_state schema file not found"]
    try:
        payload = load_json(TRUTH_SCHEMA_PATH)
    except Exception as exc:  # pragma: no cover - defensive
        return "FAIL", [f"truth_state schema parse failed: {exc}"]

    enum_values = set(payload.get("properties", {}).get("truth_state", {}).get("enum", []))
    missing_states = sorted(REQUIRED_TRUTH_STATES - enum_values)
    if missing_states:
        return "FAIL", [f"truth_state enum missing values: {', '.join(missing_states)}"]

    if enum_values != REQUIRED_TRUTH_STATES:
        extra = sorted(enum_values - REQUIRED_TRUTH_STATES)
        if extra:
            warnings.append(f"truth_state enum has extra values: {', '.join(extra)}")
    return ("WARNING" if warnings else "PASS"), warnings


def check_file_status(path: Path, status_on_exists: str = "PASS") -> tuple[str, list[str]]:
    if path.exists():
        return status_on_exists, []
    return "MISSING", [f"missing file: {path.relative_to(ROOT).as_posix()}"]


def load_scan_verdict(path: Path, label: str) -> tuple[str, list[str]]:
    if not path.exists():
        return "UNKNOWN", [f"{label} output missing: {path.relative_to(ROOT).as_posix()}"]
    try:
        payload = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive
        return "FAIL", [f"{label} output parse failed: {exc}"]
    verdict = str(payload.get("summary", {}).get("verdict", "UNKNOWN")).upper()
    if verdict not in {"PASS", "WARNING", "FAIL"}:
        return "UNKNOWN", [f"{label} verdict unsupported: {verdict}"]
    return verdict, []


def load_repo_control() -> tuple[str, str, str, list[str]]:
    warnings: list[str] = []
    if not RCC_STATUS.exists():
        return "UNKNOWN", "UNKNOWN", "UNKNOWN", ["repo_control_status.json missing"]
    try:
        payload = load_json(RCC_STATUS)
    except Exception as exc:  # pragma: no cover - defensive
        return "UNKNOWN", "UNKNOWN", "UNKNOWN", [f"repo_control_status parse failed: {exc}"]

    verdicts = payload.get("verdicts", {})
    sync = str(verdicts.get("sync", {}).get("verdict", "UNKNOWN")).upper()
    trust = str(verdicts.get("trust", {}).get("verdict", "UNKNOWN")).upper()
    governance_acceptance = str(verdicts.get("governance_acceptance", {}).get("verdict", "UNKNOWN")).upper()
    reported_head = str(payload.get("repo", {}).get("head", "")).strip()
    current_head = git_head()

    if reported_head and current_head and reported_head != current_head:
        warnings.append(
            "repo_control_status is stale vs current HEAD "
            f"(reported={reported_head[:12]}, current={current_head[:12]})"
        )
        return "UNKNOWN", "UNKNOWN", "UNKNOWN", warnings

    if sync == "UNKNOWN" or trust == "UNKNOWN" or governance_acceptance == "UNKNOWN":
        warnings.append("repo_control_status lacks one or more expected verdict fields")
    return sync, trust, governance_acceptance, warnings


def compute_overall(status: dict[str, str]) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []

    if status["truth_state_schema_status"] in {"FAIL", "MISSING"}:
        blockers.append("truth_state_schema_status is not PASS")
    elif status["truth_state_schema_status"] == "WARNING":
        warnings.append("truth_state_schema_status is WARNING")

    if status["vocabulary_freeze_status"] != "PASS":
        blockers.append("vocabulary_freeze_status is not PASS")

    if status["contradiction_scan_status"] == "FAIL":
        blockers.append("contradiction_scan_status is FAIL")
    elif status["contradiction_scan_status"] in {"WARNING", "UNKNOWN"}:
        warnings.append(f"contradiction_scan_status is {status['contradiction_scan_status']}")

    if status["registry_doc_drift_status"] == "FAIL":
        blockers.append("registry_doc_drift_status is FAIL")
    elif status["registry_doc_drift_status"] in {"WARNING", "UNKNOWN"}:
        warnings.append(f"registry_doc_drift_status is {status['registry_doc_drift_status']}")

    if status["proof_output_naming_policy_status"] != "PASS":
        warnings.append("proof_output_naming_policy_status is not PASS")
    if status["hygiene_checklist_status"] != "PASS":
        warnings.append("hygiene_checklist_status is not PASS")

    if status["sync_status"] in {"DRIFTED", "BLOCKED"}:
        blockers.append(f"sync_status is {status['sync_status']}")
    elif status["sync_status"] == "UNKNOWN":
        warnings.append("sync_status is UNKNOWN")

    if status["trust_status"] == "NOT_TRUSTED":
        blockers.append("trust_status is NOT_TRUSTED")
    elif status["trust_status"] in {"WARNING", "UNKNOWN"}:
        warnings.append(f"trust_status is {status['trust_status']}")

    if status["governance_acceptance"] == "FAIL":
        blockers.append("governance_acceptance is FAIL")
    elif status["governance_acceptance"] in {"PARTIAL", "UNKNOWN"}:
        warnings.append(f"governance_acceptance is {status['governance_acceptance']}")

    if blockers:
        return "BLOCKED", blockers, warnings
    if warnings:
        return "PARTIAL", blockers, warnings
    return "PASS", blockers, warnings


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# CONSTITUTION STATUS",
        "",
        f"- constitution_phase: `{payload['constitution_phase']}`",
        f"- constitution_version: `{payload['constitution_version']}`",
        f"- vocabulary_freeze_status: `{payload['vocabulary_freeze_status']}`",
        f"- truth_state_schema_status: `{payload['truth_state_schema_status']}`",
        f"- contradiction_scan_status: `{payload['contradiction_scan_status']}`",
        f"- registry_doc_drift_status: `{payload['registry_doc_drift_status']}`",
        f"- proof_output_naming_policy_status: `{payload['proof_output_naming_policy_status']}`",
        f"- hygiene_checklist_status: `{payload['hygiene_checklist_status']}`",
        f"- sync_status: `{payload['sync_status']}`",
        f"- trust_status: `{payload['trust_status']}`",
        f"- governance_acceptance: `{payload['governance_acceptance']}`",
        f"- overall_verdict: `{payload['overall_verdict']}`",
        f"- last_checked_at: `{payload['last_checked_at']}`",
        "",
    ]

    blockers = payload.get("blockers", [])
    warnings = payload.get("warnings", [])
    notes = payload.get("notes", [])

    lines.append("## Blockers")
    if blockers:
        lines.extend([f"- {item}" for item in blockers])
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Warnings")
    if warnings:
        lines.extend([f"- {item}" for item in warnings])
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Notes")
    if notes:
        lines.extend([f"- {item}" for item in notes])
    else:
        lines.append("- none")
    lines.append("")

    lines.append("## Sources")
    for src in payload.get("sources", []):
        lines.append(f"- `{src}`")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run lightweight constitution checks and aggregate constitution status surface.")
    p.add_argument("--output-json", default=str(DEFAULT_JSON.relative_to(ROOT)), help="Path to constitution status JSON output.")
    p.add_argument("--output-md", default=str(DEFAULT_MD.relative_to(ROOT)), help="Path to constitution status markdown output.")
    p.add_argument("--run-repo-control", action="store_true", help="Also run repo_control_center bundle + full-check before aggregation.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    if not out_json.is_absolute():
        out_json = (ROOT / out_json).resolve()
    if not out_md.is_absolute():
        out_md = (ROOT / out_md).resolve()

    command_results: list[dict[str, Any]] = []

    if args.run_repo_control:
        command_results.append(run_cmd([sys.executable, "scripts/repo_control_center.py", "bundle"]))
        command_results.append(run_cmd([sys.executable, "scripts/repo_control_center.py", "full-check"]))

    command_results.append(
        run_cmd([sys.executable, "scripts/validation/scan_canonical_contradictions.py", "--output", str(SCAN_OUTPUT.relative_to(ROOT))])
    )
    command_results.append(
        run_cmd([sys.executable, "scripts/validation/check_registry_doc_drift.py", "--output", str(DRIFT_OUTPUT.relative_to(ROOT))])
    )

    notes: list[str] = []
    for result in command_results:
        if result["exit_code"] != 0:
            notes.append(f"command returned non-zero ({result['exit_code']}): {' '.join(result['cmd'])}")

    vocabulary_status, vocabulary_notes = check_file_status(VOCAB_PATH)
    truth_status, truth_notes = check_truth_schema()
    proof_policy_status, proof_policy_notes = check_file_status(PROOF_POLICY_PATH)
    hygiene_status, hygiene_notes = check_file_status(HYGIENE_PATH)
    contradiction_status, contradiction_notes = load_scan_verdict(SCAN_OUTPUT, "canonical_contradiction_scan")
    drift_status, drift_notes = load_scan_verdict(DRIFT_OUTPUT, "registry_doc_drift_guard")
    sync_status, trust_status, governance_acceptance, repo_notes = load_repo_control()

    status_payload = {
        "constitution_phase": detect_phase(),
        "constitution_version": "WORKFLOW2_CONSTITUTION_V0",
        "vocabulary_freeze_status": vocabulary_status,
        "truth_state_schema_status": truth_status,
        "contradiction_scan_status": contradiction_status,
        "registry_doc_drift_status": drift_status,
        "proof_output_naming_policy_status": proof_policy_status,
        "hygiene_checklist_status": hygiene_status,
        "sync_status": sync_status,
        "trust_status": trust_status,
        "governance_acceptance": governance_acceptance,
        "last_checked_at": now_utc(),
    }

    overall, blockers, warnings = compute_overall(status_payload)
    status_payload["overall_verdict"] = overall
    status_payload["blockers"] = blockers
    status_payload["warnings"] = warnings
    status_payload["notes"] = (
        vocabulary_notes
        + truth_notes
        + contradiction_notes
        + drift_notes
        + proof_policy_notes
        + hygiene_notes
        + repo_notes
        + notes
    )
    status_payload["sources"] = [
        "docs/governance/WORKFLOW2_CONSTITUTION_V0.md",
        "docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md",
        "docs/governance/TRUTH_STATE_MODEL_V1.md",
        "workspace_config/schemas/truth_state_schema.json",
        "runtime/repo_control_center/validation/canonical_contradiction_scan.json",
        "runtime/repo_control_center/validation/registry_doc_drift_report.json",
        "runtime/repo_control_center/repo_control_status.json",
    ]
    status_payload["schema_version"] = "constitution_status_surface.v1.0.0"
    status_payload["command_results"] = command_results

    write_json(out_json, status_payload)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(status_payload), encoding="utf-8")

    print(json.dumps(status_payload, ensure_ascii=False, indent=2))

    if overall == "BLOCKED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
