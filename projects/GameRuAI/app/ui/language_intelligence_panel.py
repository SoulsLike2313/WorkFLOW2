from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget

from .table_utils import fill_table


class LanguageIntelligencePanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.refresh_btn = QPushButton("Refresh Language Intelligence")
        self.status_label = QLabel("Language Intelligence: n/a")

        self.languages_table = QTableWidget(0, 2)
        self.languages_table.setHorizontalHeaderLabels(["Language", "Lines"])
        self.bottleneck_table = QTableWidget(0, 2)
        self.bottleneck_table.setHorizontalHeaderLabels(["Language", "Pending/Uncertain"])
        self.uncertain_table = QTableWidget(0, 5)
        self.uncertain_table.setHorizontalHeaderLabels(["Line ID", "Type", "Lang", "Confidence", "File"])

        root.addWidget(self.refresh_btn)
        root.addWidget(self.status_label)
        root.addWidget(QLabel("Language distribution:"))
        root.addWidget(self.languages_table)
        root.addWidget(QLabel("Language bottlenecks:"))
        root.addWidget(self.bottleneck_table)
        root.addWidget(QLabel("Uncertain / ambiguous content units:"))
        root.addWidget(self.uncertain_table)

    def load_snapshot(self, snapshot: dict) -> None:
        distribution = snapshot.get("language_distribution", {}) or {}
        bottlenecks = snapshot.get("bottlenecks", {}) or {}
        uncertain_units = snapshot.get("uncertain_units", []) or []
        coverage = snapshot.get("coverage", {}) or {}

        fill_table(self.languages_table, [(k, v) for k, v in sorted(distribution.items())])
        fill_table(self.bottleneck_table, [(k, v) for k, v in sorted(bottlenecks.items(), key=lambda item: (-item[1], item[0]))])
        uncertain_rows = [
            (
                row.get("line_id", ""),
                row.get("content_type", ""),
                row.get("source_lang", ""),
                row.get("confidence", 0),
                row.get("file_path", ""),
            )
            for row in uncertain_units
        ]
        fill_table(self.uncertain_table, uncertain_rows)

        self.status_label.setText(
            f"Language Intelligence: coverage={coverage.get('coverage_rate', 0)} uncertain={len(uncertain_units)}"
        )

