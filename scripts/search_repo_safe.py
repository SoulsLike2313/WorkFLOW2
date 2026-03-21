#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = "workspace_config/search_zone_manifest.json"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_rel(path: str) -> str:
    value = path.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.strip("/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def compile_patterns(values: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(item, re.IGNORECASE) for item in values]


def is_subpath(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def should_block(rel_path: str, patterns: list[re.Pattern[str]]) -> str | None:
    normalized = normalize_rel(rel_path)
    for pattern in patterns:
        if pattern.search(normalized):
            return pattern.pattern
    return None


def gather_files(
    repo_root: Path,
    requested_paths: list[str],
    *,
    disallowed_patterns: list[re.Pattern[str]],
    allowed_exts: set[str],
    max_files: int,
) -> tuple[list[str], list[dict[str, str]], bool]:
    files: list[str] = []
    skipped: list[dict[str, str]] = []
    limit_hit = False

    for raw in requested_paths:
        rel = normalize_rel(raw)
        if not rel:
            continue
        block_reason = should_block(rel, disallowed_patterns)
        if block_reason:
            skipped.append({"path": rel, "reason": f"blocked_path_pattern:{block_reason}"})
            continue
        full = (repo_root / rel).resolve()
        if not is_subpath(full, repo_root):
            skipped.append({"path": rel, "reason": "outside_repo_root"})
            continue
        if not full.exists():
            skipped.append({"path": rel, "reason": "not_found"})
            continue

        if full.is_file():
            ext = full.suffix.lower()
            if ext and ext not in allowed_exts:
                skipped.append({"path": rel, "reason": f"extension_not_allowed:{ext}"})
                continue
            files.append(rel)
            if len(files) >= max_files:
                limit_hit = True
                break
            continue

        for item in sorted(full.rglob("*")):
            if not item.is_file():
                continue
            rel_item = normalize_rel(str(item.relative_to(repo_root)))
            block_item = should_block(rel_item, disallowed_patterns)
            if block_item:
                skipped.append({"path": rel_item, "reason": f"blocked_path_pattern:{block_item}"})
                continue
            ext = item.suffix.lower()
            if ext and ext not in allowed_exts:
                continue
            files.append(rel_item)
            if len(files) >= max_files:
                limit_hit = True
                break
        if limit_hit:
            break

    deduped = sorted(set(files))
    return deduped, skipped, limit_hit


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Policy-safe bounded repo search fallback.")
    p.add_argument("--query", help="Search query (substring by default).")
    p.add_argument("--regex", action="store_true", help="Treat query as regex.")
    p.add_argument("--case-sensitive", action="store_true", help="Case-sensitive search.")
    p.add_argument("--zone", nargs="*", default=[], help="Zone id(s) from search_zone_manifest.")
    p.add_argument("--path", nargs="*", default=[], help="Additional repo-relative file/dir path(s).")
    p.add_argument("--include-secondary", action="store_true", help="Allow SECONDARY zones.")
    p.add_argument("--include-heavy", action="store_true", help="Allow heavy staged-reading surfaces.")
    p.add_argument("--max-files", type=int, default=0, help="Override max files scan budget.")
    p.add_argument("--max-results", type=int, default=0, help="Override max result count.")
    p.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Search zone manifest path.")
    p.add_argument("--json-only", action="store_true", help="Emit JSON only.")
    p.add_argument("--show-zones", action="store_true", help="Print available zones and exit.")
    return p


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()

    manifest_path = Path(args.manifest).expanduser()
    if not manifest_path.is_absolute():
        manifest_path = (repo_root / manifest_path).resolve()
    if not manifest_path.exists():
        raise SystemExit(f"manifest file not found: {manifest_path}")

    manifest = load_json(manifest_path)
    zone_entries = manifest.get("zones", [])
    zone_map = {str(item.get("zone_id", "")).strip(): item for item in zone_entries if item.get("zone_id")}

    if args.show_zones:
        payload = {
            "manifest": normalize_rel(str(manifest_path.relative_to(repo_root))),
            "zones": sorted(zone_map.keys()),
            "default_search_zone_order": manifest.get("default_search_zone_order", []),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not args.query:
        raise SystemExit("--query is required unless --show-zones is used")

    safe_policy = manifest.get("safe_search_policy", {})
    disallowed_patterns = compile_patterns(list(safe_policy.get("disallowed_path_patterns", [])))
    allowed_exts = {str(item).lower() for item in safe_policy.get("allowed_text_extensions", [])}
    max_files = int(args.max_files or safe_policy.get("default_max_files", 1500))
    max_results = int(args.max_results or safe_policy.get("default_max_results", 200))
    heavy_surfaces = {normalize_rel(item) for item in manifest.get("heavy_staged_reading_surfaces", [])}
    default_zone_order = [str(item) for item in manifest.get("default_search_zone_order", [])]

    selected_zones = list(args.zone) if args.zone else default_zone_order
    requested_paths: list[str] = []
    blocked_zones: list[dict[str, str]] = []

    for zone_id in selected_zones:
        zone = zone_map.get(zone_id)
        if not zone:
            blocked_zones.append({"zone": zone_id, "reason": "zone_not_found"})
            continue
        classification = str(zone.get("classification", "")).upper()
        if classification.startswith("SECONDARY") and not args.include_secondary:
            blocked_zones.append({"zone": zone_id, "reason": "secondary_zone_requires_include_secondary"})
            continue
        for item in zone.get("paths", []):
            rel = normalize_rel(str(item))
            if not args.include_heavy and rel in heavy_surfaces:
                blocked_zones.append({"zone": zone_id, "reason": f"heavy_path_requires_include_heavy:{rel}"})
                continue
            requested_paths.append(rel)

    for raw in args.path:
        rel = normalize_rel(raw)
        if rel:
            requested_paths.append(rel)

    requested_paths = list(dict.fromkeys(requested_paths))
    if not requested_paths:
        payload = {
            "verdict": "BLOCKED",
            "reason": "no_paths_after_zone_filters",
            "blocked_zones": blocked_zones,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    files, skipped_paths, limit_hit = gather_files(
        repo_root,
        requested_paths,
        disallowed_patterns=disallowed_patterns,
        allowed_exts=allowed_exts,
        max_files=max_files,
    )

    flags = 0 if args.case_sensitive else re.IGNORECASE
    if args.regex:
        try:
            matcher = re.compile(args.query, flags)
        except re.error as err:
            raise SystemExit(f"invalid regex query: {err}")
    else:
        q = args.query if args.case_sensitive else args.query.lower()

        def matcher_fn(text: str) -> bool:
            content = text if args.case_sensitive else text.lower()
            return q in content

        matcher = matcher_fn

    matches: list[dict[str, Any]] = []
    files_scanned = 0
    scan_errors: list[dict[str, str]] = []

    for rel in files:
        full = (repo_root / rel).resolve()
        files_scanned += 1
        try:
            lines = full.read_text(encoding="utf-8").splitlines()
        except Exception as err:
            scan_errors.append({"path": rel, "error": str(err)})
            continue
        for idx, line in enumerate(lines, start=1):
            hit = bool(matcher.search(line)) if args.regex else bool(matcher(line))
            if not hit:
                continue
            matches.append({"path": rel, "line": idx, "text": line.strip()[:400]})
            if len(matches) >= max_results:
                break
        if len(matches) >= max_results:
            break

    result = {
        "verdict": "PASS" if matches else "PASS_NO_MATCH",
        "query": args.query,
        "query_mode": "regex" if args.regex else "substring",
        "case_sensitive": args.case_sensitive,
        "manifest_path": normalize_rel(str(manifest_path.relative_to(repo_root))),
        "zones_requested": selected_zones,
        "paths_requested": requested_paths,
        "blocked_zones": blocked_zones,
        "paths_skipped": skipped_paths,
        "files_scanned": files_scanned,
        "files_scan_limit_hit": limit_hit,
        "matches_count": len(matches),
        "max_results": max_results,
        "matches": matches,
        "scan_errors": scan_errors,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
