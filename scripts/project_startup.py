#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
TEMPLATE_RE = re.compile(r"\{([a-zA-Z0-9_.-]+)\}")


class StartupError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProjectContext:
    repo_root: Path
    project_slug: str
    project_root: Path
    project_manifest: dict[str, Any]
    registry_entry: dict[str, Any]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _resolve_path_in_repo(repo_root: Path, raw_path: Any, *, field_name: str) -> Path:
    value = str(raw_path or "").strip()
    if not value:
        raise StartupError(f"Missing path value for '{field_name}'")
    candidate = Path(value).expanduser()
    absolute = candidate if candidate.is_absolute() else (repo_root / candidate)
    absolute = absolute.resolve()
    if not _is_relative_to(absolute, repo_root.resolve()):
        raise StartupError(f"Path for '{field_name}' must stay inside repository root: {value}")
    return absolute


def _as_int(raw: Any, *, field_name: str) -> int:
    try:
        return int(raw)
    except Exception as exc:  # pragma: no cover - defensive branch
        raise StartupError(f"Field '{field_name}' must be integer: {raw!r}") from exc


def _load_context(repo_root: Path, project_slug: str) -> ProjectContext:
    workspace_manifest_path = repo_root / "workspace_config" / "workspace_manifest.json"
    if not workspace_manifest_path.exists():
        raise StartupError(f"Missing workspace manifest: {workspace_manifest_path}")

    workspace = _load_json(workspace_manifest_path)
    registry = list(workspace.get("project_registry", []))
    matched = [item for item in registry if str(item.get("slug", "")).strip() == project_slug]
    if len(matched) != 1:
        raise StartupError(f"Project slug '{project_slug}' is not unique in workspace registry")

    entry = matched[0]
    manifest_rel = str(entry.get("manifest_path", "")).strip()
    root_rel = str(entry.get("root_path", "")).strip()
    if not manifest_rel or not root_rel:
        raise StartupError(f"Project '{project_slug}' registry entry is missing manifest_path/root_path")

    project_manifest_path = (repo_root / manifest_rel).resolve()
    project_root = (repo_root / root_rel).resolve()
    if not project_manifest_path.exists():
        raise StartupError(f"Project manifest missing: {project_manifest_path}")
    if not project_root.exists():
        raise StartupError(f"Project root missing: {project_root}")

    project_manifest = _load_json(project_manifest_path)
    manifest_slug = str(project_manifest.get("slug", "")).strip()
    if manifest_slug != project_slug:
        raise StartupError(
            f"Project manifest slug mismatch: requested='{project_slug}' manifest='{manifest_slug}'"
        )

    return ProjectContext(
        repo_root=repo_root,
        project_slug=project_slug,
        project_root=project_root,
        project_manifest=project_manifest,
        registry_entry=entry,
    )


def _validate_runtime_namespace(manifest: dict[str, Any], slug: str) -> str:
    runtime_namespace = str(manifest.get("runtime_namespace", "")).strip()
    if not runtime_namespace:
        raise StartupError(f"{slug}: missing runtime_namespace in project manifest")
    return runtime_namespace


def _validate_port_contract(manifest: dict[str, Any], slug: str) -> tuple[int, int, str, dict[str, int]]:
    port_range = manifest.get("port_range")
    if not isinstance(port_range, dict):
        raise StartupError(f"{slug}: missing object 'port_range' in project manifest")

    start = _as_int(port_range.get("start"), field_name=f"{slug}.port_range.start")
    end = _as_int(port_range.get("end"), field_name=f"{slug}.port_range.end")
    if start < 1 or end > 65535 or start > end:
        raise StartupError(f"{slug}: invalid port_range {start}-{end}")

    default_mode = str(manifest.get("port_mode_default", "fixed")).strip().lower()
    if default_mode not in PORT_MODE_VALUES:
        raise StartupError(f"{slug}: invalid port_mode_default '{default_mode}'")

    service_ports_raw = manifest.get("service_ports")
    if not isinstance(service_ports_raw, dict) or not service_ports_raw:
        raise StartupError(f"{slug}: missing object 'service_ports' in project manifest")

    service_ports: dict[str, int] = {}
    for key, raw_value in service_ports_raw.items():
        name = str(key).strip().lower()
        if not name:
            raise StartupError(f"{slug}: service_ports key must be non-empty")
        port = _as_int(raw_value, field_name=f"{slug}.service_ports.{name}")
        if port < start or port > end:
            raise StartupError(f"{slug}: service port {name}={port} outside range {start}-{end}")
        if port in service_ports.values():
            raise StartupError(f"{slug}: duplicate service port value {port} in service_ports")
        service_ports[name] = port

    return start, end, default_mode, service_ports


