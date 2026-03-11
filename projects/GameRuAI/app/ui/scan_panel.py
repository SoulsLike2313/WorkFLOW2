from __future__ import annotations

import json

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget, QPlainTextEdit

from .table_utils import fill_table


class ScanPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.scan_btn = QPushButton("Run Scan")
        self.extract_btn = QPushButton("Extract Strings")
        self.info_label = QLabel("Scan demo game and build manifest.")
        self.manifest_view = QPlainTextEdit()
        self.manifest_view.setReadOnly(True)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Path", "Type", "Ext", "Bytes", "SHA1", "Group"])

        layout.addWidget(self.info_label)
        layout.addWidget(self.scan_btn)
        layout.addWidget(self.extract_btn)
        layout.addWidget(self.manifest_view)
        layout.addWidget(self.table)

    def show_manifest(self, manifest: dict) -> None:
        self.manifest_view.setPlainText(json.dumps(manifest, ensure_ascii=False, indent=2))
        rows = [
            (
                item["file_path"],
                item["file_type"],
                item["file_ext"],
                item["size_bytes"],
                item["sha1"][:10],
                item["manifest_group"],
            )
            for item in manifest.get("files", [])
        ]
        fill_table(self.table, rows)
