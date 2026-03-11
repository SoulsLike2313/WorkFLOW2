from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class TranslationPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        self.backend_status_label = QLabel("Active backend: n/a")
        self.fallback_status_label = QLabel("Fallback: n/a")
        self.context_status_label = QLabel("Context used: n/a")
        root.addWidget(self.backend_status_label)
        root.addWidget(self.fallback_status_label)
        root.addWidget(self.context_status_label)

        controls = QHBoxLayout()
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["local_mock", "dummy", "argos", "transformers"])
        self.style_combo = QComboBox()
        self.style_combo.addItems(["neutral", "dramatic", "calm", "radio"])
        self.translate_btn = QPushButton("Translate to Russian")
        controls.addWidget(QLabel("Backend:"))
        controls.addWidget(self.backend_combo)
        controls.addWidget(QLabel("Style:"))
        controls.addWidget(self.style_combo)
        controls.addWidget(self.translate_btn)

        self.table = QTableWidget(0, 13)
        self.table.setHorizontalHeaderLabels(
            [
                "Entry ID",
                "Line ID",
                "Source Lang",
                "Source",
                "Translated",
                "Backend",
                "Fallback",
                "Context",
                "Reason",
                "Quality",
                "Latency",
                "Uncertainty",
                "Warning",
            ]
        )

        correction_form = QFormLayout()
        self.correction_entry_id = QLineEdit()
        self.correction_text = QTextEdit()
        self.correction_note = QLineEdit()
        self.add_glossary_check = QCheckBox("Add correction pair to glossary")
        self.glossary_source = QLineEdit()
        self.glossary_target = QLineEdit()
        self.glossary_lang = QLineEdit("any")
        self.apply_correction_btn = QPushButton("Apply Correction")

        correction_form.addRow("Entry ID:", self.correction_entry_id)
        correction_form.addRow("Corrected RU:", self.correction_text)
        correction_form.addRow("Note:", self.correction_note)
        correction_form.addRow(self.add_glossary_check)
        correction_form.addRow("Glossary Source:", self.glossary_source)
        correction_form.addRow("Glossary Target:", self.glossary_target)
        correction_form.addRow("Glossary Lang:", self.glossary_lang)
        correction_form.addRow(self.apply_correction_btn)

        self.info_label = QLabel("No translations yet.")

        root.addLayout(controls)
        root.addWidget(self.table)
        root.addLayout(correction_form)
        root.addWidget(self.info_label)

    def load_translations(self, rows: list[dict]) -> None:
        data = [
            (
                row.get("entry_id"),
                row.get("line_id"),
                row.get("source_lang"),
                (row.get("source_text", "")[:65] + "...") if len(row.get("source_text", "")) > 65 else row.get("source_text", ""),
                (row.get("translated_text", "")[:65] + "...") if len(row.get("translated_text", "")) > 65 else row.get("translated_text", ""),
                row.get("backend", ""),
                row.get("fallback_backend", ""),
                "yes" if row.get("context_used") else "no",
                (row.get("decision_log_json", [""])[0] if row.get("decision_log_json") else ""),
                row.get("quality_score", 0),
                row.get("latency_ms", 0),
                row.get("uncertainty", 0),
                "HIGH" if float(row.get("uncertainty", 0) or 0) >= 0.28 else "",
            )
            for row in rows
        ]
        fill_table(self.table, data)
        self.info_label.setText(f"Translations: {len(rows)}")

    def set_backend_status(self, summary: dict) -> None:
        usage = summary.get("backend_usage", {})
        if usage:
            ordered = sorted(usage.items(), key=lambda item: item[1], reverse=True)
            active = ordered[0][0]
        else:
            active = summary.get("requested_backend", "n/a")
        self.backend_status_label.setText(f"Active backend: {active} (requested: {summary.get('requested_backend', 'n/a')})")
        self.fallback_status_label.setText(f"Fallback used: {summary.get('fallback_used_count', 0)}")
        self.context_status_label.setText(f"Context used: {summary.get('context_used_count', 0)} lines")
