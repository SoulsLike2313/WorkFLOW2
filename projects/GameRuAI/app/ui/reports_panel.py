from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class ReportsPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Reports")
        self.refresh_btn = QPushButton("Refresh Reports")
        controls.addWidget(self.generate_btn)
        controls.addWidget(self.refresh_btn)
        root.addLayout(controls)

        self.coverage_label = QLabel("Coverage: n/a")
        self.low_quality_label = QLabel("Low quality: n/a")
        self.uncertain_label = QLabel("Uncertain language: n/a")
        self.voice_label = QLabel("Voice quality/alignment: n/a")
        self.companion_label = QLabel("Companion events: n/a")
        self.core_label = QLabel("Multimodal core: n/a")
        root.addWidget(self.coverage_label)
        root.addWidget(self.low_quality_label)
        root.addWidget(self.uncertain_label)
        root.addWidget(self.voice_label)
        root.addWidget(self.companion_label)
        root.addWidget(self.core_label)

        self.translation_table = QTableWidget(0, 2)
        self.translation_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.language_table = QTableWidget(0, 2)
        self.language_table.setHorizontalHeaderLabels(["Language", "Lines"])
        self.qa_table = QTableWidget(0, 2)
        self.qa_table.setHorizontalHeaderLabels(["QA Metric", "Value"])
        self.summary_view = QPlainTextEdit()
        self.summary_view.setReadOnly(True)

        root.addWidget(QLabel("Translation report:"))
        root.addWidget(self.translation_table)
        root.addWidget(QLabel("Language distribution:"))
        root.addWidget(self.language_table)
        root.addWidget(QLabel("QA dashboard:"))
        root.addWidget(self.qa_table)
        root.addWidget(QLabel("Project summary (compact JSON):"))
        root.addWidget(self.summary_view)

    def load_reports(self, snapshot: dict) -> None:
        translation = snapshot.get("translation_report", {}) or {}
        project_summary = snapshot.get("project_summary", {}) or {}
        quality = snapshot.get("quality_dashboard", {}) or {}
        core_summary = snapshot.get("multimodal_core_summary", {}) or {}

        metrics_rows = [
            ("entries_total", translation.get("entries_total", 0)),
            ("translated_count", translation.get("translated_count", 0)),
            ("untranslated_count", translation.get("untranslated_count", 0)),
            ("glossary_hit_rate", translation.get("glossary_hit_rate", 0)),
            ("tm_hit_rate", translation.get("tm_hit_rate", 0)),
            ("avg_latency_ms", (translation.get("latency_stats", {}) or {}).get("avg_ms", 0)),
            ("low_quality_count", translation.get("low_quality_count", 0)),
            ("uncertain_language_rate", translation.get("uncertain_language_rate", 0)),
        ]
        fill_table(self.translation_table, metrics_rows)

        language_distribution = (translation.get("language_distribution") or {}) or (
            (project_summary.get("language") or {}).get("distribution") or {}
        )
        lang_rows = [(lang, count) for lang, count in sorted(language_distribution.items())]
        fill_table(self.language_table, lang_rows)

        qa_data = (project_summary.get("qa_dashboard") or {}) if project_summary else {}
        qa_rows = [
            ("total_findings", qa_data.get("total_findings", 0)),
            ("errors", qa_data.get("errors", 0)),
            ("warnings", qa_data.get("warnings", 0)),
            ("broken_placeholders", qa_data.get("broken_placeholders", 0)),
            ("broken_tags", qa_data.get("broken_tags", 0)),
            ("untranslated_lines", qa_data.get("untranslated_lines", 0)),
            ("export_integrity", (qa_data.get("export_integrity") or {}).get("status", "n/a")),
        ]
        fill_table(self.qa_table, qa_rows)

        self.coverage_label.setText(f"Coverage: {translation.get('translation_coverage_rate', 0)}")
        self.low_quality_label.setText(
            f"Low quality: {quality.get('low_quality_translations', translation.get('low_quality_count', 0))}"
        )
        self.uncertain_label.setText(
            f"Uncertain language: {quality.get('uncertain_language_rate', translation.get('uncertain_language_rate', 0))}"
        )
        self.voice_label.setText(
            f"Voice quality/alignment: quality={quality.get('voice_avg_quality', 0)} alignment={quality.get('voice_avg_alignment', 0)}"
        )
        companion = project_summary.get("companion", {}) if project_summary else {}
        self.companion_label.setText(
            f"Companion events: sessions={companion.get('sessions_total', 0)} events={companion.get('watched_events_total', 0)}"
        )
        self.core_label.setText(
            "Multimodal core: "
            f"assets={core_summary.get('asset_manifest_total', 0)} "
            f"content_units={core_summary.get('content_units_total', 0)} "
            f"packages={core_summary.get('translation_packages_total', 0)} "
            f"sync={core_summary.get('sync_plans_total', 0)} "
            f"evidence={core_summary.get('evidence_records_total', 0)}"
        )

        compact = {
            "translation_backend_usage": translation.get("backend_usage", {}),
            "quality_dashboard": quality,
            "voice_modes": ((project_summary.get("voice") or {}).get("synthesis_mode_usage") or {}),
            "problematic_files_top": (qa_data.get("problematic_files") or [])[:10],
        }
        self.summary_view.setPlainText(json.dumps(compact, ensure_ascii=False, indent=2))
