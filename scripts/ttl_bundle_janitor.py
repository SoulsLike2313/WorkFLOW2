#!/usr/bin/env python
from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT = "workspace_config/EPHEMERAL_BUNDLE_TTL_CONTRACT.json"


@dataclass
class RootEntry:
    path: Path
    rel_path: str
    name: str
    kind: str
    modified_at: str
    age_hours: float


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_rel(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.strip("/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def now_utc(args_now_utc: str) -> datetime:
    if args_now_utc:
        parsed = datetime.fromisoformat(args_now_utc.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def utc_stamp(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_git_ls_files(repo_root: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return set()
    values = [normalize_rel(line) for line in completed.stdout.splitlines() if line.strip()]
    return set(values)


def is_subpath(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def marker_protected(entry: Path, marker_files: list[str]) -> bool:
    for marker in marker_files:
        marker_name = marker.strip()
        if not marker_name:
            continue
        if entry.is_dir() and (entry / marker_name).exists():
            return True
        if entry.is_file() and (entry.parent / f"{entry.name}{marker_name}").exists():
            return True
    return False


def matches_any_glob(name: str, patterns: list[str]) -> bool:
    if not patterns:
        return True
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def load_pins(repo_root: Path, pins_file: str) -> set[str]:
    path = Path(pins_file).expanduser()
    if not path.is_absolute():
        path = (repo_root / path).resolve()
    if not path.exists():
        return set()
    payload = load_json(path)
    values = payload.get("pinned_paths", [])
    if not isinstance(values, list):
        return set()
    return {normalize_rel(str(item)) for item in values if str(item).strip()}


def root_entries(
    *,
    repo_root: Path,
    root_path: str,
    entry_types: list[str],
    name_globs: list[str],
    now: datetime,
) -> list[RootEntry]:
    root_abs = (repo_root / root_path).resolve()
    if not root_abs.exists() or not root_abs.is_dir():
        return []

    allowed_file = "file" in entry_types or not entry_types
    allowed_dir = "dir" in entry_types or not entry_types

    entries: list[RootEntry] = []
    for child in root_abs.iterdir():
        if child.is_dir() and not allowed_dir:
            continue
        if child.is_file() and not allowed_file:
            continue
        if not matches_any_glob(child.name, name_globs):
            continue
        mtime = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
        age_hours = max(0.0, (now - mtime).total_seconds() / 3600.0)
        rel = normalize_rel(str(child.relative_to(repo_root)))
        kind = "dir" if child.is_dir() else "file"
        entries.append(
            RootEntry(
                path=child,
                rel_path=rel,
                name=child.name,
                kind=kind,
                modified_at=utc_iso(mtime),
                age_hours=round(age_hours, 3),
            )
        )
    entries.sort(key=lambda item: item.path.stat().st_mtime, reverse=True)
    return entries


def tracked_protected(rel_path: str, kind: str, tracked_paths: set[str]) -> bool:
    if kind == "file":
        return rel_path in tracked_paths
    prefix = rel_path + "/"
    for tracked in tracked_paths:
        if tracked == rel_path or tracked.startswith(prefix):
            return True
    return False


def delete_entry(path: Path, kind: str) -> str | None:
    try:
        if kind == "dir":
            shutil.rmtree(path)
        else:
            path.unlink()
        return None
    except Exception as exc:  # pragma: no cover - defensive runtime capture
        return str(exc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TTL cleanup janitor for explicitly designated ephemeral bundle/revision roots."
    )
    parser.add_argument("--contract", default=DEFAULT_CONTRACT, help="Path to TTL contract JSON.")
    parser.add_argument(
        "--roots",
        nargs="*",
        default=[],
        help="Optional subset of root paths from contract (repo-relative).",
    )
    parser.add_argument("--ttl-hours", type=float, default=None, help="Optional TTL override in hours.")
    parser.add_argument("--apply", action="store_true", help="Apply deletion. Default mode is dry-run.")
    parser.add_argument(
        "--protect-name",
        nargs="*",
        default=[],
        help="Additional name globs to protect for this run.",
    )
    parser.add_argument(
        "--report-dir",
        default="",
        help="Optional report output directory override (repo-relative or absolute).",
    )
    parser.add_argument(
        "--now-utc",
        default="",
        help="Optional UTC timestamp override (ISO8601) for deterministic tests.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()
    now = now_utc(args.now_utc)

    contract_path = Path(args.contract).expanduser()
    if not contract_path.is_absolute():
        contract_path = (repo_root / contract_path).resolve()
    if not contract_path.exists():
        raise SystemExit(f"contract not found: {contract_path}")

    contract = load_json(contract_path)
    roots = list(contract.get("ephemeral_roots", []))
    if not roots:
        raise SystemExit("contract has no ephemeral_roots")

    selected_roots = {normalize_rel(item) for item in args.roots if normalize_rel(item)}
    if selected_roots:
        known = {normalize_rel(str(item.get("path", ""))) for item in roots}
        unknown = sorted(selected_roots - known)
        if unknown:
            raise SystemExit(f"unknown roots requested: {', '.join(unknown)}")
        roots = [item for item in roots if normalize_rel(str(item.get("path", ""))) in selected_roots]

    ttl_hours = float(args.ttl_hours if args.ttl_hours is not None else contract.get("default_ttl_hours", 24))
    apply_mode = bool(args.apply)

    safety = contract.get("safety", {})
    skip_tracked = bool(safety.get("skip_tracked_git_paths", True))
    require_subpath = bool(safety.get("require_scope_subpath", True))
    tracked_paths = run_git_ls_files(repo_root) if skip_tracked else set()

    protection = contract.get("protection", {})
    keep_latest_per_root = int(protection.get("keep_latest_per_root", 1))
    marker_files = [str(x) for x in protection.get("protect_marker_files", []) if str(x).strip()]
    contract_protect_globs = [str(x) for x in protection.get("protect_name_globs", []) if str(x).strip()]
    cli_protect_globs = [str(x) for x in args.protect_name if str(x).strip()]
    all_protect_globs = contract_protect_globs + cli_protect_globs
    pins_file = str(protection.get("pins_file", "")).strip()
    pinned_paths = load_pins(repo_root, pins_file) if pins_file else set()

    report_dir_raw = args.report_dir.strip() or str(contract.get("reporting", {}).get("default_report_root", "runtime/bundle_ttl_janitor"))
    report_dir = Path(report_dir_raw).expanduser()
    if not report_dir.is_absolute():
        report_dir = (repo_root / report_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)

    root_results: list[dict[str, Any]] = []
    total_deleted = 0
    total_would_delete = 0
    total_kept = 0
    total_errors = 0

    for root_def in roots:
        root_path = normalize_rel(str(root_def.get("path", "")))
        entry_types = [str(x).lower() for x in root_def.get("entry_types", [])]
        name_globs = [str(x) for x in root_def.get("name_globs", [])]
        description = str(root_def.get("description", "")).strip()

        if not root_path:
            continue

        root_abs = (repo_root / root_path).resolve()
        if require_subpath and not is_subpath(root_abs, repo_root):
            raise SystemExit(f"root escapes repo scope: {root_path}")

        entries = root_entries(
            repo_root=repo_root,
            root_path=root_path,
            entry_types=entry_types,
            name_globs=name_globs,
            now=now,
        )

        root_payload: dict[str, Any] = {
            "root_path": root_path,
            "root_exists": root_abs.exists() and root_abs.is_dir(),
            "description": description,
            "entries": [],
            "counts": {
                "total": 0,
                "deleted": 0,
                "would_delete": 0,
                "kept": 0,
                "errors": 0,
            },
        }

        latest_protected: set[str] = {entry.rel_path for entry in entries[: max(0, keep_latest_per_root)]}

        for entry in entries:
            reasons: list[str] = []
            if entry.rel_path in latest_protected:
                reasons.append("protected_keep_latest")
            if all_protect_globs and matches_any_glob(entry.name, all_protect_globs):
                reasons.append("protected_name_glob")
            if marker_protected(entry.path, marker_files):
                reasons.append("protected_marker")
            if entry.rel_path in pinned_paths or entry.name in pinned_paths:
                reasons.append("protected_pin_registry")
            if skip_tracked and tracked_protected(entry.rel_path, entry.kind, tracked_paths):
                reasons.append("protected_tracked_path")

            eligible = entry.age_hours >= ttl_hours and not reasons
            action = "kept"
            delete_error = None

            if eligible and apply_mode:
                delete_error = delete_entry(entry.path, entry.kind)
                if delete_error is None:
                    action = "deleted"
                    total_deleted += 1
                    root_payload["counts"]["deleted"] += 1
                else:
                    action = "error"
                    root_payload["counts"]["errors"] += 1
                    total_errors += 1
            elif eligible and not apply_mode:
                action = "would_delete"
                total_would_delete += 1
                root_payload["counts"]["would_delete"] += 1
            else:
                total_kept += 1
                root_payload["counts"]["kept"] += 1

            root_payload["entries"].append(
                {
                    "path": entry.rel_path,
                    "name": entry.name,
                    "kind": entry.kind,
                    "modified_at_utc": entry.modified_at,
                    "age_hours": entry.age_hours,
                    "eligible": eligible,
                    "action": action,
                    "protection_reasons": reasons,
                    "error": delete_error,
                }
            )
            root_payload["counts"]["total"] += 1

        root_results.append(root_payload)

    report_payload: dict[str, Any] = {
        "schema_version": "bundle_ttl_janitor_report.v1",
        "generated_at_utc": utc_iso(now),
        "mode": "apply" if apply_mode else "dry_run",
        "contract_path": normalize_rel(str(contract_path.relative_to(repo_root))),
        "ttl_hours": ttl_hours,
        "selected_roots": [normalize_rel(str(item.get("path", ""))) for item in roots],
        "keep_latest_per_root": keep_latest_per_root,
        "protect_name_globs": all_protect_globs,
        "pinned_paths_loaded": sorted(pinned_paths),
        "safety": {
            "skip_tracked_git_paths": skip_tracked,
            "require_scope_subpath": require_subpath,
        },
        "summary": {
            "roots": len(root_results),
            "deleted": total_deleted,
            "would_delete": total_would_delete,
            "kept": total_kept,
            "errors": total_errors,
        },
        "roots": root_results,
    }

    stamp = utc_stamp(now)
    report_json = report_dir / f"ttl_bundle_janitor_report_{stamp}.json"
    report_md = report_dir / f"ttl_bundle_janitor_report_{stamp}.md"
    report_json.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# TTL Bundle Janitor Report",
        "",
        f"- generated_at_utc: `{report_payload['generated_at_utc']}`",
        f"- mode: `{report_payload['mode']}`",
        f"- contract_path: `{report_payload['contract_path']}`",
        f"- ttl_hours: `{ttl_hours}`",
        "",
        "## Summary",
        f"- roots: `{report_payload['summary']['roots']}`",
        f"- deleted: `{report_payload['summary']['deleted']}`",
        f"- would_delete: `{report_payload['summary']['would_delete']}`",
        f"- kept: `{report_payload['summary']['kept']}`",
        f"- errors: `{report_payload['summary']['errors']}`",
        "",
    ]

    for root in root_results:
        lines.extend(
            [
                f"## Root `{root['root_path']}`",
                f"- root_exists: `{root['root_exists']}`",
                f"- total: `{root['counts']['total']}`",
                f"- deleted: `{root['counts']['deleted']}`",
                f"- would_delete: `{root['counts']['would_delete']}`",
                f"- kept: `{root['counts']['kept']}`",
                f"- errors: `{root['counts']['errors']}`",
                "",
            ]
        )
        for entry in root["entries"]:
            reasons = ", ".join(entry["protection_reasons"]) if entry["protection_reasons"] else "none"
            lines.append(
                f"- `{entry['path']}` | action=`{entry['action']}` | age_hours=`{entry['age_hours']}` | protected=`{reasons}`"
            )
        lines.append("")

    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "mode": report_payload["mode"],
                "report_json": normalize_rel(str(report_json.relative_to(repo_root))),
                "report_md": normalize_rel(str(report_md.relative_to(repo_root))),
                "summary": report_payload["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
