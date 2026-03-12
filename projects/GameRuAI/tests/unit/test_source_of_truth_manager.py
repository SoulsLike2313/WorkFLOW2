from __future__ import annotations

from app.knowledge.source_registry import SourceRegistry


def test_source_registry_upsert_and_list(services, demo_project) -> None:
    pid = int(demo_project["id"])
    registry = SourceRegistry(services.repo)
    registry.upsert_source(
        project_id=pid,
        source_key="test_source",
        source_type="test",
        version="v1",
        status="active",
        metadata={"k": "v"},
    )
    rows = registry.list_sources(pid)
    assert any(row["source_key"] == "test_source" for row in rows)

