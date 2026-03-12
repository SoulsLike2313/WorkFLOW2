from __future__ import annotations

from app.learning.evidence_store import EvidenceStore


def test_evidence_store_persistence(services, demo_project) -> None:
    pid = int(demo_project["id"])
    store = EvidenceStore(services.repo)
    store.record(
        project_id=pid,
        evidence_type="unit_test",
        entity_ref="entry:1",
        confidence=0.88,
        status="working",
        payload={"hello": "world"},
    )
    rows = store.list_recent(pid, limit=20)
    assert any(row["evidence_type"] == "unit_test" for row in rows)

