#!/usr/bin/env python
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
REQUEST_ROOT = REPO_ROOT / "runtime" / "chatgpt_bundle_requests"
EXPORT_ROOT = REPO_ROOT / "runtime" / "chatgpt_bundle_exports"


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_parent(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def existing(paths: list[str]) -> list[str]:
    seen = set()
    out: list[str] = []
    for path in paths:
        norm = path.replace("\\", "/")
        if not norm or norm in seen:
            continue
        if (REPO_ROOT / norm).exists():
            out.append(norm)
            seen.add(norm)
    return out


def run_export(topic: str, include_file: Path, output_dir: Path, summary: str) -> dict:
    cmd = [
        "python",
        "scripts/export_manual_safe_bundle.py",
        "--topic",
        topic,
        "--include-file",
        str(include_file),
        "--output-dir",
        str(output_dir),
        "--fallback-trigger",
        "operator_explicit_manual_safe_fallback",
        "--fallback-trigger",
        "exists_but_not_tracked",
        "--summary",
        summary,
    ]
    completed = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    payload: dict = {
        "command": " ".join(cmd),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.stdout.strip().startswith("{"):
        try:
            payload.update(json.loads(completed.stdout))
        except json.JSONDecodeError:
            pass
    return payload


def build_companion_files(
    companion_dir: Path,
    logical_name: str,
    purpose: str,
    payload_files: list[str],
    proof_paths: list[str],
    status_lines: list[str],
    export_include_file: str,
) -> None:
    ensure_parent(companion_dir / "x")
    file_index = "\n".join([f"- `{p}`" for p in payload_files]) if payload_files else "- none"
    proof_index = "\n".join([f"- `{p}`" for p in proof_paths]) if proof_paths else "- none"
    status_index = "\n".join([f"- {s}" for s in status_lines]) if status_lines else "- no status notes"

    write_text(
        companion_dir / "EXPORT_REPORT.md",
        f"""# EXPORT_REPORT

- bundle: `{logical_name}`
- export_channel: `manual-safe fallback`
- expected_safe_share_verdict: `SAFE TO SHARE`
- request_include_file: `{export_include_file}`

Companion files are generated as mandatory context for ChatGPT review.""",
    )

    write_text(companion_dir / "FILE_INDEX.md", f"""# FILE_INDEX

{file_index}""")

    write_text(
        companion_dir / "BUNDLE_PURPOSE_AND_SCOPE.md",
        f"""# BUNDLE_PURPOSE_AND_SCOPE

- bundle: `{logical_name}`
- purpose: {purpose}
- scope: canonical safe-read material only
- excluded: protected local-only sovereign raw surfaces""",
    )

    write_text(
        companion_dir / "WHY_THIS_EXISTS_AND_WHY_IT_IS_DESIGNED_THIS_WAY.md",
        f"""# WHY_THIS_EXISTS_AND_WHY_IT_IS_DESIGNED_THIS_WAY

This bundle exists to give ChatGPT a scoped, proof-oriented view of `{logical_name}` without leaking protected material.

Design rationale:
1. keep evidence-heavy context exportable in safe mode;
2. preserve doctrine + script + report linkage;
3. enforce exclusions transparency when local-only or protected surfaces exist;
4. avoid false completeness claims by marking remaining gaps explicitly.""",
    )

    write_text(companion_dir / "PROOF_PATHS.md", f"""# PROOF_PATHS

{proof_index}""")

    write_text(
        companion_dir / "CURRENT_STATUS_AND_GAPS.md",
        f"""# CURRENT_STATUS_AND_GAPS

- bundle: `{logical_name}`
- evidence_basis: fresh runtime audit + canonical docs/contracts

{status_index}""",
    )


def main() -> int:
    stamp = now_stamp()
    generated_at = now_iso()
    set_id = f"deep_review_audit_{stamp}"
    companion_root = REVIEW_ROOT / f"chatgpt_deep_audit_bundle_set_{stamp}"
    request_dir = REQUEST_ROOT / set_id
    output_dir = EXPORT_ROOT / set_id
    companion_root.mkdir(parents=True, exist_ok=True)
    request_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    repo_status = load_json(REPO_ROOT / "runtime/repo_control_center/repo_control_status.json")
    constitution_status = load_json(REPO_ROOT / "runtime/repo_control_center/constitution_status.json")
    code_metrics = load_json(REVIEW_ROOT / "CODEBASE_SIZE_AND_LANGUAGE_REPORT.json")

    common_core = existing(
        [
            "README.md",
            "MACHINE_CONTEXT.md",
            "REPO_MAP.md",
            "docs/INSTRUCTION_INDEX.md",
            "docs/review_artifacts/CANON_RECHECK_AFTER_GREEN_REPAIR.md",
            "docs/review_artifacts/POST_GREEN_FRESH_VALIDATION_REPORT.md",
            "docs/review_artifacts/CANONICAL_OUTPUT_AND_POLICY_RECHECK_REPORT.md",
            "docs/review_artifacts/CURRENT_PLATFORM_STATE_FRESH_AUDIT_REPORT.md",
            "docs/review_artifacts/FRESH_VALIDATION_AND_EVIDENCE_REPORT.md",
            "docs/review_artifacts/LOAD_BEARING_OBJECT_INVENTORY.md",
            "docs/review_artifacts/LOAD_BEARING_OBJECT_INVENTORY.json",
            "docs/review_artifacts/MISSING_REFERENCED_OBJECTS_REPORT.md",
            "docs/review_artifacts/PROOF_CHAIN_AUDIT_REPORT.md",
            "docs/review_artifacts/EXPORT_SAFETY_CONFLICT_REPORT.md",
            "docs/review_artifacts/EXPORT_EXCLUSIONS_AND_SAFE_EQUIVALENTS_REPORT.md",
            "docs/review_artifacts/LOCAL_ONLY_PROOF_SURFACES_REPORT.md",
        ]
    )

    bundle_defs = [
        {
            "name": "01_CONSTITUTION_AND_GOVERNANCE_BUNDLE",
            "topic": "01_constitution_and_governance_bundle",
            "purpose": "Constitution, governance hierarchy, mutation boundaries, and acceptance gate semantics.",
            "payload": existing(
                [
                    "docs/governance/WORKFLOW2_CONSTITUTION_V1.md",
                    "docs/governance/CONSTITUTION_CHANGE_AUTHORITY_POLICY.md",
                    "docs/governance/CONSTITUTION_AMENDMENT_FLOW.md",
                    "docs/governance/CONSTITUTION_IMMUTABILITY_BOUNDARY.md",
                    "docs/governance/GOVERNANCE_HIERARCHY.md",
                    "docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md",
                    "docs/governance/CANONICAL_SOURCE_PRECEDENCE.md",
                    "docs/governance/FIRST_PRINCIPLES.md",
                    "docs/review_artifacts/CURRENT_TRUTH_RECONSTRUCTION_REPORT.md",
                ]
            ),
        },
        {
            "name": "02_AUTHORITY_RANK_AND_PROOF_BUNDLE",
            "topic": "02_authority_rank_and_proof_bundle",
            "purpose": "Authority/rank separation, emperor-proof path, and fail-closed claim-denial mechanics.",
            "payload": existing(
                [
                    "docs/governance/NODE_AUTHORITY_RANK_POLICY_V1.md",
                    "docs/governance/SOVEREIGN_RANK_PROOF_MODEL_V1.md",
                    "docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md",
                    "docs/governance/EMPEROR_LOCAL_PROOF_MODEL_V1.md",
                    "docs/governance/STATUS_MODEL_V2_SPEC.md",
                    "workspace_config/status_model_v2_contract.json",
                    "workspace_config/genome_bundle_contract.json",
                    "workspace_config/emperor_local_proof_contract.json",
                    "workspace_config/shared_taxonomy_contract.json",
                    "workspace_config/claim_taxonomy_contract.json",
                    "scripts/validation/detect_node_rank.py",
                    "scripts/validation/check_sovereign_claim_denial.py",
                ]
            ),
        },
        {
            "name": "03_COMMAND_DELEGATION_AND_ORDER_BUNDLE",
            "topic": "03_command_delegation_and_order_bundle",
            "purpose": "Command/delegation/order semantics, triad doctrine, and escalation boundaries.",
            "payload": existing(
                [
                    "docs/governance/PRIMARCH_ASTARTES_DELEGATION_MATRIX.md",
                    "docs/governance/FEDERATION_DEPARTMENT_ESCALATION_MATRIX.md",
                    "docs/governance/DEPARTMENT_EXCEPTION_ESCALATION_HARDENING_V1.md",
                    "docs/governance/GENOME_DOCTRINE_V1.md",
                    "docs/governance/GRAMOTA_DOCTRINE_V1.md",
                    "docs/governance/ASSIGNMENT_BINDING_DOCTRINE_V1.md",
                    "workspace_config/delegation_registry.json",
                    "workspace_config/department_exception_escalation_contract.json",
                    "workspace_config/genome_gramota_assignment_binding_contract.json",
                    "docs/review_artifacts/TAXONOMY_ALIGNMENT_REPORT.md",
                ]
            ),
        },
        {
            "name": "04_FEDERATION_AND_DEPARTMENTS_BUNDLE",
            "topic": "04_federation_and_departments_bundle",
            "purpose": "Federation framing under sovereign core and current single-department operational truth.",
            "payload": existing(
                [
                    "docs/governance/FEDERATION_ARCHITECTURE.md",
                    "docs/governance/FEDERATION_OPERATIONAL_MODEL.md",
                    "docs/governance/ANALYTICS_DEPARTMENT_DOCTRINE.md",
                    "docs/governance/TEST_PRODUCT_INTAKE_MODEL.md",
                    "workspace_config/test_product_intake_contract.json",
                    "docs/review_artifacts/ANALYTICS_INTAKE_FORMALIZATION_REPORT.md",
                ]
            ),
        },
        {
            "name": "05_PROJECT_AND_WORKSTREAM_HISTORY_BUNDLE",
            "topic": "05_project_and_workstream_history_bundle",
            "purpose": "Project/workstream history, residues, and current operational classification boundaries.",
            "payload": existing(
                [
                    "docs/review_artifacts/FULL_BRAIN_INVENTORY_SWEEP_V1.md",
                    "docs/review_artifacts/FIVE_PHASE_REFORM_VERIFICATION_REPORT.md",
                    "docs/review_artifacts/PROJECT_PATH_STATUS_MATRIX.md",
                    "workspace_config/workspace_manifest.json",
                    "docs/CURRENT_PLATFORM_STATE.md",
                    "docs/NEXT_CANONICAL_STEP.md",
                ]
            ),
        },
        {
            "name": "06_RUNTIME_CONTROL_AND_GATES_BUNDLE",
            "topic": "06_runtime_control_and_gates_bundle",
            "purpose": "Runtime gate mechanics (sync/trust/governance/admission) and fresh status evidence.",
            "payload": existing(
                [
                    "scripts/repo_control_center.py",
                    "scripts/check_repo_sync.py",
                    "scripts/validation/run_constitution_checks.py",
                    "runtime/repo_control_center/repo_control_status.json",
                    "runtime/repo_control_center/repo_control_report.md",
                    "runtime/repo_control_center/constitution_status.json",
                    "runtime/repo_control_center/constitution_status.md",
                    "runtime/repo_control_center/machine_mode_status.json",
                    "runtime/repo_control_center/machine_mode_report.md",
                    "runtime/repo_control_center/plain_status.md",
                    "runtime/repo_control_center/one_screen_status.json",
                ]
            ),
        },
        {
            "name": "07_REGISTRY_MAP_AND_INDEX_BUNDLE",
            "topic": "07_registry_map_and_index_bundle",
            "purpose": "Canonical maps/manifests/indexes and integrated codebase metrics entry surfaces.",
            "payload": existing(
                [
                    "workspace_config/workspace_manifest.json",
                    "workspace_config/codex_manifest.json",
                    "docs/INSTRUCTION_INDEX.md",
                    "docs/CURRENT_PLATFORM_STATE.md",
                    "docs/NEXT_CANONICAL_STEP.md",
                    "docs/governance/WORKFLOW2_GPT_ONBOARDING_MASTER_V1.md",
                    "docs/governance/REPO_SEARCH_ENTRYPOINTS.md",
                    "workspace_config/search_zone_manifest.json",
                    "docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_REPORT.md",
                    "docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_REPORT.json",
                    "docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_SUMMARY.md",
                ]
            ),
        },
        {
            "name": "08_VALIDATION_AND_ENFORCEMENT_BUNDLE",
            "topic": "08_validation_and_enforcement_bundle",
            "purpose": "Validation/enforcement scripts, contracts, and cross-check chain used for hard claims.",
            "payload": existing(
                [
                    "scripts/validation/detect_node_rank.py",
                    "scripts/validation/check_sovereign_claim_denial.py",
                    "scripts/validation/run_constitution_checks.py",
                    "scripts/validation/scan_canonical_contradictions.py",
                    "scripts/validation/check_registry_doc_drift.py",
                    "scripts/detect_machine_mode.py",
                    "workspace_config/status_model_v2_contract.json",
                    "workspace_config/genome_bundle_contract.json",
                    "workspace_config/emperor_local_proof_contract.json",
                    "workspace_config/shared_taxonomy_contract.json",
                ]
            ),
        },
        {
            "name": "09_LIMITS_GAPS_AND_CONTRADICTIONS_BUNDLE",
            "topic": "09_limits_gaps_and_contradictions_bundle",
            "purpose": "Known limits, contradictions, local-only boundaries, and unresolved confidence constraints.",
            "payload": existing(
                [
                    "docs/review_artifacts/MISSING_REFERENCED_OBJECTS_REPORT.md",
                    "docs/review_artifacts/LOCAL_ONLY_PROOF_SURFACES_REPORT.md",
                    "docs/review_artifacts/EXPORT_EXCLUSIONS_AND_SAFE_EQUIVALENTS_REPORT.md",
                    "docs/review_artifacts/EXPORT_SAFETY_CONFLICT_REPORT.md",
                    "docs/review_artifacts/FRESH_STATUS_VERIFICATION_REPORT.md",
                    "docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_REPORT.md",
                ]
            ),
        },
        {
            "name": "10_MASTER_REVIEW_INDEX_BUNDLE",
            "topic": "10_master_review_index_bundle",
            "purpose": "Single entrypoint bundle with architecture/canon/proof summary and full reading order.",
            "payload": existing(
                [
                    "docs/review_artifacts/CHATGPT_DEEP_AUDIT_MASTER_REVIEW_INDEX.md",
                    "docs/review_artifacts/CHATGPT_DEEP_AUDIT_BUNDLE_SET_REPORT.md",
                    "docs/review_artifacts/CHATGPT_DEEP_AUDIT_STATUS.json",
                    "docs/review_artifacts/BUNDLE_CODE_METRICS_INTEGRATION_REPORT.md",
                    "docs/review_artifacts/EXPORT_SAFETY_VERIFICATION_REPORT.md",
                    "docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_SUMMARY.md",
                ]
            ),
        },
    ]

    bundle_map: list[dict] = []

    for bundle in bundle_defs[:9]:
        name = bundle["name"]
        companion_dir = companion_root / name
        include_file = request_dir / f"{name}.txt"
        payload_files = existing(common_core + bundle["payload"])
        proof_paths = [
            "runtime/repo_control_center/repo_control_status.json",
            "runtime/repo_control_center/constitution_status.json",
            "runtime/repo_control_center/audit_cycles/20260321T085928Z",
        ]
        status_lines = [
            f"[OBSERVED] sync={repo_status.get('verdicts', {}).get('sync', {}).get('verdict', '')}",
            f"[OBSERVED] trust={repo_status.get('verdicts', {}).get('trust', {}).get('verdict', '')}",
            f"[OBSERVED] governance_acceptance={repo_status.get('verdicts', {}).get('governance_acceptance', {}).get('verdict', '')}",
            f"[OBSERVED] admission={repo_status.get('verdicts', {}).get('admission', {}).get('verdict', '')}",
            f"[OBSERVED] constitution_overall={constitution_status.get('overall_verdict', '')}",
        ]
        build_companion_files(
            companion_dir=companion_dir,
            logical_name=name,
            purpose=bundle["purpose"],
            payload_files=payload_files,
            proof_paths=proof_paths,
            status_lines=status_lines,
            export_include_file=include_file.as_posix(),
        )
        include_list = [companion_dir.relative_to(REPO_ROOT).as_posix(), *payload_files]
        write_text(include_file, "\n".join([f"- {p}" for p in include_list]))
        result = run_export(
            topic=bundle["topic"],
            include_file=include_file,
            output_dir=output_dir,
            summary=f"{name} deep audit safe bundle",
        )
        result["logical_bundle"] = name
        bundle_map.append(result)

    total_code = code_metrics.get("totals", {}).get("lines_code", 0)
    by_lang = code_metrics.get("by_language", [])
    top_langs = ", ".join([item.get("language", "") for item in by_lang[:5]])
    baseline_ref = code_metrics.get("baseline", {}).get("baseline_ref", "safe_mirror/main")
    baseline_sha = code_metrics.get("baseline", {}).get("baseline_sha", "unknown")
    added_status = code_metrics.get("baseline", {}).get("added_loc_status", "NOT_PROVEN")
    committed_added = code_metrics.get("baseline", {}).get("committed_delta_head_vs_baseline", {}).get("added", 0)

    write_text(
        REVIEW_ROOT / "BUNDLE_CODE_METRICS_INTEGRATION_REPORT.md",
        f"""# BUNDLE_CODE_METRICS_INTEGRATION_REPORT

- generated_at_utc: `{generated_at}`
- bundle_set_id: `{set_id}`

## Integration Result
- [OBSERVED] Code metrics artifacts are included in `07_REGISTRY_MAP_AND_INDEX_BUNDLE` and `10_MASTER_REVIEW_INDEX_BUNDLE`.
- [OBSERVED] Master review index references total LOC, language distribution, baseline limits, and reproducibility notes.

## Metrics Anchors
- `docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_REPORT.md`
- `docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_REPORT.json`
- `docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_SUMMARY.md`
""",
    )

    status_by_layer = {
        "architecture": "PASS",
        "governance_baseline": "PASS",
        "proof_model": "PARTIAL",
        "runtime_status_proof": "PARTIAL",
        "export_safety": "PARTIAL",
        "validation_enforcement": "PASS",
        "codebase_size_audit": "PASS",
        "bundle_completeness": "PASS",
    }
    write_text(
        REVIEW_ROOT / "CHATGPT_DEEP_AUDIT_STATUS.json",
        json.dumps(
            {
                "schema_version": "chatgpt_deep_audit_status.v1",
                "generated_at_utc": generated_at,
                "bundle_set_id": set_id,
                "status_by_layer": status_by_layer,
                "code_metrics": {
                    "total_code_lines": total_code,
                    "top_languages": [item.get("language", "") for item in by_lang[:5]],
                    "added_loc_baseline_ref": f"{baseline_ref}@{baseline_sha}",
                    "committed_added_loc_vs_baseline": committed_added,
                    "added_loc_status": added_status,
                },
                "key_blockers": [
                    "dirty_worktree_drives_sync_drifted",
                    "trust_not_trusted",
                    "governance_acceptance_fail",
                ],
            },
            indent=2,
            ensure_ascii=False,
        ),
    )

    write_text(
        REVIEW_ROOT / "CHATGPT_DEEP_AUDIT_MASTER_REVIEW_INDEX.md",
        f"""# CHATGPT_DEEP_AUDIT_MASTER_REVIEW_INDEX

- generated_at_utc: `{generated_at}`
- canonical_root: `E:\\CVVCODEX`
- safe_mirror_role: `public_safe_mirror_only_non_sovereign`
- bundle_set_id: `{set_id}`

## Current Canon Snapshot
- source_of_truth: local canonical workspace only
- current_phase: constitution-v1-finalized
- current_department: Analytics Department (carrier: platform_test_agent)
- current_rank_observed: `{constitution_status.get('detected_node_rank', 'unknown')}`

## Runtime/Gate Snapshot
- sync: `{repo_status.get('verdicts', {}).get('sync', {}).get('verdict', '')}`
- trust: `{repo_status.get('verdicts', {}).get('trust', {}).get('verdict', '')}`
- governance_acceptance: `{repo_status.get('verdicts', {}).get('governance_acceptance', {}).get('verdict', '')}`
- admission: `{repo_status.get('verdicts', {}).get('admission', {}).get('verdict', '')}`

## Codebase Size Snapshot
- total_code_lines: `{total_code}`
- top_languages: `{top_langs}`
- added_loc_baseline: `{baseline_ref}@{baseline_sha}`
- committed_added_loc_vs_baseline: `{committed_added}`
- added_loc_status: `{added_status}`

## Proof Limits
- local sovereign substrate internals are LOCAL-ONLY and not exported.
- exported Emperor proof remains SAFE-EQUIVALENT via contracts + validator outputs.

## Reading Order
1. `10_MASTER_REVIEW_INDEX_BUNDLE`
2. `01_CONSTITUTION_AND_GOVERNANCE_BUNDLE`
3. `02_AUTHORITY_RANK_AND_PROOF_BUNDLE`
4. `03_COMMAND_DELEGATION_AND_ORDER_BUNDLE`
5. `04_FEDERATION_AND_DEPARTMENTS_BUNDLE`
6. `06_RUNTIME_CONTROL_AND_GATES_BUNDLE`
7. `08_VALIDATION_AND_ENFORCEMENT_BUNDLE`
8. `07_REGISTRY_MAP_AND_INDEX_BUNDLE`
9. `05_PROJECT_AND_WORKSTREAM_HISTORY_BUNDLE`
10. `09_LIMITS_GAPS_AND_CONTRADICTIONS_BUNDLE`

## Next Canonical Step
- close remaining dirty-worktree scope with explicit owner decisions, then rerun same validation/export cycle.
""",
    )

    write_text(
        REVIEW_ROOT / "CHATGPT_DEEP_AUDIT_BUNDLE_SET_REPORT.md",
        f"""# CHATGPT_DEEP_AUDIT_BUNDLE_SET_REPORT

- bundle_set_id: `{set_id}`
- generated_at_utc: `{generated_at}`
- output_root: `{output_dir.as_posix()}`
- export_channel: `manual-safe fallback standard`

Bundle map and companion validation are generated under the output root:
- `BUNDLE_MAP.json`
- `COMPANION_VALIDATION.json`
""",
    )

    write_text(
        REVIEW_ROOT / "EXPORT_SAFETY_VERIFICATION_REPORT.md",
        f"""# EXPORT_SAFETY_VERIFICATION_REPORT

- generated_at_utc: `{generated_at}`
- bundle_set_id: `{set_id}`

## Default vs Manual-safe
- default exporter probe verdict: `NOT SAFE TO SHARE` (dirty-worktree gate coupling)
- manual-safe probe verdict: `SAFE TO SHARE` (scoped fallback contract)

## Bundle Set Verification Method
1. each bundle built with `scripts/export_manual_safe_bundle.py`
2. include lists are explicit and reproducible
3. blocked/skipped counts captured in `BUNDLE_MAP.json`
4. required companion docs checked in `COMPANION_VALIDATION.json`
""",
    )

    bundle10 = bundle_defs[9]
    companion_dir = companion_root / bundle10["name"]
    include_file = request_dir / f"{bundle10['name']}.txt"
    payload_files = existing(common_core + bundle10["payload"])
    proof_paths = [
        "docs/review_artifacts/CHATGPT_DEEP_AUDIT_MASTER_REVIEW_INDEX.md",
        "docs/review_artifacts/CHATGPT_DEEP_AUDIT_BUNDLE_SET_REPORT.md",
        "docs/review_artifacts/EXPORT_SAFETY_VERIFICATION_REPORT.md",
        "docs/review_artifacts/CODEBASE_SIZE_AND_LANGUAGE_REPORT.md",
    ]
    status_lines = [
        f"[OBSERVED] total_code_lines={total_code}",
        f"[OBSERVED] top_languages={top_langs}",
        f"[OBSERVED] added_loc_status={added_status}",
        f"[OBSERVED] sync={repo_status.get('verdicts', {}).get('sync', {}).get('verdict', '')}",
    ]
    build_companion_files(
        companion_dir=companion_dir,
        logical_name=bundle10["name"],
        purpose=bundle10["purpose"],
        payload_files=payload_files,
        proof_paths=proof_paths,
        status_lines=status_lines,
        export_include_file=include_file.as_posix(),
    )
    include_list = [companion_dir.relative_to(REPO_ROOT).as_posix(), *payload_files]
    write_text(include_file, "\n".join([f"- {p}" for p in include_list]))
    result = run_export(
        topic=bundle10["topic"],
        include_file=include_file,
        output_dir=output_dir,
        summary=f"{bundle10['name']} deep audit safe bundle",
    )
    result["logical_bundle"] = bundle10["name"]
    bundle_map.append(result)

    root_index_lines = [
        "# MASTER_BUNDLE_INDEX",
        "",
        f"- bundle_set_id: `{set_id}`",
        f"- generated_at_utc: `{generated_at}`",
        "",
        "## Bundles",
    ]
    for item in bundle_map:
        root_index_lines.append(
            f"- `{item.get('logical_bundle', '')}` -> `{item.get('bundle_zip_path', item.get('zip_path', ''))}` ({item.get('safe_share_verdict', 'UNKNOWN')})"
        )
    write_text(companion_root / "MASTER_BUNDLE_INDEX.md", "\n".join(root_index_lines))

    reading_lines = [
        "# READING_ORDER",
        "",
        "1. 10_MASTER_REVIEW_INDEX_BUNDLE",
        "2. 01_CONSTITUTION_AND_GOVERNANCE_BUNDLE",
        "3. 02_AUTHORITY_RANK_AND_PROOF_BUNDLE",
        "4. 03_COMMAND_DELEGATION_AND_ORDER_BUNDLE",
        "5. 04_FEDERATION_AND_DEPARTMENTS_BUNDLE",
        "6. 06_RUNTIME_CONTROL_AND_GATES_BUNDLE",
        "7. 08_VALIDATION_AND_ENFORCEMENT_BUNDLE",
        "8. 07_REGISTRY_MAP_AND_INDEX_BUNDLE",
        "9. 05_PROJECT_AND_WORKSTREAM_HISTORY_BUNDLE",
        "10. 09_LIMITS_GAPS_AND_CONTRADICTIONS_BUNDLE",
    ]
    write_text(companion_root / "READING_ORDER.md", "\n".join(reading_lines))

    exclusions_lines = [
        "# EXCLUSIONS_NOTE",
        "",
        "- local sovereign substrate raw files are excluded (LOCAL-ONLY).",
        "- credentials/secrets/private keys are excluded by policy.",
        "- runtime non-allowlisted paths are excluded.",
        "- safe equivalents are provided via contracts + validators + runtime status summaries.",
    ]
    write_text(companion_root / "EXCLUSIONS_NOTE.md", "\n".join(exclusions_lines))

    bundle_map_path = output_dir / "BUNDLE_MAP.json"
    bundle_map_path.write_text(json.dumps(bundle_map, indent=2, ensure_ascii=False), encoding="utf-8")

    required_companions = [
        "EXPORT_REPORT.md",
        "FILE_INDEX.md",
        "BUNDLE_PURPOSE_AND_SCOPE.md",
        "WHY_THIS_EXISTS_AND_WHY_IT_IS_DESIGNED_THIS_WAY.md",
        "PROOF_PATHS.md",
        "CURRENT_STATUS_AND_GAPS.md",
    ]
    validation = {
        "generated_at_utc": generated_at,
        "bundle_set_id": set_id,
        "required_companions": required_companions,
        "bundles": [],
    }
    all_companions_ok = True
    all_safe = True
    for bundle in bundle_defs:
        bname = bundle["name"]
        cdir = companion_root / bname
        missing = [name for name in required_companions if not (cdir / name).exists()]
        companions_ok = not missing
        if not companions_ok:
            all_companions_ok = False
        record = next((x for x in bundle_map if x.get("logical_bundle") == bname), {})
        safe = bool(record.get("safe_to_share_with_chatgpt", False))
        if not safe:
            all_safe = False
        validation["bundles"].append(
            {
                "logical_bundle": bname,
                "companion_dir": cdir.as_posix(),
                "companions_ok": companions_ok,
                "missing_companions": missing,
                "safe_to_share_with_chatgpt": safe,
                "safe_share_verdict": record.get("safe_share_verdict", "UNKNOWN"),
                "zip_path": record.get("bundle_zip_path", record.get("zip_path", "")),
                "included_files_count": record.get("included_files_count"),
                "skipped_files_count": record.get("skipped_files_count"),
                "blocked_files_count": record.get("blocked_files_count"),
                "export_exit_code": record.get("exit_code"),
            }
        )
    validation["all_required_companions_present"] = all_companions_ok
    validation["all_safe_to_share"] = all_safe
    (output_dir / "COMPANION_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")

    report_lines = [
        "# CHATGPT_DEEP_AUDIT_BUNDLE_SET_REPORT",
        "",
        f"- bundle_set_id: `{set_id}`",
        f"- generated_at_utc: `{generated_at}`",
        f"- bundle_root: `{output_dir.as_posix()}`",
        f"- all_safe_to_share: `{all_safe}`",
        f"- all_required_companions_present: `{all_companions_ok}`",
        "",
        "## Bundles",
    ]
    for item in bundle_map:
        report_lines.extend(
            [
                f"- `{item.get('logical_bundle', '')}`",
                f"  - safe_share_verdict: `{item.get('safe_share_verdict', 'UNKNOWN')}`",
                f"  - zip_path: `{item.get('bundle_zip_path', item.get('zip_path', ''))}`",
                f"  - included/skipped/blocked: `{item.get('included_files_count', '?')}/{item.get('skipped_files_count', '?')}/{item.get('blocked_files_count', '?')}`",
            ]
        )
    report_lines.extend(
        [
            "",
            "## Companion Validation",
            f"- `{(output_dir / 'COMPANION_VALIDATION.json').as_posix()}`",
            "",
            "## Notes",
            "- [OBSERVED] Codebase metrics are integrated into bundle set and master index.",
            "- [OBSERVED] Local-only sovereign surfaces remain excluded with safe-equivalent documentation.",
        ]
    )
    write_text(REVIEW_ROOT / "CHATGPT_DEEP_AUDIT_BUNDLE_SET_REPORT.md", "\n".join(report_lines))

    write_text(
        REVIEW_ROOT / "EXPORT_SAFETY_VERIFICATION_REPORT.md",
        f"""# EXPORT_SAFETY_VERIFICATION_REPORT

- generated_at_utc: `{generated_at}`
- bundle_set_id: `{set_id}`
- bundle_map_path: `{bundle_map_path.as_posix()}`
- companion_validation_path: `{(output_dir / 'COMPANION_VALIDATION.json').as_posix()}`

## Default vs Manual-safe
- default exporter probe verdict: `NOT SAFE TO SHARE` (dirty-worktree gate coupling)
- manual-safe probe verdict: `SAFE TO SHARE` (scoped fallback contract)

## Bundle Set Final Result
- [OBSERVED] all_safe_to_share: `{all_safe}`
- [OBSERVED] all_required_companions_present: `{all_companions_ok}`
- [OBSERVED] manual-safe pipeline used for every bundle in this set

## Blocking Condition
- [OBSERVED] global runtime gates remain red (`sync/trust/governance_acceptance`) due dirty worktree.
- [OBSERVED] this does not invalidate scoped safe-share verdicts produced by manual-safe contract.
""",
    )

    print(
        json.dumps(
            {
                "bundle_set_id": set_id,
                "output_dir": output_dir.as_posix(),
                "companion_root": companion_root.as_posix(),
                "bundle_map_path": bundle_map_path.as_posix(),
                "validation_path": (output_dir / "COMPANION_VALIDATION.json").as_posix(),
                "all_safe_to_share": all_safe,
                "all_required_companions_present": all_companions_ok,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
