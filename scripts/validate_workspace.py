#!/usr/bin/env python
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
FAIL = "FAIL"

REQUIRED_WORKSPACE_FIELDS = [
    "workspace_name",
    "active_project",
    "project_registry",
    "status_values",
    "category_values",
    "root_paths",
    "entrypoints",
    "verification_entrypoints",
    "update_entrypoints",
    "bootstrap_rules",
]

REQUIRED_REGISTRY_FIELDS = [
    "slug",
    "name",
    "status",
    "category",
    "type",
    "priority",
    "root_path",
    "manifest_path",
    "readme_path",
    "main_entrypoints",
    "verification_entrypoints",
    "update_entrypoints",
]

REQUIRED_PROJECT_MANIFEST_FIELDS = [
    "name",
    "slug",
    "description",
    "status",
    "category",
    "type",
    "priority",
    "root_path",
    "readme_path",
    "main_entrypoints",
    "verification_entrypoints",
    "user_mode_entrypoint",
    "developer_mode_entrypoint",
    "update_entrypoint",
    "config_files",
    "runtime_dirs",
    "log_dirs",
    "data_dirs",
    "dependencies_file",
    "owner",
    "maturity_level",
    "tags",
    "notes",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def has_project_markers(path: Path) -> bool:
    if (path / "PROJECT_MANIFEST.json").exists() or (path / "README.md").exists():
        return True
    py_files = list(path.glob("*.py"))
    return bool(py_files)


def discover_candidate_project_dirs(projects_root: Path) -> list[Path]:
    ignored = {"__pycache__", ".pytest_cache", ".venv", "build", "dist"}
    candidates: list[Path] = []

    for child in projects_root.iterdir():
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name in ignored:
            continue

        if has_project_markers(child):
            candidates.append(child)

        for grand in child.iterdir():
            if not grand.is_dir():
                continue
            if grand.name.startswith(".") or grand.name in ignored:
                continue
            if has_project_markers(grand):
                candidates.append(grand)

    unique: list[Path] = []
    seen = set()
    for item in candidates:
        norm = str(item.resolve()).lower()
        if norm in seen:
            continue
        seen.add(norm)
        unique.append(item)
    return sorted(unique)


def main() -> int:
    started = utc_now()
    run_id = f"workspace-validate-{started.strftime('%Y%m%dT%H%M%SZ')}"

    repo_root = Path(__file__).resolve().parents[1]
    workspace_manifest_path = repo_root / "workspace_config" / "workspace_manifest.json"
    output_dir = repo_root / "runtime" / "workspace_validation" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    executed_checks: list[str] = []
    passed_checks: list[str] = []
    warned_checks: list[str] = []
    failed_checks: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []

    if not workspace_manifest_path.exists():
        errors.append(f"Missing workspace manifest: {workspace_manifest_path}")
        finished = utc_now()
        payload = {
            "run_id": run_id,
            "started_at": iso(started),
            "finished_at": iso(finished),
            "duration_seconds": round((finished - started).total_seconds(), 3),
            "status": FAIL,
            "executed_checks": executed_checks,
            "passed_checks": passed_checks,
            "warned_checks": warned_checks,
            "failed_checks": ["workspace_manifest_exists"],
            "errors": errors,
            "warnings": warnings,
            "artifacts": {
                "validation_summary_json": str(output_dir / "validation_summary.json"),
                "validation_summary_md": str(output_dir / "validation_summary.md"),
            },
        }
        write_json(output_dir / "validation_summary.json", payload)
        (output_dir / "validation_summary.md").write_text("# Workspace Validation\n\nFAIL\n", encoding="utf-8")
        return 1

    workspace = load_json(workspace_manifest_path)

    executed_checks.append("workspace_required_fields")
    missing_workspace_fields = [field for field in REQUIRED_WORKSPACE_FIELDS if field not in workspace]
    if missing_workspace_fields:
        failed_checks.append("workspace_required_fields")
        errors.append(f"Missing workspace fields: {missing_workspace_fields}")
    else:
        passed_checks.append("workspace_required_fields")

    status_values = list(workspace.get("status_values", []))
    category_values = list(workspace.get("category_values", []))
    registry = list(workspace.get("project_registry", []))

    executed_checks.append("project_registry_non_empty")
    if not registry:
        failed_checks.append("project_registry_non_empty")
        errors.append("project_registry is empty")
    else:
        passed_checks.append("project_registry_non_empty")

    executed_checks.append("project_registry_field_validation")
    registry_field_errors = []
    registry_entrypoint_errors = []
    for item in registry:
        slug = str(item.get("slug", "")).strip() or "<missing-slug>"
        for field in REQUIRED_REGISTRY_FIELDS:
            if field not in item:
                registry_field_errors.append(f"{slug}: missing field '{field}'")
        main_entrypoints = item.get("main_entrypoints", [])
        verification_entrypoints = item.get("verification_entrypoints", [])
        if not isinstance(main_entrypoints, list) or not main_entrypoints:
            registry_entrypoint_errors.append(f"{slug}: registry main_entrypoints must be a non-empty list")
        if not isinstance(verification_entrypoints, list) or not verification_entrypoints:
            registry_entrypoint_errors.append(f"{slug}: registry verification_entrypoints must be a non-empty list")
    if registry_field_errors:
        failed_checks.append("project_registry_field_validation")
        errors.extend(registry_field_errors)
    elif registry_entrypoint_errors:
        failed_checks.append("project_registry_field_validation")
        errors.extend(registry_entrypoint_errors)
    else:
        passed_checks.append("project_registry_field_validation")

    executed_checks.append("slug_conflicts")
    slugs = [str(item.get("slug", "")).strip() for item in registry]
    unique_slugs = {slug for slug in slugs if slug}
    if len(unique_slugs) != len(slugs):
        failed_checks.append("slug_conflicts")
        errors.append("Slug conflict detected in project_registry")
    else:
        passed_checks.append("slug_conflicts")

    executed_checks.append("active_project_valid")
    active_project = str(workspace.get("active_project", "")).strip()
    active_entries = [item for item in registry if str(item.get("slug", "")).strip() == active_project]
    if len(active_entries) != 1:
        failed_checks.append("active_project_valid")
        errors.append(f"active_project '{active_project}' does not resolve uniquely")
    elif str(active_entries[0].get("status", "")).strip() != "active":
        failed_checks.append("active_project_valid")
        errors.append(f"active_project '{active_project}' is not marked as active")
    else:
        passed_checks.append("active_project_valid")

    executed_checks.append("status_and_category_values")
    status_errors = []
    category_warnings = []
    for item in registry:
        slug = str(item.get("slug", "")).strip()
        status = str(item.get("status", "")).strip()
        category = str(item.get("category", "")).strip()
        if status not in status_values:
            status_errors.append(f"{slug}: invalid status '{status}'")
        if category and category not in category_values:
            category_warnings.append(f"{slug}: category '{category}' not listed in category_values")
    if status_errors:
        failed_checks.append("status_and_category_values")
        errors.extend(status_errors)
    else:
        if category_warnings:
            warned_checks.append("status_and_category_values")
            warnings.extend(category_warnings)
        else:
            passed_checks.append("status_and_category_values")

    registered_roots: dict[str, Path] = {}
    manifest_coverage: list[dict[str, Any]] = []

    executed_checks.append("project_paths_and_manifests")
    path_errors = []
    for item in registry:
        slug = str(item.get("slug", "")).strip()
        root_path = repo_root / str(item.get("root_path", ""))
        manifest_path = repo_root / str(item.get("manifest_path", ""))
        readme_path = repo_root / str(item.get("readme_path", ""))

        root_exists = root_path.exists()
        manifest_exists = manifest_path.exists()
        readme_exists = readme_path.exists()

        if root_exists:
            registered_roots[slug] = root_path.resolve()

        if not root_exists:
            path_errors.append(f"{slug}: missing root_path {root_path}")
        if not manifest_exists:
            path_errors.append(f"{slug}: missing manifest_path {manifest_path}")
        if not readme_exists:
            path_errors.append(f"{slug}: missing readme_path {readme_path}")

        manifest_coverage.append(
            {
                "slug": slug,
                "root_path": str(root_path),
                "root_exists": root_exists,
                "manifest_path": str(manifest_path),
                "manifest_exists": manifest_exists,
                "readme_path": str(readme_path),
                "readme_exists": readme_exists,
            }
        )

    if path_errors:
        failed_checks.append("project_paths_and_manifests")
        errors.extend(path_errors)
    else:
        passed_checks.append("project_paths_and_manifests")

    executed_checks.append("project_manifest_contract")
    contract_errors = []
    entrypoint_warnings = []
    for item in registry:
        slug = str(item.get("slug", "")).strip()
        manifest_path = repo_root / str(item.get("manifest_path", ""))
        if not manifest_path.exists():
            continue
        manifest = load_json(manifest_path)

        for field in REQUIRED_PROJECT_MANIFEST_FIELDS:
            if field not in manifest:
                contract_errors.append(f"{slug}: PROJECT_MANIFEST missing '{field}'")

        if str(manifest.get("slug", "")).strip() != slug:
            contract_errors.append(f"{slug}: manifest slug mismatch")

        registry_status = str(item.get("status", "")).strip()
        manifest_status = str(manifest.get("status", "")).strip()
        if manifest_status != registry_status:
            contract_errors.append(f"{slug}: manifest status '{manifest_status}' != registry status '{registry_status}'")

        main_entrypoints = manifest.get("main_entrypoints", [])
        verification_entrypoints = manifest.get("verification_entrypoints", [])
        if not isinstance(main_entrypoints, list) or not main_entrypoints:
            contract_errors.append(f"{slug}: main_entrypoints must be a non-empty list")
        if not isinstance(verification_entrypoints, list) or not verification_entrypoints:
            contract_errors.append(f"{slug}: verification_entrypoints must be a non-empty list")

        for field in ["user_mode_entrypoint", "developer_mode_entrypoint", "update_entrypoint"]:
            value = str(manifest.get(field, "")).strip()
            if not value:
                entrypoint_warnings.append(f"{slug}: empty {field}")

    if contract_errors:
        failed_checks.append("project_manifest_contract")
        errors.extend(contract_errors)
    else:
        if entrypoint_warnings:
            warned_checks.append("project_manifest_contract")
            warnings.extend(entrypoint_warnings)
        else:
            passed_checks.append("project_manifest_contract")

    executed_checks.append("outside_system_projects")
    projects_root = repo_root / str(workspace.get("root_paths", {}).get("projects_root", "projects"))
    outside_projects = []
    if projects_root.exists():
        candidates = discover_candidate_project_dirs(projects_root)
        for candidate in candidates:
            in_registry = any(candidate.resolve() == path for path in registered_roots.values())
            nested_in_registered = any(is_relative_to(candidate.resolve(), path) and candidate.resolve() != path for path in registered_roots.values())
            if not in_registry and not nested_in_registered:
                outside_projects.append(str(candidate.relative_to(repo_root)).replace("\\", "/"))
    else:
        warnings.append(f"Projects root not found: {projects_root}")

    if outside_projects:
        failed_checks.append("outside_system_projects")
        errors.append(f"Unregistered project folders detected: {outside_projects}")
    else:
        passed_checks.append("outside_system_projects")

    finished = utc_now()
    if errors:
        status = FAIL
    elif warnings:
        status = PASS_WITH_WARNINGS
    else:
        status = PASS

    summary = {
        "run_id": run_id,
        "started_at": iso(started),
        "finished_at": iso(finished),
        "duration_seconds": round((finished - started).total_seconds(), 3),
        "status": status,
        "workspace_manifest_path": str(workspace_manifest_path),
        "active_project": active_project,
        "executed_checks": executed_checks,
        "passed_checks": sorted(set(passed_checks)),
        "warned_checks": sorted(set(warned_checks)),
        "failed_checks": sorted(set(failed_checks)),
        "errors": errors,
        "warnings": warnings,
        "project_manifest_coverage": manifest_coverage,
        "outside_system_projects": outside_projects,
        "artifacts": {
            "validation_summary_json": str(output_dir / "validation_summary.json"),
            "validation_summary_md": str(output_dir / "validation_summary.md")
        }
    }

    write_json(output_dir / "validation_summary.json", summary)

    md_lines = [
        f"# Workspace Validation ({run_id})",
        "",
        f"- Status: `{status}`",
        f"- Started: `{summary['started_at']}`",
        f"- Finished: `{summary['finished_at']}`",
        f"- Duration: `{summary['duration_seconds']}s`",
        f"- Active project: `{active_project}`",
        "",
        "## Checks",
        f"- Passed: {len(summary['passed_checks'])}",
        f"- Warned: {len(summary['warned_checks'])}",
        f"- Failed: {len(summary['failed_checks'])}",
        "",
        "### Warned checks",
    ]
    if summary["warned_checks"]:
        md_lines.extend([f"- `{item}`" for item in summary["warned_checks"]])
    else:
        md_lines.append("- none")

    md_lines.extend(["", "### Failed checks"])
    if summary["failed_checks"]:
        md_lines.extend([f"- `{item}`" for item in summary["failed_checks"]])
    else:
        md_lines.append("- none")

    if warnings:
        md_lines.extend(["", "## Warnings"])
        md_lines.extend([f"- {item}" for item in warnings])

    if errors:
        md_lines.extend(["", "## Errors"])
        md_lines.extend([f"- {item}" for item in errors])

    (output_dir / "validation_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"[workspace-validate] status: {status}")
    print(f"[workspace-validate] run_dir: {output_dir}")

    return 1 if status == FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
