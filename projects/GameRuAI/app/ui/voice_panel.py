from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class VoicePanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Demo Voice Attempts")
        controls.addWidget(self.generate_btn)
        root.addLayout(controls)

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

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["Line ID", "Speaker", "Source Voice", "Output Voice", "Status", "Quality", "Src ms", "Out ms", "Meta"]
        )

        self.info_label = QLabel("Voice attempts: 0")

        root.addLayout(profile_form)
        root.addWidget(self.table)
        root.addWidget(self.info_label)

    def load_voice_attempts(self, rows: list[dict]) -> None:
        data = [
            (
                row.get("line_id"),
                row.get("speaker_id"),
                row.get("source_voice_path"),
                row.get("output_voice_path"),
                row.get("status"),
                row.get("quality_score"),
                row.get("duration_source_ms"),
                row.get("duration_output_ms"),
                str(row.get("metadata_json", {}))[:60],
            )
            for row in rows
        ]
        fill_table(self.table, data)
        self.info_label.setText(f"Voice attempts: {len(rows)}")
