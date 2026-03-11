from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class LiveDemoPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.scene_combo = QComboBox()
        self.start_btn = QPushButton("Start Live Demo")
        controls.addWidget(QLabel("Scene:"))
        controls.addWidget(self.scene_combo)
        controls.addWidget(self.start_btn)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Line ID", "Source", "Lang", "RU", "Voice", "Uncertainty", "Decision"]
        )
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        root.addLayout(controls)
        root.addWidget(self.table)
        root.addWidget(QLabel("Live pipeline log:"))
        root.addWidget(self.log_view)

    def load_scenes(self, scenes: list[dict]) -> None:
        self.scene_combo.clear()
        for scene in scenes:
            self.scene_combo.addItem(f"{scene.get('scene_id')} :: {scene.get('title')}", scene.get("scene_id"))

    def append_live_row(self, row: dict) -> None:
        current = []
        for r in range(self.table.rowCount()):
            current.append([self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(7)])

        current.append(
            [
                row.get("line_id", ""),
                row.get("source_text", "")[:60],
                row.get("detected_lang", ""),
                row.get("translated_text", "")[:60],
                row.get("voice_status", ""),
                row.get("uncertainty", ""),
                "; ".join(row.get("decision_log", [])[:2]),
            ]
        )
        fill_table(self.table, current)
        self.log_view.append(
            f"{row.get('line_id')} | {row.get('detected_lang')} -> {row.get('translated_text')} | voice={row.get('voice_status')}"
        )
