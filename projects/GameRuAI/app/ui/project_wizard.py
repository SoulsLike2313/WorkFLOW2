from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)


class ProjectWizardPanel(QWidget):
    def __init__(self, default_fixture_path: Path):
        super().__init__()
        self.default_fixture_path = default_fixture_path

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.project_name_edit = QLineEdit("GameRuAI Demo Project")
        self.game_path_edit = QLineEdit(str(default_fixture_path))

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_game_path)
        use_fixture_btn = QPushButton("Use Demo Fixture")
        use_fixture_btn.clicked.connect(lambda: self.game_path_edit.setText(str(self.default_fixture_path)))

        path_row = QHBoxLayout()
        path_row.addWidget(self.game_path_edit)
        path_row.addWidget(browse_btn)
        path_row.addWidget(use_fixture_btn)

        form.addRow("Project Name:", self.project_name_edit)
        form.addRow("Game Path:", path_row)

        self.create_btn = QPushButton("Create/Select Project")
        self.info_label = QLabel("Select demo game folder and create project.")

        layout.addLayout(form)
        layout.addWidget(self.create_btn)
        layout.addWidget(self.info_label)
        layout.addStretch(1)

    def _browse_game_path(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Demo Game Folder", self.game_path_edit.text())
        if directory:
            self.game_path_edit.setText(directory)
