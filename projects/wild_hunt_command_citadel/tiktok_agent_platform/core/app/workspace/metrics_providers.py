from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .contracts import BaseMetricsProvider
from .models import MetricsSourceType, Profile


class OfficialApiMetricsProvider(BaseMetricsProvider):
    source_type = MetricsSourceType.OFFICIAL_API

    def fetch_profile_metrics(self, profile: Profile) -> dict[str, Any]:
        return {
            "profile_id": profile.id,
            "source_type": self.source_type.value,
            "status": "not_implemented",
            "message": "Official API integration contract is prepared but not connected.",
        }

    def fetch_content_metrics(self, profile: Profile, content_ids: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "content_id": content_id,
                "source_type": self.source_type.value,
                "status": "not_implemented",
            }
            for content_id in content_ids
        ]

    def fetch_recent_content(self, profile: Profile, limit: int = 20) -> list[dict[str, Any]]:
        return []

    def fetch_engagement_events(self, profile: Profile, limit: int = 100) -> list[dict[str, Any]]:
        return []

    def health_check(self) -> dict[str, Any]:
        return {"status": "not_implemented", "provider": self.source_type.value}

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "official_auth_required": True,
            "fetch_profile_metrics": False,
            "fetch_content_metrics": False,
        }


class ImportedSnapshotMetricsProvider(BaseMetricsProvider):
    source_type = MetricsSourceType.IMPORTED_SNAPSHOT

    def fetch_profile_metrics(self, profile: Profile) -> dict[str, Any]:
        return {"profile_id": profile.id, "source_type": self.source_type.value, "mode": "snapshot"}

    def fetch_content_metrics(self, profile: Profile, content_ids: list[str]) -> list[dict[str, Any]]:
        return [{"content_id": cid, "source_type": self.source_type.value} for cid in content_ids]

    def fetch_recent_content(self, profile: Profile, limit: int = 20) -> list[dict[str, Any]]:
        return []

    def fetch_engagement_events(self, profile: Profile, limit: int = 100) -> list[dict[str, Any]]:
        return []

    def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "provider": self.source_type.value}

    def get_capabilities(self) -> dict[str, Any]:
        return {"import_from_snapshot": True}


class CsvJsonImportMetricsProvider(BaseMetricsProvider):
    source_type = MetricsSourceType.CSV_JSON_IMPORT

    def fetch_profile_metrics(self, profile: Profile) -> dict[str, Any]:
        return {"profile_id": profile.id, "source_type": self.source_type.value}

    def fetch_content_metrics(self, profile: Profile, content_ids: list[str]) -> list[dict[str, Any]]:
        return [{"content_id": item, "source_type": self.source_type.value} for item in content_ids]

    def fetch_recent_content(self, profile: Profile, limit: int = 20) -> list[dict[str, Any]]:
        return []

    def fetch_engagement_events(self, profile: Profile, limit: int = 100) -> list[dict[str, Any]]:
        return []

    def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "provider": self.source_type.value}

    def get_capabilities(self) -> dict[str, Any]:
        return {"file_import": [".json", ".csv"]}

    @staticmethod
    def read_file(path: Path) -> list[dict[str, Any]]:
        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
            if isinstance(payload, dict):
                items = payload.get("items")
                if isinstance(items, list):
                    return [item for item in items if isinstance(item, dict)]
            return []
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8", newline="") as fh:
                return list(csv.DictReader(fh))
        raise ValueError(f"Unsupported import format: {path.suffix}")


class ManualMetricsProvider(BaseMetricsProvider):
    source_type = MetricsSourceType.MANUAL

    def fetch_profile_metrics(self, profile: Profile) -> dict[str, Any]:
        return {"profile_id": profile.id, "source_type": self.source_type.value, "mode": "manual"}

    def fetch_content_metrics(self, profile: Profile, content_ids: list[str]) -> list[dict[str, Any]]:
        return [{"content_id": cid, "source_type": self.source_type.value} for cid in content_ids]

    def fetch_recent_content(self, profile: Profile, limit: int = 20) -> list[dict[str, Any]]:
        return []

    def fetch_engagement_events(self, profile: Profile, limit: int = 100) -> list[dict[str, Any]]:
        return []

    def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "provider": self.source_type.value}

    def get_capabilities(self) -> dict[str, Any]:
        return {"manual_entry": True}


class DemoMetricsProvider(BaseMetricsProvider):
    source_type = MetricsSourceType.DEMO

    def fetch_profile_metrics(self, profile: Profile) -> dict[str, Any]:
        return {
            "profile_id": profile.id,
            "source_type": self.source_type.value,
            "follower_count": 1000,
            "total_views_window": 20000,
        }

    def fetch_content_metrics(self, profile: Profile, content_ids: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "content_id": cid,
                "source_type": self.source_type.value,
                "views": 1000 + (index * 250),
                "likes": 80 + (index * 15),
                "comments_count": 8 + index,
                "shares": 4 + index,
                "favorites": 5 + index,
            }
            for index, cid in enumerate(content_ids)
        ]

    def fetch_recent_content(self, profile: Profile, limit: int = 20) -> list[dict[str, Any]]:
        return []

    def fetch_engagement_events(self, profile: Profile, limit: int = 100) -> list[dict[str, Any]]:
        return []

    def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "provider": self.source_type.value}

    def get_capabilities(self) -> dict[str, Any]:
        return {"demo_seed": True}


class MetricsProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[MetricsSourceType, BaseMetricsProvider] = {
            MetricsSourceType.OFFICIAL_API: OfficialApiMetricsProvider(),
            MetricsSourceType.IMPORTED_SNAPSHOT: ImportedSnapshotMetricsProvider(),
            MetricsSourceType.CSV_JSON_IMPORT: CsvJsonImportMetricsProvider(),
            MetricsSourceType.MANUAL: ManualMetricsProvider(),
            MetricsSourceType.DEMO: DemoMetricsProvider(),
        }

    def get(self, source_type: MetricsSourceType) -> BaseMetricsProvider:
        return self._providers[source_type]

    def list_capabilities(self) -> dict[str, dict[str, Any]]:
        return {key.value: provider.get_capabilities() for key, provider in self._providers.items()}
