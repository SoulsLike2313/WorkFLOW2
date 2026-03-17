#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOCAL_REPO_NAME = "CVVCODEX"
PUBLIC_SAFE_MIRROR_REPO = "WorkFLOW2"
DEFAULT_OUTPUT_DIR = "runtime/chatgpt_bundle_exports"
WORKSPACE_MANIFEST_PATH = Path("workspace_config/workspace_manifest.json")
SAFE_MIRROR_MANIFEST_PATH = Path("workspace_config/SAFE_MIRROR_MANIFEST.json")
SAFE_MIRROR_REPORT_PATH = Path("docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md")
AUDIT_RUNTIME_ALLOWLIST_PATH = Path("workspace_config/chatgpt_audit_runtime_allowlist.json")

MANDATORY_CONTEXT_FILES = [
    "README.md",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    "docs/INSTRUCTION_INDEX.md",
    "workspace_config/GITHUB_SYNC_POLICY.md",
    "workspace_config/AGENT_EXECUTION_POLICY.md",
    "workspace_config/MACHINE_REPO_READING_RULES.md",
    "workspace_config/workspace_manifest.json",
    "workspace_config/codex_manifest.json",
    "workspace_config/SAFE_MIRROR_MANIFEST.json",
    "docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md",
]

CONTEXT_MODE_FILES = [
    *MANDATORY_CONTEXT_FILES,
    "docs/repo_publication_policy.md",
    "docs/CURRENT_PLATFORM_STATE.md",
    "docs/NEXT_CANONICAL_STEP.md",
]

DISALLOWED_PATH_PATTERNS = [
    re.compile(r"(^|/)\.env(\.|$)", re.IGNORECASE),
    re.compile(r"\.(pem|key|p12|pfx)$", re.IGNORECASE),
    re.compile(r"(^|/)(credentials|secrets?)(\.|/|$)", re.IGNORECASE),
    re.compile(r"(^|/)(id_rsa|id_ed25519)$", re.IGNORECASE),
    re.compile(r"(^|/)setup_reports(/|$)", re.IGNORECASE),
    re.compile(r"(^|/)tools/public_mirror(/|$)", re.IGNORECASE),
    re.compile(r"(^|/)(logs?|tmp|temp|cache)(/|$)", re.IGNORECASE),
    re.compile(r"(^|/)(router|tunnel|wan|lan|wan_lan|network_trace|network_traces|network_diagnostics?)(/|$)", re.IGNORECASE),
    re.compile(r"\.(etl|pcap|dmp|bak|orig)$", re.IGNORECASE),
]

RUNTIME_PATH_PATTERN = re.compile(r"(^|/)runtime(/|$)", re.IGNORECASE)

DEFAULT_AUDIT_RUNTIME_ALLOWLIST = [
    "runtime/repo_control_center/repo_control_status.json",
    "runtime/repo_control_center/repo_control_report.md",
    "runtime/repo_control_center/evolution_status.json",
    "runtime/repo_control_center/evolution_report.md",
]

SECRET_CONTENT_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"https?://[^\s:@/]+:[^\s@/]+@"),
]

AUDIT_RUNTIME_CONTENT_BLOCK_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|token|secret|credentials?)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"),
    re.compile(r"[A-Za-z]:\\Users\\"),
    re.compile(r"/Users/"),
]

TEXT_EXTENSIONS = {
    ".py",
    ".ps1",
    ".cmd",
    ".bat",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".ini",
    ".cfg",
    ".xml",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".css",
    ".html",
    ".csv",
}


