from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SAFE_READING_FILES = [
    "README.md",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    "workspace_config/workspace_manifest.json",
    "workspace_config/codex_manifest.json",
    "workspace_config/TASK_RULES.md",
    "workspace_config/AGENT_EXECUTION_POLICY.md",
    "workspace_config/MACHINE_REPO_READING_RULES.md",
    "docs/INSTRUCTION_INDEX.md",
]

SAFE_READING_MANIFEST_REL_PATH = "workspace_config/safe_reading_manifest.json"


@dataclass(frozen=True)
class RepoSnapshot:
    trusted: bool
    verdict: str
    subtitle: str
    repo_name: str
    repo_path: str
    branch: str
    tracking_branch: str
    checked_at: str
    short_head: str
    statuses: dict[str, dict[str, str]]
    issues: list[str]
    details_text: str
    summary_text: str


class RepoControlDiagnostics:
    def __init__(self, repo_root: Path | None = None) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[4]
        self.repo_root = repo_root

    @property
    def safe_manifest_path(self) -> Path:
        return self.repo_root / SAFE_READING_MANIFEST_REL_PATH

    def collect(self) -> RepoSnapshot:
        checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        issues: list[str] = []
        repo_issues: list[str] = []
        sync_issues: list[str] = []
        presence_issues: list[str] = []
        manifest_issues: list[str] = []

        branch = "unknown"
        tracking_branch = "no-tracking"
        head = "unknown"
        remote_head = "unknown"
        ahead = "n/a"
        behind = "n/a"
        working_changes = "n/a"
        manifest_timestamp = "missing"

        git_ok = True
        head_value = self._git(["rev-parse", "HEAD"], allow_fail=True)
        inside_repo = self._git(["rev-parse", "--is-inside-work-tree"], allow_fail=True)

        if inside_repo != "true":
            git_ok = False
            repo_issues.append("Repository integrity check failed: current path is not a git worktree")
        if not head_value:
            git_ok = False
            repo_issues.append("Repository integrity check failed: cannot resolve HEAD")
        else:
            head = head_value

        git_dir_text = self._git(["rev-parse", "--git-dir"], allow_fail=True)
        if git_dir_text:
            git_dir = (self.repo_root / git_dir_text).resolve() if not Path(git_dir_text).is_absolute() else Path(git_dir_text)
            in_progress_markers = [
                "MERGE_HEAD",
                "CHERRY_PICK_HEAD",
                "REVERT_HEAD",
                "BISECT_LOG",
                "rebase-merge",
                "rebase-apply",
            ]
            for marker in in_progress_markers:
                if (git_dir / marker).exists():
                    repo_issues.append(f"Repository operation in progress: {marker}")

        branch_value = self._git(["rev-parse", "--abbrev-ref", "HEAD"], allow_fail=True)
        if branch_value:
            branch = branch_value

        tracking_value = self._git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], allow_fail=True)
        if tracking_value:
            tracking_branch = tracking_value
        else:
            sync_issues.append("No tracking branch configured for current branch")

        fetch_ok = self._git(["fetch", "--prune"], allow_fail=True) is not None
        if not fetch_ok:
            sync_issues.append("Failed to fetch remote state, GitHub sync cannot be confirmed")

        if tracking_value:
            remote_head_value = self._git(["rev-parse", tracking_value], allow_fail=True)
            if remote_head_value:
                remote_head = remote_head_value
            else:
                sync_issues.append(f"Cannot resolve remote tracking reference: {tracking_value}")

            counts = self._git(["rev-list", "--left-right", "--count", f"HEAD...{tracking_value}"], allow_fail=True)
            if counts:
                left, right = counts.split()
                ahead = left
                behind = right
                if int(left) > 0:
                    sync_issues.append(f"Branch is ahead of {tracking_value} by {left} commit(s)")
                if int(right) > 0:
                    sync_issues.append(f"Branch is behind {tracking_value} by {right} commit(s)")
            else:
                sync_issues.append("Cannot compute ahead/behind divergence")

        porcelain = self._git(["status", "--porcelain"], allow_fail=True)
        if porcelain is None:
            sync_issues.append("Cannot read working tree status")
        else:
            change_count = len([line for line in porcelain.splitlines() if line.strip()])
            working_changes = str(change_count)
            if change_count > 0:
                sync_issues.append(f"Working tree has uncommitted changes ({change_count})")

        missing_files = [path for path in SAFE_READING_FILES if not (self.repo_root / path).exists()]
        for missing in missing_files:
            presence_issues.append(f"Safe reading file missing: {missing}")

        if not self.safe_manifest_path.exists():
            manifest_issues.append(f"Safe reading manifest missing: {SAFE_READING_MANIFEST_REL_PATH}")
        else:
            manifest_payload = self._read_json(self.safe_manifest_path)
            if manifest_payload is None:
                manifest_issues.append(f"Safe reading manifest is not valid JSON: {SAFE_READING_MANIFEST_REL_PATH}")
            else:
                manifest_timestamp = str(manifest_payload.get("generated_at", "missing"))
                items = manifest_payload.get("files", [])
                by_path = {
                    str(item.get("path", "")).replace("\\", "/"): str(item.get("sha256", ""))
                    for item in items
                    if isinstance(item, dict)
                }
                for rel_path in SAFE_READING_FILES:
                    rel_normalized = rel_path.replace("\\", "/")
                    expected_hash = by_path.get(rel_normalized)
                    file_path = self.repo_root / rel_path
                    if expected_hash is None:
                        manifest_issues.append(f"Manifest entry missing: {rel_normalized}")
                        continue
                    if not file_path.exists():
                        manifest_issues.append(f"Manifest file target missing: {rel_normalized}")
                        continue
                    current_hash = self._sha256(file_path)
                    if current_hash != expected_hash:
                        manifest_issues.append(f"Safe reading hash mismatch: {rel_normalized}")

        issues.extend(repo_issues)
        issues.extend(sync_issues)
        issues.extend(presence_issues)
        issues.extend(manifest_issues)
        issues = self._prioritize_issues(issues)

        statuses = {
            "repo_integrity": self._status_model(
                "PASS" if git_ok and not repo_issues else "FAIL",
                "Git repository is healthy" if git_ok and not repo_issues else repo_issues[0],
            ),
            "github_sync": self._status_model(
                "PASS" if not sync_issues else "FAIL",
                "Fully synced with tracking branch and clean worktree" if not sync_issues else sync_issues[0],
            ),
            "safe_files_present": self._status_model(
                "PASS" if not presence_issues else "FAIL",
                "All required safe-reading files are present" if not presence_issues else presence_issues[0],
            ),
            "safe_files_match_manifest": self._status_model(
                "PASS" if not manifest_issues else "FAIL",
                "Safe-reading file hashes match manifest" if not manifest_issues else manifest_issues[0],
            ),
        }

        trusted = all(model["status"] == "PASS" for model in statuses.values())
        verdict = "TRUSTED" if trusted else "NOT TRUSTED"
        subtitle = "Repository state is verified and ready for machine reading."
        if not trusted:
            if issues:
                subtitle = f"{issues[0]} ({len(issues)} blocker(s))"
            else:
                subtitle = "Repository is not trusted. Review blocking reasons below."

        details_lines = [
            f"repo: {self.repo_root}",
            f"branch: {branch}",
            f"tracking_branch: {tracking_branch}",
            f"current_head: {head}",
            f"remote_head: {remote_head}",
            f"ahead: {ahead}",
            f"behind: {behind}",
            f"working_changes: {working_changes}",
            f"safe_manifest_path: {SAFE_READING_MANIFEST_REL_PATH}",
            f"safe_manifest_timestamp: {manifest_timestamp}",
            f"issues_count: {len(issues)}",
        ]

        summary_lines = [
            f"VERDICT: {verdict}",
            f"Repo: {self.repo_root.name}",
            f"Path: {self.repo_root}",
            f"Branch: {branch}",
            f"Tracking: {tracking_branch}",
            f"HEAD: {head}",
            f"Remote HEAD: {remote_head}",
            f"Ahead/Behind: {ahead}/{behind}",
            f"Working changes: {working_changes}",
            f"Safe manifest: {manifest_timestamp}",
        ]
        if issues:
            summary_lines.append("Issues:")
            summary_lines.extend(f"- {issue}" for issue in issues)

        return RepoSnapshot(
            trusted=trusted,
            verdict=verdict,
            subtitle=subtitle,
            repo_name=self.repo_root.name,
            repo_path=str(self.repo_root),
            branch=branch,
            tracking_branch=tracking_branch,
            checked_at=checked_at,
            short_head=head[:10] if head != "unknown" else "unknown",
            statuses=statuses,
            issues=issues,
            details_text="\n".join(details_lines),
            summary_text="\n".join(summary_lines),
        )

    def rebuild_manifest(self) -> Path:
        files_payload: list[dict[str, Any]] = []
        missing_source_files: list[str] = []
        for rel_path in SAFE_READING_FILES:
            file_path = self.repo_root / rel_path
            if not file_path.exists():
                missing_source_files.append(rel_path)
                continue
            files_payload.append(
                {
                    "path": rel_path.replace("\\", "/"),
                    "sha256": self._sha256(file_path),
                    "size_bytes": file_path.stat().st_size,
                }
            )

        payload = {
            "schema_version": "1.0.0",
            "manifest_type": "safe_reading_manifest",
            "generated_at": datetime.now().isoformat(),
            "files": files_payload,
            "required_files": SAFE_READING_FILES,
            "missing_source_files": missing_source_files,
        }

        self.safe_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.safe_manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return self.safe_manifest_path

    def key_files(self) -> list[Path]:
        open_targets = [
            "README.md",
            "workspace_config/workspace_manifest.json",
            "workspace_config/codex_manifest.json",
            SAFE_READING_MANIFEST_REL_PATH,
            "docs/INSTRUCTION_INDEX.md",
        ]
        return [self.repo_root / rel for rel in open_targets if (self.repo_root / rel).exists()]

    def _git(self, args: list[str], *, allow_fail: bool = False) -> str | None:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            if allow_fail:
                return None
            raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
        return completed.stdout.strip()

    @staticmethod
    def _status_model(status: str, summary: str) -> dict[str, str]:
        return {"status": status, "summary": summary}

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any] | None:
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return None

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(131072)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _priority_for_issue(message: str) -> int:
        text = message.lower()
        if "operation in progress" in text:
            return 0
        if "not a git worktree" in text or "cannot resolve head" in text:
            return 1
        if "no tracking branch" in text:
            return 2
        if "behind" in text:
            return 3
        if "fetch remote state" in text:
            return 4
        if "uncommitted changes" in text:
            return 5
        if "safe reading file missing" in text:
            return 6
        if "manifest missing" in text or "manifest is not valid json" in text:
            return 7
        if "hash mismatch" in text:
            return 8
        return 9

    def _prioritize_issues(self, issues: list[str]) -> list[str]:
        return sorted(issues, key=lambda message: (self._priority_for_issue(message), message))
