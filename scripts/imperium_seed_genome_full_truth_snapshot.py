#!/usr/bin/env python
from __future__ import annotations

import io
import json
import shutil
import subprocess
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
CAPSULE_ROOT = REVIEW_ROOT / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
BUILD_SEED_SCRIPT = REPO_ROOT / "scripts" / "build_seed_genome_working_folder.py"
ENFORCER_SCRIPT = REPO_ROOT / "scripts" / "imperium_bundle_output_enforcer.py"

STEP_PREFIX = "imperium_seed_genome_full_truth_snapshot_dirty_state_mirror_chat_relocation_mode_delta"
SEED_FOLDER_NAME = "SEED_GENOME_WORKING_FOLDER_V1"
DASHBOARD_URL = "http://127.0.0.1:8777"

SNAPSHOT_PATHS = [
    "docs/governance",
    "docs/INSTRUCTION_INDEX.md",
    "docs/NEXT_CANONICAL_STEP.md",
    "README.md",
    "MACHINE_CONTEXT.md",
    "REPO_MAP.md",
    "runtime/administratum",
    "runtime/repo_control_center",
    "runtime/imperium_force",
    "shared_systems/factory_observation_window_v1/adapters",
]

STALE_PATTERNS = [
    "imperium_living_spatial_brain_of_imperium_delta_primary_truth_bundle_latest.zip",
    "IMPERIUM_LIVING_SPATIAL_BRAIN_OF_IMPERIUM",
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


def write_json(path: Path, payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def write_text(path: Path, content: str) -> bool:
    text = content.rstrip() + "\n"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def run_cmd(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    out: dict[str, Any] = {
        "command": " ".join(args),
        "exit_code": int(proc.returncode),
        "stdout": str(proc.stdout or "").strip(),
        "stderr": str(proc.stderr or "").strip(),
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
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return (
                {"ok": int(response.status) == 200, "status_code": int(response.status), "error": ""},
                json.loads(raw),
            )
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return ({"ok": False, "status_code": 0, "error": str(exc)}, {})


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    for enc in ("utf-8-sig", "utf-8", "cp1251", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def ensure_seed_base(step_root: Path) -> None:
    result = run_cmd(
        [
            "python",
            str(BUILD_SEED_SCRIPT),
            "--step-root",
            to_rel(step_root),
            "--capsule-root",
            to_rel(CAPSULE_ROOT),
            "--output-name",
            SEED_FOLDER_NAME,
        ]
    )
    if result["exit_code"] not in {0, 2}:
        raise RuntimeError(result["stderr"] or result["stdout"])


def copy_into_seed(seed_root: Path, rel_path: str) -> str:
    src = (REPO_ROOT / rel_path).resolve()
    dst = seed_root / "FULL_TRUTH_SNAPSHOT" / rel_path
    if not src.exists():
        return f"missing::{rel_path}"
    if dst.exists():
        if dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_file():
        shutil.copy2(src, dst)
    else:
        shutil.copytree(src, dst)
    return f"copied::{rel_path}"


def latest_review_roots(limit: int) -> list[Path]:
    roots = [p for p in REVIEW_ROOT.iterdir() if p.is_dir() and p.name != "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"]
    roots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return roots[:limit]


def copy_review_summaries(seed_root: Path, roots: list[Path]) -> list[str]:
    keep = {
        "00_REVIEW_ENTRYPOINT.md",
        "01_INTEGRATION_REPORT.md",
        "02_VALIDATION_REPORT.md",
        "03_TRUTH_CHECK_AND_GAPS.md",
        "20_BLOCKER_CLASSIFICATION.json",
        "21_FINAL_RESULT.json",
    }
    copied: list[str] = []
    for root in roots:
        out_dir = seed_root / "CURRENT_REVIEW_MIRROR" / root.name
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in keep:
            src = root / name
            if not src.exists():
                continue
            dst = out_dir / name
            shutil.copy2(src, dst)
            copied.append(to_rel(dst))
    write_json(
        seed_root / "CURRENT_REVIEW_MIRROR" / "00_REVIEW_ROOT_INDEX.json",
        {
            "schema_version": "imperium_seed_review_root_index.v1",
            "generated_at_utc": now_iso(),
            "review_roots": [to_rel(x) for x in roots],
            "copied_summary_files": copied,
        },
    )
    return copied


def get_git_dirty() -> dict[str, Any]:
    status = run_cmd(["git", "status", "--porcelain"])
    lines = [x for x in str(status["stdout"]).splitlines() if x.strip()]
    tracked = [x for x in lines if not x.startswith("??")]
    untracked = [x for x in lines if x.startswith("??")]
    return {
        "total_entries": len(lines),
        "tracked_entries": len(tracked),
        "untracked_entries": len(untracked),
        "sample_entries": lines[:120],
    }


def evaluate_sync(seed_root: Path, mutable: dict[str, Any]) -> dict[str, Any]:
    continuity = str(((mutable.get("continuity_step_primary_truth", {}) or {}).get("path", "")))
    handoff = str(((mutable.get("handoff_step_primary_truth_input", {}) or {}).get("path", "")))
    active = str(((mutable.get("active_live_primary_line", {}) or {}).get("path", "")))
    vertex = str(((mutable.get("current_active_vertex", {}) or {}).get("id", "")))
    checks: dict[str, list[str]] = {
        "00_CAPSULE_ENTRYPOINT.md": [continuity, handoff, active],
        "08_CURRENT_POINT_VERIFICATION.md": [continuity, handoff, active, vertex],
        "for_chatgpt/01_PASTE_THIS_FULL.md": [continuity, handoff, active, vertex],
        "for_chatgpt/02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md": [continuity, handoff, active, vertex],
        "for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md": [continuity, handoff, active, vertex],
    }
    sync_failures: list[str] = []
    for rel, expected in checks.items():
        text = read_text(seed_root / rel)
        if not text:
            sync_failures.append(f"missing::{rel}")
            continue
        for value in expected:
            if value and value not in text:
                sync_failures.append(f"sync_mismatch::{rel}::{value}")
    stale_check_paths = [
        "00_CAPSULE_ENTRYPOINT.md",
        "02_MUTABLE_ACTIVE_STATE.md",
        "06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md",
        "08_CURRENT_POINT_VERIFICATION.md",
        "for_chatgpt/01_PASTE_THIS_FULL.md",
        "for_chatgpt/02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md",
        "for_chatgpt/05_CURRENT_BUNDLE_POINTERS.md",
        "for_chatgpt/07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md",
        "for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md",
    ]
    stale_hits: list[str] = []
    for rel in stale_check_paths:
        item = seed_root / rel
        text = read_text(item)
        if not text:
            continue
        for pattern in STALE_PATTERNS:
            if pattern in text:
                stale_hits.append(f"{to_rel(item)}::{pattern}")
    status = "PASS" if not sync_failures and not stale_hits else "FAIL"
    return {
        "schema_version": "imperium_seed_correspondence.v1",
        "generated_at_utc": now_iso(),
        "status": status,
        "current_point": {
            "continuity_line": continuity,
            "handoff_line": handoff,
            "active_line": active,
            "active_vertex": vertex,
        },
        "sync_failures": sync_failures,
        "stale_hits": stale_hits,
    }


def run_enforcer(step_root: Path) -> dict[str, Any]:
    result = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root)])
    if result["exit_code"] != 0:
        raise RuntimeError(result["stderr"] or result["stdout"])
    return load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})


