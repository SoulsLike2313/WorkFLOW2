from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class AssetExplorerPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._assets_by_path: dict[str, dict] = {}

        root = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Asset Index")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["all", "texture", "audio", "textual", "archive", "binary", "binary_unknown"])
        self.summary_label = QLabel("Assets: 0")
        controls.addWidget(self.refresh_btn)
        controls.addWidget(QLabel("Filter:"))
        controls.addWidget(self.filter_combo)
        controls.addWidget(self.summary_label)

        splitter = QSplitter()
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.resource_tree = QTreeWidget()
        self.resource_tree.setHeaderLabels(["Resource", "Type", "Preview", "Relevance"])
        left_layout.addWidget(self.resource_tree)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.metadata_view = QPlainTextEdit()
        self.metadata_view.setReadOnly(True)
        self.texture_label = QLabel("Texture preview: metadata-only")
        self.texture_label.setAlignment(Qt.AlignCenter)
        self.texture_label.setMinimumHeight(220)
        self.audio_label = QLabel("Audio preview: metadata-only")
        self.archive_table = QTableWidget(0, 4)
        self.archive_table.setHorizontalHeaderLabels(["File", "Suspected", "Confidence", "Reason"])
        right_layout.addWidget(QLabel("File metadata:"))
        right_layout.addWidget(self.metadata_view)
        right_layout.addWidget(QLabel("Texture preview:"))
        right_layout.addWidget(self.texture_label)
        right_layout.addWidget(QLabel("Audio preview:"))
        right_layout.addWidget(self.audio_label)
        right_layout.addWidget(QLabel("Archive/container report:"))
        right_layout.addWidget(self.archive_table)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([620, 780])

        root.addLayout(controls)
        root.addWidget(splitter)

    def selected_file_path(self) -> str | None:
        item = self.resource_tree.currentItem()
        if not item:
            return None
        file_path = item.data(0, Qt.UserRole)
        return str(file_path) if file_path else None

    def load_snapshot(self, snapshot: dict) -> None:
        assets = snapshot.get("assets", [])
        reports = snapshot.get("archive_reports", [])
        asset_filter = self.filter_combo.currentText()

        self._assets_by_path = {
            str(item.get("file_path")): item
            for item in assets
            if asset_filter == "all" or str(item.get("asset_type")) == asset_filter
        }
        self._render_tree(list(self._assets_by_path.values()))
        self._render_reports(reports)

        totals = snapshot.get("totals", {})
        self.summary_label.setText(
            f"Assets: {totals.get('assets', 0)} | preview ready: {totals.get('preview_ready', 0)} | metadata-only: {totals.get('metadata_only', 0)}"
        )

    def show_details(self, details: dict) -> None:
        asset = details.get("asset") or {}
        preview = details.get("preview") or {}
        archive = details.get("archive") or {}
        payload = {
            "asset": asset,
            "preview": preview,
            "archive": archive,
        }
        self.metadata_view.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2))

        self._set_texture_preview(preview)
        self._set_audio_preview(preview)

    def _render_tree(self, assets: list[dict]) -> None:
        self.resource_tree.clear()
        nodes: dict[str, QTreeWidgetItem] = {}
        for asset in assets:
            file_path = str(asset.get("file_path") or "")
            if not file_path:
                continue
            parts = file_path.split("/")
            parent_item: QTreeWidgetItem | None = None
            current_key = ""
            for idx, part in enumerate(parts):
                current_key = f"{current_key}/{part}" if current_key else part
                if current_key in nodes:
                    parent_item = nodes[current_key]
                    continue
                if idx == len(parts) - 1:
                    item = QTreeWidgetItem(
                        [
                            part,
                            str(asset.get("asset_type", "")),
                            str(asset.get("preview_status", "")),
                            str(asset.get("relevance_score", "")),
                        ]
                    )
                    item.setData(0, Qt.UserRole, file_path)
                else:
                    item = QTreeWidgetItem([part, "folder", "", ""])
                nodes[current_key] = item
                if parent_item is None:
                    self.resource_tree.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)
                parent_item = item
        self.resource_tree.expandToDepth(2)

    def _render_reports(self, reports: list[dict]) -> None:
        rows = [
            (
                row.get("file_path"),
                "yes" if row.get("suspected_container") else "no",
                row.get("confidence"),
                row.get("reason"),
            )
            for row in reports
        ]
        fill_table(self.archive_table, rows)

    def _set_texture_preview(self, preview: dict) -> None:
        if preview.get("preview_type") != "texture" or preview.get("preview_status") != "ready":
            self.texture_label.setPixmap(QPixmap())
            self.texture_label.setText("Texture preview: metadata-only")
            return

        preview_path = str(preview.get("preview_path") or "")
        if not preview_path or not Path(preview_path).exists():
            self.texture_label.setPixmap(QPixmap())
            self.texture_label.setText("Texture preview: file not available")
            return

        pixmap = QPixmap(preview_path)
        if pixmap.isNull():
            self.texture_label.setPixmap(QPixmap())
            self.texture_label.setText("Texture preview: unsupported image codec")
            return
        self.texture_label.setText("")
        self.texture_label.setPixmap(pixmap.scaled(420, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _set_audio_preview(self, preview: dict) -> None:
        if preview.get("preview_type") != "audio":
            self.audio_label.setText("Audio preview: metadata-only")
            return
        metadata = preview.get("metadata_json") or {}
        if preview.get("preview_status") != "ready":
            self.audio_label.setText("Audio preview: metadata-only")
            return
        duration = metadata.get("duration_ms", "n/a")
        channels = metadata.get("channels", "n/a")
        sample_rate = metadata.get("sample_rate", "n/a")
        self.audio_label.setText(f"Audio preview ready | duration={duration}ms channels={channels} rate={sample_rate}")

