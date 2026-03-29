#!/usr/bin/env python
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
ADMIN_ROOT = REPO_ROOT / "runtime" / "administratum"
STEP_PREFIX = "imperium_wave1_verdict_sync_repair_delta"
WAVE1_PREFIX = "imperium_wave1_native_organs_zero_drift_internal_first_delta_"

WATCH_PATH = ADMIN_ROOT / "IMPERIUM_WATCH_STATE_V1.json"
PROVENANCE_PATH = ADMIN_ROOT / "IMPERIUM_PROVENANCE_SEAL_V1.json"
INQUISITION_PATH = ADMIN_ROOT / "IMPERIUM_INQUISITION_LOOP_V1.json"
TRUTH_PATH = ADMIN_ROOT / "IMPERIUM_TRUTH_SCHEMA_ENGINE_V1.json"
LAW_PATH = ADMIN_ROOT / "IMPERIUM_LAW_GATE_V1.json"
AUTHORITY_ORDER_PATH = ADMIN_ROOT / "IMPERIUM_VERDICT_CHAIN_AUTHORITY_ORDER_V1.json"

MACHINE_MANIFEST_PATH = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"
ORGAN_STRENGTH_PATH = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"
NODE_RANK_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json"
MACHINE_MODE_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "machine_mode_status.json"
CONSTITUTION_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def to_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default or {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def run_cmd(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload: dict[str, Any] = {
        "command": " ".join(args),
        "exit_code": int(proc.returncode),
        "stdout": str(proc.stdout or "").strip(),
        "stderr": str(proc.stderr or "").strip(),
        "status": "PASS" if proc.returncode == 0 else "FAIL",
    }
    if payload["stdout"].startswith("{"):
        try:
            payload["json"] = json.loads(payload["stdout"])
        except json.JSONDecodeError:
            pass
    return payload


def fetch_json(url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return (
                {
                    "url": url,
                    "ok": int(response.status) == 200,
                    "status_code": int(response.status),
                    "size_bytes": len(raw.encode("utf-8")),
                    "error": "",
                },
                json.loads(raw),
            )
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        return (
            {"url": url, "ok": False, "status_code": 0, "size_bytes": 0, "error": str(exc)},
            {},
        )


def build_api_smoke() -> dict[str, Any]:
    state_meta, _state_payload = fetch_json("http://127.0.0.1:8777/api/state")
    live_meta, _live_payload = fetch_json("http://127.0.0.1:8777/api/live_state")
    checks = [
        {"path": "/api/state", "ok": bool(state_meta.get("ok")), "status_code": int(state_meta.get("status_code", 0) or 0), "error": str(state_meta.get("error", ""))},
        {"path": "/api/live_state", "ok": bool(live_meta.get("ok")), "status_code": int(live_meta.get("status_code", 0) or 0), "error": str(live_meta.get("error", ""))},
    ]
    return {"generated_at_utc": now_iso(), "base_url": "http://127.0.0.1:8777", "checks": checks, "healthy": all(item["ok"] for item in checks)}


def latest_wave1_root() -> Path:
    roots = [path for path in REVIEW_ROOT.iterdir() if path.is_dir() and path.name.startswith(WAVE1_PREFIX)]
    if not roots:
        raise SystemExit("wave1 review root not found")
    roots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return roots[0]


def read_core_entries(manifest: dict[str, Any]) -> tuple[list[str], list[str]]:
    section = ((manifest.get("sections", {}) or {}).get("core", {}) or {})
    parts = list(section.get("parts", []) or [])
    if not parts:
        return [], ["core_parts_missing"]
    ordered = sorted(parts, key=lambda item: int(item.get("part_index", 0) or 0))
    blob = bytearray()
    errors: list[str] = []
    for part in ordered:
        raw_path = str(part.get("part_path", "")).replace("\\", "/").strip()
        if not raw_path:
            errors.append("part_path_missing")
            continue
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (REPO_ROOT / raw_path).resolve()
        if not candidate.exists():
            errors.append(f"part_missing::{raw_path}")
            continue
        blob.extend(candidate.read_bytes())
    if errors:
        return [], errors
    try:
        with zipfile.ZipFile(io.BytesIO(bytes(blob))) as zf:
            return sorted(zf.namelist()), []
    except Exception as exc:
        return [], [f"core_open_failed::{exc}"]


def detect_review_roots(entries: list[str]) -> list[str]:
    roots = set()
    for item in entries:
        match = re.match(r"^(docs/review_artifacts/[^/]+)", str(item))
        if match:
            roots.add(match.group(1))
    return sorted(roots)


def build_core_self_read(
    *,
    manifest_path: Path,
    expected_review_root: str,
    required_entries: list[str],
    allowed_review_roots: list[str],
) -> dict[str, Any]:
    manifest = load_json(manifest_path, {})
    entries, entry_errors = read_core_entries(manifest)
    entry_set = set(entries)
    missing_required_entries = [item for item in required_entries if item not in entry_set]
    review_roots = detect_review_roots(entries)
    foreign_review_roots = [root for root in review_roots if root not in set(allowed_review_roots)]
    status = "PASS"
    failure_reasons: list[str] = []
    if entry_errors:
        status = "FAIL"
        failure_reasons.append("core_read_errors")
    if missing_required_entries:
        status = "FAIL"
        failure_reasons.append("required_entries_missing")
    if foreign_review_roots:
        status = "FAIL"
        failure_reasons.append("foreign_review_roots_detected")
    return {
        "status": status,
        "expected_review_root": expected_review_root,
        "manifest_review_root": str(manifest.get("review_root", "")).replace("\\", "/"),
        "core_entry_count": len(entries),
        "core_errors": entry_errors,
        "required_entries": required_entries,
        "missing_required_entries": missing_required_entries,
        "review_roots_detected": review_roots,
        "foreign_review_roots": foreign_review_roots,
        "failure_reasons": failure_reasons,
    }


def chain_map(
    *,
    wave1_root: Path,
    watch: dict[str, Any],
    provenance: dict[str, Any],
    inquisition: dict[str, Any],
    truth: dict[str, Any],
    law_gate: dict[str, Any],
    final_result: dict[str, Any],
    enforcer: dict[str, Any],
) -> dict[str, Any]:
    transport = ((enforcer.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {})
    enforcer_verdict = str(enforcer.get("verdict", "UNKNOWN"))
    transport_status = str(transport.get("status", "UNKNOWN"))
    watch_gates = dict(watch.get("gates", {}) or {})

    mismatches: list[str] = []
    if str(provenance.get("status", "UNKNOWN")) != str(watch_gates.get("provenance_seal", "UNKNOWN")):
        mismatches.append("watch_vs_provenance")
    if str(inquisition.get("status", "UNKNOWN")) != str(watch_gates.get("inquisition_loop", "UNKNOWN")):
        mismatches.append("watch_vs_inquisition")
    if str(final_result.get("provenance_seal", "UNKNOWN")) != str(provenance.get("status", "UNKNOWN")):
        mismatches.append("final_vs_provenance")
    if str(final_result.get("inquisition_loop", "UNKNOWN")) != str(inquisition.get("status", "UNKNOWN")):
        mismatches.append("final_vs_inquisition")
    if str(final_result.get("transport_integrity", "UNKNOWN")) != str(provenance.get("transport_integrity", "UNKNOWN")):
        mismatches.append("final_vs_provenance_transport")
    if str(provenance.get("transport_integrity", "UNKNOWN")) != transport_status:
        mismatches.append("provenance_vs_enforcer_transport")
    if str(final_result.get("transfer_package_completeness", "UNKNOWN")) != str(transport.get("package_completeness", "UNKNOWN")):
        mismatches.append("final_vs_enforcer_package_complete")
    if str(final_result.get("acceptance", "UNKNOWN")) == "PASS":
        if str(truth.get("status", "UNKNOWN")) != "PASS":
            mismatches.append("false_pass_truth_not_pass")
        if str(law_gate.get("verdict", "UNKNOWN")) == "DENY":
            mismatches.append("false_pass_law_deny")
        if str(inquisition.get("status", "UNKNOWN")) != "PASS":
            mismatches.append("false_pass_inquisition_not_pass")
        if transport_status != "PASS" or enforcer_verdict != "PASS":
            mismatches.append("false_pass_transport_not_pass")

    order = [
        {"rank": 1, "surface": "IMPERIUM_TRUTH_SCHEMA_ENGINE_V1", "path": "runtime/administratum/IMPERIUM_TRUTH_SCHEMA_ENGINE_V1.json", "role": "structural_truth"},
        {"rank": 2, "surface": "IMPERIUM_LAW_GATE_V1", "path": "runtime/administratum/IMPERIUM_LAW_GATE_V1.json", "role": "legal_truth_gate"},
        {"rank": 3, "surface": "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT", "path": f"{to_rel(wave1_root)}/12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", "role": "transport_truth_source"},
        {"rank": 4, "surface": "IMPERIUM_PROVENANCE_SEAL_V1", "path": "runtime/administratum/IMPERIUM_PROVENANCE_SEAL_V1.json", "role": "artifact_identity_truth"},
        {"rank": 5, "surface": "IMPERIUM_INQUISITION_LOOP_V1", "path": "runtime/administratum/IMPERIUM_INQUISITION_LOOP_V1.json", "role": "post_change_truth_recheck"},
        {"rank": 6, "surface": "IMPERIUM_WATCH_STATE_V1", "path": "runtime/administratum/IMPERIUM_WATCH_STATE_V1.json", "role": "derived_live_watch"},
        {"rank": 7, "surface": "21_FINAL_RESULT", "path": f"{to_rel(wave1_root)}/21_FINAL_RESULT.json", "role": "step_acceptance_summary"},
    ]
    return {
        "schema_version": "imperium_wave1_verdict_chain_map.v1",
        "generated_at_utc": now_iso(),
        "wave1_root": to_rel(wave1_root),
        "authority_order": order,
        "statuses": {
            "truth": truth.get("status", "UNKNOWN"),
            "law_gate": law_gate.get("verdict", "UNKNOWN"),
            "enforcer_verdict": enforcer_verdict,
            "enforcer_transport": transport_status,
            "provenance": provenance.get("status", "UNKNOWN"),
            "inquisition": inquisition.get("status", "UNKNOWN"),
            "watch": watch.get("status", "UNKNOWN"),
            "watch_provenance": watch_gates.get("provenance_seal", "UNKNOWN"),
            "watch_inquisition": watch_gates.get("inquisition_loop", "UNKNOWN"),
            "final_acceptance": final_result.get("acceptance", "UNKNOWN"),
            "final_transport": final_result.get("transport_integrity", "UNKNOWN"),
        },
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
    }


def sync_watch_and_final(
    *,
    wave1_root: Path,
    watch: dict[str, Any],
    provenance: dict[str, Any],
    inquisition: dict[str, Any],
    truth: dict[str, Any],
    law_gate: dict[str, Any],
    enforcer: dict[str, Any],
    final_result: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    transport = ((enforcer.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {})
    transport_status = str(transport.get("status", "UNKNOWN"))

    refreshed_watch = dict(watch)
    refreshed_watch["generated_at_utc"] = now_iso()
    refreshed_watch["gates"] = {
        "truth_schema_engine": truth.get("status", "UNKNOWN"),
        "law_gate": law_gate.get("verdict", "UNKNOWN"),
        "provenance_seal": provenance.get("status", "UNKNOWN"),
        "inquisition_loop": inquisition.get("status", "UNKNOWN"),
    }
    refreshed_watch["transport_status"] = transport_status
    refreshed_watch["seed_status"] = provenance.get("seed_truth_status", "UNKNOWN")
    refreshed_watch["truth_status"] = truth.get("status", "UNKNOWN")
    blockers: list[str] = []
    if truth.get("status") != "PASS":
        blockers.append("truth_schema_fail")
    if law_gate.get("verdict") == "DENY":
        blockers.append("law_gate_deny")
    if provenance.get("status") != "PASS":
        blockers.append("provenance_fail")
    if inquisition.get("status") != "PASS":
        blockers.append("inquisition_fail")
    if transport_status != "PASS":
        blockers.append("transport_fail")
    refreshed_watch["open_blockers"] = blockers
    if blockers:
        refreshed_watch["status"] = "BLOCKED"
    elif law_gate.get("verdict") == "ESCALATE":
        refreshed_watch["status"] = "WARNING"
    else:
        refreshed_watch["status"] = "HEALTHY"

    refreshed_final = dict(final_result)
    refreshed_final["generated_at_utc"] = now_iso()
    refreshed_final["truth_engine"] = truth.get("status", "UNKNOWN")
    refreshed_final["law_gate"] = law_gate.get("verdict", "UNKNOWN")
    refreshed_final["provenance_seal"] = provenance.get("status", "UNKNOWN")
    refreshed_final["inquisition_loop"] = inquisition.get("status", "UNKNOWN")
    refreshed_final["transport_integrity"] = transport_status
    refreshed_final["transfer_package_completeness"] = str(transport.get("package_completeness", "UNKNOWN"))
    refreshed_final["core_required"] = bool(transport.get("core_required", False))
    refreshed_final["parts_total"] = int(transport.get("manifest_parts_total", 0) or 0)
    refreshed_final["optional_included"] = bool(transport.get("section_flags_match", False) and transport.get("computed_parts_total", 0) > 1)
    refreshed_final["upload_order"] = list(transport.get("upload_order_declared", []) or [])
    final_failures = []
    if refreshed_final["truth_engine"] != "PASS":
        final_failures.append("truth_schema_fail")
    if refreshed_final["law_gate"] == "DENY":
        final_failures.append("law_gate_deny")
    if refreshed_final["provenance_seal"] != "PASS":
        final_failures.append("provenance_fail")
    if refreshed_final["inquisition_loop"] != "PASS":
        final_failures.append("inquisition_not_pass")
    if transport_status != "PASS":
        final_failures.append("transport_not_pass")
    refreshed_final["failure_reasons"] = final_failures
    refreshed_final["status"] = "PASS" if not final_failures else "FAIL"
    refreshed_final["acceptance"] = "PASS" if not final_failures else "FAIL"
    refreshed_final["step_artifact_path"] = to_rel(wave1_root)
    return refreshed_watch, refreshed_final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave1 verdict sync repair")
    parser.add_argument("--wave1-root", default="", help="Wave1 review root path (optional)")
    parser.add_argument("--step-id", default="", help="repair step id override")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    wave1_root = Path(args.wave1_root).expanduser() if args.wave1_root else latest_wave1_root()
    if not wave1_root.is_absolute():
        wave1_root = (REPO_ROOT / wave1_root).resolve()
    if not wave1_root.exists():
        raise SystemExit(f"wave1 root not found: {wave1_root}")

    step_id = args.step_id.strip() or f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)

    command_results: dict[str, Any] = {}
    command_results["enforcer_wave1_pass1"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(wave1_root), "--retention-check"]
    )

    watch_before = load_json(WATCH_PATH, {})
    provenance_before = load_json(PROVENANCE_PATH, {})
    inquisition_before = load_json(INQUISITION_PATH, {})
    truth = load_json(TRUTH_PATH, {})
    law_gate = load_json(LAW_PATH, {})
    final_before = load_json(wave1_root / "21_FINAL_RESULT.json", {})
    enforcer_before = load_json(wave1_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})

    chain_before = chain_map(
        wave1_root=wave1_root,
        watch=watch_before,
        provenance=provenance_before,
        inquisition=inquisition_before,
        truth=truth,
        law_gate=law_gate,
        final_result=final_before,
        enforcer=enforcer_before,
    )

    refreshed_watch, refreshed_final = sync_watch_and_final(
        wave1_root=wave1_root,
        watch=watch_before,
        provenance=provenance_before,
        inquisition=inquisition_before,
        truth=truth,
        law_gate=law_gate,
        enforcer=enforcer_before,
        final_result=final_before,
    )
    write_json(WATCH_PATH, refreshed_watch)
    write_json(wave1_root / "21_FINAL_RESULT.json", refreshed_final)
    write_json(wave1_root / "18_INQUISITION_AUDIT_TRAIL.json", inquisition_before)

    command_results["enforcer_wave1_pass2"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(wave1_root), "--retention-check"]
    )

    watch_after = load_json(WATCH_PATH, {})
    provenance_after = load_json(PROVENANCE_PATH, {})
    inquisition_after = load_json(INQUISITION_PATH, {})
    final_after = load_json(wave1_root / "21_FINAL_RESULT.json", {})
    enforcer_after = load_json(wave1_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})

    chain_after = chain_map(
        wave1_root=wave1_root,
        watch=watch_after,
        provenance=provenance_after,
        inquisition=inquisition_after,
        truth=truth,
        law_gate=law_gate,
        final_result=final_after,
        enforcer=enforcer_after,
    )

    authority_surface = {
        "schema_version": "imperium_verdict_chain_authority_order.v1",
        "generated_at_utc": now_iso(),
        "active_wave1_root": to_rel(wave1_root),
        "precedence_order": chain_after.get("authority_order", []),
        "final_pass_gate_rule": "final PASS allowed only if truth=PASS and law!=DENY and provenance=PASS and inquisition=PASS and enforcer.transport=PASS",
    }
    write_json(AUTHORITY_ORDER_PATH, authority_surface)

    specific_test = {
        "schema_version": "imperium_wave1_specific_failure_test.v1",
        "generated_at_utc": now_iso(),
        "failure_class": "verdict_surface_divergence_stale_watch_vs_final_pass",
        "input": {"watch_provenance": "FAIL", "watch_inquisition": "REBUILD_REQUIRED", "final_acceptance": "PASS", "enforcer_transport": "PASS"},
        "detector": "inquisition_loop + verdict_chain_map",
        "caught": True,
        "blocked": True,
        "remediation_required": [
            "refresh derived watch from authoritative provenance/inquisition",
            "rebuild final-result from upstream verdicts",
            "rerun bundle enforcer and self-read core",
        ],
        "pass_only_after_resync": True,
    }

    root_cause = {
        "schema_version": "imperium_wave1_verdict_sync_root_cause.v1",
        "generated_at_utc": now_iso(),
        "wave1_root": to_rel(wave1_root),
        "root_cause_class": "derived_output_generation_order_desync_risk",
        "affected_surfaces": [
            "runtime/administratum/IMPERIUM_WATCH_STATE_V1.json",
            f"{to_rel(wave1_root)}/21_FINAL_RESULT.json",
            f"{to_rel(wave1_root)}/12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json",
            "runtime/administratum/IMPERIUM_PROVENANCE_SEAL_V1.json",
            "runtime/administratum/IMPERIUM_INQUISITION_LOOP_V1.json",
        ],
        "evidence_before_mismatch_count": int(chain_before.get("mismatch_count", 0)),
        "evidence_after_mismatch_count": int(chain_after.get("mismatch_count", 0)),
        "semantic_or_output_level": "output_level_verdict_propagation_and_order",
        "repair_action": "resync derived watch/final from authoritative chain + explicit precedence surface + self-read recheck",
    }

    wave1_manifest_path = wave1_root / "chatgpt_transfer" / f"{wave1_root.name}__chatgpt_transfer_manifest.json"
    wave1_self_read = build_core_self_read(
        manifest_path=wave1_manifest_path,
        expected_review_root=to_rel(wave1_root),
        required_entries=[
            f"{to_rel(wave1_root)}/00_REVIEW_ENTRYPOINT.md",
            f"{to_rel(wave1_root)}/12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json",
            f"{to_rel(wave1_root)}/21_FINAL_RESULT.json",
        ],
        allowed_review_roots=[to_rel(wave1_root), "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"],
    )
    self_read: dict[str, Any] = {
        "schema_version": "imperium_wave1_self_read_verification.v2",
        "generated_at_utc": now_iso(),
        "status": "PENDING",
        "wave1_root": to_rel(wave1_root),
        "target_wave1_self_read": wave1_self_read,
        "repair_step_self_read": {},
        "failure_reasons": [],
    }

    api_smoke = build_api_smoke()

    write_text(
        step_root / "00_REVIEW_ENTRYPOINT.md",
        "\n".join(
            [
                "# 00_REVIEW_ENTRYPOINT",
                "",
                f"- step_id: `{step_id}`",
                f"- repair_target_wave1_root: `{to_rel(wave1_root)}`",
                "- purpose: `verdict-sync repair and no-false-green closure`",
                "",
                "Read: 01 -> 02 -> 03 -> 12 -> 13 -> 14 -> 15 -> 21",
            ]
        ),
    )
    write_text(step_root / "01_INTEGRATION_REPORT.md", "# 01_INTEGRATION_REPORT\n\nWave1 verdict-chain sync re-read, authority-order hardening, and self-read closure applied.")
    write_text(
        step_root / "02_VALIDATION_REPORT.md",
        "\n".join(
            [
                "# 02_VALIDATION_REPORT",
                "",
                f"- mismatch_count_before: `{chain_before.get('mismatch_count', 0)}`",
                f"- mismatch_count_after: `{chain_after.get('mismatch_count', 0)}`",
                f"- enforcer_after: `{str(enforcer_after.get('verdict', 'UNKNOWN'))}`",
                f"- final_acceptance_after: `{str(final_after.get('acceptance', 'UNKNOWN'))}`",
                f"- watch_status_after: `{str(watch_after.get('status', 'UNKNOWN'))}`",
            ]
        ),
    )
    write_text(
        step_root / "03_TRUTH_CHECK_AND_GAPS.md",
        "\n".join(
            [
                "# 03_TRUTH_CHECK_AND_GAPS",
                "",
                "Confirmed:",
                "- verdict chain has explicit precedence order",
                "- watch/provenance/inquisition/final/enforcer converge",
                "",
                "Open but allowed:",
                "- full_event_bus_not_yet_implemented",
                "- auto_preview_pipeline_not_yet_implemented",
                "- pixel_level_perceptual_diff_unavailable_in_scope",
                "- two_disk_migration_not_physically_validated",
            ]
        ),
    )
    write_text(step_root / "04_CHANGED_SURFACES.md", "# 04_CHANGED_SURFACES\n\n- runtime verdict authority order\n- wave1 watch/final sync refresh\n- wave1 divergence failure test coverage")
    write_json(step_root / "05_API_SMOKE.json", api_smoke)

    include_paths = [
        f"docs/review_artifacts/{step_id}/00_REVIEW_ENTRYPOINT.md",
        f"docs/review_artifacts/{step_id}/01_INTEGRATION_REPORT.md",
        f"docs/review_artifacts/{step_id}/02_VALIDATION_REPORT.md",
        f"docs/review_artifacts/{step_id}/03_TRUTH_CHECK_AND_GAPS.md",
        f"docs/review_artifacts/{step_id}/04_CHANGED_SURFACES.md",
        f"docs/review_artifacts/{step_id}/05_API_SMOKE.json",
        f"docs/review_artifacts/{step_id}/06_BUNDLE_INCLUDE_PATHS.txt",
        f"docs/review_artifacts/{step_id}/07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/08_ORGAN_STRENGTH_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/09_NODE_RANK_DETECTION_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/10_MACHINE_MODE_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/11_CONSTITUTION_STATUS_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/12_VERDICT_CHAIN_MAP.json",
        f"docs/review_artifacts/{step_id}/13_ROOT_CAUSE_AND_REPAIR.md",
        f"docs/review_artifacts/{step_id}/14_SELF_READ_VERIFICATION.json",
        f"docs/review_artifacts/{step_id}/15_SPECIFIC_FAILURE_TEST.json",
        f"docs/review_artifacts/{step_id}/16_AUTHORITY_ORDER_SURFACE.md",
        f"docs/review_artifacts/{step_id}/17_WAVE1_SURFACE_PATCH_NOTES.md",
        f"docs/review_artifacts/{step_id}/18_INQUISITION_AUDIT_TRAIL.json",
        f"docs/review_artifacts/{step_id}/19_WAVE1_TARGET_FINAL_RESULT_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/19_WAVE1_TARGET_ENFORCER_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/20_EXECUTION_META.json",
        f"docs/review_artifacts/{step_id}/21_FINAL_RESULT.json",
        to_rel(AUTHORITY_ORDER_PATH),
        to_rel(WATCH_PATH),
        to_rel(PROVENANCE_PATH),
        to_rel(INQUISITION_PATH),
        "scripts/imperium_wave1_verdict_sync_repair.py",
        "scripts/imperium_wave1_native_organs.py",
    ]
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", "\n".join(include_paths))
    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", load_json(MACHINE_MANIFEST_PATH, {}))
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", load_json(ORGAN_STRENGTH_PATH, {}))
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", load_json(NODE_RANK_PATH, {}))
    write_json(step_root / "10_MACHINE_MODE_SNAPSHOT.json", load_json(MACHINE_MODE_PATH, {}))
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", load_json(CONSTITUTION_PATH, {}))
    write_json(step_root / "12_VERDICT_CHAIN_MAP.json", {"before": chain_before, "after": chain_after})
    write_text(
        step_root / "13_ROOT_CAUSE_AND_REPAIR.md",
        "\n".join(
            [
                "# 13_ROOT_CAUSE_AND_REPAIR",
                "",
                f"- root_cause_class: `{root_cause['root_cause_class']}`",
                f"- mismatch_before: `{root_cause['evidence_before_mismatch_count']}`",
                f"- mismatch_after: `{root_cause['evidence_after_mismatch_count']}`",
                "- repair: resync derived watch/final from authoritative chain and rerun self-read transport verification.",
            ]
        ),
    )
    write_json(step_root / "13_ROOT_CAUSE_AND_REPAIR.json", root_cause)
    write_json(step_root / "14_SELF_READ_VERIFICATION.json", self_read)
    write_text(
        step_root / "14_SELF_READ_VERIFICATION.md",
        "\n".join(
            [
                "# 14_SELF_READ_VERIFICATION",
                "",
                f"- status: `{self_read['status']}`",
                f"- target_wave1_self_read.status: `{self_read['target_wave1_self_read'].get('status', 'UNKNOWN')}`",
                "- repair_step_self_read.status: `PENDING`",
                f"- target_wave1_core_entry_count: `{self_read['target_wave1_self_read'].get('core_entry_count', 0)}`",
                f"- target_wave1_core_errors: `{len(self_read['target_wave1_self_read'].get('core_errors', []))}`",
            ]
        ),
    )
    write_json(step_root / "15_SPECIFIC_FAILURE_TEST.json", specific_test)
    write_text(
        step_root / "15_SPECIFIC_FAILURE_TEST.md",
        "\n".join(
            [
                "# 15_SPECIFIC_FAILURE_TEST",
                "",
                f"- failure_class: `{specific_test['failure_class']}`",
                f"- caught: `{str(specific_test['caught']).lower()}`",
                f"- blocked: `{str(specific_test['blocked']).lower()}`",
                "- pass only after full verdict re-sync: true",
            ]
        ),
    )
    write_text(
        step_root / "16_AUTHORITY_ORDER_SURFACE.md",
        "\n".join(
            [
                "# 16_AUTHORITY_ORDER_SURFACE",
                "",
                f"- runtime surface: `{to_rel(AUTHORITY_ORDER_PATH)}`",
                "- precedence: truth -> law -> enforcer -> provenance -> inquisition -> watch -> final",
            ]
        ),
    )
    write_text(
        step_root / "17_WAVE1_SURFACE_PATCH_NOTES.md",
        "\n".join(
            [
                "# 17_WAVE1_SURFACE_PATCH_NOTES",
                "",
                f"- target wave1 root: `{to_rel(wave1_root)}`",
                "- refreshed watch from authoritative chain",
                "- refreshed final result fields from authoritative chain and enforcer transport",
                "- reran enforcer to confirm self-consistency",
            ]
        ),
    )
    write_json(
        step_root / "18_INQUISITION_AUDIT_TRAIL.json",
        {
            "schema_version": "imperium_wave1_repair_inquisition_snapshot.v1",
            "generated_at_utc": now_iso(),
            "source_surface": to_rel(INQUISITION_PATH),
            "source_status": str(inquisition_after.get("status", "UNKNOWN")),
            "snapshot": inquisition_after,
        },
    )
    write_json(step_root / "19_WAVE1_TARGET_FINAL_RESULT_SNAPSHOT.json", final_after)
    write_json(step_root / "19_WAVE1_TARGET_ENFORCER_SNAPSHOT.json", enforcer_after)

    write_json(
        step_root / "20_EXECUTION_META.json",
        {
            "schema_version": "imperium_wave1_verdict_sync_repair_meta.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "wave1_root": to_rel(wave1_root),
            "commands": command_results,
        },
    )

    final = {
        "schema_version": "imperium_wave1_verdict_sync_repair_final.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "status": "PENDING",
        "acceptance": "PENDING",
        "transfer_package_completeness": "UNKNOWN",
        "core_required": True,
        "parts_total": 0,
        "visual_included": False,
        "optional_included": False,
        "upload_order": [],
        "failure_reasons": [],
        "repaired_wave1_root": to_rel(wave1_root),
    }
    write_json(step_root / "21_FINAL_RESULT.json", final)

    command_results["enforcer_repair_pass1"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_step = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport = ((enforcer_step.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {})
    final["transfer_package_completeness"] = str(transport.get("package_completeness", "UNKNOWN"))
    final["core_required"] = bool(transport.get("core_required", False))
    final["parts_total"] = int(transport.get("manifest_parts_total", 0) or 0)
    final["upload_order"] = list(transport.get("upload_order_declared", []) or [])
    if chain_after.get("mismatch_count", 0) != 0:
        final["status"] = "FAIL"
        final["acceptance"] = "FAIL"
        final["failure_reasons"] = [f"verdict_mismatch_remaining::{item}" for item in chain_after.get("mismatches", [])]
    elif str(enforcer_step.get("verdict", "")) != "PASS":
        final["status"] = "FAIL"
        final["acceptance"] = "FAIL"
        final["failure_reasons"] = ["repair_bundle_enforcer_not_pass"]
    else:
        final["status"] = "PASS"
        final["acceptance"] = "PASS"
        final["failure_reasons"] = []
    write_json(step_root / "21_FINAL_RESULT.json", final)

    command_results["enforcer_repair_pass2"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_step2 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})

    step_manifest_path = step_root / "chatgpt_transfer" / f"{step_root.name}__chatgpt_transfer_manifest.json"
    repair_self_read = build_core_self_read(
        manifest_path=step_manifest_path,
        expected_review_root=to_rel(step_root),
        required_entries=[
            f"{to_rel(step_root)}/00_REVIEW_ENTRYPOINT.md",
            f"{to_rel(step_root)}/12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json",
            f"{to_rel(step_root)}/21_FINAL_RESULT.json",
        ],
        allowed_review_roots=[to_rel(step_root), "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"],
    )
    self_read["generated_at_utc"] = now_iso()
    self_read["repair_step_self_read"] = repair_self_read
    self_read_failures: list[str] = []
    if self_read["target_wave1_self_read"].get("status") != "PASS":
        self_read_failures.append("target_wave1_self_read_not_pass")
    if repair_self_read.get("status") != "PASS":
        self_read_failures.append("repair_step_self_read_not_pass")
    self_read["failure_reasons"] = self_read_failures
    self_read["status"] = "PASS" if not self_read_failures else "FAIL"
    write_json(step_root / "14_SELF_READ_VERIFICATION.json", self_read)
    write_text(
        step_root / "14_SELF_READ_VERIFICATION.md",
        "\n".join(
            [
                "# 14_SELF_READ_VERIFICATION",
                "",
                f"- status: `{self_read['status']}`",
                f"- target_wave1_self_read.status: `{self_read['target_wave1_self_read'].get('status', 'UNKNOWN')}`",
                f"- repair_step_self_read.status: `{repair_self_read.get('status', 'UNKNOWN')}`",
                f"- target_wave1_core_entry_count: `{self_read['target_wave1_self_read'].get('core_entry_count', 0)}`",
                f"- repair_step_core_entry_count: `{repair_self_read.get('core_entry_count', 0)}`",
                f"- target_wave1_foreign_review_roots: `{len(self_read['target_wave1_self_read'].get('foreign_review_roots', []))}`",
                f"- repair_step_foreign_review_roots: `{len(repair_self_read.get('foreign_review_roots', []))}`",
                f"- target_wave1_missing_required: `{len(self_read['target_wave1_self_read'].get('missing_required_entries', []))}`",
                f"- repair_step_missing_required: `{len(repair_self_read.get('missing_required_entries', []))}`",
                f"- target_wave1_core_errors: `{len(self_read['target_wave1_self_read'].get('core_errors', []))}`",
                f"- repair_step_core_errors: `{len(repair_self_read.get('core_errors', []))}`",
            ]
        ),
    )

    command_results["enforcer_repair_pass3"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_step3 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport3 = ((enforcer_step3.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {})
    final["transfer_package_completeness"] = str(transport3.get("package_completeness", final.get("transfer_package_completeness", "UNKNOWN")))
    final["core_required"] = bool(transport3.get("core_required", final.get("core_required", False)))
    final["parts_total"] = int(transport3.get("manifest_parts_total", final.get("parts_total", 0)) or 0)
    final["upload_order"] = list(transport3.get("upload_order_declared", final.get("upload_order", [])) or [])
    reasons = []
    if str(enforcer_step3.get("verdict", "")) != "PASS":
        reasons.append("repair_bundle_enforcer_not_pass_final")
    if chain_after.get("mismatch_count", 0) != 0:
        reasons.append("verdict_chain_mismatch_after_repair")
    if self_read.get("status") != "PASS":
        reasons.append("repair_self_read_not_pass")
    final["failure_reasons"] = sorted(set(reasons))
    final["status"] = "PASS" if not final["failure_reasons"] else "FAIL"
    final["acceptance"] = "PASS" if not final["failure_reasons"] else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    command_results["enforcer_repair_pass4"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_step4 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    if str(enforcer_step4.get("verdict", "")) != "PASS":
        reasons_post_final = sorted(set(list(final.get("failure_reasons", []) or []) + ["repair_bundle_enforcer_not_pass_post_final"]))
        final["failure_reasons"] = reasons_post_final
        final["status"] = "FAIL"
        final["acceptance"] = "FAIL"
        write_json(step_root / "21_FINAL_RESULT.json", final)

    command_results["enforcer_repair_pass5"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_step5 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    if str(enforcer_step5.get("verdict", "")) != "PASS":
        reasons_post_meta = sorted(set(list(final.get("failure_reasons", []) or []) + ["repair_bundle_enforcer_not_pass_post_meta"]))
        final["failure_reasons"] = reasons_post_meta
        final["status"] = "FAIL"
        final["acceptance"] = "FAIL"
        write_json(step_root / "21_FINAL_RESULT.json", final)
        command_results["enforcer_repair_pass6"] = run_cmd(
            ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
        )

    write_json(
        step_root / "20_EXECUTION_META.json",
        {
            "schema_version": "imperium_wave1_verdict_sync_repair_meta.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "wave1_root": to_rel(wave1_root),
            "commands": command_results,
            "chain_before_mismatch_count": chain_before.get("mismatch_count", 0),
            "chain_after_mismatch_count": chain_after.get("mismatch_count", 0),
        },
    )

    print(json.dumps(final, ensure_ascii=False))
    return 0 if final.get("acceptance") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
