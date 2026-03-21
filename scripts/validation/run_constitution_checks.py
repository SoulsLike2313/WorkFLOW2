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
CANONICAL_NODE_ROOT_POLICY_PATH = ROOT / "docs" / "governance" / "CANONICAL_NODE_ROOT_POLICY_V1.md"
SOVEREIGN_RANK_PROOF_MODEL_PATH = ROOT / "docs" / "governance" / "SOVEREIGN_RANK_PROOF_MODEL_V1.md"
SOVEREIGN_CLAIM_DENIAL_POLICY_PATH = ROOT / "docs" / "governance" / "SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md"
INTER_NODE_DOCUMENT_ARCHITECTURE_PATH = ROOT / "docs" / "governance" / "INTER_NODE_DOCUMENT_ARCHITECTURE_V1.md"
INTER_NODE_DOCUMENT_SCHEMA_PATH = ROOT / "docs" / "governance" / "INTER_NODE_DOCUMENT_SCHEMA_V1.md"
EMPEROR_LOCAL_PROOF_CONTRACT_PATH = ROOT / "workspace_config" / "emperor_local_proof_contract.json"
SHARED_TAXONOMY_CONTRACT_PATH = ROOT / "workspace_config" / "shared_taxonomy_contract.json"
NODE_RANK_SCRIPT = ROOT / "scripts" / "validation" / "detect_node_rank.py"
CLAIM_DENIAL_SCRIPT = ROOT / "scripts" / "validation" / "check_sovereign_claim_denial.py"

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

SEVERITY_ORDER = {
    "INFO": 0,
    "WARNING": 1,
    "SOFT_FAIL": 2,
    "HARD_FAIL": 3,
}

GATE_ACTION_ORDER = {
    "ALLOW": 0,
    "ALLOW_WITH_NOTE": 1,
    "REVIEW_REQUIRED": 2,
    "BLOCK": 3,
}

SEVERITY_GATE_EFFECT = {
    "INFO": {
        "completion_claim": "ALLOW",
        "certification_claim": "ALLOW",
        "mirror_refresh": "ALLOW",
        "phase_transition": "ALLOW",
    },
    "WARNING": {
        "completion_claim": "ALLOW_WITH_NOTE",
        "certification_claim": "REVIEW_REQUIRED",
        "mirror_refresh": "ALLOW_WITH_NOTE",
        "phase_transition": "REVIEW_REQUIRED",
    },
    "SOFT_FAIL": {
        "completion_claim": "BLOCK",
        "certification_claim": "BLOCK",
        "mirror_refresh": "REVIEW_REQUIRED",
        "phase_transition": "BLOCK",
    },
    "HARD_FAIL": {
        "completion_claim": "BLOCK",
        "certification_claim": "BLOCK",
        "mirror_refresh": "BLOCK",
        "phase_transition": "BLOCK",
    },
}


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
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def parse_cmd_json(result: dict[str, Any], label: str) -> tuple[dict[str, Any] | None, list[str]]:
    if result.get("exit_code", 1) != 0:
        return None, [f"{label} command failed: {' '.join(result.get('cmd', []))}"]
    raw = str(result.get("stdout", "")).strip()
    if not raw:
        return None, [f"{label} command returned empty stdout"]
    try:
        return json.loads(raw), []
    except Exception as exc:
        return None, [f"{label} stdout JSON parse failed: {exc}"]


def git_head() -> str | None:
    result = run_cmd(["git", "rev-parse", "HEAD"])
    if result["exit_code"] != 0:
        return None
    out = str(result["stdout_tail"]).strip()
    if not out:
        return None
    return out.splitlines()[-1].strip()


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


