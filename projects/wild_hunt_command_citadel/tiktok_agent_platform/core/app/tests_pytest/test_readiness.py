from __future__ import annotations

from app.config import load_config
from app.readiness import ReadinessService


def test_readiness_aggregation(runtime):
    config = load_config()
    readiness = ReadinessService().evaluate_local(config=config, workspace_runtime=runtime)
    assert "overall_ready" in readiness
    names = {item["name"] for item in readiness["items"]}
    assert "config_ready" in names
    assert "repository_ready" in names

