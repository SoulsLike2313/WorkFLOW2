#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json"
CODE_EXTS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".css",
    ".html",
    ".json",
    ".md",
    ".ps1",
    ".toml",
    ".yaml",
    ".yml",
    ".sh",
}
PRIMARY_CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".css", ".html"}
FOCUS_FILES = [
    "shared_systems/factory_observation_window_v1/app/local_factory_observation_server.py",
    "shared_systems/factory_observation_window_v1/web/app.js",
    "shared_systems/factory_observation_window_v1/web/styles.css",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return str(completed.stdout or "").strip()


def iter_tracked_code_files() -> list[str]:
    raw = run_git(["ls-files"])
    files: list[str] = []
    for line in raw.splitlines():
        rel = normalize(line)
        if not rel:
            continue
        suffix = Path(rel).suffix.lower()
        if suffix in CODE_EXTS:
            files.append(rel)
    return files


def iter_untracked_code_files() -> list[str]:
    raw = run_git(["ls-files", "--others", "--exclude-standard"])
    files: list[str] = []
    for line in raw.splitlines():
        rel = normalize(line)
        if not rel:
            continue
        suffix = Path(rel).suffix.lower()
        if suffix in CODE_EXTS:
            files.append(rel)
    return files


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="cp1251")
        except Exception:
            return ""
    except Exception:
        return ""


def count_loc(text: str) -> int:
    if not text:
        return 0
    return sum(1 for line in text.splitlines() if line.strip())


