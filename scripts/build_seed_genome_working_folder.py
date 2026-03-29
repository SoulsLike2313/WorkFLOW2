#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPSULE_ROOT = REPO_ROOT / "docs" / "review_artifacts" / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
DEFAULT_OUTPUT_NAME = "SEED_GENOME_WORKING_FOLDER_V1"

ROOT_FILES = [
    "00_CAPSULE_ENTRYPOINT.md",
    "00_CAPSULE_ROOT_PATH.md",
    "01_FOUNDATION_IMMUTABLE_CANON.md",
    "02_MUTABLE_ACTIVE_STATE.md",
    "03_CAPSULE_UPDATE_PROTOCOL.md",
    "04_GPT_CONFIRMATION_PROTOCOL.md",
    "05_CAPSULE_ACCEPTANCE_GATE.md",
    "06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md",
    "07_OWNER_USE_FLOW.md",
    "08_CURRENT_POINT_VERIFICATION.md",
    "09_SEED_REVIEW_REGISTRY.md",
    "10_SEED_COMPRESSION_AND_ASSEMBLY_LAW.md",
    "FOUNDATION_TRACKER.json",
    "MUTABLE_TRACKER.json",
]

REQUIRED_REL_PATHS = [
    "for_chatgpt/01_PASTE_THIS_FULL.md",
    "for_chatgpt/02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md",
    "for_chatgpt/03_AFTER_PASTE_ASK_THIS.md",
    "for_chatgpt/04_EXPECTED_GPT_CONFIRMATION_SHAPE.md",
    "for_chatgpt/05_CURRENT_BUNDLE_POINTERS.md",
    "for_chatgpt/06_CURRENT_REVIEW_POINTERS.md",
    "for_chatgpt/07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md",
    "for_codex/01_CODEX_BOOTSTRAP_NOTE.md",
    "for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md",
    "for_codex/07_CODEX_RECONSTRUCTION_CHECKLIST.md",
]

SYNC_CHECKS: dict[str, list[str]] = {
    "00_CAPSULE_ENTRYPOINT.md": ["continuity_line", "handoff_line", "active_line"],
    "02_MUTABLE_ACTIVE_STATE.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "08_CURRENT_POINT_VERIFICATION.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_chatgpt/01_PASTE_THIS_FULL.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_chatgpt/02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_chatgpt/05_CURRENT_BUNDLE_POINTERS.md": ["continuity_line", "handoff_line", "active_line"],
    "for_chatgpt/07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md": ["continuity_line", "handoff_line", "active_line"],
}

STALE_PATTERNS = [
    "imperium_living_spatial_brain_of_imperium_delta_primary_truth_bundle_latest.zip",
    "IMPERIUM_LIVING_SPATIAL_BRAIN_OF_IMPERIUM",
]


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build standalone seed genome working folder from capsule root.")
    parser.add_argument("--step-root", required=True, help="Step folder under docs/review_artifacts/<step_id>.")
    parser.add_argument("--capsule-root", default=str(DEFAULT_CAPSULE_ROOT), help="Capsule root.")
    parser.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME, help="Output folder name under step root.")
    return parser.parse_args()


def copy_seed_families(capsule_root: Path, target_root: Path) -> list[str]:
    copied: list[str] = []
    for name in ROOT_FILES:
        src = capsule_root / name
        dst = target_root / name
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(to_rel(dst))

    for folder in ["for_chatgpt", "for_codex"]:
        src_dir = capsule_root / folder
        dst_dir = target_root / folder
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        if src_dir.exists() and src_dir.is_dir():
            shutil.copytree(src_dir, dst_dir)
            for item in dst_dir.rglob("*"):
                if item.is_file():
                    copied.append(to_rel(item))
    return sorted(set(copied))


