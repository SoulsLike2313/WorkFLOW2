from __future__ import annotations

import json

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget

from .table_utils import fill_table


class DiagnosticsPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.refresh_btn = QPushButton("Refresh Diagnostics")
        self.status_label = QLabel("Diagnostics: n/a")

        self.backend_table = QTableWidget(0, 6)
        self.backend_table.setHorizontalHeaderLabels(
            ["Backend", "Runs", "Avg ms", "P95 ms", "Fallback rate", "Context rate"]
        )
        self.report_table = QTableWidget(0, 3)
        self.report_table.setHorizontalHeaderLabels(["Report Type", "Created", "Payload"])
        self.quality_table = QTableWidget(0, 3)
        self.quality_table.setHorizontalHeaderLabels(["Snapshot", "Created", "Metrics"])

        root.addWidget(self.refresh_btn)
        root.addWidget(self.status_label)
        root.addWidget(QLabel("Backend diagnostics:"))
        root.addWidget(self.backend_table)
        root.addWidget(QLabel("Report history:"))
        root.addWidget(self.report_table)
        root.addWidget(QLabel("Quality snapshots:"))
        root.addWidget(self.quality_table)

    def load_diagnostics(self, snapshot: dict) -> None:
        backend_rows = [
            (
                row.get("backend_name"),
                row.get("runs_count"),
                row.get("avg_latency_ms"),
                row.get("p95_latency_ms"),
                row.get("fallback_rate", 0),
                row.get("context_used_rate"),
            )
            for row in snapshot.get("backend_diagnostics", [])
        ]
        fill_table(self.backend_table, backend_rows)

        report_rows = [
            (
                row.get("report_type"),
                row.get("created_at"),
                json.dumps(row.get("payload_json", {}), ensure_ascii=False)[:90],
            )
            for row in snapshot.get("project_reports", [])
        ]
        fill_table(self.report_table, report_rows)

        quality_rows = [
            (
                row.get("snapshot_type"),
                row.get("created_at"),
                json.dumps(row.get("payload_json", {}), ensure_ascii=False)[:90],
            )
            for row in snapshot.get("quality_snapshots", [])
        ]
        fill_table(self.quality_table, quality_rows)

        self.status_label.setText(
            f"Diagnostics: backends={len(backend_rows)} reports={len(report_rows)} snapshots={len(quality_rows)}"
        )