def extract_manifest(report: dict[str, Any]) -> dict[str, Any]:
    rel = str((((report.get("chatgpt_transfer", {}) or {}).get("result", {}) or {}).get("transfer_report", {}).get("manifest_json", "")).strip())
    if not rel:
        return {}
    return load_json(REPO_ROOT / rel, {})


def core_entries(manifest: dict[str, Any]) -> list[str]:
    transfer_root = str(manifest.get("transfer_root", "")).strip()
    upload_order = [str(x).strip() for x in list(manifest.get("upload_order", []) or []) if str(x).strip()]
    core = next((x for x in upload_order if "__core_chatgpt_transfer.part" in x), "")
    if not transfer_root or not core:
        return []
    part_path = (REPO_ROOT / transfer_root / core).resolve()
    if not part_path.exists():
        return []
    blob = part_path.read_bytes()
    try:
        with zipfile.ZipFile(io.BytesIO(blob), "r") as zf:
            return sorted(name.replace("\\", "/").strip("/") for name in zf.namelist())
    except Exception:
        return []


def transport_self_read(step_id: str, step_root: Path, report: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    integrity = dict((report.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}))
    entries = core_entries(manifest)
    entry_set = set(entries)
    root_rel = to_rel(step_root)
    checks = {
        "transport_integrity_pass": str(integrity.get("status", "FAIL")).upper() == "PASS",
        "entrypoint_present": f"{root_rel}/00_REVIEW_ENTRYPOINT.md" in entry_set,
        "final_result_present": f"{root_rel}/21_FINAL_RESULT.json" in entry_set,
        "seed_entrypoint_present": f"{root_rel}/{SEED_FOLDER_NAME}/00_SEED_GENOME_ENTRYPOINT.md" in entry_set,
        "seed_for_chatgpt_present": f"{root_rel}/{SEED_FOLDER_NAME}/for_chatgpt/01_PASTE_THIS_FULL.md" in entry_set,
        "seed_for_codex_present": f"{root_rel}/{SEED_FOLDER_NAME}/for_codex/01_CODEX_BOOTSTRAP_NOTE.md" in entry_set,
        "seed_mutable_tracker_present": f"{root_rel}/{SEED_FOLDER_NAME}/MUTABLE_TRACKER.json" in entry_set,
        "foreign_roots_absent": len(list(integrity.get("foreign_review_roots", []) or [])) == 0,
    }
    fails = [k for k, v in checks.items() if not v]
    return {
        "schema_version": "imperium_seed_transport_self_read.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": root_rel,
        "status": "PASS" if not fails else "FAIL",
        "enforcer_verdict": str(report.get("verdict", "UNKNOWN")).upper(),
        "transport_integrity_status": str(integrity.get("status", "UNKNOWN")).upper(),
        "core_entry_count": len(entries),
        "checks": checks,
        "failures": fails,
    }


