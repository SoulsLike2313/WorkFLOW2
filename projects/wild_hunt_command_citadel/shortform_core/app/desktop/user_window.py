from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class UserWorkspaceWindow(QMainWindow):
    def __init__(self, *, api_base_url: str) -> None:
        super().__init__()
        self.api_base_url = api_base_url.rstrip("/")
        self.setWindowTitle("Shortform Workspace")
        self.resize(980, 640)
        self.setMinimumSize(860, 560)
        self._build_ui()
        self.refresh_workspace()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel("Shortform Multi-Profile Workspace")
        header.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(header)

        self.status = QLabel("Loading...")
        self.status.setStyleSheet("font-size: 13px; color: #cfd8e3;")
        layout.addWidget(self.status)

        row = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_workspace)
        self.create_profile_button = QPushButton("Create Demo Profile")
        self.create_profile_button.clicked.connect(self.create_demo_profile)
        self.open_docs_button = QPushButton("API Health")
        self.open_docs_button.clicked.connect(self.check_api_health)
        row.addWidget(self.refresh_button)
        row.addWidget(self.create_profile_button)
        row.addWidget(self.open_docs_button)
        row.addStretch(1)
        layout.addLayout(row)

        body = QHBoxLayout()
        self.profiles_list = QListWidget()
        self.profiles_list.setAlternatingRowColors(True)
        body.addWidget(self.profiles_list, stretch=3)

        self.audit_list = QListWidget()
        self.audit_list.setAlternatingRowColors(True)
        body.addWidget(self.audit_list, stretch=2)
        layout.addLayout(body, stretch=1)

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.api_base_url, timeout=5.0)

    def refresh_workspace(self) -> None:
        try:
            with self._client() as client:
                health = client.get("/workspace/health")
                profiles = client.get("/workspace/profiles")
                audit = client.get("/workspace/audit/log?limit=20")
            health.raise_for_status()
            profiles.raise_for_status()
            audit.raise_for_status()
        except Exception as exc:
            self.status.setText(f"Connection error: {exc}")
            return

        health_data = health.json()
        profiles_data = profiles.json()
        audit_data = audit.json()
        self._render_profiles(profiles_data.get("items", []))
        self._render_audit(audit_data.get("items", []))
        summary = health_data.get("summary", {})
        self.status.setText(
            "Ready | "
            f"profiles={summary.get('profile_count', 0)} "
            f"active={summary.get('active_profiles', 0)} "
            f"queued={summary.get('queued_content_items', 0)} "
            f"updated={datetime.now().strftime('%H:%M:%S')}"
        )

    def create_demo_profile(self) -> None:
        payload = {
            "display_name": f"Desktop Demo {datetime.now().strftime('%H:%M:%S')}",
            "platform": "tiktok",
            "connection_type": "cdp",
            "management_mode": "guided",
            "notes": "Created from user mode desktop.",
            "tags": ["desktop", "user_mode"],
        }
        try:
            with self._client() as client:
                response = client.post("/workspace/profiles", json=payload)
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Profile creation failed", str(exc))

    def check_api_health(self) -> None:
        try:
            with self._client() as client:
                response = client.get("/health")
            response.raise_for_status()
            body = response.json()
            QMessageBox.information(
                self,
                "API Health",
                f"status={body.get('status')}\ndatabase={body.get('database_path')}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "API unavailable", str(exc))

    def _render_profiles(self, items: list[dict[str, Any]]) -> None:
        self.profiles_list.clear()
        for item in items:
            line = (
                f"{item.get('display_name', 'unknown')} | "
                f"mode={item.get('management_mode')} | "
                f"status={item.get('status')} | "
                f"health={item.get('health_state')}"
            )
            self.profiles_list.addItem(line)

    def _render_audit(self, items: list[dict[str, Any]]) -> None:
        self.audit_list.clear()
        for item in items[:20]:
            line = f"{item.get('created_at', '')} | {item.get('action_type', '')} | {item.get('result', '')}"
            self.audit_list.addItem(line)
        if self.audit_list.count() == 0:
            self.audit_list.addItem("No audit events yet.")

