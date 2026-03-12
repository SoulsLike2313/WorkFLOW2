#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_rel(path_value: str) -> str:
    return str(path_value).replace("\\", "/").strip()


def resolve_project(workspace: dict[str, Any], project_slug: str) -> dict[str, Any]:
    registry = list(workspace.get("project_registry", []))
    matches = [item for item in registry if str(item.get("slug", "")).strip() == project_slug]
    if len(matches) != 1:
        raise ValueError(f"Project slug '{project_slug}' does not resolve uniquely in workspace manifest.")
    return matches[0]


def resolve_shared_registry(repo_root: Path, workspace: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    shared_cfg = workspace.setdefault("shared_systems", {})
    registry_rel = str(shared_cfg.get("registry_path", "workspace_config/shared_systems_registry.json")).strip()
    if not registry_rel:
        registry_rel = "workspace_config/shared_systems_registry.json"
    registry_path = repo_root / registry_rel
    if not registry_path.exists():
        raise FileNotFoundError(f"Shared systems registry not found: {registry_path}")
    return registry_path, load_json(registry_path)


def resolve_system_manifest_path(repo_root: Path, shared_registry: dict[str, Any], system_slug: str) -> Path:
    systems = list(shared_registry.get("systems", []))
    matches = [item for item in systems if str(item.get("slug", "")).strip() == system_slug]
    if len(matches) != 1:
        raise ValueError(f"System slug '{system_slug}' does not resolve uniquely in shared_systems registry.")
    manifest_rel = str(matches[0].get("manifest_path", "")).strip()
    manifest_path = repo_root / manifest_rel
    if not manifest_path.exists():
        raise FileNotFoundError(f"System manifest not found: {manifest_path}")
    return manifest_path


def ensure_project_system_fields(project_manifest: dict[str, Any]) -> None:
    if not isinstance(project_manifest.get("installed_systems"), list):
        project_manifest["installed_systems"] = []
    if not isinstance(project_manifest.get("installed_system_status"), dict):
        project_manifest["installed_system_status"] = {}
    if not isinstance(project_manifest.get("system_validation_status"), dict):
        project_manifest["system_validation_status"] = {}
    if not isinstance(project_manifest.get("install_history"), list):
        project_manifest["install_history"] = []
    if not isinstance(project_manifest.get("remove_history"), list):
        project_manifest["remove_history"] = []


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove shared system module from a project.")
    parser.add_argument("--project-slug", required=True, help="Target project slug from workspace registry.")
    parser.add_argument("--system-slug", required=True, help="System slug from shared systems registry.")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing changes.")
    args = parser.parse_args()

    started = utc_now()
    run_id = f"remove-{started.strftime('%Y%m%dT%H%M%SZ')}-{args.project_slug}-{args.system_slug}"

    repo_root = Path(__file__).resolve().parents[1]
    workspace_path = repo_root / "workspace_config" / "workspace_manifest.json"
    workspace = load_json(workspace_path)
    project = resolve_project(workspace, args.project_slug)
    project_root = repo_root / str(project.get("root_path", "")).strip()
    project_manifest_path = repo_root / str(project.get("manifest_path", "")).strip()
    project_manifest = load_json(project_manifest_path)
    ensure_project_system_fields(project_manifest)
    if str(project_manifest.get("slug", "")).strip() != args.project_slug:
        raise ValueError(
            f"Project manifest slug mismatch: expected '{args.project_slug}', "
            f"got '{project_manifest.get('slug', '')}'."
        )

    registry_path, shared_registry = resolve_shared_registry(repo_root, workspace)
    system_manifest_path = resolve_system_manifest_path(repo_root, shared_registry, args.system_slug)
    system_manifest = load_json(system_manifest_path)
    uninstall_steps = list(system_manifest.get("uninstall_steps", []))

    installed = args.system_slug in list(project_manifest.get("installed_systems", []))
    if not installed:
        summary = {
            "run_id": run_id,
            "action": "remove",
            "status": "NOT_INSTALLED",
            "timestamp": iso(started),
            "project_slug": args.project_slug,
            "system_slug": args.system_slug,
            "reason": "system_not_installed_in_project_manifest",
            "project_manifest_path": normalize_rel(str(project_manifest_path.relative_to(repo_root))),
            "dry_run": args.dry_run,
            "safe_noop": True,
        }
        summary_path = repo_root / "runtime" / "shared_systems" / "remove_runs" / f"{run_id}.json"
        write_json(summary_path, summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if args.dry_run else 1

    integration_root = project_root / "systems" / args.system_slug
    removed_paths: list[str] = []
    warnings: list[str] = []

    # Controlled remove limitation: only integration root and generated references are removed.
    if integration_root.exists():
        if args.dry_run:
            removed_paths.append(normalize_rel(str(integration_root.relative_to(repo_root))))
        else:
            shutil.rmtree(integration_root)
            removed_paths.append(normalize_rel(str(integration_root.relative_to(repo_root))))
    else:
        warnings.append("integration_root_missing_before_remove")

    installed_systems = [item for item in list(project_manifest.get("installed_systems", [])) if item != args.system_slug]
    project_manifest["installed_systems"] = sorted(set(installed_systems))

    status_map = dict(project_manifest.get("installed_system_status", {}))
    status_map[args.system_slug] = "removed"
    project_manifest["installed_system_status"] = status_map

    remove_history = list(project_manifest.get("remove_history", []))
    remove_history.append(
        {
            "run_id": run_id,
            "action": "remove",
            "system_slug": args.system_slug,
            "status": "removed",
            "timestamp": iso(started),
            "dry_run": args.dry_run,
            "source": "scripts/remove_system.py",
        }
    )
    project_manifest["remove_history"] = remove_history

    system_validation_status = dict(project_manifest.get("system_validation_status", {}))
    system_validation_status[args.system_slug] = "pending_post_remove"
    project_manifest["system_validation_status"] = system_validation_status

    project_system_index = workspace.setdefault("project_system_index", {})
    index_entry = dict(project_system_index.get(args.project_slug, {}))
    index_entry[args.system_slug] = "removed"
    project_system_index[args.project_slug] = index_entry
    workspace["project_system_index"] = project_system_index

    shared_installations = shared_registry.setdefault("project_installations", {})
    per_project = dict(shared_installations.get(args.project_slug, {}))
    per_project[args.system_slug] = {
        "status": "removed",
        "run_id": run_id,
        "timestamp": iso(started),
    }
    shared_installations[args.project_slug] = per_project
    shared_registry["project_installations"] = shared_installations

    history = list(shared_registry.get("history", []))
    history.append(
        {
            "run_id": run_id,
            "action": "remove",
            "project_slug": args.project_slug,
            "system_slug": args.system_slug,
            "status": "removed",
            "timestamp": iso(started),
            "dry_run": args.dry_run,
        }
    )
    shared_registry["history"] = history

    post_checks = {
        "integration_root_absent": (not integration_root.exists()) if not args.dry_run else True,
        "project_manifest_detached": args.system_slug not in project_manifest["installed_systems"],
        "workspace_project_system_index_updated": project_system_index.get(args.project_slug, {}).get(args.system_slug)
        == "removed",
        "remove_summary_written": True,
    }
    overall_status = "PASS" if all(post_checks.values()) else "FAIL"
    project_manifest["system_validation_status"][args.system_slug] = (
        "pass_post_remove" if overall_status == "PASS" else "fail_post_remove"
    )

    if not args.dry_run:
        write_json(project_manifest_path, project_manifest)
        write_json(workspace_path, workspace)
        write_json(registry_path, shared_registry)

    summary = {
        "run_id": run_id,
        "action": "remove",
        "status": overall_status if not args.dry_run else "DRY_RUN",
        "timestamp": iso(started),
        "project_slug": args.project_slug,
        "system_slug": args.system_slug,
        "project_manifest_path": normalize_rel(str(project_manifest_path.relative_to(repo_root))),
        "workspace_manifest_path": normalize_rel(str(workspace_path.relative_to(repo_root))),
        "shared_registry_path": normalize_rel(str(registry_path.relative_to(repo_root))),
        "system_manifest_path": normalize_rel(str(system_manifest_path.relative_to(repo_root))),
        "removed_paths": sorted(set(removed_paths)),
        "compatibility_checks": {
            "project_slug_in_workspace_registry": True,
            "project_manifest_slug_match": True,
            "system_manifest_resolved": True,
            "safe_remove_mode": "controlled",
        },
        "planned_manifest_updates": {
            "project_manifest": [
                "installed_systems",
                "installed_system_status",
                "system_validation_status",
                "remove_history",
            ],
            "workspace_manifest": ["project_system_index"],
            "shared_systems_registry": ["project_installations", "history"],
        },
        "post_remove_checks": post_checks,
        "uninstall_steps": uninstall_steps,
        "warnings": warnings,
        "limitations": [
            "Controlled remove only detaches manifest/registry links and integration_root content.",
            "Manual project-specific edits outside systems/<system_slug>/ are not auto-reverted.",
        ],
        "dry_run": args.dry_run,
    }
    summary_path = repo_root / "runtime" / "shared_systems" / "remove_runs" / f"{run_id}.json"
    write_json(summary_path, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
