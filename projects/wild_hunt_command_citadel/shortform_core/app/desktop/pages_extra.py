from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from .components import GlowCard, MetricCard, SectionHeader
from .pages import BasePage


def _fmt_ts(value: Any) -> str:
    if not value:
        return "-"
    text = str(value)
    return text.replace("T", " ")[:19] if "T" in text else text[:19]


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


class AuditPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AuditPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Audit / Timeline", "Typed event stream for workspace, AI and updates"))

        actions = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Timeline")
        refresh_btn.setObjectName("PrimaryCTA")
        refresh_btn.clicked.connect(lambda: self.action_requested.emit("refresh", None))

        self.level_filter = QComboBox()
        self.level_filter.addItems(["all", "info", "warning", "error"])
        self.level_filter.currentTextChanged.connect(
            lambda _: self.action_requested.emit("refresh", None)
        )

        actions.addWidget(refresh_btn)
        actions.addWidget(QLabel("Severity:"))
        actions.addWidget(self.level_filter)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Time", "Actor", "Action", "Result", "Profile", "Source"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(130)
        layout.addWidget(self.table, stretch=1)

        self.errors = QListWidget()
        self.errors.setMinimumHeight(120)
        layout.addWidget(SectionHeader("Recent Failures", "Error log and policy denials"))
        layout.addWidget(self.errors)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        selected = self.level_filter.currentText()
        items = _safe_list(snapshot.get("audit_log"))
        errors = _safe_list(snapshot.get("error_log"))

        self.table.setRowCount(0)
        for event in items:
            result = str(event.get("result", "-")).lower()
            level = "info"
            if "error" in result or "denied" in result or "failed" in result:
                level = "error"
            elif "warn" in result:
                level = "warning"

            if selected != "all" and selected != level:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(_fmt_ts(event.get("created_at"))))
            self.table.setItem(row, 1, QTableWidgetItem(str(event.get("actor_type", "system"))))
            self.table.setItem(row, 2, QTableWidgetItem(str(event.get("action_type", "-"))))
            self.table.setItem(row, 3, QTableWidgetItem(str(event.get("result", "-"))))
            self.table.setItem(row, 4, QTableWidgetItem(str(event.get("profile_id", "-"))))
            self.table.setItem(row, 5, QTableWidgetItem(str(event.get("source", "workspace"))))

        self.errors.clear()
        for err in errors[:20]:
            self.errors.addItem(
                f"{_fmt_ts(err.get('created_at'))} | {err.get('action_type', '-')} | {err.get('error_text', '-') }"
            )
        if self.errors.count() == 0:
            self.errors.addItem("No recent failures.")


class UpdatesPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("UpdatesPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Updates", "Version state, patch status and post-update verification"))

        cards = QHBoxLayout()
        self.current_version = MetricCard("Current Version", "-", "runtime")
        self.available_version = MetricCard("Available", "-", "manifest")
        self.patch_status = MetricCard("Patch Status", "-", "local patch flow")
        self.post_verify = MetricCard("Post Verify", "-", "machine gate")
        cards.addWidget(self.current_version)
        cards.addWidget(self.available_version)
        cards.addWidget(self.patch_status)
        cards.addWidget(self.post_verify)
        layout.addLayout(cards)

        actions = QHBoxLayout()
        check_btn = QPushButton("Check Updates")
        check_btn.setObjectName("PrimaryCTA")
        check_btn.clicked.connect(lambda: self.action_requested.emit("check_updates", None))
        post_btn = QPushButton("Run Post-Verify")
        post_btn.clicked.connect(lambda: self.action_requested.emit("run_post_verify", None))
        actions.addWidget(check_btn)
        actions.addWidget(post_btn)
        actions.addStretch(1)
        layout.addLayout(actions)

        details_card = GlowCard(elevated=False)
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(12, 10, 12, 10)
        details_layout.setSpacing(8)
        details_layout.addWidget(SectionHeader("Update Diagnostics", "Machine-readable summary reflected for operators"))

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        details_layout.addWidget(self.details)

        layout.addWidget(details_card, stretch=1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        updates = _safe_dict(snapshot.get("updates"))
        ver = _safe_dict(updates.get("version"))
        check = _safe_dict(updates.get("check"))
        patch = _safe_dict(updates.get("patch_result"))
        post = _safe_dict(updates.get("post_verify"))

        current_label = str(ver.get("version_label") or ver.get("version") or "unknown")
        self.current_version.set_data(current_label, f"build={ver.get('build', '-')}")

        avail = str(check.get("available_version") or check.get("available") or "n/a")
        self.available_version.set_data(avail, "compat" if check.get("is_compatible") else "no manifest")

        patch_status = str(patch.get("status") or updates.get("patch_status") or "idle")
        self.patch_status.set_data(patch_status, str(patch.get("message", "local patch flow")))

        post_status = str(post.get("status") or updates.get("post_verify_status") or "unknown")
        self.post_verify.set_data(post_status, "manual test allowed only when PASS")

        lines = [
            f"Checked at: {_fmt_ts(datetime.now().isoformat())}",
            f"Current version: {current_label}",
            f"Available version: {avail}",
            f"Compatibility: {check.get('is_compatible', False)}",
            f"Patch status: {patch_status}",
            f"Post-verify status: {post_status}",
            "",
            "Patch notes:",
        ]

        for note in _safe_list(check.get("patch_notes"))[:10]:
            lines.append(f"- {note}")

        details = post.get("details")
        if isinstance(details, dict):
            lines.append("")
            lines.append("Post-verify details:")
            for key, value in details.items():
                lines.append(f"- {key}: {value}")

        self.details.setPlainText("\n".join(lines).strip())


class SettingsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SettingsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Settings", "Workspace/runtime settings and diagnostics references"))

        card = GlowCard(elevated=False)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(10)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(8)

        self.mode = QLabel("-")
        self.api_base = QLabel("-")
        self.data_dir = QLabel("-")
        self.logs_dir = QLabel("-")
        self.db_path = QLabel("-")
        self.verification_state = QLabel("-")

        form.addRow("Mode:", self.mode)
        form.addRow("API base:", self.api_base)
        form.addRow("Data directory:", self.data_dir)
        form.addRow("Logs directory:", self.logs_dir)
        form.addRow("Database path:", self.db_path)
        form.addRow("Verification gate:", self.verification_state)

        card_layout.addLayout(form)

        actions = QHBoxLayout()
        diagnostics_btn = QPushButton("Open Diagnostics Guide")
        diagnostics_btn.clicked.connect(lambda: self.action_requested.emit("open_diagnostics", None))
        reload_btn = QPushButton("Reload Settings")
        reload_btn.setObjectName("PrimaryCTA")
        reload_btn.clicked.connect(lambda: self.action_requested.emit("refresh", None))
        actions.addWidget(diagnostics_btn)
        actions.addWidget(reload_btn)
        actions.addStretch(1)
        card_layout.addLayout(actions)

        layout.addWidget(card)
        layout.addStretch(1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        config = _safe_dict(snapshot.get("runtime_config"))
        self.mode.setText(str(config.get("mode", "user")))
        self.api_base.setText(str(snapshot.get("api_base_url", "-")))
        self.data_dir.setText(str(config.get("data_dir", "runtime/data")))
        self.logs_dir.setText(str(config.get("logs_dir", "runtime/logs")))
        self.db_path.setText(str(config.get("db_path", "runtime/data/workspace_state.db")))
        self.verification_state.setText(str(snapshot.get("verification_state", "UNKNOWN")))


class PlaceholderPage(BasePage):
    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(SectionHeader(title, subtitle))
        card = GlowCard(elevated=False)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)
        label = QLabel("Screen module is being connected to live data.")
        label.setWordWrap(True)
        card_layout.addWidget(label)
        layout.addWidget(card)
        layout.addStretch(1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        _ = snapshot
