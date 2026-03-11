from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


def build_backend_diagnostics(backend_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "backend_name": "unknown",
            "runs_count": 0,
            "latencies": [],
            "fallback_count": 0,
            "context_used_count": 0,
            "requested_backends": set(),
        }
    )
    for run in backend_runs:
        backend_name = str(run.get("backend_name") or "unknown")
        node = grouped[backend_name]
        node["backend_name"] = backend_name
        node["runs_count"] += 1
        node["latencies"].append(int(run.get("latency_ms") or 0))
        if bool(run.get("fallback_used")):
            node["fallback_count"] += 1
        if bool(run.get("context_used")):
            node["context_used_count"] += 1
        node["requested_backends"].add(str(run.get("requested_backend") or "unknown"))

    out: list[dict[str, Any]] = []
    for backend_name, node in grouped.items():
        lat = sorted(node["latencies"])
        p95_idx = max(0, min(len(lat) - 1, int(len(lat) * 0.95) - 1))
        runs = max(1, int(node["runs_count"]))
        out.append(
            {
                "backend_name": backend_name,
                "runs_count": int(node["runs_count"]),
                "avg_latency_ms": round(float(mean(lat)), 3) if lat else 0.0,
                "p95_latency_ms": float(lat[p95_idx]) if lat else 0.0,
                "fallback_count": int(node["fallback_count"]),
                "fallback_rate": round(int(node["fallback_count"]) / runs, 4),
                "context_used_rate": round(int(node["context_used_count"]) / runs, 4),
                "requested_backends": sorted(node["requested_backends"]),
            }
        )
    out.sort(key=lambda item: (-item["runs_count"], item["backend_name"]))
    return out