def load_claim_probe_from_shared_taxonomy() -> tuple[str, str, list[str]]:
    notes: list[str] = []
    default_probe = "denial_as_expected_claim"
    if not SHARED_TAXONOMY_CONTRACT_PATH.exists():
        return default_probe, "MISSING", [f"shared taxonomy missing: {SHARED_TAXONOMY_CONTRACT_PATH.relative_to(ROOT).as_posix()}"]

    try:
        payload = load_json(SHARED_TAXONOMY_CONTRACT_PATH)
    except Exception as exc:  # pragma: no cover - defensive
        return default_probe, "FAIL", [f"shared taxonomy parse failed: {exc}"]

    claim_classes = payload.get("claim_classes", {})
    primarch_claims = [str(x).strip() for x in claim_classes.get("primarch_allowed_non_sovereign", []) if str(x).strip()]
    astartes_claims = [str(x).strip() for x in claim_classes.get("astartes_allowed_non_sovereign", []) if str(x).strip()]
    sovereign_claims = [str(x).strip() for x in claim_classes.get("sovereign_only", []) if str(x).strip()]

    all_claims = set(primarch_claims) | set(astartes_claims) | set(sovereign_claims)
    if default_probe in all_claims:
        return default_probe, "PASS", notes

    if primarch_claims:
        probe = primarch_claims[0]
        notes.append(f"default probe claim missing in shared taxonomy; using primarch claim: {probe}")
        return probe, "WARNING", notes

    if astartes_claims:
        probe = astartes_claims[0]
        notes.append(f"default probe claim missing in shared taxonomy; using astartes claim: {probe}")
        return probe, "WARNING", notes

    if sovereign_claims:
        probe = sovereign_claims[0]
        notes.append(f"default probe claim missing in shared taxonomy; using sovereign claim: {probe}")
        return probe, "WARNING", notes

    notes.append("shared taxonomy contains no claim classes; using default probe claim")
    return default_probe, "WARNING", notes


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


def load_repo_control() -> tuple[str, str, str, str, list[str]]:
    notes: list[str] = []
    if not RCC_STATUS.exists():
        return "UNKNOWN", "UNKNOWN", "UNKNOWN", "MISSING", ["repo_control_status.json missing"]
    try:
        payload = load_json(RCC_STATUS)
    except Exception as exc:  # pragma: no cover - defensive
        return "UNKNOWN", "UNKNOWN", "UNKNOWN", "PARSE_ERROR", [f"repo_control_status parse failed: {exc}"]

    verdicts = payload.get("verdicts", {})
    sync = str(verdicts.get("sync", {}).get("verdict", "UNKNOWN")).upper()
    trust = str(verdicts.get("trust", {}).get("verdict", "UNKNOWN")).upper()
    governance_acceptance = str(verdicts.get("governance_acceptance", {}).get("verdict", "UNKNOWN")).upper()
    reported_head = str(payload.get("repo", {}).get("head", "")).strip()
    current_head = git_head()

    if reported_head and current_head and reported_head != current_head:
        notes.append(
            "repo_control_status is stale vs current HEAD "
            f"(reported={reported_head[:12]}, current={current_head[:12]})"
        )
        return "UNKNOWN", "UNKNOWN", "UNKNOWN", "STALE", notes

    freshness = "FRESH"
    if sync == "UNKNOWN" or trust == "UNKNOWN" or governance_acceptance == "UNKNOWN":
        notes.append("repo_control_status lacks one or more expected verdict fields")
        freshness = "UNKNOWN_FIELDS"
    return sync, trust, governance_acceptance, freshness, notes