@dataclass(frozen=True)
class GitState:
    branch: str
    tracking_branch: str
    head_sha: str
    ahead: int
    behind: int
    worktree_clean: bool
    sync_verdict: str
    status_short: str


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


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_rel(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.strip("/")


def load_audit_runtime_allowlist(repo_root: Path) -> set[str]:
    path = repo_root / AUDIT_RUNTIME_ALLOWLIST_PATH
    if not path.exists():
        return {normalize_rel(item) for item in DEFAULT_AUDIT_RUNTIME_ALLOWLIST}
    payload = load_json(path)
    values = payload.get("allowed_runtime_paths", [])
    if not isinstance(values, list):
        return {normalize_rel(item) for item in DEFAULT_AUDIT_RUNTIME_ALLOWLIST}
    return {normalize_rel(str(item)) for item in values if str(item).strip()}


def path_disallow_reason(rel_path: str, *, runtime_allowlist: set[str]) -> str | None:
    target = normalize_rel(rel_path)
    if RUNTIME_PATH_PATTERN.search(target):
        if target in runtime_allowlist:
            return None
        return "runtime_path_not_in_audit_allowlist"
    for pattern in DISALLOWED_PATH_PATTERNS:
        if pattern.search(target):
            return "requested_path_disallowed_by_policy"
    return None


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(131072)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_git_state(repo_root: Path) -> GitState:
    branch = run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    tracking = run_git(repo_root, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], allow_fail=True) or "no-tracking"
    head_sha = run_git(repo_root, ["rev-parse", "HEAD"])
    status_short = run_git(repo_root, ["status", "-sb"], allow_fail=True)
    worktree_clean = not bool(run_git(repo_root, ["status", "--porcelain"], allow_fail=True))

    ahead = 0
    behind = 0
    if tracking != "no-tracking":
        counts = run_git(repo_root, ["rev-list", "--left-right", "--count", f"HEAD...{tracking}"], allow_fail=True)
        if counts:
            left, right = counts.split()
            ahead = int(left)
            behind = int(right)

    sync_verdict = "PASS"
    if tracking == "no-tracking":
        sync_verdict = "NOT_SAFE_TO_SHARE"
    elif behind > 0 or not worktree_clean:
        sync_verdict = "NOT_SAFE_TO_SHARE"
    elif ahead > 0:
        sync_verdict = "PASS_WITH_WARNINGS"

    return GitState(
        branch=branch,
        tracking_branch=tracking,
        head_sha=head_sha,
        ahead=ahead,
        behind=behind,
        worktree_clean=worktree_clean,
        sync_verdict=sync_verdict,
        status_short=status_short,
    )


def tracked_files(repo_root: Path) -> set[str]:
    output = run_git(repo_root, ["ls-files"])
    items = [normalize_rel(line) for line in output.splitlines() if line.strip()]
    return set(items)


def parse_request_file(path: Path) -> list[str]:
    requested: list[str] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()
        if line:
            requested.append(line)
    return requested


def resolve_project_paths(repo_root: Path, slug: str) -> list[str]:
    workspace = load_json(repo_root / WORKSPACE_MANIFEST_PATH)
    registry = list(workspace.get("project_registry", []))
    for item in registry:
        if str(item.get("slug", "")).strip() == slug:
            root = str(item.get("root_path", "")).strip()
            manifest = str(item.get("manifest_path", "")).strip()
            readme = str(item.get("readme_path", "")).strip()
            paths = [root]
            if manifest:
                paths.append(manifest)
            if readme:
                paths.append(readme)
            return paths
    raise RuntimeError(f"Unknown project slug: {slug}")


