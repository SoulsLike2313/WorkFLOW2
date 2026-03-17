#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SAFE_MIRROR_MANIFEST_PATH = Path("workspace_config/SAFE_MIRROR_MANIFEST.json")
SAFE_MIRROR_REPORT_PATH = Path("docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md")
EVIDENCE_CONTRACT_VERSION = "2.0.0"
EVIDENCE_FILES = [
    "workspace_config/SAFE_MIRROR_MANIFEST.json",
    "docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md",
]

REQUIRED_FILES = [
    "README.md",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    "docs/INSTRUCTION_INDEX.md",
    "workspace_config/GITHUB_SYNC_POLICY.md",
    "workspace_config/AGENT_EXECUTION_POLICY.md",
    "workspace_config/MACHINE_REPO_READING_RULES.md",
    "workspace_config/workspace_manifest.json",
    "workspace_config/codex_manifest.json",
]

ALLOWED_ROOTS = {
    "README.md",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    ".gitignore",
    "docs/",
    "integration/",
    "tasks/",
    "workspace_config/",
    "scripts/",
    "projects/",
    "shared_systems/",
}

EXCLUDED_CATEGORIES = [
    ".env files",
    "credentials and private keys",
    "runtime dumps and logs",
    "temporary/cache artifacts",
    "network diagnostics and publication leftovers",
    "legacy publication/tunnel artifacts",
    "local machine-only backups",
]

DISALLOWED_PATH_PATTERNS = [
    re.compile(r"(^|/)\.env(\.|$)", re.IGNORECASE),
    re.compile(r"(^|/)(id_rsa|id_ed25519)$", re.IGNORECASE),
    re.compile(r"\.(pem|key|p12|pfx)$", re.IGNORECASE),
    re.compile(r"(^|/)(credentials|secrets?)", re.IGNORECASE),
    re.compile(r"(^|/)runtime/", re.IGNORECASE),
    re.compile(r"(^|/)setup_reports/", re.IGNORECASE),
    re.compile(r"(^|/)tools/public_mirror/", re.IGNORECASE),
    re.compile(r"(^|/)(tmp|temp|cache|logs?)/", re.IGNORECASE),
    re.compile(r"\.(etl|pcap|dmp|bak|orig)$", re.IGNORECASE),
]

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"https?://[^\s:@/]+:[^\s@/]+@"),
]


@dataclass(frozen=True)
class GitState:
    branch: str
    head_sha: str
    tracking_branch: str
    ahead: int
    behind: int
    worktree_clean: bool
    status_short: str


def git_commit_exists(repo_root: Path, sha: str) -> bool:
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def run_git(repo_root: Path, args: list[str], *, allow_fail: bool = False) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        if allow_fail:
            return ""
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(131072)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def is_allowed(rel_path: str) -> bool:
    for root in ALLOWED_ROOTS:
        if root.endswith("/"):
            if rel_path.startswith(root):
                return True
        elif rel_path == root:
            return True
    return False


def collect_git_state(repo_root: Path) -> GitState:
    branch = run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    head_sha = run_git(repo_root, ["rev-parse", "HEAD"])
    tracking = run_git(repo_root, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], allow_fail=True) or "no-tracking"
    status_short = run_git(repo_root, ["status", "-sb"], allow_fail=True)
    worktree_clean = not bool(run_git(repo_root, ["status", "--porcelain"], allow_fail=True).strip())

    ahead = 0
    behind = 0
    if tracking != "no-tracking":
        counts = run_git(repo_root, ["rev-list", "--left-right", "--count", f"HEAD...{tracking}"], allow_fail=True)
        if counts:
            left, right = counts.split()
            ahead, behind = int(left), int(right)
    return GitState(
        branch=branch,
        head_sha=head_sha,
        tracking_branch=tracking,
        ahead=ahead,
        behind=behind,
        worktree_clean=worktree_clean,
        status_short=status_short,
    )