def _validate_runtime_paths(
    *,
    repo_root: Path,
    manifest: dict[str, Any],
    slug: str,
    runtime_namespace: str,
) -> tuple[dict[str, Path], dict[str, Path]]:
    runtime_paths_raw = manifest.get("runtime_paths")
    state_paths_raw = manifest.get("state_paths")

    if not isinstance(runtime_paths_raw, dict):
        raise StartupError(f"{slug}: missing object 'runtime_paths' in project manifest")
    if not isinstance(state_paths_raw, dict):
        raise StartupError(f"{slug}: missing object 'state_paths' in project manifest")

    runtime_paths: dict[str, Path] = {}
    state_paths: dict[str, Path] = {}

    for key in REQUIRED_RUNTIME_PATH_KEYS:
        if key not in runtime_paths_raw:
            raise StartupError(f"{slug}: runtime_paths missing key '{key}'")
        runtime_paths[key] = _resolve_path_in_repo(
            repo_root,
            runtime_paths_raw.get(key),
            field_name=f"{slug}.runtime_paths.{key}",
        )

    for key in REQUIRED_STATE_PATH_KEYS:
        if key not in state_paths_raw:
            raise StartupError(f"{slug}: state_paths missing key '{key}'")
        state_paths[key] = _resolve_path_in_repo(
            repo_root,
            state_paths_raw.get(key),
            field_name=f"{slug}.state_paths.{key}",
        )

    # Guard against cross-project runtime mixing.
    marker = runtime_namespace.lower()
    for key, path in {**runtime_paths, **state_paths}.items():
        normalized = str(path).replace("\\", "/").lower()
        if marker not in normalized and slug.lower() not in normalized:
            raise StartupError(
                f"{slug}: path '{key}' is not project-scoped for namespace '{runtime_namespace}': {path}"
            )

    return runtime_paths, state_paths


def _is_port_available(port: int, host: str) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _fallback_candidates(start: int, end: int, preferred: int) -> list[int]:
    sequence: list[int] = []
    for value in range(preferred, end + 1):
        sequence.append(value)
    for value in range(start, preferred):
        sequence.append(value)
    return sequence


def _select_service_ports(
    *,
    host: str,
    mode: str,
    range_start: int,
    range_end: int,
    requested_ports: dict[str, int],
) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    selected: dict[str, int] = {}
    occupied: dict[str, int] = {}
    fallback: dict[str, int] = {}
    reserved: set[int] = set()

    for service_name, default_port in requested_ports.items():
        available = default_port not in reserved and _is_port_available(default_port, host)
        if mode == "fixed":
            if not available:
                occupied[service_name] = default_port
                continue
            selected[service_name] = default_port
            reserved.add(default_port)
            continue

        if available:
            selected[service_name] = default_port
            reserved.add(default_port)
            continue

        if not _is_port_available(default_port, host):
            occupied[service_name] = default_port

        picked: int | None = None
        for candidate in _fallback_candidates(range_start, range_end, default_port):
            if candidate in reserved:
                continue
            if not _is_port_available(candidate, host):
                continue
            picked = candidate
            break

        if picked is None:
            raise StartupError(
                f"No free fallback port for service '{service_name}' inside range {range_start}-{range_end}"
            )

        selected[service_name] = picked
        fallback[service_name] = picked
        reserved.add(picked)

    if mode == "fixed" and occupied:
        details = ", ".join(f"{name}={port}" for name, port in sorted(occupied.items()))
        raise StartupError(
            f"Fixed mode startup failed, occupied service ports detected before launch: {details}"
        )

    return selected, occupied, fallback