def write_standard_files(step_id: str, step_root: Path, seed_root: Path, api_smoke: dict[str, Any], corr: dict[str, Any], dirty: dict[str, Any]) -> None:
    write_text(step_root / "00_REVIEW_ENTRYPOINT.md", f"# 00_REVIEW_ENTRYPOINT\n\n- step_id: `{step_id}`\n- review_root: `{to_rel(step_root)}`\n- seed_root: `{to_rel(seed_root)}`\n- mode: `full-truth current-state mirror`\n")
    write_text(step_root / "01_INTEGRATION_REPORT.md", "# 01_INTEGRATION_REPORT\n\nBuilt a self-contained seed-genome mirror that carries current canon + mutable + runtime/dashboard/control truth layers, including open debt/dirty state.")
    write_text(step_root / "02_VALIDATION_REPORT.md", f"# 02_VALIDATION_REPORT\n\n- correspondence_status: `{corr.get('status','FAIL')}`\n- sync_failures: `{len(corr.get('sync_failures',[]) or [])}`\n- stale_hits: `{len(corr.get('stale_hits',[]) or [])}`\n- api_state_ok: `{str(bool(api_smoke.get('api_state_ok',False))).lower()}`\n- api_live_ok: `{str(bool(api_smoke.get('api_live_ok',False))).lower()}`\n")
    write_text(step_root / "03_TRUTH_CHECK_AND_GAPS.md", "# 03_TRUTH_CHECK_AND_GAPS\n\nThis step mirrors current Imperium state exactly (including unresolved/dirty realities) for relocation-grade continuity.\n\nOpen-but-mirrored conditions remain visible in `20_BLOCKER_CLASSIFICATION.json`.")
    write_text(step_root / "04_CHANGED_SURFACES.md", "# 04_CHANGED_SURFACES\n\n- seed genome working folder rebuilt\n- full truth snapshot sublayer injected\n- dirty/open-state mirror injected\n- transfer enforcement and self-read surfaces refreshed")
    write_json(step_root / "05_API_SMOKE.json", api_smoke)
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", f"# self-contained seed root\n{to_rel(seed_root)}")
    write_text(step_root / "14_ARCHIVE_INCLUDE_PATHS.txt", "# no extra external include roots")


