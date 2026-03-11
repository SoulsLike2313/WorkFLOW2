from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)


class ExportPanel(QWidget):
    def __init__(self, default_path: str):
        super().__init__()
        root = QVBoxLayout(self)

        row = QHBoxLayout()
        self.path_edit = QLineEdit(default_path)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        self.export_btn = QPushButton("Export Patch Output")

        row.addWidget(self.path_edit)
        row.addWidget(browse_btn)
        row.addWidget(self.export_btn)

        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.setPlainText("No exports yet.")

        root.addLayout(row)
        root.addWidget(QLabel("Export log:"))
        root.addWidget(self.info)

    def _browse(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Export Folder", self.path_edit.text())
        if directory:
            self.path_edit.setText(directory)
