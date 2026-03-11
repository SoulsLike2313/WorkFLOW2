from __future__ import annotations

from app.glossary.models import GlossaryTerm
from app.glossary.service import GlossaryService
from app.storage.repositories import RepositoryHub


class FeedbackService:
    def __init__(self, repo: RepositoryHub, glossary_service: GlossaryService):
        self.repo = repo
        self.glossary_service = glossary_service

    def apply_correction(
        self,
        *,
        project_id: int,
        entry_id: int,
        corrected_text: str,
        user_note: str | None = None,
        add_to_glossary: tuple[str, str, str] | None = None,
    ) -> None:
        entry = self.repo.get_entry(entry_id)
        source_lang = str(entry.get("detected_lang") if entry else "unknown")
        self.repo.apply_correction(
            project_id=project_id,
            entry_id=entry_id,
            corrected_text=corrected_text,
            user_note=user_note,
            source_lang=source_lang,
        )
        if add_to_glossary:
            source_term, target_term, lang = add_to_glossary
            self.glossary_service.add_term(
                project_id,
                GlossaryTerm(source_term=source_term, target_term=target_term, source_lang=lang, priority=20),
            )
        self.repo.add_adaptation_event(
            project_id,
            event_type="feedback_applied",
            event_scope="translation",
            event_ref=str(entry_id),
            details={"user_note": user_note or "", "corrected_text": corrected_text},
        )
