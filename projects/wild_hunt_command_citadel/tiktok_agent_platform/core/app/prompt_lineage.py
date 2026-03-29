from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _short_text(text: str, *, limit: int = 220) -> str:
    value = " ".join(str(text or "").split())
    if len(value) <= limit:
        return value
    return f"{value[: max(20, limit - 3)]}..."


def _lineage_digest(parts: list[str]) -> str:
    payload = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(payload).hexdigest()[:16]


def build_prompt_lineage_snapshot(*, project_root: Path) -> dict[str, Any]:
    manifest_path = project_root / "PROJECT_MANIFEST.json"
    prompt_path = project_root / "PROMPT_FOR_CODEX.txt"

    manifest = _load_json_if_exists(manifest_path)
    prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
    prompt_present = bool(prompt_text.strip())

    lineage_parts = [
        str(manifest.get("schema_version", "")),
        str(manifest.get("slug", "")),
        str(manifest.get("name", "")),
        str(prompt_path.name if prompt_path.exists() else "MISSING_PROMPT_FOR_CODEX"),
        str(len(prompt_text)),
    ]
    lineage_id = f"prompt-lineage-{_lineage_digest(lineage_parts)}"

    missing_fields: list[str] = []
    if not manifest:
        missing_fields.append("PROJECT_MANIFEST.json")
    if not prompt_present:
        missing_fields.append("PROMPT_FOR_CODEX.txt")

    if missing_fields:
        trust_class = "MISSING_TEXT_BOUNDARY"
        state = "PROMPT_LINEAGE_INCOMPLETE"
    else:
        trust_class = "PARTIAL_TEXT_ONLY"
        state = "PROMPT_LINEAGE_TRACKED_BRIEF_ONLY"

    return {
        "status": "ok",
        "active_prompt_state": state,
        "lineage_id": lineage_id,
        "trusted_boundary": trust_class,
        "lineage": {
            "project_name": str(manifest.get("name", "unknown_project")),
            "project_slug": str(manifest.get("slug", "unknown_slug")),
            "manifest_schema_version": str(manifest.get("schema_version", "unknown")),
            "manifest_path": str(manifest_path),
            "prompt_source_path": str(prompt_path),
        },
        "source_brief": {
            "manifest_notes_excerpt": _short_text(" ".join(manifest.get("notes", [])))
            if isinstance(manifest.get("notes"), list)
            else "n/a",
            "prompt_excerpt": _short_text(prompt_text, limit=260) if prompt_present else "missing",
        },
        "text_boundary": {
            "full_prompt_text_exposed": False,
            "full_prompt_text_available_locally": prompt_present,
            "boundary_note": (
                "Full prompt text is intentionally not exposed through runtime API."
                if prompt_present
                else "Prompt text is missing in local project root."
            ),
        },
        "integrity": {
            "trusted_fields": [
                "project_name",
                "project_slug",
                "manifest_schema_version",
                "manifest_path",
                "prompt_source_path",
                "prompt_excerpt",
            ],
            "missing_fields": missing_fields,
        },
    }
