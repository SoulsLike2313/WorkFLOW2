from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class EntriesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.detect_btn = QPushButton("Detect Language")
        self.refresh_btn = QPushButton("Refresh")
        self.lang_filter = QComboBox()
        self.lang_filter.addItems(["all", "en", "fr", "de", "es", "it", "pt", "pl", "ja", "tr", "ko", "zh", "unknown"])
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search text/line/file...")
        toolbar.addWidget(self.detect_btn)
        toolbar.addWidget(QLabel("Lang:"))
        toolbar.addWidget(self.lang_filter)
        toolbar.addWidget(self.search_edit)
        toolbar.addWidget(self.refresh_btn)

        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Line ID",
                "File",
                "Speaker",
                "Source",
                "Lang",
                "RU",
                "Status",
                "Gloss/TM",
                "Quality",
                "Voice Link",
                "Voice Status",
            ]
        )

        self.info_label = QLabel("Entries loaded: 0")
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        layout.addWidget(self.info_label)

    def load_entries(self, entries: list[dict]) -> None:
        rows = []
        for e in entries:
            hits = f"G:{len(e.get('glossary_hits_json', []))}/TM:{len(e.get('tm_hits_json', []))}"
            rows.append(
                (
                    e.get("id", ""),
                    e.get("line_id", ""),
                    e.get("file_path", ""),
                    e.get("speaker_id", ""),
                    (e.get("source_text", "")[:70] + "...") if len(e.get("source_text", "")) > 70 else e.get("source_text", ""),
                    e.get("detected_lang", ""),
                    (e.get("translated_text", "")[:70] + "...") if len(e.get("translated_text", "")) > 70 else e.get("translated_text", ""),
                    e.get("translation_status", ""),
                    hits,
                    e.get("quality_score", ""),
                    "yes" if e.get("has_voice_link") else "no",
                    e.get("voice_status", ""),
                )
            )
        fill_table(self.table, rows)
        self.info_label.setText(f"Entries loaded: {len(entries)}")
