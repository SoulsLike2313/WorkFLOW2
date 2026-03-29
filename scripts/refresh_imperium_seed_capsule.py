#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPSULE_ROOT = REPO_ROOT / "docs" / "review_artifacts" / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
REVIEW_ARTIFACTS_ROOT = REPO_ROOT / "docs" / "review_artifacts"
EXPORT_ROOT = REPO_ROOT / "runtime" / "chatgpt_bundle_exports"
REQUIRED_REVIEW_FILES = {
    "00_REVIEW_ENTRYPOINT.md",
    "01_INTEGRATION_REPORT.md",
    "02_VALIDATION_REPORT.md",
    "03_TRUTH_CHECK_AND_GAPS.md",
    "04_CHANGED_SURFACES.md",
    "05_API_SMOKE.json",
    "06_BUNDLE_INCLUDE_PATHS.txt",
    "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json",
    "08_ORGAN_STRENGTH_SNAPSHOT.json",
    "09_NODE_RANK_DETECTION_SNAPSHOT.json",
    "10_MACHINE_MODE_SNAPSHOT.json",
    "11_CONSTITUTION_STATUS_SNAPSHOT.json",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def is_canonical_review_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    if path.name == "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1":
        return False
    if path.name == "visual_evidence":
        return False
    files = {p.name for p in path.iterdir() if p.is_file()}
    return REQUIRED_REVIEW_FILES.issubset(files)


def latest_review_roots(limit: int = 1) -> list[Path]:
    roots = [p for p in REVIEW_ARTIFACTS_ROOT.iterdir() if is_canonical_review_root(p)]
    roots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return roots[:limit]


def latest_safe_review_set() -> tuple[str, str]:
    sets = sorted(
        [p for p in REVIEW_ARTIFACTS_ROOT.glob("imperium_safe_review_pipeline_set_*") if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not sets:
        return ("", "")
    review_dir = sets[0]
    export_dir = EXPORT_ROOT / review_dir.name
    return (to_rel(review_dir), to_rel(export_dir) if export_dir.exists() else "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh IMPERIUM seed capsule review pointers/registry.")
    parser.add_argument(
        "--capsule-root",
        default=str(DEFAULT_CAPSULE_ROOT),
        help="Capsule root path (default: docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    capsule_root = Path(args.capsule_root).expanduser()
    if not capsule_root.is_absolute():
        capsule_root = (REPO_ROOT / capsule_root).resolve()
    if not capsule_root.exists():
        raise SystemExit(f"capsule root not found: {capsule_root}")

    mutable_path = capsule_root / "MUTABLE_TRACKER.json"
    mutable = load_json(mutable_path) if mutable_path.exists() else {}

    review_roots = latest_review_roots()
    latest_review = to_rel(review_roots[0]) if review_roots else ""
    safe_review_root, safe_export_root = latest_safe_review_set()
    continuity_line = str(
        ((mutable.get("continuity_step_primary_truth", {}) or {}).get("path", "runtime/chatgpt_bundle_exports/ultimate_transfer_capsule_current_point_sync_delta_primary_truth_bundle_latest.zip"))
    )
    handoff_line = str(
        ((mutable.get("handoff_step_primary_truth_input", {}) or {}).get("path", "runtime/chatgpt_bundle_exports/repo_context_pack_for_canonical_system_mirror_primary_truth_bundle_latest.zip"))
    )
    active_line = str(
        ((mutable.get("active_live_primary_line", {}) or {}).get("path", "runtime/chatgpt_bundle_exports/imperium_remediation_consolidation_supreme_brain_delta_primary_truth_bundle_latest.zip"))
    )
    active_vertex = str(((mutable.get("current_active_vertex", {}) or {}).get("id", "")))

    registry_lines = [
        "# 09_SEED_REVIEW_REGISTRY",
        "",
        "Seed review registry binds current review evidence to onboarding layers.",
        "",
        "## Current review roots (latest-first)",
    ]
    if review_roots:
        for idx, item in enumerate(review_roots, start=1):
            registry_lines.append(f"{idx}. `{to_rel(item)}`")
    else:
        registry_lines.append("- none")
    registry_lines.extend(
        [
            "",
            "## Current safe review set",
            f"- review root: `{safe_review_root or 'none'}`",
            f"- export set: `{safe_export_root or 'none'}`",
            "",
            "## Injection layers",
            "",
            "1. GPT layer:",
            "- compact summary + `for_chatgpt/06_CURRENT_REVIEW_POINTERS.md`",
            "- no heavy payload in paste block",
            "",
            "2. Codex layer:",
            "- full registry + reconstruction order + full pointer set",
            "- use `for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md`",
            "",
            "## Refresh rule",
            "",
            "- `python scripts/refresh_imperium_seed_capsule.py --capsule-root docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1`",
            "",
            f"Last refreshed (UTC): {now_iso()}",
        ]
    )
    write_text(capsule_root / "09_SEED_REVIEW_REGISTRY.md", "\n".join(registry_lines))

    gpt_review_lines = [
        "# 06_CURRENT_REVIEW_POINTERS",
        "",
        "GPT review layer (compact pointers only).",
        "",
        "## Latest canonical review roots",
    ]
    if review_roots:
        for item in review_roots[:1]:
            gpt_review_lines.append(f"- `{to_rel(item)}`")
    else:
        gpt_review_lines.append("- none")
    gpt_review_lines.extend(
        [
            "",
            "## Latest safe review set",
            f"- review root: `{safe_review_root or 'none'}`",
            f"- export set: `{safe_export_root or 'none'}`",
            "",
            "Use pointers only; avoid heavy raw artifact paste by default.",
            f"Last refreshed (UTC): {now_iso()}",
        ]
    )
    write_text(capsule_root / "for_chatgpt" / "06_CURRENT_REVIEW_POINTERS.md", "\n".join(gpt_review_lines))

    codex_pointer_lines = [
        "# 05_CONTEXT_POINTERS_AND_RECOVERY",
        "",
        "## Foundation pointers",
        "",
        "1. docs/governance/SYSTEM_ENTRYPOINT_V1.md",
        "2. docs/governance/FOUNDATION_INDEX_V1.md",
        "3. docs/governance/LIVE_SYSTEM_INDEX_V1.md",
        "",
        "## Capsule pointers",
        "",
        "1. root: docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/",
        "2. mutable tracker: docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/MUTABLE_TRACKER.json",
        "3. current point: docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/08_CURRENT_POINT_VERIFICATION.md",
        "4. ladder: docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md",
        "5. review registry: docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/09_SEED_REVIEW_REGISTRY.md",
        "",
        "## Line split pointers",
        "",
        "1. continuity-step primary:",
        f"- {continuity_line}",
        "2. handoff-step primary input:",
        f"- {handoff_line}",
        "3. active live primary:",
        f"- {active_line}",
        "4. current active vertex:",
        f"- {active_vertex}",
        "",
        "## Current review pointers (Codex full layer)",
    ]
    if review_roots:
        for item in review_roots[:1]:
            codex_pointer_lines.append(f"- `{to_rel(item)}`")
    else:
        codex_pointer_lines.append("- none")
    codex_pointer_lines.extend(
        [
            "",
            "Archived review history remains under `docs/review_artifacts/`.",
        ]
    )
    codex_pointer_lines.extend(
        [
            "",
            "## Latest safe review set",
            f"- review root: `{safe_review_root or 'none'}`",
            f"- export set: `{safe_export_root or 'none'}`",
            "",
            "## Recovery rule",
            "",
            "Recover from tracker+verification+ladder, then verify with latest review root before execution.",
            "Never claim completion without validation artifacts.",
            f"Last refreshed (UTC): {now_iso()}",
        ]
    )
    write_text(capsule_root / "for_codex" / "05_CONTEXT_POINTERS_AND_RECOVERY.md", "\n".join(codex_pointer_lines))

    mutable["last_refreshed_utc"] = now_iso()
    mutable["seed_review_registry_file"] = to_rel(capsule_root / "09_SEED_REVIEW_REGISTRY.md")
    mutable["seed_refresh_command"] = (
        "python scripts/refresh_imperium_seed_capsule.py --capsule-root "
        "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
    )
    if latest_review:
        mutable["latest_review_root"] = latest_review
    if safe_review_root:
        mutable["latest_safe_review_set_review_root"] = safe_review_root
    if safe_export_root:
        mutable["latest_safe_review_set_export_root"] = safe_export_root
    write_json(mutable_path, mutable)

    print(
        json.dumps(
            {
                "status": "ok",
                "capsule_root": to_rel(capsule_root),
                "latest_review_root": latest_review,
                "latest_safe_review_set_review_root": safe_review_root,
                "latest_safe_review_set_export_root": safe_export_root,
                "updated_files": [
                    to_rel(capsule_root / "09_SEED_REVIEW_REGISTRY.md"),
                    to_rel(capsule_root / "for_chatgpt" / "06_CURRENT_REVIEW_POINTERS.md"),
                    to_rel(capsule_root / "for_codex" / "05_CONTEXT_POINTERS_AND_RECOVERY.md"),
                    to_rel(mutable_path),
                ],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
