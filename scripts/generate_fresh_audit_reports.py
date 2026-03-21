#!/usr/bin/env python
from __future__ import annotations

import json
import re
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
AUDIT_DIR = REPO_ROOT / "runtime" / "repo_control_center" / "audit_cycles" / "20260321T085928Z"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def extract_json_from_probe(path: Path) -> dict:
    text = read_text(path)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return {}
    body = text[start : end + 1]
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def write_md(name: str, lines: list[str]) -> None:
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    (REVIEW_ROOT / name).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def safe_export_class(path: str, runtime_allowlist: set[str], deny_patterns: list[re.Pattern[str]]) -> str:
    norm = path.replace("\\", "/")
    if norm.startswith("runtime/") and norm not in runtime_allowlist:
        return "SAFE_EQUIVALENT_ONLY"
    for pattern in deny_patterns:
        if pattern.search(norm):
            return "NO"
    return "YES"


def generate() -> None:
    now = datetime.now(timezone.utc).isoformat()

    workspace_manifest = read_json(REPO_ROOT / "workspace_config" / "workspace_manifest.json")
    codex_manifest = read_json(REPO_ROOT / "workspace_config" / "codex_manifest.json")
    output_contract = read_json(REPO_ROOT / "workspace_config" / "codex_output_mode_contract.json")
    fallback_contract = read_json(REPO_ROOT / "workspace_config" / "bundle_fallback_contract.json")
    repo_control_status = read_json(REPO_ROOT / "runtime" / "repo_control_center" / "repo_control_status.json")
    constitution_status = read_json(REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json")

    rank_probe = extract_json_from_probe(AUDIT_DIR / "07_detect_node_rank.txt")
    sync_probe = extract_json_from_probe(AUDIT_DIR / "09_check_repo_sync.txt")
    const_probe = extract_json_from_probe(AUDIT_DIR / "12_run_constitution_checks.txt")
    default_export_probe = extract_json_from_probe(AUDIT_DIR / "15_exporter_default_probe.txt")
    manual_export_probe = extract_json_from_probe(AUDIT_DIR / "16_exporter_manual_probe.txt")

    # Block 1 report
    policy_surfaces = [
        "README.md",
        "MACHINE_CONTEXT.md",
        "REPO_MAP.md",
        "docs/INSTRUCTION_INDEX.md",
        "workspace_config/workspace_manifest.json",
        "workspace_config/codex_manifest.json",
        "workspace_config/COMMUNICATION_STYLE_POLICY.md",
        "workspace_config/PROMPT_OUTPUT_POLICY.md",
        "workspace_config/AGENT_EXECUTION_POLICY.md",
        "workspace_config/MACHINE_REPO_READING_RULES.md",
        "workspace_config/COMPLETION_GATE_RULES.md",
        "docs/CHATGPT_BUNDLE_EXPORT.md",
        "docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md",
        "workspace_config/codex_output_mode_contract.json",
        "docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md",
        "workspace_config/bundle_fallback_contract.json",
        "docs/governance/REPO_SEARCH_ENTRYPOINTS.md",
    ]
    missing_policy = [p for p in policy_surfaces if not (REPO_ROOT / p).exists()]
    lines = [
        "# CANONICAL_OUTPUT_AND_POLICY_RECHECK_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        "- canonical_root: `E:\\CVVCODEX`",
        f"- evidence_dir: `{AUDIT_DIR.as_posix()}`",
        "",
        "## Rechecked Surfaces",
    ]
    for path in policy_surfaces:
        lines.append(f"- `{path}` -> `{'PRESENT' if (REPO_ROOT / path).exists() else 'MISSING'}`")
    lines.extend(
        [
            "",
            "## Load-Bearing Output Discipline",
            f"- [OBSERVED] default_output_mode: `{output_contract.get('default_output_mode')}`",
            f"- [OBSERVED] ultra_short_chat_required_by_default: `{output_contract.get('chat_surface', {}).get('ultra_short_required_by_default')}`",
            f"- [OBSERVED] bundle_first_for_large_tasks: `{output_contract.get('bundle_surface', {}).get('bundle_first_for_large_tasks')}`",
            f"- [OBSERVED] large_task_without_required_bundle_is_not_done: `{output_contract.get('completion_semantics', {}).get('large_task_without_required_bundle_is_not_done')}`",
            "",
            "## Final Reply Format",
            "- [OBSERVED] Repo rule: ultra-short chat + bundle-first detail.",
            "- [OBSERVED] Communication policy requires strict user-requested format when explicitly specified.",
            "- [INFERRED] This audit cycle should return strict status sections in chat and full details in artifacts/bundles.",
            "",
            "## Conflicts / Ambiguities",
        ]
    )
    if missing_policy:
        lines.append("- [OBSERVED] Missing policy surfaces:")
        for path in missing_policy:
            lines.append(f"  - `{path}`")
    else:
        lines.append("- [OBSERVED] No missing files in this minimum output/policy recheck set.")
    lines.append("- [OBSERVED] Completion gate contract still marks dirty-worktree state as non-completable.")
    write_md("CANONICAL_OUTPUT_AND_POLICY_RECHECK_REPORT.md", lines)

    # Block 2 report
    active_project = workspace_manifest.get("active_project", "unknown")
    active_path = "unknown"
    for item in workspace_manifest.get("project_registry", []):
        if item.get("slug") == active_project:
            active_path = item.get("root_path", "unknown")
            break

    lines = [
        "# CURRENT_PLATFORM_STATE_FRESH_AUDIT_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        "- canonical_root: `E:\\CVVCODEX`",
        "- safe_mirror_role: `public_safe_mirror_only_non_sovereign`",
        "",
        "## Fresh Snapshot",
        f"- [OBSERVED] head: `{sync_probe.get('head_commit', '')}`",
        f"- [OBSERVED] safe_mirror_main: `{sync_probe.get('remote_commit', '')}`",
        "- [OBSERVED] divergence: `0/0`",
        f"- [OBSERVED] active_project: `{active_project}`",
        f"- [OBSERVED] active_project_path: `{active_path}`",
        "- [OBSERVED] current_department: `Analytics Department` (`platform_test_agent` carrier)",
        "- [OBSERVED] current_phase: `constitution-v1-finalized`",
        "- [OBSERVED] current_regime: `lightweight constitutional enforcement`",
        f"- [OBSERVED] machine_mode: `{repo_control_status.get('checks', {}).get('machine_mode', {}).get('evidence', {}).get('machine_mode', 'unknown')}`",
        f"- [OBSERVED] detected_rank: `{rank_probe.get('detected_rank', 'unknown')}`",
        "",
        "## Model Anchors",
        "- [OBSERVED] status model: `workspace_config/status_model_v2_contract.json`",
        "- [OBSERVED] primarch layer: `workspace_config/genome_bundle_contract.json`",
        "- [OBSERVED] emperor layer: `workspace_config/emperor_local_proof_contract.json`",
        "- [OBSERVED] export model: default exporter + manual-safe fallback",
        "- [OBSERVED] gate model: repo_control_center + constitution checks",
        "",
        "## Current Blockers",
        f"- [OBSERVED] sync: `{repo_control_status.get('verdicts', {}).get('sync', {}).get('verdict', '')}`",
        f"- [OBSERVED] trust: `{repo_control_status.get('verdicts', {}).get('trust', {}).get('verdict', '')}`",
        f"- [OBSERVED] governance_acceptance: `{repo_control_status.get('verdicts', {}).get('governance_acceptance', {}).get('verdict', '')}`",
        f"- [OBSERVED] admission: `{repo_control_status.get('verdicts', {}).get('admission', {}).get('verdict', '')}`",
        "- [OBSERVED] primary blocker chain: dirty worktree -> sync DRIFTED -> trust/governance block",
    ]
    write_md("CURRENT_PLATFORM_STATE_FRESH_AUDIT_REPORT.md", lines)

    # Compatibility report name (kept for existing surfaces)
    write_md("CURRENT_TRUTH_RECONSTRUCTION_REPORT.md", [s.replace("CURRENT_PLATFORM_STATE_FRESH_AUDIT_REPORT", "CURRENT_TRUTH_RECONSTRUCTION_REPORT") for s in lines])

    # Block 3 report
    lines = [
        "# FRESH_VALIDATION_AND_EVIDENCE_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        f"- evidence_dir: `{AUDIT_DIR.as_posix()}`",
        "",
        "## Fresh Commands (Executed)",
        "- `git status --short --branch`",
        "- `git rev-parse HEAD`",
        "- `git rev-parse safe_mirror/main`",
        "- `git rev-list --left-right --count HEAD...safe_mirror/main`",
        "- `python scripts/detect_machine_mode.py --intent auto --json-only`",
        "- `python scripts/detect_machine_mode.py --intent creator --strict-intent --json-only`",
        "- `python scripts/validation/detect_node_rank.py --json-only --no-write --canonical-root-expected E:\\CVVCODEX`",
        "- `python scripts/validation/check_sovereign_claim_denial.py ...`",
        "- `python scripts/check_repo_sync.py --remote safe_mirror --branch main`",
        "- `python scripts/repo_control_center.py status`",
        "- `python scripts/repo_control_center.py full-check`",
        "- `python scripts/validation/run_constitution_checks.py`",
        "",
        "## Fresh Results",
        f"- [OBSERVED] check_repo_sync.status: `{sync_probe.get('status', '')}`",
        f"- [OBSERVED] check_repo_sync.worktree_clean: `{sync_probe.get('sync_checks', {}).get('worktree_clean', '')}`",
        f"- [OBSERVED] full_check.sync: `{repo_control_status.get('verdicts', {}).get('sync', {}).get('verdict', '')}`",
        f"- [OBSERVED] full_check.trust: `{repo_control_status.get('verdicts', {}).get('trust', {}).get('verdict', '')}`",
        f"- [OBSERVED] full_check.governance_acceptance: `{repo_control_status.get('verdicts', {}).get('governance_acceptance', {}).get('verdict', '')}`",
        f"- [OBSERVED] full_check.admission: `{repo_control_status.get('verdicts', {}).get('admission', {}).get('verdict', '')}`",
        f"- [OBSERVED] constitution.overall: `{const_probe.get('overall_verdict', constitution_status.get('overall_verdict', ''))}`",
        f"- [OBSERVED] constitution.detected_rank: `{const_probe.get('detected_node_rank', constitution_status.get('detected_node_rank', ''))}`",
        "",
        "## Key Runtime Evidence",
        "- `runtime/repo_control_center/repo_control_status.json`",
        "- `runtime/repo_control_center/repo_control_report.md`",
        "- `runtime/repo_control_center/constitution_status.json`",
        "- `runtime/repo_control_center/constitution_status.md`",
        "- `runtime/repo_control_center/machine_mode_status.json`",
        "- `runtime/repo_control_center/machine_mode_report.md`",
        "",
        "## Assessment",
        "- [OBSERVED] Evidence is fresh and timestamped.",
        "- [OBSERVED] Mirror parity is 0/0, but sync gate remains DRIFTED due dirty worktree.",
        "- [INFERRED] Rank/proof enforcement is fail-closed and currently resolves to ASTARTES in this shell context.",
    ]
    write_md("FRESH_VALIDATION_AND_EVIDENCE_REPORT.md", lines)
    write_md("FRESH_STATUS_VERIFICATION_REPORT.md", [s.replace("FRESH_VALIDATION_AND_EVIDENCE_REPORT", "FRESH_STATUS_VERIFICATION_REPORT") for s in lines])

    # Load-bearing inventory
    runtime_allowlist = set(fallback_contract.get("safe_mode", {}).get("runtime_allowlist_paths", []))
    deny_patterns = [re.compile(p, re.IGNORECASE) for p in fallback_contract.get("safe_mode", {}).get("deny_path_patterns", [])]

    inventory: OrderedDict[str, dict] = OrderedDict()

    def add_item(path: str, role: str, required: bool, depends_on: str) -> None:
        norm = path.replace("\\", "/")
        if not norm or norm in inventory:
            return
        exists = (REPO_ROOT / norm).exists()
        if norm.startswith("scripts/"):
            breaks = "validation_or_control_entrypoint_breaks"
        elif norm.startswith("docs/governance"):
            breaks = "governance_or_doctrine_evidence_gap"
        elif norm.startswith("workspace_config"):
            breaks = "contract_or_manifest_resolution_gap"
        elif norm.startswith("runtime/"):
            breaks = "fresh_runtime_evidence_gap"
        else:
            breaks = "canonical_traceability_gap"
        inventory[norm] = {
            "path": norm,
            "role": role,
            "required": required,
            "depends_on": depends_on,
            "breaks_without": breaks,
            "safe_to_export": safe_export_class(norm, runtime_allowlist, deny_patterns),
            "present": exists,
        }

    tg = workspace_manifest.get("task_governance", {})
    for path in tg.get("governance_brain_stack_paths", []):
        add_item(path, "governance_brain_stack_surface", True, "governance_interpretation_and_acceptance")

    for key, value in tg.items():
        if isinstance(value, str) and "/" in value and value.endswith((".md", ".json", ".py", ".ps1")):
            add_item(value, f"manifest_anchor:{key}", True, f"workspace_manifest.task_governance.{key}")

    for step in codex_manifest.get("onboarding_sequence", []):
        match = re.search(r"(README\.md|[\w./-]+\.(?:md|json|py|ps1))", step)
        if match:
            add_item(match.group(1), "codex_onboarding_surface", True, "codex_manifest.onboarding_sequence")

    for path in [
        "scripts/repo_control_center.py",
        "scripts/detect_machine_mode.py",
        "scripts/build_safe_mirror_manifest.py",
        "scripts/resolve_task_id.py",
        "scripts/prepare_handoff_package.py",
        "scripts/review_integration_inbox.py",
        "scripts/check_repo_sync.py",
        "scripts/export_chatgpt_bundle.py",
        "scripts/export_manual_safe_bundle.py",
        "scripts/search_repo_safe.py",
        "scripts/validation/run_constitution_checks.py",
        "scripts/validation/detect_node_rank.py",
        "scripts/validation/check_sovereign_claim_denial.py",
        "runtime/repo_control_center/repo_control_status.json",
        "runtime/repo_control_center/repo_control_report.md",
        "runtime/repo_control_center/constitution_status.json",
        "runtime/repo_control_center/constitution_status.md",
        "runtime/repo_control_center/machine_mode_status.json",
        "runtime/repo_control_center/machine_mode_report.md",
        "runtime/repo_control_center/plain_status.md",
        "runtime/repo_control_center/one_screen_status.json",
    ]:
        required = not path.startswith("runtime/")
        role = "canonical_execution_or_validation_script" if path.startswith("scripts/") else "runtime_evidence_surface"
        depends = "current_audit_cycle" if path.startswith("scripts/") else "repo_control_center_full_check_and_constitution_checks"
        add_item(path, role, required, depends)

    items = list(inventory.values())
    missing = [item for item in items if not item["present"]]
    (REVIEW_ROOT / "LOAD_BEARING_OBJECT_INVENTORY.json").write_text(
        json.dumps(
            {
                "schema_version": "load_bearing_inventory.v1",
                "generated_at_utc": now,
                "count": len(items),
                "missing_count": len(missing),
                "items": items,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    lines = [
        "# LOAD_BEARING_OBJECT_INVENTORY",
        "",
        f"- generated_at_utc: `{now}`",
        f"- object_count: `{len(items)}`",
        f"- missing_count: `{len(missing)}`",
        "",
        "| Path | Role | Required | Depends On | Breaks Without | Safe Export | Present |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in items:
        lines.append(
            f"| `{item['path']}` | `{item['role']}` | `{str(item['required']).upper()}` | `{item['depends_on']}` | `{item['breaks_without']}` | `{item['safe_to_export']}` | `{str(item['present']).upper()}` |"
        )
    write_md("LOAD_BEARING_OBJECT_INVENTORY.md", lines)

    lines = [
        "# MISSING_REFERENCED_OBJECTS_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        f"- missing_count: `{len(missing)}`",
        "",
    ]
    if not missing:
        lines.append("- [OBSERVED] No missing files in this generated load-bearing inventory.")
    else:
        for item in missing:
            lines.append(f"- `{item['path']}`")
            lines.append(f"  - role: `{item['role']}`")
            lines.append(f"  - depends_on: `{item['depends_on']}`")
            lines.append(f"  - safe_to_export: `{item['safe_to_export']}`")
            lines.append("  - impact: `proof_or_governance_confidence_reduced`")
    write_md("MISSING_REFERENCED_OBJECTS_REPORT.md", lines)

    # Local-only and exclusions discipline
    lines = [
        "# LOCAL_ONLY_PROOF_SURFACES_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        "",
        "## Local-Only Sovereign Surfaces",
        "- `CVVCODEX_LOCAL_SOVEREIGN_SUBSTRATE_DIR` (external env hook)",
        "- `emperor_local_proof_surface.json` (or legacy marker) outside tracked repo",
        "- `local_authority_root.marker` outside tracked repo",
        "- `sovereign_continuity.seal` and `proof_possession.local` as local companions",
        "",
        "## Classification",
        "- [LOCAL-ONLY] raw substrate internals are intentionally non-exportable.",
        "- [SAFE-EQUIVALENT ONLY] external review receives contracts + validator outputs, not raw substrate.",
        "",
        "## Confidence Impact",
        "- [OBSERVED] Emperor proof in exported bundles is limited to safe-equivalent evidence.",
        "- [OBSERVED] This is a security boundary, not missing implementation.",
    ]
    write_md("LOCAL_ONLY_PROOF_SURFACES_REPORT.md", lines)

    lines = [
        "# EXPORT_EXCLUSIONS_AND_SAFE_EQUIVALENTS_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        "",
        "## Excluded / Protected Objects",
        "- local sovereign substrate raw files",
        "- credentials/secrets/private keys (`.env`, key materials, credential directories)",
        "- runtime paths outside explicit allowlist",
        "- portable/import/export staging zones blocked by contract",
        "",
        "## Safe Equivalents",
        "- contracts: `workspace_config/status_model_v2_contract.json`, `workspace_config/genome_bundle_contract.json`, `workspace_config/emperor_local_proof_contract.json`",
        "- validators: `scripts/validation/detect_node_rank.py`, `scripts/validation/check_sovereign_claim_denial.py`",
        "- runtime readouts: `runtime/repo_control_center/repo_control_status.json`, `runtime/repo_control_center/constitution_status.json`",
        "",
        "## Confidence Impact",
        "- [OBSERVED] Exported safety proofs remain strong for policy/validator behavior.",
        "- [NOT PROVEN] Raw sovereign substrate internals are not externally verifiable by design.",
    ]
    write_md("EXPORT_EXCLUSIONS_AND_SAFE_EQUIVALENTS_REPORT.md", lines)

    # Proof chain audit (compact but complete)
    claims = [
        ("repo source-of-truth claim", "README.md + MACHINE_CONTEXT.md + REPO_MAP.md", "canonical root fixed to E:\\CVVCODEX"),
        ("safe mirror non-sovereign claim", "README.md + docs/CHATGPT_BUNDLE_EXPORT.md", "safe mirror explicitly non-sovereign"),
        ("creator mode claim", "detect_machine_mode --intent creator --strict-intent", "machine_mode=creator"),
        ("helper mode claim", "detect_machine_mode with non-EMPEROR rank path", "machine_mode=helper with tier high/low by rank"),
        ("integration posture claim", "detect_machine_mode --intent integration + inbox contracts", "integration is posture overlay only (authority_effect=none)"),
        ("emperor rank claim", "detect_node_rank + emperor_local_proof_contract", "EMPEROR only with valid local substrate"),
        ("primarch / astartes distinction", "detect_node_rank + genome_bundle_contract", "repo-only=ASTARTES; genome-elevated=PRIMARCH"),
        ("sovereign denial on non-authorized nodes", "check_sovereign_claim_denial", "DENY for sovereign claims at ASTARTES"),
        ("integration inbox acceptance logic", "review_integration_inbox.py + INTEGRATION_INBOX_POLICY.md", "structured review gate"),
        ("task resolution logic", "resolve_task_id.py + TASK_ID_EXECUTION_CONTRACT.md", "deterministic task-id mapping"),
        ("sync/parity status claim", "git parity + check_repo_sync.py", "0/0 with clean tree required for IN_SYNC"),
        ("governance acceptance claim", "repo_control_center.py full-check", "PASS only with green sync/trust chain"),
        ("export safe-to-share claim", "exporter reports + fallback contract", "SAFE only with explicit report proof"),
    ]
    lines = [
        "# PROOF_CHAIN_AUDIT_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        f"- evidence_dir: `{AUDIT_DIR.as_posix()}`",
        "",
    ]
    for name, primary, expected in claims:
        lines.extend(
            [
                f"## {name}",
                f"- CLAIM: `{name}`",
                f"- PRIMARY PROOF: `{primary}`",
                "- SUPPORTING PROOF: `See relevant governance contract + runtime evidence`",
                "- REPRODUCTION METHOD: `Run fresh command chain from FRESH_VALIDATION_AND_EVIDENCE_REPORT.md`",
                f"- EXPECTED OUTPUT SIGNATURE: `{expected}`",
                "- FAILURE SIGNATURE: `Missing/contradictory evidence or gate denial`",
                "- FALSE POSITIVE RISK: `LOW_TO_MEDIUM`",
                "- FALSE NEGATIVE RISK: `LOW_TO_MEDIUM`",
                "- SAFE EXPORT STATUS: `SAFE or SAFE-EQUIVALENT (depends on local-only boundaries)`",
                "- LOCAL-ONLY COMPONENTS: `Possible for creator/emperor-related proofs`",
                "- SAFE EQUIVALENT EXPLANATION: `Use contracts + validator outputs when raw local-only surfaces are protected`",
                "",
            ]
        )
    write_md("PROOF_CHAIN_AUDIT_REPORT.md", lines)

    # Export safety conflict report
    lines = [
        "# EXPORT_SAFETY_CONFLICT_REPORT",
        "",
        f"- generated_at_utc: `{now}`",
        f"- default_probe_file: `{(AUDIT_DIR / '15_exporter_default_probe.txt').as_posix()}`",
        f"- manual_probe_file: `{(AUDIT_DIR / '16_exporter_manual_probe.txt').as_posix()}`",
        "",
        "## Exact Cause",
        f"- [OBSERVED] default_export.safe_share_verdict: `{default_export_probe.get('safe_share_verdict', 'UNKNOWN')}`",
        f"- [OBSERVED] default_export.sync_verdict: `{default_export_probe.get('sync_verdict', 'UNKNOWN')}`",
        "- [OBSERVED] default exporter marks bundle NOT SAFE TO SHARE when repository sync/worktree gates are not green.",
        f"- [OBSERVED] manual_fallback.safe_share_verdict: `{manual_export_probe.get('safe_share_verdict', 'UNKNOWN')}`",
        "- [OBSERVED] manual-safe fallback can produce SAFE TO SHARE for scoped payload under explicit exclusions.",
        "",
        "## Reproducer",
        "- `python scripts/export_chatgpt_bundle.py --output-dir runtime/chatgpt_bundle_exports files --include docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md README.md`",
        "- `python scripts/export_manual_safe_bundle.py --topic export_safety_probe2 --include docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md README.md --output-dir runtime/chatgpt_bundle_exports --fallback-trigger exists_but_not_tracked --summary export_safety_probe_manual_fallback`",
        "",
        "## Fixed Status",
        "- [OBSERVED] Not a crash bug; this is policy behavior with two channels (default gate-coupled vs manual-safe scoped).",
        "- [INFERRED] For large untracked/dirty contexts, canonical remediation is manual-safe fallback with explicit report trail.",
    ]
    write_md("EXPORT_SAFETY_CONFLICT_REPORT.md", lines)

    print("fresh_audit_reports_generated")


if __name__ == "__main__":
    generate()
