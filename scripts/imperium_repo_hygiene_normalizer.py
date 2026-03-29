#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO_ROOT / "runtime" / "repo_control_center"
ADAPTER_SURFACE_PATH = (
    REPO_ROOT
    / "shared_systems"
    / "factory_observation_window_v1"
    / "adapters"
    / "IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1.json"
)
MANIFEST_PATH = RUNTIME_DIR / "imperium_untracked_classification_manifest.json"
REPORT_PATH = RUNTIME_DIR / "imperium_untracked_classification_report.md"
GATE_PATH = RUNTIME_DIR / "imperium_post_step_hygiene_gate.json"
GATE_MD_PATH = RUNTIME_DIR / "imperium_post_step_hygiene_gate.md"

CLASS_CANONICAL = "CANONICAL_MUST_TRACK"
CLASS_RUNTIME = "GENERATED_RUNTIME_ONLY"
CLASS_REVIEW = "REVIEW_ARTIFACT_RETENTION"
CLASS_JUNK = "JUNK_OR_RESIDUE"
CLASS_OWNER = "NEEDS_OWNER_DECISION"

HYGIENE_GITIGNORE_BLOCK = """
# IMPERIUM REPO HYGIENE NORMALIZATION (generated/review boundaries)
docs/review_artifacts/**
!docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/
!docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/**
vpn_diag/
""".strip()


@dataclass
class GitSnapshot:
    branch: str
    head: str
    staged_paths: list[str]
    unstaged_paths: list[str]
    untracked_paths: list[str]
    deleted_paths: list[str]
    renamed_paths: list[str]
    modified_paths: list[str]
    stash_entries: list[str]
    diff_stat: str
    diff_shortstat: str
    diff_cached_stat: str
    diff_cached_shortstat: str

    @property
    def tracked_dirty_count(self) -> int:
        return len(self.staged_paths) + len(self.unstaged_paths) + len(self.deleted_paths) + len(self.renamed_paths)

    @property
    def untracked_count(self) -> int:
        return len(self.untracked_paths)

    @property
    def cleanliness_verdict(self) -> str:
        tracked_dirty = self.tracked_dirty_count
        untracked = self.untracked_count
        if tracked_dirty == 0 and untracked == 0:
            return "CLEAN"
        if tracked_dirty > 0 and untracked == 0:
            return "DIRTY_TRACKED_ONLY"
        if tracked_dirty == 0 and untracked > 0:
            return "DIRTY_UNTRACKED_ONLY"
        if tracked_dirty > 0 and untracked > 0:
            return "DIRTY_MIXED"
        return "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "head": self.head,
            "cleanliness_verdict": self.cleanliness_verdict,
            "tracked_dirty_count": self.tracked_dirty_count,
            "untracked_count": self.untracked_count,
            "staged_paths": self.staged_paths,
            "unstaged_paths": self.unstaged_paths,
            "modified_paths": self.modified_paths,
            "deleted_paths": self.deleted_paths,
            "renamed_paths": self.renamed_paths,
            "untracked_paths": self.untracked_paths,
            "stash_count": len(self.stash_entries),
            "stash_entries": self.stash_entries,
            "diff_stat": self.diff_stat,
            "diff_shortstat": self.diff_shortstat,
            "diff_cached_stat": self.diff_cached_stat,
            "diff_cached_shortstat": self.diff_cached_shortstat,
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip()


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return str(completed.stdout or "").strip()


