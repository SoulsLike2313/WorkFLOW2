from __future__ import annotations

import time

from app.core.context_models import TranslationContext
from app.core.enums import TranslationStatus
from app.core.models import TranslationDecision
from app.memory.service import TranslationMemoryService
from app.translator.base import BackendUnavailableError
from app.translator.glossary_injector import GlossaryInjector
from app.translator.memory_lookup import MemoryLookup
from app.translator.postprocess import postprocess_translation
from app.translator.quality_score import score_translation
from app.translator.router import TranslatorRouter


class RealtimeOrchestrator:
    def __init__(
        self,
        *,
        translator_router: TranslatorRouter,
        glossary_injector: GlossaryInjector,
        memory_lookup: MemoryLookup,
        memory_service: TranslationMemoryService,
    ):
        self.translator_router = translator_router
        self.glossary_injector = glossary_injector
        self.memory_lookup = memory_lookup
        self.memory_service = memory_service

    def translate_entry(
        self,
        *,
        project_id: int,
        entry_id: int,
        source_text: str,
        source_lang: str,
        backend_name: str = "local_mock",
        style: str = "neutral",
        context: TranslationContext | None = None,
    ) -> TranslationDecision:
        t0 = time.perf_counter()
        decision_log: list[str] = []
        tm_hits = self.memory_lookup.find(project_id, source_lang, source_text)

        if context and context.used():
            decision_log.append("context used: yes")
            decision_log.append(
                f"context speaker={context.speaker_id or '-'} scene={context.scene_id or '-'} "
                f"neighbors={len(context.neighboring_lines)} line_type={context.line_type} group={context.file_group}"
            )
        else:
            decision_log.append("context used: no")

        if tm_hits and tm_hits[0]["score"] >= 0.92:
            hit = tm_hits[0]
            self.memory_service.repo.mark_tm_used(hit["tm_id"])
            translated = hit["target_text"]
            decision_log.append(f"TM hit: {hit['score']}")
            latency_ms = int((time.perf_counter() - t0) * 1000)
            quality = score_translation(source_text, translated, glossary_hits=0, tm_hits=1, uncertainty=0.05)
            decision_log.append(f"latency_ms={latency_ms}")
            decision_log.append(f"quality={quality}")
            return TranslationDecision(
                entry_id=entry_id,
                source_lang=source_lang,
                translated_text=translated,
                status=TranslationStatus.TRANSLATED,
                glossary_hits=[],
                tm_hits=tm_hits,
                quality_score=quality,
                latency_ms=latency_ms,
                backend="translation_memory",
                fallback_backend=None,
                context_used=bool(context and context.used()),
                context_summary=context.as_dict() if context else {},
                uncertainty=max(0.01, 1.0 - hit["score"]),
                decision_log=decision_log,
            )

        gloss_text, glossary_hits = self.glossary_injector.inject(project_id, source_lang, source_text)
        decision_log.append(f"glossary_hits={len(glossary_hits)}")

        backend, resolution = self.translator_router.resolve(backend_name)
        active_backend = backend.name
        fallback_backend: str | None = resolution.fallback_backend if resolution.fallback_used else None
        decision_log.append(f"requested_backend={backend_name}")
        decision_log.append(f"active_backend={active_backend}")
        decision_log.append(f"fallback_used={resolution.fallback_used}")

        try:
            translated = backend.translate(
                gloss_text,
                source_lang=source_lang,
                target_lang="ru",
                style=style,
                context=context,
            )
        except BackendUnavailableError:
            fallback = self.translator_router.get("local_mock")
            translated = fallback.translate(
                gloss_text,
                source_lang=source_lang,
                target_lang="ru",
                style=style,
                context=context,
            )
            fallback_backend = fallback.name
            active_backend = fallback.name
            decision_log.append("runtime fallback due backend unavailable")
        except Exception as exc:
            fallback = self.translator_router.get("dummy")
            translated = fallback.translate(
                gloss_text,
                source_lang=source_lang,
                target_lang="ru",
                style=style,
                context=context,
            )
            fallback_backend = fallback.name
            active_backend = fallback.name
            decision_log.append(f"runtime fallback due backend error: {exc}")

        translated, post_decisions = postprocess_translation(source_text, translated)
        decision_log.extend(post_decisions)

        tm_count = 1 if tm_hits else 0
        uncertainty = 0.35 if source_lang == "unknown" else 0.18 - min(0.1, len(glossary_hits) * 0.03)
        quality = score_translation(
            source_text,
            translated,
            glossary_hits=len(glossary_hits),
            tm_hits=tm_count,
            uncertainty=max(0.02, uncertainty),
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        if uncertainty >= 0.28:
            decision_log.append("uncertainty warning: high")
        decision_log.append(f"latency_ms={latency_ms}")
        decision_log.append(f"quality={quality}")

        decision = TranslationDecision(
            entry_id=entry_id,
            source_lang=source_lang,
            translated_text=translated,
            status=TranslationStatus.TRANSLATED,
            glossary_hits=glossary_hits,
            tm_hits=tm_hits,
            quality_score=quality,
            latency_ms=latency_ms,
            backend=active_backend,
            fallback_backend=fallback_backend,
            context_used=bool(context and context.used()),
            context_summary=context.as_dict() if context else {},
            uncertainty=max(0.02, uncertainty),
            decision_log=decision_log,
        )

        if quality >= 0.55:
            self.memory_service.remember(
                project_id=project_id,
                source_text=source_text,
                target_text=translated,
                source_lang=source_lang,
                quality_score=quality,
            )
        return decision
