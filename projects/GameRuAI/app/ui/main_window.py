from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.bootstrap import AppServices

from .asset_explorer_panel import AssetExplorerPanel
from .audio_analysis_lab_panel import AudioAnalysisLabPanel
from .companion_panel import CompanionPanel
from .diagnostics_panel import DiagnosticsPanel
from .evidence_review_panel import EvidenceReviewPanel
from .entries_panel import EntriesPanel
from .export_panel import ExportPanel
from .glossary_panel import GlossaryPanel
from .jobs_panel import JobsPanel
from .language_intelligence_panel import LanguageIntelligencePanel
from .language_hub_panel import LanguageHubPanel
from .learning_panel import LearningPanel
from .live_demo_panel import LiveDemoPanel
from .project_wizard import ProjectWizardPanel
from .qa_panel import QaPanel
from .reports_panel import ReportsPanel
from .scan_panel import ScanPanel
from .sync_review_panel import SyncReviewPanel
from .translation_panel import TranslationPanel
from .voice_panel import VoicePanel
from .hud_panel import ProductHudPanel


class MainWindow(QMainWindow):
    def __init__(self, services: AppServices):
        super().__init__()
        self.services = services
        self.current_project_id: int | None = None
        self.current_game_root: Path = services.config.paths.fixtures_root
        self.current_companion_session_id: str | None = None
        self._live_rows: list[dict[str, Any]] = []
        self._live_idx = 0
        self._live_timer = QTimer(self)
        self._live_timer.timeout.connect(self._consume_live_row)

        self.setWindowTitle("GameRuAI - Desktop Demo MVP")
        self.resize(1600, 960)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        self.hud_panel = ProductHudPanel()
        self.tabs = QTabWidget()
        root_layout.addWidget(self.hud_panel)
        root_layout.addWidget(self.tabs)
        self.setCentralWidget(root)

        self.project_panel = ProjectWizardPanel(services.config.paths.fixtures_root)
        self.scan_panel = ScanPanel()
        self.asset_panel = AssetExplorerPanel()
        self.entries_panel = EntriesPanel()
        self.language_hub_panel = LanguageHubPanel()
        self.translation_panel = TranslationPanel()
        self.voice_panel = VoicePanel()
        self.learning_panel = LearningPanel()
        self.glossary_panel = GlossaryPanel()
        self.qa_panel = QaPanel()
        self.reports_panel = ReportsPanel()
        self.diagnostics_panel = DiagnosticsPanel()
        self.language_intelligence_panel = LanguageIntelligencePanel()
        self.audio_analysis_lab_panel = AudioAnalysisLabPanel()
        self.evidence_review_panel = EvidenceReviewPanel()
        self.sync_review_panel = SyncReviewPanel()
        self.export_panel = ExportPanel(str(services.config.paths.exports_dir))
        self.jobs_panel = JobsPanel()
        self.live_panel = LiveDemoPanel()
        self.companion_panel = CompanionPanel()

        self.tabs.addTab(self.project_panel, "Project")
        self.tabs.addTab(self.scan_panel, "Scan")
        self.tabs.addTab(self.asset_panel, "Asset Explorer")
        self.tabs.addTab(self.entries_panel, "Entries")
        self.tabs.addTab(self.language_hub_panel, "Language Hub")
        self.tabs.addTab(self.translation_panel, "Translation")
        self.tabs.addTab(self.voice_panel, "Voice")
        self.tabs.addTab(self.learning_panel, "Learning")
        self.tabs.addTab(self.glossary_panel, "Glossary")
        self.tabs.addTab(self.qa_panel, "QA")
        self.tabs.addTab(self.reports_panel, "Reports")
        self.tabs.addTab(self.diagnostics_panel, "Diagnostics")
        self.tabs.addTab(self.language_intelligence_panel, "Language Intelligence")
        self.tabs.addTab(self.audio_analysis_lab_panel, "Audio Analysis Lab")
        self.tabs.addTab(self.evidence_review_panel, "Evidence Review")
        self.tabs.addTab(self.sync_review_panel, "Sync Review")
        self.tabs.addTab(self.export_panel, "Export")
        self.tabs.addTab(self.jobs_panel, "Jobs / Logs")
        self.tabs.addTab(self.live_panel, "Live Demo")
        self.tabs.addTab(self.companion_panel, "Companion")

        self._wire_actions()
        self.refresh_all_views()

    def _wire_actions(self) -> None:
        self.project_panel.create_btn.clicked.connect(self.on_create_project)
        self.project_panel.run_pipeline_btn.clicked.connect(self.on_run_full_pipeline)
        self.hud_panel.quick_scan_btn.clicked.connect(self.on_scan)
        self.hud_panel.quick_detect_btn.clicked.connect(self.on_detect_languages)
        self.hud_panel.quick_translate_btn.clicked.connect(self.on_translate)
        self.hud_panel.quick_voice_btn.clicked.connect(self.on_voice_attempts)
        self.hud_panel.quick_export_btn.clicked.connect(self.on_export)
        self.hud_panel.quick_reports_btn.clicked.connect(self.on_generate_reports)

        self.scan_panel.scan_btn.clicked.connect(self.on_scan)
        self.scan_panel.extract_btn.clicked.connect(self.on_extract)
        self.asset_panel.refresh_btn.clicked.connect(self.on_refresh_assets)
        self.asset_panel.filter_combo.currentIndexChanged.connect(self.refresh_assets)
        self.asset_panel.resource_tree.itemSelectionChanged.connect(self.on_asset_selected)

        self.entries_panel.detect_btn.clicked.connect(self.on_detect_languages)
        self.entries_panel.refresh_btn.clicked.connect(self.refresh_entries)
        self.entries_panel.lang_filter.currentIndexChanged.connect(self.refresh_entries)
        self.entries_panel.search_edit.returnPressed.connect(self.refresh_entries)
        self.language_hub_panel.refresh_btn.clicked.connect(self.refresh_language_hub)
        self.language_hub_panel.focus_uncertain_btn.clicked.connect(self.on_language_focus_uncertain)
        self.language_hub_panel.focus_stress_btn.clicked.connect(self.on_language_focus_stress)
        self.language_hub_panel.open_translation_btn.clicked.connect(self.on_language_open_translation)

        self.translation_panel.translate_btn.clicked.connect(self.on_translate)
        self.translation_panel.apply_correction_btn.clicked.connect(self.on_apply_correction)

        self.voice_panel.generate_btn.clicked.connect(self.on_voice_attempts)
        self.voice_panel.update_profile_btn.clicked.connect(self.on_update_voice_profile)
        self.voice_panel.attempts_table.itemSelectionChanged.connect(self.on_voice_attempt_selected)

        self.learning_panel.refresh_btn.clicked.connect(self.refresh_learning)
        self.glossary_panel.add_btn.clicked.connect(self.on_add_glossary_term)
        self.qa_panel.run_btn.clicked.connect(self.on_run_qa)
        self.reports_panel.generate_btn.clicked.connect(self.on_generate_reports)
        self.reports_panel.refresh_btn.clicked.connect(self.refresh_reports)
        self.diagnostics_panel.refresh_btn.clicked.connect(self.refresh_diagnostics)
        self.language_intelligence_panel.refresh_btn.clicked.connect(self.refresh_language_intelligence)
        self.audio_analysis_lab_panel.refresh_btn.clicked.connect(self.refresh_audio_lab)
        self.evidence_review_panel.refresh_btn.clicked.connect(self.refresh_evidence_review)
        self.sync_review_panel.refresh_btn.clicked.connect(self.refresh_sync_review)
        self.export_panel.export_btn.clicked.connect(self.on_export)
        self.jobs_panel.refresh_btn.clicked.connect(self.refresh_jobs)
        self.live_panel.start_btn.clicked.connect(self.on_start_live_demo)
        self.companion_panel.pick_executable_btn.clicked.connect(self.companion_panel.choose_executable)
        self.companion_panel.pick_watch_btn.clicked.connect(self.companion_panel.choose_watched_path)
        self.companion_panel.launch_btn.clicked.connect(self.on_launch_companion)
        self.companion_panel.poll_btn.clicked.connect(self.on_poll_companion)
        self.companion_panel.stop_btn.clicked.connect(self.on_stop_companion)

    def _require_project(self) -> bool:
        if self.current_project_id is None:
            QMessageBox.warning(self, "No Project", "Create/select project first in Project tab.")
            return False
        return True

    def on_create_project(self) -> None:
        game_root = Path(self.project_panel.game_path_edit.text().strip())
        if not game_root.exists():
            QMessageBox.critical(self, "Invalid Path", f"Path does not exist: {game_root}")
            return
        project = self.services.ensure_project(self.project_panel.project_name_edit.text().strip(), game_root)
        self.current_project_id = int(project["id"])
        self.current_game_root = game_root
        self.project_panel.info_label.setText(
            f"Project ready: id={project['id']} name={project['name']} root={project['game_path']}"
        )
        self.companion_panel.watched_path_edit.setText(str(game_root))
        self.live_panel.load_scenes(self.services.load_scenes(game_root))
        self.refresh_all_views()

    def on_run_full_pipeline(self) -> None:
        game_root = Path(self.project_panel.game_path_edit.text().strip())
        if not game_root.exists():
            QMessageBox.critical(self, "Invalid Path", f"Path does not exist: {game_root}")
            return
        summary = self.services.pipeline_end_to_end(
            self.project_panel.project_name_edit.text().strip() or "GameRuAI Demo Project",
            game_root,
        )
        self.current_project_id = int(summary["project"]["id"])
        self.current_game_root = game_root
        self.live_panel.load_scenes(self.services.load_scenes(game_root))
        self.scan_panel.show_manifest(summary["scan"])
        self.project_panel.info_label.setText(
            f"Pipeline done: extracted={summary['extract']['entries_extracted']}, translated={summary['translate']['translated']}, voice={summary['voice']['voice_attempts']}"
        )
        self.translation_panel.set_backend_status(summary["translate"])
        self.refresh_all_views()

    def on_scan(self) -> None:
        if not self._require_project():
            return
        manifest = self.services.scan(self.current_project_id, self.current_game_root)
        self.scan_panel.show_manifest(manifest)
        self.statusBar().showMessage("Scan complete", 3000)
        self.refresh_assets()
        self.refresh_jobs()
        self.refresh_language_hub()
        self.refresh_hud()

    def on_extract(self) -> None:
        if not self._require_project():
            return
        result = self.services.extract(self.current_project_id, self.current_game_root)
        self.scan_panel.info_label.setText(f"Extract complete: {result['entries_extracted']} entries")
        self.refresh_entries()
        self.refresh_jobs()
        self.refresh_language_hub()
        self.refresh_hud()

    def on_detect_languages(self) -> None:
        if not self._require_project():
            return
        result = self.services.detect_languages(self.current_project_id)
        self.entries_panel.info_label.setText(f"Language detection complete: {result['detected']} rows")
        self.refresh_entries()
        self.refresh_jobs()
        self.refresh_language_hub()
        self.refresh_hud()

    def on_translate(self) -> None:
        if not self._require_project():
            return
        result = self.services.translate(
            self.current_project_id,
            backend_name=self.translation_panel.backend_combo.currentText(),
            style=self.translation_panel.style_combo.currentText(),
        )
        self.translation_panel.info_label.setText(f"Translated: {result['translated']}")
        self.translation_panel.set_backend_status(result)
        self.refresh_translations()
        self.refresh_entries()
        self.refresh_learning()
        self.refresh_reports()
        self.refresh_diagnostics()
        self.refresh_language_intelligence()
        self.refresh_evidence_review()
        self.refresh_jobs()
        self.refresh_language_hub()
        self.refresh_hud()

    def on_apply_correction(self) -> None:
        if not self._require_project():
            return
        entry_id_raw = self.translation_panel.correction_entry_id.text().strip()
        if not entry_id_raw.isdigit():
            QMessageBox.warning(self, "Invalid Entry ID", "Entry ID must be a number.")
            return
        corrected_text = self.translation_panel.correction_text.toPlainText().strip()
        if not corrected_text:
            QMessageBox.warning(self, "Invalid Correction", "Corrected text cannot be empty.")
            return
        glossary_tuple = None
        if self.translation_panel.add_glossary_check.isChecked():
            glossary_tuple = (
                self.translation_panel.glossary_source.text().strip(),
                self.translation_panel.glossary_target.text().strip(),
                self.translation_panel.glossary_lang.text().strip() or "any",
            )
            if not glossary_tuple[0] or not glossary_tuple[1]:
                QMessageBox.warning(self, "Glossary", "Glossary source/target must be filled when checkbox is enabled.")
                return
        self.services.apply_correction(
            self.current_project_id,
            int(entry_id_raw),
            corrected_text,
            user_note=self.translation_panel.correction_note.text().strip() or None,
            glossary_term=glossary_tuple,
        )
        self.refresh_translations()
        self.refresh_entries()
        self.refresh_learning()
        self.refresh_glossary()
        self.refresh_language_hub()
        self.refresh_evidence_review()
        self.refresh_language_intelligence()
        self.refresh_hud()

    def on_voice_attempts(self) -> None:
        if not self._require_project():
            return
        result = self.services.voice_attempts(self.current_project_id, self.current_game_root)
        self.voice_panel.info_label.setText(
            "Voice attempts generated: "
            f"{result['voice_attempts']} | linked={result.get('linked_total', 0)} | "
            f"broken_links={result.get('broken_links', 0)}"
        )
        self.refresh_voice()
        self.refresh_entries()
        self.refresh_learning()
        self.refresh_reports()
        self.refresh_diagnostics()
        self.refresh_audio_lab()
        self.refresh_sync_review()
        self.refresh_evidence_review()
        self.refresh_jobs()
        self.refresh_hud()

    def on_voice_attempt_selected(self) -> None:
        if self.current_project_id is None:
            return
        attempt = self.voice_panel.selected_attempt()
        if not attempt:
            return
        preview = self.services.voice_preview(
            str(attempt.get("source_voice_path") or ""),
            str(attempt.get("output_voice_path") or ""),
            game_root=self.current_game_root,
        )
        self.voice_panel.show_attempt_details(preview_payload=preview, attempt=attempt)

    def on_update_voice_profile(self) -> None:
        if not self._require_project():
            return
        speaker_id = self.voice_panel.speaker_id_edit.text().strip()
        if not speaker_id:
            QMessageBox.warning(self, "Missing speaker", "Speaker ID is required.")
            return
        patch = {
            "style_preset": self.voice_panel.style_combo.currentText(),
            "speech_rate": self.voice_panel.rate_spin.value(),
        }
        self.services.speaker_profiles.update_profile(self.current_project_id, speaker_id, patch)
        self.refresh_voice()
        self.refresh_learning()
        self.refresh_hud()

    def on_add_glossary_term(self) -> None:
        if not self._require_project():
            return
        source = self.glossary_panel.source_edit.text().strip()
        target = self.glossary_panel.target_edit.text().strip()
        lang = self.glossary_panel.lang_edit.text().strip() or "any"
        if not source or not target:
            QMessageBox.warning(self, "Glossary", "Source and target terms are required.")
            return
        self.services.add_glossary_term(self.current_project_id, source, target, lang)
        self.refresh_glossary()
        self.refresh_learning()
        self.refresh_hud()
        self.refresh_language_hub()

    def on_language_focus_uncertain(self) -> None:
        if not self._require_project():
            return
        idx = self.entries_panel.lang_filter.findText("unknown")
        if idx >= 0:
            self.entries_panel.lang_filter.setCurrentIndex(idx)
        self.entries_panel.search_edit.setText("")
        self.refresh_entries()
        self._switch_tab("Entries")
        self.statusBar().showMessage("Focused uncertain language rows in Entries.", 3000)

    def on_language_focus_stress(self) -> None:
        if not self._require_project():
            return
        self.entries_panel.lang_filter.setCurrentText("all")
        self.entries_panel.search_edit.setText("%PLAYER_NAME% {money} [E] <b>")
        self.refresh_entries()
        self._switch_tab("Entries")
        self.statusBar().showMessage("Focused localization stress rows in Entries.", 3000)

    def on_language_open_translation(self) -> None:
        if not self._require_project():
            return
        self.refresh_translations()
        self._switch_tab("Translation")
        self.statusBar().showMessage("Opened Translation workbench from Language Hub.", 2500)

    def on_run_qa(self) -> None:
        if not self._require_project():
            return
        summary = self.services.run_qa(self.current_project_id)
        self.qa_panel.info_label.setText(
            f"QA done. total={summary['findings_total']} errors={summary['errors']} warnings={summary['warnings']}"
        )
        self.refresh_qa()
        self.refresh_reports()
        self.refresh_diagnostics()
        self.refresh_language_intelligence()
        self.refresh_audio_lab()
        self.refresh_evidence_review()
        self.refresh_sync_review()
        self.refresh_hud()

    def on_generate_reports(self) -> None:
        if not self._require_project():
            return
        self.services.generate_reports(self.current_project_id)
        self.refresh_reports()
        self.refresh_diagnostics()
        self.refresh_hud()

    def on_export(self) -> None:
        if not self._require_project():
            return
        out_dir = Path(self.export_panel.path_edit.text().strip())
        result = self.services.export(self.current_project_id, out_dir)
        self.export_panel.info.setPlainText(
            "\n".join(
                [
                    f"Export directory: {result.output_dir}",
                    f"Manifest: {result.manifest_path}",
                    f"Diff report: {result.diff_report_path}",
                    f"Translated entries: {result.translated_entries}",
                    f"Voiced entries: {result.voiced_entries}",
                ]
            )
        )
        self.refresh_reports()
        self.refresh_diagnostics()
        self.refresh_sync_review()
        self.refresh_evidence_review()
        self.refresh_jobs()
        self.refresh_hud()

    def on_launch_companion(self) -> None:
        if not self._require_project():
            return
        executable = Path(self.companion_panel.executable_edit.text().strip())
        watched_path = Path(self.companion_panel.watched_path_edit.text().strip() or str(self.current_game_root))
        if not executable.exists():
            QMessageBox.warning(self, "Companion", f"Executable not found: {executable}")
            return
        if not watched_path.exists():
            QMessageBox.warning(self, "Companion", f"Watched path not found: {watched_path}")
            return
        session = self.services.launch_companion(
            project_id=self.current_project_id,
            executable_path=executable,
            watched_path=watched_path,
            args=self.companion_panel.args_list(),
        )
        self.current_companion_session_id = str(session.get("session_id"))
        self.companion_panel.session_status.setText(
            f"Session status: {session.get('process_status')} ({self.current_companion_session_id})"
        )
        self.refresh_companion()
        self.refresh_hud()

    def on_poll_companion(self) -> None:
        if not self._require_project() or not self.current_companion_session_id:
            return
        status = self.services.poll_companion(
            project_id=self.current_project_id,
            session_id=self.current_companion_session_id,
            game_root=self.current_game_root,
        )
        session = status.get("session") or {}
        self.companion_panel.session_status.setText(
            f"Session status: {status.get('status')} pid={session.get('process_pid')}"
        )
        self.companion_panel.reindex_status.setText(f"Quick re-index: {status.get('quick_reindexed_entries', 0)}")
        self.companion_panel.load_events(status.get("all_events", []))
        self.refresh_assets()
        self.refresh_reports()
        self.refresh_diagnostics()
        self.refresh_companion()
        self.refresh_hud()

    def on_stop_companion(self) -> None:
        if not self._require_project() or not self.current_companion_session_id:
            return
        session = self.services.stop_companion(
            project_id=self.current_project_id,
            session_id=self.current_companion_session_id,
        )
        self.companion_panel.session_status.setText(
            f"Session status: {session.get('process_status')} ({self.current_companion_session_id})"
        )
        self.refresh_companion()
        self.refresh_hud()

    def on_start_live_demo(self) -> None:
        if not self._require_project():
            return
        scene_id = self.live_panel.scene_combo.currentData()
        if not scene_id:
            QMessageBox.warning(self, "Scene", "No scene selected.")
            return
        stream = list(
            self.services.live_demo_stream(
                project_id=self.current_project_id,
                game_root=self.current_game_root,
                scene_id=str(scene_id),
                backend_name=self.translation_panel.backend_combo.currentText(),
            )
        )
        self._live_rows = stream
        self._live_idx = 0
        self.live_panel.log_view.clear()
        self.live_panel.table.setRowCount(0)
        self._live_timer.start(250)
        self.refresh_hud()

    def on_refresh_assets(self) -> None:
        if not self._require_project():
            return
        self.refresh_assets()

    def on_asset_selected(self) -> None:
        if self.current_project_id is None:
            return
        file_path = self.asset_panel.selected_file_path()
        if not file_path:
            return
        self.asset_panel.show_details(self.services.asset_details(self.current_project_id, file_path))

    def _consume_live_row(self) -> None:
        if self._live_idx >= len(self._live_rows):
            self._live_timer.stop()
            self.refresh_entries()
            self.refresh_translations()
            self.refresh_voice()
            self.refresh_language_hub()
            self.refresh_hud()
            return
        self.live_panel.append_live_row(self._live_rows[self._live_idx])
        self._live_idx += 1

    def refresh_all_views(self) -> None:
        self.refresh_assets()
        self.refresh_entries()
        self.refresh_language_hub()
        self.refresh_translations()
        self.refresh_voice()
        self.refresh_learning()
        self.refresh_glossary()
        self.refresh_qa()
        self.refresh_reports()
        self.refresh_diagnostics()
        self.refresh_language_intelligence()
        self.refresh_audio_lab()
        self.refresh_evidence_review()
        self.refresh_sync_review()
        self.refresh_jobs()
        self.refresh_companion()
        self.refresh_hud()

    def refresh_entries(self) -> None:
        if self.current_project_id is None:
            self.entries_panel.load_entries([])
            return
        lang = self.entries_panel.lang_filter.currentText()
        lang_filter = None if lang == "all" else lang
        search = self.entries_panel.search_edit.text().strip() or None
        rows = self.services.repo.list_entries(self.current_project_id, language=lang_filter, search=search, limit=100000)
        self.entries_panel.load_entries(rows)

    def refresh_assets(self) -> None:
        if self.current_project_id is None:
            self.asset_panel.load_snapshot({})
            return
        self.asset_panel.load_snapshot(self.services.asset_snapshot(self.current_project_id))

    def refresh_translations(self) -> None:
        if self.current_project_id is None:
            self.translation_panel.load_translations([])
            return
        self.translation_panel.load_translations(self.services.repo.list_translations(self.current_project_id))

    def refresh_voice(self) -> None:
        if self.current_project_id is None:
            self.voice_panel.load_voice_data({})
            return
        snapshot = self.services.voice_snapshot(self.current_project_id, game_root=self.current_game_root)
        self.voice_panel.load_voice_data(snapshot)

    def refresh_learning(self) -> None:
        if self.current_project_id is None:
            self.learning_panel.load_snapshot({})
            return
        self.learning_panel.load_snapshot(self.services.learning_snapshot(self.current_project_id))

    def refresh_glossary(self) -> None:
        if self.current_project_id is None:
            self.glossary_panel.load_terms([])
            return
        self.glossary_panel.load_terms(self.services.glossary_service.list_terms(self.current_project_id))

    def refresh_qa(self) -> None:
        if self.current_project_id is None:
            self.qa_panel.load_findings([])
            return
        self.qa_panel.load_findings(self.services.repo.list_qa_findings(self.current_project_id))

    def refresh_reports(self) -> None:
        if self.current_project_id is None:
            self.reports_panel.load_reports({})
            return
        snapshot = self.services.reports_snapshot(self.current_project_id)
        if not snapshot.get("project_summary"):
            self.services.generate_reports(self.current_project_id)
            snapshot = self.services.reports_snapshot(self.current_project_id)
        self.reports_panel.load_reports(snapshot)

    def refresh_language_hub(self) -> None:
        if self.current_project_id is None:
            self.language_hub_panel.load_snapshot({})
            return
        snapshot = self.services.language_hub_snapshot(
            self.current_project_id,
            requested_backend=self.translation_panel.backend_combo.currentText(),
        )
        self.language_hub_panel.load_snapshot(snapshot)

    def refresh_diagnostics(self) -> None:
        if self.current_project_id is None:
            self.diagnostics_panel.load_diagnostics({})
            return
        snapshot = self.services.diagnostics_snapshot(self.current_project_id)
        if not snapshot.get("backend_diagnostics"):
            self.services.generate_reports(self.current_project_id)
            snapshot = self.services.diagnostics_snapshot(self.current_project_id)
        self.diagnostics_panel.load_diagnostics(snapshot)

    def refresh_language_intelligence(self) -> None:
        if self.current_project_id is None:
            self.language_intelligence_panel.load_snapshot({})
            return
        self.language_intelligence_panel.load_snapshot(self.services.language_intelligence_snapshot(self.current_project_id))

    def refresh_audio_lab(self) -> None:
        if self.current_project_id is None:
            self.audio_analysis_lab_panel.load_snapshot({})
            return
        self.audio_analysis_lab_panel.load_snapshot(self.services.audio_analysis_lab_snapshot(self.current_project_id))

    def refresh_evidence_review(self) -> None:
        if self.current_project_id is None:
            self.evidence_review_panel.load_snapshot({})
            return
        self.evidence_review_panel.load_snapshot(self.services.evidence_review_snapshot(self.current_project_id))

    def refresh_sync_review(self) -> None:
        if self.current_project_id is None:
            self.sync_review_panel.load_snapshot({})
            return
        self.sync_review_panel.load_snapshot(self.services.sync_review_snapshot(self.current_project_id))

    def refresh_jobs(self) -> None:
        if self.current_project_id is None:
            self.jobs_panel.show_jobs({})
            return
        jobs = {
            "scan": self.services.job_manager.get_job_state("scan"),
            "extract": self.services.job_manager.get_job_state("extract"),
            "detect": self.services.job_manager.get_job_state("detect"),
            "translate": self.services.job_manager.get_job_state("translate"),
            "voice": self.services.job_manager.get_job_state("voice"),
            "export": self.services.job_manager.get_job_state("export"),
            "export_jobs": self.services.repo.list_export_jobs(self.current_project_id),
            "backend_runs": self.services.repo.list_translation_backend_runs(self.current_project_id, limit=20),
        }
        self.jobs_panel.show_jobs(jobs)

    def refresh_companion(self) -> None:
        if self.current_project_id is None:
            self.companion_panel.load_sessions([])
            self.companion_panel.load_events([])
            return
        sessions = self.services.list_companion_sessions(self.current_project_id)
        self.companion_panel.load_sessions(sessions)
        if self.current_companion_session_id:
            events = self.services.repo.list_watched_file_events(
                self.current_project_id, session_id=self.current_companion_session_id, limit=300
            )
        else:
            events = self.services.repo.list_watched_file_events(self.current_project_id, limit=300)
        self.companion_panel.load_events(events)

    def refresh_hud(self) -> None:
        if self.current_project_id is None:
            self.hud_panel.load_snapshot({})
            return
        self.hud_panel.load_snapshot(
            self.services.hud_snapshot(
                self.current_project_id,
                game_root=self.current_game_root,
                current_companion_session_id=self.current_companion_session_id,
                requested_backend=self.translation_panel.backend_combo.currentText(),
            )
        )

    def _switch_tab(self, tab_name: str) -> bool:
        for idx in range(self.tabs.count()):
            if self.tabs.tabText(idx) == tab_name:
                self.tabs.setCurrentIndex(idx)
                return True
        return False
