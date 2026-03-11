from __future__ import annotations

from typing import Iterable

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


def fill_table(table: QTableWidget, rows: list[Iterable[object]]) -> None:
    table.setRowCount(0)
    for r_idx, row in enumerate(rows):
        table.insertRow(r_idx)
        for c_idx, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            table.setItem(r_idx, c_idx, item)
    table.resizeColumnsToContents()
