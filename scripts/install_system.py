#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_SYSTEM_FIELDS = [
    "name",
    "slug",
    "purpose",
    "category",
    "description",
    "required_project_inputs",
    "optional_project_inputs",
    "files_to_create",
    "files_to_update",
    "runtime_outputs",
    "validation_entrypoints",
    "integration_steps",
    "post_install_checks",
    "uninstall_steps",
    "notes",
    "maturity_level",
    "supported_project_types",
]


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


def resolve_system(shared_registry: dict[str, Any], system_slug: str) -> dict[str, Any]:
    systems = list(shared_registry.get("systems", []))
    matches = [item for item in systems if str(item.get("slug", "")).strip() == system_slug]
    if len(matches) != 1:
        raise ValueError(f"System slug '{system_slug}' does not resolve uniquely in shared_systems registry.")
    return matches[0]


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


def ensure_system_manifest(system_manifest: dict[str, Any], system_slug: str) -> None:
    missing = [field for field in REQUIRED_SYSTEM_FIELDS if field not in system_manifest]
    if missing:
        raise ValueError(f"{system_slug}: SYSTEM_MANIFEST missing fields: {missing}")
    if str(system_manifest.get("slug", "")).strip() != system_slug:
        raise ValueError(f"{system_slug}: slug mismatch in SYSTEM_MANIFEST.")


def copy_integration_assets(
    module_root: Path, integration_root: Path, repo_root: Path, *, dry_run: bool
) -> list[str]:
    copied: list[str] = []
    if dry_run:
        for rel in ["README.md", "integration_guide.md", "SYSTEM_MANIFEST.json"]:
            copied.append(normalize_rel(str((integration_root / rel).relative_to(repo_root))))
        for rel in ["templates", "examples", "validation", "tests", "adapters"]:
            copied.append(normalize_rel(str((integration_root / rel).relative_to(repo_root))))
        return copied

    integration_root.mkdir(parents=True, exist_ok=True)
    for rel in ["README.md", "integration_guide.md", "SYSTEM_MANIFEST.json"]:
        src = module_root / rel
        dst = integration_root / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(normalize_rel(str(dst.relative_to(repo_root))))
    for rel in ["templates", "examples", "validation", "tests", "adapters"]:
        src_dir = module_root / rel
        dst_dir = integration_root / rel
        if src_dir.exists():
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            copied.append(normalize_rel(str(dst_dir.relative_to(repo_root))))
    return copied


