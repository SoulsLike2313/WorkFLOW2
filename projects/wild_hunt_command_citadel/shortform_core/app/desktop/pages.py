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
    QSplitter,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .components import EmptyStateCard, GlowCard, MetricCard, MotionButton, SectionHeader


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


PAGE_GAP = 18
ROW_GAP = 14
GRID_GAP = 12
CARD_INSET = (18, 16, 18, 16)
ACTION_BUTTON_HEIGHT = 40
PRIMARY_ACTION_MIN_WIDTH = 156


def _setup_card_layout(layout: QVBoxLayout) -> None:
    layout.setContentsMargins(*CARD_INSET)
    layout.setSpacing(ROW_GAP)


def _ru_gate(value: str) -> str:
    mapping = {
        "PASS": "PASS",
        "PASS_WITH_WARNINGS": "PASS+",
        "FAIL": "FAIL",
        "UNKNOWN": "н/д",
        "unknown": "н/д",
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


def _ru_connection_type(value: str) -> str:
    mapping = {
        "cdp": "CDP",
        "official_auth": "Официальная авторизация",
        "device": "Устройство",
    }
    return mapping.get(value, value)


def _ru_management_mode(value: str) -> str:
    mapping = {
        "manual": "Ручной",
        "guided": "С подсказками",
        "managed": "Управляемый",
    }
    return mapping.get(value, value)


def _ru_profile_status(value: str) -> str:
    mapping = {
        "active": "Активен",
        "disconnected": "Отключён",
        "warning": "Предупреждение",
        "disabled": "Отключён вручную",
    }
    return mapping.get(value, value)


def _ru_health_state(value: str) -> str:
    mapping = {
        "healthy": "Стабильно",
        "ok": "Стабильно",
        "ready": "Готово",
        "warning": "Требует внимания",
        "degraded": "Ограничено",
        "error": "Ошибка",
        "unknown": "Неизвестно",
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
        layout.setSpacing(PAGE_GAP)

        overview_header = SectionHeader("Обзор", "Сводка рабочего пространства и быстрые действия")
        overview_header.setObjectName("DashboardOverviewHeader")
        layout.addWidget(overview_header)

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(ROW_GAP)
        metrics_grid.setVerticalSpacing(ROW_GAP)

        self.cards = {
            "profiles": MetricCard("Активные профили", "0", "зарегистрировано"),
            "sessions": MetricCard("Подключённые сессии", "0", "открытые окна"),
            "queue": MetricCard("Состояние очереди", "0", "элементов в публикации"),
            "verify": MetricCard("Верификация", "--", "статус гейта"),
            "ai": MetricCard("Состояние AI", "--", "готовность модулей"),
            "updates": MetricCard("Состояние обновлений", "--", "пост-проверка"),
        }

        order = ["profiles", "sessions", "queue", "verify", "ai", "updates"]
        for idx, key in enumerate(order):
            row = idx // 3
            col = idx % 3
            metric_tier = "primary" if row == 0 else "system"
            self.cards[key].setProperty("dashboardMetric", metric_tier)
            metrics_grid.addWidget(self.cards[key], row, col)
            metrics_grid.setColumnStretch(col, 1)

        metrics_grid.setRowStretch(0, 1)
        metrics_grid.setRowStretch(1, 1)

        layout.addLayout(metrics_grid)

        quick_card = GlowCard(elevated=False)
        quick_card.setObjectName("DashboardQuickActions")
        quick_layout = QVBoxLayout(quick_card)
        _setup_card_layout(quick_layout)
        quick_header = SectionHeader("Быстрые действия", "Ключевые шаги рабочего сценария")
        quick_header.setObjectName("DashboardQuickHeader")
        quick_layout.addWidget(quick_header)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row1.setSpacing(GRID_GAP)
        row2.setSpacing(GRID_GAP)

        row1_caption = QLabel("Запуск рабочего цикла")
        row1_caption.setObjectName("DashboardRowCaption")
        row2_caption = QLabel("Планирование и контроль")
        row2_caption.setObjectName("DashboardRowCaption")
        quick_hint = QLabel("Рекомендуемый порядок: профиль -> сессия -> метрики -> план -> AI.")
        quick_hint.setObjectName("SectionHint")
        quick_hint.setWordWrap(True)

        actions = [
            ("Добавить профиль", "add_profile", "primary"),
            ("Открыть сессию", "open_session", "secondary"),
            ("Загрузить метрики", "import_metrics", "outline"),
            ("Собрать контент-план", "generate_plan", "secondary"),
            ("Открыть AI-студию", "open_ai_studio", "secondary"),
            ("Проверить апдейты", "check_updates", "outline"),
        ]
        for idx, (title, action, tone) in enumerate(actions):
            button = MotionButton(title)
            if tone == "primary":
                button.setObjectName("PrimaryCTA")
            elif tone == "outline":
                button.setObjectName("OutlineCTA")
            else:
                button.setObjectName("SecondaryCTA")
            button.setProperty("dashboardQuickButton", "true")
            button.setMinimumHeight(ACTION_BUTTON_HEIGHT)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda _=False, a=action: self.action_requested.emit(a, None))
            (row1 if idx < 3 else row2).addWidget(button, 1)

        quick_layout.addWidget(row1_caption)
        quick_layout.addLayout(row1)
        quick_layout.addWidget(row2_caption)
        quick_layout.addLayout(row2)
        quick_layout.addWidget(quick_hint)
        layout.addWidget(quick_card)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setObjectName("DashboardSplit")
        split.setChildrenCollapsible(False)
        split.setHandleWidth(10)

        audit_card = GlowCard(elevated=False)
        audit_card.setObjectName("DashboardAuditBlock")
        audit_card.setMinimumWidth(320)
        audit_layout = QVBoxLayout(audit_card)
        _setup_card_layout(audit_layout)
        audit_header = SectionHeader("Последние события журнала", "Актуальная лента действий")
        audit_header.setObjectName("DashboardAuditHeader")
        audit_layout.addWidget(audit_header)
        self.audit_list = QListWidget()
        self.audit_list.setObjectName("DashboardAuditList")
        self.audit_list.setSpacing(6)
        self.audit_list.setWordWrap(True)
        audit_layout.addWidget(self.audit_list)

        rec_card = GlowCard(elevated=False)
        rec_card.setObjectName("DashboardRecommendationBlock")
        rec_card.setMinimumWidth(320)
        rec_layout = QVBoxLayout(rec_card)
        _setup_card_layout(rec_layout)
        rec_header = SectionHeader("Сводка рекомендаций AI", "Приоритетные предложения")
        rec_header.setObjectName("DashboardRecommendationHeader")
        rec_layout.addWidget(rec_header)
        self.rec_list = QListWidget()
        self.rec_list.setObjectName("DashboardRecommendationList")
        self.rec_list.setSpacing(6)
        self.rec_list.setWordWrap(True)
        rec_layout.addWidget(self.rec_list)

        split.addWidget(audit_card)
        split.addWidget(rec_card)
        split.setStretchFactor(0, 11)
        split.setStretchFactor(1, 9)
        split.setSizes([580, 500])
        layout.addWidget(split, stretch=1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        summary = snapshot.get("workspace_summary", {})
        readiness = snapshot.get("workspace_readiness", {})
        updates = snapshot.get("updates", {})

        self.cards["profiles"].set_data(str(summary.get("active_profiles", 0)), f"{summary.get('profile_count', 0)} всего")
        self.cards["sessions"].set_data(str(summary.get("open_session_windows", 0)), "окна формата 9:16")
        self.cards["queue"].set_data(str(summary.get("queued_content_items", 0)), "контент-элементов")

        verify = str(snapshot.get("verification_state", "--"))
        self.cards["verify"].set_data(_ru_gate(verify), "ручное тестирование доступно только при PASS")

        ai_ready = readiness.get("items", {}).get("ai_ready", False) if isinstance(readiness.get("items"), dict) else False
        self.cards["ai"].set_data("готово" if ai_ready else "ограничено", "ассистивные модули")

        post_status = str(updates.get("post_verify_status", "unknown"))
        self.cards["updates"].set_data(_ru_gate(post_status), str(updates.get("version_label", "версия не определена")))

        self.audit_list.clear()
        for item in _safe_list(snapshot.get("audit_log"))[:16]:
            action_type = str(item.get("action_type", "-"))
            actor = str(item.get("actor_type", "system"))
            result = str(item.get("result", "-"))
            line = f"{_fmt_ts(item.get('created_at'))} · {action_type} · {actor}\n{result}"
            self.audit_list.addItem(line)
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
            try:
                confidence_label = f"{float(confidence):.2f}"
            except Exception:
                confidence_label = str(confidence)
            self.rec_list.addItem(f"Уверенность: {confidence_label} · {title}\n{rationale}")
        if self.rec_list.count() == 0:
            self.rec_list.addItem("Рекомендации появятся после синхронизации метрик профиля.")


class ProfilesPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ProfilesPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)

        header = SectionHeader("Профили", "Тип подключения, режим управления, состояние и быстрые действия")
        header.setObjectName("ProfilesHeader")
        layout.addWidget(header)

        summary = QHBoxLayout()
        summary.setSpacing(ROW_GAP)
        self.profile_total_card = MetricCard("Профилей", "0", "в рабочем реестре")
        self.profile_connected_card = MetricCard("Подключено", "0", "активные связи")
        self.profile_healthy_card = MetricCard("Стабильные", "0", "состояние: стабильно")
        self.profile_attention_card = MetricCard("Требуют внимания", "0", "сигналы и отключения")
        for card in (
            self.profile_total_card,
            self.profile_connected_card,
            self.profile_healthy_card,
            self.profile_attention_card,
        ):
            card.setProperty("profilesMetric", "true")
            summary.addWidget(card)
        layout.addLayout(summary)

        actions_card = GlowCard(elevated=False)
        actions_card.setObjectName("ProfilesQuickActionsBlock")
        actions_layout = QVBoxLayout(actions_card)
        _setup_card_layout(actions_layout)
        actions_layout.addWidget(SectionHeader("Быстрые действия профилей", "Создание, подключение и переходы в рабочие модули"))

        actions_grid = QGridLayout()
        actions_grid.setHorizontalSpacing(GRID_GAP)
        actions_grid.setVerticalSpacing(GRID_GAP)
        profile_actions = [
            ("Создать профиль", "add_profile", "primary"),
            ("Подключить профиль", "connect_profile", "outline"),
            ("Открыть сессию", "open_session", "secondary"),
            ("Открыть аналитику", "open_analytics", "secondary"),
            ("Открыть контент", "open_content", "secondary"),
            ("Открыть AI", "open_ai_studio", "secondary"),
        ]
        for idx, (title, action, tone) in enumerate(profile_actions):
            btn = MotionButton(title)
            if tone == "primary":
                btn.setObjectName("PrimaryCTA")
            elif tone == "outline":
                btn.setObjectName("OutlineCTA")
            else:
                btn.setObjectName("SecondaryCTA")
            btn.setProperty("profilesQuickAction", "true")
            btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda _=False, a=action: self.action_requested.emit(a, self.selected_profile_id()))
            row = idx // 2
            col = idx % 2
            actions_grid.addWidget(btn, row, col)

        actions_grid.setColumnStretch(0, 1)
        actions_grid.setColumnStretch(1, 1)
        actions_layout.addLayout(actions_grid)
        layout.addWidget(actions_card)

        identity_card = GlowCard(elevated=False)
        identity_card.setObjectName("ProfilesIdentityBlock")
        identity_layout = QVBoxLayout(identity_card)
        _setup_card_layout(identity_layout)
        identity_layout.addWidget(SectionHeader("Карточка выбранного профиля", "Быстрый срез по состоянию профиля и сессии"))

        identity_body = QHBoxLayout()
        identity_body.setSpacing(14)
        self.identity_avatar = QLabel("PR")
        self.identity_avatar.setObjectName("ProfilesAvatar")
        self.identity_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.identity_avatar.setMinimumSize(52, 52)
        self.identity_avatar.setMaximumSize(52, 52)
        identity_body.addWidget(self.identity_avatar, alignment=Qt.AlignmentFlag.AlignTop)

        identity_info_col = QVBoxLayout()
        identity_info_col.setSpacing(7)
        self.identity_name = QLabel("Профиль не выбран")
        self.identity_name.setObjectName("ProfilesIdentityName")
        self.identity_name.setWordWrap(True)
        identity_info_col.addWidget(self.identity_name)
        self.identity_meta = QLabel("Выберите профиль в таблице, чтобы увидеть контекст и быстрые действия.")
        self.identity_meta.setObjectName("ProfilesIdentityMeta")
        self.identity_meta.setWordWrap(True)
        identity_info_col.addWidget(self.identity_meta)
        self.identity_aux = QLabel("Последнее обновление: —")
        self.identity_aux.setObjectName("ProfilesIdentityAux")
        self.identity_aux.setWordWrap(True)
        identity_info_col.addWidget(self.identity_aux)
        identity_body.addLayout(identity_info_col, stretch=2)

        chips_grid = QGridLayout()
        chips_grid.setHorizontalSpacing(8)
        chips_grid.setVerticalSpacing(8)
        self.connection_chip = QLabel("Подключение: —")
        self.mode_chip = QLabel("Режим: —")
        self.health_chip = QLabel("Здоровье: —")
        self.session_chip = QLabel("Сессия: —")
        for chip in (self.connection_chip, self.mode_chip, self.health_chip, self.session_chip):
            chip.setProperty("profileStateChip", "true")
            chip.setProperty("profileStateLevel", "info")
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chip.setMinimumHeight(29)
        chips_grid.addWidget(self.connection_chip, 0, 0)
        chips_grid.addWidget(self.mode_chip, 0, 1)
        chips_grid.addWidget(self.health_chip, 1, 0)
        chips_grid.addWidget(self.session_chip, 1, 1)
        identity_body.addLayout(chips_grid, stretch=3)
        identity_layout.addLayout(identity_body)

        selected_actions = QGridLayout()
        selected_actions.setHorizontalSpacing(GRID_GAP)
        selected_actions.setVerticalSpacing(GRID_GAP)
        connect_selected = MotionButton("Подключить выбранный")
        connect_selected.setObjectName("PrimaryCTA")
        connect_selected.setProperty("profilesSelectedAction", "true")
        connect_selected.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        connect_selected.clicked.connect(lambda: self.action_requested.emit("connect_profile", self.selected_profile_id()))
        open_session = MotionButton("Открыть сессию")
        open_session.setObjectName("SecondaryCTA")
        open_session.setProperty("profilesSelectedAction", "true")
        open_session.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        open_session.clicked.connect(lambda: self.action_requested.emit("open_session", self.selected_profile_id()))
        open_analytics = MotionButton("Открыть аналитику")
        open_analytics.setObjectName("OutlineCTA")
        open_analytics.setProperty("profilesSelectedAction", "true")
        open_analytics.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        open_analytics.clicked.connect(lambda: self.action_requested.emit("open_analytics", self.selected_profile_id()))
        selected_actions.addWidget(connect_selected, 0, 0)
        selected_actions.addWidget(open_session, 0, 1)
        selected_actions.addWidget(open_analytics, 1, 0, 1, 2)
        selected_actions.setColumnStretch(0, 1)
        selected_actions.setColumnStretch(1, 1)
        identity_layout.addLayout(selected_actions)
        selected_hint = QLabel("Поток действий: подключение -> открытие сессии -> переход в аналитику.")
        selected_hint.setObjectName("SectionHint")
        selected_hint.setWordWrap(True)
        identity_layout.addWidget(selected_hint)
        layout.addWidget(identity_card)

        self.table = QTableWidget(0, 8)
        self.table.setObjectName("ProfilesTable")
        self.table.setHorizontalHeaderLabels(["Профиль", "Платформа", "Подключение", "Режим", "Статус", "Состояние", "Сессия", "Обновлено"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._emit_profile_selected)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(116)
        self.table.horizontalHeader().setMinimumSectionSize(84)
        layout.addWidget(self.table, stretch=1)

    def _profile_initials(self, name: str) -> str:
        parts = [part for part in name.replace("-", " ").split() if part]
        if not parts:
            return "PR"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[1][0]).upper()

    def _set_profile_chip(self, chip: QLabel, text: str, level: str) -> None:
        if level not in {"ok", "warn", "danger", "info"}:
            level = "info"
        chip.setText(text)
        if chip.property("profileStateLevel") != level:
            chip.setProperty("profileStateLevel", level)
            chip.style().unpolish(chip)
            chip.style().polish(chip)

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
        sessions_by_profile = snapshot.get("sessions_by_profile", {})
        sessions_by_profile = sessions_by_profile if isinstance(sessions_by_profile, dict) else {}

        connected = 0
        healthy = 0
        attention = 0
        for profile in items:
            status = str(profile.get("status", "")).lower()
            health = str(profile.get("health_state", "")).lower()
            if status in {"active"}:
                connected += 1
            if health in {"healthy", "ok", "ready"}:
                healthy += 1
            if status in {"warning", "disconnected", "disabled"} or health in {"warning", "degraded", "error"}:
                attention += 1

        self.profile_total_card.set_data(str(len(items)), "всего профилей")
        self.profile_connected_card.set_data(str(connected), "в активном состоянии")
        self.profile_healthy_card.set_data(str(healthy), "стабильные и готовые")
        self.profile_attention_card.set_data(str(attention), "требуют проверки")

        self.table.setRowCount(0)
        for row, profile in enumerate(items):
            self.table.insertRow(row)
            display_name = str(profile.get("display_name", "Без имени"))
            profile_id = profile.get("id")
            session = sessions_by_profile.get(profile_id) or {}
            session = session if isinstance(session, dict) else {}
            session_open = bool(session.get("is_open", False))
            session_runtime = _ru_runtime_state(str(session.get("runtime_state", "closed")))

            marker = self._profile_initials(display_name)
            name_item = QTableWidgetItem(f"{marker}  {display_name}")
            name_item.setData(Qt.ItemDataRole.UserRole, profile.get("id"))

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, QTableWidgetItem(str(profile.get("platform", "-"))))
            self.table.setItem(row, 2, QTableWidgetItem(_ru_connection_type(str(profile.get("connection_type", "-")))))
            self.table.setItem(row, 3, QTableWidgetItem(_ru_management_mode(str(profile.get("management_mode", "-")))))
            self.table.setItem(row, 4, QTableWidgetItem(_ru_profile_status(str(profile.get("status", "-")))))
            self.table.setItem(row, 5, QTableWidgetItem(_ru_health_state(str(profile.get("health_state", "-")))))
            self.table.setItem(row, 6, QTableWidgetItem(f"{'Открыта' if session_open else 'Закрыта'} · {session_runtime}"))
            self.table.setItem(row, 7, QTableWidgetItem(_fmt_ts(profile.get("updated_at"))))

            if selected and profile.get("id") == selected:
                self.table.selectRow(row)

        selected_profile = None
        if selected:
            selected_profile = next((profile for profile in items if profile.get("id") == selected), None)
        if selected_profile is None and items:
            selected_profile = items[0]

        if isinstance(selected_profile, dict):
            profile_id = selected_profile.get("id")
            display_name = str(selected_profile.get("display_name", "Профиль"))
            connection = _ru_connection_type(str(selected_profile.get("connection_type", "-")))
            mode = _ru_management_mode(str(selected_profile.get("management_mode", "-")))
            health = _ru_health_state(str(selected_profile.get("health_state", "-")))
            status = _ru_profile_status(str(selected_profile.get("status", "-")))
            session = sessions_by_profile.get(profile_id) or {}
            session = session if isinstance(session, dict) else {}
            session_open = bool(session.get("is_open", False))
            runtime = _ru_runtime_state(str(session.get("runtime_state", "closed")))
            updated = _fmt_ts(selected_profile.get("updated_at"))

            self.identity_avatar.setText(self._profile_initials(display_name))
            self.identity_name.setText(display_name)
            self.identity_meta.setText(f"{status} · {connection} · режим {mode.lower()}")
            self.identity_aux.setText(
                f"Последнее обновление: {updated} · "
                f"Сессия: {'открыта' if session_open else 'закрыта'} ({runtime})"
            )
            self._set_profile_chip(self.connection_chip, f"Подключение: {connection}", "ok" if str(selected_profile.get("status", "")).lower() == "active" else "warn")
            self._set_profile_chip(self.mode_chip, f"Режим: {mode}", "info")
            self._set_profile_chip(
                self.health_chip,
                f"Здоровье: {health}",
                "ok" if str(selected_profile.get("health_state", "")).lower() in {"healthy", "ok", "ready"} else "warn",
            )
            self._set_profile_chip(
                self.session_chip,
                f"Сессия: {'открыта' if session_open else 'закрыта'}",
                "ok" if session_open else "info",
            )
        else:
            self.identity_avatar.setText("PR")
            self.identity_name.setText("Профиль не выбран")
            self.identity_meta.setText("Выберите профиль в таблице, чтобы увидеть контекст и быстрые действия.")
            self.identity_aux.setText("Последнее обновление: —")
            self._set_profile_chip(self.connection_chip, "Подключение: —", "info")
            self._set_profile_chip(self.mode_chip, "Режим: —", "info")
            self._set_profile_chip(self.health_chip, "Здоровье: —", "info")
            self._set_profile_chip(self.session_chip, "Сессия: —", "info")

class SessionsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SessionsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)

        header = SectionHeader("Сессии", "Премиальное окно 9:16 с управлением и статусом")
        header.setObjectName("SessionsHeader")
        layout.addWidget(header)

        summary = QHBoxLayout()
        summary.setSpacing(ROW_GAP)
        self.sessions_open_card = MetricCard("Открытые сессии", "0", "из доступных профилей")
        self.sessions_selected_card = MetricCard("Текущий профиль", "-", "состояние исполнения")
        self.sessions_viewport_card = MetricCard("Пресет окна", "-", "формат 9:16")
        for card in (self.sessions_open_card, self.sessions_selected_card, self.sessions_viewport_card):
            card.setProperty("sessionsMetric", "true")
            summary.addWidget(card)
        layout.addLayout(summary)

        controls_card = GlowCard(elevated=False)
        controls_card.setObjectName("SessionsControlBlock")
        controls_layout = QVBoxLayout(controls_card)
        _setup_card_layout(controls_layout)
        controls_layout.addWidget(SectionHeader("Управление сессией", "Выбор пресета, запуск и завершение окна профиля"))

        controls_top = QHBoxLayout()
        controls_top.setSpacing(GRID_GAP)
        self.viewport = QComboBox()
        self.viewport.setObjectName("SessionsViewportPreset")
        self.viewport.addItem("Смартфон (по умолчанию)", "smartphone_default")
        self.viewport.addItem("Android (высокий)", "android_tall")
        self.viewport.addItem("iPhone-стиль", "iphone_like")
        self.viewport.addItem("Пользовательский", "custom")
        preset_label = QLabel("Вид:")
        preset_label.setMinimumWidth(66)
        controls_top.addWidget(preset_label)
        controls_top.addWidget(self.viewport, 1)
        controls_layout.addLayout(controls_top)

        open_btn = MotionButton("Открыть сессию")
        open_btn.setObjectName("PrimaryCTA")
        open_btn.setProperty("sessionsAction", "true")
        open_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        open_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        open_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        open_btn.clicked.connect(lambda: self.action_requested.emit("open_session", self._payload()))
        close_btn = MotionButton("Закрыть сессию")
        close_btn.setObjectName("DangerCTA")
        close_btn.setProperty("sessionsAction", "true")
        close_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        close_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        close_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        close_btn.clicked.connect(lambda: self.action_requested.emit("close_session", self._payload()))

        controls_actions = QGridLayout()
        controls_actions.setHorizontalSpacing(GRID_GAP)
        controls_actions.setVerticalSpacing(GRID_GAP)
        controls_actions.addWidget(open_btn, 0, 0)
        controls_actions.addWidget(close_btn, 0, 1)
        controls_actions.setColumnStretch(0, 1)
        controls_actions.setColumnStretch(1, 1)
        controls_layout.addLayout(controls_actions)
        layout.addWidget(controls_card)

        body = QHBoxLayout()
        body.setSpacing(ROW_GAP)

        left_card = GlowCard(elevated=False)
        left_card.setObjectName("SessionsRegistryBlock")
        left_card.setMinimumWidth(280)
        left_layout = QVBoxLayout(left_card)
        _setup_card_layout(left_layout)
        left_layout.addWidget(SectionHeader("Реестр сессий", "Состояние выполнения по каждому профилю"))
        self.session_list = QListWidget()
        self.session_list.setObjectName("SessionsList")
        self.session_list.setSpacing(6)
        self.session_list.setWordWrap(True)
        self.session_list.itemClicked.connect(self._session_clicked)
        left_layout.addWidget(self.session_list)
        body.addWidget(left_card, stretch=2)

        right_card = GlowCard(elevated=False)
        right_card.setObjectName("SessionsWorkspaceBlock")
        right_card.setMinimumWidth(340)
        right_layout = QVBoxLayout(right_card)
        _setup_card_layout(right_layout)

        self.session_frame = GlowCard(elevated=True)
        self.session_frame.setObjectName("SessionFrame")
        frame_layout = QVBoxLayout(self.session_frame)
        frame_layout.setContentsMargins(18, 18, 18, 18)
        frame_layout.setSpacing(ROW_GAP)

        self.frame_title = QLabel("Окно сессии 9:16")
        self.frame_title.setObjectName("SectionTitle")
        self.frame_title.setWordWrap(True)
        frame_layout.addWidget(self.frame_title)

        self.frame_runtime = QLabel("Активной сессии нет")
        self.frame_runtime.setObjectName("SectionHint")
        self.frame_runtime.setWordWrap(True)
        frame_layout.addWidget(self.frame_runtime)

        self.frame_source = QLabel("Источник: не привязан")
        self.frame_source.setObjectName("SectionHint")
        self.frame_source.setWordWrap(True)
        frame_layout.addWidget(self.frame_source)

        chip_grid = QGridLayout()
        chip_grid.setHorizontalSpacing(10)
        chip_grid.setVerticalSpacing(8)
        self.session_runtime_chip = QLabel("Состояние: ожидание")
        self.session_link_chip = QLabel("Источник: не привязан")
        self.session_viewport_chip = QLabel("Пресет: смартфон")
        for chip, level in (
            (self.session_runtime_chip, "warn"),
            (self.session_link_chip, "warn"),
            (self.session_viewport_chip, "info"),
        ):
            chip.setProperty("sessionChip", "true")
            chip.setProperty("sessionChipLevel", level)
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chip.setMinimumHeight(28)
        chip_grid.addWidget(self.session_runtime_chip, 0, 0)
        chip_grid.addWidget(self.session_link_chip, 0, 1)
        chip_grid.addWidget(self.session_viewport_chip, 1, 0, 1, 2)
        chip_grid.setColumnStretch(0, 1)
        chip_grid.setColumnStretch(1, 1)
        frame_layout.addLayout(chip_grid)

        self.session_preview = QLabel("ПРЕВЬЮ СЕССИИ 9:16\n\nОткройте сессию профиля, чтобы увидеть рабочее состояние.")
        self.session_preview.setObjectName("SessionMobilePreview")
        self.session_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_preview.setMinimumSize(240, 320)
        self.session_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.session_preview.setWordWrap(True)
        frame_layout.addWidget(self.session_preview)

        self.session_telemetry = QLabel("Телеметрия: синхронизация — | ввод — | поток —")
        self.session_telemetry.setObjectName("SectionHint")
        self.session_telemetry.setWordWrap(True)
        frame_layout.addWidget(self.session_telemetry)

        self.session_activity = QLabel("Активность: ожидается выбор профиля и запуск сессии.")
        self.session_activity.setObjectName("SectionHint")
        self.session_activity.setWordWrap(True)
        frame_layout.addWidget(self.session_activity)

        context_block = QWidget()
        context_block.setObjectName("SessionContextBlock")
        context_layout = QVBoxLayout(context_block)
        context_layout.setContentsMargins(12, 12, 12, 12)
        context_layout.setSpacing(8)
        self.frame_context = QLabel("Контур сессии ожидает подключения профиля и источника.")
        self.frame_context.setObjectName("SessionContextHint")
        self.frame_context.setWordWrap(True)
        context_layout.addWidget(self.frame_context)
        self.frame_next_step = QLabel("Следующий шаг: выберите профиль в реестре и откройте сессию.")
        self.frame_next_step.setObjectName("SessionNextStep")
        self.frame_next_step.setWordWrap(True)
        context_layout.addWidget(self.frame_next_step)
        frame_layout.addWidget(context_block)

        self.frame_footer = QLabel("Контекст: рабочая мобильная рамка с привязкой к источнику.")
        self.frame_footer.setObjectName("SectionHint")
        self.frame_footer.setWordWrap(True)
        frame_layout.addWidget(self.frame_footer)

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

    def _set_session_chip(self, chip: QLabel, text: str, level: str) -> None:
        if level not in {"ok", "warn", "info"}:
            level = "info"
        chip.setText(text)
        if chip.property("sessionChipLevel") != level:
            chip.setProperty("sessionChipLevel", level)
            chip.style().unpolish(chip)
            chip.style().polish(chip)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        self.session_list.clear()

        selected_profile_id = snapshot.get("selected_profile_id")
        sessions_by_profile = snapshot.get("sessions_by_profile", {})
        profiles = _safe_list(snapshot.get("profiles"))
        open_sessions = 0

        for profile in profiles:
            profile_id = profile.get("id")
            session = sessions_by_profile.get(profile_id) or {}
            is_open = bool(session.get("is_open", False))
            if is_open:
                open_sessions += 1
            session_runtime = _ru_runtime_state(str(session.get("runtime_state", "closed")))
            session_source_raw = str(session.get("attached_source_type", "")).strip()
            session_source = (
                session_source_raw
                if session_source_raw and session_source_raw.lower() not in {"none", "null", "-", "не указан"}
                else "не указан"
            )
            session_viewport = _ru_viewport_preset(str(session.get("viewport_preset", "smartphone_default")))
            line = (
                f"{profile.get('display_name', 'Без имени')}\n"
                f"Состояние: {session_runtime} · Окно: {'открыто' if is_open else 'закрыто'}\n"
                f"Источник: {session_source} · Пресет: {session_viewport}"
            )
            item = QListWidgetItem(line)
            item.setData(Qt.ItemDataRole.UserRole, profile_id)
            self.session_list.addItem(item)
            if profile_id == selected_profile_id:
                self.session_list.setCurrentItem(item)

        selected_session = snapshot.get("selected_session") or {}
        profile_name = snapshot.get("selected_profile_name", "Профиль не выбран")
        runtime_state = _ru_runtime_state(str(selected_session.get("runtime_state", "closed")))
        viewport_label = _ru_viewport_preset(str(selected_session.get("viewport_preset", "-")))
        is_open = bool(selected_session.get("is_open", False))
        source_raw = str(selected_session.get("attached_source_type", "")).strip()
        source_label = source_raw if source_raw and source_raw.lower() not in {"none", "null", "-", "не указан"} else "не указан"
        source_id_raw = str(selected_session.get("attached_source_id", "")).strip()
        source_id = source_id_raw if source_id_raw and source_id_raw.lower() not in {"none", "null"} else "-"

        self.sessions_open_card.set_data(str(open_sessions), f"из {len(profiles)} профилей")
        self.sessions_selected_card.set_data("Открыта" if is_open else "Закрыта", f"режим: {runtime_state}")
        self.sessions_viewport_card.set_data(viewport_label, "активный профиль")
        self._set_session_chip(self.session_runtime_chip, "Окн.: откр." if is_open else "Окн.: закр.", "ok" if is_open else "warn")
        self._set_session_chip(
            self.session_link_chip,
            f"Источник: {source_label if source_label != 'не указан' else '—'}",
            "info" if source_label != "не указан" else "warn",
        )
        self._set_session_chip(self.session_viewport_chip, f"Пресет: {viewport_label}", "info")

        self.frame_title.setText(f"Сессия 9:16 | {profile_name}")
        self.frame_runtime.setText(
            f"Состояние: {runtime_state} | "
            f"Окно: {'открыто' if is_open else 'закрыто'} | "
            f"Пресет: {viewport_label}"
        )
        self.frame_source.setText(f"Источник: {source_label}\nID: {source_id}")
        if is_open:
            self.session_preview.setText(
                f"АКТИВНАЯ СЕССИЯ 9:16\n\n{profile_name}\n\n"
                f"Состояние: {runtime_state}\n"
                f"Пресет: {viewport_label}\n"
                f"Источник: {source_label}\n\n"
                "Контур готов к рабочим действиям в режиме управления."
            )
            self.session_telemetry.setText("Телеметрия: синхронизация стабильна | ввод доступен | поток 9:16 активен")
            self.session_activity.setText("Активность: окно открыто, источник привязан, рабочая сессия готова к контентным операциям.")
            self.frame_context.setText("Сессия активна и синхронизирована с профилем. Можно переходить к контенту и аналитике.")
            self.frame_next_step.setText("Следующий шаг: откройте «Контент» для очереди публикаций или «Аналитику» для оценки динамики.")
        else:
            self.session_preview.setText(
                "ПРЕВЬЮ СЕССИИ 9:16\n\n"
                "Сессия не открыта.\n"
                "Выберите профиль в реестре и нажмите «Открыть сессию».\n\n"
                "Рамка подготовлена и ожидает подключение источника."
            )
            if selected_profile_id:
                self.session_telemetry.setText("Телеметрия: синхронизация отсутствует | ввод недоступен | поток остановлен")
                self.session_activity.setText("Активность: профиль выбран, система ожидает запуск окна сессии.")
                self.frame_context.setText("Профиль выбран, но рабочее окно сессии ещё не запущено.")
                self.frame_next_step.setText("Следующий шаг: задайте пресет окна и нажмите «Открыть сессию».")
            else:
                self.session_telemetry.setText("Телеметрия: синхронизация — | ввод — | поток —")
                self.session_activity.setText("Активность: ожидается выбор профиля и запуск сессии.")
                self.frame_context.setText("Сессионная зона ожидает выбор профиля в реестре.")
                self.frame_next_step.setText("Следующий шаг: выберите профиль слева, затем откройте сессию 9:16.")
        self.frame_footer.setText("Сессионная зона связана со статусом профиля, источником и текущим пресетом окна.")


class ContentPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ContentPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)
        layout.addWidget(SectionHeader("Контент", "Библиотека, очередь, валидация и готовность к публикации"))

        summary = QHBoxLayout()
        summary.setSpacing(ROW_GAP)
        self.card_total = MetricCard("Библиотека", "0", "элементов")
        self.card_queue = MetricCard("В очереди", "0", "готово к публикации")
        self.card_ready = MetricCard("Готово", "0", "прошло валидацию")
        self.card_invalid = MetricCard("Риски и ошибки", "0", "требует проверки")
        summary.addWidget(self.card_total)
        summary.addWidget(self.card_queue)
        summary.addWidget(self.card_ready)
        summary.addWidget(self.card_invalid)
        layout.addLayout(summary)

        actions = QGridLayout()
        actions.setHorizontalSpacing(GRID_GAP)
        actions.setVerticalSpacing(GRID_GAP)
        actions_caption = QLabel("Операции контента")
        actions_caption.setObjectName("DashboardRowCaption")
        layout.addWidget(actions_caption)
        add_btn = MotionButton("Добавить демо-контент")
        add_btn.setObjectName("OutlineCTA")
        add_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        add_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        add_btn.clicked.connect(lambda: self.action_requested.emit("add_placeholder_content", None))
        validate_btn = MotionButton("Проверить выбранное")
        validate_btn.setObjectName("SecondaryCTA")
        validate_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        validate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        validate_btn.clicked.connect(lambda: self.action_requested.emit("validate_content", self.selected_content_id()))
        queue_btn = MotionButton("Поставить в очередь")
        queue_btn.setObjectName("PrimaryCTA")
        queue_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        queue_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        queue_btn.clicked.connect(lambda: self.action_requested.emit("queue_content", self.selected_content_id()))
        actions.addWidget(add_btn, 0, 0)
        actions.addWidget(validate_btn, 0, 1)
        actions.addWidget(queue_btn, 0, 2)
        actions.setColumnStretch(0, 1)
        actions.setColumnStretch(1, 1)
        actions.setColumnStretch(2, 1)
        layout.addLayout(actions)
        self.content_hint = QLabel("Подсказка: сначала валидация, затем постановка в очередь публикации.")
        self.content_hint.setObjectName("SectionHint")
        self.content_hint.setWordWrap(True)
        layout.addWidget(self.content_hint)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Статус", "Валидация", "Длительность", "Тема", "Обновлено"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(128)
        self.table.horizontalHeader().setMinimumSectionSize(84)
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
        if not items:
            self.content_hint.setText("Добавьте контент и выполните валидацию перед постановкой в очередь.")
        elif invalid > 0:
            self.content_hint.setText("Обнаружены риски: исправьте проблемные элементы до публикации.")
        elif queued > 0:
            self.content_hint.setText("Очередь сформирована. Проверьте готовность профиля перед запуском публикаций.")
        else:
            self.content_hint.setText("Контент готов. Следующий шаг: поставьте выбранные элементы в очередь.")

class AnalyticsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AnalyticsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)
        analytics_header = SectionHeader("Аналитика", "Результативность, топ-контент, слабые сигналы и план действий")
        analytics_header.setObjectName("AnalyticsHeader")
        layout.addWidget(analytics_header)

        row = QHBoxLayout()
        row.setSpacing(ROW_GAP)
        self.views_card = MetricCard("Окно просмотров", "0", "результат профиля")
        self.engagement_card = MetricCard("Вовлечённость", "0", "суммарно за окно")
        self.momentum_card = MetricCard("Моментум", "0", "оценка динамики")
        self.top_card = MetricCard("Топ-контент", "0", "ранжирование по весам")
        for card in (self.views_card, self.engagement_card, self.momentum_card, self.top_card):
            card.setProperty("analyticsMetric", "true")
        row.addWidget(self.views_card)
        row.addWidget(self.engagement_card)
        row.addWidget(self.momentum_card)
        row.addWidget(self.top_card)
        layout.addLayout(row)

        story_card = GlowCard(elevated=False)
        story_card.setObjectName("AnalyticsStoryBlock")
        story_layout = QVBoxLayout(story_card)
        _setup_card_layout(story_layout)
        story_layout.addWidget(SectionHeader("История периода", "Ключевой контекст и сигналы перед действиями"))

        self.story_headline = QLabel("Ожидаем данные, чтобы построить связную картину результатов.")
        self.story_headline.setObjectName("AnalyticsStoryHeadline")
        self.story_headline.setWordWrap(True)
        story_layout.addWidget(self.story_headline)

        self.story_subline = QLabel("После синхронизации метрик появятся тренды, риски и приоритеты на следующий цикл.")
        self.story_subline.setObjectName("AnalyticsStorySubline")
        self.story_subline.setWordWrap(True)
        story_layout.addWidget(self.story_subline)

        self.story_signals = QLabel("Ключевые сигналы:\n• ожидаем метрики\n• ожидаем паттерны\n• ожидаем action plan")
        self.story_signals.setObjectName("SectionHint")
        self.story_signals.setWordWrap(True)
        story_layout.addWidget(self.story_signals)

        cues_grid = QGridLayout()
        cues_grid.setHorizontalSpacing(GRID_GAP)
        cues_grid.setVerticalSpacing(8)
        self.trend_chip = QLabel("Тренд: —")
        self.quality_chip = QLabel("Качество: —")
        self.stability_chip = QLabel("Стабильность: —")
        self.action_chip = QLabel("План: —")
        for chip, level in (
            (self.trend_chip, "info"),
            (self.quality_chip, "info"),
            (self.stability_chip, "info"),
            (self.action_chip, "info"),
        ):
            chip.setProperty("analyticsCue", "true")
            chip.setProperty("analyticsCueLevel", level)
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chip.setMinimumHeight(30)
        cues_grid.addWidget(self.trend_chip, 0, 0)
        cues_grid.addWidget(self.quality_chip, 0, 1)
        cues_grid.addWidget(self.stability_chip, 1, 0)
        cues_grid.addWidget(self.action_chip, 1, 1)
        cues_grid.setColumnStretch(0, 1)
        cues_grid.setColumnStretch(1, 1)
        story_layout.addLayout(cues_grid)
        layout.addWidget(story_card)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setObjectName("AnalyticsSplit")
        split.setChildrenCollapsible(False)
        split.setHandleWidth(10)

        left = GlowCard(elevated=False)
        left.setObjectName("AnalyticsTopWeakBlock")
        left.setMinimumWidth(320)
        left_layout = QVBoxLayout(left)
        _setup_card_layout(left_layout)
        top_header = SectionHeader("Топ-контент", "Лучшие ролики и выбросы")
        top_header.setObjectName("AnalyticsTopHeader")
        left_layout.addWidget(top_header)
        self.top_list = QListWidget()
        self.top_list.setObjectName("AnalyticsTopList")
        self.top_list.setSpacing(6)
        self.top_list.setWordWrap(True)
        left_layout.addWidget(self.top_list)

        weak_header = SectionHeader("Слабые сигналы", "Вероятные причины и кандидаты на остановку")
        weak_header.setObjectName("AnalyticsWeakHeader")
        left_layout.addWidget(weak_header)
        self.weak_list = QListWidget()
        self.weak_list.setObjectName("AnalyticsWeakList")
        self.weak_list.setSpacing(6)
        self.weak_list.setWordWrap(True)
        left_layout.addWidget(self.weak_list)

        right = GlowCard(elevated=False)
        right.setObjectName("AnalyticsInsightsBlock")
        right.setMinimumWidth(320)
        right_layout = QVBoxLayout(right)
        _setup_card_layout(right_layout)
        patterns_header = SectionHeader("Паттерны контента", "Темы, форматы, хуки и окна публикации")
        patterns_header.setObjectName("AnalyticsPatternsHeader")
        right_layout.addWidget(patterns_header)
        self.patterns_list = QListWidget()
        self.patterns_list.setObjectName("AnalyticsPatternsList")
        self.patterns_list.setSpacing(6)
        self.patterns_list.setWordWrap(True)
        right_layout.addWidget(self.patterns_list)

        plan_header = SectionHeader("Сводка плана действий", "Что повторить, протестировать и остановить")
        plan_header.setObjectName("AnalyticsPlanHeader")
        right_layout.addWidget(plan_header)
        self.plan_text = QTextEdit()
        self.plan_text.setObjectName("AnalyticsPlanText")
        self.plan_text.setReadOnly(True)
        right_layout.addWidget(self.plan_text)

        recs_header = SectionHeader("Рекомендации", "Приоритеты для следующего цикла публикаций")
        recs_header.setObjectName("AnalyticsRecommendationsHeader")
        right_layout.addWidget(recs_header)
        self.recommendations_list = QListWidget()
        self.recommendations_list.setObjectName("AnalyticsRecommendationList")
        self.recommendations_list.setSpacing(6)
        self.recommendations_list.setWordWrap(True)
        right_layout.addWidget(self.recommendations_list)

        split.addWidget(left)
        split.addWidget(right)
        split.setStretchFactor(0, 11)
        split.setStretchFactor(1, 9)
        split.setSizes([560, 500])
        layout.addWidget(split, stretch=1)

    def _set_cue_chip(self, chip: QLabel, text: str, level: str) -> None:
        if level not in {"ok", "warn", "danger", "info"}:
            level = "info"
        chip.setText(text)
        if chip.property("analyticsCueLevel") != level:
            chip.setProperty("analyticsCueLevel", level)
            chip.style().unpolish(chip)
            chip.style().polish(chip)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        perf = snapshot.get("analytics_performance", {}) or {}
        self.views_card.set_data(_fmt_num(perf.get("total_views_window", 0)), perf.get("snapshot_window", "период"))
        self.engagement_card.set_data(f"{float(perf.get('total_engagement_window', 0.0)):.2f}", "вовлечённость за период")
        self.momentum_card.set_data(f"{float(perf.get('momentum_score', 0.0)):.2f}", "оценка динамики")

        top = _safe_list(snapshot.get("analytics_top_content"))
        self.top_card.set_data(str(len(top)), "позиций")

        weak_items = []
        for item in top:
            if float(item.get("weighted_engagement_score", 0.0)) < 0.15:
                weak_items.append(item)

        top_scores = [float(item.get("weighted_engagement_score", 0.0)) for item in top]
        avg_top_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
        weak_ratio = (len(weak_items) / len(top)) if top else 0.0
        momentum = float(perf.get("momentum_score", 0.0))
        recs = _safe_list(snapshot.get("analytics_recommendations"))
        plan = snapshot.get("analytics_action_plan")
        plan_steps = _safe_list(plan.get("next_actions")) if isinstance(plan, dict) else []

        if not top:
            self.story_headline.setText("Данных пока недостаточно для устойчивой оценки динамики контента.")
            self.story_subline.setText("Синхронизируйте метрики и сформируйте рекомендации, чтобы увидеть вектор роста.")
        elif momentum >= 0.6 and avg_top_score >= 0.28:
            self.story_headline.setText("Профиль показывает уверенный рост: сильные ролики удерживают темп.")
            self.story_subline.setText("Рекомендуется масштабировать рабочие форматы и закрепить слот публикации по времени.")
        elif momentum < 0.25 or weak_ratio >= 0.45:
            self.story_headline.setText("Динамика замедлена: заметна доля слабых роликов и нестабильные сигналы.")
            self.story_subline.setText("Приоритет — пересборка хука, упрощение структуры и короткий цикл повторного теста.")
        else:
            self.story_headline.setText("Результаты смешанные: есть точки роста, но стабильность пока не закреплена.")
            self.story_subline.setText("Сфокусируйтесь на 2–3 форматах с лучшей вовлечённостью и снижайте вариативность.")

        trend_text, trend_level = (
            ("Тренд: рост", "ok")
            if momentum >= 0.6
            else ("Тренд: замедление", "warn")
            if momentum < 0.25
            else ("Тренд: стабилизация", "info")
        )
        quality_text, quality_level = (
            ("Качество: сильное", "ok")
            if avg_top_score >= 0.30
            else ("Качество: умеренное", "info")
            if avg_top_score >= 0.17
            else ("Качество: слабое", "warn")
        )
        stability_text, stability_level = (
            ("Стабильность: высокая", "ok")
            if weak_ratio <= 0.20
            else ("Стабильность: средняя", "info")
            if weak_ratio <= 0.40
            else ("Стабильность: риск", "warn")
        )
        action_text, action_level = (
            (f"План: {len(plan_steps)} шага", "ok")
            if len(plan_steps) >= 3
            else ("План: доработать", "warn")
            if top
            else ("План: ожидание", "info")
        )
        self._set_cue_chip(self.trend_chip, trend_text, trend_level)
        self._set_cue_chip(self.quality_chip, quality_text, quality_level)
        self._set_cue_chip(self.stability_chip, stability_text, stability_level)
        self._set_cue_chip(self.action_chip, action_text, action_level)
        signal_lines = [
            f"• Моментум: {momentum:.2f}",
            f"• Средний top-score: {avg_top_score:.2f}",
            f"• Доля слабых роликов: {weak_ratio * 100:.0f}%",
        ]
        if plan_steps:
            signal_lines.append(f"• Следующий шаг: {plan_steps[0]}")
        self.story_signals.setText("Ключевые сигналы:\n" + "\n".join(signal_lines))

        self.top_list.clear()
        for idx, item in enumerate(top[:10], start=1):
            score = float(item.get("weighted_engagement_score", 0.0))
            views = int(item.get("views", 0))
            engagement_raw = float(item.get("engagement_rate", 0.0))
            engagement_label = f"{engagement_raw * 100:.1f}%" if engagement_raw <= 1.0 else f"{engagement_raw:.1f}%"
            signal = "сильный" if score >= 0.40 else "перспективный" if score >= 0.24 else "умеренный"
            marker = "▲" if score >= 0.40 else "•"
            self.top_list.addItem(
                f"{marker} TOP #{idx} · {item.get('content_id', '-')}\n"
                f"Оценка: {score:.2f} · Вовлечённость: {engagement_label} · Просмотры: {_fmt_num(views)}\n"
                f"Инсайт: {signal} сигнал, формат можно масштабировать."
            )
        if self.top_list.count() == 0:
            self.top_list.addItem("Пока нет данных по топ-контенту.")

        self.weak_list.clear()
        for idx, item in enumerate(weak_items[:10], start=1):
            score = float(item.get("weighted_engagement_score", 0.0))
            completion = float(item.get("completion_rate", 0.0))
            comments_ratio = float(item.get("comment_to_view_ratio", 0.0))
            causes: list[str] = []
            if completion and completion < 0.35:
                causes.append("слабое удержание")
            if comments_ratio and comments_ratio < 0.01:
                causes.append("низкая реакция аудитории")
            if not causes:
                causes.append("низкая конверсия в действия")
            self.weak_list.addItem(
                f"▼ RISK #{idx} · {item.get('content_id', '-')}\n"
                f"Оценка: {score:.2f} · Причины: {', '.join(causes)}\n"
                f"Рекомендация: пересобрать хук и структуру, затем повторно проверить формат."
            )
        if self.weak_list.count() == 0:
            self.weak_list.addItem("Для выбранного профиля слабых роликов не найдено.")

        patterns = _safe_list(snapshot.get("analytics_patterns"))
        self.patterns_list.clear()
        for pattern in patterns[:12]:
            confidence = float(pattern.get("confidence", 0.0))
            marker = "◆" if confidence >= 0.65 else "◇" if confidence >= 0.40 else "·"
            strength = "сильный" if confidence >= 0.65 else "рабочий" if confidence >= 0.40 else "гипотеза"
            self.patterns_list.addItem(
                f"{marker} {pattern.get('pattern_type', '-')} · {pattern.get('label', '-')}\n"
                f"Уверенность: {confidence:.2f} ({strength}) | подтверждение: {pattern.get('evidence', '-')}"
            )
        if self.patterns_list.count() == 0:
            self.patterns_list.addItem("Паттерны пока не выявлены.")

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
            self.plan_text.setPlainText("План действий ещё не сформирован. Используйте кнопку «Собрать контент-план».")

        self.recommendations_list.clear()
        for idx, rec in enumerate(recs[:10], start=1):
            title = str(rec.get("title", rec.get("recommendation_type", "Рекомендация")))
            rationale = str(rec.get("rationale", "Обоснование не указано"))
            priority = rec.get("priority", "-")
            next_action = str(rec.get("suggested_action", "без явного действия"))
            self.recommendations_list.addItem(
                f"#{idx} · приоритет {priority}\n{title}\n{rationale}\nШаг: {next_action}"
            )
        if self.recommendations_list.count() == 0:
            self.recommendations_list.addItem("Рекомендации появятся после генерации action plan и обновления метрик.")


class AIStudioPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AIStudioPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)

        ai_header = SectionHeader("AI-студия", "Восприятие, рекомендации, обучение и креативные брифы")
        ai_header.setObjectName("AIStudioHeader")
        layout.addWidget(ai_header)

        cards = QHBoxLayout()
        cards.setSpacing(ROW_GAP)
        self.rec_count_card = MetricCard("Рекомендации", "0", "активный список")
        self.learning_card = MetricCard("Записи обучения", "0", "цикл обратной связи")
        self.bundle_card = MetricCard("Пакеты генерации", "0", "конвейер брифов")
        self.confidence_card = MetricCard("Средняя уверенность", "0.00", "доверие к рекомендациям")
        for card in (self.rec_count_card, self.learning_card, self.bundle_card, self.confidence_card):
            card.setProperty("aiMetric", "true")
        cards.addWidget(self.rec_count_card)
        cards.addWidget(self.learning_card)
        cards.addWidget(self.bundle_card)
        cards.addWidget(self.confidence_card)
        layout.addLayout(cards)

        action_card = GlowCard(elevated=False)
        action_card.setObjectName("AIActionBlock")
        action_card_layout = QVBoxLayout(action_card)
        _setup_card_layout(action_card_layout)
        action_card_layout.addWidget(SectionHeader("Операции AI", "Генерация рекомендаций и подготовка рабочего пакета"))

        action_row = QGridLayout()
        action_row.setHorizontalSpacing(GRID_GAP)
        action_row.setVerticalSpacing(GRID_GAP)
        gen_btn = MotionButton("Сгенерировать рекомендации")
        gen_btn.setObjectName("PrimaryCTA")
        gen_btn.setProperty("aiAction", "true")
        gen_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        gen_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        gen_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gen_btn.clicked.connect(lambda: self.action_requested.emit("generate_ai_recommendations", None))
        bundle_btn = MotionButton("Собрать пакет генерации")
        bundle_btn.setObjectName("SecondaryCTA")
        bundle_btn.setProperty("aiAction", "true")
        bundle_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        bundle_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        bundle_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bundle_btn.clicked.connect(lambda: self.action_requested.emit("build_generation_bundle", None))
        action_row.addWidget(gen_btn, 0, 0)
        action_row.addWidget(bundle_btn, 0, 1)
        action_row.setColumnStretch(0, 1)
        action_row.setColumnStretch(1, 1)
        action_card_layout.addLayout(action_row)
        self.ai_operator_hint = QLabel("Поток: сначала рекомендации, затем сбор пакета генерации.")
        self.ai_operator_hint.setObjectName("SectionHint")
        self.ai_operator_hint.setWordWrap(True)
        action_card_layout.addWidget(self.ai_operator_hint)
        layout.addWidget(action_card)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setObjectName("AIStudioSplit")
        split.setChildrenCollapsible(False)
        split.setHandleWidth(10)

        left = GlowCard(elevated=False)
        left.setObjectName("AIRecommendationBlock")
        left.setMinimumWidth(320)
        left_layout = QVBoxLayout(left)
        _setup_card_layout(left_layout)
        ai_recs_header = SectionHeader("Рекомендации", "Обоснование, уверенность, альтернативы")
        ai_recs_header.setObjectName("AIRecommendationsHeader")
        left_layout.addWidget(ai_recs_header)
        self.recommendations = QListWidget()
        self.recommendations.setObjectName("AIRecommendationList")
        self.recommendations.setSpacing(6)
        self.recommendations.setWordWrap(True)
        left_layout.addWidget(self.recommendations)

        right = GlowCard(elevated=False)
        right.setObjectName("AILearningBlock")
        right.setMinimumWidth(320)
        right_layout = QVBoxLayout(right)
        _setup_card_layout(right_layout)
        ai_learn_header = SectionHeader("Сводка обучения", "Что система узнала по результатам")
        ai_learn_header.setObjectName("AILearningHeader")
        right_layout.addWidget(ai_learn_header)
        self.learning_summary = QTextEdit()
        self.learning_summary.setObjectName("AILearningSummary")
        self.learning_summary.setReadOnly(True)
        right_layout.addWidget(self.learning_summary)

        bundle_header = SectionHeader("Превью пакета генерации", "Подготовка видео, аудио, сценария и текста")
        bundle_header.setObjectName("AIBundleHeader")
        right_layout.addWidget(bundle_header)
        self.bundle_list = QListWidget()
        self.bundle_list.setObjectName("AIBundleList")
        self.bundle_list.setSpacing(6)
        self.bundle_list.setWordWrap(True)
        right_layout.addWidget(self.bundle_list)

        split.addWidget(left)
        split.addWidget(right)
        split.setStretchFactor(0, 11)
        split.setStretchFactor(1, 9)
        split.setSizes([560, 500])
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
        if recs and not bundles:
            self.ai_operator_hint.setText("Рекомендации готовы. Следующий шаг: собрать пакет генерации для выбранной идеи.")
        elif bundles:
            self.ai_operator_hint.setText("Пакеты генерации готовы. Проверьте качество и запустите публикационный сценарий.")
        else:
            self.ai_operator_hint.setText("Сначала сформируйте рекомендации, затем соберите пакет генерации.")

        self.recommendations.clear()
        for item in recs[:16]:
            priority = item.get("priority", "-")
            confidence = float(item.get("confidence", 0.0))
            self.recommendations.addItem(
                f"Уверенность {confidence:.2f} · приоритет {priority}\n"
                f"{item.get('title', item.get('recommendation_type', 'Рекомендация'))}\n"
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
            ready = "готов к генерации" if bundle.get("generation_ready_flag", False) else "черновик"
            self.bundle_list.addItem(
                f"{bundle.get('id', '-')} · статус: {ready}\n"
                f"Цель: {bundle.get('content_goal', '-')} | Угол: {bundle.get('creative_angle', '-')}"
            )
        if self.bundle_list.count() == 0:
            self.bundle_list.addItem("Пакеты генерации пока отсутствуют.")
