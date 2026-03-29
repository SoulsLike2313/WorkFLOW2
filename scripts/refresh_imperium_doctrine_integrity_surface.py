#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    REPO_ROOT
    / "shared_systems"
    / "factory_observation_window_v1"
    / "adapters"
    / "IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_V1.json"
)
GOVERNANCE_DIR = REPO_ROOT / "docs" / "governance"
ENTRYPOINT_PATH = REPO_ROOT / "docs" / "governance" / "SYSTEM_ENTRYPOINT_V1.md"
INSTRUCTION_INDEX_PATH = REPO_ROOT / "docs" / "INSTRUCTION_INDEX.md"
NEXT_STEP_PATH = REPO_ROOT / "docs" / "NEXT_CANONICAL_STEP.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")


def file_exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def extract_step_id(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip()
        if clean.lower().startswith("- step_id:"):
            parts = clean.split("`")
            if len(parts) >= 2:
                return parts[1].strip()
            return clean.split(":", 1)[1].strip()
    return "unknown-next-step"


def build_surface() -> dict[str, Any]:
    governance_files = sorted([p for p in GOVERNANCE_DIR.glob("*") if p.is_file()])
    governance_docs_count = len(governance_files)
    governance_md_count = len([p for p in governance_files if p.suffix.lower() == ".md"])
    entrypoint_exists = file_exists(ENTRYPOINT_PATH)
    index_exists = file_exists(INSTRUCTION_INDEX_PATH)
    next_step_exists = file_exists(NEXT_STEP_PATH)
    next_step_text = read_text(NEXT_STEP_PATH) if next_step_exists else ""
    next_step_id = extract_step_id(next_step_text)

    integrity_status = "ACTIVE"
    if not entrypoint_exists or not index_exists:
        integrity_status = "PARTIAL"

    doctrine_gaps: list[str] = []
    if not entrypoint_exists:
        doctrine_gaps.append("missing_system_entrypoint")
    if not index_exists:
        doctrine_gaps.append("missing_instruction_index")
    if not next_step_exists:
        doctrine_gaps.append("missing_next_canonical_step")

    return {
        "surface_id": "IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_V1",
        "version": "1.0.0",
        "status": integrity_status,
        "truth_class": "SOURCE_EXACT",
        "generated_at_utc": utc_now_iso(),
        "source_path": "scripts/refresh_imperium_doctrine_integrity_surface.py",
        "doctrine_inventory": {
            "governance_docs_total": governance_docs_count,
            "governance_markdown_total": governance_md_count,
            "system_entrypoint_exists": entrypoint_exists,
            "instruction_index_exists": index_exists,
            "next_canonical_step_exists": next_step_exists,
            "next_canonical_step_id": next_step_id,
        },
        "ui_disclosure_boundary": {
            "status": "ACTIVE",
            "policy": "owner_readable_first_technical_second",
            "outside_ui_scope_allowed": True,
            "outside_ui_scope_requires_explicit_note": True,
        },
        "doctrine_gaps": doctrine_gaps,
        "notes": [
            "Surface keeps doctrine visibility source-exact in dashboard coverage matrix.",
            "No fake completeness: gaps remain explicit and machine-readable.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh IMPERIUM doctrine integrity surface.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    args = parser.parse_args()

    out_path = Path(args.out).expanduser()
    if not out_path.is_absolute():
        out_path = (REPO_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_surface()
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "output": str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
