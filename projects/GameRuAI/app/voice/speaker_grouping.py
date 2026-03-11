from __future__ import annotations

from collections import defaultdict
from typing import Any


class SpeakerGroupingService:
    def build_groups(self, linked_entries: list[dict]) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "speaker_id": "unknown",
                "group_label": "unknown",
                "line_count": 0,
                "linked_count": 0,
                "broken_links": 0,
                "avg_confidence": 0.0,
                "scene_ids": set(),
                "_confidence_sum": 0.0,
            }
        )

        for row in linked_entries:
            speaker_id = str(row.get("speaker_id") or "unknown")
            node = grouped[speaker_id]
            node["speaker_id"] = speaker_id
            node["group_label"] = f"speaker:{speaker_id}"
            node["line_count"] += 1
            if row.get("voice_link"):
                node["linked_count"] += 1
            if not row.get("link_valid", True):
                node["broken_links"] += 1
            confidence = float(row.get("link_confidence") or 0.0)
            node["_confidence_sum"] += confidence
            scene_id = str(row.get("scene_id") or "")
            if scene_id:
                node["scene_ids"].add(scene_id)

        out: list[dict[str, Any]] = []
        for speaker_id, node in grouped.items():
            line_count = max(1, int(node["line_count"]))
            avg_confidence = round(node["_confidence_sum"] / line_count, 3)
            out.append(
                {
                    "speaker_id": speaker_id,
                    "group_label": node["group_label"],
                    "line_count": int(node["line_count"]),
                    "linked_count": int(node["linked_count"]),
                    "broken_links": int(node["broken_links"]),
                    "scene_count": len(node["scene_ids"]),
                    "scene_ids": sorted(node["scene_ids"]),
                    "avg_confidence": avg_confidence,
                }
            )
        out.sort(key=lambda item: (-item["line_count"], item["speaker_id"]))
        return out

