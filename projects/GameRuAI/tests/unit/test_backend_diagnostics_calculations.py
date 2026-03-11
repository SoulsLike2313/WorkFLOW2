from __future__ import annotations

from app.reports.backend_diagnostics import build_backend_diagnostics


def test_backend_diagnostics_calculates_latency_and_rates() -> None:
    rows = [
        {"backend_name": "local_mock", "latency_ms": 10, "fallback_used": False, "context_used": True, "requested_backend": "local_mock"},
        {"backend_name": "local_mock", "latency_ms": 20, "fallback_used": True, "context_used": False, "requested_backend": "argos"},
        {"backend_name": "dummy", "latency_ms": 30, "fallback_used": False, "context_used": False, "requested_backend": "dummy"},
    ]
    report = build_backend_diagnostics(rows)
    local = next(item for item in report if item["backend_name"] == "local_mock")
    assert local["runs_count"] == 2
    assert local["avg_latency_ms"] == 15.0
    assert local["fallback_count"] == 1
    assert local["context_used_rate"] == 0.5

