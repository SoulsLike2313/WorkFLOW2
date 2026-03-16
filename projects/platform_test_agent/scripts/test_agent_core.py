from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_MANIFEST = REPO_ROOT / "workspace_config" / "workspace_manifest.json"
LANE_REGISTRY = REPO_ROOT / "projects" / "platform_test_agent" / "core" / "lane_registry.json"
OUTPUT_ROOT = REPO_ROOT / "runtime" / "projects" / "platform_test_agent" / "audit_reports"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class TargetProject:
    slug: str
    root_path: str
    manifest_path: str
    project_type: str
    status: str


def _resolve_target_project(*, target_path: str, target_slug: str) -> TargetProject:
    workspace = _load_json(WORKSPACE_MANIFEST)
    registry = list(workspace.get("project_registry", []))
    matches: list[dict[str, Any]] = []
    normalized_target_path = str(target_path).strip().replace("\\", "/")

    for item in registry:
        item_slug = str(item.get("slug", "")).strip()
        item_root = str(item.get("root_path", "")).strip()
        normalized_item_root = item_root.replace("\\", "/")
        slug_match = bool(target_slug) and item_slug == target_slug
        path_match = bool(normalized_target_path) and normalized_item_root == normalized_target_path
        if slug_match or path_match:
            matches.append(item)

    if len(matches) != 1:
        raise RuntimeError(
            "Unable to resolve unique target project. "
            f"target_slug='{target_slug}', target_path='{target_path}', matches={len(matches)}"
        )

    item = matches[0]
    project_manifest_path = REPO_ROOT / str(item.get("manifest_path", "")).strip()
    if not project_manifest_path.exists():
        raise RuntimeError(f"Target project manifest missing: {project_manifest_path}")
    project_manifest = _load_json(project_manifest_path)

    return TargetProject(
        slug=str(item.get("slug", "")).strip(),
        root_path=str(item.get("root_path", "")).strip(),
        manifest_path=str(item.get("manifest_path", "")).strip(),
        project_type=str(project_manifest.get("type", "unknown")).strip() or "unknown",
        status=str(project_manifest.get("status", "unknown")).strip() or "unknown",
    )


def _is_ui_applicable(project_type: str) -> bool:
    return project_type in {"desktop_app", "web_app", "mobile_app", "gui_tool"}


def _run_verify_entrypoint(target_slug: str) -> tuple[int, str]:
    command = [
        "python",
        "scripts/project_startup.py",
        "run",
        "--project-slug",
        target_slug,
        "--entrypoint",
        "verify",
        "--startup-kind",
        "verify",
        "--port-mode",
        "fixed",
    ]
    completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if completed.returncode == 0:
        return 0, "verification_entrypoint_pass"
    return int(completed.returncode), completed.stderr.strip() or completed.stdout.strip() or "verification_entrypoint_failed"


def _lane_payload(*, lane_slug: str, selected: bool, status: str, note: str) -> dict[str, Any]:
    return {
        "lane_slug": lane_slug,
        "selected": bool(selected),
        "status": status,
        "note": note,
    }


