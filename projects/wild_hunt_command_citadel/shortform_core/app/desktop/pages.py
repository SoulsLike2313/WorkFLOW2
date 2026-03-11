from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .components import EmptyStateCard, GlowCard, MetricCard, SectionHeader


def _fmt_ts(value: Any) -> str:
    if not value:
        return "-"
    text = str(value)
    if "T" in text:
        return text.replace("T", " ")[:19]
    return text[:19]


def _fmt_num(value: Any) -> str:
    try:
        return f"{float(value):,.0f}".replace(",", " ")
    except Exception:
        return "0"


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


class BasePage(QWidget):
    action_requested = Signal(str, object)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        raise NotImplementedError


class DashboardPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DashboardPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Dashboard", "Workspace overview and fast actions"))

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(10)
        metrics_grid.setVerticalSpacing(10)

        self.cards = {
            "profiles": MetricCard("Active Profiles", "0", "registered"),
            "sessions": MetricCard("Connected Sessions", "0", "open windows"),
            "queue": MetricCard("Queue State", "0", "items waiting"),
            "verify": MetricCard("Verification", "--", "gate status"),
            "ai": MetricCard("AI State", "--", "runtime readiness"),
            "updates": MetricCard("Update State", "--", "post-verify"),
        }

        order = ["profiles", "sessions", "queue", "verify", "ai", "updates"]
        for idx, key in enumerate(order):
            row = idx // 3
            col = idx % 3
            metrics_grid.addWidget(self.cards[key], row, col)

        layout.addLayout(metrics_grid)

        quick_card = GlowCard(elevated=False)
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(12, 10, 12, 10)
        quick_layout.setSpacing(8)
        quick_layout.addWidget(SectionHeader("Quick Actions", "Primary product flow shortcuts"))

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        actions = [
            ("Add Profile", "add_profile"),
            ("Open Session", "open_session"),
            ("Import Metrics", "import_metrics"),
            ("Generate Content Plan", "generate_plan"),
            ("Open AI Studio", "open_ai_studio"),
            ("Check Updates", "check_updates"),
        ]
        for idx, (title, action) in enumerate(actions):
            button = QPushButton(title)
            if action in {"add_profile", "open_session", "generate_plan"}:
                button.setObjectName("PrimaryCTA")
            button.clicked.connect(lambda _=False, a=action: self.action_requested.emit(a, None))
            (row1 if idx < 3 else row2).addWidget(button)

        quick_layout.addLayout(row1)
        quick_layout.addLayout(row2)
        layout.addWidget(quick_card)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)

        audit_card = GlowCard(elevated=False)
        audit_layout = QVBoxLayout(audit_card)
        audit_layout.setContentsMargins(12, 10, 12, 10)
        audit_layout.setSpacing(8)
        audit_layout.addWidget(SectionHeader("Recent Audit Events", "Latest workspace timeline"))
        self.audit_list = QListWidget()
        audit_layout.addWidget(self.audit_list)

        rec_card = GlowCard(elevated=False)
        rec_layout = QVBoxLayout(rec_card)
        rec_layout.setContentsMargins(12, 10, 12, 10)
        rec_layout.setSpacing(8)
        rec_layout.addWidget(SectionHeader("AI Recommendations Summary", "Top suggestions by priority"))
        self.rec_list = QListWidget()
        rec_layout.addWidget(self.rec_list)

        split.addWidget(audit_card)
        split.addWidget(rec_card)
        split.setSizes([520, 520])
        layout.addWidget(split, stretch=1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        summary = snapshot.get("workspace_summary", {})
        readiness = snapshot.get("workspace_readiness", {})
        updates = snapshot.get("updates", {})

        self.cards["profiles"].set_data(str(summary.get("active_profiles", 0)), f"{summary.get('profile_count', 0)} total")
        self.cards["sessions"].set_data(str(summary.get("open_session_windows", 0)), "9:16 session windows")
        self.cards["queue"].set_data(str(summary.get("queued_content_items", 0)), "content items")

        verify = str(snapshot.get("verification_state", "--"))
        self.cards["verify"].set_data(verify, "PASS required for manual test")

        ai_ready = readiness.get("items", {}).get("ai_ready", False) if isinstance(readiness.get("items"), dict) else False
        self.cards["ai"].set_data("ready" if ai_ready else "degraded", "assistive intelligence")

        post_status = str(updates.get("post_verify_status", "unknown"))
        self.cards["updates"].set_data(post_status, str(updates.get("version_label", "version unknown")))

        self.audit_list.clear()
        for item in _safe_list(snapshot.get("audit_log"))[:16]:
            self.audit_list.addItem(f"{_fmt_ts(item.get('created_at'))} | {item.get('action_type', '-') } | {item.get('result', '-')}")
        if self.audit_list.count() == 0:
            self.audit_list.addItem("No audit events yet.")

        self.rec_list.clear()
        recs = _safe_list(snapshot.get("analytics_recommendations"))
        ai_recs = _safe_list(snapshot.get("ai_recommendations"))
        merged = recs[:6] + ai_recs[:6]
        for item in merged[:10]:
            title = str(item.get("title", item.get("recommendation_type", "Recommendation")))
            rationale = str(item.get("rationale", "No rationale"))
            confidence = item.get("confidence", "-")
            self.rec_list.addItem(f"{title} | confidence={confidence}\n{rationale}")
        if self.rec_list.count() == 0:
            self.rec_list.addItem("Recommendations will appear after profile metrics are available.")


class ProfilesPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ProfilesPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Profiles", "Connection types, modes, health and quick actions"))

        action_row = QHBoxLayout()
        for title, action, primary in [
            ("Create Profile", "add_profile", True),
            ("Connect Profile", "connect_profile", False),
            ("Open Session", "open_session", True),
            ("View Metrics", "open_analytics", False),
            ("Open Content", "open_content", False),
            ("Open AI", "open_ai_studio", False),
        ]:
            btn = QPushButton(title)
            if primary:
                btn.setObjectName("PrimaryCTA")
            btn.clicked.connect(lambda _=False, a=action: self.action_requested.emit(a, self.selected_profile_id()))
            action_row.addWidget(btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Profile", "Platform", "Connection", "Mode", "Status", "Health", "Updated"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._emit_profile_selected)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(132)
        layout.addWidget(self.table, stretch=1)

    def selected_profile_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _emit_profile_selected(self) -> None:
        profile_id = self.selected_profile_id()
        if profile_id:
            self.action_requested.emit("select_profile", profile_id)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        items = _safe_list(snapshot.get("profiles"))
        selected = snapshot.get("selected_profile_id")

        self.table.setRowCount(0)
        for row, profile in enumerate(items):
            self.table.insertRow(row)
            name_item = QTableWidgetItem(str(profile.get("display_name", "Unknown")))
            name_item.setData(Qt.ItemDataRole.UserRole, profile.get("id"))

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(str(profile.get("platform", "-"))))
            self.table.setItem(row, 2, QTableWidgetItem(str(profile.get("connection_type", "-"))))
            self.table.setItem(row, 3, QTableWidgetItem(str(profile.get("management_mode", "-"))))
            self.table.setItem(row, 4, QTableWidgetItem(str(profile.get("status", "-"))))
            self.table.setItem(row, 5, QTableWidgetItem(str(profile.get("health_state", "-"))))
            self.table.setItem(row, 6, QTableWidgetItem(_fmt_ts(profile.get("updated_at"))))

            if selected and profile.get("id") == selected:
                self.table.selectRow(row)

class SessionsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SessionsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Sessions", "Premium 9:16 frame with runtime controls and health"))

        controls = QHBoxLayout()
        self.viewport = QComboBox()
        self.viewport.addItems(["smartphone_default", "android_tall", "iphone_like", "custom"])
        controls.addWidget(QLabel("Viewport:"))
        controls.addWidget(self.viewport)

        open_btn = QPushButton("Open Session")
        open_btn.setObjectName("PrimaryCTA")
        open_btn.clicked.connect(lambda: self.action_requested.emit("open_session", self._payload()))
        close_btn = QPushButton("Close Session")
        close_btn.setObjectName("DangerCTA")
        close_btn.clicked.connect(lambda: self.action_requested.emit("close_session", self._payload()))

        controls.addWidget(open_btn)
        controls.addWidget(close_btn)
        controls.addStretch(1)
        layout.addLayout(controls)

        body = QHBoxLayout()

        left_card = GlowCard(elevated=False)
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)
        left_layout.addWidget(SectionHeader("Session Registry", "Per-profile runtime state"))
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self._session_clicked)
        left_layout.addWidget(self.session_list)
        body.addWidget(left_card, stretch=2)

        right_card = GlowCard(elevated=False)
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(10)

        self.session_frame = GlowCard(elevated=True)
        self.session_frame.setObjectName("SessionFrame")
        frame_layout = QVBoxLayout(self.session_frame)
        frame_layout.setContentsMargins(14, 16, 14, 16)
        frame_layout.setSpacing(8)

        self.frame_title = QLabel("9:16 Session Window")
        self.frame_title.setObjectName("SectionTitle")
        frame_layout.addWidget(self.frame_title)

        self.frame_runtime = QLabel("No active session")
        self.frame_runtime.setObjectName("SectionHint")
        self.frame_runtime.setWordWrap(True)
        frame_layout.addWidget(self.frame_runtime)

        self.frame_source = QLabel("source: not attached")
        self.frame_source.setObjectName("SectionHint")
        frame_layout.addWidget(self.frame_source)

        dummy_phone = QLabel("Mobile viewport canvas\n(9:16 preview frame)")
        dummy_phone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dummy_phone.setMinimumSize(280, 500)
        dummy_phone.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(16,26,42,0.92), stop:1 rgba(12,20,33,0.92)); "
            "border: 1px solid rgba(192,167,255,0.55); "
            "border-radius: 24px; font-size: 14px; color: #C8D1EA;"
        )
        frame_layout.addWidget(dummy_phone)

        right_layout.addWidget(self.session_frame)
        body.addWidget(right_card, stretch=3)

        layout.addLayout(body, stretch=1)

    def _payload(self) -> dict[str, Any]:
        return {
            "profile_id": self.property("selected_profile_id"),
            "viewport_preset": self.viewport.currentText(),
        }

    def _session_clicked(self, item: QListWidgetItem) -> None:
        profile_id = item.data(Qt.ItemDataRole.UserRole)
        if profile_id:
            self.setProperty("selected_profile_id", profile_id)
            self.action_requested.emit("select_profile", profile_id)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        self.session_list.clear()

        selected_profile_id = snapshot.get("selected_profile_id")
        sessions_by_profile = snapshot.get("sessions_by_profile", {})
        profiles = _safe_list(snapshot.get("profiles"))

        for profile in profiles:
            profile_id = profile.get("id")
            session = sessions_by_profile.get(profile_id) or {}
            line = (
                f"{profile.get('display_name', 'Unknown')} | "
                f"state={session.get('runtime_state', 'closed')} | "
                f"open={session.get('is_open', False)}"
            )
            item = QListWidgetItem(line)
            item.setData(Qt.ItemDataRole.UserRole, profile_id)
            self.session_list.addItem(item)
            if profile_id == selected_profile_id:
                self.session_list.setCurrentItem(item)

        selected_session = snapshot.get("selected_session") or {}
        profile_name = snapshot.get("selected_profile_name", "No profile selected")
        self.frame_title.setText(f"9:16 Session | {profile_name}")
        self.frame_runtime.setText(
            f"runtime={selected_session.get('runtime_state', 'closed')} | "
            f"is_open={selected_session.get('is_open', False)} | "
            f"preset={selected_session.get('viewport_preset', '-') }"
        )
        self.frame_source.setText(
            f"source={selected_session.get('attached_source_type', 'none')} "
            f"id={selected_session.get('attached_source_id', '-') }"
        )


class ContentPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ContentPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(SectionHeader("Content Desk", "Library, queue, validation and publish readiness"))

        summary = QHBoxLayout()
        self.card_total = MetricCard("Library", "0", "items")
        self.card_queue = MetricCard("Queued", "0", "ready to post")
        self.card_ready = MetricCard("Ready", "0", "validated")
        self.card_invalid = MetricCard("Warnings/Invalid", "0", "manual review")
        summary.addWidget(self.card_total)
        summary.addWidget(self.card_queue)
        summary.addWidget(self.card_ready)
        summary.addWidget(self.card_invalid)
        layout.addLayout(summary)

        actions = QHBoxLayout()
        add_btn = QPushButton("Add Placeholder Content")
        add_btn.setObjectName("PrimaryCTA")
        add_btn.clicked.connect(lambda: self.action_requested.emit("add_placeholder_content", None))
        validate_btn = QPushButton("Validate Selected")
        validate_btn.clicked.connect(lambda: self.action_requested.emit("validate_content", self.selected_content_id()))
        queue_btn = QPushButton("Queue Selected")
        queue_btn.clicked.connect(lambda: self.action_requested.emit("queue_content", self.selected_content_id()))
        actions.addWidget(add_btn)
        actions.addWidget(validate_btn)
        actions.addWidget(queue_btn)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Status", "Validation", "Duration", "Topic", "Updated"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(140)
        layout.addWidget(self.table, stretch=1)

    def selected_content_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.text() if item else None

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        items = _safe_list(snapshot.get("content_items"))
        self.table.setRowCount(0)

        queued = 0
        ready = 0
        invalid = 0
        for row, item in enumerate(items):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get("id", "-"))))
            self.table.setItem(row, 1, QTableWidgetItem(str(item.get("title", "untitled"))))
            status = str(item.get("status", "draft"))
            validation = str(item.get("validation_state", "pending"))
            self.table.setItem(row, 2, QTableWidgetItem(status))
            self.table.setItem(row, 3, QTableWidgetItem(validation))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.get("duration", "-"))))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.get("topic_label", "-"))))
            self.table.setItem(row, 6, QTableWidgetItem(_fmt_ts(item.get("updated_at"))))

            if status == "queued":
                queued += 1
            if status == "ready":
                ready += 1
            if validation in {"warning", "invalid"}:
                invalid += 1

        self.card_total.set_data(str(len(items)), "content library")
        self.card_queue.set_data(str(queued), "queue status")
        self.card_ready.set_data(str(ready), "ready to publish")
        self.card_invalid.set_data(str(invalid), "needs review")

class AnalyticsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AnalyticsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(SectionHeader("Analytics", "Performance, top content, weak signals and action plan"))

        row = QHBoxLayout()
        self.views_card = MetricCard("Views Window", "0", "profile performance")
        self.engagement_card = MetricCard("Engagement", "0", "total engagement window")
        self.momentum_card = MetricCard("Momentum", "0", "profile momentum score")
        self.top_card = MetricCard("Top Content", "0", "ranked by weighted score")
        row.addWidget(self.views_card)
        row.addWidget(self.engagement_card)
        row.addWidget(self.momentum_card)
        row.addWidget(self.top_card)
        layout.addLayout(row)

        split = QSplitter(Qt.Orientation.Horizontal)

        left = GlowCard(elevated=False)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 10, 12, 10)
        left_layout.setSpacing(8)
        left_layout.addWidget(SectionHeader("Top Content", "Best performers and outliers"))
        self.top_list = QListWidget()
        left_layout.addWidget(self.top_list)

        weak_header = SectionHeader("Weak Content Signals", "Likely causes and stop-testing candidates")
        left_layout.addWidget(weak_header)
        self.weak_list = QListWidget()
        left_layout.addWidget(self.weak_list)

        right = GlowCard(elevated=False)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.setSpacing(8)
        right_layout.addWidget(SectionHeader("Content Patterns", "Topic, format, hooks, posting windows"))
        self.patterns_list = QListWidget()
        right_layout.addWidget(self.patterns_list)

        right_layout.addWidget(SectionHeader("Action Plan Summary", "Repeat, test, stop, and next rollout"))
        self.plan_text = QTextEdit()
        self.plan_text.setReadOnly(True)
        right_layout.addWidget(self.plan_text)

        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([500, 540])
        layout.addWidget(split, stretch=1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        perf = snapshot.get("analytics_performance", {}) or {}
        self.views_card.set_data(_fmt_num(perf.get("total_views_window", 0)), perf.get("snapshot_window", "window"))
        self.engagement_card.set_data(f"{float(perf.get('total_engagement_window', 0.0)):.2f}", "engagement window")
        self.momentum_card.set_data(f"{float(perf.get('momentum_score', 0.0)):.2f}", "momentum score")

        top = _safe_list(snapshot.get("analytics_top_content"))
        self.top_card.set_data(str(len(top)), "top entries")

        self.top_list.clear()
        for item in top[:10]:
            self.top_list.addItem(
                f"{item.get('content_id', '-') } | score={float(item.get('weighted_engagement_score', 0.0)):.2f} "
                f"| views={item.get('views', 0)}"
            )
        if self.top_list.count() == 0:
            self.top_list.addItem("No top-content data yet.")

        weak_items = []
        for item in top:
            if float(item.get("weighted_engagement_score", 0.0)) < 0.15:
                weak_items.append(item)

        self.weak_list.clear()
        for item in weak_items[:10]:
            self.weak_list.addItem(
                f"{item.get('content_id', '-') } | weak score={float(item.get('weighted_engagement_score', 0.0)):.2f}"
            )
        if self.weak_list.count() == 0:
            self.weak_list.addItem("Weak content set is empty for current profile window.")

        patterns = _safe_list(snapshot.get("analytics_patterns"))
        self.patterns_list.clear()
        for pattern in patterns[:12]:
            self.patterns_list.addItem(
                f"{pattern.get('pattern_type', '-') } | {pattern.get('label', '-') } "
                f"| confidence={float(pattern.get('confidence', 0.0)):.2f}"
            )
        if self.patterns_list.count() == 0:
            self.patterns_list.addItem("Pattern extraction has not produced entries yet.")

        plan = snapshot.get("analytics_action_plan")
        if isinstance(plan, dict):
            lines = [
                f"Performance: {plan.get('performance_summary', '-')}",
                "",
                "What worked:",
            ]
            lines.extend([f"- {item}" for item in _safe_list(plan.get("top_content_findings"))])
            lines.append("")
            lines.append("What did not work:")
            lines.extend([f"- {item}" for item in _safe_list(plan.get("weak_content_findings"))])
            lines.append("")
            lines.append("Next actions:")
            lines.extend([f"- {item}" for item in _safe_list(plan.get("next_actions"))])
            self.plan_text.setPlainText("\n".join(lines).strip())
        else:
            self.plan_text.setPlainText("Action plan not generated yet. Use 'Generate Content Plan' quick action.")


class AIStudioPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AIStudioPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("AI Studio", "Perception, recommendations, learning and creative briefing"))

        cards = QHBoxLayout()
        self.rec_count_card = MetricCard("Recommendations", "0", "active list")
        self.learning_card = MetricCard("Learning Records", "0", "feedback loop")
        self.bundle_card = MetricCard("Generation Bundles", "0", "brief pipeline")
        self.confidence_card = MetricCard("Confidence Avg", "0.00", "recommendation confidence")
        cards.addWidget(self.rec_count_card)
        cards.addWidget(self.learning_card)
        cards.addWidget(self.bundle_card)
        cards.addWidget(self.confidence_card)
        layout.addLayout(cards)

        action_row = QHBoxLayout()
        gen_btn = QPushButton("Generate Recommendations")
        gen_btn.setObjectName("PrimaryCTA")
        gen_btn.clicked.connect(lambda: self.action_requested.emit("generate_ai_recommendations", None))
        bundle_btn = QPushButton("Build Generation Bundle")
        bundle_btn.clicked.connect(lambda: self.action_requested.emit("build_generation_bundle", None))
        action_row.addWidget(gen_btn)
        action_row.addWidget(bundle_btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        split = QSplitter(Qt.Orientation.Horizontal)

        left = GlowCard(elevated=False)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 10, 12, 10)
        left_layout.setSpacing(8)
        left_layout.addWidget(SectionHeader("Recommendations", "Rationale, confidence, alternatives"))
        self.recommendations = QListWidget()
        left_layout.addWidget(self.recommendations)

        right = GlowCard(elevated=False)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.setSpacing(8)
        right_layout.addWidget(SectionHeader("Learning Summary", "What the system learned from outcomes"))
        self.learning_summary = QTextEdit()
        self.learning_summary.setReadOnly(True)
        right_layout.addWidget(self.learning_summary)

        right_layout.addWidget(SectionHeader("Generation Bundle Preview", "Video/audio/script/text preparation"))
        self.bundle_list = QListWidget()
        right_layout.addWidget(self.bundle_list)

        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([500, 560])
        layout.addWidget(split, stretch=1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        recs = _safe_list(snapshot.get("ai_recommendations"))
        learn = snapshot.get("ai_learning_summary")
        bundles = _safe_list(snapshot.get("generation_bundles"))

        conf_values = [float(item.get("confidence", 0.0)) for item in recs if item.get("confidence") is not None]
        conf_avg = sum(conf_values) / len(conf_values) if conf_values else 0.0

        self.rec_count_card.set_data(str(len(recs)), "ranked items")
        learning_count = 0
        if isinstance(learn, dict):
            learning_count = int(learn.get("record_count", 0))
        self.learning_card.set_data(str(learning_count), "recorded outcomes")
        self.bundle_card.set_data(str(len(bundles)), "stored bundles")
        self.confidence_card.set_data(f"{conf_avg:.2f}", "mean confidence")

        self.recommendations.clear()
        for item in recs[:16]:
            self.recommendations.addItem(
                f"{item.get('title', item.get('recommendation_type', 'Recommendation'))} | "
                f"priority={item.get('priority', '-') } | confidence={float(item.get('confidence', 0.0)):.2f}\n"
                f"{item.get('rationale', 'No rationale') }"
            )
        if self.recommendations.count() == 0:
            self.recommendations.addItem("No AI recommendations yet. Generate recommendations for selected profile.")

        if isinstance(learn, dict):
            lines = [
                f"Profile: {learn.get('profile_id', '-')}",
                f"Record count: {learn.get('record_count', 0)}",
                "",
                "Outcome labels:",
            ]
            for key, value in dict(learn.get("outcome_breakdown", {})).items():
                lines.append(f"- {key}: {value}")
            lines.append("")
            lines.append("Top learnings:")
            for item in _safe_list(learn.get("recent_highlights"))[:8]:
                lines.append(f"- {item}")
            self.learning_summary.setPlainText("\n".join(lines))
        else:
            self.learning_summary.setPlainText("Learning summary unavailable for selected profile.")

        self.bundle_list.clear()
        for bundle in bundles[:12]:
            self.bundle_list.addItem(
                f"{bundle.get('id', '-') } | goal={bundle.get('content_goal', '-') } | "
                f"ready={bundle.get('generation_ready_flag', False)}"
            )
        if self.bundle_list.count() == 0:
            self.bundle_list.addItem("No generation bundles yet.")
