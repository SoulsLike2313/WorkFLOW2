from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QVBoxLayout, QWidget

from .table_utils import fill_table


class GlossaryPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)

        form = QFormLayout()
        self.source_edit = QLineEdit()
        self.target_edit = QLineEdit()
        self.lang_edit = QLineEdit("any")
        self.add_btn = QPushButton("Add Term")
        form.addRow("Source term:", self.source_edit)
        form.addRow("Target RU:", self.target_edit)
        form.addRow("Source lang:", self.lang_edit)
        form.addRow(self.add_btn)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Source", "Target", "Lang", "Priority", "Updated"])
        self.info_label = QLabel("Glossary terms: 0")

        root.addLayout(form)
        root.addWidget(self.table)
        root.addWidget(self.info_label)

    def load_terms(self, terms: list[dict]) -> None:
        rows = [
            (
                item.get("id"),
                item.get("source_term"),
                item.get("target_term"),
                item.get("source_lang"),
                item.get("priority"),
                item.get("updated_at"),
            )
            for item in terms
        ]
        fill_table(self.table, rows)
        self.info_label.setText(f"Glossary terms: {len(terms)}")
