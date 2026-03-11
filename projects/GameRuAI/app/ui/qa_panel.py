from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget

from .table_utils import fill_table


class QaPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.run_btn = QPushButton("Run QA Checks")
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Entry", "Check", "Severity", "Message", "Created"])
        self.info_label = QLabel("QA findings: 0")
        root.addWidget(self.run_btn)
        root.addWidget(self.table)
        root.addWidget(self.info_label)

    def load_findings(self, findings: list[dict]) -> None:
        rows = [
            (
                item.get("id"),
                item.get("entry_id"),
                item.get("check_name"),
                item.get("severity"),
                item.get("message"),
                item.get("created_at"),
            )
            for item in findings
        ]
        fill_table(self.table, rows)
        self.info_label.setText(f"QA findings: {len(findings)}")