def parse_status_snapshot() -> GitSnapshot:
    status_raw = run_git(["status", "--porcelain=v1", "--branch"])
    branch = "UNKNOWN"
    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []
    deleted: list[str] = []
    renamed: list[str] = []
    modified: list[str] = []
    for idx, line in enumerate(status_raw.splitlines()):
        row = str(line or "")
        if idx == 0 and row.startswith("##"):
            branch = row[2:].strip().split("...")[0].strip() or branch
            continue
        if row.startswith("?? "):
            value = normalize(row[3:])
            if value:
                untracked.append(value)
            continue
        if len(row) < 4:
            continue
        x = row[0]
        y = row[1]
        payload = row[3:].strip()
        if " -> " in payload:
            left, right = payload.split(" -> ", 1)
            renamed.append(f"{normalize(left)} -> {normalize(right)}")
            path_norm = normalize(right)
        else:
            path_norm = normalize(payload)
        if not path_norm:
            continue
        if x not in {" ", "?"}:
            staged.append(path_norm)
        if y not in {" ", "?"}:
            unstaged.append(path_norm)
        if "D" in {x, y}:
            deleted.append(path_norm)
        if "M" in {x, y}:
            modified.append(path_norm)

    def uniq(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            out.append(item)
        return out

    return GitSnapshot(
        branch=branch,
        head=run_git(["rev-parse", "HEAD"]),
        staged_paths=uniq(staged),
        unstaged_paths=uniq(unstaged),
        untracked_paths=uniq(untracked),
        deleted_paths=uniq(deleted),
        renamed_paths=uniq(renamed),
        modified_paths=uniq(modified),
        stash_entries=[x for x in run_git(["stash", "list"]).splitlines() if x.strip()],
        diff_stat=run_git(["diff", "--stat"]),
        diff_shortstat=run_git(["diff", "--shortstat"]),
        diff_cached_stat=run_git(["diff", "--cached", "--stat"]),
        diff_cached_shortstat=run_git(["diff", "--cached", "--shortstat"]),
    )


def classify_untracked(path: str) -> str:
    rel = normalize(path).rstrip("/")
    if not rel:
        return CLASS_OWNER

    if rel.startswith("docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/"):
        return CLASS_CANONICAL
    if rel == "CHAT_TRANSFER_CAPSULE_V1.md":
        return CLASS_CANONICAL
    if rel.startswith("docs/governance/"):
        return CLASS_CANONICAL
    if rel.startswith("scripts/"):
        return CLASS_CANONICAL
    if rel.startswith("shared_systems/factory_observation_window_v1/"):
        return CLASS_CANONICAL
    if rel.startswith("workspace_config/"):
        return CLASS_CANONICAL
    if rel.startswith("projects/wild_hunt_command_citadel/tiktok_agent_platform/core/app/"):
        return CLASS_CANONICAL

    if rel.startswith("runtime/"):
        return CLASS_RUNTIME
    if rel.startswith("vpn_diag"):
        return CLASS_RUNTIME
    if rel.startswith("docs/review_artifacts/"):
        return CLASS_REVIEW

    lowered = rel.lower()
    if lowered.endswith((".tmp", ".temp", ".bak", ".old", ".orig")):
        return CLASS_JUNK
    if "/__pycache__/" in lowered or lowered.endswith("/__pycache__"):
        return CLASS_JUNK

    return CLASS_OWNER


def ensure_gitignore_block() -> bool:
    gitignore_path = REPO_ROOT / ".gitignore"
    original = gitignore_path.read_text(encoding="utf-8-sig") if gitignore_path.exists() else ""
    marker = "# IMPERIUM REPO HYGIENE NORMALIZATION (generated/review boundaries)"
    if marker in original:
        return False
    updated = original.rstrip() + "\n\n" + HYGIENE_GITIGNORE_BLOCK + "\n"
    gitignore_path.write_text(updated, encoding="utf-8")
    return True


def chunked(items: list[str], size: int = 120) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def git_add(paths: list[str]) -> int:
    count = 0
    for group in chunked(paths):
        subprocess.run(["git", "add", "--", *group], cwd=REPO_ROOT, check=False)
        count += len(group)
    return count


def remove_junk(paths: list[str]) -> int:
    removed = 0
    for rel in paths:
        target = (REPO_ROOT / rel).resolve()
        if not target.exists():
            continue
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        else:
            target.unlink(missing_ok=True)
        removed += 1
    return removed


def to_surface(classification: dict[str, list[str]], snapshot: GitSnapshot) -> dict[str, Any]:
    counts = {key: len(values) for key, values in classification.items()}
    return {
        "surface_id": "IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1",
        "version": "1.0.0",
        "status": "ACTIVE",
        "generated_at_utc": utc_now_iso(),
        "truth_class": "SOURCE_EXACT",
        "cleanliness_verdict": snapshot.cleanliness_verdict,
        "tracked_dirty_count": snapshot.tracked_dirty_count,
        "untracked_count": snapshot.untracked_count,
        "classification_counts": counts,
        "classification": classification,
        "notes": [
            "classification_first_no_silent_delete",
            "review_artifacts_under_retention_boundary",
            "canonical_assets_staged_for_tracking_when_safe",
        ],
    }


def write_markdown_report(
    *,
    run_id: str,
    before: GitSnapshot,
    after: GitSnapshot,
    classification: dict[str, list[str]],
    actions: dict[str, Any],
) -> None:
    lines: list[str] = [
        "# IMPERIUM Repo Hygiene Normalization",
        "",
        f"- run_id: `{run_id}`",
        f"- generated_at_utc: `{utc_now_iso()}`",
        f"- baseline_cleanliness: `{before.cleanliness_verdict}`",
        f"- post_cleanliness: `{after.cleanliness_verdict}`",
        f"- baseline_untracked: `{before.untracked_count}`",
        f"- post_untracked: `{after.untracked_count}`",
        "",
        "## Classification Counts",
        "",
    ]
    for key in [CLASS_CANONICAL, CLASS_RUNTIME, CLASS_REVIEW, CLASS_JUNK, CLASS_OWNER]:
        lines.append(f"- `{key}`: `{len(classification.get(key, []))}`")
    lines.extend(
        [
            "",
            "## Applied Actions",
            "",
            f"- gitignore_boundary_updated: `{actions.get('gitignore_boundary_updated', False)}`",
            f"- staged_canonical_paths: `{actions.get('staged_canonical_paths', 0)}`",
            f"- removed_junk_paths: `{actions.get('removed_junk_paths', 0)}`",
            f"- owner_review_needed_count: `{len(classification.get(CLASS_OWNER, []))}`",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_gate_snapshot(
    *,
    run_id: str,
    before: GitSnapshot,
    after: GitSnapshot,
    classification: dict[str, list[str]],
) -> None:
    payload = {
        "surface_id": "IMPERIUM_POST_STEP_HYGIENE_GATE_V1",
        "run_id": run_id,
        "generated_at_utc": utc_now_iso(),
        "truth_class": "SOURCE_EXACT",
        "repo_hygiene": {
            "before": before.to_dict(),
            "after": after.to_dict(),
        },
        "classification_summary": {key: len(values) for key, values in classification.items()},
        "verdict": {
            "cleanliness_verdict": after.cleanliness_verdict,
            "worktree_improved": after.untracked_count < before.untracked_count
            or after.cleanliness_verdict != before.cleanliness_verdict,
        },
    }
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = [
        "# IMPERIUM Post-Step Hygiene Gate",
        "",
        f"- run_id: `{run_id}`",
        f"- before: `{before.cleanliness_verdict}`",
        f"- after: `{after.cleanliness_verdict}`",
        f"- untracked_before: `{before.untracked_count}`",
        f"- untracked_after: `{after.untracked_count}`",
        f"- tracked_dirty_after: `{after.tracked_dirty_count}`",
        "",
        "## Class Summary",
        "",
    ]
    for key in [CLASS_CANONICAL, CLASS_RUNTIME, CLASS_REVIEW, CLASS_JUNK, CLASS_OWNER]:
        markdown.append(f"- `{key}`: `{len(classification.get(key, []))}`")
    GATE_MD_PATH.write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM repo hygiene normalization and untracked classification.")
    parser.add_argument("--apply", action="store_true", help="Apply safe normalization actions (no destructive cleanup for ambiguous paths).")
    parser.add_argument("--enforce-ignore-boundary", action="store_true", help="Append canonical review/runtime boundary block to .gitignore.")
    parser.add_argument("--stage-canonical", action="store_true", help="Stage CANONICAL_MUST_TRACK untracked assets.")
    parser.add_argument("--remove-junk", action="store_true", help="Remove JUNK_OR_RESIDUE paths.")
    args = parser.parse_args()

    run_id = f"imperium-repo-hygiene-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    before = parse_status_snapshot()

    classification: dict[str, list[str]] = {
        CLASS_CANONICAL: [],
        CLASS_RUNTIME: [],
        CLASS_REVIEW: [],
        CLASS_JUNK: [],
        CLASS_OWNER: [],
    }
    for rel in before.untracked_paths:
        bucket = classify_untracked(rel)
        classification[bucket].append(rel)

    actions = {
        "gitignore_boundary_updated": False,
        "staged_canonical_paths": 0,
        "removed_junk_paths": 0,
    }
    if args.apply:
        if args.enforce_ignore_boundary:
            actions["gitignore_boundary_updated"] = ensure_gitignore_block()
        if args.remove_junk:
            actions["removed_junk_paths"] = remove_junk(classification.get(CLASS_JUNK, []))
        if args.stage_canonical:
            actions["staged_canonical_paths"] = git_add(classification.get(CLASS_CANONICAL, []))

    after = parse_status_snapshot()
    manifest = {
        "run_id": run_id,
        "generated_at_utc": utc_now_iso(),
        "truth_class": "SOURCE_EXACT",
        "baseline": before.to_dict(),
        "classification": {
            "counts": {key: len(values) for key, values in classification.items()},
            "paths_by_class": classification,
        },
        "actions": actions,
        "post": after.to_dict(),
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ADAPTER_SURFACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ADAPTER_SURFACE_PATH.write_text(
        json.dumps(to_surface(classification=classification, snapshot=after), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown_report(
        run_id=run_id,
        before=before,
        after=after,
        classification=classification,
        actions=actions,
    )
    write_gate_snapshot(
        run_id=run_id,
        before=before,
        after=after,
        classification=classification,
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "run_id": run_id,
                "before_cleanliness": before.cleanliness_verdict,
                "after_cleanliness": after.cleanliness_verdict,
                "before_untracked": before.untracked_count,
                "after_untracked": after.untracked_count,
                "classification_counts": {key: len(values) for key, values in classification.items()},
                "actions": actions,
                "manifest_path": str(MANIFEST_PATH),
                "surface_path": str(ADAPTER_SURFACE_PATH),
                "gate_path": str(GATE_PATH),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