def build_manifest(
    repo_root: Path,
    *,
    basis_head_sha: str | None = None,
    evidence_mode: str = "tracked_evidence_refresh_commit",
    evidence_commit_note: str = "",
) -> dict[str, Any]:
    tracked_files = run_git(repo_root, ["ls-files"]).splitlines()
    tracked_files = [item.strip() for item in tracked_files if item.strip()]

    disallowed_tracked: list[str] = []
    not_allowlisted: list[str] = []
    secret_hits: list[dict[str, str]] = []

    for rel in tracked_files:
        rel_norm = rel.replace("\\", "/")
        if not is_allowed(rel_norm):
            not_allowlisted.append(rel_norm)
        for pattern in DISALLOWED_PATH_PATTERNS:
            if pattern.search(rel_norm):
                disallowed_tracked.append(rel_norm)
                break

        path = repo_root / rel_norm
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".wav", ".mp3", ".mp4", ".zip", ".exe", ".dll", ".bin", ".pdf"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append({"path": rel_norm, "pattern": pattern.pattern})
                break

    missing_required = [path for path in REQUIRED_FILES if not (repo_root / path).exists()]
    git_state = collect_git_state(repo_root)
    basis_sha = basis_head_sha or git_state.head_sha

    workspace_manifest = json.loads((repo_root / "workspace_config/workspace_manifest.json").read_text(encoding="utf-8"))
    active_project = workspace_manifest.get("active_project", "unknown")
    entrypoints = workspace_manifest.get("entrypoints", {})

    key_files_for_hash = [
        "README.md",
        "REPO_MAP.md",
        "MACHINE_CONTEXT.md",
        "workspace_config/workspace_manifest.json",
        "workspace_config/codex_manifest.json",
    ]
    key_hashes: dict[str, str] = {}
    for rel in key_files_for_hash:
        path = repo_root / rel
        if path.exists():
            key_hashes[rel] = file_hash(path)

    publication_safe_verdict = "PASS"
    failure_reasons: list[str] = []
    if missing_required:
        publication_safe_verdict = "FAIL"
        failure_reasons.append("missing required safe-reading files")
    if disallowed_tracked:
        publication_safe_verdict = "FAIL"
        failure_reasons.append("disallowed tracked paths detected")
    if secret_hits:
        publication_safe_verdict = "FAIL"
        failure_reasons.append("secret pattern hits detected")
    if not_allowlisted:
        publication_safe_verdict = "FAIL"
        failure_reasons.append("tracked files outside allowlist roots")
    if not git_commit_exists(repo_root, basis_sha):
        publication_safe_verdict = "FAIL"
        failure_reasons.append("basis_head_sha does not resolve to valid commit")
    if evidence_mode not in {"runtime_current_head", "tracked_evidence_refresh_commit"}:
        publication_safe_verdict = "FAIL"
        failure_reasons.append("unsupported evidence_mode")

    if git_state.tracking_branch == "no-tracking":
        sync_verdict = "FAIL"
        sync_state = "no_tracking_branch"
    elif git_state.behind > 0:
        sync_verdict = "FAIL"
        sync_state = "behind_remote"
    elif git_state.ahead > 0:
        sync_verdict = "PASS"
        sync_state = "ahead_only_ready_to_push"
    else:
        sync_verdict = "PASS"
        sync_state = "in_sync"

    now = datetime.now(timezone.utc).isoformat()
    manifest: dict[str, Any] = {
        "schema_version": "1.0.0",
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "evidence_generated_at": now,
        "evidence_mode": evidence_mode,
        "basis_head_sha": basis_sha,
        "evidence_commit_note": evidence_commit_note,
        "evidence_files": EVIDENCE_FILES,
        "repo_name": "WorkFLOW2",
        "local_repo_name": "CVVCODEX",
        "public_safe_mirror_remote": "safe_mirror",
        "public_safe_mirror_url": "https://github.com/SoulsLike2313/WorkFLOW2.git",
        "generated_at": now,
        "export_tool_version": "safe-mirror-builder/1.0.0",
        "local_source_root": str(repo_root),
        "privacy_mode": "publication_safe_local_prepare",
        "current_branch": git_state.branch,
        "tracking_branch": git_state.tracking_branch,
        "head_sha": basis_sha,
        "head_sha_legacy_field": basis_sha,
        "head_sha_runtime_at_generation": git_state.head_sha,
        "ahead": git_state.ahead,
        "behind": git_state.behind,
        "worktree_clean": git_state.worktree_clean,
        "git": {
            "current_branch": git_state.branch,
            "head_sha": basis_sha,
            "basis_head_sha": basis_sha,
            "runtime_head_sha_at_generation": git_state.head_sha,
            "tracking_branch": git_state.tracking_branch,
            "ahead": git_state.ahead,
            "behind": git_state.behind,
            "worktree_clean": git_state.worktree_clean,
            "status_short": git_state.status_short,
            "sync_state": sync_state,
        },
        "active_project": active_project,
        "safe_reading_entrypoints": {
            "workspace_validate": entrypoints.get("workspace_validate", ""),
            "repo_sync_check": entrypoints.get("repo_sync_check", ""),
            "tester_agent_project_intake": entrypoints.get("tester_agent_project_intake", ""),
        },
        "included_directories": sorted([item.rstrip("/") for item in ALLOWED_ROOTS if item.endswith("/")]),
        "included_files": sorted([item for item in ALLOWED_ROOTS if not item.endswith("/")]),
        "included_safe_state_files": sorted(tracked_files),
        "tracked_files_count": len(tracked_files),
        "excluded_categories": EXCLUDED_CATEGORIES,
        "required_files": REQUIRED_FILES,
        "required_safe_reading_files": REQUIRED_FILES,
        "missing_required_files": missing_required,
        "disallowed_tracked_paths": sorted(set(disallowed_tracked)),
        "allowlist_violations": sorted(set(not_allowlisted)),
        "secret_hits": secret_hits,
        "key_file_hashes": key_hashes,
        "sync_verdict": sync_verdict,
        "publication_safe_verdict": publication_safe_verdict,
        "failure_reasons": failure_reasons,
        "notes_for_chatgpt": [
            "Local working source root is E:\\CVVCODEX.",
            "GitHub WorkFLOW2 (safe_mirror) is synchronized only after local publication-safe validation.",
            "Use required safe-reading files and workspace manifests as source of truth.",
        ],
    }
    return manifest


