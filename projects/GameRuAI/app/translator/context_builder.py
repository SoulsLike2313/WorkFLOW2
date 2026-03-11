from __future__ import annotations

from app.core.context_models import TranslationContext
from app.storage.repositories import RepositoryHub


class TranslationContextBuilder:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def build(
        self,
        *,
        project_id: int,
        entry_id: int,
        style_preset: str = "neutral",
        scene_index: dict[str, str] | None = None,
        neighbor_window: int = 1,
    ) -> TranslationContext:
        entry = self.repo.get_entry(entry_id)
        if not entry:
            return TranslationContext(style_preset=style_preset)

        line_id = str(entry.get("line_id") or "")
        file_path = str(entry.get("file_path") or "")
        file_group = file_path.split("/", 1)[0] if "/" in file_path else "root"
        neighbors = self.repo.get_neighbor_texts(project_id, entry_id, window=neighbor_window)
        scene_id = None
        if scene_index:
            scene_id = scene_index.get(line_id)

        return TranslationContext(
            speaker_id=str(entry.get("speaker_id") or "") or None,
            scene_id=scene_id,
            neighboring_lines=neighbors,
            line_type=str(entry.get("context_type") or "unknown"),
            file_group=file_group,
            style_preset=style_preset or "neutral",
        )
