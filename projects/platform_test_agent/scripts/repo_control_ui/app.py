from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from .components import (
    ActionPanel,
    HeaderMetaPanel,
    HeroCard,
    StatusCard,
    StatusViewModel,
    TechnicalDetailsPanel,
    WhyNotTrustedPanel,
)
from .diagnostics import RepoControlDiagnostics
from .theme import (
    PALETTE,
    SPACE_2,
    SPACE_3,
    SPACE_4,
    SPACE_5,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    build_stylesheet,
)


class RepoControlMainWindow(QMainWindow):
    def __init__(self, diagnostics: RepoControlDiagnostics | None = None) -> None:
        super().__init__()
        self.diagnostics = diagnostics or RepoControlDiagnostics()
        self.current_snapshot = None

        self.setObjectName("RepoControlWindow")
        self.setWindowTitle("Repository Trust Control")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(SPACE_5, SPACE_5, SPACE_5, SPACE_5)
        root_layout.setSpacing(SPACE_4)

        self.meta_panel = HeaderMetaPanel()
        self.hero = HeroCard()

        status_wrapper = QWidget()
        status_grid = QGridLayout(status_wrapper)
        status_grid.setContentsMargins(0, 0, 0, 0)
        status_grid.setSpacing(SPACE_3)

        self.status_cards = {
            "repo_integrity": StatusCard("Repo integrity", "Git structure and operation state"),
            "github_sync": StatusCard("GitHub sync", "Branch tracking and divergence"),
            "safe_files_present": StatusCard("Safe reading files present", "Required files are available"),
            "safe_files_match_manifest": StatusCard("Safe reading files match manifest", "Hash verification against manifest"),
        }

        status_grid.addWidget(self.status_cards["repo_integrity"], 0, 0)
        status_grid.addWidget(self.status_cards["github_sync"], 0, 1)
        status_grid.addWidget(self.status_cards["safe_files_present"], 1, 0)
        status_grid.addWidget(self.status_cards["safe_files_match_manifest"], 1, 1)

        self.why_not_trusted = WhyNotTrustedPanel()
        self.actions = ActionPanel()
        self.tech = TechnicalDetailsPanel()

        technical_header = QHBoxLayout()
        technical_title = QLabel("Quick diagnostics")
        technical_title.setObjectName("SectionTitle")
        technical_hint = QLabel("Low-noise technical details for fast root-cause checks.")
        technical_hint.setObjectName("SectionHint")
        technical_header.addWidget(technical_title)
        technical_header.addStretch(1)
        technical_header.addWidget(technical_hint)

        root_layout.addWidget(self.meta_panel)
        root_layout.addWidget(self.hero)
        root_layout.addWidget(status_wrapper)
        root_layout.addWidget(self.why_not_trusted)
        root_layout.addWidget(self.actions)
        root_layout.addLayout(technical_header)
        root_layout.addWidget(self.tech)

        self.setStyleSheet(build_stylesheet())

        self.actions.refresh_button.clicked.connect(self.refresh_state)
        self.actions.open_repo_button.clicked.connect(self.open_repo_folder)
        self.actions.open_keys_button.clicked.connect(self.open_key_files)
        self.actions.rebuild_manifest_button.clicked.connect(self.rebuild_manifest)
        self.actions.copy_summary_button.clicked.connect(self.copy_summary)

        self.refresh_state()

    def refresh_state(self) -> None:
        snapshot = self.diagnostics.collect()
        self.current_snapshot = snapshot

        self.meta_panel.set_values(
            repo=f"{snapshot.repo_name} ({snapshot.repo_path})",
            branch=snapshot.branch,
            tracking=snapshot.tracking_branch,
            checked=snapshot.checked_at,
            sha_short=snapshot.short_head,
        )

        self.hero.set_verdict(snapshot.verdict, snapshot.subtitle)
        for key, card in self.status_cards.items():
            state = snapshot.statuses.get(key, {"status": "FAIL", "summary": "Status missing"})
            card.set_status(
                StatusViewModel(
                    name=key,
                    status=state.get("status", "FAIL"),
                    summary=state.get("summary", "Unknown status"),
                )
            )

        self.why_not_trusted.set_issues(snapshot.issues, snapshot.trusted)
        self.tech.set_details(snapshot.details_text)
        self.statusBar().showMessage(
            "Repository trusted" if snapshot.trusted else f"Repository not trusted: {len(snapshot.issues)} issue(s)",
            4000,
        )

    def open_repo_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.diagnostics.repo_root)))

    def open_key_files(self) -> None:
        key_files = self.diagnostics.key_files()
        if not key_files:
            QMessageBox.warning(self, "Key Files", "No key files found.")
            return
        for path in key_files:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.resolve())))

    def rebuild_manifest(self) -> None:
        manifest_path = self.diagnostics.rebuild_manifest()
        self.statusBar().showMessage(f"Safe-reading manifest rebuilt: {manifest_path}", 5000)
        self.refresh_state()

    def copy_summary(self) -> None:
        if self.current_snapshot is None:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_snapshot.summary_text)
        self.statusBar().showMessage("Diagnostic summary copied", 3000)


def launch() -> int:
    app = QApplication.instance() or QApplication([])
    window = RepoControlMainWindow()
    window.show()
    return app.exec()
