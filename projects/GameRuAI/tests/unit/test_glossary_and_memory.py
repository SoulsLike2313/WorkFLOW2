from __future__ import annotations

from app.glossary.models import GlossaryTerm


def test_glossary_application_and_tm_lookup(services, demo_project) -> None:
    pid = int(demo_project["id"])
    services.glossary_service.add_term(
        pid,
        GlossaryTerm(source_term="mission", target_term="миссия", source_lang="en"),
    )
    transformed, hits = services.glossary_service.apply(pid, "en", "mission ready now")
    assert "миссия" in transformed
    assert len(hits) == 1

    services.memory_service.remember(pid, "mission ready now", "миссия готова", "en", 0.95)
    matches = services.memory_service.lookup(pid, "en", "mission ready now")
    assert matches
    assert matches[0]["target_text"] == "миссия готова"