def main() -> int:
    args = parse_args()
    step_root = Path(args.step_root).expanduser()
    if not step_root.is_absolute():
        step_root = (REPO_ROOT / step_root).resolve()
    if not step_root.exists():
        raise SystemExit(f"step root not found: {step_root}")

    capsule_root = Path(args.capsule_root).expanduser()
    if not capsule_root.is_absolute():
        capsule_root = (REPO_ROOT / capsule_root).resolve()
    if not capsule_root.exists():
        raise SystemExit(f"capsule root not found: {capsule_root}")

    mutable_path = capsule_root / "MUTABLE_TRACKER.json"
    if not mutable_path.exists():
        raise SystemExit("capsule mutable tracker missing")
    mutable = load_json(mutable_path)

    active_line = str(((mutable.get("active_live_primary_line", {}) or {}).get("path", "")))
    continuity_line = str(((mutable.get("continuity_step_primary_truth", {}) or {}).get("path", "")))
    handoff_line = str(((mutable.get("handoff_step_primary_truth_input", {}) or {}).get("path", "")))
    active_vertex = str(((mutable.get("current_active_vertex", {}) or {}).get("id", "")))

    target_root = step_root / str(args.output_name).strip()
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    copied_files = copy_seed_families(capsule_root=capsule_root, target_root=target_root)

    entrypoint = "\n".join(
        [
            "# 00_SEED_GENOME_ENTRYPOINT",
            "",
            "Standalone seed-genome working folder for relocation/new-chat reconstruction.",
            "",
            "## Read-first flow",
            "",
            "1. for_chatgpt/01_PASTE_THIS_FULL.md",
            "2. for_chatgpt/03_AFTER_PASTE_ASK_THIS.md",
            "3. for_chatgpt/04_EXPECTED_GPT_CONFIRMATION_SHAPE.md",
            "4. for_codex/07_CODEX_RECONSTRUCTION_CHECKLIST.md",
            "5. 08_CURRENT_POINT_VERIFICATION.md",
            "",
            "## Current point",
            f"- active live line: `{active_line}`",
            f"- continuity line: `{continuity_line}`",
            f"- handoff line: `{handoff_line}`",
            f"- active vertex: `{active_vertex}`",
            "",
            "## System-slice rule",
            "- full system slice must include seed-genome sync + Inquisition audit + relocation-readiness check.",
            "",
            f"Generated (UTC): {now_iso()}",
        ]
    )
    write_text(target_root / "00_SEED_GENOME_ENTRYPOINT.md", entrypoint)

    sync_failures: list[str] = []
    lookup = {
        "active_line": active_line,
        "continuity_line": continuity_line,
        "handoff_line": handoff_line,
        "active_vertex": active_vertex,
    }
    for rel, keys in SYNC_CHECKS.items():
        file_path = target_root / rel
        if not file_path.exists():
            sync_failures.append(f"missing_sync_file::{rel}")
            continue
        text = file_path.read_text(encoding="utf-8-sig")
        for key in keys:
            value = lookup.get(key, "")
            if value and value not in text:
                sync_failures.append(f"sync_mismatch::{rel}::{key}")

    stale_hits: list[str] = []
    for item in target_root.rglob("*"):
        if not item.is_file() or item.suffix.lower() not in {".md", ".json", ".txt"}:
            continue
        text = item.read_text(encoding="utf-8-sig")
        for pattern in STALE_PATTERNS:
            if pattern in text:
                stale_hits.append(f"stale::{to_rel(item)}::{pattern}")

    missing_required = [rel for rel in REQUIRED_REL_PATHS if not (target_root / rel).exists()]
    tracker_presence = {
        "foundation_tracker_present": (target_root / "FOUNDATION_TRACKER.json").exists(),
        "mutable_tracker_present": (target_root / "MUTABLE_TRACKER.json").exists(),
    }
    relocation_ready = len(missing_required) == 0 and all(tracker_presence.values())

    gate_text = (target_root / "05_CAPSULE_ACCEPTANCE_GATE.md").read_text(encoding="utf-8-sig")
    gate_claims_ok = (
        "stale active-live wording is absent" in gate_text
        and "continuity/handoff/live lines remain separate" in gate_text
    )

    inquisition_failures = [*sync_failures, *stale_hits]
    inquisition_pass = len(inquisition_failures) == 0
    acceptance_pass = inquisition_pass and relocation_ready and gate_claims_ok

    audit = {
        "schema_version": "imperium_seed_genome_inquisition_audit.v1",
        "generated_at_utc": now_iso(),
        "step_root": to_rel(step_root),
        "seed_genome_root": to_rel(target_root),
        "authoritative_current_point": {
            "active_live_line": active_line,
            "continuity_line": continuity_line,
            "handoff_line": handoff_line,
            "active_vertex": active_vertex,
        },
        "copied_files_count": len(copied_files),
        "sync_failures": sync_failures,
        "stale_hits": stale_hits,
        "missing_required_paths": missing_required,
        "tracker_presence": tracker_presence,
        "relocation_ready": relocation_ready,
        "acceptance_gate_claims_present": gate_claims_ok,
        "inquisition_pass": inquisition_pass,
        "acceptance_pass": acceptance_pass,
        "status": "PASS" if acceptance_pass else "FAIL",
        "failures": inquisition_failures if not acceptance_pass else [],
    }
    write_json(target_root / "90_INQUISITION_SEED_TRUTH_AUDIT.json", audit)
    audit_md = [
        "# 90_INQUISITION_SEED_TRUTH_AUDIT",
        "",
        f"- status: `{audit['status']}`",
        f"- inquisition_pass: `{str(inquisition_pass).lower()}`",
        f"- relocation_ready: `{str(relocation_ready).lower()}`",
        f"- acceptance_pass: `{str(acceptance_pass).lower()}`",
        f"- sync_failures: `{len(sync_failures)}`",
        f"- stale_hits: `{len(stale_hits)}`",
        f"- missing_required_paths: `{len(missing_required)}`",
        "",
        "## Failures",
    ]
    if audit["failures"]:
        audit_md.extend([f"- `{item}`" for item in audit["failures"]])
    else:
        audit_md.append("- none")
    write_text(target_root / "90_INQUISITION_SEED_TRUTH_AUDIT.md", "\n".join(audit_md))

    manifest = {
        "schema_version": "imperium_seed_genome_folder_manifest.v1",
        "generated_at_utc": now_iso(),
        "seed_genome_root": to_rel(target_root),
        "families": {
            "for_chatgpt": (target_root / "for_chatgpt").exists(),
            "for_codex": (target_root / "for_codex").exists(),
            "seed_capsule_root_files": all((target_root / name).exists() for name in ROOT_FILES),
            "trackers": tracker_presence,
        },
        "copied_files_count": len(copied_files),
        "copied_files": copied_files,
        "system_slice_rule_enabled": True,
    }
    write_json(target_root / "91_SEED_GENOME_FOLDER_MANIFEST.json", manifest)

    print(
        json.dumps(
            {
                "status": audit["status"].lower(),
                "step_root": to_rel(step_root),
                "seed_genome_root": to_rel(target_root),
                "inquisition_pass": inquisition_pass,
                "acceptance_pass": acceptance_pass,
                "sync_failures": len(sync_failures),
                "stale_hits": len(stale_hits),
                "missing_required_paths": len(missing_required),
            },
            ensure_ascii=False,
        )
    )
    return 0 if acceptance_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