def run_agent(*, mode: str, target_path: str, target_slug: str, execute_verification: bool) -> dict[str, Any]:
    target = _resolve_target_project(target_path=target_path, target_slug=target_slug)
    lane_registry = _load_json(LANE_REGISTRY)
    lane_order = list(lane_registry.get("lane_order", []))

    selected_lanes = set(lane_order)
    if not _is_ui_applicable(target.project_type):
        selected_lanes.discard("ui_audit_lane")

    lane_results: list[dict[str, Any]] = []
    for lane_slug in lane_order:
        if lane_slug not in selected_lanes:
            lane_results.append(_lane_payload(lane_slug=lane_slug, selected=False, status="not_applicable", note="ui_not_applicable_for_project_type"))
            continue
        lane_results.append(_lane_payload(lane_slug=lane_slug, selected=True, status="planned", note="dry_machine_plan"))

    final_status = "under_audit"
    admission_status = "manual_testing_blocked"
    execution_note = "dry_run_only"

    if mode == "intake":
        final_status = "under_audit"
        admission_status = "manual_testing_blocked"
        execution_note = "intake_completed"
        for lane in lane_results:
            if lane["lane_slug"] == "project_intake":
                lane["status"] = "completed"
                lane["note"] = "target_project_resolved"

    elif mode in {"audit", "verify"} and execute_verification:
        exit_code, verify_note = _run_verify_entrypoint(target.slug)
        execution_note = "verification_executed"
        for lane in lane_results:
            if lane["lane_slug"] == "verification_lane":
                lane["status"] = "completed" if exit_code == 0 else "failed"
                lane["note"] = verify_note
        if exit_code == 0:
            final_status = "PASS_WITH_WARNINGS"
            admission_status = "manual_testing_allowed"
        else:
            final_status = "failed_audit"
            admission_status = "manual_testing_blocked"

    run_time = _utc_now()
    run_id = f"test-agent-{mode}-{target.slug}-{run_time.strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = OUTPUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    required_checks = [
        "project_intake",
        "verification_lane",
        "readiness_lane",
        "reporting_lane",
        "localization_audit_lane",
        "audit_observability_lane",
        "evidence_collection",
        "final_admission_gate",
    ]
    if _is_ui_applicable(target.project_type):
        required_checks.append("ui_audit_lane")

    evidence_outputs = {
        "run_report_json": str((run_dir / "final_machine_report.json").resolve()),
        "run_report_md": str((run_dir / "final_machine_report.md").resolve()),
        "admission_decision_json": str((run_dir / "admission_decision.json").resolve()),
        "evidence_manifest_json": str((run_dir / "evidence_manifest.json").resolve()),
    }

    payload = {
        "run_id": run_id,
        "timestamp": _iso(run_time),
        "mode": mode,
        "target_project": {
            "slug": target.slug,
            "root_path": target.root_path,
            "manifest_path": target.manifest_path,
            "project_type": target.project_type,
            "current_status": target.status,
        },
        "lane_selection": lane_results,
        "required_checks": required_checks,
        "execution_note": execution_note,
        "final_status": final_status,
        "admission_status": admission_status,
        "manual_testing_gate": {
            "allowed_statuses": ["PASS", "PASS_WITH_WARNINGS"],
            "repo_visible_evidence_required": True,
            "decision": admission_status,
        },
        "evidence_outputs": evidence_outputs,
        "future_lanes": list(lane_registry.get("future_lanes", [])),
    }

    _write_json(run_dir / "final_machine_report.json", payload)
    _write_json(
        run_dir / "admission_decision.json",
        {
            "run_id": run_id,
            "target_project_slug": target.slug,
            "final_status": final_status,
            "admission_status": admission_status,
        },
    )
    _write_json(
        run_dir / "evidence_manifest.json",
        {
            "run_id": run_id,
            "evidence_outputs": evidence_outputs,
            "lane_count": len([lane for lane in lane_results if lane.get("selected")]),
        },
    )

    md_lines = [
        "# Platform Test Agent Run",
        "",
        f"- run_id: `{run_id}`",
        f"- mode: `{mode}`",
        f"- target_project_slug: `{target.slug}`",
        f"- target_project_type: `{target.project_type}`",
        f"- final_status: `{final_status}`",
        f"- admission_status: `{admission_status}`",
        f"- execution_note: `{execution_note}`",
        "",
        "## Selected Lanes",
    ]
    for lane in lane_results:
        if not lane.get("selected"):
            continue
        md_lines.append(f"- `{lane['lane_slug']}`: `{lane['status']}` ({lane['note']})")
    (run_dir / "final_machine_report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    (OUTPUT_ROOT / "latest_run.txt").write_text(str(run_dir.resolve()) + "\n", encoding="utf-8")
    _write_json(
        OUTPUT_ROOT / "latest_run.json",
        {
            "run_id": run_id,
            "path": str(run_dir.resolve()),
            "target_project_slug": target.slug,
            "final_status": final_status,
            "admission_status": admission_status,
            "timestamp": _iso(run_time),
        },
    )
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Platform Test Agent core runner (intake/audit/verify lanes).")
    parser.add_argument("--mode", choices=["intake", "audit", "verify"], required=True)
    parser.add_argument("--target-project-path", default="", help="Repo-relative path to target project root.")
    parser.add_argument("--target-project-slug", default="", help="Target project slug from workspace registry.")
    parser.add_argument(
        "--execute-verification",
        action="store_true",
        help="Execute target verification entrypoint instead of dry machine plan.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    if not args.target_project_path and not args.target_project_slug:
        raise SystemExit("Either --target-project-path or --target-project-slug is required.")

    result = run_agent(
        mode=args.mode,
        target_path=str(args.target_project_path).strip(),
        target_slug=str(args.target_project_slug).strip(),
        execute_verification=bool(args.execute_verification),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
