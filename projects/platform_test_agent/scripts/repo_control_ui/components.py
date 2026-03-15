from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .theme import PALETTE, SPACE_1, SPACE_2, SPACE_3, SPACE_4


@dataclass(frozen=True)
class StatusViewModel:
    name: str
    status: str
    summary: str


def _status_colors(status: str) -> tuple[str, str]:
    status_upper = status.upper()
    if status_upper == "PASS":
        return PALETTE.success, "#133325"
    if status_upper in {"FAIL", "NOT TRUSTED"}:
        return PALETTE.danger, "#3d1820"
    if status_upper in {"WARN", "WARNING", "PARTIAL"}:
        return PALETTE.warning, "#3a2e15"
    return PALETTE.accent, PALETTE.accent_soft


class HeaderMetaPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Panel")

        layout = QGridLayout(self)
        layout.setHorizontalSpacing(SPACE_4)
        layout.setVerticalSpacing(SPACE_1)
        layout.setContentsMargins(SPACE_4, SPACE_3, SPACE_4, SPACE_3)

        self.repo_value = self._add_pair(layout, 0, "Repo")
        self.branch_value = self._add_pair(layout, 1, "Branch")
        self.tracking_value = self._add_pair(layout, 2, "Tracking")
        self.checked_value = self._add_pair(layout, 3, "Last checked")
        self.sha_value = self._add_pair(layout, 4, "HEAD")

    def _add_pair(self, layout: QGridLayout, column: int, label: str) -> QLabel:
        title = QLabel(label)
        title.setObjectName("MetaLabel")
        value = QLabel("-")
        value.setObjectName("MetaValue")
        value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(title, 0, column)
        layout.addWidget(value, 1, column)
        return value

    def set_values(self, repo: str, branch: str, tracking: str, checked: str, sha_short: str) -> None:
        self.repo_value.setText(repo)
        self.branch_value.setText(branch)
        self.tracking_value.setText(tracking)
        self.checked_value.setText(checked)
        self.sha_value.setText(sha_short)


class HeroCard(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("HeroCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_4, SPACE_4, SPACE_4, SPACE_4)
        layout.setSpacing(SPACE_1)

        top_row = QHBoxLayout()
        top_row.setSpacing(SPACE_2)
        top_row.addStretch(1)

        self.verdict_chip = QLabel("REPO")
        self.verdict_chip.setObjectName("StatusBadge")
        self.verdict_chip.setAlignment(Qt.AlignCenter)
        self.verdict_chip.setMinimumWidth(88)
        top_row.addWidget(self.verdict_chip)

        self.verdict_label = QLabel("NOT TRUSTED")
        self.verdict_label.setObjectName("HeroVerdict")
        self.subtitle_label = QLabel("Run refresh to evaluate repository trust state.")
        self.subtitle_label.setObjectName("HeroSubtitle")
        self.subtitle_label.setWordWrap(True)

        layout.addLayout(top_row)
        layout.addWidget(self.verdict_label)
        layout.addWidget(self.subtitle_label)

    def set_verdict(self, verdict: str, subtitle: str) -> None:
        verdict_upper = verdict.upper()
        self.verdict_label.setText(verdict_upper)
        self.subtitle_label.setText(subtitle)
        status = "PASS" if verdict_upper == "TRUSTED" else "FAIL"
        color, bg = _status_colors(status)
        self.verdict_label.setStyleSheet(f"color: {color};")
        self.verdict_chip.setText(verdict_upper)
        self.verdict_chip.setStyleSheet(f"color: {color}; background: {bg}; border: 1px solid {color};")


class StatusCard(QFrame):
    def __init__(self, title: str, default_hint: str) -> None:
        super().__init__()
        self.setObjectName("Panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_3, SPACE_3, SPACE_3, SPACE_3)
        layout.setSpacing(SPACE_1)

        top_row = QHBoxLayout()
        top_row.setSpacing(SPACE_2)

        self.title = QLabel(title)
        self.title.setObjectName("StatusName")

        self.badge = QLabel("CHECK")
        self.badge.setObjectName("StatusBadge")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setMinimumWidth(70)

        top_row.addWidget(self.title)
        top_row.addStretch(1)
        top_row.addWidget(self.badge)

        self.status_text = QLabel("-")
        self.status_text.setObjectName("StatusText")
        self.summary_text = QLabel(default_hint)
        self.summary_text.setObjectName("StatusSummary")
        self.summary_text.setWordWrap(True)

        layout.addLayout(top_row)
        layout.addWidget(self.status_text)
        layout.addWidget(self.summary_text)

    def set_status(self, model: StatusViewModel) -> None:
        status_upper = model.status.upper()
        color, bg = _status_colors(status_upper)
        self.badge.setText(status_upper)
        self.badge.setStyleSheet(f"color: {color}; background: {bg}; border: 1px solid {color};")
        self.status_text.setText(status_upper)
        self.status_text.setStyleSheet(f"color: {color};")
        self.summary_text.setText(model.summary)


class WhyNotTrustedPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_3, SPACE_3, SPACE_3, SPACE_3)
        layout.setSpacing(SPACE_2)

        title = QLabel("Why not trusted")
        title.setObjectName("SectionTitle")
        hint = QLabel("Only blocking reasons, highest priority first.")
        hint.setObjectName("SectionHint")

        self.issue_list = QListWidget()
        self.issue_list.setObjectName("IssuesList")

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.issue_list)

    def set_issues(self, issues: list[str], trusted: bool) -> None:
        self.issue_list.clear()
        if trusted:
            ok_item = QListWidgetItem("Repository is trusted. No blocking issues.")
            self.issue_list.addItem(ok_item)
            return
        if not issues:
            self.issue_list.addItem(QListWidgetItem("Status is not trusted, but no explicit blocker message was produced."))
            return
        for issue in issues:
            self.issue_list.addItem(QListWidgetItem(issue))


class ActionPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Panel")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACE_3, SPACE_3, SPACE_3, SPACE_3)
        layout.setSpacing(SPACE_2)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("PrimaryButton")

        self.open_repo_button = QPushButton("Open Repo Folder")
        self.open_keys_button = QPushButton("Open Key Files")
        self.rebuild_manifest_button = QPushButton("Rebuild Manifest")
        self.rebuild_manifest_button.setObjectName("DangerSecondaryButton")
        self.copy_summary_button = QPushButton("Copy Diagnostic Summary")

        layout.addWidget(self.refresh_button)
        layout.addWidget(self.open_repo_button)
        layout.addWidget(self.open_keys_button)
        layout.addWidget(self.rebuild_manifest_button)
        layout.addWidget(self.copy_summary_button)
        layout.addStretch(1)


class TechnicalDetailsPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Panel")

        self._collapsed = True

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_3, SPACE_3, SPACE_3, SPACE_3)
        root.setSpacing(SPACE_2)

        self.toggle_button = QToolButton()
        self.toggle_button.setObjectName("CollapseButton")
        self.toggle_button.setText("Technical details")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextOnly)

        self.text = QTextEdit()
        self.text.setObjectName("TechnicalText")
        self.text.setReadOnly(True)
        self.text.setMinimumHeight(170)
        self.text.setVisible(False)

        root.addWidget(self.toggle_button)
        root.addWidget(self.text)

        self.toggle_button.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool) -> None:
        self._collapsed = not checked
        self.text.setVisible(checked)
        self.toggle_button.setText("Technical details (expanded)" if checked else "Technical details (collapsed)")

    def set_details(self, details_text: str) -> None:
        self.text.setPlainText(details_text)
