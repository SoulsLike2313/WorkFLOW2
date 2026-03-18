#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "registry_doc_drift_guard.v1.0.0"
DEFAULT_OUTPUT = ROOT / "runtime" / "repo_control_center" / "validation" / "registry_doc_drift_report.json"

MISSION_REGISTRY_JSON = ROOT / "workspace_config" / "operator_mission_registry.json"
MISSION_REGISTRY_DOC = ROOT / "docs" / "governance" / "OPERATOR_MISSION_REGISTRY.md"
WORKSPACE_MANIFEST = ROOT / "workspace_config" / "workspace_manifest.json"
CODEX_MANIFEST = ROOT / "workspace_config" / "codex_manifest.json"

CANONICAL_DOCS_FOR_MISSION_IDS = [
    ROOT / "README.md",
    ROOT / "docs" / "governance" / "OPERATOR_MISSION_REGISTRY.md",
    ROOT / "docs" / "governance" / "OPERATOR_MISSION_CATALOG_WAVE_3A.md",
    ROOT / "docs" / "governance" / "OPERATOR_MISSION_CATALOG_WAVE_3B.md",
    ROOT / "docs" / "governance" / "OPERATOR_MISSION_CATALOG_WAVE_3C.md",
    ROOT / "docs" / "review_artifacts" / "OPERATOR_MISSION_CERTIFICATION_REPORT.md",
    ROOT / "docs" / "review_artifacts" / "OPERATOR_MISSION_LAYER_FINAL_SUMMARY.md",
    ROOT / "docs" / "NEXT_CANONICAL_STEP.md",
]

MISSION_ID_PATTERN = re.compile(r"\bmission\.[A-Za-z0-9_.-]+\b")

REQUIRED_ANCHORS = [
    "docs/governance/WORKFLOW2_CONSTITUTION_V1.md",
    "docs/governance/WORKFLOW2_CONSTITUTION_V0.md",
    "docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md",
    "docs/governance/TRUTH_STATE_MODEL_V1.md",
    "workspace_config/schemas/truth_state_schema.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def collect_registry_data() -> tuple[list[str], list[str]]:
    payload = read_json(MISSION_REGISTRY_JSON)
    classes: list[str] = []
    mission_ids: list[str] = []
    for cls in payload.get("mission_classes", []):
        c = str(cls.get("mission_class", "")).strip()
        if c and c not in classes:
            classes.append(c)
        for m in cls.get("missions", []):
            mid = str(m.get("mission_id", "")).strip()
            if mid:
                mission_ids.append(mid)
    return sorted(classes), sorted(set(mission_ids))


def check_registry_doc(classes: list[str], mission_ids: list[str]) -> dict[str, Any]:
    text = read_text(MISSION_REGISTRY_DOC)
    missing_classes = [c for c in classes if c not in text]
    missing_mission_ids = [m for m in mission_ids if m not in text]
    return {
        "missing_classes_in_doc": missing_classes,
        "missing_mission_ids_in_doc": missing_mission_ids,
        "class_count": len(classes),
        "mission_id_count": len(mission_ids),
    }


def check_manifest_anchors() -> dict[str, Any]:
    workspace = read_json(WORKSPACE_MANIFEST)
    codex = read_json(CODEX_MANIFEST)

    workspace_text = json.dumps(workspace, ensure_ascii=False)
    codex_text = json.dumps(codex, ensure_ascii=False)
    missing_workspace = [a for a in REQUIRED_ANCHORS if a not in workspace_text]
    missing_codex = [a for a in REQUIRED_ANCHORS if a not in codex_text]

    return {
        "required_anchors": REQUIRED_ANCHORS,
        "missing_in_workspace_manifest": missing_workspace,
        "missing_in_codex_manifest": missing_codex,
    }


def check_doc_mission_examples(registry_mission_ids: list[str]) -> dict[str, Any]:
    missing_examples: list[dict[str, str]] = []
    found_examples: dict[str, list[str]] = {}
    registry_set = set(registry_mission_ids)

    for path in CANONICAL_DOCS_FOR_MISSION_IDS:
        if not path.exists():
            continue
        text = read_text(path)
        ids = sorted(set(MISSION_ID_PATTERN.findall(text)))
        if not ids:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        found_examples[rel] = ids
        for mid in ids:
            if mid not in registry_set:
                missing_examples.append({"file": rel, "mission_id": mid})

    return {
        "scanned_docs": [str(p.relative_to(ROOT)).replace("\\", "/") for p in CANONICAL_DOCS_FOR_MISSION_IDS if p.exists()],
        "found_examples_by_doc": found_examples,
        "missing_registry_links": missing_examples,
    }


def run_guard() -> dict[str, Any]:
    classes, mission_ids = collect_registry_data()
    registry_doc = check_registry_doc(classes, mission_ids)
    manifest_anchor = check_manifest_anchors()
    mission_examples = check_doc_mission_examples(mission_ids)

    findings: list[dict[str, str]] = []

    for c in registry_doc["missing_classes_in_doc"]:
        findings.append({"severity": "FAIL", "class": "registry_doc_class_missing", "message": f"missing class in doc: {c}"})
    for m in registry_doc["missing_mission_ids_in_doc"]:
        findings.append({"severity": "WARNING", "class": "registry_doc_mission_id_missing", "message": f"missing mission id in doc: {m}"})
    for a in manifest_anchor["missing_in_workspace_manifest"]:
        findings.append({"severity": "WARNING", "class": "workspace_manifest_anchor_missing", "message": f"missing anchor in workspace_manifest: {a}"})
    for a in manifest_anchor["missing_in_codex_manifest"]:
        findings.append({"severity": "WARNING", "class": "codex_manifest_anchor_missing", "message": f"missing anchor in codex_manifest: {a}"})
    for item in mission_examples["missing_registry_links"]:
        findings.append(
            {
                "severity": "FAIL",
                "class": "mission_example_unknown_id",
                "message": f"{item['file']} references unknown mission id {item['mission_id']}",
            }
        )

    fail_count = sum(1 for f in findings if f["severity"] == "FAIL")
    warning_count = sum(1 for f in findings if f["severity"] == "WARNING")
    verdict = "FAIL" if fail_count else ("WARNING" if warning_count else "PASS")

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_utc(),
        "checks": {
            "registry_doc_alignment": registry_doc,
            "manifest_anchor_alignment": manifest_anchor,
            "mission_id_examples": mission_examples,
        },
        "findings": findings,
        "summary": {
            "fail_count": fail_count,
            "warning_count": warning_count,
            "verdict": verdict,
        },
        "coverage_gaps": [
            "No deep semantic markdown parsing beyond direct token checks.",
            "Does not verify every mission-related doc in repo; focuses on high-value canonical surfaces.",
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Low-risk guard for registry/manifests/docs drift.")
    p.add_argument("--output", default=str(DEFAULT_OUTPUT.relative_to(ROOT)), help="Path to JSON output report.")
    p.add_argument("--strict-warning", action="store_true", help="Return non-zero on WARNING as well.")
    return p


def main() -> int:
    args = parser().parse_args()
    out = Path(args.output).expanduser()
    if not out.is_absolute():
        out = (ROOT / out).resolve()

    payload = run_guard()
    write_json(out, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    verdict = payload["summary"]["verdict"]
    if verdict == "FAIL":
        return 1
    if verdict == "WARNING" and args.strict_warning:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
