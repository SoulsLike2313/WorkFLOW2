from __future__ import annotations

import json
import wave
from pathlib import Path
from typing import Any, Generator

from app.config import AppConfig
from app.core.models import ExportResult
from app.extractors.registry import ExtractorRegistry
from app.glossary.models import GlossaryTerm
from app.glossary.service import GlossaryService
from app.language.detector import LanguageDetector
from app.learning.adaptation_rules import AdaptationRules
from app.learning.correction_tracker import CorrectionTracker
from app.learning.feedback_service import FeedbackService
from app.learning.history_service import HistoryService
from app.logging_setup import setup_logging
from app.memory.service import TranslationMemoryService
from app.patcher.exporter import Exporter
from app.qa.service import QaService
from app.scanner.scanner_service import ScannerService
from app.storage.db import Database
from app.storage.repositories import RepositoryHub
from app.translator.glossary_injector import GlossaryInjector
from app.translator.memory_lookup import MemoryLookup
from app.translator.realtime_orchestrator import RealtimeOrchestrator
from app.translator.router import TranslatorRouter
from app.voice.audio_post import alignment_plan
from app.voice.quality_score import score_voice_attempt
from app.voice.speaker_profile import SpeakerProfileService
from app.voice.synthesis_mock import MockVoiceSynthesizer
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
        self.detector = LanguageDetector()
        self.glossary_service = GlossaryService(self.repo)
        self.memory_service = TranslationMemoryService(self.repo)
        self.translator = RealtimeOrchestrator(
            translator_router=TranslatorRouter(),
            glossary_injector=GlossaryInjector(self.glossary_service),
            memory_lookup=MemoryLookup(self.memory_service),
            memory_service=self.memory_service,
        )
        self.feedback_service = FeedbackService(self.repo, self.glossary_service)
        self.correction_tracker = CorrectionTracker(self.repo)
        self.adaptation_rules = AdaptationRules(self.repo)
        self.history_service = HistoryService(self.repo)
        self.speaker_profiles = SpeakerProfileService(self.repo)
        self.voice_linker = VoiceLinker(self.repo)
        self.voice_synthesizer = MockVoiceSynthesizer()
        self.qa_service = QaService(self.repo)
        self.exporter = Exporter(self.repo)

    def close(self) -> None:
        self.db.close()

    def ensure_project(self, name: str, game_root: Path) -> dict[str, Any]:
        project = self.repo.ensure_project(name, str(game_root))
        return {"id": project.id, "name": project.name, "game_path": project.game_path}

    def list_projects(self) -> list[dict[str, Any]]:
        return [
            {"id": project.id, "name": project.name, "game_path": project.game_path}
            for project in self.repo.list_projects()
        ]

    def scan(self, project_id: int, game_root: Path) -> dict[str, Any]:
        self.repo.clear_project_runtime(project_id)
        return self.job_manager.run_job("scan", lambda: self.scanner.scan(project_id, game_root))

    def extract(self, project_id: int, game_root: Path) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            records = []
            for row in self.repo.list_scanned_files(project_id):
                rel_path = row["file_path"]
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
            for entry in entries:
                result = self.detector.detect(entry["source_text"])
                self.repo.upsert_language_detection(
                    entry_id=int(entry["id"]),
                    project_id=project_id,
                    detected_lang=result.language,
                    confidence=result.confidence,
                    heuristics=result.details,
                )
            return {"detected": len(entries)}

        return self.job_manager.run_job("detect", _run)

    def translate(self, project_id: int, *, backend_name: str = "local_mock", style: str = "neutral") -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            entries = self.repo.list_entries(project_id, limit=100000)
            translated = 0
            tm_reuse = 0
            glossary_reuse = 0
            corrected_rows = 0
            for entry in entries:
                source_lang = entry.get("detected_lang") or "unknown"
                decision = self.translator.translate_entry(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    source_text=entry["source_text"],
                    source_lang=str(source_lang),
                    backend_name=backend_name,
                    style=style,
                )
                self.repo.upsert_translation(project_id, decision)
                translated += 1
                if decision.backend == "translation_memory" or decision.tm_hits:
                    tm_reuse += 1
                if decision.glossary_hits:
                    glossary_reuse += 1
                if decision.status.value == "corrected":
                    corrected_rows += 1
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
                },
            )
            return {
                "translated": translated,
                "tm_reuse_count": tm_reuse,
                "glossary_reuse_count": glossary_reuse,
                "corrected_rows": corrected_rows,
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

    def add_glossary_term(self, project_id: int, source: str, target: str, source_lang: str = "any") -> None:
        self.glossary_service.add_term(
            project_id,
            GlossaryTerm(source_term=source, target_term=target, source_lang=source_lang, priority=30),
        )

    def voice_attempts(self, project_id: int, game_root: Path) -> dict[str, Any]:
        def _run() -> dict[str, Any]:
            voice_out = self.config.paths.runtime_root / "voice_outputs"
            voice_out.mkdir(parents=True, exist_ok=True)
            entries = self.voice_linker.get_voiced_entries(project_id)
            profiles = self.speaker_profiles.get_profiles(project_id)
            generated = 0

            for entry in entries:
                translated_text = (entry.get("translated_text") or "").strip()
                if not translated_text:
                    continue
                speaker_id = entry.get("speaker_id") or "narrator"
                profile = profiles.get(speaker_id, {"speaker_id": speaker_id, "speech_rate": 1.0, "style_preset": "neutral"})
                source_voice_rel = str(entry.get("voice_link"))
                source_voice_path = game_root / source_voice_rel
                source_duration = self._wav_duration_ms(source_voice_path)
                output_path = voice_out / f"{entry['line_id']}_ru.wav"
                synth = self.voice_synthesizer.synthesize(
                    translated_text,
                    speaker_profile=profile,
                    output_path=output_path,
                    source_duration_ms=source_duration,
                )
                alignment = alignment_plan(source_duration, int(synth["duration_ms"]))
                quality = score_voice_attempt(
                    has_translation=True,
                    alignment_ratio=float(alignment["ratio"]),
                    style_match=True,
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
                        "voice_mode": "mock_stub",
                        "profile": profile,
                        "synthesis": synth,
                        "alignment": alignment,
                    },
                )
                self.repo.add_voice_attempt(project_id, attempt)
                generated += 1

            self.repo.add_adaptation_event(
                project_id,
                event_type="voice_batch",
                event_scope="voice",
                event_ref=str(generated),
                details={"generated": generated},
            )
            return {"voice_attempts": generated}

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
        return summary

    def learning_snapshot(self, project_id: int) -> dict[str, Any]:
        return {
            "corrections": self.correction_tracker.list_recent(project_id, limit=100),
            "adaptation_summary": self.adaptation_rules.summarize(project_id),
            "translation_history": self.history_service.translation_history(project_id, limit=200),
            "improvement_examples": self.repo.list_learning_improvements(project_id, limit=200),
            "terms": self.glossary_service.list_terms(project_id),
            "tm": self.repo.list_translation_memory(project_id),
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

            decision = self.translator.translate_entry(
                project_id=project_id,
                entry_id=int(entry["id"]),
                source_text=entry["source_text"],
                source_lang=str(entry.get("detected_lang") or "unknown"),
                backend_name=backend_name,
            )
            self.repo.upsert_translation(project_id, decision)

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
            }

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

    def _preload_voice_profiles(self, project_id: int, game_root: Path) -> None:
        profile_file = game_root / "metadata" / "voice_profiles.json"
        if profile_file.exists():
            self.speaker_profiles.load_from_metadata(project_id, profile_file)