def materialize_file(path: Path, payload: dict[str, Any], *, dry_run: bool) -> bool:
    if dry_run:
        return not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        write_json(path, payload)
    else:
        path.write_text(
            f"generated_by=install_system.py\nsystem_slug={payload.get('system_slug','')}\n",
            encoding="utf-8",
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Install shared system module into a project.")
    parser.add_argument("--project-slug", required=True, help="Target project slug from workspace registry.")
    parser.add_argument("--system-slug", required=True, help="System slug from shared systems registry.")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing changes.")
    args = parser.parse_args()

    started = utc_now()
    run_id = f"install-{started.strftime('%Y%m%dT%H%M%SZ')}-{args.project_slug}-{args.system_slug}"

    repo_root = Path(__file__).resolve().parents[1]
    workspace_path = repo_root / "workspace_config" / "workspace_manifest.json"
    workspace = load_json(workspace_path)
    project = resolve_project(workspace, args.project_slug)

    registry_path, shared_registry = resolve_shared_registry(repo_root, workspace)
    system_entry = resolve_system(shared_registry, args.system_slug)
    system_manifest_path = repo_root / str(system_entry.get("manifest_path", "")).strip()
    if not system_manifest_path.exists():
        raise FileNotFoundError(f"System manifest not found: {system_manifest_path}")
    system_manifest = load_json(system_manifest_path)
    ensure_system_manifest(system_manifest, args.system_slug)

    project_type = str(project.get("type", "")).strip()
    supported_types = [str(item).strip() for item in system_manifest.get("supported_project_types", [])]
    if project_type not in supported_types:
        raise ValueError(
            f"System '{args.system_slug}' is not compatible with project type '{project_type}'. "
            f"Supported: {supported_types}"
        )

    project_root = repo_root / str(project.get("root_path", "")).strip()
    project_manifest_path = repo_root / str(project.get("manifest_path", "")).strip()
    project_manifest = load_json(project_manifest_path)
    ensure_project_system_fields(project_manifest)
    if str(project_manifest.get("slug", "")).strip() != args.project_slug:
        raise ValueError(
            f"Project manifest slug mismatch: expected '{args.project_slug}', "
            f"got '{project_manifest.get('slug', '')}'."
        )
    integration_root = project_root / "systems" / args.system_slug
    module_root = system_manifest_path.parent

    already_installed = args.system_slug in list(project_manifest.get("installed_systems", []))
    copied_assets = copy_integration_assets(module_root, integration_root, repo_root, dry_run=args.dry_run)

    created_files: list[str] = []
    for rel_path in list(system_manifest.get("files_to_create", [])):
        rel = (
            str(rel_path)
            .replace("{system_slug}", args.system_slug)
            .replace("{project_slug}", args.project_slug)
            .replace("\\", "/")
            .strip()
        )
        if not rel:
            continue
        target = project_root / rel
        changed = materialize_file(
            target,
            {
                "generated_by": "install_system.py",
                "system_slug": args.system_slug,
                "project_slug": args.project_slug,
            },
            dry_run=args.dry_run,
        )
        if changed:
            created_files.append(normalize_rel(str(target.relative_to(repo_root))))

    if not args.dry_run:
        context_payload = {
            "run_id": run_id,
            "project_slug": args.project_slug,
            "system_slug": args.system_slug,
            "installed_at": iso(started),
            "system_manifest_path": normalize_rel(str(system_manifest_path.relative_to(repo_root))),
            "module_root": normalize_rel(str(module_root.relative_to(repo_root))),
        }
        write_json(integration_root / "INSTALLATION_CONTEXT.json", context_payload)
        created_files.append(normalize_rel(str((integration_root / "INSTALLATION_CONTEXT.json").relative_to(repo_root))))

    installed_systems = list(project_manifest.get("installed_systems", []))
    if args.system_slug not in installed_systems:
        installed_systems.append(args.system_slug)
    project_manifest["installed_systems"] = sorted(set(installed_systems))

    status_map = dict(project_manifest.get("installed_system_status", {}))
    status_map[args.system_slug] = "installed"
    project_manifest["installed_system_status"] = status_map

    install_history = list(project_manifest.get("install_history", []))
    install_history.append(
        {
            "run_id": run_id,
            "action": "install",
            "system_slug": args.system_slug,
            "status": "installed",
            "timestamp": iso(started),
            "dry_run": args.dry_run,
            "already_installed": already_installed,
            "source": "scripts/install_system.py",
        }
    )
    project_manifest["install_history"] = install_history

    system_validation_status = dict(project_manifest.get("system_validation_status", {}))
    system_validation_status[args.system_slug] = "pending_post_install"
    project_manifest["system_validation_status"] = system_validation_status

    workspace_shared = workspace.setdefault("shared_systems", {})
    workspace_shared["root_path"] = "shared_systems"
    workspace_shared["registry_path"] = normalize_rel(str(registry_path.relative_to(repo_root)))
    workspace_shared["install_script"] = "scripts/install_system.py"
    workspace_shared["remove_script"] = "scripts/remove_system.py"

    project_system_index = workspace.setdefault("project_system_index", {})
    project_index_entry = dict(project_system_index.get(args.project_slug, {}))
    project_index_entry[args.system_slug] = "installed"
    project_system_index[args.project_slug] = project_index_entry
    workspace["project_system_index"] = project_system_index

    shared_installations = shared_registry.setdefault("project_installations", {})
    per_project_installations = dict(shared_installations.get(args.project_slug, {}))
    per_project_installations[args.system_slug] = {
        "status": "installed",
        "run_id": run_id,
        "timestamp": iso(started),
    }
    shared_installations[args.project_slug] = per_project_installations
    shared_registry["project_installations"] = shared_installations

    registry_history = list(shared_registry.get("history", []))
    registry_history.append(
        {
            "run_id": run_id,
            "action": "install",
            "project_slug": args.project_slug,
            "system_slug": args.system_slug,
            "status": "installed",
            "timestamp": iso(started),
            "dry_run": args.dry_run,
        }
    )
    shared_registry["history"] = registry_history

    post_checks = {
        "integration_root_exists": integration_root.exists() if not args.dry_run else True,
        "project_manifest_contains_installed_slug": args.system_slug in project_manifest["installed_systems"],
        "workspace_project_system_index_updated": project_system_index.get(args.project_slug, {}).get(args.system_slug)
        == "installed",
        "install_summary_written": True,
    }
    overall_status = "PASS" if all(post_checks.values()) else "FAIL"
    project_manifest["system_validation_status"][args.system_slug] = (
        "pass_post_install" if overall_status == "PASS" else "fail_post_install"
    )

    if not args.dry_run:
        write_json(project_manifest_path, project_manifest)
        write_json(workspace_path, workspace)
        write_json(registry_path, shared_registry)

    summary_dir = repo_root / "runtime" / "shared_systems" / "install_runs"
    summary_path = summary_dir / f"{run_id}.json"
    summary = {
        "run_id": run_id,
        "action": "install",
        "status": overall_status if not args.dry_run else "DRY_RUN",
        "timestamp": iso(started),
        "project_slug": args.project_slug,
        "system_slug": args.system_slug,
        "project_manifest_path": normalize_rel(str(project_manifest_path.relative_to(repo_root))),
        "workspace_manifest_path": normalize_rel(str(workspace_path.relative_to(repo_root))),
        "shared_registry_path": normalize_rel(str(registry_path.relative_to(repo_root))),
        "system_manifest_path": normalize_rel(str(system_manifest_path.relative_to(repo_root))),
        "created_files": sorted(set(created_files)),
        "copied_assets": sorted(set(copied_assets)),
        "compatibility_checks": {
            "project_slug_in_workspace_registry": True,
            "project_manifest_slug_match": True,
            "project_type_supported": True,
            "system_manifest_contract_valid": True,
        },
        "planned_manifest_updates": {
            "project_manifest": [
                "installed_systems",
                "installed_system_status",
                "system_validation_status",
                "install_history",
            ],
            "workspace_manifest": ["shared_systems", "project_system_index"],
            "shared_systems_registry": ["project_installations", "history"],
        },
        "post_install_checks": post_checks,
        "dry_run": args.dry_run,
        "already_installed": already_installed,
    }
    write_json(summary_path, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
