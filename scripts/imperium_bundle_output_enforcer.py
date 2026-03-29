#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT = "workspace_config/review_bundle_output_contract.json"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def split_archive(archive_path: Path, part_size_bytes: int) -> dict[str, Any]:
    if not archive_path.exists() or not archive_path.is_file():
        return {
            "archive": str(archive_path),
            "status": "MISSING",
            "parts": [],
        }

    parts_dir = archive_path.parent / f"{archive_path.name}_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    for old in parts_dir.glob(f"{archive_path.name}.part*"):
        old.unlink(missing_ok=True)

    parts: list[dict[str, Any]] = []
    with archive_path.open("rb") as source:
        index = 1
        while True:
            chunk = source.read(part_size_bytes)
            if not chunk:
                break
            part_name = f"{archive_path.name}.part{index:03d}"
            part_path = parts_dir / part_name
            with part_path.open("wb") as target:
                target.write(chunk)
            parts.append(
                {
                    "part_index": index,
                    "part_name": part_name,
                    "part_path": str(part_path),
                    "size_bytes": part_path.stat().st_size,
                    "sha256": sha256_of_file(part_path),
                }
            )
            index += 1

    return {
        "archive": str(archive_path),
        "archive_size_bytes": archive_path.stat().st_size,
        "archive_sha256": sha256_of_file(archive_path),
        "parts_dir": str(parts_dir),
        "part_count": len(parts),
        "parts": parts,
        "status": "SPLIT_OK" if parts else "EMPTY_ARCHIVE",
    }


def run_ttl_janitor(repo_root: Path, apply_mode: bool) -> dict[str, Any]:
    cmd = ["python", "scripts/ttl_bundle_janitor.py"]
    if apply_mode:
        cmd.append("--apply")
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload: dict[str, Any] = {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "status": "OK" if proc.returncode == 0 else "ERROR",
    }
    raw = payload["stdout"]
    if raw.startswith("{"):
        try:
            parsed = json.loads(raw)
            payload["janitor_report"] = parsed
        except json.JSONDecodeError:
            pass
    return payload


def run_chatgpt_transfer_pack(repo_root: Path, review_root: Path, contract_path: Path) -> dict[str, Any]:
    cmd = [
        "python",
        "scripts/build_chatgpt_transfer_pack.py",
        "--review-root",
        str(review_root),
        "--contract",
        str(contract_path),
    ]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload: dict[str, Any] = {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "status": "OK" if proc.returncode == 0 else "ERROR",
    }
    raw = payload["stdout"]
    if raw.startswith("{"):
        try:
            payload["transfer_report"] = json.loads(raw)
        except json.JSONDecodeError:
            pass
    return payload