def write_report(repo_root: Path, manifest: dict[str, Any]) -> Path:
    output = repo_root / SAFE_MIRROR_REPORT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)

    git_state = manifest["git"]
    lines = [
        "# SAFE MIRROR Build Report",
        "",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- local_source_root: `{manifest['local_source_root']}`",
        f"- repo_name: `{manifest['repo_name']}`",
        f"- evidence_contract_version: `{manifest['evidence_contract_version']}`",
        f"- evidence_mode: `{manifest['evidence_mode']}`",
        f"- basis_head_sha: `{manifest['basis_head_sha']}`",
        f"- evidence_generated_at: `{manifest['evidence_generated_at']}`",
        f"- evidence_commit_note: `{manifest.get('evidence_commit_note', '') or 'none'}`",
        f"- active_project: `{manifest['active_project']}`",
        f"- branch: `{git_state['current_branch']}`",
        f"- head_sha (basis): `{git_state['head_sha']}`",
        f"- tracking_branch: `{git_state['tracking_branch']}`",
        f"- ahead/behind: `{git_state['ahead']}/{git_state['behind']}`",
        f"- worktree_clean: `{git_state['worktree_clean']}`",
        f"- tracked_files_count: `{manifest['tracked_files_count']}`",
        f"- sync_verdict: `{manifest['sync_verdict']}`",
        f"- publication_safe_verdict: `{manifest['publication_safe_verdict']}`",
        "",
        "## Evidence Contract",
        "- tracked evidence artifacts describe `basis_head_sha` commit.",
        "- for `tracked_evidence_refresh_commit` mode, current `HEAD` can be an evidence refresh commit on top of basis.",
        "",
        "## Included Roots",
    ]
    lines.extend([f"- `{item}`" for item in manifest["included_directories"]])
    lines.extend([f"- `{item}`" for item in manifest["included_files"]])
    lines += [
        "",
        "## Excluded Categories",
    ]
    lines.extend([f"- {item}" for item in manifest["excluded_categories"]])
    lines += [
        "",
        "## Required File Check",
        f"- missing_required_files: `{len(manifest['missing_required_files'])}`",
    ]
    lines.extend([f"- `{item}`" for item in manifest["missing_required_files"]])
    lines += [
        "",
        "## Safety Check Findings",
        f"- disallowed_tracked_paths: `{len(manifest['disallowed_tracked_paths'])}`",
        f"- allowlist_violations: `{len(manifest['allowlist_violations'])}`",
        f"- secret_hits: `{len(manifest['secret_hits'])}`",
    ]
    if manifest["failure_reasons"]:
        lines.append("- failure_reasons:")
        lines.extend([f"  - {item}" for item in manifest["failure_reasons"]])
    else:
        lines.append("- failure_reasons: none")

    lines += [
        "",
        "## Verdict",
        f"- publication_safe_verdict: `{manifest['publication_safe_verdict']}`",
        f"- sync_verdict: `{manifest['sync_verdict']}`",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build publication-safe mirror manifest/report from local root.")
    parser.add_argument("--repo-root", default=".", help="Repository root path (default: current directory).")
    parser.add_argument(
        "--basis-head-sha",
        default="",
        help="Basis commit SHA described by tracked evidence artifacts (default: current HEAD).",
    )
    parser.add_argument(
        "--evidence-mode",
        default="tracked_evidence_refresh_commit",
        choices=["runtime_current_head", "tracked_evidence_refresh_commit"],
        help="Evidence validation mode written to SAFE_MIRROR_MANIFEST.",
    )
    parser.add_argument(
        "--evidence-commit-note",
        default="",
        help="Optional note for evidence refresh commit context.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest = build_manifest(
        repo_root,
        basis_head_sha=args.basis_head_sha or None,
        evidence_mode=args.evidence_mode,
        evidence_commit_note=args.evidence_commit_note,
    )

    manifest_path = repo_root / SAFE_MIRROR_MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path = write_report(repo_root, manifest)

    print(f"manifest: {manifest_path}")
    print(f"report: {report_path}")
    print(f"publication_safe_verdict: {manifest['publication_safe_verdict']}")
    print(f"sync_verdict: {manifest['sync_verdict']}")
    return 0 if manifest["publication_safe_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