def write_standard_snapshots(step_root: Path) -> None:
    machine_cap = load_json(REPO_ROOT / "runtime/imperium_force/IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json", {})
    organ = load_json(REPO_ROOT / "runtime/imperium_force/IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json", {})
    node = load_json(REPO_ROOT / "runtime/repo_control_center/validation/node_rank_detection.json", {})
    one_screen = load_json(REPO_ROOT / "runtime/repo_control_center/one_screen_status.json", {})
    constitution = load_json(REPO_ROOT / "runtime/repo_control_center/constitution_status.json", {})
    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", machine_cap)
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", organ)
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", node)
    write_json(step_root / "10_MACHINE_MODE_SNAPSHOT.json", {
        "schema_version": "imperium_machine_mode_snapshot.v1",
        "generated_at_utc": now_iso(),
        "machine_mode": str(one_screen.get("machine_mode", "UNKNOWN")),
        "rank": str(one_screen.get("rank", "UNKNOWN")),
    })
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", constitution)


def build_final_result(step_id: str, step_root: Path, report: dict[str, Any], manifest: dict[str, Any], corr: dict[str, Any], seed_audit: dict[str, Any], self_read: dict[str, Any], blockers: dict[str, Any]) -> dict[str, Any]:
    integrity = dict((report.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}))
    fail_reasons: list[str] = []
    if str(report.get("verdict", "FAIL")).upper() != "PASS":
        fail_reasons.append("bundle_enforcer_not_pass")
    if str(integrity.get("status", "FAIL")).upper() != "PASS":
        fail_reasons.append("transport_integrity_not_pass")
    if str(self_read.get("status", "FAIL")).upper() != "PASS":
        fail_reasons.append("transport_self_read_not_pass")
    if str(corr.get("status", "FAIL")).upper() != "PASS":
        fail_reasons.append("current_state_correspondence_not_pass")
    if str(seed_audit.get("status", "FAIL")).upper() != "PASS":
        fail_reasons.append("seed_inquisition_not_pass")
    if any(str(x.get("class", "")).upper() == "FIX_NOW" for x in list(blockers.get("blockers", []) or [])):
        fail_reasons.append("unresolved_fix_now_blockers")
    status = "PASS" if not fail_reasons else "FAIL"
    return {
        "schema_version": "imperium_seed_genome_full_truth_snapshot_final.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "status": status,
        "acceptance": status,
        "current_state_correspondence": str(corr.get("status", "FAIL")).upper(),
        "seed_inquisition_audit": str(seed_audit.get("status", "FAIL")).upper(),
        "bundle_enforcer_verdict": str(report.get("verdict", "FAIL")).upper(),
        "transport_integrity": str(integrity.get("status", "FAIL")).upper(),
        "transport_self_read": str(self_read.get("status", "FAIL")).upper(),
        "transfer_package_completeness": str(manifest.get("package_completeness", "PARTIAL")),
        "core_required": bool(manifest.get("core_required", False)),
        "parts_total": int(manifest.get("parts_total", 0) or 0),
        "optional_included": bool(manifest.get("optional_included", False)),
        "visual_included": bool(manifest.get("visual_included", False)),
        "upload_order": [str(x).strip() for x in list(manifest.get("upload_order", []) or []) if str(x).strip()],
        "failure_reasons": fail_reasons,
    }


