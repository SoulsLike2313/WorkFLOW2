from __future__ import annotations

from collections import Counter

from app.storage.repositories import RepositoryHub


class AdaptationRules:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def summarize(self, project_id: int) -> dict:
        events = self.repo.list_adaptation_events(project_id, limit=500)
        by_type = Counter(item["event_type"] for item in events)
        return {
            "events_total": len(events),
            "by_type": dict(by_type),
            "recent": events[:15],
        }
