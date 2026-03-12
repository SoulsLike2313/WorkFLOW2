from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget

from .table_utils import fill_table


class SyncReviewPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.refresh_btn = QPushButton("Refresh Sync Review")
        self.status_label = QLabel("Sync Review: n/a")
        self.risk_label = QLabel("Export risk: n/a")

        self.sync_table = QTableWidget(0, 7)
        self.sync_table.setHorizontalHeaderLabels(
            ["Line", "Source ms", "Target ms", "Delta", "Adjustment", "Confidence", "Status"]
        )

        root.addWidget(self.refresh_btn)
        root.addWidget(self.status_label)
        root.addWidget(self.risk_label)
        root.addWidget(self.sync_table)

    def load_snapshot(self, snapshot: dict) -> None:
        sync_plans = snapshot.get("sync_plans", []) or []
        fill_table(
            self.sync_table,
            [
                (
                    row.get("line_id"),
                    row.get("source_duration_ms"),
                    row.get("target_duration_ms"),
                    row.get("delta_ms"),
                    row.get("recommended_adjustment"),
                    row.get("confidence"),
                    row.get("status"),
                )
                for row in sync_plans
            ],
        )
        self.status_label.setText(
            f"Sync Review: plans={len(sync_plans)} high_risk={snapshot.get('high_risk_count', 0)} subtitle_issues={snapshot.get('subtitle_issue_count', 0)}"
        )
        risk = snapshot.get("export_risk_summary", {}) or {}
        self.risk_label.setText(f"Export risk summary: high={risk.get('high', 0)} normal={risk.get('medium_or_low', 0)}")

