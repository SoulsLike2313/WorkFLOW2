from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)
from PySide6.QtCore import Qt

from .table_utils import fill_table


class LearningPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.refresh_btn = QPushButton("Refresh Learning Snapshot")
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.corrections_table = QTableWidget(0, 6)
        self.corrections_table.setHorizontalHeaderLabels(["ID", "Entry", "Line", "Before", "After", "When"])
        self.improvements_table = QTableWidget(0, 7)
        self.improvements_table.setHorizontalHeaderLabels(
            ["Entry", "Line", "Backend", "TM", "Glossary", "Status", "Quality"]
        )
        self.events_table = QTableWidget(0, 5)
        self.events_table.setHorizontalHeaderLabels(["ID", "Type", "Scope", "Ref", "Created"])
        splitter.addWidget(self.corrections_table)
        splitter.addWidget(self.improvements_table)
        splitter.addWidget(self.events_table)
        splitter.setSizes([500, 600, 400])

        root.addWidget(self.refresh_btn)
        root.addWidget(self.summary)
        root.addWidget(splitter)

    def load_snapshot(self, snapshot: dict) -> None:
        corrections = snapshot.get("corrections", [])
        corr_rows = [
            (
                c.get("id"),
                c.get("entry_id"),
                c.get("line_id"),
                str(c.get("before_text", ""))[:42],
                str(c.get("after_text", ""))[:42],
                c.get("created_at"),
            )
            for c in corrections
        ]
        fill_table(self.corrections_table, corr_rows)

        events = snapshot.get("adaptation_summary", {}).get("recent", [])
        event_rows = [
            (e.get("id"), e.get("event_type"), e.get("event_scope"), e.get("event_ref"), e.get("created_at"))
            for e in events
        ]
        fill_table(self.events_table, event_rows)

        improvements = snapshot.get("improvement_examples", [])
        improvement_rows = [
            (
                row.get("entry_id"),
                row.get("line_id"),
                row.get("backend"),
                len(row.get("tm_hits_json", [])),
                len(row.get("glossary_hits_json", [])),
                row.get("translation_status"),
                row.get("quality_score"),
            )
            for row in improvements
        ]
        fill_table(self.improvements_table, improvement_rows)

        summary_payload = {
            "adaptation_summary": snapshot.get("adaptation_summary", {}),
            "terms_learned": len(snapshot.get("terms", [])),
            "tm_entries": len(snapshot.get("tm", [])),
            "evidence_records": len(snapshot.get("evidence", [])),
            "knowledge_sources": len(snapshot.get("knowledge_sources", [])),
            "external_reference_events": len(snapshot.get("external_references", [])),
            "recent_corrections": len(corrections),
            "improved_examples_visible": len(improvements),
        }
        self.summary.setPlainText(json.dumps(summary_payload, ensure_ascii=False, indent=2))
