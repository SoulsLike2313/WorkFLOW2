from __future__ import annotations

import json
import wave
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any, Generator

from app.assets.asset_intelligence import AssetIntelligenceCore
from app.assets.explorer_service import AssetExplorerService
from app.audio.analysis_service import AudioAnalysisService
from app.audio.source_audio_compare import compare_audio_metadata
from app.companion.file_watch_service import FileWatchService
from app.companion.launcher import CompanionLauncher
from app.companion.process_monitor import ProcessMonitor
from app.companion.session_registry import SessionRegistry
from app.config import AppConfig
from app.core.models import ExportResult, ScannedFile
from app.extractors.registry import ExtractorRegistry
from app.glossary.models import GlossaryTerm
from app.glossary.service import GlossaryService
from app.knowledge.external_reference_source import ExternalReferenceSource
from app.knowledge.glossary_source import GlossarySource
from app.knowledge.locale_rules_source import LocaleRulesSource
from app.knowledge.source_refresh import SourceRefreshService
from app.knowledge.source_registry import SourceRegistry
from app.knowledge.tm_source import TmSource
from app.knowledge.voice_profile_source import VoiceProfileSource
from app.language.detector import LanguageDetector
from app.learning.adaptation_rules import AdaptationRules
from app.learning.adaptation_engine import AdaptationEngine
from app.learning.confidence_tracking import track_confidence
from app.learning.correction_tracker import CorrectionTracker
from app.learning.correction_memory import CorrectionMemory
from app.learning.evidence_store import EvidenceStore
from app.learning.external_reference_log import ExternalReferenceLog
from app.learning.feedback_service import FeedbackService
from app.learning.history_service import HistoryService
from app.learning.regression_memory import RegressionMemory
from app.logging_setup import setup_logging
from app.memory.service import TranslationMemoryService
from app.patcher.exporter import Exporter
from app.qa.service import QaService
from app.reports.backend_diagnostics import build_backend_diagnostics
from app.reports.project_summary import build_project_summary
from app.reports.translation_report import build_translation_report
from app.runtime.batch_pipeline import BatchPipeline
from app.runtime.realtime_pipeline import RealtimePipeline
from app.runtime.session_pipeline import SessionPipeline
from app.scanner.scanner_service import ScannerService
from app.scanner.file_classifier import classify_file
from app.storage.db import Database
from app.storage.repositories import RepositoryHub
from app.sync.audio_sync import plan_audio_sync
from app.sync.rebuild_plan import build_rebuild_plan
from app.sync.subtitle_sync import plan_subtitle_sync
from app.translator.context_builder import TranslationContextBuilder
from app.translator.evidence_router import EvidenceRouter
from app.translator.glossary_injector import GlossaryInjector
from app.translator.memory_lookup import MemoryLookup
from app.translator.reference_compare import compare_with_references
from app.translator.realtime_orchestrator import RealtimeOrchestrator
from app.translator.router import TranslatorRouter
from app.translator.translation_policies import TranslationPolicies
from app.understanding.content_classifier import ContentClassifier
from app.understanding.emotion_hints import infer_emotion_hint
from app.understanding.image_text_candidates import detect_image_text_candidate
from app.understanding.language_analysis import LanguageAnalysisService
from app.understanding.scene_model import SceneModelService
from app.understanding.speaker_identity import SpeakerIdentityService
from app.understanding.subtitle_alignment import SubtitleAlignmentService
from app.voice.attempt_history import VoiceAttemptHistoryService
from app.voice.audio_post import alignment_plan
from app.voice.duration_planner import plan_duration
from app.voice.preview_player import VoicePreviewPlayer
from app.voice.quality_score import score_voice_attempt
from app.voice.dubbing_prep import build_dubbing_prep
from app.voice.speaker_profile_bank import SpeakerProfileBank
from app.voice.speaker_grouping import SpeakerGroupingService
from app.voice.speaker_profile import SpeakerProfileService
from app.voice.synthesis_mock import MockVoiceSynthesizer
from app.voice.voice_comparison import compare_source_and_generated
from app.voice.voice_sample_bank import VoiceSampleBankService
from app.voice.voice_linker import VoiceLinker
from app.workers.job_manager import JobManager


