from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ProductHudPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(8)

        context_box = QGroupBox("Project HUD")
        context_layout = QGridLayout(context_box)
        self.project_label = QLabel("Project: n/a")
        self.game_path_label = QLabel("Game path: n/a")
        self.backend_label = QLabel("Active backend: n/a")
        self.companion_label = QLabel("Companion: idle")
        self.next_action_label = QLabel("Next action: create/select project")
        self.language_map_label = QLabel("Language map: n/a")
        self.project_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.game_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.language_map_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        context_layout.addWidget(self.project_label, 0, 0, 1, 2)
        context_layout.addWidget(self.game_path_label, 1, 0, 1, 2)
        context_layout.addWidget(self.backend_label, 0, 2)
        context_layout.addWidget(self.companion_label, 1, 2)
        context_layout.addWidget(self.next_action_label, 0, 3)
        context_layout.addWidget(self.language_map_label, 1, 3)
        root.addWidget(context_box)

        actions_box = QGroupBox("Primary Actions")
        actions_layout = QHBoxLayout(actions_box)
        self.quick_scan_btn = QPushButton("1) Scan")
        self.quick_detect_btn = QPushButton("2) Detect")
        self.quick_translate_btn = QPushButton("3) Translate")
        self.quick_voice_btn = QPushButton("4) Voice")
        self.quick_export_btn = QPushButton("5) Export")
        self.quick_reports_btn = QPushButton("6) Reports")
        self.quick_actions = [
            self.quick_scan_btn,
            self.quick_detect_btn,
            self.quick_translate_btn,
            self.quick_voice_btn,
            self.quick_export_btn,
            self.quick_reports_btn,
        ]
        for button in self.quick_actions:
            actions_layout.addWidget(button)
        actions_layout.addStretch(1)
        root.addWidget(actions_box)

        status_box = QGroupBox("Pipeline + Quality Status")
        status_layout = QGridLayout(status_box)
        self.stage_labels: dict[str, QLabel] = {}
        stage_titles = [
            ("scan", "Scan"),
            ("extract", "Extract"),
            ("detect", "Detect"),
            ("translate", "Translate"),
            ("voice", "Voice"),
            ("export", "Export"),
            ("reports", "Reports"),
            ("diagnostics", "Diagnostics"),
        ]
        for idx, (key, title) in enumerate(stage_titles):
            label = QLabel(f"{title}: pending")
            label.setFrameShape(QFrame.StyledPanel)
            label.setAlignment(Qt.AlignCenter)
            self.stage_labels[key] = label
            status_layout.addWidget(label, idx // 4, idx % 4)

        self.translation_progress = QProgressBar()
        self.translation_progress.setRange(0, 100)
        self.translation_progress.setValue(0)
        self.translation_progress.setFormat("Translation coverage: %p%")
        self.uncertainty_progress = QProgressBar()
        self.uncertainty_progress.setRange(0, 100)
        self.uncertainty_progress.setValue(0)
        self.uncertainty_progress.setFormat("Uncertain lines: %p%")
        status_layout.addWidget(self.translation_progress, 2, 0, 1, 2)
        status_layout.addWidget(self.uncertainty_progress, 2, 2, 1, 2)
        root.addWidget(status_box)

        metrics_box = QGroupBox("Operational Metrics")
        metrics_layout = QGridLayout(metrics_box)
        self.entries_label = QLabel("Entries: 0")
        self.languages_label = QLabel("Languages: 0")
        self.translated_label = QLabel("Translated: 0")
        self.uncertain_label = QLabel("Uncertain: 0")
        self.voice_label = QLabel("Voice prep: n/a")
        self.qa_label = QLabel("QA: n/a")
        self.reports_label = QLabel("Reports: n/a")
        self.bottlenecks_label = QLabel("Language bottlenecks: n/a")
        self.core_label = QLabel("Core: n/a")
        self.metrics_labels = [
            self.entries_label,
            self.languages_label,
            self.translated_label,
            self.uncertain_label,
            self.voice_label,
            self.qa_label,
            self.reports_label,
            self.bottlenecks_label,
            self.core_label,
        ]
        for idx, label in enumerate(self.metrics_labels):
            label.setFrameShape(QFrame.StyledPanel)
            metrics_layout.addWidget(label, idx // 4, idx % 4)
        root.addWidget(metrics_box)

    def load_snapshot(self, snapshot: dict) -> None:
        if not snapshot:
            self.project_label.setText("Project: n/a")
            self.game_path_label.setText("Game path: n/a")
            self.backend_label.setText("Active backend: n/a")
            self.companion_label.setText("Companion: idle")
            self.next_action_label.setText("Next action: create/select project")
            self.language_map_label.setText("Language map: n/a")
            for label in self.stage_labels.values():
                label.setText(label.text().split(":", 1)[0] + ": pending")
                label.setStyleSheet("")
            self.translation_progress.setValue(0)
            self.uncertainty_progress.setValue(0)
            for label in self.metrics_labels:
                prefix = label.text().split(":", 1)[0]
                label.setText(f"{prefix}: n/a")
            for button in self.quick_actions:
                button.setEnabled(False)
            self.entries_label.setText("Entries: 0")
            self.languages_label.setText("Languages: 0")
            self.translated_label.setText("Translated: 0")
            self.uncertain_label.setText("Uncertain: 0")
            return

        self.project_label.setText(
            f"Project: {snapshot.get('project_name', 'n/a')} (id={snapshot.get('project_id', 'n/a')})"
        )
        self.game_path_label.setText(f"Game path: {snapshot.get('game_path', 'n/a')}")
        self.backend_label.setText(
            "Active backend: "
            f"{snapshot.get('active_backend', 'n/a')} | fallback={snapshot.get('fallback_backend', '-')}"
        )
        self.companion_label.setText(
            "Companion: "
            f"{snapshot.get('companion_status', 'idle')} ({snapshot.get('companion_session_id', 'no-session')})"
        )
        self.next_action_label.setText(f"Next action: {snapshot.get('next_action', 'n/a')}")
        self.language_map_label.setText(f"Language map: {snapshot.get('language_map', 'n/a')}")

        stage_snapshot = snapshot.get("pipeline_stage", {}) or {}
        for key, label in self.stage_labels.items():
            state = str(stage_snapshot.get(key, "pending"))
            if state == "done":
                label.setText(label.text().split(":", 1)[0] + ": done")
                label.setStyleSheet("QLabel { background-color: #2f6f44; color: #f2fff5; padding: 4px; }")
            elif state == "partial":
                label.setText(label.text().split(":", 1)[0] + ": partial")
                label.setStyleSheet("QLabel { background-color: #7a632d; color: #fff8e5; padding: 4px; }")
            else:
                label.setText(label.text().split(":", 1)[0] + ": pending")
                label.setStyleSheet("QLabel { background-color: #5b3030; color: #ffecec; padding: 4px; }")

        coverage = int(float(snapshot.get("translation_coverage_rate", 0.0)) * 100)
        uncertainty = int(float(snapshot.get("uncertain_rate", 0.0)) * 100)
        self.translation_progress.setValue(max(0, min(100, coverage)))
        self.uncertainty_progress.setValue(max(0, min(100, uncertainty)))

        self.entries_label.setText(f"Entries: {snapshot.get('entries_total', 0)}")
        self.languages_label.setText(f"Languages: {snapshot.get('languages_total', 0)}")
        self.translated_label.setText(f"Translated: {snapshot.get('translated_total', 0)}")
        self.uncertain_label.setText(f"Uncertain: {snapshot.get('uncertain_total', 0)}")
        self.voice_label.setText(
            "Voice prep: "
            f"attempts={snapshot.get('voice_attempts_total', 0)} "
            f"broken_links={snapshot.get('voice_broken_links', 0)}"
        )
        self.qa_label.setText(
            f"QA: errors={snapshot.get('qa_errors', 0)} warnings={snapshot.get('qa_warnings', 0)}"
        )
        self.reports_label.setText(
            "Reports: "
            f"{snapshot.get('reports_status', 'n/a')} | diagnostics={snapshot.get('diagnostics_status', 'n/a')}"
        )
        self.bottlenecks_label.setText(
            "Language bottlenecks: "
            + ", ".join(snapshot.get("language_bottlenecks", []) or ["none"])
        )
        self.core_label.setText(
            "Core: "
            f"packages={snapshot.get('translation_packages_total', 0)} "
            f"evidence={snapshot.get('evidence_records_total', 0)} "
            f"sync={snapshot.get('sync_plans_total', 0)} "
            f"sources={snapshot.get('knowledge_sources_total', 0)}"
        )

        stage_snapshot = snapshot.get("pipeline_stage", {}) or {}
        self.quick_scan_btn.setEnabled(stage_snapshot.get("scan") != "done")
        self.quick_detect_btn.setEnabled(stage_snapshot.get("extract") in {"done", "partial"})
        self.quick_translate_btn.setEnabled(stage_snapshot.get("detect") in {"done", "partial"})
        self.quick_voice_btn.setEnabled(stage_snapshot.get("translate") in {"done", "partial"})
        self.quick_export_btn.setEnabled(stage_snapshot.get("translate") in {"done", "partial"})
        self.quick_reports_btn.setEnabled(True)
