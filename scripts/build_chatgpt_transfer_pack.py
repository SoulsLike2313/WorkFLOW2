#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT = "workspace_config/review_bundle_output_contract.json"
DEFAULT_TEXT_EXTENSIONS = [
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
    ".tsv",
    ".xml",
    ".html",
    ".htm",
    ".py",
    ".js",
    ".css",
    ".ps1",
    ".sh",
    ".bat",
]
VISUAL_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".svg",
}
OPTIONAL_BINARY_EXTENSIONS = {
    ".zip",
    ".7z",
    ".rar",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".bin",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def safe_step_id(raw: str) -> str:
    value = str(raw or "").strip()
    if not value:
        return "unknown_step"
    allowed = []
    for ch in value:
        if ch.isalnum() or ch in {"-", "_", "."}:
            allowed.append(ch)
        else:
            allowed.append("_")
    return "".join(allowed)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def parse_include_lines(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    items: list[str] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        items.append(line.replace("\\", "/").strip("/"))
    return items


def split_bytes_to_parts(blob: bytes, part_size_bytes: int, prefix: str, out_dir: Path) -> list[dict[str, Any]]:
    total = len(blob)
    if total == 0:
        return []
    count = (total + part_size_bytes - 1) // part_size_bytes
    width = max(2, len(str(count)))
    out_dir.mkdir(parents=True, exist_ok=True)
    parts: list[dict[str, Any]] = []
    for idx in range(count):
        start = idx * part_size_bytes
        end = min(start + part_size_bytes, total)
        chunk = blob[start:end]
        name = f"{prefix}.part{idx + 1:0{width}d}of{count:0{width}d}"
        path = out_dir / name
        path.write_bytes(chunk)
        parts.append(
            {
                "part_index": idx + 1,
                "part_name": name,
                "part_path": str(path),
                "size_bytes": len(chunk),
                "sha256": sha256_bytes(chunk),
            }
        )
    return parts


def gather_review_root_files(review_root: Path, transfer_root: Path) -> list[Path]:
    files: list[Path] = []
    for item in review_root.rglob("*"):
        if not item.is_file():
            continue
        if transfer_root in item.parents:
            continue
        files.append(item.resolve())
    return sorted(set(files))


def gather_external_from_include_files(
    repo_root: Path,
    review_root: Path,
    include_files: list[str],
) -> tuple[list[Path], list[str], list[str]]:
    external: set[Path] = set()
    pointer_only: list[str] = []
    missing: list[str] = []

    for include_file in include_files:
        include_path = review_root / include_file
        for rel in parse_include_lines(include_path):
            candidate = (repo_root / rel).resolve()
            if not candidate.exists():
                missing.append(rel)
                continue
            if candidate.is_file():
                external.add(candidate)
                continue
            if candidate.is_dir():
                pointer_only.append(rel)
                for child in candidate.rglob("*"):
                    if child.is_file():
                        external.add(child.resolve())
    return sorted(external), sorted(set(pointer_only)), sorted(set(missing))


def is_visual_path(path: Path) -> bool:
    rel = str(path).replace("\\", "/").lower()
    if "/visual_evidence/" in rel:
        return True
    return path.suffix.lower() in VISUAL_EXTENSIONS


def is_optional_binary(path: Path) -> bool:
    name = path.name.lower()
    if ".part" in name:
        return True
    return path.suffix.lower() in OPTIONAL_BINARY_EXTENSIONS


def is_text_surface(path: Path, text_exts: set[str], max_text_bytes: int) -> bool:
    if path.suffix.lower() not in text_exts:
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    return size <= max_text_bytes


def gather_seed_capsule_text_files(
    repo_root: Path,
    policy: dict[str, Any],
    text_exts: set[str],
    max_text_bytes: int,
) -> tuple[list[Path], Path | None]:
    if not bool(policy.get("include_seed_capsule_root", True)):
        return [], None
    seed_root_raw = str(
        policy.get(
            "seed_capsule_root",
            "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1",
        )
    ).strip()
    if not seed_root_raw:
        return [], None
    seed_root = (repo_root / seed_root_raw).resolve()
    if not seed_root.exists() or not seed_root.is_dir():
        return [], seed_root

    files: list[Path] = []
    for item in seed_root.rglob("*"):
        if not item.is_file():
            continue
        if is_visual_path(item):
            continue
        if is_optional_binary(item):
            continue
        if is_text_surface(item, text_exts, max_text_bytes):
            files.append(item.resolve())
    return sorted(set(files)), seed_root


def build_section_archive(
    *,
    repo_root: Path,
    output_dir: Path,
    archive_prefix: str,
    files: list[Path],
    part_size_bytes: int,
) -> dict[str, Any]:
    archive_name = f"{archive_prefix}.zip"
    archive_path = output_dir / archive_name
    if output_dir.exists():
        for old in output_dir.glob(f"{archive_prefix}.part*of*"):
            old.unlink(missing_ok=True)
    if archive_path.exists():
        archive_path.unlink()

    unique_files = sorted(set(files))
    if not unique_files:
        return {
            "mode": "empty",
            "archive_name": archive_name,
            "archive_size_bytes": 0,
            "archive_sha256": "",
            "part_count": 0,
            "parts": [],
            "included_paths": [],
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src in unique_files:
            zf.write(src, arcname=normalize_rel(src, repo_root))

    blob = archive_path.read_bytes()
    parts = split_bytes_to_parts(
        blob=blob,
        part_size_bytes=part_size_bytes,
        prefix=archive_prefix,
        out_dir=output_dir,
    )
    archive_sha = sha256_bytes(blob)
    archive_size = len(blob)
    archive_path.unlink(missing_ok=True)

    return {
        "mode": "split_parts",
        "archive_name": archive_name,
        "archive_size_bytes": archive_size,
        "archive_sha256": archive_sha,
        "part_count": len(parts),
        "parts": [
            {
                "part_index": item["part_index"],
                "part_name": item["part_name"],
                "part_path": normalize_rel(Path(item["part_path"]), repo_root),
                "size_bytes": item["size_bytes"],
                "sha256": item["sha256"],
            }
            for item in parts
        ],
        "included_paths": [normalize_rel(path, repo_root) for path in unique_files],
    }


def collect_core_families(
    *,
    included_paths: list[str],
    review_root_rel: str,
    seed_root_rel: str | None,
    required_files: list[str],
) -> list[str]:
    families: set[str] = set()
    required_names = set(required_files)
    has_foundation_tracker = False
    has_mutable_tracker = False

    for rel in included_paths:
        if rel.startswith(f"{review_root_rel}/"):
            name = Path(rel).name
            if name in required_names:
                families.add("review_standard_set")
            if name in {
                "01_INTEGRATION_REPORT.md",
                "02_VALIDATION_REPORT.md",
                "03_TRUTH_CHECK_AND_GAPS.md",
                "04_CHANGED_SURFACES.md",
                "05_API_SMOKE.json",
                "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.md",
                "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json",
            }:
                families.add("validation_truth_changed_surfaces")
            if rel.endswith(".md") or rel.endswith(".json") or rel.endswith(".txt"):
                families.add("review_text_surfaces")
        elif seed_root_rel and rel.startswith(f"{seed_root_rel}/"):
            families.add("seed_capsule_root")
            if "/for_chatgpt/" in rel:
                families.add("for_chatgpt")
            if "/for_codex/" in rel:
                families.add("for_codex")
            if rel.endswith("/FOUNDATION_TRACKER.json"):
                has_foundation_tracker = True
            if rel.endswith("/MUTABLE_TRACKER.json"):
                has_mutable_tracker = True
        else:
            families.add("external_include_text")
    if has_foundation_tracker and has_mutable_tracker:
        families.add("trackers")
    return sorted(families)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build compact ChatGPT transfer package for a review root.")
    parser.add_argument("--review-root", required=True, help="Review root under docs/review_artifacts/<step_folder>.")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT, help="Contract json path.")
    return parser.parse_args()


def ensure_archive_first_outer_layer(
    *,
    transfer_root: Path,
    keep_names: set[str],
) -> list[str]:
    removed: list[str] = []
    for item in transfer_root.iterdir():
        if item.name in {"visual", "optional"}:
            continue
        if item.name in keep_names:
            continue
        if item.is_file():
            item.unlink(missing_ok=True)
            removed.append(item.name)
        elif item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
            removed.append(item.name)
    return sorted(removed)


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()

    contract_path = Path(args.contract).expanduser()
    if not contract_path.is_absolute():
        contract_path = (repo_root / contract_path).resolve()
    if not contract_path.exists():
        raise SystemExit(f"contract not found: {contract_path}")
    contract = load_json(contract_path)

    review_root = Path(args.review_root).expanduser()
    if not review_root.is_absolute():
        review_root = (repo_root / review_root).resolve()
    if not review_root.exists():
        raise SystemExit(f"review root not found: {review_root}")
    step_id = safe_step_id(review_root.name)

    policy = contract.get("chatgpt_transfer_policy", {}) or {}
    if not bool(policy.get("enabled", True)):
        print(
            json.dumps(
                {
                    "status": "disabled",
                    "review_root": normalize_rel(review_root, repo_root),
                    "reason": "chatgpt_transfer_policy.disabled",
                },
                ensure_ascii=False,
            )
        )
        return 0

    transfer_dir_name = str(policy.get("folder_name", "chatgpt_transfer")).strip() or "chatgpt_transfer"
    part_target_mb = int(policy.get("part_size_mb_target", 32) or 32)
    part_min_mb = int(policy.get("part_size_mb_min", 20) or 20)
    part_max_mb = int(policy.get("part_size_mb_max", 40) or 40)
    max_parts_per_wave = int(policy.get("max_parts_per_wave", 9) or 9)
    max_parts_hard_limit = int(policy.get("max_parts_hard_limit", 15) or 15)
    ideal_parts_min = int(policy.get("ideal_parts_min", 1) or 1)
    ideal_parts_max = int(policy.get("ideal_parts_max", 3) or 3)
    archive_first_required = bool(policy.get("archive_first_required", True))
    include_files = [str(x).strip() for x in policy.get("include_paths_files", []) if str(x).strip()]
    if not include_files:
        include_files = ["06_BUNDLE_INCLUDE_PATHS.txt", "14_ARCHIVE_INCLUDE_PATHS.txt"]
    core_archive_prefix_base = str(policy.get("core_archive_prefix", "core_chatgpt_transfer")).strip() or "core_chatgpt_transfer"
    visual_archive_prefix_base = str(policy.get("visual_archive_prefix", "visual_chatgpt_transfer")).strip() or "visual_chatgpt_transfer"
    optional_archive_prefix_base = str(policy.get("optional_archive_prefix", "optional_chatgpt_transfer")).strip() or "optional_chatgpt_transfer"
    core_archive_prefix = f"{step_id}__{core_archive_prefix_base}"
    visual_archive_prefix = f"{step_id}__{visual_archive_prefix_base}"
    optional_archive_prefix = f"{step_id}__{optional_archive_prefix_base}"
    max_text_mb = int(policy.get("core_max_text_file_mb", 5) or 5)
    text_exts = {
        str(ext).strip().lower()
        for ext in policy.get("core_text_extensions", DEFAULT_TEXT_EXTENSIONS)
        if str(ext).strip()
    }
    max_text_bytes = max_text_mb * 1024 * 1024

    if part_target_mb < part_min_mb:
        part_target_mb = part_min_mb
    if part_target_mb > part_max_mb:
        part_target_mb = part_max_mb
    part_size_bytes = part_target_mb * 1024 * 1024

    transfer_root = review_root / transfer_dir_name
    if transfer_root.exists():
        shutil.rmtree(transfer_root)
    transfer_root.mkdir(parents=True, exist_ok=True)

    required_files = [str(x).strip() for x in contract.get("required_review_files", []) if str(x).strip()]
    required_set = {review_root / name for name in required_files}

    review_files = gather_review_root_files(review_root, transfer_root)
    external_files, pointer_only_paths, missing_paths = gather_external_from_include_files(
        repo_root=repo_root,
        review_root=review_root,
        include_files=include_files,
    )
    seed_files, seed_root = gather_seed_capsule_text_files(
        repo_root=repo_root,
        policy=policy,
        text_exts=text_exts,
        max_text_bytes=max_text_bytes,
    )

    all_candidates = sorted(set(review_files + external_files + seed_files))

    visual_candidates = sorted(path for path in all_candidates if is_visual_path(path))
    review_root_resolved = review_root.resolve()
    optional_candidates = sorted(
        path
        for path in all_candidates
        if is_optional_binary(path) and not path.resolve().is_relative_to(review_root_resolved)
    )

    core_candidates: set[Path] = set()
    core_candidates.update([path.resolve() for path in required_set if path.exists() and path.is_file()])
    for path in all_candidates:
        if is_text_surface(path, text_exts, max_text_bytes):
            core_candidates.add(path.resolve())

    visual_set = {path.resolve() for path in visual_candidates}
    optional_set = {path.resolve() for path in optional_candidates}

    core_files = sorted(
        path
        for path in core_candidates
        if path.resolve() not in visual_set and path.resolve() not in optional_set
    )
    visual_files = sorted(path for path in visual_candidates if path.resolve() not in optional_set)
    optional_files = sorted(path for path in optional_candidates if path.resolve() not in visual_set)

    core_result = build_section_archive(
        repo_root=repo_root,
        output_dir=transfer_root,
        archive_prefix=core_archive_prefix,
        files=core_files,
        part_size_bytes=part_size_bytes,
    )
    visual_dir = transfer_root / "visual"
    visual_result = build_section_archive(
        repo_root=repo_root,
        output_dir=visual_dir,
        archive_prefix=visual_archive_prefix,
        files=visual_files,
        part_size_bytes=part_size_bytes,
    )
    optional_dir = transfer_root / "optional"
    optional_result = build_section_archive(
        repo_root=repo_root,
        output_dir=optional_dir,
        archive_prefix=optional_archive_prefix,
        files=optional_files,
        part_size_bytes=part_size_bytes,
    )
    if visual_result.get("part_count", 0) == 0 and visual_dir.exists():
        shutil.rmtree(visual_dir)
    if optional_result.get("part_count", 0) == 0 and optional_dir.exists():
        shutil.rmtree(optional_dir)

    total_part_count = (
        int(core_result.get("part_count", 0))
        + int(visual_result.get("part_count", 0))
        + int(optional_result.get("part_count", 0))
    )
    upload_wave_ready = total_part_count <= max_parts_per_wave
    hard_limit_ok = total_part_count <= max_parts_hard_limit
    ideal_parts_band = ideal_parts_min <= total_part_count <= ideal_parts_max

    upload_order: list[str] = []
    upload_order.extend([item["part_name"] for item in core_result.get("parts", [])])
    upload_order.extend([item["part_name"] for item in visual_result.get("parts", [])])
    upload_order.extend([item["part_name"] for item in optional_result.get("parts", [])])

    core_included = core_result.get("included_paths", [])
    required_present = {
        item: any(path.endswith(f"/{item}") for path in core_included) for item in required_files
    }
    all_required_embedded = all(required_present.values()) if required_files else True
    package_complete = bool(
        upload_wave_ready
        and hard_limit_ok
        and all_required_embedded
        and core_result.get("part_count", 0) > 0
    )

    review_root_rel = normalize_rel(review_root, repo_root)
    seed_root_rel = normalize_rel(seed_root, repo_root) if seed_root and seed_root.exists() else None
    included_file_families = collect_core_families(
        included_paths=core_included,
        review_root_rel=review_root_rel,
        seed_root_rel=seed_root_rel,
        required_files=required_files,
    )

    transfer_manifest = {
        "schema_version": "imperium_chatgpt_transfer_manifest.v3",
        "generated_at_utc": utc_now_iso(),
        "step_id": step_id,
        "review_root": review_root_rel,
        "transfer_root": normalize_rel(transfer_root, repo_root),
        "archive_first_required": archive_first_required,
        "core_required": True,
        "parts_total": total_part_count,
        "parts_hard_limit": max_parts_hard_limit,
        "parts_hard_limit_ok": hard_limit_ok,
        "parts_ideal_band": [ideal_parts_min, ideal_parts_max],
        "parts_ideal_band_hit": ideal_parts_band,
        "package_completeness": "COMPLETE" if package_complete else "PARTIAL",
        "visual_included": bool(visual_result.get("part_count", 0)),
        "optional_included": bool(optional_result.get("part_count", 0)),
        "included_file_families": included_file_families,
        "policy": {
            "layout": "compact_core_layered_visual_optional",
            "part_size_mb_target": part_target_mb,
            "part_size_mb_min": part_min_mb,
            "part_size_mb_max": part_max_mb,
            "max_parts_per_wave": max_parts_per_wave,
            "max_parts_hard_limit": max_parts_hard_limit,
            "ideal_parts_min": ideal_parts_min,
            "ideal_parts_max": ideal_parts_max,
            "step_id_prefix_required": bool(policy.get("step_id_prefix_required", True)),
            "core_archive_prefix": core_archive_prefix,
        },
        "upload_wave_ready": upload_wave_ready,
        "upload_order": upload_order,
        "required_review_files_embedded": {
            "all_12_embedded": all_required_embedded,
            "by_file": required_present,
        },
        "sections": {
            "core": core_result,
            "visual": visual_result,
            "optional": optional_result,
        },
        "pointer_only_paths": pointer_only_paths,
        "missing_paths": missing_paths,
    }

    manifest_json = transfer_root / f"{step_id}__chatgpt_transfer_manifest.json"
    manifest_md = transfer_root / f"{step_id}__chatgpt_transfer_manifest.md"
    readme_md = transfer_root / f"{step_id}__00_CHATGPT_TRANSFER_README.md"
    manifest_json.write_text(json.dumps(transfer_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# ChatGPT Transfer Manifest",
        "",
        f"- review_root: `{transfer_manifest['review_root']}`",
        f"- transfer_root: `{transfer_manifest['transfer_root']}`",
        f"- core_required: `true`",
        f"- parts_total: `{total_part_count}`",
        f"- package_completeness: `{transfer_manifest['package_completeness']}`",
        f"- visual_included: `{str(transfer_manifest['visual_included']).lower()}`",
        f"- optional_included: `{str(transfer_manifest['optional_included']).lower()}`",
        "",
        "## Included File Families",
    ]
    md_lines.extend([f"- `{item}`" for item in included_file_families] or ["- none"])
    md_lines.extend(["", "## Required Review Files In CORE"])
    md_lines.append(f"- all_12_embedded: `{str(all_required_embedded).lower()}`")
    for name, ok in required_present.items():
        md_lines.append(f"- `{name}`: `{str(ok).lower()}`")
    md_lines.extend(["", "## Upload Order"])
    md_lines.extend([f"- `{item}`" for item in upload_order] or ["- none"])
    manifest_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    readme_lines = [
        "# CHATGPT Transfer README",
        "",
        "- read order: `core first` -> `visual (if needed)` -> `optional (if needed)`",
        f"- core_required: `true`",
        f"- parts_total: `{total_part_count}`",
        f"- package_complete: `{str(package_complete).lower()}`",
        f"- part_size_target_mb: `{part_target_mb}` (allowed `{part_min_mb}-{part_max_mb}`)",
        "",
        "## Upload Order",
    ]
    readme_lines.extend([f"{idx}. `{name}`" for idx, name in enumerate(upload_order, start=1)] or ["1. `none`"])
    readme_lines.extend(
        [
            "",
            "## Layer Meaning",
            "- core: mandatory reading package for reconstruction (review + seed-facing text surfaces).",
            "- visual: screenshots / diff previews / visual-only payload.",
            "- optional: heavy non-essential extras.",
            "",
            "## Notes",
            "- local review root remains canonical source.",
            "- this transfer folder is the upload-optimized handoff layer.",
            "",
        ]
    )
    readme_md.write_text("\n".join(readme_lines), encoding="utf-8")

    keep_names: set[str] = {
        readme_md.name,
        manifest_json.name,
        manifest_md.name,
    }
    keep_names.update([item["part_name"] for item in core_result.get("parts", [])])
    if visual_result.get("part_count", 0) == 0:
        keep_names.update([item["part_name"] for item in visual_result.get("parts", [])])
    if optional_result.get("part_count", 0) == 0:
        keep_names.update([item["part_name"] for item in optional_result.get("parts", [])])

    removed_outer = ensure_archive_first_outer_layer(transfer_root=transfer_root, keep_names=keep_names)
    transfer_manifest["outer_layer_removed_nonstandard"] = removed_outer
    transfer_manifest["outer_layer_helper_files"] = sorted(list(keep_names))
    manifest_json.write_text(json.dumps(transfer_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out = {
        "status": "ok",
        "review_root": review_root_rel,
        "transfer_root": normalize_rel(transfer_root, repo_root),
        "mode": "compact_core_layered_visual_optional",
        "archive_first_required": archive_first_required,
        "part_size_target_mb": part_target_mb,
        "part_size_allowed_range_mb": [part_min_mb, part_max_mb],
        "total_part_count": total_part_count,
        "parts_hard_limit": max_parts_hard_limit,
        "parts_hard_limit_ok": hard_limit_ok,
        "parts_ideal_band": [ideal_parts_min, ideal_parts_max],
        "parts_ideal_band_hit": ideal_parts_band,
        "upload_wave_ready": upload_wave_ready,
        "core_part_count": core_result["part_count"],
        "visual_part_count": visual_result["part_count"],
        "optional_part_count": optional_result["part_count"],
        "core_required": True,
        "package_completeness": transfer_manifest["package_completeness"],
        "included_file_families": included_file_families,
        "visual_included": transfer_manifest["visual_included"],
        "optional_included": transfer_manifest["optional_included"],
        "readme": normalize_rel(readme_md, repo_root),
        "manifest_json": normalize_rel(manifest_json, repo_root),
        "manifest_md": normalize_rel(manifest_md, repo_root),
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
