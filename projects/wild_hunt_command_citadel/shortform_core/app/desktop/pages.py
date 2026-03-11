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


def _ru_gate(value: str) -> str:
    mapping = {
        "PASS": "PASS",
        "PASS_WITH_WARNINGS": "PASS с предупреждениями",
        "FAIL": "FAIL",
        "UNKNOWN": "неизвестно",
        "unknown": "неизвестно",
    }
    return mapping.get(value, value)


def _ru_runtime_state(value: str) -> str:
    mapping = {
        "ready": "готово",
        "degraded": "ограничено",
        "open": "открыта",
        "closed": "закрыта",
        "active": "активна",
        "idle": "ожидание",
        "running": "в работе",
        "error": "ошибка",
    }
    return mapping.get(value, value)


def _ru_content_status(value: str) -> str:
    mapping = {
        "draft": "черновик",
        "ready": "готово",
        "queued": "в очереди",
        "posted": "опубликовано",
        "failed": "ошибка",
    }
    return mapping.get(value, value)


def _ru_validation_state(value: str) -> str:
    mapping = {
        "pending": "ожидает",
        "valid": "валидно",
        "warning": "предупреждение",
        "invalid": "невалидно",
    }
    return mapping.get(value, value)


def _ru_viewport_preset(value: str) -> str:
    mapping = {
        "smartphone_default": "Смартфон (по умолчанию)",
        "android_tall": "Android (высокий)",
        "iphone_like": "iPhone-стиль",
        "custom": "Пользовательский",
    }
    return mapping.get(value, value)


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

        layout.addWidget(SectionHeader("Обзор", "Сводка рабочего пространства и быстрые действия"))

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(10)
        metrics_grid.setVerticalSpacing(10)

        self.cards = {
            "profiles": MetricCard("Активные профили", "0", "зарегистрировано"),
            "sessions": MetricCard("Подключённые сессии", "0", "открытые окна"),
            "queue": MetricCard("Состояние очереди", "0", "элементов в ожидании"),
            "verify": MetricCard("Верификация", "--", "статус гейта"),
            "ai": MetricCard("Состояние AI", "--", "готовность модулей"),
            "updates": MetricCard("Состояние обновлений", "--", "post-verify"),
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
        quick_layout.addWidget(SectionHeader("Быстрые действия", "Ключевые шаги рабочего сценария"))

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        actions = [
            ("Добавить профиль", "add_profile"),
            ("Открыть сессию", "open_session"),
            ("Загрузить метрики", "import_metrics"),
            ("Сформировать контент-план", "generate_plan"),
            ("Открыть AI-студию", "open_ai_studio"),
            ("Проверить обновления", "check_updates"),
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
        audit_layout.addWidget(SectionHeader("Последние события журнала", "Актуальная лента действий"))
        self.audit_list = QListWidget()
        audit_layout.addWidget(self.audit_list)

        rec_card = GlowCard(elevated=False)
        rec_layout = QVBoxLayout(rec_card)
        rec_layout.setContentsMargins(12, 10, 12, 10)
        rec_layout.setSpacing(8)
        rec_layout.addWidget(SectionHeader("Сводка рекомендаций AI", "Приоритетные предложения"))
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

        self.cards["profiles"].set_data(str(summary.get("active_profiles", 0)), f"{summary.get('profile_count', 0)} всего")
        self.cards["sessions"].set_data(str(summary.get("open_session_windows", 0)), "окна формата 9:16")
        self.cards["queue"].set_data(str(summary.get("queued_content_items", 0)), "контент-элементов")

        verify = str(snapshot.get("verification_state", "--"))
        self.cards["verify"].set_data(_ru_gate(verify), "ручной тест только при PASS")

        ai_ready = readiness.get("items", {}).get("ai_ready", False) if isinstance(readiness.get("items"), dict) else False
        self.cards["ai"].set_data("готово" if ai_ready else "ограничено", "ассистивный интеллект")

        post_status = str(updates.get("post_verify_status", "unknown"))
        self.cards["updates"].set_data(_ru_gate(post_status), str(updates.get("version_label", "версия не определена")))

        self.audit_list.clear()
        for item in _safe_list(snapshot.get("audit_log"))[:16]:
            self.audit_list.addItem(f"{_fmt_ts(item.get('created_at'))} | {item.get('action_type', '-') } | {item.get('result', '-')}")
        if self.audit_list.count() == 0:
            self.audit_list.addItem("Событий в журнале пока нет.")

        self.rec_list.clear()
        recs = _safe_list(snapshot.get("analytics_recommendations"))
        ai_recs = _safe_list(snapshot.get("ai_recommendations"))
        merged = recs[:6] + ai_recs[:6]
        for item in merged[:10]:
            title = str(item.get("title", item.get("recommendation_type", "Рекомендация")))
            rationale = str(item.get("rationale", "Обоснование не указано"))
            confidence = item.get("confidence", "-")
            self.rec_list.addItem(f"{title} | уверенность={confidence}\n{rationale}")
        if self.rec_list.count() == 0:
            self.rec_list.addItem("Рекомендации появятся после загрузки метрик профиля.")


class ProfilesPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ProfilesPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("Профили", "Тип подключения, режим управления, состояние и быстрые действия"))

        action_row = QHBoxLayout()
        for title, action, primary in [
            ("Создать профиль", "add_profile", True),
            ("Подключить профиль", "connect_profile", False),
            ("Открыть сессию", "open_session", True),
            ("Открыть аналитику", "open_analytics", False),
            ("Открыть контент", "open_content", False),
            ("Открыть AI", "open_ai_studio", False),
        ]:
            btn = QPushButton(title)
            if primary:
                btn.setObjectName("PrimaryCTA")
            btn.clicked.connect(lambda _=False, a=action: self.action_requested.emit(a, self.selected_profile_id()))
            action_row.addWidget(btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Профиль", "Платформа", "Подключение", "Режим", "Статус", "Состояние", "Обновлено"])
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
            name_item = QTableWidgetItem(str(profile.get("display_name", "Без имени")))
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

        layout.addWidget(SectionHeader("Сессии", "Премиальное окно 9:16 с управлением и статусом"))

        controls = QHBoxLayout()
        self.viewport = QComboBox()
        self.viewport.addItem("Смартфон (по умолчанию)", "smartphone_default")
        self.viewport.addItem("Android (высокий)", "android_tall")
        self.viewport.addItem("iPhone-стиль", "iphone_like")
        self.viewport.addItem("Пользовательский", "custom")
        controls.addWidget(QLabel("Пресет окна:"))
        controls.addWidget(self.viewport)

        open_btn = QPushButton("Открыть сессию")
        open_btn.setObjectName("PrimaryCTA")
        open_btn.clicked.connect(lambda: self.action_requested.emit("open_session", self._payload()))
        close_btn = QPushButton("Закрыть сессию")
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
        left_layout.addWidget(SectionHeader("Реестр сессий", "Состояние выполнения по каждому профилю"))
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

        self.frame_title = QLabel("Окно сессии 9:16")
        self.frame_title.setObjectName("SectionTitle")
        frame_layout.addWidget(self.frame_title)

        self.frame_runtime = QLabel("Активной сессии нет")
        self.frame_runtime.setObjectName("SectionHint")
        self.frame_runtime.setWordWrap(True)
        frame_layout.addWidget(self.frame_runtime)

        self.frame_source = QLabel("источник: не привязан")
        self.frame_source.setObjectName("SectionHint")
        frame_layout.addWidget(self.frame_source)

        dummy_phone = QLabel("Холст мобильной сессии\n(превью 9:16)")
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
            "viewport_preset": self.viewport.currentData() or self.viewport.currentText(),
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
                f"{profile.get('display_name', 'Без имени')} | "
                f"состояние={_ru_runtime_state(str(session.get('runtime_state', 'closed')))} | "
                f"открыта={'да' if session.get('is_open', False) else 'нет'}"
            )
            item = QListWidgetItem(line)
            item.setData(Qt.ItemDataRole.UserRole, profile_id)
            self.session_list.addItem(item)
            if profile_id == selected_profile_id:
                self.session_list.setCurrentItem(item)

        selected_session = snapshot.get("selected_session") or {}
        profile_name = snapshot.get("selected_profile_name", "Профиль не выбран")
        self.frame_title.setText(f"Сессия 9:16 | {profile_name}")
        self.frame_runtime.setText(
            f"состояние={_ru_runtime_state(str(selected_session.get('runtime_state', 'closed')))} | "
            f"открыта={'да' if selected_session.get('is_open', False) else 'нет'} | "
            f"пресет={_ru_viewport_preset(str(selected_session.get('viewport_preset', '-')))}"
        )
        self.frame_source.setText(
            f"источник={selected_session.get('attached_source_type', 'none')} "
            f"id={selected_session.get('attached_source_id', '-') }"
        )


class ContentPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ContentPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(SectionHeader("Контент", "Библиотека, очередь, валидация и готовность к публикации"))

        summary = QHBoxLayout()
        self.card_total = MetricCard("Библиотека", "0", "элементов")
        self.card_queue = MetricCard("В очереди", "0", "готово к постингу")
        self.card_ready = MetricCard("Готово", "0", "прошло валидацию")
        self.card_invalid = MetricCard("Предупр./ошибки", "0", "требует проверки")
        summary.addWidget(self.card_total)
        summary.addWidget(self.card_queue)
        summary.addWidget(self.card_ready)
        summary.addWidget(self.card_invalid)
        layout.addLayout(summary)

        actions = QHBoxLayout()
        add_btn = QPushButton("Добавить демо-контент")
        add_btn.setObjectName("PrimaryCTA")
        add_btn.clicked.connect(lambda: self.action_requested.emit("add_placeholder_content", None))
        validate_btn = QPushButton("Проверить выбранное")
        validate_btn.clicked.connect(lambda: self.action_requested.emit("validate_content", self.selected_content_id()))
        queue_btn = QPushButton("Поставить в очередь")
        queue_btn.clicked.connect(lambda: self.action_requested.emit("queue_content", self.selected_content_id()))
        actions.addWidget(add_btn)
        actions.addWidget(validate_btn)
        actions.addWidget(queue_btn)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Статус", "Валидация", "Длительность", "Тема", "Обновлено"])
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
            self.table.setItem(row, 1, QTableWidgetItem(str(item.get("title", "без названия"))))
            status = str(item.get("status", "draft"))
            validation = str(item.get("validation_state", "pending"))
            self.table.setItem(row, 2, QTableWidgetItem(_ru_content_status(status)))
            self.table.setItem(row, 3, QTableWidgetItem(_ru_validation_state(validation)))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.get("duration", "-"))))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.get("topic_label", "-"))))
            self.table.setItem(row, 6, QTableWidgetItem(_fmt_ts(item.get("updated_at"))))

            if status == "queued":
                queued += 1
            if status == "ready":
                ready += 1
            if validation in {"warning", "invalid"}:
                invalid += 1

        self.card_total.set_data(str(len(items)), "контент-библиотека")
        self.card_queue.set_data(str(queued), "состояние очереди")
        self.card_ready.set_data(str(ready), "можно публиковать")
        self.card_invalid.set_data(str(invalid), "нужна ручная проверка")

class AnalyticsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AnalyticsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(SectionHeader("Аналитика", "Результативность, топ-контент, слабые сигналы и план действий"))

        row = QHBoxLayout()
        self.views_card = MetricCard("Окно просмотров", "0", "результат профиля")
        self.engagement_card = MetricCard("Вовлечённость", "0", "суммарно за окно")
        self.momentum_card = MetricCard("Моментум", "0", "оценка динамики")
        self.top_card = MetricCard("Топ-контент", "0", "ранжирование по весам")
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
        left_layout.addWidget(SectionHeader("Топ-контент", "Лучшие ролики и выбросы"))
        self.top_list = QListWidget()
        left_layout.addWidget(self.top_list)

        weak_header = SectionHeader("Слабые сигналы", "Вероятные причины и кандидаты на остановку")
        left_layout.addWidget(weak_header)
        self.weak_list = QListWidget()
        left_layout.addWidget(self.weak_list)

        right = GlowCard(elevated=False)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.setSpacing(8)
        right_layout.addWidget(SectionHeader("Паттерны контента", "Темы, форматы, хуки и окна публикации"))
        self.patterns_list = QListWidget()
        right_layout.addWidget(self.patterns_list)

        right_layout.addWidget(SectionHeader("Сводка плана действий", "Что повторить, протестировать и остановить"))
        self.plan_text = QTextEdit()
        self.plan_text.setReadOnly(True)
        right_layout.addWidget(self.plan_text)

        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([500, 540])
        layout.addWidget(split, stretch=1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        perf = snapshot.get("analytics_performance", {}) or {}
        self.views_card.set_data(_fmt_num(perf.get("total_views_window", 0)), perf.get("snapshot_window", "период"))
        self.engagement_card.set_data(f"{float(perf.get('total_engagement_window', 0.0)):.2f}", "вовлечённость за период")
        self.momentum_card.set_data(f"{float(perf.get('momentum_score', 0.0)):.2f}", "оценка динамики")

        top = _safe_list(snapshot.get("analytics_top_content"))
        self.top_card.set_data(str(len(top)), "позиций")

        self.top_list.clear()
        for item in top[:10]:
            self.top_list.addItem(
                f"{item.get('content_id', '-') } | оценка={float(item.get('weighted_engagement_score', 0.0)):.2f} "
                f"| просмотры={item.get('views', 0)}"
            )
        if self.top_list.count() == 0:
            self.top_list.addItem("Пока нет данных по топ-контенту.")

        weak_items = []
        for item in top:
            if float(item.get("weighted_engagement_score", 0.0)) < 0.15:
                weak_items.append(item)

        self.weak_list.clear()
        for item in weak_items[:10]:
            self.weak_list.addItem(
                f"{item.get('content_id', '-') } | слабая оценка={float(item.get('weighted_engagement_score', 0.0)):.2f}"
            )
        if self.weak_list.count() == 0:
            self.weak_list.addItem("Для выбранного профиля слабых роликов не найдено.")

        patterns = _safe_list(snapshot.get("analytics_patterns"))
        self.patterns_list.clear()
        for pattern in patterns[:12]:
            self.patterns_list.addItem(
                f"{pattern.get('pattern_type', '-') } | {pattern.get('label', '-') } "
                f"| уверенность={float(pattern.get('confidence', 0.0)):.2f}"
            )
        if self.patterns_list.count() == 0:
            self.patterns_list.addItem("Паттерны пока не выявлены.")

        plan = snapshot.get("analytics_action_plan")
        if isinstance(plan, dict):
            lines = [
                f"Результативность: {plan.get('performance_summary', '-')}",
                "",
                "Что сработало:",
            ]
            lines.extend([f"- {item}" for item in _safe_list(plan.get("top_content_findings"))])
            lines.append("")
            lines.append("Что не сработало:")
            lines.extend([f"- {item}" for item in _safe_list(plan.get("weak_content_findings"))])
            lines.append("")
            lines.append("Следующие шаги:")
            lines.extend([f"- {item}" for item in _safe_list(plan.get("next_actions"))])
            self.plan_text.setPlainText("\n".join(lines).strip())
        else:
            self.plan_text.setPlainText("План действий ещё не сформирован. Используйте кнопку «Сформировать контент-план».")


class AIStudioPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AIStudioPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(SectionHeader("AI-студия", "Восприятие, рекомендации, обучение и креативные брифы"))

        cards = QHBoxLayout()
        self.rec_count_card = MetricCard("Рекомендации", "0", "активный список")
        self.learning_card = MetricCard("Записи обучения", "0", "feedback-цикл")
        self.bundle_card = MetricCard("Пакеты генерации", "0", "конвейер брифов")
        self.confidence_card = MetricCard("Средняя уверенность", "0.00", "доверие к рекомендациям")
        cards.addWidget(self.rec_count_card)
        cards.addWidget(self.learning_card)
        cards.addWidget(self.bundle_card)
        cards.addWidget(self.confidence_card)
        layout.addLayout(cards)

        action_row = QHBoxLayout()
        gen_btn = QPushButton("Сгенерировать рекомендации")
        gen_btn.setObjectName("PrimaryCTA")
        gen_btn.clicked.connect(lambda: self.action_requested.emit("generate_ai_recommendations", None))
        bundle_btn = QPushButton("Собрать пакет генерации")
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
        left_layout.addWidget(SectionHeader("Рекомендации", "Обоснование, уверенность, альтернативы"))
        self.recommendations = QListWidget()
        left_layout.addWidget(self.recommendations)

        right = GlowCard(elevated=False)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.setSpacing(8)
        right_layout.addWidget(SectionHeader("Сводка обучения", "Что система узнала по результатам"))
        self.learning_summary = QTextEdit()
        self.learning_summary.setReadOnly(True)
        right_layout.addWidget(self.learning_summary)

        right_layout.addWidget(SectionHeader("Превью пакета генерации", "Подготовка видео, аудио, сценария и текста"))
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

        self.rec_count_card.set_data(str(len(recs)), "ранжированных элементов")
        learning_count = 0
        if isinstance(learn, dict):
            learning_count = int(learn.get("record_count", 0))
        self.learning_card.set_data(str(learning_count), "зафиксированных исходов")
        self.bundle_card.set_data(str(len(bundles)), "сохранённых пакетов")
        self.confidence_card.set_data(f"{conf_avg:.2f}", "средняя уверенность")

        self.recommendations.clear()
        for item in recs[:16]:
            self.recommendations.addItem(
                f"{item.get('title', item.get('recommendation_type', 'Рекомендация'))} | "
                f"приоритет={item.get('priority', '-') } | уверенность={float(item.get('confidence', 0.0)):.2f}\n"
                f"{item.get('rationale', 'Обоснование не указано') }"
            )
        if self.recommendations.count() == 0:
            self.recommendations.addItem("Пока нет AI-рекомендаций. Сформируйте их для выбранного профиля.")

        if isinstance(learn, dict):
            lines = [
                f"Профиль: {learn.get('profile_id', '-')}",
                f"Количество записей: {learn.get('record_count', 0)}",
                "",
                "Метки исходов:",
            ]
            for key, value in dict(learn.get("outcome_breakdown", {})).items():
                lines.append(f"- {key}: {value}")
            lines.append("")
            lines.append("Ключевые выводы:")
            for item in _safe_list(learn.get("recent_highlights"))[:8]:
                lines.append(f"- {item}")
            self.learning_summary.setPlainText("\n".join(lines))
        else:
            self.learning_summary.setPlainText("Для выбранного профиля сводка обучения пока недоступна.")

        self.bundle_list.clear()
        for bundle in bundles[:12]:
            self.bundle_list.addItem(
                f"{bundle.get('id', '-') } | цель={bundle.get('content_goal', '-') } | "
                f"готово={'да' if bundle.get('generation_ready_flag', False) else 'нет'}"
            )
        if self.bundle_list.count() == 0:
            self.bundle_list.addItem("Пакеты генерации пока отсутствуют.")