def _render_template(template: str, context: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        dotted = match.group(1)
        node: Any = context
        for part in dotted.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
                continue
            raise StartupError(f"Unknown template key '{dotted}' in env_overrides")
        return str(node)

    return TEMPLATE_RE.sub(replace, template)


def _build_environment(
    *,
    context: ProjectContext,
    runtime_namespace: str,
    range_start: int,
    range_end: int,
    mode: str,
    selected_ports: dict[str, int],
    runtime_paths: dict[str, Path],
    state_paths: dict[str, Path],
    backend_base_url: str,
    health_endpoint: str,
) -> dict[str, str]:
    env: dict[str, str] = {
        "PROJECT_SLUG": context.project_slug,
        "PROJECT_RUNTIME_NAMESPACE": runtime_namespace,
        "PROJECT_PORT_MODE": mode,
        "PROJECT_PORT_RANGE_START": str(range_start),
        "PROJECT_PORT_RANGE_END": str(range_end),
        "PROJECT_REPO_ROOT": str(context.repo_root),
        "PROJECT_ROOT": str(context.project_root),
        "PROJECT_BACKEND_BASE_URL": backend_base_url,
        "PROJECT_HEALTH_ENDPOINT": health_endpoint,
    }

    for key, value in selected_ports.items():
        env[f"PROJECT_{key.upper()}"] = str(value)
    for key, value in runtime_paths.items():
        env[f"PROJECT_{key.upper()}"] = str(value)
    for key, value in state_paths.items():
        env[f"PROJECT_{key.upper()}"] = str(value)

    overrides_raw = context.project_manifest.get("env_overrides", {})
    if overrides_raw is None:
        overrides_raw = {}
    if not isinstance(overrides_raw, dict):
        raise StartupError(f"{context.project_slug}: env_overrides must be an object")

    template_context = {
        "slug": context.project_slug,
        "runtime_namespace": runtime_namespace,
        "port_mode": mode,
        "port_range": {"start": range_start, "end": range_end},
        "service_ports": selected_ports,
        "runtime_paths": {k: str(v) for k, v in runtime_paths.items()},
        "state_paths": {k: str(v) for k, v in state_paths.items()},
        "backend_base_url": backend_base_url,
        "health_endpoint": health_endpoint,
        "repo_root": str(context.repo_root),
        "project_root": str(context.project_root),
    }

    for raw_key, raw_value in overrides_raw.items():
        key = str(raw_key or "").strip()
        if not key:
            raise StartupError(f"{context.project_slug}: env_overrides contains empty key")
        if isinstance(raw_value, str):
            env[key] = _render_template(raw_value, template_context)
        else:
            env[key] = str(raw_value)

    return env


def _resolve_entrypoint(manifest: dict[str, Any], *, entrypoint: str, main_index: int) -> str:
    if entrypoint == "user":
        command = str(manifest.get("user_mode_entrypoint", "")).strip()
        if not command:
            raise StartupError("Manifest user_mode_entrypoint is empty")
        return command

    if entrypoint == "developer":
        command = str(manifest.get("developer_mode_entrypoint", "")).strip()
        if not command:
            raise StartupError("Manifest developer_mode_entrypoint is empty")
        return command

    if entrypoint == "update":
        command = str(manifest.get("update_entrypoint", "")).strip()
        if not command or command == "not_applicable":
            raise StartupError("Manifest update_entrypoint is not applicable")
        return command

    if entrypoint == "verify":
        entries = list(manifest.get("verification_entrypoints", []))
        if not entries:
            raise StartupError("Manifest verification_entrypoints is empty")
        return str(entries[0]).strip()

    entries = list(manifest.get("main_entrypoints", []))
    if not entries:
        raise StartupError("Manifest main_entrypoints is empty")
    if main_index < 0 or main_index >= len(entries):
        raise StartupError(
            f"main_index {main_index} out of range for main_entrypoints (count={len(entries)})"
        )
    return str(entries[main_index]).strip()


def _write_startup_report(
    *,
    context: ProjectContext,
    runtime_namespace: str,
    mode: str,
    startup_kind: str,
    host: str,
    range_start: int,
    range_end: int,
    requested_ports: dict[str, int],
    selected_ports: dict[str, int],
    occupied_ports: dict[str, int],
    fallback_ports: dict[str, int],
    backend_base_url: str,
    health_endpoint: str,
    runtime_paths: dict[str, Path],
    state_paths: dict[str, Path],
    command: str | None,
) -> tuple[Path, Path, str]:
    started = _utc_now()
    run_id = f"{context.project_slug}-startup-{started.strftime('%Y%m%dT%H%M%SZ')}"
    startup_dir = runtime_paths["diagnostics_dir"] / "startup"
    startup_dir.mkdir(parents=True, exist_ok=True)
    json_path = startup_dir / f"{run_id}.json"
    md_path = startup_dir / f"{run_id}.md"

    payload = {
        "run_id": run_id,
        "started_at": _iso(started),
        "status": "READY",
        "project_slug": context.project_slug,
        "runtime_namespace": runtime_namespace,
        "startup_kind": startup_kind,
        "port_mode": mode,
        "host": host,
        "port_range": {"start": range_start, "end": range_end},
        "requested_ports": requested_ports,
        "selected_ports": selected_ports,
        "occupied_ports": occupied_ports,
        "fallback_ports": fallback_ports,
        "backend_base_url": backend_base_url,
        "health_endpoint": health_endpoint,
        "project_root": str(context.project_root),
        "runtime_paths": {k: str(v) for k, v in runtime_paths.items()},
        "state_paths": {k: str(v) for k, v in state_paths.items()},
        "command": command or "",
        "artifacts": {
            "startup_report_json": str(json_path),
            "startup_report_md": str(md_path),
        },
    }

    _write_json(json_path, payload)

    md_lines = [
        f"# Startup Diagnostics ({run_id})",
        "",
        f"- status: `READY`",
        f"- project_slug: `{context.project_slug}`",
        f"- runtime_namespace: `{runtime_namespace}`",
        f"- startup_kind: `{startup_kind}`",
        f"- port_mode: `{mode}`",
        f"- host: `{host}`",
        f"- port_range: `{range_start}-{range_end}`",
        f"- backend_base_url: `{backend_base_url}`",
        f"- health_endpoint: `{health_endpoint}`",
        "",
        "## Selected Ports",
    ]
    if selected_ports:
        md_lines.extend([f"- `{key}`: `{value}`" for key, value in selected_ports.items()])
    else:
        md_lines.append("- none")

    md_lines.extend(["", "## Occupied Ports"])
    if occupied_ports:
        md_lines.extend([f"- `{key}`: `{value}`" for key, value in occupied_ports.items()])
    else:
        md_lines.append("- none")

    md_lines.extend(["", "## Fallback Ports"])
    if fallback_ports:
        md_lines.extend([f"- `{key}`: `{value}`" for key, value in fallback_ports.items()])
    else:
        md_lines.append("- none")

    md_lines.extend(["", "## Runtime Paths"])
    for key, value in runtime_paths.items():
        md_lines.append(f"- `{key}`: `{value}`")

    md_lines.extend(["", "## State Paths"])
    for key, value in state_paths.items():
        md_lines.append(f"- `{key}`: `{value}`")

    if command:
        md_lines.extend(["", "## Command", f"- `{command}`"])

    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return json_path, md_path, run_id


def prepare_startup(
    *,
    repo_root: Path,
    project_slug: str,
    requested_mode: str | None,
    host: str,
    startup_kind: str,
    command: str | None,
) -> dict[str, Any]:
    context = _load_context(repo_root, project_slug)
    runtime_namespace = _validate_runtime_namespace(context.project_manifest, context.project_slug)

    range_start, range_end, default_mode, requested_ports = _validate_port_contract(
        context.project_manifest, context.project_slug
    )
    selected_mode = requested_mode or default_mode
    selected_mode = selected_mode.strip().lower()
    if selected_mode not in PORT_MODE_VALUES:
        raise StartupError(
            f"Invalid port mode '{selected_mode}', expected one of: {sorted(PORT_MODE_VALUES)}"
        )

    runtime_paths, state_paths = _validate_runtime_paths(
        repo_root=repo_root,
        manifest=context.project_manifest,
        slug=context.project_slug,
        runtime_namespace=runtime_namespace,
    )

    for _, directory in runtime_paths.items():
        directory.mkdir(parents=True, exist_ok=True)
    for _, file_path in state_paths.items():
        file_path.parent.mkdir(parents=True, exist_ok=True)

    selected_ports, occupied_ports, fallback_ports = _select_service_ports(
        host=host,
        mode=selected_mode,
        range_start=range_start,
        range_end=range_end,
        requested_ports=requested_ports,
    )

    api_port = int(selected_ports.get("api_port", range_start))
    backend_base_url = f"http://{host}:{api_port}"
    health_path = str(context.project_manifest.get("health_path", "/workspace/health")).strip() or "/workspace/health"
    if not health_path.startswith("/"):
        health_path = "/" + health_path
    health_endpoint = backend_base_url + health_path

    env = _build_environment(
        context=context,
        runtime_namespace=runtime_namespace,
        range_start=range_start,
        range_end=range_end,
        mode=selected_mode,
        selected_ports=selected_ports,
        runtime_paths=runtime_paths,
        state_paths=state_paths,
        backend_base_url=backend_base_url,
        health_endpoint=health_endpoint,
    )

    startup_json, startup_md, run_id = _write_startup_report(
        context=context,
        runtime_namespace=runtime_namespace,
        mode=selected_mode,
        startup_kind=startup_kind,
        host=host,
        range_start=range_start,
        range_end=range_end,
        requested_ports=requested_ports,
        selected_ports=selected_ports,
        occupied_ports=occupied_ports,
        fallback_ports=fallback_ports,
        backend_base_url=backend_base_url,
        health_endpoint=health_endpoint,
        runtime_paths=runtime_paths,
        state_paths=state_paths,
        command=command,
    )

    return {
        "status": "READY",
        "run_id": run_id,
        "project_slug": context.project_slug,
        "runtime_namespace": runtime_namespace,
        "startup_kind": startup_kind,
        "project_root": str(context.project_root),
        "port_mode": selected_mode,
        "port_range": {"start": range_start, "end": range_end},
        "requested_ports": requested_ports,
        "selected_ports": selected_ports,
        "occupied_ports": occupied_ports,
        "fallback_ports": fallback_ports,
        "backend_base_url": backend_base_url,
        "health_endpoint": health_endpoint,
        "runtime_paths": {k: str(v) for k, v in runtime_paths.items()},
        "state_paths": {k: str(v) for k, v in state_paths.items()},
        "startup_report_json": str(startup_json),
        "startup_report_md": str(startup_md),
        "env": env,
    }


def _command_prepare(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    result = prepare_startup(
        repo_root=repo_root,
        project_slug=args.project_slug,
        requested_mode=args.port_mode,
        host=args.host,
        startup_kind=args.startup_kind,
        command=None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _command_run(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    context = _load_context(repo_root, args.project_slug)
    command = _resolve_entrypoint(
        context.project_manifest,
        entrypoint=args.entrypoint,
        main_index=args.main_index,
    )

    prepared = prepare_startup(
        repo_root=repo_root,
        project_slug=args.project_slug,
        requested_mode=args.port_mode,
        host=args.host,
        startup_kind=args.startup_kind,
        command=command,
    )

    if args.dry_run:
        prepared["dry_run"] = True
        prepared["executed_command"] = command
        prepared["exit_code"] = 0
        print(json.dumps(prepared, ensure_ascii=False, indent=2))
        return 0

    run_env = os.environ.copy()
    for key, value in prepared["env"].items():
        run_env[key] = str(value)

    completed = subprocess.run(
        command,
        cwd=context.project_root,
        shell=True,
        env=run_env,
        check=False,
    )

    prepared["executed_command"] = command
    prepared["exit_code"] = int(completed.returncode)
    print(json.dumps(prepared, ensure_ascii=False, indent=2))
    return int(completed.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project startup preflight: runtime namespace + port isolation")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare", help="Run startup preflight and emit machine-readable diagnostics")
    prepare.add_argument("--project-slug", required=True, help="Project slug from workspace manifest")
    prepare.add_argument("--port-mode", choices=sorted(PORT_MODE_VALUES), default=None, help="Port selection mode")
    prepare.add_argument("--host", default="127.0.0.1", help="Host used for local port probing")
    prepare.add_argument(
        "--startup-kind",
        default="startup",
        help="Logical startup kind marker for diagnostics (user/developer/update/etc.)",
    )
    prepare.set_defaults(func=_command_prepare)

    run = sub.add_parser("run", help="Run preflight and then execute an entrypoint command")
    run.add_argument("--project-slug", required=True, help="Project slug from workspace manifest")
    run.add_argument("--entrypoint", choices=["user", "developer", "update", "verify", "main"], default="user")
    run.add_argument("--main-index", type=int, default=0, help="Index for entrypoint=main")
    run.add_argument("--port-mode", choices=sorted(PORT_MODE_VALUES), default=None, help="Port selection mode")
    run.add_argument("--host", default="127.0.0.1", help="Host used for local port probing")
    run.add_argument(
        "--startup-kind",
        default="startup",
        help="Logical startup kind marker for diagnostics (user/developer/update/etc.)",
    )
    run.add_argument("--dry-run", action="store_true", help="Do preflight and resolve command without execution")
    run.set_defaults(func=_command_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except StartupError as exc:
        print(f"[project-startup] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
