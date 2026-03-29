#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json"
INDEX_HTML = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "web" / "index.html"
MUTABLE_TRACKER = REPO_ROOT / "docs" / "review_artifacts" / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1" / "MUTABLE_TRACKER.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def file_age_minutes(path: Path) -> int | None:
    if not path.exists():
        return None
    delta = datetime.now(timezone.utc).timestamp() - path.stat().st_mtime
    return max(0, int(delta // 60))


def freshness_class(age_minutes: int | None) -> str:
    if age_minutes is None:
        return "MISSING"
    if age_minutes <= 180:
        return "FRESH"
    if age_minutes <= 1440:
        return "AGING"
    return "STALE"


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def resolve_current_live_primary_path() -> str:
    fallback = "runtime/chatgpt_bundle_exports/imperium_living_spatial_brain_of_imperium_delta_primary_truth_bundle_latest.zip"
    if not MUTABLE_TRACKER.exists():
        return fallback
    try:
        payload = json.loads(MUTABLE_TRACKER.read_text(encoding="utf-8-sig"))
    except Exception:
        return fallback
    active = payload.get("active_live_primary_line", {})
    path = normalize(str((active or {}).get("path", "")))
    return path or fallback


def base_rows() -> list[dict]:
    return [
        {
            "contour_id": "foundation_governance",
            "title_ru": "Foundation canon / governance",
            "source_path": "docs/governance/FOUNDATION_INDEX_V1.md",
            "representation_surface_id": "visionBrainCore",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "mutable_live_truth",
            "title_ru": "Mutable live truth",
            "source_path": "docs/governance/LIVE_SYSTEM_INDEX_V1.md",
            "representation_surface_id": "visionImperialOverview",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "continuity_capsule",
            "title_ru": "Continuity / capsule",
            "source_path": "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/MUTABLE_TRACKER.json",
            "representation_surface_id": "visionMemoryChronology",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "current_live_primary_line",
            "title_ru": "Current live primary line",
            "source_path": "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/MUTABLE_TRACKER.json",
            "representation_surface_id": "visionBundleHealth",
            "truth_class": "DERIVED_CANONICAL",
            "active_bundle_pointer": resolve_current_live_primary_path(),
        },
        {
            "contour_id": "chronology_memory_checkpoints",
            "title_ru": "Chronology / memory / checkpoints",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/TIKTOK_WAVE1_PRODUCTION_HISTORY_SEED_V1.json",
            "representation_surface_id": "visionMemoryChronology",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "contradiction_lane",
            "title_ru": "Contradiction lane",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/TIKTOK_WAVE1_CONTROL_SURFACES_V1.json",
            "representation_surface_id": "visionInquisitionCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "owner_gate_lane",
            "title_ru": "Owner-gate lane",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/CURRENT_FACTORY_CANON_STATE_V1.json",
            "representation_surface_id": "visionCheckpoint",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "storage_sovereignty_portability_recovery",
            "title_ru": "Storage / sovereignty / portability / recovery",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_STORAGE_HEALTH_SURFACE_V1.json",
            "representation_surface_id": "visionSystemSemantics",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "repo_worktree_health",
            "title_ru": "Repo / worktree health",
            "source_path": "runtime/repo_control_center/repo_control_status.json",
            "representation_surface_id": "visionBrainCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "repo_hygiene_classification",
            "title_ru": "Repo hygiene classification",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1.json",
            "representation_surface_id": "visionBrainCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "code_bank_code_mass",
            "title_ru": "Code-bank / code mass",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionBrainCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "anomaly_signals",
            "title_ru": "Anomaly signals",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionInquisitionCore",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "dashboard_self_health",
            "title_ru": "Dashboard self-health",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/LIVE_OBSERVATION_STATE_MODEL_V1.json",
            "representation_surface_id": "visionSignalBand",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "factory",
            "title_ru": "Factory",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_FACTORY_PRODUCTION_STATE_V1.json",
            "representation_surface_id": "visionFactoryAssembly",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "tiktok_agent",
            "title_ru": "TikTok Agent",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_PRODUCT_EVOLUTION_MAP_V1.json",
            "representation_surface_id": "visionProductLive",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "evolution",
            "title_ru": "Evolution",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVOLUTION_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionEvolutionChannel",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "inquisition",
            "title_ru": "Inquisition",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_INQUISITION_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionInquisitionCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "custodes",
            "title_ru": "Adeptus Custodes",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionCustodesCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "mechanicus",
            "title_ru": "Adeptus Mechanicus",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionMechanicusCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "administratum",
            "title_ru": "Administratum",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionAdministratumCore",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "regent_sigillite",
            "title_ru": "Regent Sigillite",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_REGENT_SIGILLITE_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionMemoryChronology",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "force_doctrine",
            "title_ru": "Force doctrine / machine capability",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_FORCE_DOCTRINE_SURFACE_V1.json",
            "representation_surface_id": "visionForceDoctrine",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "palace_archive_node_prep",
            "title_ru": "Palace / archive / node prep",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_PALACE_AND_ARCHIVE_STATE_SURFACE_V1.json",
            "representation_surface_id": "visionPalaceArchive",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "control_gates",
            "title_ru": "Control gates",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CONTROL_GATES_SURFACE_V1.json",
            "representation_surface_id": "visionControlGates",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "brain_v2_layers",
            "title_ru": "Supreme Brain V2 layers",
            "source_path": "docs/governance/IMPERIUM_SUPREME_BRAIN_V2_LAYER_MODEL_V1.md",
            "representation_surface_id": "visionBrainCore",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "golden_throne_discoverability",
            "title_ru": "Golden Throne discoverability",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_GOLDEN_THRONE_DISCOVERABILITY_SURFACE_V1.json",
            "representation_surface_id": "visionGoldenThrone",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "golden_throne_authority_anchor",
            "title_ru": "Golden Throne authority anchor",
            "source_path": "docs/governance/GOLDEN_THRONE_AUTHORITY_ANCHOR_V1.json",
            "representation_surface_id": "visionGoldenThrone",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "prompt_command_state",
            "title_ru": "Prompt / command state",
            "source_path": "runtime/operator_command_layer/command_surface_status.json",
            "representation_surface_id": "visionPromptState",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "runtime_endpoints_event_flows",
            "title_ru": "Runtime endpoints / event flows",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVENT_FLOW_SPINE_SURFACE_V1.json",
            "representation_surface_id": "visionEventFlowSpine",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "diff_preview",
            "title_ru": "Diff / preview",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_V1.json",
            "representation_surface_id": "visionDiffPreview",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "doctrine_integrity_surface",
            "title_ru": "Doctrine integrity / outside-UI boundaries",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_V1.json",
            "representation_surface_id": "visionSystemSemantics",
            "truth_class": "SOURCE_EXACT",
        },
        {
            "contour_id": "full_realtime_event_bus",
            "title_ru": "Full realtime event bus",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVENT_FLOW_SPINE_SURFACE_V1.json",
            "representation_surface_id": "visionRealtimeBusLane",
            "truth_class": "DERIVED_CANONICAL",
        },
        {
            "contour_id": "live_work_visibility",
            "title_ru": "Live work visibility",
            "source_path": "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_V1.json",
            "representation_surface_id": "visionCurrentOperation",
            "truth_class": "SOURCE_EXACT",
        },
    ]


def build_surface() -> dict:
    html = INDEX_HTML.read_text(encoding="utf-8-sig") if INDEX_HTML.exists() else ""
    rows: list[dict] = []
    full_rows = 0
    partial_rows = 0
    missing_rows = 0

    for row in base_rows():
        source = normalize(str(row.get("source_path", "")))
        source_file = (REPO_ROOT / source).resolve()
        source_exists = source_file.exists()
        panel_id = str(row.get("representation_surface_id", "")).strip()
        represented = bool(panel_id) and f'id="{panel_id}"' in html
        age_min = file_age_minutes(source_file) if source_exists else None
        fresh = freshness_class(age_min)
        truth_class = str(row.get("truth_class", "UNKNOWN")).upper()

        if source_exists and represented:
            representation_status = "FULL"
            full_rows += 1
        elif source_exists or represented:
            representation_status = "PARTIAL"
            partial_rows += 1
        else:
            representation_status = "MISSING"
            missing_rows += 1

        confidence = 0.95 if representation_status == "FULL" else (0.65 if representation_status == "PARTIAL" else 0.35)
        blind_spot = ""
        if truth_class == "POINTER_ONLY":
            blind_spot = "Surface is pointer-only in UI; raw truth stays outside first layer."
        elif representation_status != "FULL":
            blind_spot = "Representation is incomplete or source path missing."

        rows.append(
            {
                **row,
                "source_path": source,
                "source_exists": source_exists,
                "represented_in_dashboard": represented,
                "representation_status": representation_status,
                "freshness_class": fresh,
                "source_age_minutes": age_min,
                "confidence": round(confidence, 2),
                "blind_spot_note": blind_spot,
            }
        )

    pointer_only_count = len([r for r in rows if str(r.get("truth_class", "")).upper() == "POINTER_ONLY"])
    missing_truth_count = len([r for r in rows if str(r.get("representation_status")) == "MISSING"])
    full_coverage_claimable = missing_truth_count == 0 and pointer_only_count == 0 and partial_rows == 0
    coverage_verdict = "FULL_COVERAGE" if full_coverage_claimable else "PARTIAL_COVERAGE"

    return {
        "surface_id": "IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1",
        "version": "1.0.0",
        "status": "ACTIVE",
        "truth_class": "SOURCE_EXACT",
        "generated_at_utc": utc_now_iso(),
        "source_path": "scripts/refresh_imperium_dashboard_coverage_surface.py",
        "coverage_verdict": coverage_verdict,
        "full_coverage_claimable": full_coverage_claimable,
        "rows_total": len(rows),
        "full_rows": full_rows,
        "partial_rows": partial_rows,
        "missing_rows": missing_rows,
        "pointer_only_count": pointer_only_count,
        "rows": rows,
        "notes": [
            "Coverage matrix is strict: no full claim while pointer-only or missing rows remain.",
            "Factory and Brain are represented as distinct dashboard zones.",
            "Custodes/Mechanicus/Administratum/Force/Palace/Control-Gates are tracked as separate organ contours.",
            "Golden throne discoverability and authority anchor are tracked as separate contours.",
            "Realtime bus completeness remains explicit through a dedicated undercovered contour until fully implemented.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh dashboard coverage matrix surface for IMPERIUM.")
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
