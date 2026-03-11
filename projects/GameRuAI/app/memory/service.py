from __future__ import annotations

from app.storage.repositories import RepositoryHub

from .fuzzy import similarity


class TranslationMemoryService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def lookup(self, project_id: int, source_lang: str, source_text: str) -> list[dict]:
        candidates = self.repo.list_translation_memory(project_id, source_lang=source_lang)
        ranked = []
        for cand in candidates:
            score = similarity(source_text, cand["source_text"])
            if score >= 0.65:
                ranked.append(
                    {
                        "tm_id": cand["id"],
                        "source_text": cand["source_text"],
                        "target_text": cand["target_text"],
                        "score": round(score, 4),
                        "quality_score": cand["quality_score"],
                        "use_count": cand["use_count"],
                    }
                )
        ranked.sort(key=lambda item: (item["score"], item["quality_score"], item["use_count"]), reverse=True)
        return ranked[:5]

    def remember(
        self,
        project_id: int,
        source_text: str,
        target_text: str,
        source_lang: str,
        quality_score: float,
    ) -> None:
        self.repo.add_translation_memory(project_id, source_text, target_text, source_lang, quality_score)
