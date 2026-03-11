#!/usr/bin/env python
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
FAIL = "FAIL"
PORT_MODE_VALUES = {"fixed", "auto"}
REQUIRED_RUNTIME_PATH_KEYS = (
    "runtime_dir",
    "log_dir",
    "data_dir",
    "cache_dir",
    "temp_dir",
    "diagnostics_dir",
    "update_artifacts_dir",
    "verification_dir",
)
REQUIRED_STATE_PATH_KEYS = ("db_path", "state_path")

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
    "isolation_policy",
]

REQUIRED_REGISTRY_FIELDS = [
    "slug",
    "name",
    "status",
    "category",
    "type",
    "priority",
    "runtime_namespace",
    "port_range",
    "port_mode_default",
    "service_ports",
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
    "runtime_namespace",
    "port_range",
    "port_mode_default",
    "service_ports",
    "runtime_paths",
    "state_paths",
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
    ignored = {"__pycache__", ".pytest_cache", ".venv", "build", "dist", "runtime"}
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


def parse_port_range(raw: Any, *, label: str) -> tuple[int, int]:
    if not isinstance(raw, dict):
        raise ValueError(f"{label}: port_range must be an object")
    try:
        start = int(raw.get("start"))
        end = int(raw.get("end"))
    except Exception as exc:
        raise ValueError(f"{label}: invalid port_range values") from exc
    if start < 1 or end > 65535 or start > end:
        raise ValueError(f"{label}: invalid port_range {start}-{end}")
    return start, end


def ranges_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def parse_service_ports(raw: Any, *, label: str) -> dict[str, int]:
    if not isinstance(raw, dict) or not raw:
        raise ValueError(f"{label}: service_ports must be a non-empty object")
    out: dict[str, int] = {}
    for key, value in raw.items():
        name = str(key).strip().lower()
        if not name:
            raise ValueError(f"{label}: empty service_ports key")
        try:
            port = int(value)
        except Exception as exc:
            raise ValueError(f"{label}: invalid service port '{name}'") from exc
        if port < 1 or port > 65535:
            raise ValueError(f"{label}: service port '{name}' is outside TCP range")
        out[name] = port
    return out


def normalize_rel_path(raw: Any) -> str:
    return str(raw or "").strip().replace("\\", "/")


def is_project_scoped_path(path_value: str, *, slug: str, runtime_namespace: str) -> bool:
    normalized = path_value.replace("\\", "/").lower()
    return slug.lower() in normalized or runtime_namespace.lower() in normalized


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

    executed_checks.append("isolation_policy_contract")
    isolation_policy = workspace.get("isolation_policy")
    if not isinstance(isolation_policy, dict):
        failed_checks.append("isolation_policy_contract")
        errors.append("workspace isolation_policy must be an object")
    else:
        allocator = isolation_policy.get("port_allocator")
        runtime_layout = isolation_policy.get("runtime_layout")
        policy_errors: list[str] = []
        if not isinstance(allocator, dict):
            policy_errors.append("isolation_policy.port_allocator must be an object")
        else:
            try:
                base_start = int(allocator.get("base_start"))
                range_size = int(allocator.get("range_size"))
                max_end = int(allocator.get("max_end"))
                if base_start < 1 or range_size < 10 or max_end > 65535:
                    policy_errors.append("isolation_policy.port_allocator values are out of bounds")
            except Exception:
                policy_errors.append("isolation_policy.port_allocator values must be integers")
        if not isinstance(runtime_layout, dict):
            policy_errors.append("isolation_policy.runtime_layout must be an object")
        else:
            runtime_root = str(runtime_layout.get("runtime_root", "")).strip()
            if not runtime_root:
                policy_errors.append("isolation_policy.runtime_layout.runtime_root must be non-empty")
        if policy_errors:
            failed_checks.append("isolation_policy_contract")
            errors.extend(policy_errors)
        else:
            passed_checks.append("isolation_policy_contract")

    executed_checks.append("project_registry_non_empty")
    if not registry:
        failed_checks.append("project_registry_non_empty")
        errors.append("project_registry is empty")
    else:
        passed_checks.append("project_registry_non_empty")

    executed_checks.append("project_registry_field_validation")
    registry_field_errors: list[str] = []
    registry_entrypoint_errors: list[str] = []
    for item in registry:
        slug = str(item.get("slug", "")).strip() or "<missing-slug>"
        for field in REQUIRED_REGISTRY_FIELDS:
            if field not in item:
                registry_field_errors.append(f"{slug}: missing registry field '{field}'")

        main_entrypoints = item.get("main_entrypoints", [])
        verification_entrypoints = item.get("verification_entrypoints", [])
        if not isinstance(main_entrypoints, list) or not main_entrypoints:
            registry_entrypoint_errors.append(f"{slug}: registry main_entrypoints must be a non-empty list")
        if not isinstance(verification_entrypoints, list) or not verification_entrypoints:
            registry_entrypoint_errors.append(f"{slug}: registry verification_entrypoints must be a non-empty list")

        if "port_mode_default" in item:
            mode = str(item.get("port_mode_default", "")).strip().lower()
            if mode not in PORT_MODE_VALUES:
                registry_field_errors.append(f"{slug}: invalid registry port_mode_default '{mode}'")

        if "port_range" in item:
            try:
                parse_port_range(item.get("port_range"), label=f"{slug}.registry")
            except ValueError as exc:
                registry_field_errors.append(str(exc))

        if "service_ports" in item:
            try:
                parse_service_ports(item.get("service_ports"), label=f"{slug}.registry")
            except ValueError as exc:
                registry_field_errors.append(str(exc))

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

    executed_checks.append("runtime_namespace_conflicts")
    runtime_namespaces = [str(item.get("runtime_namespace", "")).strip() for item in registry]
    runtime_ns_unique = {value for value in runtime_namespaces if value}
    if len(runtime_ns_unique) != len(runtime_namespaces):
        failed_checks.append("runtime_namespace_conflicts")
        errors.append("runtime_namespace conflict detected in project_registry")
    elif any(not value for value in runtime_namespaces):
        failed_checks.append("runtime_namespace_conflicts")
        errors.append("runtime_namespace must be non-empty for all registry entries")
    else:
        passed_checks.append("runtime_namespace_conflicts")

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
    status_errors: list[str] = []
    category_warnings: list[str] = []
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
    path_errors: list[str] = []
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

    isolation_records: list[dict[str, Any]] = []
    executed_checks.append("project_manifest_contract")
    contract_errors: list[str] = []
    entrypoint_warnings: list[str] = []
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
            contract_errors.append(
                f"{slug}: manifest status '{manifest_status}' != registry status '{registry_status}'"
            )

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

        runtime_namespace = str(manifest.get("runtime_namespace", "")).strip()
        if not runtime_namespace:
            contract_errors.append(f"{slug}: runtime_namespace must be non-empty")

        port_mode = str(manifest.get("port_mode_default", "")).strip().lower()
        if port_mode not in PORT_MODE_VALUES:
            contract_errors.append(f"{slug}: invalid port_mode_default '{port_mode}'")

        manifest_range: tuple[int, int] | None = None
        try:
            manifest_range = parse_port_range(manifest.get("port_range"), label=f"{slug}.manifest")
        except ValueError as exc:
            contract_errors.append(str(exc))

        manifest_service_ports: dict[str, int] = {}
        try:
            manifest_service_ports = parse_service_ports(
                manifest.get("service_ports"), label=f"{slug}.manifest"
            )
        except ValueError as exc:
            contract_errors.append(str(exc))

        runtime_paths = manifest.get("runtime_paths")
        state_paths = manifest.get("state_paths")
        if not isinstance(runtime_paths, dict):
            contract_errors.append(f"{slug}: runtime_paths must be an object")
            runtime_paths = {}
        if not isinstance(state_paths, dict):
            contract_errors.append(f"{slug}: state_paths must be an object")
            state_paths = {}

        for key in REQUIRED_RUNTIME_PATH_KEYS:
            if key not in runtime_paths or not str(runtime_paths.get(key, "")).strip():
                contract_errors.append(f"{slug}: runtime_paths missing '{key}'")
        for key in REQUIRED_STATE_PATH_KEYS:
            if key not in state_paths or not str(state_paths.get(key, "")).strip():
                contract_errors.append(f"{slug}: state_paths missing '{key}'")

        registry_runtime_ns = str(item.get("runtime_namespace", "")).strip()
        if registry_runtime_ns and runtime_namespace and registry_runtime_ns != runtime_namespace:
            contract_errors.append(
                f"{slug}: runtime_namespace mismatch (registry='{registry_runtime_ns}' manifest='{runtime_namespace}')"
            )

        try:
            registry_range = parse_port_range(item.get("port_range"), label=f"{slug}.registry")
            if manifest_range and registry_range != manifest_range:
                contract_errors.append(
                    f"{slug}: port_range mismatch (registry={registry_range} manifest={manifest_range})"
                )
        except ValueError as exc:
            contract_errors.append(str(exc))

        try:
            registry_service_ports = parse_service_ports(
                item.get("service_ports"), label=f"{slug}.registry"
            )
            if manifest_service_ports and registry_service_ports != manifest_service_ports:
                contract_errors.append(
                    f"{slug}: service_ports mismatch between registry and manifest"
                )
        except ValueError as exc:
            contract_errors.append(str(exc))

        if manifest_range is not None and runtime_namespace:
            isolation_records.append(
                {
                    "slug": slug,
                    "runtime_namespace": runtime_namespace,
                    "port_range": {"start": manifest_range[0], "end": manifest_range[1]},
                    "port_mode_default": port_mode,
                    "service_ports": manifest_service_ports,
                    "runtime_paths": {k: normalize_rel_path(v) for k, v in runtime_paths.items()},
                    "state_paths": {k: normalize_rel_path(v) for k, v in state_paths.items()},
                }
            )

    if contract_errors:
        failed_checks.append("project_manifest_contract")
        errors.extend(contract_errors)
    else:
        if entrypoint_warnings:
            warned_checks.append("project_manifest_contract")
            warnings.extend(entrypoint_warnings)
        else:
            passed_checks.append("project_manifest_contract")

    executed_checks.append("port_range_overlaps")
    overlap_errors: list[str] = []
    for idx, left in enumerate(isolation_records):
        a = (int(left["port_range"]["start"]), int(left["port_range"]["end"]))
        for right in isolation_records[idx + 1 :]:
            b = (int(right["port_range"]["start"]), int(right["port_range"]["end"]))
            if ranges_overlap(a, b):
                overlap_errors.append(
                    f"port_range overlap: {left['slug']} {a[0]}-{a[1]} intersects {right['slug']} {b[0]}-{b[1]}"
                )
    if overlap_errors:
        failed_checks.append("port_range_overlaps")
        errors.extend(overlap_errors)
    else:
        passed_checks.append("port_range_overlaps")

    executed_checks.append("service_port_conflicts")
    service_errors: list[str] = []
    global_service_ports: dict[int, list[str]] = {}
    for record in isolation_records:
        slug = str(record["slug"])
        start = int(record["port_range"]["start"])
        end = int(record["port_range"]["end"])
        local_ports: set[int] = set()
        for service_name, port in record["service_ports"].items():
            if port < start or port > end:
                service_errors.append(
                    f"{slug}: service port {service_name}={port} outside range {start}-{end}"
                )
            if port in local_ports:
                service_errors.append(f"{slug}: duplicate local service port {port}")
            local_ports.add(port)
            global_service_ports.setdefault(port, []).append(f"{slug}.{service_name}")

    for port, owners in sorted(global_service_ports.items()):
        if len(owners) > 1:
            service_errors.append(f"global service port conflict on {port}: {owners}")

    if service_errors:
        failed_checks.append("service_port_conflicts")
        errors.extend(service_errors)
    else:
        passed_checks.append("service_port_conflicts")

    executed_checks.append("runtime_state_paths")
    runtime_path_errors: list[str] = []
    runtime_path_conflicts: dict[str, list[str]] = {}
    runtime_root_hint = str(
        workspace.get("isolation_policy", {})
        .get("runtime_layout", {})
        .get("runtime_root", "runtime/projects")
    ).strip()
    require_scoped_paths = bool(
        workspace.get("isolation_policy", {})
        .get("runtime_layout", {})
        .get("require_project_scoped_paths", True)
    )

    for record in isolation_records:
        slug = str(record["slug"])
        runtime_namespace = str(record["runtime_namespace"])
        for key, rel_path in {**record["runtime_paths"], **record["state_paths"]}.items():
            normalized = normalize_rel_path(rel_path)
            if not normalized:
                runtime_path_errors.append(f"{slug}: empty runtime/state path for '{key}'")
                continue

            absolute = (repo_root / normalized).resolve()
            if not is_relative_to(absolute, repo_root.resolve()):
                runtime_path_errors.append(f"{slug}: path '{key}' escapes repository: {normalized}")
                continue

            if runtime_root_hint and not normalized.lower().startswith(runtime_root_hint.lower()):
                runtime_path_errors.append(
                    f"{slug}: path '{key}' must be inside runtime root '{runtime_root_hint}': {normalized}"
                )

            if require_scoped_paths and not is_project_scoped_path(
                normalized, slug=slug, runtime_namespace=runtime_namespace
            ):
                runtime_path_errors.append(
                    f"{slug}: path '{key}' is not project-scoped for runtime namespace '{runtime_namespace}'"
                )

            runtime_path_conflicts.setdefault(str(absolute).lower(), []).append(f"{slug}.{key}")

    for absolute_path, owners in runtime_path_conflicts.items():
        if len(owners) > 1:
            runtime_path_errors.append(f"runtime path conflict: {absolute_path} shared by {owners}")

    if runtime_path_errors:
        failed_checks.append("runtime_state_paths")
        errors.extend(runtime_path_errors)
    else:
        passed_checks.append("runtime_state_paths")

    executed_checks.append("outside_system_projects")
    projects_root = repo_root / str(workspace.get("root_paths", {}).get("projects_root", "projects"))
    outside_projects = []
    if projects_root.exists():
        candidates = discover_candidate_project_dirs(projects_root)
        for candidate in candidates:
            in_registry = any(candidate.resolve() == path for path in registered_roots.values())
            nested_in_registered = any(
                is_relative_to(candidate.resolve(), path) and candidate.resolve() != path
                for path in registered_roots.values()
            )
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
        "isolation_matrix": isolation_records,
        "outside_system_projects": outside_projects,
        "artifacts": {
            "validation_summary_json": str(output_dir / "validation_summary.json"),
            "validation_summary_md": str(output_dir / "validation_summary.md"),
        },
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