def mode_requests(repo_root: Path, args: argparse.Namespace) -> tuple[list[str], str, set[str]]:
    mode = args.mode
    if mode == "context":
        return list(CONTEXT_MODE_FILES), "built-in:context", set()
    if mode == "files":
        return list(args.include), "cli:files", set()
    if mode == "paths":
        return list(args.include), "cli:paths", set()
    if mode == "project":
        return resolve_project_paths(repo_root, args.slug), f"project:{args.slug}", set()
    if mode == "request":
        request_file = Path(args.request_file).expanduser()
        if not request_file.is_absolute():
            request_file = (repo_root / request_file).resolve()
        if not request_file.exists():
            raise RuntimeError(f"Request file not found: {request_file}")
        return parse_request_file(request_file), f"request-file:{request_file}", set()
    if mode == "audit-runtime":
        runtime_allowlist = load_audit_runtime_allowlist(repo_root)
        requested: list[str] = []
        if args.include_rcc_runtime:
            requested.extend(sorted(runtime_allowlist))
        if args.include:
            requested.extend(list(args.include))
        if not requested:
            raise RuntimeError("audit-runtime mode requires --include-rcc-runtime or --include paths.")
        return requested, "audit-runtime", runtime_allowlist
    raise RuntimeError(f"Unsupported mode: {mode}")


def expand_and_filter(
    repo_root: Path,
    tracked: set[str],
    requested: list[str],
    runtime_allowlist: set[str],
) -> tuple[list[str], list[dict[str, str]], list[dict[str, str]]]:
    included: set[str] = set()
    skipped: list[dict[str, str]] = []
    blocked: list[dict[str, str]] = []

    requested_with_context = list(dict.fromkeys([*requested, *MANDATORY_CONTEXT_FILES]))

    for raw in requested_with_context:
        rel = normalize_rel(raw)
        if not rel:
            continue
        disallow_reason = path_disallow_reason(rel, runtime_allowlist=runtime_allowlist)
        if disallow_reason:
            blocked.append({"path": rel, "reason": disallow_reason})
            continue

        if rel in tracked:
            included.add(rel)
            continue

        prefix = rel.rstrip("/") + "/"
        dir_matches = sorted(item for item in tracked if item.startswith(prefix))
        if dir_matches:
            included.update(dir_matches)
            continue

        full = (repo_root / rel).resolve()
        if full.exists():
            if rel in runtime_allowlist and full.is_file():
                included.add(rel)
                continue
            if full.is_dir():
                allowlisted_dir_matches = sorted(
                    item
                    for item in runtime_allowlist
                    if item.startswith(prefix) and (repo_root / item).is_file()
                )
                if allowlisted_dir_matches:
                    included.update(allowlisted_dir_matches)
                    continue
            skipped.append({"path": rel, "reason": "exists_but_not_tracked"})
        else:
            skipped.append({"path": rel, "reason": "not_found"})

    filtered: list[str] = []
    for rel in sorted(included):
        disallow_reason = path_disallow_reason(rel, runtime_allowlist=runtime_allowlist)
        if disallow_reason:
            blocked.append({"path": rel, "reason": disallow_reason})
            continue
        filtered.append(rel)

    final_included: list[str] = []
    for rel in filtered:
        path = repo_root / rel
        suffix = path.suffix.lower()
        if suffix and suffix not in TEXT_EXTENSIONS:
            final_included.append(rel)
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            final_included.append(rel)
            continue
        secret_hit = False
        for pattern in SECRET_CONTENT_PATTERNS:
            if pattern.search(text):
                blocked.append({"path": rel, "reason": f"content_pattern_block:{pattern.pattern}"})
                secret_hit = True
                break
        if not secret_hit and rel in runtime_allowlist:
            for pattern in AUDIT_RUNTIME_CONTENT_BLOCK_PATTERNS:
                if pattern.search(text):
                    blocked.append({"path": rel, "reason": f"audit_runtime_content_block:{pattern.pattern}"})
                    secret_hit = True
                    break
        if not secret_hit:
            final_included.append(rel)

    return sorted(set(final_included)), skipped, blocked