class AppServices:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = setup_logging(config.paths.logs_dir)

        self.db = Database(config.paths.db_path)
        self.db.init_schema(config.project_root / "app" / "storage" / "schema.sql")
        self.repo = RepositoryHub(self.db)
        self.job_manager = JobManager(self.repo)
        self.job_manager.mark_interrupted_jobs()

        self.extractors = ExtractorRegistry()
        self.scanner = ScannerService(self.repo)
        self.asset_explorer = AssetExplorerService(self.repo)
        self.asset_intelligence = AssetIntelligenceCore(self.repo)
        self.detector = LanguageDetector()
        self.language_analysis = LanguageAnalysisService(self.detector)
        self.content_classifier = ContentClassifier()
        self.scene_model = SceneModelService()
        self.speaker_identity = SpeakerIdentityService()
        self.subtitle_alignment = SubtitleAlignmentService()
        self.glossary_service = GlossaryService(self.repo)
        self.memory_service = TranslationMemoryService(self.repo)
        self.context_builder = TranslationContextBuilder(self.repo)
        self.translation_policies = TranslationPolicies()
        self.evidence_router = EvidenceRouter()
        self.translator = RealtimeOrchestrator(
            translator_router=TranslatorRouter(),
            glossary_injector=GlossaryInjector(self.glossary_service),
            memory_lookup=MemoryLookup(self.memory_service),
            memory_service=self.memory_service,
        )
        self.source_registry = SourceRegistry(self.repo)
        self.glossary_source = GlossarySource(self.source_registry)
        self.tm_source = TmSource(self.source_registry)
        self.locale_rules_source = LocaleRulesSource(self.source_registry)
        self.voice_profile_source = VoiceProfileSource(self.source_registry)
        self.external_reference_source = ExternalReferenceSource(self.source_registry)
        self.source_refresh = SourceRefreshService(self.source_registry)
        self.evidence_store = EvidenceStore(self.repo)
        self.correction_memory = CorrectionMemory(self.repo)
        self.adaptation_engine_v2 = AdaptationEngine()
        self.external_reference_log = ExternalReferenceLog(self.repo)
        self.regression_memory = RegressionMemory(self.repo)
        self.feedback_service = FeedbackService(self.repo, self.glossary_service)
        self.correction_tracker = CorrectionTracker(self.repo)
        self.adaptation_rules = AdaptationRules(self.repo)
        self.history_service = HistoryService(self.repo)
        self.speaker_profiles = SpeakerProfileService(self.repo)
        self.speaker_profile_bank = SpeakerProfileBank(self.repo)
        self.voice_linker = VoiceLinker(self.repo)
        self.speaker_grouping = SpeakerGroupingService()
        self.voice_sample_bank = VoiceSampleBankService(self.repo)
        self.voice_attempt_history = VoiceAttemptHistoryService(self.repo)
        self.voice_preview_player = VoicePreviewPlayer()
        self.voice_synthesizer = MockVoiceSynthesizer()
        self.audio_analysis = AudioAnalysisService()
        self.batch_pipeline = BatchPipeline()
        self.realtime_pipeline = RealtimePipeline()
        self.session_pipeline = SessionPipeline()
        self.qa_service = QaService(self.repo)
        self.exporter = Exporter(self.repo)
        self.process_monitor = ProcessMonitor()
        self.session_registry = SessionRegistry(self.repo)
        self.file_watch_service = FileWatchService(self.repo)
        self.companion_launcher = CompanionLauncher(self.session_registry, self.process_monitor)
        self._register_default_knowledge_sources()

    def close(self) -> None:
        self.db.close()

    def ensure_project(self, name: str, game_root: Path) -> dict[str, Any]:
        project = self.repo.ensure_project(name, str(game_root))
        pid = int(project.id)
        self.locale_rules_source.mark_active(pid, version="locale-rules-v1", locale="ru-RU")
        self.glossary_source.mark_active(pid, version="glossary-v1", term_count=len(self.glossary_service.list_terms(pid)))
        self.tm_source.mark_active(pid, version="tm-v1", entries_count=len(self.repo.list_translation_memory(pid)))
        self.voice_profile_source.mark_active(pid, version="voice-profiles-v1", profile_count=len(self.repo.list_voice_profiles(pid)))
        self.external_reference_source.mark_state(
            pid,
            version="reference-checks-v1",
            status="foundation_only",
            provider="internal_reference_compare",
        )
        return {"id": project.id, "name": project.name, "game_path": project.game_path}

    def list_projects(self) -> list[dict[str, Any]]:
        return [
            {"id": project.id, "name": project.name, "game_path": project.game_path}
            for project in self.repo.list_projects()
        ]

    def _resolve_project_game_root(self, project_id: int) -> Path:
        for project in self.repo.list_projects():
            if int(project.id) == int(project_id):
                return Path(project.game_path)
        return self.config.paths.fixtures_root

    def _build_scene_index(self, game_root: Path) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for scene in self.load_scenes(game_root):
            scene_id = str(scene.get("scene_id") or "")
            for line_id in scene.get("line_ids", []):
                mapping[str(line_id)] = scene_id
        return mapping

    def scan(self, project_id: int, game_root: Path) -> dict[str, Any]:
        self.repo.clear_project_runtime(project_id)

        def _run() -> dict[str, Any]:
            manifest = self.scanner.scan(project_id, game_root)
            asset_summary = self.asset_explorer.index_project_assets(project_id=project_id, game_root=game_root)
            intelligence_manifest = self.asset_intelligence.build_and_store_manifest(project_id=project_id, game_root=game_root)
            manifest["asset_index"] = asset_summary
            manifest["asset_intelligence"] = {
                "assets_total": intelligence_manifest.get("assets_total", 0),
                "by_media_type": intelligence_manifest.get("by_media_type", {}),
                "by_content_role": intelligence_manifest.get("by_content_role", {}),
            }
            return manifest

        return self.job_manager.run_job("scan", _run)

    def extract(self, project_id: int, game_root: Path) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            records = []
            for row in self.repo.list_scanned_files(project_id):
                rel_path = row["file_path"]
                file_type = str(row.get("file_type", ""))
                if file_type not in {"text", "config"}:
                    continue
                if rel_path.startswith("metadata/"):
                    continue
                path = game_root / rel_path
                extractor = self.extractors.get_for_path(path)
                if not extractor:
                    continue
                chunk = extractor.extract(path, project_id=project_id, rel_path=rel_path)
                records.extend(chunk)
            extracted = self.repo.add_extracted_entries(records)
            self._preload_voice_profiles(project_id, game_root)
            return {"entries_extracted": extracted}

        return self.job_manager.run_job("extract", _run)

    def detect_languages(self, project_id: int) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            entries = self.repo.list_entries(project_id, limit=100000)
            game_root = self._resolve_project_game_root(project_id)
            scenes = self.load_scenes(game_root)
            scene_index = self._build_scene_index(game_root)
            entry_map = {str(row.get("line_id") or ""): row for row in entries}
            content_units: list[dict[str, Any]] = []
            for entry in entries:
                insight = self.language_analysis.analyze(entry["source_text"])
                self.repo.upsert_language_detection(
                    entry_id=int(entry["id"]),
                    project_id=project_id,
                    detected_lang=insight.language,
                    confidence=insight.confidence,
                    heuristics=insight.details,
                )
                scene_id = scene_index.get(str(entry.get("line_id") or ""))
                tags = entry.get("tags_json") if isinstance(entry.get("tags_json"), list) else []
                content = self.content_classifier.classify(
                    entry_id=int(entry["id"]),
                    line_id=str(entry.get("line_id") or ""),
                    file_path=str(entry.get("file_path") or ""),
                    source_text=str(entry.get("source_text") or ""),
                    speaker_id=str(entry.get("speaker_id") or "") or None,
                    tags=tags,
                    scene_id=scene_id,
                )
                speaker = self.speaker_identity.infer(
                    entry_speaker_id=content.speaker_id,
                    metadata_speaker=str((entry.get("metadata_json") or {}).get("speaker_id") or "") or None,
                    scene_hint=scene_id,
                )
                subtitle_rel = self.subtitle_alignment.align(
                    line_id=content.line_id,
                    voice_link=str(entry.get("voice_link") or ""),
                    content_type=content.content_type,
                )
                emotion = infer_emotion_hint(str(entry.get("source_text") or ""))
                content_units.append(
                    {
                        "entry_id": content.entry_id,
                        "line_id": content.line_id,
                        "file_path": content.file_path,
                        "content_type": content.content_type,
                        "source_lang": insight.language,
                        "confidence": round((content.confidence + insight.confidence) / 2, 4),
                        "scene_id": scene_id,
                        "speaker_id": speaker.speaker_id,
                        "status": "uncertain" if insight.uncertain or insight.ambiguous else "ready",
                        "metadata": {
                        "language_uncertain": insight.uncertain,
                        "language_ambiguous": insight.ambiguous,
                        "speaker_confidence": speaker.confidence,
                        "speaker_reason": speaker.reason,
                        "subtitle_alignment": asdict(subtitle_rel),
                        "emotion_hint": emotion,
                    },
                    "provenance": "content_understanding_core",
                }
                )

            self.repo.replace_content_units(project_id, content_units)
            scene_groups = self.scene_model.build_scene_groups(scenes, entry_map)
            self.repo.replace_scene_groups_v2(
                project_id,
                [
                    {
                        "scene_id": group.scene_id,
                        "line_count": len(group.line_ids),
                        "speaker_count": len(group.speaker_ids),
                        "status": "ready",
                        "confidence": 0.78 if group.line_ids else 0.4,
                        "metadata": {
                            **group.metadata,
                            "line_ids": group.line_ids,
                            "speaker_ids": group.speaker_ids,
                        },
                    }
                    for group in scene_groups
                ],
            )
            self.evidence_store.record(
                project_id=project_id,
                evidence_type="content_understanding_pass",
                entity_ref=f"detect:{len(entries)}",
                confidence=0.75,
                status="working",
                payload={
                    "detected_entries": len(entries),
                    "content_units": len(content_units),
                    "scene_groups": len(scene_groups),
                },
            )
            return {"detected": len(entries), "content_units": len(content_units), "scene_groups": len(scene_groups)}

        return self.job_manager.run_job("detect", _run)

    def translate(self, project_id: int, *, backend_name: str = "local_mock", style: str = "neutral") -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            entries = self.repo.list_entries(project_id, limit=100000)
            game_root = self._resolve_project_game_root(project_id)
            scene_index = self._build_scene_index(game_root)
            corrections = self.repo.list_corrections(project_id, limit=2000)
            correction_refs: dict[str, list[str]] = defaultdict(list)
            for row in corrections:
                key = str(row.get("before_text") or "").strip().lower()
                value = str(row.get("after_text") or "").strip()
                if key and value:
                    correction_refs[key].append(value)
            translated = 0
            tm_reuse = 0
            glossary_reuse = 0
            corrected_rows = 0
            context_used_count = 0
            fallback_used_count = 0
            backend_usage: dict[str, int] = {}
            total_latency = 0
            for entry in entries:
                source_lang = entry.get("detected_lang") or "unknown"
                context = self.context_builder.build(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    style_preset=style,
                    scene_index=scene_index,
                )
                policy = self.translation_policies.select(source_lang=str(source_lang), context=context)
                requested_backend = backend_name
                if backend_name == "policy_auto":
                    requested_backend = policy.backend_preference[0]
                decision = self.translator.translate_entry(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    source_text=entry["source_text"],
                    source_lang=str(source_lang),
                    backend_name=requested_backend,
                    style=style,
                    context=context,
                )
                self.repo.upsert_translation(project_id, decision)
                self.repo.add_translation_backend_run(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    requested_backend=requested_backend,
                    backend_name=decision.backend,
                    fallback_backend=decision.fallback_backend,
                    latency_ms=decision.latency_ms,
                    context_used=decision.context_used,
                    fallback_used=bool(decision.fallback_backend),
                )
                references = [str(hit.get("target_text") or "") for hit in decision.tm_hits[:3] if hit.get("target_text")]
                references.extend(correction_refs.get(str(entry.get("source_text") or "").strip().lower(), [])[:3])
                reference_checks = compare_with_references(decision.translated_text, references) if references else []
                if reference_checks:
                    self.external_reference_log.record(
                        project_id=project_id,
                        entry_id=int(entry["id"]),
                        provider="internal_reference_compare",
                        payload={"checks": reference_checks},
                    )

                translation_package = self.evidence_router.build_package(
                    entry_id=int(entry["id"]),
                    source_text=str(entry["source_text"]),
                    source_lang=str(source_lang),
                    context_summary=context.as_dict() if context else {},
                    chosen_backend=decision.backend,
                    fallback_used=bool(decision.fallback_backend),
                    glossary_hits=decision.glossary_hits,
                    tm_hits=decision.tm_hits,
                    alternatives=[
                        {"backend": candidate, "note": "policy_candidate"}
                        for candidate in policy.backend_preference
                        if candidate != decision.backend
                    ][:3],
                    quality_score=decision.quality_score,
                    uncertainty=decision.uncertainty,
                    final_translation=decision.translated_text,
                    reference_checks=reference_checks,
                )
                self.repo.add_translation_package(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    backend_name=decision.backend,
                    fallback_used=bool(decision.fallback_backend),
                    confidence=translation_package.confidence,
                    quality_score=decision.quality_score,
                    status="generated",
                    package=asdict(translation_package),
                )
                conf_state = track_confidence(
                    confidence=translation_package.confidence,
                    uncertainty=decision.uncertainty,
                )
                self.evidence_store.record(
                    project_id=project_id,
                    evidence_type="translation_package",
                    entity_ref=f"entry:{int(entry['id'])}",
                    confidence=translation_package.confidence,
                    status="working",
                    payload={
                        "backend": decision.backend,
                        "fallback_backend": decision.fallback_backend,
                        "quality_score": decision.quality_score,
                        "warnings": translation_package.warnings,
                        "confidence_state": conf_state,
                    },
                )
                previous_quality = float(entry.get("quality_score") or 0.0)
                adaptation_eval = self.adaptation_engine_v2.evaluate_improvement(
                    previous_quality=previous_quality,
                    current_quality=decision.quality_score,
                )
                self.repo.add_adaptation_event(
                    project_id,
                    event_type="translation_quality_delta",
                    event_scope="translation",
                    event_ref=str(entry["id"]),
                    details=adaptation_eval,
                )
                self.logger.info(
                    "translation_backend_run",
                    extra={
                        "event": "translation.backend_run",
                        "project_id": project_id,
                        "entry_id": int(entry["id"]),
                        "details": {
                            "requested_backend": requested_backend,
                            "active_backend": decision.backend,
                            "fallback_backend": decision.fallback_backend,
                            "latency_ms": decision.latency_ms,
                            "context_used": decision.context_used,
                            "quality_score": decision.quality_score,
                        },
                    },
                )
                translated += 1
                if decision.backend == "translation_memory" or decision.tm_hits:
                    tm_reuse += 1
                if decision.glossary_hits:
                    glossary_reuse += 1
                if decision.status.value == "corrected":
                    corrected_rows += 1
                if decision.context_used:
                    context_used_count += 1
                if decision.fallback_backend:
                    fallback_used_count += 1
                backend_usage[decision.backend] = backend_usage.get(decision.backend, 0) + 1
                total_latency += decision.latency_ms
            self.repo.add_adaptation_event(
                project_id,
                event_type="batch_translation",
                event_scope="translation",
                event_ref=str(translated),
                details={"backend": backend_name, "style": style, "count": translated},
            )
            self.repo.add_adaptation_event(
                project_id,
                event_type="translation_reuse_summary",
                event_scope="translation",
                event_ref=str(translated),
                details={
                    "tm_reuse_count": tm_reuse,
                    "glossary_reuse_count": glossary_reuse,
                    "corrected_rows": corrected_rows,
                    "context_used_count": context_used_count,
                    "fallback_used_count": fallback_used_count,
                },
            )
            return {
                "translated": translated,
                "tm_reuse_count": tm_reuse,
                "glossary_reuse_count": glossary_reuse,
                "corrected_rows": corrected_rows,
                "requested_backend": backend_name,
                "backend_usage": backend_usage,
                "fallback_used_count": fallback_used_count,
                "context_used_count": context_used_count,
                "avg_latency_ms": int(total_latency / max(1, translated)),
            }

        return self.job_manager.run_job("translate", _run)

    def apply_correction(
        self,
        project_id: int,
        entry_id: int,
        corrected_text: str,
        *,
        user_note: str | None = None,
        glossary_term: tuple[str, str, str] | None = None,
    ) -> None:
        self.feedback_service.apply_correction(
            project_id=project_id,
            entry_id=entry_id,
            corrected_text=corrected_text,
            user_note=user_note,
            add_to_glossary=glossary_term,
        )
        self.evidence_store.record(
            project_id=project_id,
            evidence_type="user_correction",
            entity_ref=f"entry:{entry_id}",
            confidence=0.98,
            status="working",
            payload={
                "corrected_text": corrected_text,
                "user_note": user_note or "",
                "glossary_term": glossary_term or [],
            },
        )
        self.tm_source.mark_active(
            project_id,
            version="tm-v1",
            entries_count=len(self.repo.list_translation_memory(project_id)),
        )
        self.glossary_source.mark_active(
            project_id,
            version="glossary-v1",
            term_count=len(self.glossary_service.list_terms(project_id)),
        )

    def add_glossary_term(self, project_id: int, source: str, target: str, source_lang: str = "any") -> None:
        self.glossary_service.add_term(
            project_id,
            GlossaryTerm(source_term=source, target_term=target, source_lang=source_lang, priority=30),
        )
        self.glossary_source.mark_active(
            project_id,
            version="glossary-v1",
            term_count=len(self.glossary_service.list_terms(project_id)),
        )

    def voice_attempts(self, project_id: int, game_root: Path) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            voice_out = self.config.paths.runtime_root / "voice_outputs"
            voice_out.mkdir(parents=True, exist_ok=True)
            scene_index = self._build_scene_index(game_root)
            linked_all = self.voice_linker.analyze_links(project_id, game_root=game_root, scene_index=scene_index)
            entries = [item for item in linked_all if item.get("voice_link")]
            valid_entries = [item for item in entries if item.get("link_valid", True)]

            sample_summary = self.voice_sample_bank.rebuild(
                project_id=project_id,
                linked_entries=entries,
                game_root=game_root,
            )
            groups = self.speaker_grouping.build_groups(entries)
            self.repo.replace_speaker_groups(project_id, groups)

            profiles = self.speaker_profiles.get_profiles(project_id)
            generated = 0
            avg_alignment = 0.0
            avg_quality = 0.0
            avg_confidence = 0.0
            sync_plan_count = 0
            transcript_segments: list[dict[str, Any]] = []

            for entry in valid_entries:
                translated_text = (entry.get("translated_text") or "").strip()
                if not translated_text:
                    continue
                speaker_id = entry.get("speaker_id") or "narrator"
                profile = profiles.get(
                    speaker_id,
                    {
                        "speaker_id": speaker_id,
                        "speech_rate": 1.0,
                        "style_preset": "neutral",
                        "emotion_bias": "neutral",
                        "base_frequency": 220,
                    },
                )
                source_voice_rel = str(entry.get("voice_link"))
                source_voice_path = game_root / source_voice_rel
                source_duration = self._wav_duration_ms(source_voice_path)
                output_path = voice_out / f"{entry['line_id']}_ru.wav"

                duration_plan = plan_duration(
                    translated_text,
                    source_duration_ms=source_duration,
                    speech_rate=float(profile.get("speech_rate", 1.0)),
                    style_preset=str(profile.get("style_preset", "neutral")),
                    emotion=str(profile.get("emotion_bias", "neutral")),
                )
                synth = self.voice_synthesizer.synthesize(
                    translated_text,
                    speaker_profile=profile,
                    output_path=output_path,
                    source_duration_ms=source_duration,
                    style_override=str(profile.get("style_preset", "neutral")),
                    emotion=str(profile.get("emotion_bias", "neutral")),
                    duration_plan=duration_plan.as_dict(),
                    synthesis_mode="mock_demo_tts_stub",
                )
                alignment = alignment_plan(source_duration, int(synth["duration_ms"]))
                planner_alignment_ratio = float(duration_plan.alignment_ratio)
                dubbing_prep = build_dubbing_prep(
                    source_duration_ms=source_duration,
                    translated_text=translated_text,
                    emotion=str(profile.get("emotion_bias", "neutral")),
                    style=str(profile.get("style_preset", "neutral")),
                    speech_rate=float(profile.get("speech_rate", 1.0)),
                )
                audio_sync = plan_audio_sync(
                    source_duration_ms=source_duration,
                    generated_duration_ms=int(synth["duration_ms"]),
                )
                subtitle_sync = plan_subtitle_sync(
                    source_duration_ms=source_duration,
                    translated_text=translated_text,
                )
                rebuild_plan = build_rebuild_plan(audio_sync=audio_sync, subtitle_sync=subtitle_sync)
                quality = score_voice_attempt(
                    has_translation=True,
                    alignment_ratio=float(alignment["ratio"]),
                    style_match=True,
                )
                confidence = round(
                    max(
                        0.1,
                        min(
                            0.99,
                            (float(entry.get("link_confidence") or 0.4) * 0.45)
                            + (float(duration_plan.confidence) * 0.35)
                            + (quality * 0.2),
                        ),
                    ),
                    3,
                )
                from app.core.enums import VoiceAttemptStatus
                from app.core.models import VoiceAttempt

                try:
                    output_voice_path = str(output_path.relative_to(self.config.paths.repo_root))
                except ValueError:
                    output_voice_path = str(output_path)

                attempt = VoiceAttempt(
                    entry_id=int(entry["id"]),
                    speaker_id=speaker_id,
                    source_voice_path=source_voice_rel,
                    output_voice_path=output_voice_path,
                    status=VoiceAttemptStatus.GENERATED,
                    quality_score=quality,
                    duration_source_ms=source_duration,
                    duration_output_ms=int(synth["duration_ms"]),
                    metadata={
                        "voice_mode": "mock_demo",
                        "synthesis_mode": "mock_demo_tts_stub",
                        "profile": profile,
                        "synthesis": synth,
                        "alignment": alignment,
                        "duration_plan": duration_plan.as_dict(),
                        "dubbing_prep": dubbing_prep,
                        "audio_sync": audio_sync,
                        "subtitle_sync": subtitle_sync,
                        "rebuild_plan": rebuild_plan,
                        "linking": {
                            "strategy": entry.get("linking_strategy", "speaker_id+metadata+scene"),
                            "reason": entry.get("link_reason", ""),
                            "confidence": float(entry.get("link_confidence") or 0.0),
                            "valid": bool(entry.get("link_valid", True)),
                            "scene_id": entry.get("scene_id", ""),
                        },
                        "confidence_score": confidence,
                    },
                )
                self.repo.add_voice_attempt(project_id, attempt)
                source_analysis = self.audio_analysis.analyze(
                    source_voice_path,
                    line_id=str(entry.get("line_id") or ""),
                    transcript_text=str(entry.get("source_text") or ""),
                )
                generated_analysis = self.audio_analysis.analyze(
                    output_path,
                    line_id=str(entry.get("line_id") or ""),
                    transcript_text=translated_text,
                )
                audio_compare = compare_source_and_generated(
                    source_analysis.get("summary", {}),
                    generated_analysis.get("summary", {}),
                )
                self.repo.add_audio_analysis_result(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    source_file=source_voice_rel,
                    generated_file=output_voice_path,
                    source_duration_ms=int(source_analysis.get("summary", {}).get("duration_ms", source_duration)),
                    generated_duration_ms=int(generated_analysis.get("summary", {}).get("duration_ms", synth["duration_ms"])),
                    delta_ms=int(audio_compare.get("delta_ms", 0)),
                    quality_score=float(audio_compare.get("quality", quality)),
                    confidence=confidence,
                    status=str(audio_compare.get("status", "aligned")),
                    payload={
                        "source_summary": source_analysis.get("summary", {}),
                        "generated_summary": generated_analysis.get("summary", {}),
                        "comparison": audio_compare,
                    },
                )
                self.repo.add_sync_plan(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    line_id=str(entry.get("line_id") or ""),
                    source_duration_ms=source_duration,
                    target_duration_ms=int(synth["duration_ms"]),
                    delta_ms=int(audio_sync.get("delta_ms", 0)),
                    recommended_adjustment=str(audio_sync.get("recommended_adjustment", "none")),
                    confidence=float(audio_sync.get("confidence", 0.0)),
                    status=str(audio_sync.get("status", "needs_review")),
                    payload={
                        "audio_sync": audio_sync,
                        "subtitle_sync": subtitle_sync,
                        "rebuild_plan": rebuild_plan,
                        "dubbing_prep": dubbing_prep,
                    },
                )
                sync_plan_count += 1
                for segment in source_analysis.get("transcript_links", []):
                    transcript_segments.append(
                        {
                            "entry_id": int(entry["id"]),
                            "line_id": str(entry.get("line_id") or ""),
                            "segment_id": int(segment.get("segment_id") or 0),
                            "start_ms": int(segment.get("start_ms") or 0),
                            "end_ms": int(segment.get("end_ms") or 0),
                            "link_confidence": float(segment.get("link_confidence") or 0.0),
                            "provenance": "audio_analysis",
                            "metadata": {
                                "token_estimate": segment.get("token_estimate", 0),
                                "source_file": source_voice_rel,
                            },
                        }
                    )
                self.voice_attempt_history.record(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    speaker_id=str(speaker_id),
                    source_file=source_voice_rel,
                    source_duration_ms=source_duration,
                    generated_file=output_voice_path,
                    synthesis_mode="mock_demo_tts_stub",
                    alignment_ratio=planner_alignment_ratio,
                    quality_score=quality,
                    confidence_score=confidence,
                    metadata={
                        "line_id": entry.get("line_id", ""),
                        "scene_id": entry.get("scene_id", ""),
                        "duration_plan": duration_plan.as_dict(),
                        "alignment": alignment,
                    },
                )
                generated += 1
                avg_alignment += float(alignment["ratio"])
                avg_quality += quality
                avg_confidence += confidence
                self.evidence_store.record(
                    project_id=project_id,
                    evidence_type="voice_attempt",
                    entity_ref=f"entry:{int(entry['id'])}",
                    confidence=confidence,
                    status="working",
                    payload={
                        "speaker_id": speaker_id,
                        "synthesis_mode": "mock_demo_tts_stub",
                        "quality_score": quality,
                        "alignment_ratio": planner_alignment_ratio,
                        "sync_status": audio_sync.get("status", "n/a"),
                    },
                )

            self.repo.replace_transcript_segments(project_id, transcript_segments)

            self.repo.add_adaptation_event(
                project_id,
                event_type="voice_batch",
                event_scope="voice",
                event_ref=str(generated),
                details={
                    "generated": generated,
                    "linked_total": len(entries),
                    "valid_links": len(valid_entries),
                    "broken_links": len([item for item in entries if not item.get("link_valid", True)]),
                    "sample_bank_total": sample_summary["samples_total"],
                    "speaker_groups": len(groups),
                    "sync_plans": sync_plan_count,
                    "transcript_segments": len(transcript_segments),
                    "synthesis_mode": "mock_demo_tts_stub",
                },
            )
            return {
                "voice_attempts": generated,
                "linked_total": len(entries),
                "valid_links": len(valid_entries),
                "broken_links": len([item for item in entries if not item.get("link_valid", True)]),
                "speaker_groups": len(groups),
                "sample_bank_total": sample_summary["samples_total"],
                "sync_plans": sync_plan_count,
                "transcript_segments": len(transcript_segments),
                "synthesis_mode": "mock_demo_tts_stub",
                "avg_alignment_ratio": round(avg_alignment / max(1, generated), 3),
                "avg_quality_score": round(avg_quality / max(1, generated), 3),
                "avg_confidence_score": round(avg_confidence / max(1, generated), 3),
            }

        return self.job_manager.run_job("voice", _run)

    def run_qa(self, project_id: int) -> dict[str, Any]:
        findings = self.qa_service.run(project_id)
        return {
            "findings_total": len(findings),
            "errors": len([f for f in findings if f.severity.value == "error"]),
            "warnings": len([f for f in findings if f.severity.value == "warning"]),
        }

    def export(self, project_id: int, output_dir: Path | None = None) -> ExportResult:
        target = output_dir or (self.config.paths.exports_dir / f"export_{project_id}")
        target.mkdir(parents=True, exist_ok=True)
        job_id = self.repo.create_export_job(project_id, str(target))
        try:
            result = self.job_manager.run_job("export", lambda: self.exporter.export(project_id, target))
            self.repo.finish_export_job(job_id, "done", str(result.manifest_path), str(result.diff_report_path))
            return result
        except Exception:
            self.repo.finish_export_job(job_id, "failed", "", "")
            raise

    def pipeline_end_to_end(self, project_name: str, game_root: Path) -> dict[str, Any]:
        project = self.ensure_project(project_name, game_root)
        pid = int(project["id"])
        summary = {
            "project": project,
            "scan": self.scan(pid, game_root),
            "extract": self.extract(pid, game_root),
            "detect": self.detect_languages(pid),
            "translate": self.translate(pid),
            "voice": self.voice_attempts(pid, game_root),
            "qa": self.run_qa(pid),
        }
        export_result = self.export(pid)
        summary["export"] = {
            "dir": str(export_result.output_dir),
            "manifest": str(export_result.manifest_path),
            "diff_report": str(export_result.diff_report_path),
            "translated_entries": export_result.translated_entries,
            "voiced_entries": export_result.voiced_entries,
        }
        summary["reports"] = self.generate_reports(pid)
        return summary

    def learning_snapshot(self, project_id: int) -> dict[str, Any]:
        return {
            "corrections": self.correction_tracker.list_recent(project_id, limit=100),
            "adaptation_summary": self.adaptation_rules.summarize(project_id),
            "translation_history": self.history_service.translation_history(project_id, limit=200),
            "improvement_examples": self.repo.list_learning_improvements(project_id, limit=200),
            "terms": self.glossary_service.list_terms(project_id),
            "tm": self.repo.list_translation_memory(project_id),
            "evidence": self.repo.list_evidence_records(project_id, limit=200),
            "knowledge_sources": self.repo.list_knowledge_sources(project_id, limit=200),
            "external_references": self.repo.list_external_reference_events(project_id, limit=200),
        }

    def load_scenes(self, game_root: Path) -> list[dict[str, Any]]:
        scenes_path = game_root / "metadata" / "scenes.json"
        if not scenes_path.exists():
            return []
        return json.loads(scenes_path.read_text(encoding="utf-8-sig"))

    def live_demo_stream(
        self,
        *,
        project_id: int,
        game_root: Path,
        scene_id: str,
        backend_name: str = "local_mock",
    ) -> Generator[dict[str, Any], None, None]:
        scenes = {scene["scene_id"]: scene for scene in self.load_scenes(game_root)}
        scene = scenes.get(scene_id)
        if not scene:
            return
        line_ids = scene.get("line_ids", [])
        all_entries = {row["line_id"]: row for row in self.repo.list_entries(project_id, limit=100000)}
        scene_index = self._build_scene_index(game_root)

        for line_id in line_ids:
            entry = all_entries.get(line_id)
            if not entry:
                continue
            if not entry.get("detected_lang"):
                detect = self.detector.detect(entry["source_text"])
                self.repo.upsert_language_detection(
                    int(entry["id"]), project_id, detect.language, detect.confidence, detect.details
                )
                entry["detected_lang"] = detect.language
                entry["language_confidence"] = detect.confidence

            context = self.context_builder.build(
                project_id=project_id,
                entry_id=int(entry["id"]),
                style_preset="neutral",
                scene_index=scene_index,
            )

            decision = self.translator.translate_entry(
                project_id=project_id,
                entry_id=int(entry["id"]),
                source_text=entry["source_text"],
                source_lang=str(entry.get("detected_lang") or "unknown"),
                backend_name=backend_name,
                context=context,
            )
            self.repo.upsert_translation(project_id, decision)
            self.repo.add_translation_backend_run(
                project_id=project_id,
                entry_id=int(entry["id"]),
                requested_backend=backend_name,
                backend_name=decision.backend,
                fallback_backend=decision.fallback_backend,
                latency_ms=decision.latency_ms,
                context_used=decision.context_used,
                fallback_used=bool(decision.fallback_backend),
            )

            voice_status = "skipped"
            if entry.get("voice_link"):
                self.voice_attempts(project_id, game_root)
                voice_status = "generated_mock"

            yield {
                "line_id": entry["line_id"],
                "source_text": entry["source_text"],
                "detected_lang": entry.get("detected_lang") or "unknown",
                "translated_text": decision.translated_text,
                "translation_quality": decision.quality_score,
                "voice_status": voice_status,
                "uncertainty": decision.uncertainty,
                "decision_log": decision.decision_log,
                "context_used": decision.context_used,
                "active_backend": decision.backend,
                "fallback_backend": decision.fallback_backend or "",
            }

    def launch_companion(
        self,
        *,
        project_id: int,
        executable_path: Path,
        watched_path: Path,
        args: list[str] | None = None,
    ) -> dict[str, Any]:
        session = self.companion_launcher.launch(
            project_id=project_id,
            executable_path=executable_path,
            watched_path=watched_path,
            args=args,
            cwd=watched_path,
        )
        self.file_watch_service.start_watch(project_id=project_id, session_id=session.session_id, watched_path=watched_path)
        self.repo.add_adaptation_event(
            project_id,
            event_type="companion_session_started",
            event_scope="companion",
            event_ref=session.session_id,
            details={"executable_path": str(executable_path), "watched_path": str(watched_path)},
        )
        return self.session_registry.get(session.session_id) or {}

    def poll_companion(self, *, project_id: int, session_id: str, game_root: Path) -> dict[str, Any]:
        status = self.process_monitor.status(session_id)
        ended = status.startswith("exited")
        self.session_registry.update(session_id, status=status, pid=self.process_monitor.pid(session_id), ended=ended)
        events = self.file_watch_service.poll(session_id)
        changed_paths = [str(event["file_path"]) for event in events if event["event_type"] in {"created", "modified"}]
        quick_reindexed_entries = 0
        if changed_paths:
            quick_reindexed_entries = self.quick_reindex(project_id=project_id, game_root=game_root, changed_paths=changed_paths)
            self.repo.add_adaptation_event(
                project_id,
                event_type="companion_quick_reindex",
                event_scope="companion",
                event_ref=session_id,
                details={"changed_paths": changed_paths, "reindexed_entries": quick_reindexed_entries},
            )
        return {
            "session": self.session_registry.get(session_id),
            "status": status,
            "events": events,
            "quick_reindexed_entries": quick_reindexed_entries,
            "all_events": self.repo.list_watched_file_events(project_id, session_id=session_id, limit=300),
        }

    def stop_companion(self, *, project_id: int, session_id: str) -> dict[str, Any]:
        status = self.process_monitor.stop(session_id)
        self.session_registry.update(session_id, status=status, pid=self.process_monitor.pid(session_id), ended=True)
        self.file_watch_service.stop_watch(session_id)
        self.process_monitor.unregister(session_id)
        self.repo.add_adaptation_event(
            project_id,
            event_type="companion_session_stopped",
            event_scope="companion",
            event_ref=session_id,
            details={"status": status},
        )
        return self.session_registry.get(session_id) or {}

    def list_companion_sessions(self, project_id: int) -> list[dict[str, Any]]:
        return self.session_registry.list_by_project(project_id)

    def asset_snapshot(self, project_id: int, *, limit: int = 5000) -> dict[str, Any]:
        assets = self.asset_explorer.list_index(project_id, limit=limit)
        reports = self.asset_explorer.list_archive_reports(project_id, suspected_only=False, limit=1000)
        manifest_assets = self.repo.list_asset_manifest(project_id, limit=limit)
        image_candidates = []
        for row in assets:
            metadata = row.get("metadata_json") or {}
            abs_path = Path(str(metadata.get("absolute_path") or ""))
            if not abs_path:
                continue
            candidate = detect_image_text_candidate(abs_path)
            if candidate.get("is_image"):
                image_candidates.append(
                    {
                        "file_path": row.get("file_path"),
                        "candidate_text_overlay": candidate.get("candidate_text_overlay"),
                        "confidence": candidate.get("confidence"),
                    }
                )
        return {
            "assets": assets,
            "asset_manifest": manifest_assets,
            "archive_reports": reports,
            "image_text_candidates": image_candidates,
            "tree": self.asset_explorer.build_tree(project_id),
            "totals": {
                "assets": len(assets),
                "manifest_assets": len(manifest_assets),
                "preview_ready": len([row for row in assets if row.get("preview_status") == "ready"]),
                "metadata_only": len([row for row in assets if row.get("preview_status") != "ready"]),
                "suspected_containers": len([row for row in reports if row.get("suspected_container")]),
                "image_text_candidates": len([row for row in image_candidates if row.get("candidate_text_overlay")]),
            },
        }

    def asset_details(self, project_id: int, file_path: str) -> dict[str, Any]:
        return self.asset_explorer.get_resource_details(project_id, file_path)

    def voice_snapshot(self, project_id: int, *, game_root: Path) -> dict[str, Any]:
        attempts = self.repo.list_voice_attempts(project_id)
        for row in attempts:
            meta = row.get("metadata_json") or {}
            row["synthesis_mode"] = str(meta.get("synthesis_mode") or meta.get("voice_mode") or "unknown")
            row["confidence_score"] = float(meta.get("confidence_score") or 0.0)
            align = meta.get("alignment") or {}
            row["alignment_ratio"] = float(align.get("ratio") or 0.0)
            plan = meta.get("duration_plan") or {}
            row["duration_action"] = str(plan.get("recommended_action") or "")

        history = self.voice_attempt_history.list_recent(project_id, limit=600)
        groups = self.repo.list_speaker_groups(project_id, limit=200)
        samples = self.repo.list_voice_sample_bank(project_id, limit=5000)
        audio_results = self.repo.list_audio_analysis_results(project_id, limit=1000)
        sync_plans = self.repo.list_sync_plans(project_id, limit=1000)
        return {
            "attempts": attempts,
            "history": history,
            "speaker_groups": groups,
            "sample_bank": samples,
            "audio_analysis": audio_results,
            "sync_plans": sync_plans,
            "summary": {
                "attempts_total": len(attempts),
                "history_total": len(history),
                "speaker_groups": len(groups),
                "sample_bank_total": len(samples),
                "audio_analysis_total": len(audio_results),
                "sync_plans_total": len(sync_plans),
                "broken_links": len(
                    [
                        item
                        for item in samples
                        if not bool((item.get("metadata_json") or {}).get("link_valid", True))
                    ]
                ),
                "synthesis_mode": "mock_demo_tts_stub",
            },
        }

    def voice_preview(self, source_voice_path: str, generated_voice_path: str, *, game_root: Path) -> dict[str, Any]:
        return self.voice_preview_player.preview_payload(
            source_voice_path=source_voice_path,
            generated_voice_path=generated_voice_path,
            game_root=game_root,
            repo_root=self.config.paths.repo_root,
        )

    def generate_reports(self, project_id: int) -> dict[str, Any]:
        entries = self.repo.list_entries(project_id, limit=100000)
        translations = self.repo.list_translations(project_id)
        backend_runs = self.repo.list_translation_backend_runs(project_id, limit=100000)
        voice_attempts = self.repo.list_voice_attempts(project_id, limit=100000)
        voice_history = self.repo.list_voice_attempt_history(project_id=project_id, limit=100000)
        speaker_groups = self.repo.list_speaker_groups(project_id, limit=1000)
        qa_findings = self.repo.list_qa_findings(project_id, limit=100000)
        export_jobs = self.repo.list_export_jobs(project_id, limit=1000)
        companion_sessions = self.repo.list_companion_sessions(project_id, limit=1000)
        watched_events = self.repo.list_watched_file_events(project_id, limit=100000)
        asset_rows = self.repo.list_asset_index(project_id, limit=100000)
        asset_manifest = self.repo.list_asset_manifest(project_id, limit=100000)
        content_units = self.repo.list_content_units(project_id, limit=100000)
        sync_plans = self.repo.list_sync_plans(project_id, limit=100000)
        translation_packages = self.repo.list_translation_packages(project_id, limit=100000)
        knowledge_sources = self.repo.list_knowledge_sources(project_id, limit=1000)
        evidence_records = self.repo.list_evidence_records(project_id, limit=100000)
        audio_analysis_results = self.repo.list_audio_analysis_results(project_id, limit=100000)

        translation_report = build_translation_report(entries, translations)
        backend_diag = build_backend_diagnostics(backend_runs)
        summary = build_project_summary(
            entries=entries,
            translations=translations,
            translation_report=translation_report,
            voice_attempts=voice_attempts,
            voice_history=voice_history,
            speaker_groups=speaker_groups,
            qa_findings=qa_findings,
            export_jobs=export_jobs,
            companion_sessions=companion_sessions,
            watched_events=watched_events,
            asset_index=asset_rows,
        )
        multimodal_core_summary = {
            "asset_manifest_total": len(asset_manifest),
            "content_units_total": len(content_units),
            "translation_packages_total": len(translation_packages),
            "sync_plans_total": len(sync_plans),
            "audio_analysis_total": len(audio_analysis_results),
            "knowledge_sources_total": len(knowledge_sources),
            "evidence_records_total": len(evidence_records),
        }
        summary["multimodal_core"] = multimodal_core_summary

        language_payload = summary.get("language", {})
        self.repo.upsert_language_report(
            project_id=project_id,
            report_name="language_distribution",
            lines_total=len(entries),
            uncertain_count=int(language_payload.get("uncertain_count", 0)),
            uncertain_rate=round(int(language_payload.get("uncertain_count", 0)) / max(1, len(entries)), 4),
            payload=language_payload,
        )
        self.repo.replace_backend_diagnostics(project_id, backend_diag)
        self.repo.add_project_report(project_id=project_id, report_type="translation_report", payload=translation_report)
        self.repo.add_project_report(project_id=project_id, report_type="project_summary", payload=summary)
        self.repo.add_project_report(
            project_id=project_id,
            report_type="multimodal_core_summary",
            payload=multimodal_core_summary,
        )
        self.repo.add_quality_snapshot(
            project_id=project_id,
            snapshot_type="quality_dashboard",
            payload=summary.get("quality_dashboard", {}),
        )

        return {
            "translation_report": translation_report,
            "backend_diagnostics": backend_diag,
            "project_summary": summary,
            "quality_dashboard": summary.get("quality_dashboard", {}),
        }

    def reports_snapshot(self, project_id: int) -> dict[str, Any]:
        reports = self.repo.list_project_reports(project_id, limit=40)
        language_reports = self.repo.list_language_reports(project_id, limit=40)
        quality_snapshots = self.repo.list_quality_snapshots(project_id, limit=40)
        translation_report = next((item for item in reports if item.get("report_type") == "translation_report"), None)
        project_summary = next((item for item in reports if item.get("report_type") == "project_summary"), None)
        multimodal_core = next((item for item in reports if item.get("report_type") == "multimodal_core_summary"), None)
        return {
            "translation_report": (translation_report or {}).get("payload_json", {}),
            "project_summary": (project_summary or {}).get("payload_json", {}),
            "multimodal_core_summary": (multimodal_core or {}).get("payload_json", {}),
            "language_reports": language_reports,
            "quality_snapshots": quality_snapshots,
            "quality_dashboard": ((project_summary or {}).get("payload_json", {}) or {}).get("quality_dashboard", {}),
        }

    def diagnostics_snapshot(self, project_id: int) -> dict[str, Any]:
        return {
            "backend_diagnostics": self.repo.list_backend_diagnostics(project_id, limit=200),
            "project_reports": self.repo.list_project_reports(project_id, limit=80),
            "quality_snapshots": self.repo.list_quality_snapshots(project_id, limit=80),
        }

    def language_intelligence_snapshot(self, project_id: int) -> dict[str, Any]:
        content_units = self.repo.list_content_units(project_id, limit=100000)
        entries = self.repo.list_entries(project_id, limit=100000)
        manifest = self.repo.list_asset_manifest(project_id, limit=100000)
        language_counter = Counter(str(row.get("source_lang") or row.get("detected_lang") or "unknown") for row in content_units or entries)
        uncertain_rows = [
            row
            for row in content_units
            if str(row.get("status") or "") == "uncertain"
            or float(row.get("confidence") or 0.0) < 0.75
        ]
        translated = len([row for row in entries if str(row.get("translated_text") or "").strip()])
        bottlenecks = Counter(
            str(row.get("source_lang") or "unknown")
            for row in content_units
            if str(row.get("status") or "") != "ready"
        )
        return {
            "language_distribution": dict(sorted(language_counter.items(), key=lambda item: (-item[1], item[0]))),
            "uncertain_units": uncertain_rows[:300],
            "coverage": {
                "entries_total": len(entries),
                "translated_total": translated,
                "coverage_rate": round(translated / max(1, len(entries)), 4),
            },
            "bottlenecks": dict(sorted(bottlenecks.items(), key=lambda item: (-item[1], item[0]))),
            "asset_media_distribution": dict(Counter(str(row.get("media_type") or "unknown") for row in manifest)),
        }

    def audio_analysis_lab_snapshot(self, project_id: int) -> dict[str, Any]:
        audio_results = self.repo.list_audio_analysis_results(project_id, limit=1000)
        transcript_segments = self.repo.list_transcript_segments(project_id, limit=2000)
        speaker_groups = self.repo.list_speaker_groups(project_id, limit=500)
        voice_attempts = self.repo.list_voice_attempts(project_id, limit=1000)
        sync_plans = self.repo.list_sync_plans(project_id, limit=1000)
        comparison_status = Counter(str(row.get("status") or "unknown") for row in audio_results)
        avg_quality = round(
            sum(float(row.get("quality_score") or 0.0) for row in audio_results) / max(1, len(audio_results)),
            4,
        )
        return {
            "audio_results": audio_results,
            "transcript_segments": transcript_segments,
            "speaker_groups": speaker_groups,
            "voice_attempts": voice_attempts,
            "sync_plans": sync_plans,
            "comparison_status": dict(comparison_status),
            "avg_quality": avg_quality,
            "synthesis_mode": "mock_demo_tts_stub",
            "lab_status": "working" if audio_results else "partial",
        }

    def evidence_review_snapshot(self, project_id: int) -> dict[str, Any]:
        packages = self.repo.list_translation_packages(project_id, limit=1200)
        evidence = self.repo.list_evidence_records(project_id, limit=1200)
        references = self.repo.list_external_reference_events(project_id, limit=500)
        corrections = self.repo.list_corrections(project_id, limit=500)
        adaptation = self.repo.list_adaptation_events(project_id, limit=500)
        return {
            "translation_packages": packages,
            "evidence_records": evidence,
            "external_references": references,
            "corrections": corrections,
            "adaptation_events": adaptation,
            "knowledge_sources": self.repo.list_knowledge_sources(project_id, limit=200),
        }

    def sync_review_snapshot(self, project_id: int) -> dict[str, Any]:
        sync_plans = self.repo.list_sync_plans(project_id, limit=1200)
        high_risk = [row for row in sync_plans if str((row.get("payload_json") or {}).get("audio_sync", {}).get("sync_risk")) == "high"]
        subtitle_issues = [
            row
            for row in sync_plans
            if str((row.get("payload_json") or {}).get("subtitle_sync", {}).get("status")) in {"too_fast_for_reading", "borderline"}
        ]
        return {
            "sync_plans": sync_plans,
            "high_risk_count": len(high_risk),
            "subtitle_issue_count": len(subtitle_issues),
            "export_risk_summary": {
                "high": len(high_risk),
                "medium_or_low": max(0, len(sync_plans) - len(high_risk)),
            },
        }

    def hud_snapshot(
        self,
        project_id: int,
        *,
        game_root: Path | None = None,
        current_companion_session_id: str | None = None,
        requested_backend: str = "local_mock",
    ) -> dict[str, Any]:
        project_row = next((p for p in self.repo.list_projects() if int(p.id) == int(project_id)), None)
        if not project_row:
            return {}

        resolved_game_root = Path(project_row.game_path) if project_row.game_path else (game_root or self.config.paths.fixtures_root)
        scanned_files = self.repo.list_scanned_files(project_id)
        entries = self.repo.list_entries(project_id, limit=100000)
        translations = self.repo.list_translations(project_id)
        backend_runs = self.repo.list_translation_backend_runs(project_id, limit=8000)
        voice_attempts = self.repo.list_voice_attempts(project_id, limit=100000)
        voice_samples = self.repo.list_voice_sample_bank(project_id, limit=100000)
        qa_findings = self.repo.list_qa_findings(project_id, limit=100000)
        export_jobs = self.repo.list_export_jobs(project_id, limit=300)
        reports = self.repo.list_project_reports(project_id, limit=20)
        diagnostics = self.repo.list_backend_diagnostics(project_id, limit=20)
        sessions = self.repo.list_companion_sessions(project_id, limit=120)
        translation_packages = self.repo.list_translation_packages(project_id, limit=5000)
        evidence_records = self.repo.list_evidence_records(project_id, limit=5000)
        sync_plans = self.repo.list_sync_plans(project_id, limit=5000)
        knowledge_sources = self.repo.list_knowledge_sources(project_id, limit=500)

        entries_total = len(entries)
        detected_total = len([row for row in entries if str(row.get("detected_lang") or "").strip() != ""])
        translated_total = len([row for row in translations if (row.get("translated_text") or "").strip()])
        voice_linked_total = len([row for row in entries if bool(row.get("has_voice_link"))])
        uncertain_total = len(
            [
                row
                for row in entries
                if str(row.get("detected_lang") or "unknown") in {"unknown", "mixed"}
                or float(row.get("language_confidence") or 0.0) < 0.75
            ]
        )

        language_distribution = Counter(str(row.get("detected_lang") or "unknown") for row in entries)
        languages_total = len(language_distribution)
        language_map = ", ".join(
            f"{lang}:{count}" for lang, count in sorted(language_distribution.items(), key=lambda item: (-item[1], item[0]))[:8]
        ) or "n/a"
        lang_pending = Counter()
        for row in entries:
            lang = str(row.get("detected_lang") or "unknown")
            has_translation = bool(str(row.get("translated_text") or "").strip())
            low_confidence = float(row.get("language_confidence") or 0.0) < 0.75
            if (not has_translation) or low_confidence or lang in {"unknown", "mixed"}:
                lang_pending[lang] += 1
        language_bottlenecks = [
            f"{lang}:{count}" for lang, count in sorted(lang_pending.items(), key=lambda item: (-item[1], item[0]))[:4]
        ]

        active_backend = backend_runs[0]["backend_name"] if backend_runs else requested_backend
        fallback_backend = next(
            (str(row.get("fallback_backend")) for row in backend_runs if str(row.get("fallback_backend") or "").strip()),
            "-",
        )
        qa_errors = len([row for row in qa_findings if str(row.get("severity") or "").lower() == "error"])
        qa_warnings = len([row for row in qa_findings if str(row.get("severity") or "").lower() == "warning"])

        companion = None
        if current_companion_session_id:
            companion = next((row for row in sessions if str(row.get("session_id")) == current_companion_session_id), None)
        if companion is None and sessions:
            companion = sessions[0]
        companion_status = str((companion or {}).get("process_status") or "idle")
        companion_session_id = str((companion or {}).get("session_id") or "no-session")

        def _stage(done: bool, partial: bool = False) -> str:
            if done:
                return "done"
            if partial:
                return "partial"
            return "pending"

        pipeline_stage = {
            "scan": _stage(bool(scanned_files)),
            "extract": _stage(entries_total > 0),
            "detect": _stage(detected_total >= max(1, entries_total), detected_total > 0),
            "translate": _stage(translated_total >= max(1, entries_total), translated_total > 0),
            "voice": _stage(voice_linked_total > 0 and len(voice_attempts) >= voice_linked_total, len(voice_attempts) > 0),
            "export": _stage(any(str(row.get("status")) == "done" for row in export_jobs)),
            "reports": _stage(bool(reports)),
            "diagnostics": _stage(bool(diagnostics)),
        }

        next_action = "review QA/report results"
        if pipeline_stage["scan"] == "pending":
            next_action = "run Scan to index files"
        elif pipeline_stage["extract"] == "pending":
            next_action = "run Extract Strings"
        elif pipeline_stage["detect"] == "pending":
            next_action = "run Detect Language"
        elif pipeline_stage["translate"] == "pending":
            next_action = "run Translate to Russian"
        elif uncertain_total > 0:
            next_action = "review uncertain language lines"
        elif pipeline_stage["voice"] == "pending":
            next_action = "generate voice preparation attempts"
        elif pipeline_stage["export"] == "pending":
            next_action = "export patch output"
        elif qa_errors > 0:
            next_action = "fix critical QA errors before export"

        return {
            "project_id": int(project_row.id),
            "project_name": project_row.name,
            "game_path": str(resolved_game_root),
            "active_backend": active_backend,
            "fallback_backend": fallback_backend,
            "language_map": language_map,
            "language_bottlenecks": language_bottlenecks,
            "pipeline_stage": pipeline_stage,
            "entries_total": entries_total,
            "languages_total": languages_total,
            "translated_total": translated_total,
            "uncertain_total": uncertain_total,
            "voice_attempts_total": len(voice_attempts),
            "voice_broken_links": len(
                [row for row in voice_samples if not bool((row.get("metadata_json") or {}).get("link_valid", True))]
            ),
            "qa_errors": qa_errors,
            "qa_warnings": qa_warnings,
            "reports_status": "ready" if reports else "missing",
            "diagnostics_status": "ready" if diagnostics else "missing",
            "companion_status": companion_status,
            "companion_session_id": companion_session_id,
            "translation_coverage_rate": round(translated_total / max(1, entries_total), 4),
            "uncertain_rate": round(uncertain_total / max(1, entries_total), 4),
            "translation_packages_total": len(translation_packages),
            "evidence_records_total": len(evidence_records),
            "sync_plans_total": len(sync_plans),
            "knowledge_sources_total": len(knowledge_sources),
            "next_action": next_action,
        }

    def language_hub_snapshot(self, project_id: int, *, requested_backend: str = "local_mock") -> dict[str, Any]:
        entries = self.repo.list_entries(project_id, limit=100000)
        backend_runs = self.repo.list_translation_backend_runs(project_id, limit=15000)
        corrections = self.repo.list_corrections(project_id, limit=100000)
        export_jobs = self.repo.list_export_jobs(project_id, limit=1000)

        if not entries:
            return {
                "overview": [],
                "queue": [],
                "review": [],
                "stress": [],
                "flow_summary": [],
                "backend_status": {
                    "active_backend": requested_backend,
                    "fallback_backend": "-",
                    "available_backends": self.translator.translator_router.available_backends(),
                    "avg_latency_ms": 0,
                    "p95_latency_ms": 0,
                    "context_usage_rate": 0.0,
                    "fallback_used": 0,
                    "mode": "mock/fallback",
                },
                "languages_total": 0,
                "uncertain_total": 0,
                "detected_total": 0,
                "translated_total": 0,
                "reviewed_total": 0,
                "exported_total": 0,
            }

        entry_lang: dict[int, str] = {}
        lang_stats: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "lines": 0,
                "translated": 0,
                "needs_review": 0,
                "confidence_sum": 0.0,
            }
        )
        source_targets: dict[str, set[str]] = defaultdict(set)
        review_rows: list[dict[str, Any]] = []
        stress_rows: list[dict[str, Any]] = []

        for row in entries:
            entry_id = int(row.get("id") or 0)
            lang = str(row.get("detected_lang") or "unknown")
            entry_lang[entry_id] = lang
            source_text = str(row.get("source_text") or "")
            translated_text = str(row.get("translated_text") or "")
            confidence = float(row.get("language_confidence") or 0.0)
            context_type = str(row.get("context_type") or "unknown")
            placeholders = row.get("placeholders_json") or []
            tags = row.get("tags_json") or []

            stats = lang_stats[lang]
            stats["lines"] += 1
            stats["confidence_sum"] += confidence
            if translated_text.strip():
                stats["translated"] += 1
            uncertain = lang in {"unknown", "mixed"} or confidence < 0.75
            if uncertain:
                stats["needs_review"] += 1
                review_rows.append(
                    {
                        "entry_id": entry_id,
                        "line_id": row.get("line_id", ""),
                        "lang": lang,
                        "confidence": round(confidence, 3),
                        "issue": "mixed/unknown" if lang in {"unknown", "mixed"} else "low_confidence",
                        "file_path": row.get("file_path", ""),
                    }
                )

            if context_type in {"ui", "system", "tutorial"} and len(source_text.strip()) <= 4:
                review_rows.append(
                    {
                        "entry_id": entry_id,
                        "line_id": row.get("line_id", ""),
                        "lang": lang,
                        "confidence": round(confidence, 3),
                        "issue": "short_ui_string",
                        "file_path": row.get("file_path", ""),
                    }
                )

            source_key = source_text.strip().lower()
            if source_key and translated_text.strip():
                source_targets[source_key].add(translated_text.strip().lower())

            source_len = len(source_text)
            translated_len = len(translated_text)
            placeholder_count = len(placeholders)
            tag_count = len(tags)
            overflow_risk = translated_len > max(40, int(source_len * 1.35))
            long_line = source_len >= 90 or translated_len >= 110
            if overflow_risk or long_line or placeholder_count > 0 or tag_count > 0:
                risk_tokens: list[str] = []
                if overflow_risk:
                    risk_tokens.append("overflow")
                if long_line:
                    risk_tokens.append("long")
                if placeholder_count > 0:
                    risk_tokens.append("placeholders")
                if tag_count > 0:
                    risk_tokens.append("tags")
                stress_rows.append(
                    {
                        "line_id": row.get("line_id", ""),
                        "lang": lang,
                        "source_len": source_len,
                        "translated_len": translated_len,
                        "placeholders": placeholder_count,
                        "tags": tag_count,
                        "risk": ",".join(risk_tokens),
                        "file_path": row.get("file_path", ""),
                    }
                )

        repeated_conflicts = {
            source_key for source_key, targets in source_targets.items() if len(targets) > 1 and source_key
        }
        if repeated_conflicts:
            for row in entries:
                source_key = str(row.get("source_text") or "").strip().lower()
                if source_key in repeated_conflicts:
                    review_rows.append(
                        {
                            "entry_id": int(row.get("id") or 0),
                            "line_id": row.get("line_id", ""),
                            "lang": str(row.get("detected_lang") or "unknown"),
                            "confidence": round(float(row.get("language_confidence") or 0.0), 3),
                            "issue": "repeated_translation_conflict",
                            "file_path": row.get("file_path", ""),
                        }
                    )

        last_processed: dict[str, str] = {}
        for run in backend_runs:
            entry_id = int(run.get("entry_id") or 0)
            lang = entry_lang.get(entry_id)
            if not lang:
                continue
            created_at = str(run.get("created_at") or "")
            if created_at and created_at > last_processed.get(lang, ""):
                last_processed[lang] = created_at

        overview_rows = []
        queue_rows = []
        for lang, stats in sorted(lang_stats.items(), key=lambda item: (-item[1]["lines"], item[0])):
            lines = int(stats["lines"])
            translated = int(stats["translated"])
            needs_review = int(stats["needs_review"])
            avg_conf = round(float(stats["confidence_sum"]) / max(1, lines), 3)
            coverage = round(translated / max(1, lines), 3)
            pending = max(0, lines - translated)

            if pending == 0 and needs_review == 0:
                queue_status = "done"
                priority = "low"
                next_step = "none"
            elif needs_review > 0:
                queue_status = "review"
                priority = "high" if (needs_review / max(1, lines)) >= 0.25 else "medium"
                next_step = "open Language Review block"
            else:
                queue_status = "queued"
                priority = "high" if pending > 30 else "medium"
                next_step = "run Translate to Russian"

            overview_rows.append(
                {
                    "language": lang,
                    "lines": lines,
                    "avg_confidence": avg_conf,
                    "translated": translated,
                    "needs_review": needs_review,
                    "coverage": coverage,
                }
            )
            queue_rows.append(
                {
                    "language": lang,
                    "pending": pending,
                    "priority": priority,
                    "status": queue_status,
                    "errors": needs_review,
                    "last_processed": last_processed.get(lang, "-"),
                    "next_step": next_step,
                }
            )

        latencies = [int(run.get("latency_ms") or 0) for run in backend_runs]
        p95_latency_ms = 0
        avg_latency_ms = 0
        if latencies:
            sorted_lat = sorted(latencies)
            avg_latency_ms = int(sum(sorted_lat) / max(1, len(sorted_lat)))
            idx = max(0, min(len(sorted_lat) - 1, int(len(sorted_lat) * 0.95) - 1))
            p95_latency_ms = int(sorted_lat[idx])

        active_backend = backend_runs[0]["backend_name"] if backend_runs else requested_backend
        fallback_backend = next(
            (str(run.get("fallback_backend")) for run in backend_runs if str(run.get("fallback_backend") or "").strip()),
            "-",
        )
        context_used_count = len([run for run in backend_runs if bool(run.get("context_used"))])
        fallback_used_count = len([run for run in backend_runs if bool(run.get("fallback_used"))])
        mode = "advanced"
        if active_backend in {"local_mock", "dummy"}:
            mode = "mock/fallback"
        elif fallback_used_count > 0:
            mode = "fallback"

        entries_total = len(entries)
        detected_total = len([row for row in entries if str(row.get("detected_lang") or "").strip() != ""])
        normalized_total = len([row for row in entries if str(row.get("source_text") or "").strip() != ""])
        translated_total = len([row for row in entries if str(row.get("translated_text") or "").strip() != ""])
        reviewed_total = len(corrections)
        exported_total = len([row for row in export_jobs if str(row.get("status") or "") == "done"])

        def _flow_stage(stage: str, done_count: int, total: int, notes: str) -> dict[str, Any]:
            if total <= 0:
                status = "pending"
            elif done_count >= total:
                status = "done"
            elif done_count > 0:
                status = "partial"
            else:
                status = "pending"
            return {
                "stage": stage,
                "progress": f"{done_count}/{total}",
                "status": status,
                "notes": notes,
            }

        flow_rows = [
            _flow_stage("detected", detected_total, entries_total, "language detection completed"),
            _flow_stage("normalized", normalized_total, entries_total, "placeholder/tag normalization tracked"),
            _flow_stage("translated", translated_total, entries_total, "RU translation availability"),
            _flow_stage("reviewed", reviewed_total, translated_total or entries_total, "manual corrections and review"),
            _flow_stage("exported", exported_total, max(1, exported_total), "patch export history"),
        ]

        review_rows.sort(
            key=lambda item: (
                0 if str(item.get("issue")) in {"mixed/unknown", "low_confidence"} else 1,
                str(item.get("file_path") or ""),
                str(item.get("line_id") or ""),
            )
        )
        stress_rows.sort(
            key=lambda item: (
                0 if "overflow" in str(item.get("risk")) else 1,
                -int(item.get("translated_len") or 0),
            )
        )

        return {
            "overview": overview_rows[:40],
            "queue": queue_rows[:40],
            "review": review_rows[:220],
            "stress": stress_rows[:220],
            "flow_summary": flow_rows,
            "backend_status": {
                "active_backend": active_backend,
                "fallback_backend": fallback_backend,
                "available_backends": self.translator.translator_router.available_backends(),
                "avg_latency_ms": avg_latency_ms,
                "p95_latency_ms": p95_latency_ms,
                "context_usage_rate": round(context_used_count / max(1, len(backend_runs)), 3),
                "fallback_used": fallback_used_count,
                "mode": mode,
            },
            "languages_total": len(lang_stats),
            "uncertain_total": len(
                [row for row in entries if str(row.get("detected_lang") or "unknown") in {"unknown", "mixed"}]
            ),
            "detected_total": detected_total,
            "translated_total": translated_total,
            "reviewed_total": reviewed_total,
            "exported_total": exported_total,
        }

    def quick_reindex(self, *, project_id: int, game_root: Path, changed_paths: list[str]) -> int:
        reindexed_entries = 0
        scene_index = self._build_scene_index(game_root)
        for rel_path in changed_paths:
            path = game_root / rel_path
            if not path.exists() or not path.is_file():
                continue

            file_type, file_ext = classify_file(path)
            if file_type not in {"text", "config"} or rel_path.startswith("metadata/"):
                continue

            scanned_file = ScannedFile(
                project_id=project_id,
                file_path=rel_path,
                file_type=file_type,
                file_ext=file_ext,
                size_bytes=path.stat().st_size,
                sha1=self._sha1_file(path),
                manifest_group=rel_path.split("/", 1)[0] if "/" in rel_path else "root",
            )
            self.repo.upsert_scanned_file(scanned_file)

            if file_type not in {"text", "config"} or rel_path.startswith("metadata/"):
                continue

            extractor = self.extractors.get_for_path(path)
            if not extractor:
                continue
            self.repo.clear_entries_for_file(project_id, rel_path)
            records = extractor.extract(path, project_id=project_id, rel_path=rel_path)
            if not records:
                continue
            self.repo.add_extracted_entries(records)
            reindexed_entries += len(records)

            updated_entries = [entry for entry in self.repo.list_entries(project_id, search=rel_path, limit=100000) if entry.get("file_path") == rel_path]
            for entry in updated_entries:
                detect = self.detector.detect(entry["source_text"])
                self.repo.upsert_language_detection(
                    entry_id=int(entry["id"]),
                    project_id=project_id,
                    detected_lang=detect.language,
                    confidence=detect.confidence,
                    heuristics=detect.details,
                )
                context = self.context_builder.build(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    style_preset="neutral",
                    scene_index=scene_index,
                )
                decision = self.translator.translate_entry(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    source_text=entry["source_text"],
                    source_lang=detect.language,
                    backend_name="local_mock",
                    style="neutral",
                    context=context,
                )
                self.repo.upsert_translation(project_id, decision)
                self.repo.add_translation_backend_run(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    requested_backend="local_mock",
                    backend_name=decision.backend,
                    fallback_backend=decision.fallback_backend,
                    latency_ms=decision.latency_ms,
                    context_used=decision.context_used,
                    fallback_used=bool(decision.fallback_backend),
                )

        # Keep asset research index in sync for changed files (any file type).
        if changed_paths:
            self.asset_explorer.index_project_assets(
                project_id=project_id,
                game_root=game_root,
                changed_paths=list(dict.fromkeys(changed_paths)),
            )

        return reindexed_entries

    def _register_default_knowledge_sources(self) -> None:
        # Global app-level defaults are recorded per project when project exists.
        # This function keeps the intent explicit for architecture transparency.
        return

    @staticmethod
    def _wav_duration_ms(path: Path) -> int:
        if not path.exists():
            return 1500
        try:
            with wave.open(str(path), "rb") as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                return int((frames / max(1, rate)) * 1000)
        except Exception:
            return 1500

    @staticmethod
    def _sha1_file(path: Path) -> str:
        import hashlib

        hasher = hashlib.sha1()
        with path.open("rb") as file_handle:
            while True:
                chunk = file_handle.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def _preload_voice_profiles(self, project_id: int, game_root: Path) -> None:
        profile_file = game_root / "metadata" / "voice_profiles.json"
        if profile_file.exists():
            self.speaker_profiles.load_from_metadata(project_id, profile_file)
        self.voice_profile_source.mark_active(
            project_id,
            version="voice-profiles-v1",
            profile_count=len(self.repo.list_voice_profiles(project_id)),
        )
