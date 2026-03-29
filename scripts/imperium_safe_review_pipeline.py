#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUEST_ROOT = REPO_ROOT / "runtime" / "chatgpt_bundle_requests"
EXPORT_ROOT = REPO_ROOT / "runtime" / "chatgpt_bundle_exports"
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def export_lane(topic: str, include_file: Path, output_dir: Path, summary: str, dry_run: bool) -> dict[str, Any]:
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
        "imperium_safe_review_pipeline_default",
        "--summary",
        summary,
    ]
    if dry_run:
        return {
            "lane_topic": topic,
            "dry_run": True,
            "command": " ".join(cmd),
            "exit_code": 0,
            "safe_to_share_with_chatgpt": False,
        }
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload: dict[str, Any] = {
        "lane_topic": topic,
        "command": " ".join(cmd),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    out = str(completed.stdout or "").strip()
    if out.startswith("{"):
        try:
            payload.update(json.loads(out))
        except json.JSONDecodeError:
            pass
    return payload


def lane_definitions() -> list[dict[str, Any]]:
    return [
        {
            "id": "01_repo_cleanliness_and_git_truth",
            "summary": "Fresh branch/head/status/diff/stash truth with no mutation.",
            "include": [
                "scripts/imperium_safe_review_pipeline.py",
                "runtime/repo_control_center/repo_control_status.json",
                "runtime/repo_control_center/one_screen_status.json",
                "runtime/repo_control_center/plain_status.md",
                "docs/review_artifacts/imperium_deep_review_safeplus_followup_set_20260326T181339Z/01_repo_cleanliness_and_git_truth/REPO_CLEANLINESS_AND_GIT_TRUTH_REPORT.md",
            ],
        },
        {
            "id": "02_code_bank_inventory_anomaly_and_growth",
            "summary": "Code-bank mass, monolith concentration, anomaly ledger.",
            "include": [
                "scripts/refresh_imperium_code_bank_surface.py",
                "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json",
                "shared_systems/factory_observation_window_v1/app/local_factory_observation_server.py",
                "shared_systems/factory_observation_window_v1/web/app.js",
                "shared_systems/factory_observation_window_v1/web/styles.css",
            ],
        },
        {
            "id": "03_dashboard_source_truth_and_brain_surface_map",
            "summary": "Source map for Brain/Factory/Custodes/Inquisition and dashboard render paths.",
            "include": [
                "shared_systems/factory_observation_window_v1/web/index.html",
                "shared_systems/factory_observation_window_v1/web/app.js",
                "shared_systems/factory_observation_window_v1/web/styles.css",
                "shared_systems/factory_observation_window_v1/app/local_factory_observation_server.py",
                "shared_systems/factory_observation_window_v1/adapters/TIKTOK_BUNDLE_ADAPTER_V1.json",
                "shared_systems/factory_observation_window_v1/adapters/TIKTOK_DASHBOARD_PANEL_REGISTRY_V1.json",
            ],
        },
        {
            "id": "04_dashboard_coverage_matrix_full_imperium",
            "summary": "Coverage matrix rows with exact/derived/pointer/missing disclosure.",
            "include": [
                "scripts/refresh_imperium_dashboard_coverage_surface.py",
                "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json",
                "shared_systems/factory_observation_window_v1/adapters/SYSTEM_SEMANTIC_STATE_SURFACES_V1.json",
                "shared_systems/factory_observation_window_v1/web/index.html",
            ],
        },
        {
            "id": "05_runtime_freshness_authority_and_dominance_reconciliation",
            "summary": "Freshness/authority winner rules and stale-mix warnings.",
            "include": [
                "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_TRUTH_DOMINANCE_SURFACE_V1.json",
                "runtime/repo_control_center/one_screen_status.json",
                "runtime/repo_control_center/repo_control_status.json",
                "runtime/operator_command_layer/command_surface_status.json",
                "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVENT_FLOW_SPINE_SURFACE_V1.json",
                "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_V1.json",
            ],
        },
        {
            "id": "06_safe_review_bundle_pipeline_design_and_operator_flow",
            "summary": "Owner-runnable safe review pipeline contract and flow docs.",
            "include": [
                "scripts/imperium_safe_review_pipeline.py",
                "scripts/export_manual_safe_bundle.py",
                "docs/governance/IMPERIUM_SAFE_REVIEW_PIPELINE_CANON_V1.md",
                "docs/review_artifacts/IMPERIUM_SAFE_REVIEW_PIPELINE_OPERATOR_FLOW_V1.md",
            ],
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Owner-runnable IMPERIUM Safe Review Bundle Pipeline (manual-safe).")
    parser.add_argument("--set-id", default="", help="Optional set id override")
    parser.add_argument("--dry-run", action="store_true", help="Only generate include files and indexes")
    args = parser.parse_args()

    stamp = utc_stamp()
    set_id = args.set_id.strip() or f"imperium_safe_review_pipeline_set_{stamp}"
    request_dir = REQUEST_ROOT / set_id
    export_dir = EXPORT_ROOT / set_id
    review_dir = REVIEW_ROOT / set_id
    request_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    lane_results: list[dict[str, Any]] = []
    lane_map: dict[str, Any] = {}

    for lane in lane_definitions():
        lane_id = str(lane["id"])
        include_lines = [normalize(path) for path in lane.get("include", [])]
        include_path = request_dir / f"{lane_id}_include.txt"
        write_text(include_path, "\n".join(include_lines))
        result = export_lane(
            topic=lane_id,
            include_file=include_path,
            output_dir=export_dir,
            summary=str(lane.get("summary", lane_id)),
            dry_run=args.dry_run,
        )
        result["lane_id"] = lane_id
        result["include_file"] = str(include_path)
        lane_results.append(result)

        lane_map[lane_id] = {
            "topic": lane_id,
            "include_file": str(include_path),
            "zip_path": str(result.get("zip_path", "")),
            "safe_to_share_with_chatgpt": bool(result.get("safe_to_share_with_chatgpt", False)),
            "included_files_count": int(result.get("included_files_count", 0) or 0),
            "skipped_files_count": int(result.get("skipped_files_count", 0) or 0),
            "blocked_files_count": int(result.get("blocked_files_count", 0) or 0),
            "generated_at_utc": result.get("generated_at_utc") or utc_iso(),
        }

    failed_lanes = [item["lane_id"] for item in lane_results if int(item.get("exit_code", 1)) != 0]
    safe_fail_lanes = [
        item["lane_id"]
        for item in lane_results
        if not bool(item.get("safe_to_share_with_chatgpt", False)) and not args.dry_run
    ]
    validation_verdict = "PASS"
    if failed_lanes:
        validation_verdict = "FAIL"
    elif safe_fail_lanes:
        validation_verdict = "PARTIAL_SAFE"
    elif args.dry_run:
        validation_verdict = "DRY_RUN"

    bundle_map = {
        "set_id": set_id,
        "generated_at_utc": utc_iso(),
        "manual_safe_only": True,
        "dry_run": bool(args.dry_run),
        "lanes": lane_map,
    }
    (review_dir / "03_BUNDLE_MAP.json").write_text(json.dumps(bundle_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (export_dir / "03_BUNDLE_MAP.json").write_text(json.dumps(bundle_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    entry = f"""# IMPERIUM Safe Review Pipeline Set

- set_id: `{set_id}`
- generated_at_utc: `{utc_iso()}`
- manual_safe_only: `true`
- dry_run: `{str(bool(args.dry_run)).lower()}`
- validation_verdict: `{validation_verdict}`
"""
    write_text(review_dir / "00_FOLLOWUP_ENTRYPOINT.md", entry)
    write_text(export_dir / "00_FOLLOWUP_ENTRYPOINT.md", entry)

    index_lines = ["# MASTER_INDEX", ""]
    for lane_id, lane_info in lane_map.items():
        index_lines.extend(
            [
                f"- `{lane_id}`",
                f"  - zip: `{lane_info.get('zip_path') or 'not_generated'}`",
                f"  - safe_to_share_with_chatgpt: `{lane_info.get('safe_to_share_with_chatgpt')}`",
                f"  - included/skipped/blocked: `{lane_info.get('included_files_count')}/{lane_info.get('skipped_files_count')}/{lane_info.get('blocked_files_count')}`",
            ]
        )
    write_text(review_dir / "01_MASTER_INDEX.md", "\n".join(index_lines))
    write_text(export_dir / "01_MASTER_INDEX.md", "\n".join(index_lines))

    reading_order = """# READING_ORDER

1. 00_FOLLOWUP_ENTRYPOINT.md
2. 01_MASTER_INDEX.md
3. 03_BUNDLE_MAP.json
4. lane bundles 01 -> 06
5. 04_VALIDATION_REPORT.md
6. 05_REMAINING_GAPS.md
"""
    write_text(review_dir / "02_READING_ORDER.md", reading_order)
    write_text(export_dir / "02_READING_ORDER.md", reading_order)

    validation_report = f"""# VALIDATION_REPORT

- verdict: `{validation_verdict}`
- failed_lanes: `{", ".join(failed_lanes) if failed_lanes else "none"}`
- unsafe_lanes: `{", ".join(safe_fail_lanes) if safe_fail_lanes else "none"}`
- policy: `manual-safe only`
- mutation_mode: `zero-repo-mutation-by-default`
"""
    write_text(review_dir / "04_VALIDATION_REPORT.md", validation_report)
    write_text(export_dir / "04_VALIDATION_REPORT.md", validation_report)

    remaining_gaps = """# REMAINING_GAPS

- full_event_bus: `NOT_YET_IMPLEMENTED`
- auto_preview_pipeline: `NOT_YET_IMPLEMENTED`
- pixel_perceptual_diff: `NOT_YET_IMPLEMENTED`
- pipeline currently orchestrates safe evidence export; it does not auto-remediate code.
"""
    write_text(review_dir / "05_REMAINING_GAPS.md", remaining_gaps)
    write_text(export_dir / "05_REMAINING_GAPS.md", remaining_gaps)

    raw_results = {"set_id": set_id, "lane_results": lane_results, "validation_verdict": validation_verdict}
    (review_dir / "lane_results.json").write_text(json.dumps(raw_results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "set_id": set_id,
                "validation_verdict": validation_verdict,
                "review_dir": str(review_dir),
                "export_dir": str(export_dir),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
