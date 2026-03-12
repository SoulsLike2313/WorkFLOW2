from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget

from .table_utils import fill_table


class EvidenceReviewPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        self.refresh_btn = QPushButton("Refresh Evidence")
        self.status_label = QLabel("Evidence Review: n/a")

        self.package_table = QTableWidget(0, 6)
        self.package_table.setHorizontalHeaderLabels(["Entry", "Backend", "Fallback", "Confidence", "Quality", "Status"])
        self.evidence_table = QTableWidget(0, 5)
        self.evidence_table.setHorizontalHeaderLabels(["Type", "Ref", "Confidence", "Status", "Created"])
        self.reference_table = QTableWidget(0, 5)
        self.reference_table.setHorizontalHeaderLabels(["Entry", "Provider", "Status", "Confidence", "Created"])

        root.addWidget(self.refresh_btn)
        root.addWidget(self.status_label)
        root.addWidget(QLabel("Translation packages:"))
        root.addWidget(self.package_table)
        root.addWidget(QLabel("Evidence trail:"))
        root.addWidget(self.evidence_table)
        root.addWidget(QLabel("External reference events:"))
        root.addWidget(self.reference_table)

    def load_snapshot(self, snapshot: dict) -> None:
        packages = snapshot.get("translation_packages", []) or []
        evidence = snapshot.get("evidence_records", []) or []
        references = snapshot.get("external_references", []) or []

        fill_table(
            self.package_table,
            [
                (
                    row.get("entry_id"),
                    row.get("backend_name"),
                    "yes" if row.get("fallback_used") else "no",
                    row.get("confidence"),
                    row.get("quality_score"),
                    row.get("status"),
                )
                for row in packages
            ],
        )
        fill_table(
            self.evidence_table,
            [
                (
                    row.get("evidence_type"),
                    row.get("entity_ref"),
                    row.get("confidence"),
                    row.get("status"),
                    row.get("created_at"),
                )
                for row in evidence
            ],
        )
        fill_table(
            self.reference_table,
            [
                (
                    row.get("entry_id"),
                    row.get("provider"),
                    row.get("status"),
                    row.get("confidence"),
                    row.get("created_at"),
                )
                for row in references
            ],
        )

        self.status_label.setText(
            f"Evidence Review: packages={len(packages)} evidence={len(evidence)} refs={len(references)}"
        )

