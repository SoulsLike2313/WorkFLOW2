#!/usr/bin/env python
from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MACHINE_OUT = ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"
ORGAN_OUT = ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"

THRONE_ANCHOR = ROOT / "docs" / "governance" / "GOLDEN_THRONE_AUTHORITY_ANCHOR_V1.json"
NODE_RANK = ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json"
CODE_BANK = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json"
COVERAGE = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json"
DOMINANCE = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_TRUTH_DOMINANCE_SURFACE_V1.json"
CUSTODES = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1.json"
INQUISITION = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_INQUISITION_STATE_SURFACE_V1.json"
MECHANICUS = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1.json"
ADMINISTRATUM = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1.json"
FORCE_SURFACE = ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_FORCE_DOCTRINE_SURFACE_V1.json"
CONTRACT = ROOT / "runtime" / "administratum" / "IMPERIUM_ACTIVE_MISSION_CONTRACT_V1.json"
CAPSULE_TRACKER = ROOT / "docs" / "review_artifacts" / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1" / "MUTABLE_TRACKER.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return load_json(path)
    except Exception:
        return {}


def to_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def bool_score(value: bool) -> int:
    return 100 if value else 30


def bounded(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(value)))


def git_cleanliness() -> tuple[str, int, int]:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain=v1"],
            cwd=ROOT,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except Exception:
        return ("UNKNOWN", -1, -1)
    tracked_dirty = 0
    untracked = 0
    for raw in out.splitlines():
        line = str(raw or "")
        if line.startswith("?? "):
            untracked += 1
            continue
        if line[:2].strip():
            tracked_dirty += 1
    if tracked_dirty == 0 and untracked == 0:
        return ("CLEAN", tracked_dirty, untracked)
    if tracked_dirty > 0 and untracked == 0:
        return ("DIRTY_TRACKED_ONLY", tracked_dirty, untracked)
    if tracked_dirty == 0 and untracked > 0:
        return ("DIRTY_UNTRACKED_ONLY", tracked_dirty, untracked)
    return ("DIRTY_MIXED", tracked_dirty, untracked)


def detect_total_memory_bytes() -> int:
    if os.name == "nt":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return int(stat.ullTotalPhys)
        return 0

    if hasattr(os, "sysconf"):
        try:
            pages = int(os.sysconf("SC_PHYS_PAGES"))
            page_size = int(os.sysconf("SC_PAGE_SIZE"))
            return pages * page_size
        except Exception:
            return 0
    return 0


def bytes_to_gb(value: int) -> float:
    if value <= 0:
        return 0.0
    return round(value / (1024 ** 3), 2)


@dataclass
class OrganScore:
    organ_id: str
    readiness: int
    bottleneck: str
    state: str