def classify_status_payload(status: dict[str, str], notes: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    unknown_critical: list[str] = []
    checks: list[dict[str, str]] = []

    def add(check_name: str, check_status: str, severity: str, rationale: str) -> None:
        checks.append(
            {
                "check": check_name,
                "status": check_status,
                "severity": severity,
                "rationale": rationale,
            }
        )

    phase = status["constitution_phase"]
    if phase == "constitution-v1-finalized":
        add("constitution_phase", phase, "INFO", "phase claim aligned with finalized Constitution V1 regime")
    elif phase == "constitution-first":
        add("constitution_phase", phase, "WARNING", "phase remains pre-finalization constitution-first")
    elif phase == "unknown":
        add("constitution_phase", phase, "SOFT_FAIL", "current phase claim is missing")
    else:
        add("constitution_phase", phase, "SOFT_FAIL", "phase claim diverges from allowed constitutional phases")

    vocab = status["vocabulary_freeze_status"]
    if vocab == "PASS":
        add("vocabulary_freeze_status", vocab, "INFO", "canonical vocabulary surface exists")
    else:
        add("vocabulary_freeze_status", vocab, "HARD_FAIL", "canonical vocabulary surface missing or invalid")

    truth = status["truth_state_schema_status"]
    if truth == "PASS":
        add("truth_state_schema_status", truth, "INFO", "truth-state schema is present and valid")
    elif truth == "WARNING":
        add("truth_state_schema_status", truth, "WARNING", "truth-state schema has non-blocking deviations")
    else:
        add("truth_state_schema_status", truth, "HARD_FAIL", "truth-state schema is not reliable")

    contradiction = status["contradiction_scan_status"]
    if contradiction == "PASS":
        add("contradiction_scan_status", contradiction, "INFO", "no contradiction class currently failing")
    elif contradiction == "WARNING":
        add("contradiction_scan_status", contradiction, "SOFT_FAIL", "contradiction warning requires review before completion")
    elif contradiction == "FAIL":
        add("contradiction_scan_status", contradiction, "HARD_FAIL", "critical contradiction state detected")
    else:
        add("contradiction_scan_status", contradiction, "SOFT_FAIL", "contradiction scan result unavailable")
        unknown_critical.append("contradiction_scan_status")

    drift = status["registry_doc_drift_status"]
    if drift == "PASS":
        add("registry_doc_drift_status", drift, "INFO", "registry/doc drift guard is green")
    elif drift == "WARNING":
        add("registry_doc_drift_status", drift, "WARNING", "non-critical registry/doc drift detected")
    elif drift == "FAIL":
        add("registry_doc_drift_status", drift, "SOFT_FAIL", "registry/doc drift must be resolved before completion")
    else:
        add("registry_doc_drift_status", drift, "SOFT_FAIL", "registry/doc drift status unavailable")
        unknown_critical.append("registry_doc_drift_status")

    proof = status["proof_output_naming_policy_status"]
    if proof == "PASS":
        add("proof_output_naming_policy_status", proof, "INFO", "proof output naming policy is available")
    else:
        add("proof_output_naming_policy_status", proof, "WARNING", "proof output naming policy missing")

    hygiene = status["hygiene_checklist_status"]
    if hygiene == "PASS":
        add("hygiene_checklist_status", hygiene, "INFO", "hygiene checklist is available")
    else:
        add("hygiene_checklist_status", hygiene, "SOFT_FAIL", "hygiene checklist is missing")

    node_root_policy = status["canonical_node_root_policy_status"]
    if node_root_policy == "PASS":
        add("canonical_node_root_policy_status", node_root_policy, "INFO", "canonical root policy artifact exists")
    else:
        add("canonical_node_root_policy_status", node_root_policy, "WARNING", "canonical root policy artifact missing")

    sovereign_rank_model = status["sovereign_rank_proof_model_status"]
    if sovereign_rank_model == "PASS":
        add("sovereign_rank_proof_model_status", sovereign_rank_model, "INFO", "sovereign rank proof model artifact exists")
    else:
        add("sovereign_rank_proof_model_status", sovereign_rank_model, "WARNING", "sovereign rank proof model missing")

    sovereign_claim_policy = status["sovereign_claim_denial_policy_status"]
    if sovereign_claim_policy == "PASS":
        add("sovereign_claim_denial_policy_status", sovereign_claim_policy, "INFO", "sovereign claim denial policy artifact exists")
    else:
        add("sovereign_claim_denial_policy_status", sovereign_claim_policy, "WARNING", "sovereign claim denial policy missing")

    inter_node_architecture = status["inter_node_document_architecture_status"]
    if inter_node_architecture == "PASS":
        add(
            "inter_node_document_architecture_status",
            inter_node_architecture,
            "INFO",
            "inter-node document architecture artifact exists",
        )
    else:
        add("inter_node_document_architecture_status", inter_node_architecture, "WARNING", "inter-node architecture missing")

    inter_node_schema = status["inter_node_document_schema_status"]
    if inter_node_schema == "PASS":
        add("inter_node_document_schema_status", inter_node_schema, "INFO", "inter-node document schema artifact exists")
    else:
        add("inter_node_document_schema_status", inter_node_schema, "WARNING", "inter-node schema missing")

    emperor_local_proof_contract = status["emperor_local_proof_contract_status"]
    if emperor_local_proof_contract == "PASS":
        add(
            "emperor_local_proof_contract_status",
            emperor_local_proof_contract,
            "INFO",
            "emperor local proof contract artifact exists",
        )
    else:
        add(
            "emperor_local_proof_contract_status",
            emperor_local_proof_contract,
            "WARNING",
            "emperor local proof contract artifact missing",
        )

    taxonomy_contract = status["shared_taxonomy_contract_status"]
    if taxonomy_contract == "PASS":
        add("shared_taxonomy_contract_status", taxonomy_contract, "INFO", "shared taxonomy contract is available")
    elif taxonomy_contract == "WARNING":
        add(
            "shared_taxonomy_contract_status",
            taxonomy_contract,
            "WARNING",
            "shared taxonomy contract is present but probe claim fallback was used",
        )
    else:
        add(
            "shared_taxonomy_contract_status",
            taxonomy_contract,
            "SOFT_FAIL",
            "shared taxonomy contract is missing or invalid",
        )

    node_rank_detection = status["node_rank_detection_status"]
    if node_rank_detection == "PASS":
        add("node_rank_detection_status", node_rank_detection, "INFO", "node rank detection passed with fail-closed logic")
    elif node_rank_detection == "UNKNOWN":
        add("node_rank_detection_status", node_rank_detection, "SOFT_FAIL", "node rank detection unavailable")
    else:
        add("node_rank_detection_status", node_rank_detection, "WARNING", "node rank detection has warnings")

    root_validity = status["canonical_root_validity"]
    if root_validity == "VALID":
        add("canonical_root_validity", root_validity, "INFO", "canonical node root context is valid")
    elif root_validity == "INVALID":
        add("canonical_root_validity", root_validity, "HARD_FAIL", "canonical node root context is invalid")
    else:
        add("canonical_root_validity", root_validity, "SOFT_FAIL", "canonical root validity unknown")

    detected_rank = status["detected_node_rank"]
    if detected_rank in {"EMPEROR", "PRIMARCH", "ASTARTES"}:
        add("detected_node_rank", detected_rank, "INFO", "node rank resolved")
    else:
        add("detected_node_rank", detected_rank, "SOFT_FAIL", "node rank unresolved")

    sovereign_proof = status["sovereign_proof_status"]
    if sovereign_proof in {"VALID", "MISSING_OR_INVALID", "NOT_REQUIRED"}:
        add("sovereign_proof_status", sovereign_proof, "INFO", "sovereign proof state recorded")
    else:
        add("sovereign_proof_status", sovereign_proof, "SOFT_FAIL", "sovereign proof state unknown")

    sovereign_claim_denial = status["sovereign_claim_denial_status"]
    if sovereign_claim_denial in {"ALLOW", "DENY"}:
        add("sovereign_claim_denial_status", sovereign_claim_denial, "INFO", "sovereign claim evaluation recorded")
    else:
        add("sovereign_claim_denial_status", sovereign_claim_denial, "SOFT_FAIL", "sovereign claim evaluation missing")

    freshness = status["repo_control_status_freshness"]
    if freshness == "FRESH":
        add("repo_control_status_freshness", freshness, "INFO", "repo control snapshot aligned with current HEAD")
    elif freshness == "STALE":
        add("repo_control_status_freshness", freshness, "SOFT_FAIL", "refresh repo control status before admission claim")
    elif freshness in {"MISSING", "PARSE_ERROR"}:
        add("repo_control_status_freshness", freshness, "SOFT_FAIL", "repo control snapshot is unavailable")
        unknown_critical.append("repo_control_status_freshness")
    else:
        add("repo_control_status_freshness", freshness, "SOFT_FAIL", "repo control snapshot is incomplete")
        unknown_critical.append("repo_control_status_freshness")

    sync = status["sync_status"]
    if sync == "IN_SYNC":
        add("sync_status", sync, "INFO", "sync parity is clean")
    elif sync in {"DRIFTED", "BLOCKED"}:
        add("sync_status", sync, "HARD_FAIL", "sync state blocks completion and certification")
    elif sync == "UNKNOWN":
        add("sync_status", sync, "SOFT_FAIL", "sync status is unknown")
    else:
        add("sync_status", sync, "SOFT_FAIL", "sync status is non-canonical")

    trust = status["trust_status"]
    if trust == "TRUSTED":
        add("trust_status", trust, "INFO", "trust chain is green")
    elif trust == "NOT_TRUSTED":
        add("trust_status", trust, "HARD_FAIL", "trust chain is broken")
    elif trust in {"WARNING", "UNKNOWN"}:
        add("trust_status", trust, "SOFT_FAIL", "trust state requires review/refresh")
    else:
        add("trust_status", trust, "SOFT_FAIL", "trust status is non-canonical")

    acceptance = status["governance_acceptance"]
    if acceptance == "PASS":
        add("governance_acceptance", acceptance, "INFO", "governance acceptance is open")
    elif acceptance == "FAIL":
        add("governance_acceptance", acceptance, "HARD_FAIL", "governance acceptance gate is closed")
    elif acceptance in {"PARTIAL", "UNKNOWN"}:
        add("governance_acceptance", acceptance, "SOFT_FAIL", "governance acceptance requires refresh/review")
    else:
        add("governance_acceptance", acceptance, "SOFT_FAIL", "governance acceptance is non-canonical")

    for note in notes:
        if "parse failed" in note.lower():
            unknown_critical.append("repo_control_status_freshness")

    unknown_critical = sorted(set(unknown_critical))
    return checks, unknown_critical


def aggregate_gate_actions(checks: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    gates: dict[str, dict[str, Any]] = {}
    gate_names = ["completion_claim", "certification_claim", "mirror_refresh", "phase_transition"]

    for gate in gate_names:
        worst_action = "ALLOW"
        reasons: list[str] = []
        for item in checks:
            severity = item["severity"]
            action = SEVERITY_GATE_EFFECT[severity][gate]
            if GATE_ACTION_ORDER[action] > GATE_ACTION_ORDER[worst_action]:
                worst_action = action
                reasons = [f"{item['check']}({severity})"]
            elif GATE_ACTION_ORDER[action] == GATE_ACTION_ORDER[worst_action] and action != "ALLOW":
                reasons.append(f"{item['check']}({severity})")

        gates[gate] = {
            "action": worst_action,
            "reasons": sorted(set(reasons)),
        }
    return gates


def summarize_verdict(checks: list[dict[str, str]], unknown_critical: list[str]) -> tuple[str, list[str], list[str], dict[str, int]]:
    severity_counts = {"INFO": 0, "WARNING": 0, "SOFT_FAIL": 0, "HARD_FAIL": 0}
    blockers: list[str] = []
    warnings: list[str] = []

    for item in checks:
        sev = item["severity"]
        severity_counts[sev] += 1
        if sev == "HARD_FAIL":
            blockers.append(f"{item['check']}: {item['status']}")
        elif sev in {"SOFT_FAIL", "WARNING"}:
            warnings.append(f"{item['check']}: {item['status']}")

    if severity_counts["HARD_FAIL"] > 0:
        return "FAIL", blockers, warnings, severity_counts
    if unknown_critical:
        blockers.append(f"unknown critical dependencies: {', '.join(unknown_critical)}")
        return "UNKNOWN", blockers, warnings, severity_counts
    if severity_counts["SOFT_FAIL"] > 0 or severity_counts["WARNING"] > 0:
        return "PARTIAL", blockers, warnings, severity_counts
    return "PASS", blockers, warnings, severity_counts


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
        f"- canonical_node_root_policy_status: `{payload['canonical_node_root_policy_status']}`",
        f"- sovereign_rank_proof_model_status: `{payload['sovereign_rank_proof_model_status']}`",
        f"- sovereign_claim_denial_policy_status: `{payload['sovereign_claim_denial_policy_status']}`",
        f"- inter_node_document_architecture_status: `{payload['inter_node_document_architecture_status']}`",
        f"- inter_node_document_schema_status: `{payload['inter_node_document_schema_status']}`",
        f"- emperor_local_proof_contract_status: `{payload['emperor_local_proof_contract_status']}`",
        f"- shared_taxonomy_contract_status: `{payload['shared_taxonomy_contract_status']}`",
        f"- claim_denial_probe_claim_class: `{payload['claim_denial_probe_claim_class']}`",
        f"- node_rank_detection_status: `{payload['node_rank_detection_status']}`",
        f"- detected_node_rank: `{payload['detected_node_rank']}`",
        f"- sovereign_proof_status: `{payload['sovereign_proof_status']}`",
        f"- canonical_root_validity: `{payload['canonical_root_validity']}`",
        f"- sovereign_claim_denial_status: `{payload['sovereign_claim_denial_status']}`",
        f"- repo_control_status_freshness: `{payload['repo_control_status_freshness']}`",
        f"- sync_status: `{payload['sync_status']}`",
        f"- trust_status: `{payload['trust_status']}`",
        f"- governance_acceptance: `{payload['governance_acceptance']}`",
        f"- overall_verdict: `{payload['overall_verdict']}`",
        f"- last_checked_at: `{payload['last_checked_at']}`",
        "",
    ]

    lines.append("## Gate Actions")
    for gate, entry in payload.get("gate_actions", {}).items():
        lines.append(f"- {gate}: `{entry.get('action', 'UNKNOWN')}`")
    lines.append("")

    lines.append("## Severity Counts")
    sev_counts = payload.get("severity_counts", {})
    lines.append(f"- INFO: `{sev_counts.get('INFO', 0)}`")
    lines.append(f"- WARNING: `{sev_counts.get('WARNING', 0)}`")
    lines.append(f"- SOFT_FAIL: `{sev_counts.get('SOFT_FAIL', 0)}`")
    lines.append(f"- HARD_FAIL: `{sev_counts.get('HARD_FAIL', 0)}`")
    lines.append("")

    blockers = payload.get("blockers", [])
    warnings = payload.get("warnings", [])
    notes = payload.get("notes", [])
    unknown_critical = payload.get("unknown_critical_dependencies", [])

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

    lines.append("## Unknown Critical Dependencies")
    if unknown_critical:
        lines.extend([f"- {item}" for item in unknown_critical])
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
    p.add_argument(
        "--write-surfaces",
        action="store_true",
        help=(
            "Persist constitution status surfaces to output paths. "
            "Default behavior is no-write to avoid self-dirtying tracked worktree during verification runs."
        ),
    )
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

    node_rank_result: dict[str, Any] | None = None
    claim_denial_result: dict[str, Any] | None = None
    if NODE_RANK_SCRIPT.exists():
        rank_cmd = run_cmd(
            [
                sys.executable,
                str(NODE_RANK_SCRIPT),
                "--json-only",
                "--no-write",
                "--canonical-root-expected",
                str(ROOT),
            ]
        )
        command_results.append(rank_cmd)
        node_rank_result, node_rank_notes = parse_cmd_json(rank_cmd, "detect_node_rank")
    else:
        node_rank_notes = [f"missing node rank validator: {NODE_RANK_SCRIPT.relative_to(ROOT).as_posix()}"]

    detected_rank = "UNKNOWN"
    canonical_root_valid = "UNKNOWN"
    if node_rank_result:
        detected_rank = str(node_rank_result.get("detected_rank", "UNKNOWN")).upper()
        canonical_root_valid = "VALID" if bool(node_rank_result.get("canonical_root_valid", False)) else "INVALID"

    shared_taxonomy_contract_status, shared_taxonomy_notes = check_file_status(SHARED_TAXONOMY_CONTRACT_PATH)
    claim_probe_class, claim_probe_status, claim_probe_notes = load_claim_probe_from_shared_taxonomy()
    if shared_taxonomy_contract_status == "PASS" and claim_probe_status in {"WARNING", "FAIL", "MISSING"}:
        shared_taxonomy_contract_status = "WARNING"
    if shared_taxonomy_contract_status != "PASS" and claim_probe_status == "PASS":
        shared_taxonomy_contract_status = "WARNING"

    if CLAIM_DENIAL_SCRIPT.exists() and detected_rank != "UNKNOWN":
        claim_cmd = run_cmd(
            [
                sys.executable,
                str(CLAIM_DENIAL_SCRIPT),
                "--json-only",
                "--no-write",
                "--detected-rank",
                detected_rank,
                "--canonical-root-valid",
                "true" if canonical_root_valid == "VALID" else "false",
                "--context-surface",
                "local_runtime",
                "--signature-status",
                "valid",
                "--issuer-identity-status",
                "verified",
                "--signature-assurance",
                "structurally_bound",
                "--warrant-status",
                "not_required",
                "--charter-status",
                "not_required",
                "--claim-class",
                claim_probe_class,
            ]
        )
        command_results.append(claim_cmd)
        claim_denial_result, claim_denial_notes = parse_cmd_json(claim_cmd, "check_sovereign_claim_denial")
    elif not CLAIM_DENIAL_SCRIPT.exists():
        claim_denial_notes = [f"missing sovereign claim validator: {CLAIM_DENIAL_SCRIPT.relative_to(ROOT).as_posix()}"]
    else:
        claim_denial_notes = ["sovereign claim validator skipped: detected rank unknown"]

    notes: list[str] = []
    for result in command_results:
        if result["exit_code"] != 0:
            notes.append(f"command returned non-zero ({result['exit_code']}): {' '.join(result['cmd'])}")

    vocabulary_status, vocabulary_notes = check_file_status(VOCAB_PATH)
    truth_status, truth_notes = check_truth_schema()
    proof_policy_status, proof_policy_notes = check_file_status(PROOF_POLICY_PATH)
    hygiene_status, hygiene_notes = check_file_status(HYGIENE_PATH)
    canonical_node_root_policy_status, canonical_node_root_policy_notes = check_file_status(CANONICAL_NODE_ROOT_POLICY_PATH)
    sovereign_rank_proof_model_status, sovereign_rank_proof_model_notes = check_file_status(SOVEREIGN_RANK_PROOF_MODEL_PATH)
    sovereign_claim_denial_policy_status, sovereign_claim_denial_policy_notes = check_file_status(SOVEREIGN_CLAIM_DENIAL_POLICY_PATH)
    inter_node_document_architecture_status, inter_node_document_architecture_notes = check_file_status(
        INTER_NODE_DOCUMENT_ARCHITECTURE_PATH
    )
    inter_node_document_schema_status, inter_node_document_schema_notes = check_file_status(INTER_NODE_DOCUMENT_SCHEMA_PATH)
    emperor_local_proof_contract_status, emperor_local_proof_contract_notes = check_file_status(
        EMPEROR_LOCAL_PROOF_CONTRACT_PATH
    )
    contradiction_status, contradiction_notes = load_scan_verdict(SCAN_OUTPUT, "canonical_contradiction_scan")
    drift_status, drift_notes = load_scan_verdict(DRIFT_OUTPUT, "registry_doc_drift_guard")
    sync_status, trust_status, governance_acceptance, repo_freshness, repo_notes = load_repo_control()

    node_rank_detection_status = "PASS" if node_rank_result else "UNKNOWN"
    sovereign_proof_status = "MISSING_OR_INVALID"
    sovereign_proof_present = False
    primarch_authority_path_valid = False
    primarch_genome_bundle_valid = False
    if node_rank_result:
        sovereign_proof_status = str(
            node_rank_result.get("proof_status", {}).get("emperor", {}).get("status", "MISSING_OR_INVALID")
        ).upper()
        sovereign_proof_present = bool(node_rank_result.get("sovereign_proof_present", False))
        primarch_authority_path_valid = bool(node_rank_result.get("primarch_authority_path_valid", False))
        primarch_genome_bundle_valid = bool(node_rank_result.get("primarch_genome_bundle_valid", primarch_authority_path_valid))

    sovereign_claim_denial_status = "UNKNOWN"
    sovereign_claim_denial_reason = ""
    sovereign_claim_denial_severity = "INFO"
    sovereign_claim_inputs: list[str] = []
    if claim_denial_result:
        sovereign_claim_denial_status = str(claim_denial_result.get("overall_verdict", "UNKNOWN")).upper()
        sovereign_claim_denial_reason = str(claim_denial_result.get("denial_reason", ""))
        sovereign_claim_denial_severity = str(claim_denial_result.get("claim_severity", "INFO")).upper()
        sovereign_claim_inputs = [str(x) for x in claim_denial_result.get("claim_inputs", [])]

    status_payload: dict[str, Any] = {
        "constitution_phase": detect_phase(),
        "constitution_version": "WORKFLOW2_CONSTITUTION_V1",
        "vocabulary_freeze_status": vocabulary_status,
        "truth_state_schema_status": truth_status,
        "contradiction_scan_status": contradiction_status,
        "registry_doc_drift_status": drift_status,
        "proof_output_naming_policy_status": proof_policy_status,
        "hygiene_checklist_status": hygiene_status,
        "canonical_node_root_policy_status": canonical_node_root_policy_status,
        "sovereign_rank_proof_model_status": sovereign_rank_proof_model_status,
        "sovereign_claim_denial_policy_status": sovereign_claim_denial_policy_status,
        "inter_node_document_architecture_status": inter_node_document_architecture_status,
        "inter_node_document_schema_status": inter_node_document_schema_status,
        "emperor_local_proof_contract_status": emperor_local_proof_contract_status,
        "shared_taxonomy_contract_status": shared_taxonomy_contract_status,
        "claim_denial_probe_claim_class": claim_probe_class,
        "node_rank_detection_status": node_rank_detection_status,
        "detected_node_rank": detected_rank,
        "sovereign_proof_status": sovereign_proof_status,
        "sovereign_proof_present": str(sovereign_proof_present).lower(),
        "primarch_genome_bundle_valid": str(primarch_genome_bundle_valid).lower(),
        "primarch_authority_path_valid": str(primarch_authority_path_valid).lower(),
        "canonical_root_validity": canonical_root_valid,
        "sovereign_claim_denial_status": sovereign_claim_denial_status,
        "sovereign_claim_denial_reason": sovereign_claim_denial_reason,
        "sovereign_claim_denial_severity": sovereign_claim_denial_severity,
        "sovereign_claim_inputs": sovereign_claim_inputs,
        "repo_control_status_freshness": repo_freshness,
        "sync_status": sync_status,
        "trust_status": trust_status,
        "governance_acceptance": governance_acceptance,
        "last_checked_at": now_utc(),
    }

    status_payload["notes"] = (
        vocabulary_notes
        + truth_notes
        + contradiction_notes
        + drift_notes
        + proof_policy_notes
        + hygiene_notes
        + canonical_node_root_policy_notes
        + sovereign_rank_proof_model_notes
        + sovereign_claim_denial_policy_notes
        + inter_node_document_architecture_notes
        + inter_node_document_schema_notes
        + emperor_local_proof_contract_notes
        + shared_taxonomy_notes
        + claim_probe_notes
        + node_rank_notes
        + claim_denial_notes
        + repo_notes
        + notes
        + [
            "primarch_authority_path_valid is kept as compatibility alias; status model v2 uses primarch_genome_bundle_valid as load-bearing indicator"
        ]
    )

    check_assessment, unknown_critical = classify_status_payload(status_payload, status_payload["notes"])
    gate_actions = aggregate_gate_actions(check_assessment)
    overall, blockers, warnings, severity_counts = summarize_verdict(check_assessment, unknown_critical)

    status_payload["check_assessment"] = check_assessment
    status_payload["unknown_critical_dependencies"] = unknown_critical
    status_payload["gate_actions"] = gate_actions
    status_payload["severity_counts"] = severity_counts
    status_payload["overall_verdict"] = overall
    status_payload["blockers"] = blockers
    status_payload["warnings"] = warnings
    status_payload["severity_model_version"] = "constitution_gate_severity_model.v1.0.0"
    status_payload["overall_verdict_logic"] = {
        "PASS": "no hard-fail, no soft-fail, no warning, no unknown-critical dependency",
        "PARTIAL": "no hard-fail; at least one warning or soft-fail",
        "FAIL": "one or more hard-fail checks",
        "UNKNOWN": "unknown-critical dependency blocks reliable decision",
    }
    status_payload["schema_version"] = "constitution_status_surface.v1.2.0"
    status_payload["status_surface_write_mode"] = "write_surfaces" if args.write_surfaces else "no_write_default"
    status_payload["sources"] = [
        "docs/governance/WORKFLOW2_CONSTITUTION_V1.md",
        "docs/governance/WORKFLOW2_CONSTITUTION_V0.md",
        "docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md",
        "docs/governance/TRUTH_STATE_MODEL_V1.md",
        "workspace_config/schemas/truth_state_schema.json",
        "docs/governance/PROOF_OUTPUT_NAMING_POLICY_V1.md",
        "docs/governance/CONSTITUTION_PHASE_HYGIENE_CHECKLIST_V1.md",
        "docs/governance/CANONICAL_NODE_ROOT_POLICY_V1.md",
        "docs/governance/SOVEREIGN_RANK_PROOF_MODEL_V1.md",
        "docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md",
        "docs/governance/INTER_NODE_DOCUMENT_ARCHITECTURE_V1.md",
        "docs/governance/INTER_NODE_DOCUMENT_SCHEMA_V1.md",
        "workspace_config/emperor_local_proof_contract.json",
        "workspace_config/shared_taxonomy_contract.json",
        "scripts/validation/detect_node_rank.py",
        "scripts/validation/check_sovereign_claim_denial.py",
        "runtime/repo_control_center/validation/canonical_contradiction_scan.json",
        "runtime/repo_control_center/validation/registry_doc_drift_report.json",
        "runtime/repo_control_center/repo_control_status.json",
    ]
    status_payload["command_results"] = command_results

    if args.write_surfaces:
        write_json(out_json, status_payload)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(status_payload), encoding="utf-8")
    else:
        status_payload["notes"].append(
            "status surfaces not written (default no-write mode); use --write-surfaces for explicit evidence refresh"
        )
    print(json.dumps(status_payload, ensure_ascii=False, indent=2))

    if overall == "FAIL":
        return 1
    if overall == "UNKNOWN":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
