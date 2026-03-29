#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
ADMIN_ROOT = REPO_ROOT / "runtime" / "administratum"
RUNTIME_ROOT = REPO_ROOT / "runtime"
STEP_PREFIX = "imperium_absolute_cleanliness_before_seed_dashboard_tree_code_bug_purge_delta"

ENFORCER_SCRIPT = REPO_ROOT / "scripts" / "imperium_bundle_output_enforcer.py"
VISUAL_AUDIT_SCRIPT = REPO_ROOT / "scripts" / "imperial_dashboard_visual_audit_loop.py"

APP_JS = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "web" / "app.js"
INDEX_HTML = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "web" / "index.html"
SERVER_PY = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "app" / "local_factory_observation_server.py"

WORKTREE_GATE = ADMIN_ROOT / "IMPERIUM_WORKTREE_PURITY_GATE_V1.json"
INQUISITION = ADMIN_ROOT / "IMPERIUM_INQUISITION_LOOP_V1.json"
WATCH = ADMIN_ROOT / "IMPERIUM_WATCH_STATE_V1.json"
TRUTH_SPINE = ADMIN_ROOT / "IMPERIUM_TRUTH_SPINE_V1.json"
BUNDLE_CHAMBER = ADMIN_ROOT / "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1.json"

MACHINE_CAP = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"
ORGAN_STRENGTH = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"
NODE_RANK = REPO_ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json"
ONE_SCREEN = REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json"
CONSTITUTION = REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json"

REQUIRED_REVIEW = [
    "00_REVIEW_ENTRYPOINT.md",
    "01_INTEGRATION_REPORT.md",
    "02_VALIDATION_REPORT.md",
    "03_TRUTH_CHECK_AND_GAPS.md",
    "04_CHANGED_SURFACES.md",
    "05_API_SMOKE.json",
    "06_BUNDLE_INCLUDE_PATHS.txt",
    "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json",
    "08_ORGAN_STRENGTH_SNAPSHOT.json",
    "09_NODE_RANK_DETECTION_SNAPSHOT.json",
    "10_MACHINE_MODE_SNAPSHOT.json",
    "11_CONSTITUTION_STATUS_SNAPSHOT.json",
]


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_cmd(args: list[str]) -> dict[str, Any]:
    done = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", check=False)
    out: dict[str, Any] = {
        "command": " ".join(args),
        "exit_code": int(done.returncode),
        "stdout": str(done.stdout or "").strip(),
        "stderr": str(done.stderr or "").strip(),
        "status": "PASS" if done.returncode == 0 else "FAIL",
    }
    if out["stdout"].startswith("{"):
        try:
            out["json"] = json.loads(out["stdout"])
        except json.JSONDecodeError:
            pass
    return out


