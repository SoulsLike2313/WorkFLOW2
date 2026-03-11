from __future__ import annotations

import json

from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget


class JobsPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.refresh_btn = QPushButton("Refresh Job States")
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.status_label = QLabel("Jobs: n/a")
        root.addWidget(self.refresh_btn)
        root.addWidget(self.log_view)
        root.addWidget(self.status_label)

    def show_jobs(self, jobs: dict) -> None:
        self.log_view.setPlainText(json.dumps(jobs, ensure_ascii=False, indent=2))
        self.status_label.setText(f"Tracked jobs: {len(jobs)}")