def analyze_code_bank() -> dict:
    tracked = iter_tracked_code_files()
    untracked = iter_untracked_code_files()
    unique_map: dict[str, None] = {}
    for rel in tracked + untracked:
        unique_map[rel] = None
    scanned_files = list(unique_map.keys())
    untracked_set = set(untracked)
    by_ext_files: dict[str, int] = Counter()
    by_ext_loc: dict[str, int] = Counter()
    by_dir_loc: dict[str, int] = defaultdict(int)
    file_rows: list[dict] = []
    todo_count = 0
    fixme_count = 0
    not_yet_count = 0
    placeholder_count = 0
    utf8_sig_count = 0
    cp1251_suspect_count = 0
    utf8_decode_error_count = 0
    import_hotspots: list[dict] = []

    for rel in scanned_files:
        path = REPO_ROOT / rel
        ext = path.suffix.lower() or "no_ext"
        by_ext_files[ext] += 1
        raw_bytes = b""
        try:
            raw_bytes = path.read_bytes()
            if raw_bytes.startswith(b"\xef\xbb\xbf"):
                utf8_sig_count += 1
        except Exception:
            raw_bytes = b""

        text = read_text(path)
        if not text and raw_bytes:
            utf8_decode_error_count += 1
            try:
                raw_bytes.decode("cp1251")
                cp1251_suspect_count += 1
            except Exception:
                pass

        loc = count_loc(text)
        by_ext_loc[ext] += loc
        tracking_class = "UNTRACKED" if rel in untracked_set else "TRACKED"
        file_rows.append({"path": rel, "ext": ext, "loc": loc, "tracking_class": tracking_class})

        lowered = text.lower()
        todo_count += lowered.count("todo")
        fixme_count += lowered.count("fixme")
        not_yet_count += lowered.count("not_yet_implemented")
        placeholder_count += lowered.count("placeholder")

        dir_key = "/".join(rel.split("/")[:2]) if "/" in rel else "."
        by_dir_loc[dir_key] += loc

        if ext in {".py", ".js", ".ts", ".tsx"}:
            import_count = 0
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from ") or "require(" in stripped:
                    import_count += 1
            if import_count >= 40:
                import_hotspots.append({"path": rel, "import_lines": import_count, "loc": loc})

    file_rows.sort(key=lambda x: int(x.get("loc", 0)), reverse=True)
    import_hotspots.sort(key=lambda x: int(x.get("import_lines", 0)), reverse=True)
    meaningful_code_loc = int(
        sum(int(row.get("loc", 0) or 0) for row in file_rows if str(row.get("ext", "")) in PRIMARY_CODE_EXTS)
    )
    top_monoliths = [row for row in file_rows if int(row.get("loc", 0)) >= 800][:100]
    threshold_counts = {
        "ge_800": len([row for row in file_rows if int(row.get("loc", 0)) >= 800]),
        "ge_1200": len([row for row in file_rows if int(row.get("loc", 0)) >= 1200]),
        "ge_2000": len([row for row in file_rows if int(row.get("loc", 0)) >= 2000]),
        "ge_3000": len([row for row in file_rows if int(row.get("loc", 0)) >= 3000]),
    }
    monolith_pressure_index = int(
        threshold_counts["ge_3000"] * 5
        + threshold_counts["ge_2000"] * 3
        + threshold_counts["ge_1200"] * 2
        + threshold_counts["ge_800"]
    )

    status_classification = "HEALTHY"
    if threshold_counts["ge_3000"] > 0:
        status_classification = "MONOLITH_RISK"
    elif threshold_counts["ge_1200"] > 0:
        status_classification = "WATCH"
    if utf8_decode_error_count > 0:
        status_classification = "ANOMALY_REVIEW_REQUIRED"
    large_step_readiness_hint = "READY"
    if status_classification == "MONOLITH_RISK":
        large_step_readiness_hint = "CONSTRAINED"
    if status_classification == "ANOMALY_REVIEW_REQUIRED":
        large_step_readiness_hint = "BLOCKED"

    top_dirs = sorted(
        [{"dir": key, "loc": val} for key, val in by_dir_loc.items()],
        key=lambda x: int(x["loc"]),
        reverse=True,
    )[:25]
    ext_rows = sorted(
        [
            {
                "ext": ext,
                "files": int(by_ext_files[ext]),
                "loc": int(by_ext_loc[ext]),
                "primary_code": ext in PRIMARY_CODE_EXTS,
            }
            for ext in by_ext_files
        ],
        key=lambda x: int(x["loc"]),
        reverse=True,
    )
    top_ext = ext_rows[0]["ext"] if ext_rows else "n/a"

    focus_rows = []
    for rel in FOCUS_FILES:
        row = next((item for item in file_rows if item["path"] == rel), None)
        if row:
            focus_rows.append(row)
        else:
            focus_path = REPO_ROOT / rel
            if focus_path.exists():
                focus_text = read_text(focus_path)
                focus_rows.append(
                    {
                        "path": rel,
                        "ext": Path(rel).suffix.lower(),
                        "loc": count_loc(focus_text),
                        "tracking_class": "UNTRACKED",
                    }
                )
            else:
                focus_rows.append({"path": rel, "ext": Path(rel).suffix.lower(), "loc": 0, "missing": True})

    return {
        "status_classification": status_classification,
        "tracked_code_files_count": len(set(tracked)),
        "untracked_code_files_count": len(untracked_set),
        "scanned_code_files_count": len(scanned_files),
        "total_loc": int(sum(int(row.get("loc", 0)) for row in file_rows)),
        "meaningful_code_loc": meaningful_code_loc,
        "top_extension_by_loc": top_ext,
        "threshold_counts": threshold_counts,
        "monolith_pressure_index": monolith_pressure_index,
        "large_step_readiness_hint": large_step_readiness_hint,
        "by_extension": ext_rows,
        "top_directories_by_loc": top_dirs,
        "top_monoliths": top_monoliths,
        "focus_surfaces": focus_rows,
        "anomaly_ledger": {
            "todo_count": int(todo_count),
            "fixme_count": int(fixme_count),
            "not_yet_implemented_count": int(not_yet_count),
            "placeholder_count": int(placeholder_count),
            "utf8_sig_files_count": int(utf8_sig_count),
            "cp1251_suspect_files_count": int(cp1251_suspect_count),
            "utf8_decode_error_files_count": int(utf8_decode_error_count),
            "import_hotspots": import_hotspots[:50],
            "suspicious_growth_candidates": [
                {
                    "path": row["path"],
                    "loc": row["loc"],
                    "reason": "high_loc_concentration",
                }
                for row in file_rows
                if int(row.get("loc", 0)) >= 1200
            ][:80],
        },
    }


def build_surface() -> dict:
    data = analyze_code_bank()
    return {
        "surface_id": "IMPERIUM_CODE_BANK_STATE_SURFACE_V1",
        "version": "1.0.0",
        "status": "ACTIVE",
        "truth_class": "SOURCE_EXACT",
        "generated_at_utc": utc_now_iso(),
        "source_path": "scripts/refresh_imperium_code_bank_surface.py",
        "summary": {
            "status_classification": data["status_classification"],
            "tracked_code_files_count": data["tracked_code_files_count"],
            "untracked_code_files_count": data["untracked_code_files_count"],
            "scanned_code_files_count": data["scanned_code_files_count"],
            "total_loc": data["total_loc"],
            "meaningful_code_loc": data["meaningful_code_loc"],
            "top_extension_by_loc": data["top_extension_by_loc"],
            "threshold_counts": data["threshold_counts"],
            "monolith_pressure_index": data["monolith_pressure_index"],
            "large_step_readiness_hint": data["large_step_readiness_hint"],
        },
        "by_extension": data["by_extension"],
        "top_directories_by_loc": data["top_directories_by_loc"],
        "top_monoliths": data["top_monoliths"],
        "focus_surfaces": data["focus_surfaces"],
        "anomaly_ledger": data["anomaly_ledger"],
        "hygiene_controls": {
            "refresh_mode": "manual_script_refresh",
            "dashboard_binding": "brain_system_health_shell",
            "warning_policy": "monolith_and_encoding_risks_are_shown_without_masking",
        },
        "notes": [
            "Code-bank metrics include both TRACKED and UNTRACKED code-carrying files.",
            "Each file row includes tracking_class to avoid tracked/untracked confusion.",
            "Runtime/generated binary payloads are excluded from code-mass metrics.",
            "This surface is canonical input for Supreme Brain code-mass visibility.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh IMPERIUM code-bank dashboard surface.")
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output JSON path for IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json",
    )
    args = parser.parse_args()
    out_path = Path(args.out).expanduser()
    if not out_path.is_absolute():
        out_path = (REPO_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    surface = build_surface()
    out_path.write_text(json.dumps(surface, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "output": str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