def build_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    now = utc_now()
    code_bank = load_json_if_exists(CODE_BANK)
    coverage = load_json_if_exists(COVERAGE)
    dominance = load_json_if_exists(DOMINANCE)
    throne = load_json_if_exists(THRONE_ANCHOR)
    rank = load_json_if_exists(NODE_RANK)
    custodes = load_json_if_exists(CUSTODES)
    inquisition = load_json_if_exists(INQUISITION)
    mechanicus = load_json_if_exists(MECHANICUS)
    administratum = load_json_if_exists(ADMINISTRATUM)
    force_surface = load_json_if_exists(FORCE_SURFACE)
    contract = load_json_if_exists(CONTRACT)
    capsule_tracker = load_json_if_exists(CAPSULE_TRACKER)

    cleanliness, tracked_dirty, untracked = git_cleanliness()

    cpu_count = int(os.cpu_count() or 1)
    mem_total = detect_total_memory_bytes()
    disk = shutil.disk_usage(str(ROOT.drive) + "\\") if ROOT.drive else shutil.disk_usage(str(ROOT))

    tool_power = {
        "git": bool(shutil.which("git")),
        "python": bool(shutil.which("python")),
        "node": bool(shutil.which("node")),
        "playwright_capture_script": (ROOT / "scripts" / "imperial_dashboard_visual_audit_loop.py").exists(),
        "diff_pack_script": (ROOT / "scripts" / "imperium_diff_preview_pack.py").exists(),
        "safe_review_pipeline_script": (ROOT / "scripts" / "imperium_safe_review_pipeline.py").exists(),
    }

    coverage_verdict = str(coverage.get("coverage_verdict", "UNKNOWN")).upper()
    pointer_only = int(coverage.get("pointer_only_count", 0) or 0)
    stale_rules = int(dominance.get("stale_rules_count", 0) or 0)
    code_status = str((code_bank.get("summary", {}) or {}).get("status_classification", "UNKNOWN")).upper()
    monolith_count = len(code_bank.get("top_monoliths", []) or [])

    emperor_status = str(rank.get("emperor_status", "EMPEROR_STATUS_BLOCKED")).upper()
    throne_breach = bool(rank.get("throne_breach", emperor_status != "VALID"))
    full_authority = bool(throne.get("full_system_authority", False)) and emperor_status == "VALID"

    unknowns = list(contract.get("unknowns", []) or [])
    assumptions = list(contract.get("assumptions", []) or [])
    required_fields = list((administratum.get("contract_gate", {}) or {}).get("required_fields", []) or [])
    contract_missing = [field for field in required_fields if field not in contract]
    clarity_pressure = len(unknowns) + len(assumptions) + len(contract_missing)
    clarity_state = "GREEN"
    if contract_missing:
        clarity_state = "RED_BLOCK"
    elif clarity_pressure >= 4:
        clarity_state = "AMBER"

    capsule_ready = bool(capsule_tracker)
    active_line = bool(((capsule_tracker.get("active_live_primary_line", {}) or {}).get("path", "")).strip())

    machine_manifest = {
        "manifest_id": "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1",
        "generated_at_utc": now,
        "truth_class": "DERIVED_CANONICAL",
        "source_path": "scripts/refresh_imperium_force_manifest.py",
        "machine_identity": {
            "hostname": socket.gethostname(),
            "os": platform.platform(),
            "python_version": platform.python_version(),
            "repo_root": str(ROOT),
        },
        "compute_power": {
            "cpu_logical_cores": cpu_count,
            "memory_total_gb": bytes_to_gb(mem_total),
            "disk_total_gb": bytes_to_gb(int(disk.total)),
            "disk_free_gb": bytes_to_gb(int(disk.free)),
            "gpu_profile": "UNKNOWN_NOT_MAPPED",
            "network_profile": "LOCAL_FIRST",
        },
        "tool_power": {
            "available_tools": tool_power,
            "available_count": len([x for x in tool_power.values() if bool(x)]),
        },
        "knowledge_power": {
            "repo_truth": "LOCAL_CANONICAL_REPO",
            "bundle_truth": "ACTIVE_PRIMARY_PLUS_COMPANION",
            "doctrine_access": "GOVERNANCE_SURFACES_PRESENT",
            "coverage_verdict": coverage_verdict,
            "pointer_only_count": pointer_only,
        },
        "authority_power": {
            "emperor_status": emperor_status,
            "throne_breach": throne_breach,
            "full_system_authority": full_authority,
            "authority_source": to_rel(THRONE_ANCHOR),
            "non_authority_sources_enforced": True,
        },
        "clarity_power": {
            "contract_state": clarity_state,
            "unknowns_count": len(unknowns),
            "assumptions_count": len(assumptions),
            "missing_required_fields_count": len(contract_missing),
            "missing_required_fields": contract_missing,
        },
        "execution_power": {
            "repo_hygiene": cleanliness,
            "tracked_dirty_count": tracked_dirty,
            "untracked_count": untracked,
            "code_bank_status": code_status,
            "code_monolith_count": monolith_count,
        },
        "validation_power": {
            "stale_dominance_rules_count": stale_rules,
            "coverage_claimable": bool(coverage.get("full_coverage_claimable", False)),
            "coverage_verdict": coverage_verdict,
        },
        "coordination_power": {
            "capsule_ready": capsule_ready,
            "active_line_pointer_present": active_line,
            "node_era_deployment_status": "NOT_YET_IMPLEMENTED",
        },
        "force_assessment": {
            "readiness_band": (
                "HIGH" if emperor_status == "VALID" and cleanliness == "CLEAN" and stale_rules == 0
                else "MEDIUM" if emperor_status == "VALID"
                else "BLOCKED"
            ),
            "bottlenecks": [
                "repo_hygiene_not_clean" if cleanliness != "CLEAN" else "",
                "stale_dominance_rules" if stale_rules > 0 else "",
                "coverage_partial_or_pointer_only" if coverage_verdict != "FULL_COVERAGE" or pointer_only > 0 else "",
                "code_bank_monolith_risk" if code_status == "MONOLITH_RISK" else "",
                "clarity_contract_not_green" if clarity_state != "GREEN" else "",
            ],
        },
    }
    machine_manifest["force_assessment"]["bottlenecks"] = [
        item for item in machine_manifest["force_assessment"]["bottlenecks"] if item
    ]

    custodes_score = OrganScore(
        organ_id="custodes",
        readiness=90 if not throne_breach else 45,
        bottleneck="throne_breach" if throne_breach else "none",
        state=str(custodes.get("status", "ACTIVE")),
    )
    inquisition_alerts = len(inquisition.get("active_heresy_alerts", []) or [])
    inquisition_score = OrganScore(
        organ_id="inquisition",
        readiness=bounded(80 - (inquisition_alerts * 5), 35, 90),
        bottleneck="high_open_case_count" if inquisition_alerts > 4 else "none",
        state=str(inquisition.get("status", "ACTIVE")),
    )
    mechanicus_score = OrganScore(
        organ_id="mechanicus",
        readiness=bounded(85 - (10 if code_status == "MONOLITH_RISK" else 0) - (5 if cleanliness != "CLEAN" else 0)),
        bottleneck="code_monolith_pressure" if code_status == "MONOLITH_RISK" else "none",
        state=str(mechanicus.get("status", "ACTIVE")),
    )
    administratum_score = OrganScore(
        organ_id="administratum",
        readiness=90 if clarity_state == "GREEN" else (60 if clarity_state == "AMBER" else 35),
        bottleneck="contract_gate_red_block" if clarity_state == "RED_BLOCK" else ("contract_gate_amber" if clarity_state == "AMBER" else "none"),
        state=str(administratum.get("status", "ACTIVE")),
    )

    organ_strength = {
        "surface_id": "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1",
        "generated_at_utc": now,
        "truth_class": "DERIVED_CANONICAL",
        "source_path": "scripts/refresh_imperium_force_manifest.py",
        "organ_strength": [
            custodes_score.__dict__,
            inquisition_score.__dict__,
            mechanicus_score.__dict__,
            administratum_score.__dict__,
        ],
        "mission_cost_context": {
            "active_contract_path": to_rel(CONTRACT),
            "active_contract_id": str(contract.get("contract_id", "UNKNOWN")),
            "risk_band": str((contract.get("risk_cost_estimate", {}) or {}).get("risk_band", "UNKNOWN")),
            "cost_band": str((contract.get("risk_cost_estimate", {}) or {}).get("cost_band", "UNKNOWN")),
            "mission_class": "bounded_ui_runtime_doctrine_delta",
            "templates_source_path": to_rel(FORCE_SURFACE),
            "templates_count": len(force_surface.get("mission_cost_templates", []) or []),
        },
        "gate_projection": {
            "throne_proof_control": "PASS" if emperor_status == "VALID" else "BLOCKED",
            "truth_dominance_chamber": "PASS" if stale_rules == 0 else "WARNING",
            "coverage_authority_control": "PASS" if coverage_verdict == "FULL_COVERAGE" and pointer_only == 0 else "WARNING",
            "contract_stop_and_ask_gate": clarity_state,
        },
    }

    return machine_manifest, organ_strength


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh IMPERIUM machine capability and organ strength force surfaces.")
    parser.add_argument("--machine-out", default=str(MACHINE_OUT))
    parser.add_argument("--organ-out", default=str(ORGAN_OUT))
    args = parser.parse_args()

    machine_out = Path(args.machine_out)
    organ_out = Path(args.organ_out)
    if not machine_out.is_absolute():
        machine_out = (ROOT / machine_out).resolve()
    if not organ_out.is_absolute():
        organ_out = (ROOT / organ_out).resolve()

    machine_payload, organ_payload = build_payload()
    machine_out.parent.mkdir(parents=True, exist_ok=True)
    organ_out.parent.mkdir(parents=True, exist_ok=True)
    machine_out.write_text(json.dumps(machine_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    organ_out.write_text(json.dumps(organ_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "machine_output": str(machine_out),
                "organ_output": str(organ_out),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