def to_repo_rel(path: Path, repo_root: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


def normalize_rel_path(value: str) -> str:
    return str(value or "").replace("\\", "/").strip("/")


def resolve_part_path(repo_root: Path, raw: str) -> Path:
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (repo_root / candidate).resolve()


def parse_readme_parts_total(readme_text: str) -> int:
    match = re.search(r"parts_total:\s*`?(\d+)`?", readme_text)
    if not match:
        return -1
    return int(match.group(1))


def verify_transfer_integrity(
    *,
    repo_root: Path,
    review_root: Path,
    contract: dict[str, Any],
    required_files: list[str],
    transfer_result: dict[str, Any] | None,
) -> dict[str, Any]:
    expected_review_root = to_repo_rel(review_root, repo_root)
    step_id = review_root.name
    policy = contract.get("chatgpt_transfer_policy", {}) or {}
    step_prefixed_required = bool(policy.get("step_id_prefix_required", True))
    result: dict[str, Any] = {
        "status": "FAIL",
        "expected_review_root": expected_review_root,
        "manifest_review_root": "",
        "transfer_root": "",
        "manifest_transfer_root": "",
        "package_completeness": "",
        "core_required": None,
        "manifest_parts_total": 0,
        "computed_parts_total": 0,
        "parts_hard_limit": 15,
        "parts_hard_limit_pass": True,
        "upload_order_declared": [],
        "upload_order_computed": [],
        "upload_order_match": False,
        "section_flags_match": False,
        "readme_exists": False,
        "readme_parts_total": -1,
        "readme_upload_order_match": False,
        "required_entries_missing": [],
        "foreign_review_roots": [],
        "allowed_review_roots": [],
        "detected_review_roots": [],
        "entry_count": 0,
        "entrypoint_exists": False,
        "entrypoint_step_id_match": False,
        "entrypoint_matches_disk": False,
        "final_result_exists": False,
        "final_result_matches_manifest": False,
        "final_result_matches_disk": False,
        "final_result_mismatches": [],
        "seed_truth_audit_required": True,
        "seed_truth_audit_pass": False,
        "seed_family_claims": [],
        "seed_presence": {},
        "seed_claim_mismatches": [],
        "step_prefixed_naming_required": step_prefixed_required,
        "step_prefixed_naming_pass": False,
        "manifest_name_prefixed": False,
        "readme_name_prefixed": False,
        "all_part_names_prefixed": False,
        "error": "",
    }

    if not transfer_result or transfer_result.get("status") != "OK":
        result["error"] = "transfer_pack_not_ok"
        return result

    transfer_report = transfer_result.get("transfer_report", {}) if isinstance(transfer_result, dict) else {}
    transfer_root_rel = normalize_rel_path(str(transfer_report.get("transfer_root", "")))
    if not transfer_root_rel:
        transfer_root_rel = f"{expected_review_root}/chatgpt_transfer"
    transfer_root = (repo_root / transfer_root_rel).resolve()
    manifest_report_rel = normalize_rel_path(str(transfer_report.get("manifest_json", "")))
    if manifest_report_rel:
        manifest_path = (repo_root / manifest_report_rel).resolve()
    else:
        prefixed_manifest = transfer_root / f"{step_id}__chatgpt_transfer_manifest.json"
        legacy_manifest = transfer_root / "chatgpt_transfer_manifest.json"
        manifest_path = prefixed_manifest if prefixed_manifest.exists() else legacy_manifest
    if not manifest_path.exists():
        result["error"] = "transfer_manifest_missing"
        result["transfer_root"] = transfer_root_rel
        return result

    try:
        manifest = load_json(manifest_path)
    except Exception as exc:  # pragma: no cover - defensive guard
        result["error"] = f"transfer_manifest_parse_error:{exc}"
        result["transfer_root"] = transfer_root_rel
        return result

    manifest_review_root = normalize_rel_path(str(manifest.get("review_root", "")))
    result["manifest_review_root"] = manifest_review_root
    result["transfer_root"] = transfer_root_rel
    result["manifest_transfer_root"] = normalize_rel_path(str(manifest.get("transfer_root", "")))
    result["package_completeness"] = str(manifest.get("package_completeness", ""))
    result["core_required"] = bool(manifest.get("core_required", False))
    result["manifest_parts_total"] = int(manifest.get("parts_total", 0) or 0)

    sections = dict(manifest.get("sections", {}) or {})
    core = dict((sections.get("core", {}) or {}))
    visual = dict((sections.get("visual", {}) or {}))
    optional = dict((sections.get("optional", {}) or {}))
    parts = list(core.get("parts", []) or [])
    if not parts:
        result["error"] = "core_parts_missing"
        return result

    core_parts = sorted(parts, key=lambda item: int(item.get("part_index", 0) or 0))
    visual_parts = sorted(list((visual.get("parts", []) or [])), key=lambda item: int(item.get("part_index", 0) or 0))
    optional_parts = sorted(list((optional.get("parts", []) or [])), key=lambda item: int(item.get("part_index", 0) or 0))
    computed_upload_order = [str(item.get("part_name", "")) for item in [*core_parts, *visual_parts, *optional_parts] if str(item.get("part_name", "")).strip()]
    declared_upload_order = [str(item).strip() for item in list(manifest.get("upload_order", []) or []) if str(item).strip()]

    computed_parts_total = int(core.get("part_count", 0) or 0) + int(visual.get("part_count", 0) or 0) + int(optional.get("part_count", 0) or 0)
    result["computed_parts_total"] = computed_parts_total
    hard_cap = int(
        (
            manifest.get("parts_hard_limit")
            or policy.get("max_parts_hard_limit")
            or policy.get("max_parts_per_wave")
            or 15
        )
        or 15
    )
    result["parts_hard_limit"] = hard_cap
    result["parts_hard_limit_pass"] = computed_parts_total <= hard_cap
    result["upload_order_declared"] = declared_upload_order
    result["upload_order_computed"] = computed_upload_order
    result["upload_order_match"] = declared_upload_order == computed_upload_order

    visual_included = bool(manifest.get("visual_included", False))
    optional_included = bool(manifest.get("optional_included", False))
    visual_flag_match = visual_included == (int(visual.get("part_count", 0) or 0) > 0)
    optional_flag_match = optional_included == (int(optional.get("part_count", 0) or 0) > 0)
    result["section_flags_match"] = bool(visual_flag_match and optional_flag_match)

    readme_report_rel = normalize_rel_path(str(transfer_report.get("readme", "")))
    if readme_report_rel:
        readme_path = (repo_root / readme_report_rel).resolve()
    else:
        prefixed_readme = transfer_root / f"{step_id}__00_CHATGPT_TRANSFER_README.md"
        legacy_readme = transfer_root / "00_CHATGPT_TRANSFER_README.md"
        readme_path = prefixed_readme if prefixed_readme.exists() else legacy_readme
    result["readme_exists"] = readme_path.exists()
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8-sig")
        result["readme_parts_total"] = parse_readme_parts_total(readme_text)
        result["readme_upload_order_match"] = all(name in readme_text for name in declared_upload_order)

    prefix = f"{step_id}__"
    result["manifest_name_prefixed"] = manifest_path.name.startswith(prefix)
    result["readme_name_prefixed"] = readme_path.name.startswith(prefix)
    result["all_part_names_prefixed"] = all(name.startswith(prefix) for name in computed_upload_order)
    result["step_prefixed_naming_pass"] = bool(
        (not step_prefixed_required)
        or (
            result["manifest_name_prefixed"]
            and result["readme_name_prefixed"]
            and result["all_part_names_prefixed"]
        )
    )

    blob = bytearray()
    for part in core_parts:
        raw_part_path = str(part.get("part_path", "")).strip()
        if not raw_part_path:
            result["error"] = "core_part_path_missing"
            return result
        part_path = resolve_part_path(repo_root, raw_part_path)
        if not part_path.exists():
            result["error"] = f"core_part_missing:{normalize_rel_path(raw_part_path)}"
            return result
        blob.extend(part_path.read_bytes())

    try:
        with zipfile.ZipFile(io.BytesIO(bytes(blob)), "r") as zf:
            entries = sorted(name.replace("\\", "/").strip("/") for name in zf.namelist())
    except Exception as exc:  # pragma: no cover - defensive guard
        result["error"] = f"core_zip_parse_error:{exc}"
        return result

    result["entry_count"] = len(entries)
    entry_set = set(entries)
    required_entries = [f"{expected_review_root}/{name}" for name in required_files]
    missing_required = [name for name in required_entries if name not in entry_set]
    result["required_entries_missing"] = missing_required

    detected_review_roots: set[str] = set()
    for entry in entries:
        if not entry.startswith("docs/review_artifacts/"):
            continue
        parts_entry = entry.split("/")
        if len(parts_entry) >= 3:
            detected_review_roots.add("/".join(parts_entry[:3]))

    allowed_extra = [
        normalize_rel_path(str(item))
        for item in policy.get("allowed_review_roots_in_core", [])
        if normalize_rel_path(str(item))
    ]
    allowed_roots = {expected_review_root, *allowed_extra}
    foreign_roots = sorted(root for root in detected_review_roots if root not in allowed_roots)
    result["allowed_review_roots"] = sorted(allowed_roots)
    result["detected_review_roots"] = sorted(detected_review_roots)
    result["foreign_review_roots"] = foreign_roots

    claimed_families = [str(item).strip() for item in list(manifest.get("included_file_families", []) or []) if str(item).strip()]
    claims = set(claimed_families)
    has_for_chatgpt = any("/for_chatgpt/" in entry for entry in entries)
    has_for_codex = any("/for_codex/" in entry for entry in entries)
    has_seed_root = any(entry.startswith("docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/") for entry in entries)
    has_foundation_tracker = any(entry.endswith("ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/FOUNDATION_TRACKER.json") for entry in entries)
    has_mutable_tracker = any(entry.endswith("ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/MUTABLE_TRACKER.json") for entry in entries)
    has_trackers = bool(has_foundation_tracker and has_mutable_tracker)
    seed_presence = {
        "for_chatgpt_present": has_for_chatgpt,
        "for_codex_present": has_for_codex,
        "seed_capsule_root_present": has_seed_root,
        "foundation_tracker_present": has_foundation_tracker,
        "mutable_tracker_present": has_mutable_tracker,
        "trackers_present": has_trackers,
    }
    seed_mismatches: list[str] = []
    if "for_chatgpt" in claims and not has_for_chatgpt:
        seed_mismatches.append("claimed_for_chatgpt_but_missing")
    if "for_codex" in claims and not has_for_codex:
        seed_mismatches.append("claimed_for_codex_but_missing")
    if "seed_capsule_root" in claims and not has_seed_root:
        seed_mismatches.append("claimed_seed_capsule_root_but_missing")
    if "trackers" in claims and not has_trackers:
        seed_mismatches.append("claimed_trackers_but_missing_foundation_or_mutable_tracker")
    result["seed_family_claims"] = claimed_families
    result["seed_presence"] = seed_presence
    result["seed_claim_mismatches"] = seed_mismatches
    result["seed_truth_audit_pass"] = len(seed_mismatches) == 0

    entrypoint_rel = f"{expected_review_root}/00_REVIEW_ENTRYPOINT.md"
    result["entrypoint_exists"] = entrypoint_rel in entry_set
    if result["entrypoint_exists"]:
        with zipfile.ZipFile(io.BytesIO(bytes(blob)), "r") as zf:
            entrypoint_text = zf.read(entrypoint_rel).decode("utf-8", errors="replace")
        result["entrypoint_step_id_match"] = step_id in entrypoint_text
        disk_entrypoint = review_root / "00_REVIEW_ENTRYPOINT.md"
        if disk_entrypoint.exists():
            disk_text = disk_entrypoint.read_text(encoding="utf-8-sig")
            result["entrypoint_matches_disk"] = entrypoint_text.replace("\r\n", "\n") == disk_text.replace("\r\n", "\n")

    final_result_rel = f"{expected_review_root}/21_FINAL_RESULT.json"
    disk_final_result = review_root / "21_FINAL_RESULT.json"
    result["final_result_exists"] = final_result_rel in entry_set
    final_mismatches: list[str] = []
    if result["final_result_exists"]:
        with zipfile.ZipFile(io.BytesIO(bytes(blob)), "r") as zf:
            try:
                final_payload = json.loads(zf.read(final_result_rel).decode("utf-8", errors="replace"))
            except Exception:
                final_payload = {}
                final_mismatches.append("final_result_parse_error")
        if disk_final_result.exists():
            try:
                disk_payload = load_json(disk_final_result)
            except Exception:
                disk_payload = {}
            result["final_result_matches_disk"] = bool(final_payload and final_payload == disk_payload)
        checks = {
            "review_root": str(final_payload.get("review_root", "")) == expected_review_root,
            "transfer_package_completeness": str(final_payload.get("transfer_package_completeness", "")) == str(manifest.get("package_completeness", "")),
            "core_required": bool(final_payload.get("core_required", False)) == bool(manifest.get("core_required", False)),
            "parts_total": int(final_payload.get("parts_total", -1) or -1) == int(manifest.get("parts_total", 0) or 0),
            "optional_included": bool(final_payload.get("optional_included", False)) == bool(manifest.get("optional_included", False)),
            "visual_included": bool(final_payload.get("visual_included", False)) == bool(manifest.get("visual_included", False)),
            "upload_order": list(final_payload.get("upload_order", []) or []) == declared_upload_order,
        }
        for key, ok in checks.items():
            if not ok:
                final_mismatches.append(f"final_result_mismatch::{key}")
        result["final_result_matches_manifest"] = len(final_mismatches) == 0
    elif disk_final_result.exists():
        final_mismatches.append("final_result_missing_in_core")
    result["final_result_mismatches"] = final_mismatches

    checks_ok = (
        manifest_review_root == expected_review_root
        and normalize_rel_path(str(manifest.get("transfer_root", ""))) == transfer_root_rel
        and bool(manifest.get("core_required", False))
        and str(manifest.get("package_completeness", "")).upper() == "COMPLETE"
        and int(manifest.get("parts_total", 0) or 0) == computed_parts_total
        and result["parts_hard_limit_pass"]
        and result["upload_order_match"]
        and result["section_flags_match"]
        and result["readme_exists"]
        and result["readme_parts_total"] == int(manifest.get("parts_total", 0) or 0)
        and result["readme_upload_order_match"]
        and not missing_required
        and not foreign_roots
        and result["entrypoint_exists"]
        and result["entrypoint_step_id_match"]
        and result["entrypoint_matches_disk"]
        and result["final_result_exists"]
        and result["final_result_matches_manifest"]
        and result["final_result_matches_disk"]
        and not final_mismatches
        and result["seed_truth_audit_pass"]
        and result["step_prefixed_naming_pass"]
    )
    result["status"] = "PASS" if checks_ok else "FAIL"
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enforce IMPERIUM review-bundle output contract (12 files + 10MB split + retention check)."
    )
    parser.add_argument("--review-root", required=True, help="Review root under docs/review_artifacts/<step_folder>.")
    parser.add_argument("--archive", action="append", default=[], help="Archive path to split into 10MB parts.")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT, help="Contract json path.")
    parser.add_argument("--retention-check", action="store_true", help="Run TTL janitor in dry-run mode.")
    parser.add_argument("--retention-apply", action="store_true", help="Run TTL janitor in apply mode.")
    parser.add_argument("--skip-chatgpt-transfer", action="store_true", help="Skip auto build of chatgpt_transfer package.")
    return parser.parse_args()


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
    review_root.mkdir(parents=True, exist_ok=True)

    required_files = [str(x).strip() for x in contract.get("required_review_files", []) if str(x).strip()]
    present_files: list[str] = []
    missing_files: list[str] = []
    for name in required_files:
        target = review_root / name
        if target.exists() and target.is_file():
            present_files.append(name)
        else:
            missing_files.append(name)

    archive_policy = contract.get("archive_split_policy", {}) or {}
    split_enabled = bool(archive_policy.get("enabled", True))
    part_size_mb = int(archive_policy.get("part_size_mb", 10) or 10)
    part_size_bytes = part_size_mb * 1024 * 1024

    archive_results: list[dict[str, Any]] = []
    if split_enabled:
        for raw in args.archive:
            archive_path = Path(raw).expanduser()
            if not archive_path.is_absolute():
                archive_path = (repo_root / archive_path).resolve()
            archive_results.append(split_archive(archive_path, part_size_bytes))

    janitor_result: dict[str, Any] | None = None
    if args.retention_apply:
        janitor_result = run_ttl_janitor(repo_root, apply_mode=True)
    elif args.retention_check:
        janitor_result = run_ttl_janitor(repo_root, apply_mode=False)

    transfer_result: dict[str, Any] | None = None
    if not args.skip_chatgpt_transfer:
        transfer_result = run_chatgpt_transfer_pack(repo_root, review_root, contract_path)

    transport_integrity = verify_transfer_integrity(
        repo_root=repo_root,
        review_root=review_root,
        contract=contract,
        required_files=required_files,
        transfer_result=transfer_result,
    )

    verdict = "PASS"
    if missing_files:
        verdict = "FAIL_MISSING_REQUIRED_REVIEW_FILES"
    if any(item.get("status") not in {"SPLIT_OK", "EMPTY_ARCHIVE"} for item in archive_results):
        verdict = "PARTIAL_ARCHIVE_SPLIT"
    if janitor_result and janitor_result.get("status") != "OK":
        verdict = "PARTIAL_RETENTION_CHECK"
    if transfer_result and transfer_result.get("status") != "OK":
        verdict = "PARTIAL_CHATGPT_TRANSFER"
    if transfer_result and transport_integrity.get("status") != "PASS":
        verdict = "PARTIAL_TRANSPORT_MISMATCH"

    report = {
        "schema_version": "imperium_bundle_output_enforcement.v1",
        "generated_at_utc": utc_now_iso(),
        "contract_path": normalize_rel(contract_path, repo_root),
        "review_root": normalize_rel(review_root, repo_root),
        "required_review_files_count": len(required_files),
        "present_review_files_count": len(present_files),
        "missing_review_files_count": len(missing_files),
        "present_review_files": present_files,
        "missing_review_files": missing_files,
        "archive_split": {
            "enabled": split_enabled,
            "part_size_mb": part_size_mb,
            "archive_count": len(archive_results),
            "results": archive_results,
        },
        "retention": {
            "executed": bool(janitor_result),
            "apply_mode": bool(args.retention_apply),
            "result": janitor_result or {},
        },
        "chatgpt_transfer": {
            "executed": transfer_result is not None,
            "result": transfer_result or {},
            "transport_integrity": transport_integrity,
        },
        "verdict": verdict,
    }

    report_json = review_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json"
    report_md = review_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.md"
    write_json(report_json, report)

    lines = [
        "# IMPERIUM Bundle Output Enforcement Report",
        "",
        f"- generated_at_utc: `{report['generated_at_utc']}`",
        f"- review_root: `{report['review_root']}`",
        f"- verdict: `{verdict}`",
        f"- required_review_files: `{len(required_files)}`",
        f"- present_review_files: `{len(present_files)}`",
        f"- missing_review_files: `{len(missing_files)}`",
        "",
        "## Missing Review Files",
    ]
    if missing_files:
        lines.extend([f"- `{name}`" for name in missing_files])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Archive Split",
            f"- enabled: `{split_enabled}`",
            f"- part_size_mb: `{part_size_mb}`",
            f"- archive_count: `{len(archive_results)}`",
        ]
    )
    for item in archive_results:
        lines.extend(
            [
                f"- archive: `{item.get('archive')}`",
                f"  - status: `{item.get('status')}`",
                f"  - part_count: `{item.get('part_count', 0)}`",
                f"  - parts_dir: `{item.get('parts_dir', '')}`",
            ]
        )

    lines.extend(["", "## Retention"])
    if janitor_result:
        lines.extend(
            [
                f"- executed: `true`",
                f"- apply_mode: `{str(bool(args.retention_apply)).lower()}`",
                f"- status: `{janitor_result.get('status', 'UNKNOWN')}`",
                f"- command: `{janitor_result.get('command', '')}`",
            ]
        )
    else:
        lines.append("- executed: `false`")

    lines.extend(["", "## ChatGPT Transfer"])
    if transfer_result:
        transfer_report = transfer_result.get("transfer_report", {}) if isinstance(transfer_result, dict) else {}
        lines.extend(
            [
                "- executed: `true`",
                f"- status: `{transfer_result.get('status', 'UNKNOWN')}`",
                f"- command: `{transfer_result.get('command', '')}`",
                f"- transfer_root: `{transfer_report.get('transfer_root', '')}`",
                f"- mode: `{transfer_report.get('mode', '')}`",
                f"- part_count: `{transfer_report.get('part_count', transfer_report.get('total_part_count', ''))}`",
                f"- transport_integrity: `{transport_integrity.get('status', 'UNKNOWN')}`",
                f"- expected_review_root: `{transport_integrity.get('expected_review_root', '')}`",
                f"- manifest_review_root: `{transport_integrity.get('manifest_review_root', '')}`",
                f"- manifest_transfer_root: `{transport_integrity.get('manifest_transfer_root', '')}`",
                f"- manifest_parts_total: `{transport_integrity.get('manifest_parts_total', 0)}`",
                f"- computed_parts_total: `{transport_integrity.get('computed_parts_total', 0)}`",
                f"- parts_hard_limit: `{transport_integrity.get('parts_hard_limit', 15)}`",
                f"- parts_hard_limit_pass: `{str(bool(transport_integrity.get('parts_hard_limit_pass', False))).lower()}`",
                f"- upload_order_match: `{str(bool(transport_integrity.get('upload_order_match', False))).lower()}`",
                f"- section_flags_match: `{str(bool(transport_integrity.get('section_flags_match', False))).lower()}`",
                f"- readme_exists: `{str(bool(transport_integrity.get('readme_exists', False))).lower()}`",
                f"- readme_parts_total: `{transport_integrity.get('readme_parts_total', -1)}`",
                f"- readme_upload_order_match: `{str(bool(transport_integrity.get('readme_upload_order_match', False))).lower()}`",
                f"- step_prefixed_naming_pass: `{str(bool(transport_integrity.get('step_prefixed_naming_pass', False))).lower()}`",
                f"- manifest_name_prefixed: `{str(bool(transport_integrity.get('manifest_name_prefixed', False))).lower()}`",
                f"- readme_name_prefixed: `{str(bool(transport_integrity.get('readme_name_prefixed', False))).lower()}`",
                f"- all_part_names_prefixed: `{str(bool(transport_integrity.get('all_part_names_prefixed', False))).lower()}`",
                f"- seed_truth_audit_pass: `{str(bool(transport_integrity.get('seed_truth_audit_pass', False))).lower()}`",
                f"- seed_claim_mismatches: `{len(transport_integrity.get('seed_claim_mismatches', []) or [])}`",
                f"- entrypoint_matches_disk: `{str(bool(transport_integrity.get('entrypoint_matches_disk', False))).lower()}`",
                f"- final_result_matches_manifest: `{str(bool(transport_integrity.get('final_result_matches_manifest', False))).lower()}`",
                f"- final_result_matches_disk: `{str(bool(transport_integrity.get('final_result_matches_disk', False))).lower()}`",
                f"- final_result_mismatches: `{len(transport_integrity.get('final_result_mismatches', []) or [])}`",
                f"- required_entries_missing: `{len(transport_integrity.get('required_entries_missing', []) or [])}`",
                f"- foreign_review_roots: `{len(transport_integrity.get('foreign_review_roots', []) or [])}`",
            ]
        )
    else:
        lines.append("- executed: `false`")

    write_text(report_md, "\n".join(lines))

    print(
        json.dumps(
            {
                "status": "ok",
                "verdict": verdict,
                "review_root": normalize_rel(review_root, repo_root),
                "report_json": normalize_rel(report_json, repo_root),
                "report_md": normalize_rel(report_md, repo_root),
                "missing_review_files_count": len(missing_files),
                "archive_split_count": len(archive_results),
                "retention_executed": bool(janitor_result),
                "chatgpt_transfer_executed": transfer_result is not None,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