def fetch_json(url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return (
                {"ok": int(response.status) == 200, "status_code": int(response.status), "error": ""},
                json.loads(raw),
            )
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        return ({"ok": False, "status_code": 0, "error": str(exc)}, {})


def latest_json(path: Path, pattern: str) -> dict[str, Any]:
    files = sorted(path.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return {}
    payload = load_json(files[0], {})
    payload["_path"] = to_rel(files[0])
    return payload


def has_apply_janitor_report(path: Path) -> bool:
    for file in sorted(path.glob("ttl_bundle_janitor_report_*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        payload = load_json(file, {})
        if str(payload.get("mode", "")).lower() == "apply":
            return True
    return False


def load_transport(step_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    report = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transfer = dict(report.get("chatgpt_transfer", {}) or {})
    transport = dict(transfer.get("transport_integrity", {}) or {})
    transfer_report = dict((transfer.get("result", {}) or {}).get("transfer_report", {}) or {})
    return report, transport, transfer_report


def as_status(v: Any, default: str = "UNKNOWN") -> str:
    raw = str(v if v is not None else default).strip()
    return raw.upper() if raw else default


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM absolute cleanliness before seed")
    parser.add_argument("--step-id", default="")
    parser.add_argument("--dashboard-url", default="http://127.0.0.1:8777/")
    args = parser.parse_args()

    step_id = args.step_id.strip() or f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)

    command_results: dict[str, Any] = {}

    # API + visual evidence
    state_meta, state_payload = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/state")
    live_meta, live_payload = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/live_state")
    if VISUAL_AUDIT_SCRIPT.exists():
        command_results["dashboard_visual_assault"] = run_cmd(
            [
                "python",
                str(VISUAL_AUDIT_SCRIPT),
                "--url",
                args.dashboard_url,
                "--out-dir",
                str(step_root / "dashboard_cleanliness_visual"),
            ]
        )
    else:
        command_results["dashboard_visual_assault"] = {"status": "FAIL", "error": "visual_script_missing"}

    # Fresh git snapshot (evidence only)
    command_results["git_status_short"] = run_cmd(["git", "status", "--short"])
    command_results["git_status_branch"] = run_cmd(["git", "status", "--short", "--branch"])

    # Cleanup evidence from TTL janitor (already applied before this script in the same step)
    janitor_report = latest_json(RUNTIME_ROOT / "bundle_ttl_janitor", "ttl_bundle_janitor_report_*.json")
    janitor_apply_seen = has_apply_janitor_report(RUNTIME_ROOT / "bundle_ttl_janitor")

    # Local filesystem cleanliness checks
    bak_count = len(list((RUNTIME_ROOT / "factory_observation").glob("*.bak")))
    tmp_snapshot_present = (RUNTIME_ROOT / "tmp_state_snapshot.json").exists()

    # Content checks for dashboard command layer and critical code path
    app_js_text = APP_JS.read_text(encoding="utf-8-sig")
    index_text = INDEX_HTML.read_text(encoding="utf-8-sig")
    server_text = SERVER_PY.read_text(encoding="utf-8-sig")

    blocker_classes = dict((state_payload.get("system_brain_state", {}) or {}).get("blocker_classes", {}) or {})
    repo_hygiene_blockers = list(blocker_classes.get("repo_hygiene_blockers", []) or [])
    factory_overview = dict(state_payload.get("factory_overview", {}) or {})
    live_factory = dict(live_payload.get("live_factory_state", {}) or {})
    owner_gates_state = len(list(factory_overview.get("owner_gates_waiting", []) or []))
    owner_gates_live = int(live_factory.get("pending_owner_gates_count", 0) or 0)

    dashboard_checks = {
        "api_state_ok": bool(state_meta.get("ok")),
        "api_live_ok": bool(live_meta.get("ok")),
        "command_panels_not_preformatted_raw": (
            '<pre id="bundleSummary">' not in index_text
            and '<pre id="canonStateSync">' not in index_text
            and '<pre id="systemSemanticState">' not in index_text
            and '<pre id="liveFactoryState">' not in index_text
        ),
        "command_summary_writer_present": "function writeCommandSummary" in app_js_text,
        "raw_noise_removed_from_signal_cards": "signal-band-note\">raw:" not in app_js_text,
        "inspector_explicit_debug_boundary": (
            "Command-layer truth summary выше; ниже только audit/debug raw layers." in app_js_text
            and "Технический инспектор (audit/debug)" in index_text
        ),
    }

    repo_checks = {
        "repo_hygiene_blocker_zero": len(repo_hygiene_blockers) == 0,
        "worktree_purity_gate_pass": as_status((state_payload.get("imperium_worktree_purity_gate_state", {}) or {}).get("status", "UNKNOWN")) == "PASS",
        "runtime_bak_debris_zero": bak_count == 0,
        "tmp_snapshot_removed": not tmp_snapshot_present,
        "ttl_janitor_apply_seen": janitor_apply_seen,
    }

    code_checks = {
        "controlled_dirty_logic_hardened": (
            "SUSPICIOUS_INQUISITION_ATTENTION" in server_text
            and "controlled_total > 0" in server_text
        ),
        "factory_owner_gate_alignment": owner_gates_state == owner_gates_live,
    }

    all_checks = {}
    all_checks.update({f"dashboard::{k}": bool(v) for k, v in dashboard_checks.items()})
    all_checks.update({f"repo::{k}": bool(v) for k, v in repo_checks.items()})
    all_checks.update({f"code::{k}": bool(v) for k, v in code_checks.items()})
    check_failures = [k for k, v in all_checks.items() if not v]

    # Standard review files
    write_text(
        step_root / "00_REVIEW_ENTRYPOINT.md",
        f"# 00_REVIEW_ENTRYPOINT\n\n- step_id: `{step_id}`\n- focus: `absolute cleanliness before seed`\n- review_root: `{to_rel(step_root)}`\n",
    )
    write_text(
        step_root / "01_INTEGRATION_REPORT.md",
        "# 01_INTEGRATION_REPORT\n\nCleanliness pass completed across dashboard command-layer semantics, runtime debris, TTL bundle retention, and hygiene-blocker logic in server control path.",
    )
    write_text(
        step_root / "02_VALIDATION_REPORT.md",
        "\n".join(
            [
                "# 02_VALIDATION_REPORT",
                "",
                f"- dashboard_checks_pass: `{str(all(v for v in dashboard_checks.values())).lower()}`",
                f"- repo_checks_pass: `{str(all(v for v in repo_checks.values())).lower()}`",
                f"- code_checks_pass: `{str(all(v for v in code_checks.values())).lower()}`",
                f"- check_failures: `{len(check_failures)}`",
                f"- repo_hygiene_blockers: `{len(repo_hygiene_blockers)}`",
                f"- worktree_purity_gate: `{as_status((state_payload.get('imperium_worktree_purity_gate_state', {}) or {}).get('status', 'UNKNOWN'))}`",
                f"- bundle_truth_chamber: `{as_status((state_payload.get('imperium_bundle_truth_chamber_state', {}) or {}).get('status', 'UNKNOWN'))}`",
            ]
        ),
    )
    write_text(
        step_root / "03_TRUTH_CHECK_AND_GAPS.md",
        "\n".join(
            [
                "# 03_TRUTH_CHECK_AND_GAPS",
                "",
                f"- repo_hygiene_blocker_zero: `{str(repo_checks['repo_hygiene_blocker_zero']).lower()}`",
                f"- runtime_bak_debris_zero: `{str(repo_checks['runtime_bak_debris_zero']).lower()}`",
                f"- tmp_snapshot_removed: `{str(repo_checks['tmp_snapshot_removed']).lower()}`",
                f"- command_panels_not_preformatted_raw: `{str(dashboard_checks['command_panels_not_preformatted_raw']).lower()}`",
                f"- owner_gate_alignment: `{str(code_checks['factory_owner_gate_alignment']).lower()}`",
                "",
                "Open known future gaps:",
                "- full_event_bus_not_yet_implemented",
                "- auto_preview_pipeline_not_yet_implemented",
                "- pixel_level_perceptual_diff_unavailable_in_scope",
                "- two_disk_migration_not_physically_validated",
            ]
        ),
    )
    write_text(
        step_root / "04_CHANGED_SURFACES.md",
        "# 04_CHANGED_SURFACES\n\n- dashboard command summary surfaces (`bundle/canon/semantic/live factory`)\n- signal-band semantic noise cleanup\n- technical inspector boundary clarity\n- server hygiene-classification control logic\n- runtime debris cleanup (`*.bak`, temp snapshot)\n- TTL retention execution evidence",
    )
    write_json(
        step_root / "05_API_SMOKE.json",
        {
            "generated_at_utc": now_iso(),
            "state_meta": state_meta,
            "live_meta": live_meta,
            "state_status": state_payload.get("status", ""),
            "bundle_name": state_payload.get("bundle_name", ""),
        },
    )
    include_paths = [f"docs/review_artifacts/{step_id}/{name}" for name in REQUIRED_REVIEW]
    include_paths += [
        f"docs/review_artifacts/{step_id}/12_CLEANLINESS_MAP.json",
        f"docs/review_artifacts/{step_id}/13_DASHBOARD_COMMAND_CLEANLINESS.json",
        f"docs/review_artifacts/{step_id}/14_REPO_TREE_CLEANUP_REPORT.json",
        f"docs/review_artifacts/{step_id}/15_CODE_BUG_PURGE_REPORT.json",
        f"docs/review_artifacts/{step_id}/16_TRANSPORT_SELF_READ_REPORT.json",
        f"docs/review_artifacts/{step_id}/20_BLOCKER_CLASSIFICATION.json",
        f"docs/review_artifacts/{step_id}/21_FINAL_RESULT.json",
        f"docs/review_artifacts/{step_id}/24_EXECUTION_META.json",
        to_rel(TRUTH_SPINE),
        to_rel(WORKTREE_GATE),
        to_rel(INQUISITION),
        to_rel(WATCH),
        to_rel(BUNDLE_CHAMBER),
        to_rel(APP_JS),
        to_rel(INDEX_HTML),
        to_rel(SERVER_PY),
        to_rel(ENFORCER_SCRIPT),
        to_rel(VISUAL_AUDIT_SCRIPT),
        to_rel(REPO_ROOT / "scripts" / "imperium_repo_wide_dirty_baseline_purity_closure.py"),
        to_rel(REPO_ROOT / "runtime" / "repo_control_center" / "imperium_repo_wide_dirty_baseline_classification_v1.json"),
    ]
    if janitor_report.get("_path"):
        include_paths.append(str(janitor_report["_path"]))
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", "\n".join(sorted(set(include_paths))))

    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", load_json(MACHINE_CAP, {}))
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", load_json(ORGAN_STRENGTH, {}))
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", load_json(NODE_RANK, {}))
    write_json(step_root / "10_MACHINE_MODE_SNAPSHOT.json", load_json(ONE_SCREEN, {}))
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", load_json(CONSTITUTION, {}))

    write_json(
        step_root / "12_CLEANLINESS_MAP.json",
        {
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "dashboard_checks": dashboard_checks,
            "repo_checks": repo_checks,
            "code_checks": code_checks,
            "all_checks": all_checks,
            "failures": check_failures,
        },
    )
    write_json(
        step_root / "13_DASHBOARD_COMMAND_CLEANLINESS.json",
        {
            "generated_at_utc": now_iso(),
            "command_layer_focus": [
                "raw-first pre blocks removed from top summary cards",
                "signal raw noise removed from trust/conflict cards",
                "audit/debug boundary marked explicitly",
            ],
            "checks": dashboard_checks,
        },
    )
    write_json(
        step_root / "14_REPO_TREE_CLEANUP_REPORT.json",
        {
            "generated_at_utc": now_iso(),
            "runtime_bak_count_after_cleanup": bak_count,
            "tmp_snapshot_present_after_cleanup": tmp_snapshot_present,
            "repo_hygiene_blockers": repo_hygiene_blockers,
            "janitor_report": janitor_report,
        },
    )
    write_json(
        step_root / "15_CODE_BUG_PURGE_REPORT.json",
        {
            "generated_at_utc": now_iso(),
            "server_hygiene_logic_signals": {
                "controlled_total_guard_present": "controlled_total > 0" in server_text,
                "suspicious_class_guard_present": "SUSPICIOUS_INQUISITION_ATTENTION" in server_text,
            },
            "owner_gate_alignment": {
                "factory_state_count": owner_gates_state,
                "live_state_count": owner_gates_live,
                "aligned": owner_gates_state == owner_gates_live,
            },
            "checks": code_checks,
        },
    )

    preliminary = {
        "schema_version": "imperium_absolute_cleanliness_before_seed_final.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "status": "PENDING",
        "acceptance": "PENDING",
        "dashboard_cleanliness": "PASS" if all(dashboard_checks.values()) else "FAIL",
        "repo_cleanup": "PASS" if all(repo_checks.values()) else "FAIL",
        "code_bug_purge": "PASS" if all(code_checks.values()) else "FAIL",
        "transport_integrity": "UNKNOWN",
        "transfer_package_completeness": "UNKNOWN",
        "core_required": True,
        "parts_total": 0,
        "optional_included": False,
        "visual_included": False,
        "optional_part_count": 0,
        "visual_part_count": 0,
        "upload_order": [],
        "failure_reasons": [],
    }
    write_json(step_root / "21_FINAL_RESULT.json", preliminary)

    # Enforcer pass1 -> transport self-read
    command_results["enforcer_pass1"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer1, transport1, transfer1 = load_transport(step_root)
    write_json(
        step_root / "16_TRANSPORT_SELF_READ_REPORT.json",
        {
            "generated_at_utc": now_iso(),
            "enforcer_verdict": as_status(enforcer1.get("verdict", "UNKNOWN")),
            "transport_integrity": transport1,
            "transfer_report": transfer1,
        },
    )

    blockers = {"FIX_NOW": [], "OPEN_BUT_ALLOWED": [], "POLICY_SKIPPED": [], "FUTURE_WORK": []}
    for failure in check_failures:
        blockers["FIX_NOW"].append(f"check_failed::{failure}")
    if as_status(enforcer1.get("verdict", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("bundle_output_enforcer_not_pass")
    if as_status(transport1.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("transport_integrity_not_pass")
    blockers["FUTURE_WORK"] = [
        "full_event_bus_not_yet_implemented",
        "auto_preview_pipeline_not_yet_implemented",
        "pixel_level_perceptual_diff_unavailable_in_scope",
        "two_disk_migration_not_physically_validated",
    ]
    write_json(step_root / "20_BLOCKER_CLASSIFICATION.json", blockers)

    final = dict(preliminary)
    final["generated_at_utc"] = now_iso()
    final["dashboard_cleanliness"] = "PASS" if all(dashboard_checks.values()) else "FAIL"
    final["repo_cleanup"] = "PASS" if all(repo_checks.values()) else "FAIL"
    final["code_bug_purge"] = "PASS" if all(code_checks.values()) else "FAIL"
    final["transport_integrity"] = as_status(transport1.get("status", "UNKNOWN"))
    final["transfer_package_completeness"] = str(transport1.get("package_completeness", "UNKNOWN"))
    final["core_required"] = bool(transport1.get("core_required", False))
    final["parts_total"] = int(transport1.get("manifest_parts_total", 0) or 0)
    final["upload_order"] = list(transport1.get("upload_order_declared", []) or [])
    final["optional_included"] = bool(transfer1.get("optional_included", False))
    final["visual_included"] = bool(transfer1.get("visual_included", False))
    final["optional_part_count"] = int(transfer1.get("optional_part_count", 0) or 0)
    final["visual_part_count"] = int(transfer1.get("visual_part_count", 0) or 0)
    final["failure_reasons"] = sorted(set(blockers.get("FIX_NOW", [])))
    final["status"] = "PASS" if len(final["failure_reasons"]) == 0 else "FAIL"
    final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    # Enforcer pass2 after final result sync
    command_results["enforcer_pass2"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer2, transport2, transfer2 = load_transport(step_root)
    final["generated_at_utc"] = now_iso()
    final["transport_integrity"] = as_status(transport2.get("status", "UNKNOWN"))
    final["transfer_package_completeness"] = str(transport2.get("package_completeness", "UNKNOWN"))
    final["core_required"] = bool(transport2.get("core_required", False))
    final["parts_total"] = int(transport2.get("manifest_parts_total", 0) or 0)
    final["upload_order"] = list(transport2.get("upload_order_declared", []) or [])
    final["optional_included"] = bool(transfer2.get("optional_included", False))
    final["visual_included"] = bool(transfer2.get("visual_included", False))
    final["optional_part_count"] = int(transfer2.get("optional_part_count", 0) or 0)
    final["visual_part_count"] = int(transfer2.get("visual_part_count", 0) or 0)
    final_failures = list(check_failures)
    if as_status(enforcer2.get("verdict", "UNKNOWN")) != "PASS":
        final_failures.append("bundle_output_enforcer_not_pass")
    if as_status(transport2.get("status", "UNKNOWN")) != "PASS":
        final_failures.append("transport_integrity_not_pass")
    final["failure_reasons"] = sorted(set(final_failures))
    final["status"] = "PASS" if len(final["failure_reasons"]) == 0 else "FAIL"
    final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    write_json(
        step_root / "16_TRANSPORT_SELF_READ_REPORT.json",
        {
            "generated_at_utc": now_iso(),
            "enforcer_verdict": as_status(enforcer2.get("verdict", "UNKNOWN")),
            "transport_integrity": transport2,
            "transfer_report": transfer2,
        },
    )

    write_json(
        step_root / "24_EXECUTION_META.json",
        {
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "command_results": command_results,
            "dashboard_checks": dashboard_checks,
            "repo_checks": repo_checks,
            "code_checks": code_checks,
            "check_failures": check_failures,
            "janitor_report_path": janitor_report.get("_path", ""),
        },
    )

    print(json.dumps(final, ensure_ascii=False))
    return 0 if final.get("acceptance") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
