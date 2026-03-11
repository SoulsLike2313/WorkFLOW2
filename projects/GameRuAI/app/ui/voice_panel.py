from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class VoicePanel(QWidget):
    def __init__(self):
        super().__init__()
        self._attempt_rows: list[dict] = []

        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Demo Voice Attempts")
        controls.addWidget(self.generate_btn)
        root.addLayout(controls)

        self.mode_label = QLabel("Synthesis mode: MOCK/DEMO preparation layer (no final dubbing).")
        self.quality_confidence_label = QLabel("Voice quality/confidence: n/a")
        self.info_label = QLabel("Voice attempts: 0")
        root.addWidget(self.mode_label)
        root.addWidget(self.quality_confidence_label)
        root.addWidget(self.info_label)

        profile_form = QFormLayout()
        self.speaker_id_edit = QLineEdit()
        self.style_combo = QComboBox()
        self.style_combo.addItems(["neutral", "dramatic", "calm", "radio"])
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0.5, 2.0)
        self.rate_spin.setSingleStep(0.1)
        self.rate_spin.setValue(1.0)
        self.update_profile_btn = QPushButton("Update Speaker Profile")
        profile_form.addRow("Speaker ID:", self.speaker_id_edit)
        profile_form.addRow("Style Preset:", self.style_combo)
        profile_form.addRow("Speech Rate:", self.rate_spin)
        profile_form.addRow(self.update_profile_btn)
        root.addLayout(profile_form)

        splitter = QSplitter()
        left = QWidget()
        left_layout = QVBoxLayout(left)
        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.speaker_groups_table = QTableWidget(0, 7)
        self.speaker_groups_table.setHorizontalHeaderLabels(
            ["Speaker", "Lines", "Linked", "Broken", "Scenes", "Avg conf", "Group"]
        )

        self.attempts_table = QTableWidget(0, 11)
        self.attempts_table.setHorizontalHeaderLabels(
            [
                "Line ID",
                "Speaker",
                "Source Voice",
                "Output Voice",
                "Status",
                "Synthesis",
                "Align",
                "Duration plan",
                "Quality",
                "Confidence",
                "Meta",
            ]
        )

        self.history_table = QTableWidget(0, 8)
        self.history_table.setHorizontalHeaderLabels(
            ["When", "Speaker", "Source", "Generated", "Mode", "Align", "Quality", "Confidence"]
        )

        self.preview_panel = QPlainTextEdit()
        self.preview_panel.setReadOnly(True)
        self.duration_plan_panel = QPlainTextEdit()
        self.duration_plan_panel.setReadOnly(True)

        left_layout.addWidget(QLabel("Speaker groups:"))
        left_layout.addWidget(self.speaker_groups_table)
        left_layout.addWidget(QLabel("Voice attempts:"))
        left_layout.addWidget(self.attempts_table)
        left_layout.addWidget(QLabel("Voice attempt history:"))
        left_layout.addWidget(self.history_table)

        right_layout.addWidget(QLabel("Voice Preview panel:"))
        right_layout.addWidget(self.preview_panel)
        right_layout.addWidget(QLabel("Duration Plan widget:"))
        right_layout.addWidget(self.duration_plan_panel)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([1000, 580])
        root.addWidget(splitter)

    def selected_attempt(self) -> dict | None:
        row = self.attempts_table.currentRow()
        if row < 0 or row >= len(self._attempt_rows):
            return None
        return self._attempt_rows[row]

    def load_voice_data(self, snapshot: dict) -> None:
        attempts = snapshot.get("attempts", [])
        groups = snapshot.get("speaker_groups", [])
        history = snapshot.get("history", [])
        summary = snapshot.get("summary", {})

        self._attempt_rows = list(attempts)

        groups_rows = [
            (
                row.get("speaker_id"),
                row.get("line_count"),
                row.get("linked_count"),
                row.get("broken_links"),
                row.get("scene_count"),
                row.get("avg_confidence"),
                row.get("group_label"),
            )
            for row in groups
        ]
        fill_table(self.speaker_groups_table, groups_rows)

        attempts_rows = []
        for row in attempts:
            meta = row.get("metadata_json", {})
            plan = meta.get("duration_plan", {})
            attempts_rows.append(
                (
                    row.get("line_id"),
                    row.get("speaker_id"),
                    row.get("source_voice_path"),
                    row.get("output_voice_path"),
                    row.get("status"),
                    row.get("synthesis_mode", ""),
                    row.get("alignment_ratio", ""),
                    plan.get("recommended_action", ""),
                    row.get("quality_score"),
                    row.get("confidence_score"),
                    str(meta)[:80],
                )
            )
        fill_table(self.attempts_table, attempts_rows)

        history_rows = [
            (
                row.get("created_at"),
                row.get("speaker_id"),
                row.get("source_file"),
                row.get("generated_file"),
                row.get("synthesis_mode"),
                row.get("alignment_ratio"),
                row.get("quality_score"),
                row.get("confidence_score"),
            )
            for row in history
        ]
        fill_table(self.history_table, history_rows)

        self.mode_label.setText(
            f"Synthesis mode: {summary.get('synthesis_mode', 'mock_demo_tts_stub')} (DEMO/MOCK, preparation layer)"
        )
        self.info_label.setText(
            f"Voice attempts: {summary.get('attempts_total', 0)} | groups: {summary.get('speaker_groups', 0)} | sample bank: {summary.get('sample_bank_total', 0)}"
        )

    def show_attempt_details(self, *, preview_payload: dict, attempt: dict) -> None:
        self.preview_panel.setPlainText(json.dumps(preview_payload, ensure_ascii=False, indent=2))
        meta = attempt.get("metadata_json") or {}
        plan = meta.get("duration_plan") or {}
        self.duration_plan_panel.setPlainText(json.dumps(plan, ensure_ascii=False, indent=2))
        quality = attempt.get("quality_score", 0)
        confidence = attempt.get("confidence_score", 0)
        self.quality_confidence_label.setText(f"Voice quality/confidence: quality={quality} confidence={confidence}")
