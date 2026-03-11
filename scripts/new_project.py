#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_STATUSES = ["active", "supporting", "experimental", "archived", "legacy"]
ALLOWED_TYPES = ["desktop_app", "backend_service", "tool", "prototype", "library"]
PORT_MODE_VALUES = {"fixed", "auto"}

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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _prompt(label: str, *, default: str | None = None, allowed: list[str] | None = None) -> str:
    hint = f" [{default}]" if default else ""
    allowed_hint = f" ({', '.join(allowed)})" if allowed else ""
    while True:
        value = input(f"{label}{allowed_hint}{hint}: ").strip()
        if not value and default is not None:
            value = default
        if not value:
            print("Value is required.")
            continue
        if allowed and value not in allowed:
            print(f"Invalid value: {value}")
            continue
        return value


def _preset_structure(repo_root: Path, project_type: str) -> dict[str, Any]:
    path = (
        repo_root
        / "workspace_config"
        / "templates"
        / "project_template"
        / "presets"
        / project_type
        / "structure.json"
    )
    if not path.exists():
        raise FileNotFoundError(f"Missing preset structure: {path}")
    return _load_json(path)


def _default_category(project_type: str, preset: dict[str, Any]) -> str:
    if project_type == "prototype":
        return "research_prototype"
    if project_type in {"desktop_app", "tool"}:
        return "desktop_tool"
    if project_type in {"backend_service", "library"}:
        return "platform_core"
    return str(preset.get("default_category", "desktop_tool"))


