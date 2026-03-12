#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_EXPECTED_PATHS = [
    "workspace_config/GITHUB_SYNC_POLICY.md",
    "workspace_config/COMPLETION_GATE_RULES.md",
    "workspace_config/workspace_manifest.json",
    "workspace_config/codex_manifest.json",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat()


def run_git(args: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def load_expected_paths(file_path: Path | None, inline_paths: list[str]) -> list[str]:
    expected = list(DEFAULT_EXPECTED_PATHS)
    expected.extend([item.strip() for item in inline_paths if item.strip()])
    if file_path is not None and file_path.exists():
        for line in file_path.read_text(encoding="utf-8-sig").splitlines():
            path = line.strip()
            if not path or path.startswith("#"):
                continue
            expected.append(path)
    unique: list[str] = []
    seen = set()
    for path in expected:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Check branch/head sync and repo-visible completion paths.")
    parser.add_argument("--remote", default="origin", help="Git remote name.")
    parser.add_argument("--branch", default="main", help="Target branch.")
    parser.add_argument(
        "--expected-path",
        action="append",
        default=[],
        help="Expected repo-relative path that must exist in remote branch tree.",
    )
    parser.add_argument(
        "--expected-paths-file",
        default="",
        help="Optional file with expected repo-relative paths, one per line.",
    )
    parser.add_argument(
        "--completion-summary",
        default="",
        help="Repo-relative summary path that must be repo-visible.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    started = utc_now()
    run_id = f"repo-sync-{started.strftime('%Y%m%dT%H%M%SZ')}"
    remote_ref = f"{args.remote}/{args.branch}"

    current_branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    head_commit = run_git(["rev-parse", "HEAD"], cwd=repo_root)
    remote_commit = run_git(["rev-parse", remote_ref], cwd=repo_root)
    ls_remote = run_git(["ls-remote", args.remote, f"refs/heads/{args.branch}"], cwd=repo_root)
    remote_head_commit = ls_remote.split()[0] if ls_remote else ""
    status_short = run_git(["status", "-sb"], cwd=repo_root)
    porcelain = run_git(["status", "--porcelain"], cwd=repo_root)
    dirty = bool(porcelain.strip())
    tree_output = run_git(["ls-tree", "--name-only", "-r", remote_ref], cwd=repo_root)
    remote_tree_paths = set(item.strip() for item in tree_output.splitlines() if item.strip())

    expected_file = Path(args.expected_paths_file).resolve() if args.expected_paths_file else None
    expected_paths = load_expected_paths(expected_file if expected_file and expected_file.exists() else None, args.expected_path)
    if args.completion_summary.strip():
        expected_paths.append(args.completion_summary.strip())
    expected_paths = load_expected_paths(None, expected_paths)

    path_checks = []
    for path in expected_paths:
        exists = path in remote_tree_paths
        path_checks.append({"path": path, "exists_in_remote_tree": exists})

    sync_checks: dict[str, Any] = {
        "branch_matches_target": current_branch == args.branch,
        "head_equals_remote_ref": head_commit == remote_commit,
        "remote_ref_equals_ls_remote": remote_commit == remote_head_commit,
        "worktree_clean": not dirty,
    }
    sync_checks["expected_paths_all_exist"] = all(item["exists_in_remote_tree"] for item in path_checks)

    status = "PASS" if all(sync_checks.values()) else "FAIL"
    finished = utc_now()

    payload = {
        "run_id": run_id,
        "status": status,
        "started_at": iso(started),
        "finished_at": iso(finished),
        "duration_seconds": round((finished - started).total_seconds(), 3),
        "remote": args.remote,
        "branch": args.branch,
        "remote_ref": remote_ref,
        "current_branch": current_branch,
        "head_commit": head_commit,
        "remote_commit": remote_commit,
        "remote_head_commit": remote_head_commit,
        "status_short": status_short,
        "sync_checks": sync_checks,
        "path_checks": path_checks,
    }

    output_path = repo_root / "runtime" / "repo_sync_checks" / f"{run_id}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
