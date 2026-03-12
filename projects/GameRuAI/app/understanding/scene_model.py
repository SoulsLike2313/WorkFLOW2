from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SceneGroup:
    scene_id: str
    line_ids: list[str] = field(default_factory=list)
    speaker_ids: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class SceneModelService:
    def build_scene_groups(self, scenes: list[dict], entry_map: dict[str, dict]) -> list[SceneGroup]:
        groups: list[SceneGroup] = []
        for row in scenes:
            scene_id = str(row.get("scene_id") or "")
            line_ids = [str(line_id) for line_id in row.get("line_ids", [])]
            speakers = sorted(
                {
                    str(entry_map.get(line_id, {}).get("speaker_id") or "")
                    for line_id in line_ids
                    if str(entry_map.get(line_id, {}).get("speaker_id") or "")
                }
            )
            groups.append(
                SceneGroup(
                    scene_id=scene_id,
                    line_ids=line_ids,
                    speaker_ids=speakers,
                    metadata={
                        "title": row.get("title", ""),
                        "location": row.get("location", ""),
                        "line_count": len(line_ids),
                    },
                )
            )
        return groups

