from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VISUAL_PREFIX = "imperial_dashboard_visual_audit_loop_"
DIFF_PREFIX = "imperium_diff_preview_pack_"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def list_visual_runs(visual_root: Path) -> list[Path]:
    runs = [p for p in visual_root.glob(f"{VISUAL_PREFIX}*") if p.is_dir()]
    runs.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return runs


def resolve_run(visual_root: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    candidate = Path(raw)
    if candidate.exists() and candidate.is_dir():
        return candidate.resolve()
    run_id = raw.strip()
    direct = visual_root / f"{VISUAL_PREFIX}{run_id}"
    if direct.exists() and direct.is_dir():
        return direct.resolve()
    return None


def map_pngs(run_dir: Path) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for path in sorted(run_dir.glob("*.png")):
        mapping[path.name] = path
    return mapping


def build_contact_sheet_html(pairs: list[dict[str, Any]], out_dir: Path) -> str:
    rows = []
    for item in pairs:
        before_rel = item.get("before_rel", "")
        after_rel = item.get("after_rel", "")
        status = item.get("status", "UNKNOWN")
        zone = item.get("zone", "unknown")
        rows.append(
            f"""
            <tr>
              <td>{zone}</td>
              <td>{status}</td>
              <td><img src="{before_rel}" alt="before {zone}" /></td>
              <td><img src="{after_rel}" alt="after {zone}" /></td>
            </tr>
            """
        )

    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Imperium Diff Preview Contact Sheet</title>
  <style>
    body {{
      margin: 0;
      padding: 16px;
      background: #0d1020;
      color: #e7ebff;
      font-family: "Segoe UI", Arial, sans-serif;
    }}
    h1 {{ margin: 0 0 12px 0; font-size: 20px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{
      border: 1px solid #2f355f;
      padding: 8px;
      vertical-align: top;
      font-size: 12px;
    }}
    th {{ background: #1a1f3e; color: #c8d2ff; }}
    td {{ background: #131734; }}
    img {{
      width: 100%;
      max-width: 640px;
      height: auto;
      border: 1px solid #3f4a84;
      border-radius: 6px;
      background: #090b17;
    }}
  </style>
</head>
<body>
  <h1>Imperium Before/After Diff Contact Sheet</h1>
  <table>
    <thead>
      <tr>
        <th>Sector</th>
        <th>Status</th>
        <th>Before</th>
        <th>After</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    out_path = out_dir / "contact_sheet.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path.name


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate bounded before/after diff preview pack for imperial dashboard.")
    parser.add_argument(
        "--visual-root",
        default="docs/review_artifacts/visual_evidence",
        help="Visual evidence root with imperial_dashboard_visual_audit_loop_* runs.",
    )
    parser.add_argument("--before-run", default="", help="Before run dir path or run_id.")
    parser.add_argument("--after-run", default="", help="After run dir path or run_id.")
    parser.add_argument("--out-dir", default="", help="Output pack directory.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    visual_root = (repo_root / args.visual_root).resolve()
    visual_root.mkdir(parents=True, exist_ok=True)

    before_run = resolve_run(visual_root, args.before_run) if args.before_run else None
    after_run = resolve_run(visual_root, args.after_run) if args.after_run else None

    if before_run is None or after_run is None:
        runs = list_visual_runs(visual_root)
        if len(runs) < 2:
            raise SystemExit("Need at least two visual audit runs to build diff preview pack.")
        if after_run is None:
            after_run = runs[0]
        if before_run is None:
            before_run = runs[1] if runs[0] == after_run else runs[0]
            if before_run == after_run and len(runs) > 1:
                before_run = runs[1]

    assert before_run is not None and after_run is not None
    if before_run.resolve() == after_run.resolve():
        raise SystemExit("Before and after runs must be different.")

    before_png = map_pngs(before_run)
    after_png = map_pngs(after_run)
    common_names = sorted(set(before_png.keys()) & set(after_png.keys()))
    before_only = sorted(set(before_png.keys()) - set(after_png.keys()))
    after_only = sorted(set(after_png.keys()) - set(before_png.keys()))

    pack_id = f"{DIFF_PREFIX}{utc_stamp()}"
    out_dir = (Path(args.out_dir).resolve() if args.out_dir else (visual_root / pack_id))
    out_dir.mkdir(parents=True, exist_ok=True)
    before_out = out_dir / "before"
    after_out = out_dir / "after"
    before_out.mkdir(parents=True, exist_ok=True)
    after_out.mkdir(parents=True, exist_ok=True)

    compared_pairs: list[dict[str, Any]] = []
    changed_count = 0
    for name in common_names:
        before_src = before_png[name]
        after_src = after_png[name]
        before_hash = sha256_file(before_src)
        after_hash = sha256_file(after_src)
        status = "CHANGED" if before_hash != after_hash else "UNCHANGED"
        if status == "CHANGED":
            changed_count += 1

        before_dst = before_out / name
        after_dst = after_out / name
        shutil.copy2(before_src, before_dst)
        shutil.copy2(after_src, after_dst)
        compared_pairs.append(
            {
                "file": name,
                "zone": name.replace(".png", ""),
                "status": status,
                "before_hash": before_hash,
                "after_hash": after_hash,
                "before_rel": f"before/{name}",
                "after_rel": f"after/{name}",
            }
        )

    contact_sheet_name = build_contact_sheet_html(compared_pairs, out_dir)

    manifest = {
        "pack_id": pack_id,
        "generated_at_utc": utc_iso(),
        "before_run_id": before_run.name.replace(VISUAL_PREFIX, ""),
        "after_run_id": after_run.name.replace(VISUAL_PREFIX, ""),
        "before_run_path": str(before_run),
        "after_run_path": str(after_run),
        "compared_count": len(common_names),
        "changed_count": changed_count,
        "unchanged_count": len(common_names) - changed_count,
        "missing_count": len(before_only) + len(after_only),
        "before_only_files": before_only,
        "after_only_files": after_only,
        "contact_sheet_html": contact_sheet_name,
        "pairs": compared_pairs,
        "truth_class": "SOURCE_EXACT",
        "notes": [
            "bounded_diff_preview_pack",
            "no_fake_realtime_claim",
            "paired_before_after_visual_evidence",
        ],
    }
    (out_dir / "diff_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    report = f"""# Imperium Diff Preview Pack

- pack_id: `{pack_id}`
- generated_at_utc: `{manifest["generated_at_utc"]}`
- before_run: `{manifest["before_run_id"]}`
- after_run: `{manifest["after_run_id"]}`
- compared: `{manifest["compared_count"]}`
- changed: `{manifest["changed_count"]}`
- unchanged: `{manifest["unchanged_count"]}`
- missing: `{manifest["missing_count"]}`
- contact_sheet: `{contact_sheet_name}`
"""
    (out_dir / "diff_report.md").write_text(report, encoding="utf-8")

    print(json.dumps({"status": "ok", "pack_id": pack_id, "out_dir": str(out_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

