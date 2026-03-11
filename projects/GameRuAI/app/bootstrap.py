from __future__ import annotations

import json
import wave
from pathlib import Path
from typing import Any, Generator

from app.companion.file_watch_service import FileWatchService
from app.companion.launcher import CompanionLauncher
from app.companion.process_monitor import ProcessMonitor
from app.companion.session_registry import SessionRegistry
from app.config import AppConfig
from app.core.models import ExportResult, ScannedFile
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
from app.scanner.file_classifier import classify_file
from app.storage.db import Database
from app.storage.repositories import RepositoryHub
from app.translator.context_builder import TranslationContextBuilder
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
        self.context_builder = TranslationContextBuilder(self.repo)
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
        self.process_monitor = ProcessMonitor()
        self.session_registry = SessionRegistry(self.repo)
        self.file_watch_service = FileWatchService(self.repo)
        self.companion_launcher = CompanionLauncher(self.session_registry, self.process_monitor)

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
        return self.job_manager.run_job("scan", lambda: self.scanner.scan(project_id, game_root))

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
            game_root = self._resolve_project_game_root(project_id)
            scene_index = self._build_scene_index(game_root)
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
                decision = self.translator.translate_entry(
                    project_id=project_id,
                    entry_id=int(entry["id"]),
                    source_text=entry["source_text"],
                    source_lang=str(source_lang),
                    backend_name=backend_name,
                    style=style,
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
                self.logger.info(
                    "translation_backend_run",
                    extra={
                        "event": "translation.backend_run",
                        "project_id": project_id,
                        "entry_id": int(entry["id"]),
                        "details": {
                            "requested_backend": backend_name,
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

        return reindexed_entries

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
