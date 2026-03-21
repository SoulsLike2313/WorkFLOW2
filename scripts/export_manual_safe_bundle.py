#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTRACT_PATH = "workspace_config/bundle_fallback_contract.json"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_now_stamp(fmt: str) -> str:
    return datetime.now(timezone.utc).strftime(fmt)


def normalize_rel(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.strip("/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_include_file(path: Path) -> list[str]:
    items: list[str] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("* "):
            line = line[2:].strip()
        if line:
            items.append(line)
    return items


def run_git(repo_root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def is_subpath(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def compile_patterns(raw_patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(item, re.IGNORECASE) for item in raw_patterns]


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in {
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".py",
        ".ps1",
        ".js",
        ".ts",
        ".css",
        ".html",
        ".xml",
        ".csv",
        ".ini",
        ".cfg",
    }


def path_block_reason(
    rel_path: str,
    *,
    deny_path_patterns: list[re.Pattern[str]],
    runtime_allowlist: set[str],
) -> str | None:
    normalized = normalize_rel(rel_path)
    if normalized.startswith("runtime/") and normalized not in runtime_allowlist:
        return "runtime_path_not_in_manual_allowlist"
    for pattern in deny_path_patterns:
        if pattern.search(normalized):
            return f"path_policy_block:{pattern.pattern}"
    return None


def content_block_reason(
    full_path: Path,
    *,
    deny_content_patterns: list[re.Pattern[str]],
    max_text_scan_bytes: int,
) -> str | None:
    if not is_text_file(full_path):
        return None
    try:
        if full_path.stat().st_size > max_text_scan_bytes:
            return None
    except OSError:
        return None
    try:
        text = full_path.read_text(encoding="utf-8")
    except Exception:
        return None
    for pattern in deny_content_patterns:
        if pattern.search(text):
            return f"content_policy_block:{pattern.pattern}"
    return None


def iter_files_for_request(repo_root: Path, rel_path: str) -> tuple[list[str], str | None]:
    full_path = (repo_root / rel_path).resolve()
    if not is_subpath(full_path, repo_root):
        return [], "outside_repo_root"
    if not full_path.exists():
        return [], "not_found"
    if full_path.is_file():
        return [normalize_rel(rel_path)], None
    files: list[str] = []
    for item in sorted(full_path.rglob("*")):
        if item.is_file():
            files.append(normalize_rel(str(item.relative_to(repo_root))))
    if not files:
        return [], "directory_has_no_files"
    return files, None


def write_markdown_list(title: str, items: list[str]) -> list[str]:
    lines = [title]
    if not items:
        lines.append("- none")
    else:
        for item in items:
            lines.append(f"- `{item}`")
    lines.append("")
    return lines


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build manual-safe staged bundle when default exporter is insufficient.")
    p.add_argument("--topic", required=True, help="Bundle topic slug (for name prefix).")
    p.add_argument("--include", nargs="*", default=[], help="Repo-relative files or directories.")
    p.add_argument("--include-file", help="Optional text file with repo-relative include paths.")
    p.add_argument("--summary", default="", help="Optional one-line bundle summary.")
    p.add_argument(
        "--fallback-trigger",
        nargs="*",
        default=[],
        help="Optional trigger labels (for manifest/report transparency).",
    )
    p.add_argument("--contract", default=DEFAULT_CONTRACT_PATH, help="Path to fallback contract JSON.")
    p.add_argument("--output-dir", default="", help="Optional override for zip output directory.")
    p.add_argument("--staging-root", default="", help="Optional override for staging root.")
    p.add_argument("--dry-run", action="store_true", help="Evaluate policy and produce summary without writing files.")
    return p


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()

    contract_path = Path(args.contract).expanduser()
    if not contract_path.is_absolute():
        contract_path = (repo_root / contract_path).resolve()
    if not contract_path.exists():
        raise SystemExit(f"contract file not found: {contract_path}")

    contract = load_json(contract_path)
    safe_mode = contract.get("safe_mode", {})
    deny_path_patterns = compile_patterns(list(safe_mode.get("deny_path_patterns", [])))
    deny_content_patterns = compile_patterns(list(safe_mode.get("deny_content_patterns", [])))
    runtime_allowlist = {normalize_rel(item) for item in safe_mode.get("runtime_allowlist_paths", [])}
    max_text_scan_bytes = int(safe_mode.get("max_text_scan_bytes", 1_000_000))

    default_paths = contract.get("default_paths", {})
    output_dir_raw = args.output_dir or str(default_paths.get("export_root", "runtime/chatgpt_bundle_exports"))
    staging_root_raw = args.staging_root or str(default_paths.get("staging_root", "runtime/manual_safe_bundle_staging"))
    output_dir = Path(output_dir_raw).expanduser()
    staging_root = Path(staging_root_raw).expanduser()
    if not output_dir.is_absolute():
        output_dir = (repo_root / output_dir).resolve()
    if not staging_root.is_absolute():
        staging_root = (repo_root / staging_root).resolve()

    include_paths = list(args.include)
    if args.include_file:
        include_file = Path(args.include_file).expanduser()
        if not include_file.is_absolute():
            include_file = (repo_root / include_file).resolve()
        if not include_file.exists():
            raise SystemExit(f"include file not found: {include_file}")
        include_paths.extend(parse_include_file(include_file))

    requested = [normalize_rel(item) for item in include_paths if normalize_rel(item)]
    requested = list(dict.fromkeys(requested))
    if not requested:
        raise SystemExit("no include paths provided; use --include and/or --include-file")

    naming = contract.get("naming", {})
    timestamp_format = str(naming.get("timestamp_format_utc", "%Y%m%dT%H%M%SZ"))
    timestamp = utc_now_stamp(timestamp_format)
    topic = re.sub(r"[^a-zA-Z0-9._-]+", "_", args.topic.strip()).strip("_") or "manual_safe"
    bundle_name = f"{topic}_manual_safe_bundle_{timestamp}"

    included_set: set[str] = set()
    skipped: list[dict[str, str]] = []
    blocked: list[dict[str, str]] = []

    for req in requested:
        request_block = path_block_reason(
            req,
            deny_path_patterns=deny_path_patterns,
            runtime_allowlist=runtime_allowlist,
        )
        if request_block:
            blocked.append({"path": req, "reason": request_block})
            continue

        candidates, request_error = iter_files_for_request(repo_root, req)
        if request_error:
            skipped.append({"path": req, "reason": request_error})
            continue

        for rel in candidates:
            block = path_block_reason(
                rel,
                deny_path_patterns=deny_path_patterns,
                runtime_allowlist=runtime_allowlist,
            )
            if block:
                blocked.append({"path": rel, "reason": block})
                continue
            full = (repo_root / rel).resolve()
            content_block = content_block_reason(
                full,
                deny_content_patterns=deny_content_patterns,
                max_text_scan_bytes=max_text_scan_bytes,
            )
            if content_block:
                blocked.append({"path": rel, "reason": content_block})
                continue
            included_set.add(rel)

    included = sorted(included_set)
    skipped = sorted(skipped, key=lambda x: (x["path"], x["reason"]))
    blocked = sorted(blocked, key=lambda x: (x["path"], x["reason"]))

    safe_share_verdict = "SAFE TO SHARE" if included else "BLOCKED"
    if included and blocked:
        safe_share_verdict = "SAFE TO SHARE WITH EXCLUSIONS"

    git_branch = run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    git_head = run_git(repo_root, ["rev-parse", "HEAD"]) or "unknown"

    required_bundle_files = list(contract.get("required_bundle_files", []))
    payload_root_name = str(contract.get("required_payload_root", "exported"))

    manifest_payload: dict[str, Any] = {
        "schema_version": "manual_safe_bundle_manifest.v1",
        "bundle_name": bundle_name,
        "topic": topic,
        "generated_at": utc_now_iso(),
        "contract_version": contract.get("contract_version", "unknown"),
        "contract_path": normalize_rel(str(contract_path.relative_to(repo_root))),
        "repo_root": str(repo_root),
        "git_branch": git_branch,
        "git_head": git_head,
        "fallback_triggers": list(dict.fromkeys(args.fallback_trigger)),
        "requested_paths": requested,
        "included_files": included,
        "skipped_files": skipped,
        "blocked_files": blocked,
        "required_bundle_files": required_bundle_files,
        "required_payload_root": payload_root_name,
        "safe_share_verdict": safe_share_verdict,
        "safe_to_share_with_chatgpt": safe_share_verdict != "BLOCKED",
        "counts": {
            "requested": len(requested),
            "included": len(included),
            "skipped": len(skipped),
            "blocked": len(blocked),
        },
    }

    summary_text = args.summary.strip() or (
        "Manual-safe fallback bundle assembled from explicit include scope with policy-safe filtering."
    )

    summary_lines = [
        "# Bundle Summary",
        "",
        f"- bundle_name: `{bundle_name}`",
        f"- topic: `{topic}`",
        f"- generated_at: `{manifest_payload['generated_at']}`",
        f"- safe_share_verdict: `{safe_share_verdict}`",
        f"- SAFE TO SHARE WITH CHATGPT: `{'YES' if manifest_payload['safe_to_share_with_chatgpt'] else 'NO'}`",
        "",
        "## Summary",
        f"- {summary_text}",
        "",
        "## Counts",
        f"- requested: `{len(requested)}`",
        f"- included: `{len(included)}`",
        f"- skipped: `{len(skipped)}`",
        f"- blocked: `{len(blocked)}`",
    ]
    if args.fallback_trigger:
        summary_lines.extend(["", "## Fallback Triggers"])
        summary_lines.extend([f"- `{item}`" for item in args.fallback_trigger])
    summary_lines.append("")
    summary_md = "\n".join(summary_lines) + "\n"

    reading_order_lines = [
        "# Bundle Reading Order",
        "",
        "1. `bundle_summary.md`",
        "2. `bundle_include_manifest.json`",
        "3. `bundle_exclusions.md`",
        "4. `manual_safe_export_report.md`",
        "5. `exported/` payload files (domain docs/contracts/scripts)",
        "",
        "## Payload Quick List",
    ]
    reading_order_lines.extend([f"- `{item}`" for item in included[:30]] or ["- none"])
    if len(included) > 30:
        reading_order_lines.append(f"- ... +{len(included) - 30} more")
    reading_order_lines.append("")
    reading_order_md = "\n".join(reading_order_lines) + "\n"

    exclusion_lines = ["# Bundle Exclusions", ""]
    exclusion_lines.extend(write_markdown_list("## Skipped Paths", [f"{x['path']} ({x['reason']})" for x in skipped]))
    exclusion_lines.extend(write_markdown_list("## Blocked Paths", [f"{x['path']} ({x['reason']})" for x in blocked]))
    exclusion_lines.extend(
        [
            "## Note",
            "- blocked/skipped items are documented for transparency and are not packed into payload.",
            "- protected/local-sovereign artifacts remain excluded by policy.",
            "",
        ]
    )
    exclusions_md = "\n".join(exclusion_lines)

    report_lines = [
        "# Manual Safe Export Report",
        "",
        f"- bundle_name: `{bundle_name}`",
        f"- generated_at: `{manifest_payload['generated_at']}`",
        f"- git_branch: `{git_branch}`",
        f"- git_head: `{git_head}`",
        f"- fallback_contract: `{manifest_payload['contract_path']}`",
        "",
        "## Fallback Basis",
        "- manual-safe fallback is canonical path when default exporter is insufficient.",
        "- safe-mode policy is applied to every requested candidate before packing.",
        "",
        "## Result",
        f"- safe_share_verdict: `{safe_share_verdict}`",
        f"- SAFE TO SHARE WITH CHATGPT: `{'YES' if manifest_payload['safe_to_share_with_chatgpt'] else 'NO'}`",
        f"- included_files: `{len(included)}`",
        f"- skipped_files: `{len(skipped)}`",
        f"- blocked_files: `{len(blocked)}`",
    ]
    if args.fallback_trigger:
        report_lines.extend(["", "## Trigger Labels"])
        report_lines.extend([f"- `{item}`" for item in args.fallback_trigger])
    report_lines.append("")
    report_md = "\n".join(report_lines) + "\n"

    if args.dry_run:
        print(json.dumps(manifest_payload, ensure_ascii=False, indent=2))
        return 0 if included else 1

    staging_bundle_root = staging_root / bundle_name
    output_dir.mkdir(parents=True, exist_ok=True)
    if staging_bundle_root.exists():
        shutil.rmtree(staging_bundle_root)
    (staging_bundle_root / payload_root_name).mkdir(parents=True, exist_ok=True)

    for rel in included:
        src = repo_root / rel
        dst = staging_bundle_root / payload_root_name / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    (staging_bundle_root / "bundle_include_manifest.json").write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (staging_bundle_root / "bundle_summary.md").write_text(summary_md, encoding="utf-8")
    (staging_bundle_root / "bundle_reading_order.md").write_text(reading_order_md, encoding="utf-8")
    (staging_bundle_root / "bundle_exclusions.md").write_text(exclusions_md, encoding="utf-8")
    (staging_bundle_root / "manual_safe_export_report.md").write_text(report_md, encoding="utf-8")

    zip_path = output_dir / f"{bundle_name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(staging_bundle_root.rglob("*")):
            if file_path.is_file():
                archive.write(
                    file_path,
                    arcname=str(Path(bundle_name) / file_path.relative_to(staging_bundle_root)),
                )

    result = {
        "bundle_name": bundle_name,
        "bundle_staging_path": str(staging_bundle_root),
        "bundle_zip_path": str(zip_path),
        "safe_share_verdict": safe_share_verdict,
        "safe_to_share_with_chatgpt": manifest_payload["safe_to_share_with_chatgpt"],
        "included_files_count": len(included),
        "skipped_files_count": len(skipped),
        "blocked_files_count": len(blocked),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if included else 1


if __name__ == "__main__":
    raise SystemExit(main())
