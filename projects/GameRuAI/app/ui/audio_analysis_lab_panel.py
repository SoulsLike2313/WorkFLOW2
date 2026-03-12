from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget

from .table_utils import fill_table


class AudioAnalysisLabPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.refresh_btn = QPushButton("Refresh Audio Lab")
        self.status_label = QLabel("Audio Lab: n/a")

        self.audio_table = QTableWidget(0, 7)
        self.audio_table.setHorizontalHeaderLabels(
            ["Entry", "Source", "Generated", "Source ms", "Generated ms", "Delta", "Quality"]
        )
        self.segment_table = QTableWidget(0, 5)
        self.segment_table.setHorizontalHeaderLabels(["Line", "Segment", "Start", "End", "Confidence"])
        self.sync_table = QTableWidget(0, 5)
        self.sync_table.setHorizontalHeaderLabels(["Line", "Delta", "Adjustment", "Confidence", "Status"])

        root.addWidget(self.refresh_btn)
        root.addWidget(self.status_label)
        root.addWidget(QLabel("Source vs generated audio comparison:"))
        root.addWidget(self.audio_table)
        root.addWidget(QLabel("Transcript-linked segments:"))
        root.addWidget(self.segment_table)
        root.addWidget(QLabel("Sync plan summary:"))
        root.addWidget(self.sync_table)

    def load_snapshot(self, snapshot: dict) -> None:
        audio_rows = [
            (
                row.get("entry_id"),
                row.get("source_file"),
                row.get("generated_file"),
                row.get("source_duration_ms"),
                row.get("generated_duration_ms"),
                row.get("delta_ms"),
                row.get("quality_score"),
            )
            for row in snapshot.get("audio_results", [])
        ]
        fill_table(self.audio_table, audio_rows)

        segment_rows = [
            (
                row.get("line_id"),
                row.get("segment_id"),
                row.get("start_ms"),
                row.get("end_ms"),
                row.get("confidence"),
            )
            for row in snapshot.get("transcript_segments", [])
        ]
        fill_table(self.segment_table, segment_rows)

        sync_rows = [
            (
                row.get("line_id"),
                row.get("delta_ms"),
                row.get("recommended_adjustment"),
                row.get("confidence"),
                row.get("status"),
            )
            for row in snapshot.get("sync_plans", [])
        ]
        fill_table(self.sync_table, sync_rows)

        self.status_label.setText(
            f"Audio Lab: results={len(audio_rows)} segments={len(segment_rows)} avg_quality={snapshot.get('avg_quality', 0)} mode={snapshot.get('synthesis_mode', 'n/a')}"
        )