def _status_index_with(registry: list[dict[str, Any]], statuses: list[str]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {status: [] for status in statuses}
    for item in registry:
        status = str(item.get("status", "")).strip()
        slug = str(item.get("slug", "")).strip()
        if status in mapping and slug:
            mapping[status].append(slug)
    return mapping


def _create_scaffold(project_root: Path, directories: list[str]) -> None:
    project_root.mkdir(parents=True, exist_ok=False)
    for rel in directories:
        (project_root / rel).mkdir(parents=True, exist_ok=True)


def _write_project_readme(path: Path, *, name: str, status: str, project_type: str, slug: str) -> None:
    lines = [
        f"# {name}",
        "",
        "## Overview",
        f"Project slug: `{slug}`",
        f"Project type: `{project_type}`",
        f"Workspace status: `{status}`",
        "",
        "## Entry points",
        "Use startup preflight wrappers from `run_project.ps1`.",
        "See `PROJECT_MANIFEST.json` for machine-readable entrypoints.",
        "",
        "## Notes",
        "This project was generated via `python scripts/new_project.py`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_port_range(raw: Any) -> tuple[int, int] | None:
    if not isinstance(raw, dict):
        return None
    try:
        start = int(raw.get("start"))
        end = int(raw.get("end"))
    except Exception:
        return None
    if start < 1 or end > 65535 or start > end:
        return None
    return start, end


def _ranges_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def _read_allocator_settings(workspace: dict[str, Any]) -> tuple[int, int, int, str, str]:
    isolation = workspace.get("isolation_policy", {})
    allocator = isolation.get("port_allocator", {}) if isinstance(isolation, dict) else {}
    runtime_layout = isolation.get("runtime_layout", {}) if isinstance(isolation, dict) else {}

    base_start = int(allocator.get("base_start", 8000))
    range_size = int(allocator.get("range_size", 100))
    max_end = int(allocator.get("max_end", 19999))
    default_mode = str(allocator.get("default_mode", "fixed")).strip().lower()
    runtime_root = str(runtime_layout.get("runtime_root", "runtime/projects")).strip()

    if base_start < 1:
        raise ValueError("isolation_policy.port_allocator.base_start must be >= 1")
    if range_size < 10:
        raise ValueError("isolation_policy.port_allocator.range_size must be >= 10")
    if max_end > 65535:
        raise ValueError("isolation_policy.port_allocator.max_end must be <= 65535")
    if default_mode not in PORT_MODE_VALUES:
        raise ValueError("isolation_policy.port_allocator.default_mode must be 'fixed' or 'auto'")
    if not runtime_root:
        raise ValueError("isolation_policy.runtime_layout.runtime_root must be non-empty")

    return base_start, range_size, max_end, default_mode, runtime_root


def _next_free_port_range(
    registry: list[dict[str, Any]],
    *,
    base_start: int,
    range_size: int,
    max_end: int,
) -> tuple[int, int]:
    used_ranges: list[tuple[int, int]] = []
    for item in registry:
        parsed = _parse_port_range(item.get("port_range"))
        if parsed is not None:
            used_ranges.append(parsed)

    candidate_start = base_start
    while True:
        candidate_end = candidate_start + range_size - 1
        if candidate_end > max_end:
            raise RuntimeError("No free port range available in configured allocator bounds")

        candidate = (candidate_start, candidate_end)
        has_overlap = any(_ranges_overlap(candidate, existing) for existing in used_ranges)
        if not has_overlap:
            return candidate
        candidate_start += range_size


def _runtime_contract(
    *,
    slug: str,
    range_start: int,
    range_end: int,
    port_mode_default: str,
    runtime_root: str,
) -> dict[str, Any]:
    runtime_namespace = slug
    runtime_base = f"{runtime_root}/{runtime_namespace}"

    service_ports = {
        "api_port": range_start,
        "ui_bridge_port": range_start + 10,
        "update_port": range_start + 20,
        "health_port": range_start + 30,
    }
    for name, port in service_ports.items():
        if port < range_start or port > range_end:
            raise ValueError(f"Service port '{name}'={port} is outside allocated range {range_start}-{range_end}")

    runtime_paths = {
        "runtime_dir": runtime_base,
        "log_dir": f"{runtime_base}/logs",
        "data_dir": f"{runtime_base}/data",
        "cache_dir": f"{runtime_base}/cache",
        "temp_dir": f"{runtime_base}/temp",
        "diagnostics_dir": f"{runtime_base}/diagnostics",
        "update_artifacts_dir": f"{runtime_base}/update_artifacts",
        "verification_dir": f"{runtime_base}/verification",
    }
    state_paths = {
        "db_path": f"{runtime_base}/db/{slug}.db",
        "state_path": f"{runtime_base}/state/runtime_state.json",
    }

    return {
        "runtime_namespace": runtime_namespace,
        "port_range": {"start": range_start, "end": range_end},
        "port_mode_default": port_mode_default,
        "service_ports": service_ports,
        "runtime_paths": runtime_paths,
        "state_paths": state_paths,
    }


def _build_project_manifest(
    *,
    name: str,
    slug: str,
    description: str,
    status: str,
    category: str,
    project_type: str,
    priority: int,
    root_path: str,
    readme_path: str,
    main_entrypoint: str,
    verify_entrypoint: str,
    dependencies_file: str,
    owner: str,
    runtime_contract: dict[str, Any],
) -> dict[str, Any]:
    user_entry = "powershell -ExecutionPolicy Bypass -File .\\run_project.ps1 -Mode user -PortMode fixed"
    dev_entry = "powershell -ExecutionPolicy Bypass -File .\\run_project.ps1 -Mode developer -PortMode fixed"
    verify_entry = "powershell -ExecutionPolicy Bypass -File .\\run_project.ps1 -Mode verify -PortMode fixed"

    runtime_dirs = list(runtime_contract["runtime_paths"].values())
    log_dirs = [
        runtime_contract["runtime_paths"]["log_dir"],
        runtime_contract["runtime_paths"]["diagnostics_dir"],
    ]
    data_dirs = [runtime_contract["runtime_paths"]["data_dir"]]

    payload: dict[str, Any] = {
        "schema_version": "2.1.0",
        "name": name,
        "slug": slug,
        "description": description,
        "status": status,
        "category": category,
        "type": project_type,
        "priority": priority,
        "root_path": root_path,
        "readme_path": readme_path,
        "runtime_namespace": runtime_contract["runtime_namespace"],
        "port_range": runtime_contract["port_range"],
        "port_mode_default": runtime_contract["port_mode_default"],
        "service_ports": runtime_contract["service_ports"],
        "runtime_paths": runtime_contract["runtime_paths"],
        "state_paths": runtime_contract["state_paths"],
        "health_path": "/health",
        "env_overrides": {},
        "main_entrypoints": [
            user_entry,
            dev_entry,
            verify_entry,
        ],
        "verification_entrypoints": [verify_entrypoint],
        "user_mode_entrypoint": user_entry,
        "developer_mode_entrypoint": dev_entry,
        "update_entrypoint": "not_applicable",
        "config_files": [dependencies_file],
        "runtime_dirs": runtime_dirs,
        "log_dirs": log_dirs,
        "data_dirs": data_dirs,
        "dependencies_file": dependencies_file,
        "owner": owner,
        "maturity_level": "prototype" if project_type == "prototype" else "early",
        "tags": ["generated", project_type, status],
        "notes": [
            "Generated by scripts/new_project.py.",
            "Runtime namespace and port isolation configured automatically.",
            f"Preset main entrypoint suggestion: {main_entrypoint}",
        ],
    }
    for field in REQUIRED_PROJECT_MANIFEST_FIELDS:
        if field not in payload:
            raise ValueError(f"Missing required manifest field during generation: {field}")
    return payload


def _registry_entry(
    *,
    slug: str,
    name: str,
    status: str,
    category: str,
    project_type: str,
    priority: int,
    root_path: str,
    manifest_rel: str,
    readme_rel: str,
    runtime_contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        "slug": slug,
        "name": name,
        "status": status,
        "category": category,
        "type": project_type,
        "priority": priority,
        "runtime_namespace": runtime_contract["runtime_namespace"],
        "port_range": runtime_contract["port_range"],
        "port_mode_default": runtime_contract["port_mode_default"],
        "service_ports": runtime_contract["service_ports"],
        "root_path": root_path,
        "manifest_path": manifest_rel,
        "readme_path": readme_rel,
        "main_entrypoints": [
            f"python scripts/project_startup.py run --project-slug {slug} --entrypoint user --startup-kind user --port-mode {runtime_contract['port_mode_default']}",
            f"python scripts/project_startup.py run --project-slug {slug} --entrypoint developer --startup-kind developer --port-mode {runtime_contract['port_mode_default']}",
            f"python scripts/project_startup.py run --project-slug {slug} --entrypoint verify --startup-kind verify --port-mode {runtime_contract['port_mode_default']}",
        ],
        "verification_entrypoints": [f"python scripts/project_startup.py run --project-slug {slug} --entrypoint verify --startup-kind verify --port-mode {runtime_contract['port_mode_default']}"],
        "update_entrypoints": [],
    }


def _write_project_runner_script(
    *,
    path: Path,
    slug: str,
    user_command: str,
    developer_command: str,
    verify_command: str,
) -> None:
    user_cmd = user_command.replace("`", "``").replace('"', '`"')
    dev_cmd = developer_command.replace("`", "``").replace('"', '`"')
    verify_cmd = verify_command.replace("`", "``").replace('"', '`"')

    script = f"""$ErrorActionPreference = "Stop"

param(
    [ValidateSet("user", "developer", "verify")]
    [string]$Mode = "user",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed"
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$cursor = $projectRoot
$repoRoot = $null
while ($true) {{
    if (Test-Path (Join-Path $cursor "workspace_config\\workspace_manifest.json")) {{
        $repoRoot = $cursor
        break
    }}
    $parent = Split-Path -Parent $cursor
    if ($parent -eq $cursor) {{
        throw "Unable to locate workspace root from project path: $projectRoot"
    }}
    $cursor = $parent
}}

$startupScript = Join-Path $repoRoot "scripts\\project_startup.py"
$startupRaw = & python $startupScript prepare --project-slug {slug} --startup-kind $Mode --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {{
    throw "Startup preflight failed for project: {slug}"
}}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {{
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}}

$command = ""
if ($Mode -eq "user") {{
    $command = "{user_cmd}"
}} elseif ($Mode -eq "developer") {{
    $command = "{dev_cmd}"
}} else {{
    $command = "{verify_cmd}"
}}

Invoke-Expression $command
exit $LASTEXITCODE
"""
    path.write_text(script + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and register a workspace project from standard preset")
    parser.add_argument("--name", help="Project display name")
    parser.add_argument("--slug", help="Project slug (unique)")
    parser.add_argument("--status", choices=ALLOWED_STATUSES, help="Project status")
    parser.add_argument("--type", dest="project_type", choices=ALLOWED_TYPES, help="Project preset type")
    parser.add_argument("--category", help="Project category (defaults from preset)")
    parser.add_argument("--description", default="", help="Project description")
    parser.add_argument("--owner", default="workspace-owner", help="Project owner marker")
    parser.add_argument("--relative-path", default="", help="Project path relative to repo root")
    parser.add_argument("--set-active", action="store_true", help="Allow switching active project when status=active")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print changes without writing")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_manifest_path = repo_root / "workspace_config" / "workspace_manifest.json"
    workspace = _load_json(workspace_manifest_path)

    name = args.name or _prompt("Project name")
    slug = args.slug or _prompt("Project slug")
    status = args.status or _prompt("Project status", default="experimental", allowed=ALLOWED_STATUSES)
    project_type = args.project_type or _prompt("Project type", default="tool", allowed=ALLOWED_TYPES)

    preset = _preset_structure(repo_root, project_type)
    category = args.category or _default_category(project_type, preset)
    description = args.description.strip() or f"{name} ({project_type}) generated workspace project."

    registry = list(workspace.get("project_registry", []))
    slugs = {str(item.get("slug", "")).strip() for item in registry}
    if slug in slugs:
        raise SystemExit(f"Slug already exists in workspace manifest: {slug}")

    active_slug = str(workspace.get("active_project", "")).strip()
    if status == "active" and active_slug and active_slug != slug and not args.set_active:
        raise SystemExit(
            f"Active project already set to '{active_slug}'. Use --set-active to switch active project to '{slug}'."
        )

    relative_path = args.relative_path.strip() if args.relative_path else f"projects/{slug}"
    root_path = relative_path.replace("\\", "/")
    project_root = repo_root / Path(relative_path)
    manifest_rel = f"{root_path}/PROJECT_MANIFEST.json"
    readme_rel = f"{root_path}/README.md"

    if project_root.exists():
        raise SystemExit(f"Project path already exists: {project_root}")

    max_priority = 0
    for item in registry:
        try:
            max_priority = max(max_priority, int(item.get("priority", 0)))
        except Exception:
            continue
    next_priority = max_priority + 1

    main_entrypoint = str(preset.get("main_entrypoint", "python -m main"))
    verify_entrypoint = str(preset.get("verification_entrypoint", "python -m pytest -q"))
    dependencies_file = str(preset.get("dependencies_file", "requirements.txt"))
    directories = [str(item) for item in preset.get("directories", [])]

    base_start, range_size, max_end, default_mode, runtime_root = _read_allocator_settings(workspace)
    range_start, range_end = _next_free_port_range(
        registry,
        base_start=base_start,
        range_size=range_size,
        max_end=max_end,
    )
    runtime_contract = _runtime_contract(
        slug=slug,
        range_start=range_start,
        range_end=range_end,
        port_mode_default=default_mode,
        runtime_root=runtime_root,
    )

    project_manifest = _build_project_manifest(
        name=name,
        slug=slug,
        description=description,
        status=status,
        category=category,
        project_type=project_type,
        priority=next_priority,
        root_path=root_path,
        readme_path=readme_rel,
        main_entrypoint=main_entrypoint,
        verify_entrypoint=verify_entrypoint,
        dependencies_file=dependencies_file,
        owner=args.owner,
        runtime_contract=runtime_contract,
    )

    registry_item = _registry_entry(
        slug=slug,
        name=name,
        status=status,
        category=category,
        project_type=project_type,
        priority=next_priority,
        root_path=root_path,
        manifest_rel=manifest_rel,
        readme_rel=readme_rel,
        runtime_contract=runtime_contract,
    )

    updated_registry = sorted([*registry, registry_item], key=lambda item: int(item.get("priority", 999999)))
    workspace["project_registry"] = updated_registry

    if status == "active":
        workspace["active_project"] = slug

    statuses = [str(item) for item in workspace.get("status_values", ALLOWED_STATUSES)]
    workspace["project_status_index"] = _status_index_with(updated_registry, statuses)

    if args.dry_run:
        print("[new-project] dry-run successful")
        print(f"[new-project] slug={slug}")
        print(f"[new-project] root_path={root_path}")
        print(f"[new-project] status={status} type={project_type}")
        print(f"[new-project] runtime_namespace={runtime_contract['runtime_namespace']}")
        print(
            f"[new-project] port_range={runtime_contract['port_range']['start']}-{runtime_contract['port_range']['end']}"
        )
        return 0

    _create_scaffold(project_root, directories)

    readme_path = repo_root / readme_rel
    manifest_path = repo_root / manifest_rel
    _write_project_readme(readme_path, name=name, status=status, project_type=project_type, slug=slug)
    _write_json(manifest_path, project_manifest)

    deps_path = project_root / dependencies_file
    if not deps_path.exists():
        deps_path.write_text("\n", encoding="utf-8")

    runner_path = project_root / "run_project.ps1"
    _write_project_runner_script(
        path=runner_path,
        slug=slug,
        user_command=main_entrypoint,
        developer_command=main_entrypoint,
        verify_command=verify_entrypoint,
    )

    # Ensure isolated runtime tree is ready.
    for runtime_path in runtime_contract["runtime_paths"].values():
        (repo_root / runtime_path).mkdir(parents=True, exist_ok=True)
    for state_path in runtime_contract["state_paths"].values():
        (repo_root / state_path).parent.mkdir(parents=True, exist_ok=True)

    _write_json(workspace_manifest_path, workspace)

    print(f"[new-project] created: {root_path}")
    print(f"[new-project] manifest: {manifest_rel}")
    print(f"[new-project] runtime_namespace: {runtime_contract['runtime_namespace']}")
    print(f"[new-project] port_range: {range_start}-{range_end}")
    print(f"[new-project] workspace registry updated: {workspace_manifest_path}")
    print("[new-project] next step: python scripts/validate_workspace.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