def main() -> int:
    step_id = f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)

    ensure_seed_base(step_root)
    seed_root = step_root / SEED_FOLDER_NAME

    copied = [copy_into_seed(seed_root, rel) for rel in SNAPSHOT_PATHS]
    copied_reviews = copy_review_summaries(seed_root, latest_review_roots(8))

    mutable = load_json(CAPSULE_ROOT / "MUTABLE_TRACKER.json", {})
    corr = evaluate_sync(seed_root, mutable)
    write_json(seed_root / "92_CURRENT_STATE_CORRESPONDENCE_PROOF.json", corr)
    write_text(seed_root / "92_CURRENT_STATE_CORRESPONDENCE_PROOF.md", f"# 92_CURRENT_STATE_CORRESPONDENCE_PROOF\n\n- status: `{corr['status']}`\n- sync_failures: `{len(corr['sync_failures'])}`\n- stale_hits: `{len(corr['stale_hits'])}`\n")

    dirty = get_git_dirty()
    watch = load_json(REPO_ROOT / "runtime/administratum/IMPERIUM_WATCH_STATE_V1.json", {})
    inq = load_json(REPO_ROOT / "runtime/administratum/IMPERIUM_INQUISITION_LOOP_V1.json", {})
    dirty_mirror = {
        "schema_version": "imperium_seed_dirty_state_mirror.v1",
        "generated_at_utc": now_iso(),
        "repo_dirty_state": dirty,
        "watch_open_blockers": list(watch.get("open_blockers", []) or []),
        "watch_open_risks": list(watch.get("open_risks", []) or []),
        "mutable_open_risks": list(mutable.get("open_risks", []) or []),
        "inquisition_status": str(inq.get("status", "UNKNOWN")),
        "mirrored": True,
    }
    write_json(seed_root / "93_DIRTY_STATE_MIRROR.json", dirty_mirror)
    write_text(seed_root / "93_DIRTY_STATE_MIRROR.md", f"# 93_DIRTY_STATE_MIRROR\n\n- entries_mirrored: `{dirty['total_entries']}`\n- open_risks: `{len(dirty_mirror['watch_open_risks'])}`\n")

    write_text(
        seed_root / "00_SEED_GENOME_ENTRYPOINT.md",
        "\n".join(
            [
                "# 00_SEED_GENOME_ENTRYPOINT",
                "",
                "Self-contained current-state seed genome for relocation/new chat.",
                "This mirrors current Imperium truth including open debt/dirty state.",
                "",
                "Read order:",
                "1. for_chatgpt/01_PASTE_THIS_FULL.md",
                "2. for_codex/01_CODEX_BOOTSTRAP_NOTE.md",
                "3. 08_CURRENT_POINT_VERIFICATION.md",
                "4. 92_CURRENT_STATE_CORRESPONDENCE_PROOF.md",
                "5. 93_DIRTY_STATE_MIRROR.md",
                "",
                f"- active_line: `{corr['current_point']['active_line']}`",
                f"- active_vertex: `{corr['current_point']['active_vertex']}`",
                f"- generated_utc: `{now_iso()}`",
            ]
        ),
    )

    api_state_meta, api_state_payload = fetch_json(f"{DASHBOARD_URL}/api/state")
    api_live_meta, api_live_payload = fetch_json(f"{DASHBOARD_URL}/api/live_state")
    api_smoke = {
        "schema_version": "imperium_seed_api_smoke.v1",
        "generated_at_utc": now_iso(),
        "dashboard_url": DASHBOARD_URL,
        "api_state_ok": bool(api_state_meta["ok"]),
        "api_live_ok": bool(api_live_meta["ok"]),
        "api_state_status_code": int(api_state_meta["status_code"]),
        "api_live_status_code": int(api_live_meta["status_code"]),
        "api_state_error": str(api_state_meta["error"]),
        "api_live_error": str(api_live_meta["error"]),
        "api_state_payload_keys": sorted(list(api_state_payload.keys()))[:20],
        "api_live_payload_keys": sorted(list(api_live_payload.keys()))[:20],
    }

    blockers = {"schema_version": "imperium_blockers.v1", "generated_at_utc": now_iso(), "step_id": step_id, "blockers": []}
    if not (api_smoke["api_state_ok"] and api_smoke["api_live_ok"]):
        blockers["blockers"].append({"class": "OPEN_BUT_ALLOWED", "id": "dashboard_api_unreachable_during_snapshot", "reason": "file-based authoritative surfaces were mirrored"})
    if dirty["total_entries"] > 0:
        blockers["blockers"].append({"class": "OPEN_BUT_ALLOWED", "id": "repo_dirty_state_mirrored", "reason": "step mirrors current state without cleanup frontier"})
    if corr["status"] != "PASS":
        blockers["blockers"].append({"class": "FIX_NOW", "id": "seed_current_point_mismatch", "reason": "seed files diverge from mutable tracker"})
    blockers["status"] = "PASS" if not [x for x in blockers["blockers"] if x["class"] == "FIX_NOW"] else "FAIL"

    write_standard_files(step_id, step_root, seed_root, api_smoke, corr, dirty_mirror)
    write_standard_snapshots(step_root)
    write_json(step_root / "13_CURRENT_STATE_CORRESPONDENCE_PROOF.json", corr)
    write_text(step_root / "13_CURRENT_STATE_CORRESPONDENCE_PROOF.md", f"# 13_CURRENT_STATE_CORRESPONDENCE_PROOF\n\n- status: `{corr['status']}`\n- sync_failures: `{len(corr['sync_failures'])}`\n- stale_hits: `{len(corr['stale_hits'])}`\n")
    write_json(step_root / "20_BLOCKER_CLASSIFICATION.json", blockers)
    write_json(step_root / "05_API_SMOKE.json", api_smoke)
    write_json(step_root / "21_FINAL_RESULT.json", {
        "schema_version": "imperium_seed_genome_full_truth_snapshot_final.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "status": "FAIL",
        "acceptance": "FAIL",
        "transfer_package_completeness": "PARTIAL",
        "core_required": True,
        "parts_total": 0,
        "optional_included": False,
        "visual_included": False,
        "upload_order": [],
        "failure_reasons": ["bootstrap_pending_enforcer"],
    })

    write_json(
        step_root / "24_EXECUTION_META.json",
        {
            "schema_version": "imperium_seed_snapshot_execution_meta.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "copied_truth_surfaces": copied,
            "copied_recent_review_summaries": copied_reviews,
        },
    )

    for _ in range(5):
        report = run_enforcer(step_root)
        manifest = extract_manifest(report)
        seed_audit = load_json(seed_root / "90_INQUISITION_SEED_TRUTH_AUDIT.json", {})
        self_read = transport_self_read(step_id, step_root, report, manifest)
        final = build_final_result(step_id, step_root, report, manifest, corr, seed_audit, self_read, blockers)
        changed = False
        changed = write_json(step_root / "16_TRANSPORT_SELF_READ_REPORT.json", self_read) or changed
        changed = write_json(step_root / "21_FINAL_RESULT.json", final) or changed
        if not changed:
            break

    report = run_enforcer(step_root)
    manifest = extract_manifest(report)
    seed_audit = load_json(seed_root / "90_INQUISITION_SEED_TRUTH_AUDIT.json", {})
    self_read = transport_self_read(step_id, step_root, report, manifest)
    final = build_final_result(step_id, step_root, report, manifest, corr, seed_audit, self_read, blockers)
    write_json(step_root / "16_TRANSPORT_SELF_READ_REPORT.json", self_read)
    write_json(step_root / "21_FINAL_RESULT.json", final)
    report = run_enforcer(step_root)
    final_status = str(final.get("status", "FAIL")).upper()

    print(
        json.dumps(
            {
                "status": final_status.lower(),
                "step_id": step_id,
                "review_root": to_rel(step_root),
                "enforcer_verdict": str(report.get("verdict", "UNKNOWN")),
            },
            ensure_ascii=False,
        )
    )
    return 0 if final_status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
