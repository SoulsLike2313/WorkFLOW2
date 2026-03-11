from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = PROJECT_ROOT / "runtime" / "ui_snapshots"
VALIDATION_ROOT = PROJECT_ROOT / "runtime" / "ui_validation"
COMPARE_ROOT = PROJECT_ROOT / "runtime" / "ui_compare"


@dataclass(frozen=True)
class ShotKey:
    page: str
    size: str
    scale: str
    source: str

    def as_dict(self) -> dict[str, str]:
        return {
            "page": self.page,
            "size": self.size,
            "scale": self.scale,
            "source": self.source,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "ui_screenshots_manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _resolve_run_dir(kind: str, run_id_or_path: str) -> tuple[Path, str]:
    candidate = Path(run_id_or_path)
    if candidate.exists() and candidate.is_dir():
        return candidate.resolve(), "custom"

    if kind == "snapshots":
        run_dir = SNAPSHOT_ROOT / run_id_or_path
        return run_dir.resolve(), kind
    if kind == "validation":
        run_dir = VALIDATION_ROOT / run_id_or_path
        return run_dir.resolve(), kind

    snapshot_dir = SNAPSHOT_ROOT / run_id_or_path
    validation_dir = VALIDATION_ROOT / run_id_or_path
    if snapshot_dir.exists():
        return snapshot_dir.resolve(), "snapshots"
    if validation_dir.exists():
        return validation_dir.resolve(), "validation"
    raise FileNotFoundError(
        f"Run '{run_id_or_path}' was not found in snapshots or validation roots."
    )


def _build_key(entry: dict[str, Any], include_source: bool) -> ShotKey:
    page = str(entry.get("page", "unknown"))
    size = str(entry.get("size", "unknown"))
    scale = str(entry.get("scale", "unknown"))
    source = str(entry.get("source", "snapshot")) if include_source else "any"
    return ShotKey(page=page, size=size, scale=scale, source=source)


def _parse_filter(raw: str) -> set[str]:
    values = {token.strip() for token in raw.split(",") if token.strip()}
    return values


def _render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# UI Compare Summary",
        "",
        f"- Compare run id: `{payload.get('compare_run_id')}`",
        f"- Status: `{payload.get('status')}`",
        f"- Base run: `{payload.get('base', {}).get('run_id')}` ({payload.get('base', {}).get('kind')})",
        f"- Target run: `{payload.get('target', {}).get('run_id')}` ({payload.get('target', {}).get('kind')})",
        "",
        "## Totals",
        "",
    ]
    totals = payload.get("totals", {})
    lines.append(f"- base entries: {totals.get('base_entries', 0)}")
    lines.append(f"- target entries: {totals.get('target_entries', 0)}")
    lines.append(f"- compared entries: {totals.get('compared_entries', 0)}")
    lines.append(f"- changed entries: {totals.get('changed_entries', 0)}")
    lines.append(f"- added entries: {totals.get('added_entries', 0)}")
    lines.append(f"- removed entries: {totals.get('removed_entries', 0)}")
    lines.append(f"- unknown hash entries: {totals.get('unknown_hash_entries', 0)}")
    lines.append("")

    changed_pages = payload.get("changed_pages", [])
    lines.append("## Changed Pages")
    lines.append("")
    if changed_pages:
        for page in changed_pages:
            lines.append(f"- {page}")
    else:
        lines.append("- none")
    lines.append("")

    page_details = payload.get("page_summary", {})
    lines.append("## Per Page Summary")
    lines.append("")
    if page_details:
        for page, details in page_details.items():
            lines.append(
                f"- {page}: changed={details.get('changed', 0)}, added={details.get('added', 0)}, "
                f"removed={details.get('removed', 0)}, unknown={details.get('unknown', 0)}"
            )
    else:
        lines.append("- no page details")

    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    artifacts = payload.get("artifacts", {})
    for key, value in artifacts.items():
        lines.append(f"- {key}: `{value}`")

    return "\n".join(lines).strip() + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two UI run manifests/screenshots and show changed pages."
    )
    parser.add_argument("--base-run", required=True, help="Base run_id or absolute run directory path.")
    parser.add_argument("--target-run", required=True, help="Target run_id or absolute run directory path.")
    parser.add_argument(
        "--kind",
        choices=("auto", "snapshots", "validation"),
        default="auto",
        help="Where to search for run_id folders.",
    )
    parser.add_argument("--pages", default="", help="Optional comma-separated page filter.")
    parser.add_argument("--sizes", default="", help="Optional comma-separated size filter (e.g. 1540x920).")
    parser.add_argument("--scales", default="", help="Optional comma-separated scale filter (e.g. 1.0,1.25).")
    parser.add_argument(
        "--ignore-source",
        action="store_true",
        help="Do not include screenshot source in compare key.",
    )
    parser.add_argument(
        "--output-dir",
        default="runtime/ui_compare",
        help="Output folder for compare artifacts.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    compare_started_at = _now_iso()
    compare_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        base_dir, base_kind = _resolve_run_dir(args.kind, args.base_run)
        target_dir, target_kind = _resolve_run_dir(args.kind, args.target_run)
    except FileNotFoundError as exc:
        print(str(exc))
        return 2

    try:
        base_manifest = _load_manifest(base_dir)
        target_manifest = _load_manifest(target_dir)
    except FileNotFoundError as exc:
        print(str(exc))
        return 2

    base_list = base_manifest.get("screenshots", [])
    target_list = target_manifest.get("screenshots", [])
    if not isinstance(base_list, list) or not isinstance(target_list, list):
        print("Invalid manifest format: screenshots must be a list.")
        return 2

    page_filter = _parse_filter(args.pages)
    size_filter = _parse_filter(args.sizes)
    scale_filter = _parse_filter(args.scales)
    include_source = not args.ignore_source

    def include_entry(entry: dict[str, Any]) -> bool:
        page = str(entry.get("page", ""))
        size = str(entry.get("size", ""))
        scale = str(entry.get("scale", ""))
        if page_filter and page not in page_filter:
            return False
        if size_filter and size not in size_filter:
            return False
        if scale_filter and scale not in scale_filter:
            return False
        return True

    def to_records(items: list[dict[str, Any]]) -> dict[ShotKey, dict[str, Any]]:
        records: dict[ShotKey, dict[str, Any]] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            if not include_entry(item):
                continue
            key = _build_key(item, include_source=include_source)
            records[key] = item
        return records

    base_records = to_records(base_list)
    target_records = to_records(target_list)

    base_keys = set(base_records.keys())
    target_keys = set(target_records.keys())

    common_keys = sorted(base_keys & target_keys, key=lambda k: (k.page, k.size, k.scale, k.source))
    added_keys = sorted(target_keys - base_keys, key=lambda k: (k.page, k.size, k.scale, k.source))
    removed_keys = sorted(base_keys - target_keys, key=lambda k: (k.page, k.size, k.scale, k.source))

    changed: list[dict[str, Any]] = []
    unknown_hash: list[dict[str, Any]] = []
    page_summary: dict[str, dict[str, int]] = {}

    def bump(page: str, field: str) -> None:
        if page not in page_summary:
            page_summary[page] = {"changed": 0, "added": 0, "removed": 0, "unknown": 0}
        page_summary[page][field] += 1

    for key in common_keys:
        base_item = base_records[key]
        target_item = target_records[key]
        base_path = Path(str(base_item.get("path", "")))
        target_path = Path(str(target_item.get("path", "")))
        base_hash = str(base_item.get("sha256", "")).strip() or _hash_file(base_path)
        target_hash = str(target_item.get("sha256", "")).strip() or _hash_file(target_path)

        if not base_hash or not target_hash:
            unknown_hash.append(
                {
                    "key": key.as_dict(),
                    "base_path": str(base_path),
                    "target_path": str(target_path),
                }
            )
            bump(key.page, "unknown")
            continue

        if base_hash != target_hash:
            changed.append(
                {
                    "key": key.as_dict(),
                    "base_hash": base_hash,
                    "target_hash": target_hash,
                    "base_path": str(base_path),
                    "target_path": str(target_path),
                }
            )
            bump(key.page, "changed")

    added = [{"key": key.as_dict(), "entry": target_records[key]} for key in added_keys]
    removed = [{"key": key.as_dict(), "entry": base_records[key]} for key in removed_keys]
    for key in added_keys:
        bump(key.page, "added")
    for key in removed_keys:
        bump(key.page, "removed")

    changed_pages = sorted(
        {
            *[item["key"]["page"] for item in changed],
            *[item["key"]["page"] for item in added],
            *[item["key"]["page"] for item in removed],
            *[item["key"]["page"] for item in unknown_hash],
        }
    )

    if changed or added or removed:
        status = "PASS_WITH_WARNINGS"
    else:
        status = "PASS"

    output_root = (PROJECT_ROOT / args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    compare_dir = output_root / f"{compare_run_id}_{Path(args.base_run).name}_vs_{Path(args.target_run).name}"
    compare_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "compare_run_id": compare_run_id,
        "started_at": compare_started_at,
        "finished_at": _now_iso(),
        "status": status,
        "filters": {
            "pages": sorted(page_filter),
            "sizes": sorted(size_filter),
            "scales": sorted(scale_filter),
            "include_source": include_source,
        },
        "base": {
            "run_id": base_manifest.get("run_id", args.base_run),
            "kind": base_kind,
            "path": str(base_dir),
        },
        "target": {
            "run_id": target_manifest.get("run_id", args.target_run),
            "kind": target_kind,
            "path": str(target_dir),
        },
        "totals": {
            "base_entries": len(base_records),
            "target_entries": len(target_records),
            "compared_entries": len(common_keys),
            "changed_entries": len(changed),
            "added_entries": len(added),
            "removed_entries": len(removed),
            "unknown_hash_entries": len(unknown_hash),
        },
        "changed_pages": changed_pages,
        "page_summary": page_summary,
        "changed_entries": changed,
        "added_entries": added,
        "removed_entries": removed,
        "unknown_hash_entries": unknown_hash,
        "artifacts": {
            "summary_json": str((compare_dir / "ui_compare_summary.json").resolve()),
            "summary_md": str((compare_dir / "ui_compare_summary.md").resolve()),
            "latest_run_json": str((output_root / "latest_run.json").resolve()),
            "latest_run_txt": str((output_root / "latest_run.txt").resolve()),
        },
    }

    summary_json = compare_dir / "ui_compare_summary.json"
    summary_md = compare_dir / "ui_compare_summary.md"
    summary_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_md.write_text(_render_md(payload), encoding="utf-8")

    (output_root / "latest_run.json").write_text(
        json.dumps(
            {
                "compare_run_id": compare_run_id,
                "status": status,
                "path": str(compare_dir.resolve()),
                "base_run": str(payload["base"]["run_id"]),
                "target_run": str(payload["target"]["run_id"]),
                "timestamp": payload["finished_at"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (output_root / "latest_run.txt").write_text(str(compare_dir.resolve()) + "\n", encoding="utf-8")

    print(str(compare_dir.resolve()))
    print(f"UI compare status: {status}")
    if changed_pages:
        print("Changed pages: " + ", ".join(changed_pages))
    else:
        print("Changed pages: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
