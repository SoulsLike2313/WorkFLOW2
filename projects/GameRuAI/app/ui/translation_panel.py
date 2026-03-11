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

        controls = QHBoxLayout()
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["local_mock", "dummy"])
        self.style_combo = QComboBox()
        self.style_combo.addItems(["neutral", "dramatic", "calm", "radio"])
        self.translate_btn = QPushButton("Translate to Russian")
        controls.addWidget(QLabel("Backend:"))
        controls.addWidget(self.backend_combo)
        controls.addWidget(QLabel("Style:"))
        controls.addWidget(self.style_combo)
        controls.addWidget(self.translate_btn)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["Entry ID", "Line ID", "Source Lang", "Source", "Translated", "Quality", "Latency", "Uncertainty"]
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
                row.get("quality_score", 0),
                row.get("latency_ms", 0),
                row.get("uncertainty", 0),
            )
            for row in rows
        ]
        fill_table(self.table, data)
        self.info_label.setText(f"Translations: {len(rows)}")
