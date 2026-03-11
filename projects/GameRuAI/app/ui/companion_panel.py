from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
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


class CompanionPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        form = QFormLayout()
        self.executable_edit = QLineEdit()
        self.watched_path_edit = QLineEdit()
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("optional args, separated by space")
        form.addRow("Executable:", self.executable_edit)
        form.addRow("Watched path:", self.watched_path_edit)
        form.addRow("Args:", self.args_edit)

        buttons = QHBoxLayout()
        self.pick_executable_btn = QPushButton("Pick Executable")
        self.pick_watch_btn = QPushButton("Pick Watched Path")
        self.launch_btn = QPushButton("Launch Companion Session")
        self.poll_btn = QPushButton("Poll Status / Watch")
        self.stop_btn = QPushButton("Stop Session")
        buttons.addWidget(self.pick_executable_btn)
        buttons.addWidget(self.pick_watch_btn)
        buttons.addWidget(self.launch_btn)
        buttons.addWidget(self.poll_btn)
        buttons.addWidget(self.stop_btn)

        self.session_status = QLabel("Session status: n/a")
        self.reindex_status = QLabel("Quick re-index: 0")

        self.sessions_table = QTableWidget(0, 7)
        self.sessions_table.setHorizontalHeaderLabels(
            ["Session", "Status", "PID", "Executable", "Watched", "Started", "Ended"]
        )
        self.events_table = QTableWidget(0, 4)
        self.events_table.setHorizontalHeaderLabels(["When", "Event", "File", "Watched Path"])

        root.addLayout(form)
        root.addLayout(buttons)
        root.addWidget(self.session_status)
        root.addWidget(self.reindex_status)
        root.addWidget(QLabel("Sessions:"))
        root.addWidget(self.sessions_table)
        root.addWidget(QLabel("Watched file events:"))
        root.addWidget(self.events_table)

    def choose_executable(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Game Executable", self.executable_edit.text())
        if file_path:
            self.executable_edit.setText(file_path)

    def choose_watched_path(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Watched Game Path", self.watched_path_edit.text())
        if folder:
            self.watched_path_edit.setText(folder)

    def args_list(self) -> list[str]:
        raw = self.args_edit.text().strip()
        if not raw:
            return []
        return [part for part in raw.split(" ") if part]

    def load_sessions(self, sessions: list[dict]) -> None:
        rows = [
            (
                session.get("session_id"),
                session.get("process_status"),
                session.get("process_pid"),
                session.get("executable_path"),
                session.get("watched_path"),
                session.get("started_at"),
                session.get("ended_at"),
            )
            for session in sessions
        ]
        fill_table(self.sessions_table, rows)

    def load_events(self, events: list[dict]) -> None:
        rows = [
            (
                event.get("created_at"),
                event.get("event_type"),
                event.get("file_path"),
                event.get("watched_path"),
            )
            for event in events
        ]
        fill_table(self.events_table, rows)
