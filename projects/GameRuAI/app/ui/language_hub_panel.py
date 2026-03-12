from __future__ import annotations

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from .table_utils import fill_table


class LanguageHubPanel(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(8)

        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Language Blocks")
        self.focus_uncertain_btn = QPushButton("Focus Uncertain In Entries")
        self.focus_stress_btn = QPushButton("Focus Stress In Entries")
        self.open_translation_btn = QPushButton("Open Translation Workbench")
        self.status_label = QLabel("Language hub: n/a")
        controls.addWidget(self.refresh_btn)
        controls.addWidget(self.focus_uncertain_btn)
        controls.addWidget(self.focus_stress_btn)
        controls.addWidget(self.open_translation_btn)
        controls.addWidget(self.status_label)
        controls.addStretch(1)
        root.addLayout(controls)

        top_grid = QGridLayout()

        overview_box = QGroupBox("Language Overview")
        overview_layout = QVBoxLayout(overview_box)
        self.overview_table = QTableWidget(0, 6)
        self.overview_table.setHorizontalHeaderLabels(
            ["Language", "Lines", "Avg conf", "Translated", "Needs review", "Coverage"]
        )
        overview_layout.addWidget(self.overview_table)
        top_grid.addWidget(overview_box, 0, 0)

        queue_box = QGroupBox("Language Queue")
        queue_layout = QVBoxLayout(queue_box)
        self.queue_table = QTableWidget(0, 7)
        self.queue_table.setHorizontalHeaderLabels(
            ["Language", "Pending", "Priority", "Status", "Errors", "Last processed", "Next step"]
        )
        queue_layout.addWidget(self.queue_table)
        top_grid.addWidget(queue_box, 0, 1)

        backend_box = QGroupBox("Translation Backend Status")
        backend_layout = QVBoxLayout(backend_box)
        self.backend_labels = [
            QLabel("Active backend: n/a"),
            QLabel("Fallback backend: n/a"),
            QLabel("Backend availability: n/a"),
            QLabel("Avg latency: n/a"),
            QLabel("Context usage: n/a"),
            QLabel("Current mode: n/a"),
        ]
        for label in self.backend_labels:
            backend_layout.addWidget(label)
        top_grid.addWidget(backend_box, 0, 2)

        root.addLayout(top_grid)

        middle_grid = QGridLayout()
        review_box = QGroupBox("Language Review")
        review_layout = QVBoxLayout(review_box)
        self.review_table = QTableWidget(0, 6)
        self.review_table.setHorizontalHeaderLabels(["Entry", "Line", "Lang", "Confidence", "Issue", "File"])
        review_layout.addWidget(self.review_table)
        middle_grid.addWidget(review_box, 0, 0)

        stress_box = QGroupBox("Localization Stress")
        stress_layout = QVBoxLayout(stress_box)
        self.stress_table = QTableWidget(0, 8)
        self.stress_table.setHorizontalHeaderLabels(
            ["Line", "Lang", "Src len", "RU len", "Placeholders", "Tags", "Risk", "File"]
        )
        stress_layout.addWidget(self.stress_table)
        middle_grid.addWidget(stress_box, 0, 1)
        root.addLayout(middle_grid)

        flow_box = QGroupBox("Language Flow Summary")
        flow_layout = QVBoxLayout(flow_box)
        self.flow_table = QTableWidget(0, 4)
        self.flow_table.setHorizontalHeaderLabels(["Stage", "Progress", "Status", "Notes"])
        self.flow_info = QLabel("Flow: n/a")
        flow_layout.addWidget(self.flow_table)
        flow_layout.addWidget(self.flow_info)
        root.addWidget(flow_box)

    def load_snapshot(self, snapshot: dict) -> None:
        if not snapshot:
            fill_table(self.overview_table, [])
            fill_table(self.queue_table, [])
            fill_table(self.review_table, [])
            fill_table(self.stress_table, [])
            fill_table(self.flow_table, [])
            self.status_label.setText("Language hub: no active project")
            self.flow_info.setText("Flow: n/a")
            self.focus_uncertain_btn.setEnabled(False)
            self.focus_stress_btn.setEnabled(False)
            self.open_translation_btn.setEnabled(False)
            for label in self.backend_labels:
                prefix = label.text().split(":", 1)[0]
                label.setText(f"{prefix}: n/a")
            return

        overview_rows = [
            (
                row.get("language"),
                row.get("lines"),
                row.get("avg_confidence"),
                row.get("translated"),
                row.get("needs_review"),
                row.get("coverage"),
            )
            for row in snapshot.get("overview", [])
        ]
        queue_rows = [
            (
                row.get("language"),
                row.get("pending"),
                row.get("priority"),
                row.get("status"),
                row.get("errors"),
                row.get("last_processed"),
                row.get("next_step"),
            )
            for row in snapshot.get("queue", [])
        ]
        review_rows = [
            (
                row.get("entry_id"),
                row.get("line_id"),
                row.get("lang"),
                row.get("confidence"),
                row.get("issue"),
                row.get("file_path"),
            )
            for row in snapshot.get("review", [])
        ]
        stress_rows = [
            (
                row.get("line_id"),
                row.get("lang"),
                row.get("source_len"),
                row.get("translated_len"),
                row.get("placeholders"),
                row.get("tags"),
                row.get("risk"),
                row.get("file_path"),
            )
            for row in snapshot.get("stress", [])
        ]
        flow_rows = [
            (row.get("stage"), row.get("progress"), row.get("status"), row.get("notes"))
            for row in snapshot.get("flow_summary", [])
        ]

        fill_table(self.overview_table, overview_rows)
        fill_table(self.queue_table, queue_rows)
        fill_table(self.review_table, review_rows)
        fill_table(self.stress_table, stress_rows)
        fill_table(self.flow_table, flow_rows)

        backend = snapshot.get("backend_status", {}) or {}
        self.backend_labels[0].setText(f"Active backend: {backend.get('active_backend', 'n/a')}")
        self.backend_labels[1].setText(f"Fallback backend: {backend.get('fallback_backend', '-')}")
        self.backend_labels[2].setText(
            "Backend availability: " + ", ".join(backend.get("available_backends", []) or ["n/a"])
        )
        self.backend_labels[3].setText(
            f"Avg latency: {backend.get('avg_latency_ms', 0)} ms (p95={backend.get('p95_latency_ms', 0)} ms)"
        )
        self.backend_labels[4].setText(
            f"Context usage: {backend.get('context_usage_rate', 0)} | fallback used={backend.get('fallback_used', 0)}"
        )
        self.backend_labels[5].setText(f"Current mode: {backend.get('mode', 'n/a')}")

        self.status_label.setText(
            "Language hub: "
            f"languages={snapshot.get('languages_total', 0)} "
            f"uncertain={snapshot.get('uncertain_total', 0)} "
            f"review={len(review_rows)}"
        )
        self.flow_info.setText(
            "Flow: "
            f"detected={snapshot.get('detected_total', 0)} "
            f"translated={snapshot.get('translated_total', 0)} "
            f"reviewed={snapshot.get('reviewed_total', 0)} "
            f"exported_jobs={snapshot.get('exported_total', 0)}"
        )
        self.focus_uncertain_btn.setEnabled(bool(review_rows))
        self.focus_stress_btn.setEnabled(bool(stress_rows))
        self.open_translation_btn.setEnabled(bool(snapshot.get("translated_total", 0) or snapshot.get("detected_total", 0)))