def write_bundle(
    repo_root: Path,
    output_root: Path,
    bundle_name: str,
    included: list[str],
    manifest: dict[str, Any],
    report_md: str,
) -> Path:
    bundle_root = output_root / bundle_name
    exported_root = bundle_root / "exported"
    exported_root.mkdir(parents=True, exist_ok=True)

    for rel in included:
        src = repo_root / rel
        dst = exported_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    (bundle_root / "CHATGPT_BUNDLE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (bundle_root / "EXPORT_REPORT.md").write_text(report_md, encoding="utf-8")

    zip_path = output_root / f"{bundle_name}.zip"
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(bundle_root.rglob("*")):
            if file_path.is_dir():
                continue
            archive.write(file_path, arcname=str(Path(bundle_name) / file_path.relative_to(bundle_root)))
    return zip_path


def build_report(
    *,
    mode: str,
    request_source: str,
    requested: list[str],
    included: list[str],
    skipped: list[dict[str, str]],
    blocked: list[dict[str, str]],
    git_state: GitState,
    active_project: str,
    verdict: str,
) -> str:
    safe_yes_no = "YES" if verdict == "SAFE TO SHARE" else "NO"
    lines = [
        "# ChatGPT Bundle Export Report",
        "",
        f"- generated_at: `{utc_now_iso()}`",
        f"- export_mode: `{mode}`",
        f"- request_source: `{request_source}`",
        f"- active_project: `{active_project}`",
        "",
        "## Git / Sync Summary",
        f"- branch: `{git_state.branch}`",
        f"- tracking_branch: `{git_state.tracking_branch}`",
        f"- head_sha: `{git_state.head_sha}`",
        f"- ahead/behind: `{git_state.ahead}/{git_state.behind}`",
        f"- worktree_clean: `{git_state.worktree_clean}`",
        f"- sync_verdict: `{git_state.sync_verdict}`",
        "",
        "## Requested Paths",
    ]
    lines.extend([f"- `{item}`" for item in requested] or ["- none"])
    lines += [
        "",
        "## Included Files",
        f"- count: `{len(included)}`",
    ]
    lines.extend([f"- `{item}`" for item in included] or ["- none"])
    lines += [
        "",
        "## Skipped Files",
        f"- count: `{len(skipped)}`",
    ]
    lines.extend([f"- `{item['path']}` ({item['reason']})" for item in skipped] or ["- none"])
    lines += [
        "",
        "## Blocked Files",
        f"- count: `{len(blocked)}`",
    ]
    lines.extend([f"- `{item['path']}` ({item['reason']})" for item in blocked] or ["- none"])
    lines += [
        "",
        "## Final Verdict",
        f"- safe_share_verdict: `{verdict}`",
        f"- SAFE TO SHARE WITH CHATGPT: `{safe_yes_no}`",
    ]
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build targeted safe ChatGPT bundle from local repository state.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory for bundle folders and zip files.")
    sub = parser.add_subparsers(dest="mode", required=True)

    sub.add_parser("context", help="Export policy-approved machine-readable context bundle.")

    files_mode = sub.add_parser("files", help="Export only explicitly listed files plus mandatory context files.")
    files_mode.add_argument("--include", nargs="+", required=True, help="Repo-relative file paths.")

    paths_mode = sub.add_parser("paths", help="Export listed files/directories plus mandatory context files.")
    paths_mode.add_argument("--include", nargs="+", required=True, help="Repo-relative file or directory paths.")

    project_mode = sub.add_parser("project", help="Export policy-approved bundle for a single project slug.")
    project_mode.add_argument("--slug", required=True, help="Project slug from workspace project_registry.")

    request_mode = sub.add_parser("request", help="Export from request file containing paths listed by ChatGPT/user.")
    request_mode.add_argument("--request-file", required=True, help="Path to request file.")

    audit_runtime = sub.add_parser(
        "audit-runtime",
        help="Export audit-safe runtime reports only via explicit allowlist (no global runtime policy weakening).",
    )
    audit_runtime.add_argument(
        "--include-rcc-runtime",
        action="store_true",
        help="Include policy-approved runtime/repo_control_center reports from allowlist.",
    )
    audit_runtime.add_argument(
        "--include",
        nargs="*",
        default=[],
        help="Optional extra repo-relative paths; runtime paths still require allowlist.",
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()
    if not (repo_root / WORKSPACE_MANIFEST_PATH).exists():
        raise SystemExit(f"workspace manifest not found at expected repo root: {repo_root}")

    workspace_manifest = load_json(repo_root / WORKSPACE_MANIFEST_PATH)
    active_project = str(workspace_manifest.get("active_project", "unknown"))
    git_state = build_git_state(repo_root)
    tracked = tracked_files(repo_root)

    requested, request_source, runtime_allowlist = mode_requests(repo_root, args)
    included, skipped, blocked = expand_and_filter(
        repo_root,
        tracked,
        requested,
        runtime_allowlist=runtime_allowlist,
    )

    included_hashes = {path: file_hash(repo_root / path) for path in included}

    if blocked:
        safe_share_verdict = "RESTRICTED/BLOCKED"
    elif git_state.sync_verdict == "NOT_SAFE_TO_SHARE":
        safe_share_verdict = "NOT SAFE TO SHARE"
    else:
        safe_share_verdict = "SAFE TO SHARE"

    output_root = Path(args.output_dir).expanduser()
    if not output_root.is_absolute():
        output_root = (repo_root / output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_name = f"chatgpt_bundle_{args.mode}_{ts}"

    manifest_payload: dict[str, Any] = {
        "schema_version": "1.0.0",
        "repo_name": PUBLIC_SAFE_MIRROR_REPO,
        "local_repo_name": LOCAL_REPO_NAME,
        "public_safe_mirror_repo": PUBLIC_SAFE_MIRROR_REPO,
        "public_safe_mirror_remote": "safe_mirror",
        "local_root": str(repo_root),
        "current_branch": git_state.branch,
        "tracking_branch": git_state.tracking_branch,
        "head_sha": git_state.head_sha,
        "ahead": git_state.ahead,
        "behind": git_state.behind,
        "worktree_clean": git_state.worktree_clean,
        "sync_verdict": git_state.sync_verdict,
        "export_mode": args.mode,
        "request_source": request_source,
        "requested_paths": [normalize_rel(item) for item in requested],
        "required_safe_reading_files": MANDATORY_CONTEXT_FILES,
        "included_files": included,
        "skipped_files": skipped,
        "blocked_files": blocked,
        "included_file_hashes": included_hashes,
        "generated_at": utc_now_iso(),
        "active_project": active_project,
        "safe_share_verdict": safe_share_verdict,
        "safe_state_basis": {
            "safe_mirror_manifest_path": str(SAFE_MIRROR_MANIFEST_PATH),
            "safe_mirror_report_path": str(SAFE_MIRROR_REPORT_PATH),
        },
        "audit_runtime_allowlist_path": str(AUDIT_RUNTIME_ALLOWLIST_PATH),
        "audit_runtime_allowlist_enabled": bool(runtime_allowlist),
        "audit_runtime_allowlist": sorted(runtime_allowlist),
    }

    report_md = build_report(
        mode=args.mode,
        request_source=request_source,
        requested=[normalize_rel(item) for item in requested],
        included=included,
        skipped=skipped,
        blocked=blocked,
        git_state=git_state,
        active_project=active_project,
        verdict=safe_share_verdict,
    )

    zip_path = write_bundle(
        repo_root=repo_root,
        output_root=output_root,
        bundle_name=bundle_name,
        included=included,
        manifest=manifest_payload,
        report_md=report_md,
    )

    summary = {
        "bundle_name": bundle_name,
        "bundle_zip_path": str(zip_path),
        "safe_share_verdict": safe_share_verdict,
        "included_files_count": len(included),
        "skipped_files_count": len(skipped),
        "blocked_files_count": len(blocked),
        "sync_verdict": git_state.sync_verdict,
        "head_sha": git_state.head_sha,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if safe_share_verdict == "SAFE TO SHARE":
        return 0
    if safe_share_verdict == "RESTRICTED/BLOCKED":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
