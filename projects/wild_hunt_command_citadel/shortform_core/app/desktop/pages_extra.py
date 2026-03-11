from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from .components import GlowCard, MetricCard, MotionButton, SectionHeader
from .pages import (
    ACTION_BUTTON_HEIGHT,
    CARD_INSET,
    GRID_GAP,
    PAGE_GAP,
    PRIMARY_ACTION_MIN_WIDTH,
    ROW_GAP,
    BasePage,
)


def _fmt_ts(value: Any) -> str:
    if not value:
        return "-"
    text = str(value)
    return text.replace("T", " ")[:19] if "T" in text else text[:19]


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _ru_gate(value: str) -> str:
    mapping = {
        "PASS": "PASS",
        "PASS_WITH_WARNINGS": "PASS с предупреждениями",
        "FAIL": "FAIL",
        "unknown": "неизвестно",
        "UNKNOWN": "неизвестно",
    }
    return mapping.get(value, value)


def _ru_patch_status(value: str) -> str:
    mapping = {
        "applied": "применён",
        "failed": "ошибка",
        "rolled_back": "откачен",
        "skipped": "пропущен",
        "idle": "ожидание",
        "unknown": "неизвестно",
    }
    return mapping.get(value, value)


class AuditPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("AuditPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)

        layout.addWidget(SectionHeader("Журнал / Таймлайн", "Типизированная лента событий рабочего пространства, AI и обновлений"))

        actions_card = GlowCard(elevated=False)
        actions_card.setObjectName("AuditActionBar")
        actions = QHBoxLayout(actions_card)
        actions.setContentsMargins(*CARD_INSET)
        actions.setSpacing(ROW_GAP)
        refresh_btn = MotionButton("Обновить таймлайн")
        refresh_btn.setObjectName("PrimaryCTA")
        refresh_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        refresh_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        refresh_btn.clicked.connect(lambda: self.action_requested.emit("refresh", None))

        self.level_filter = QComboBox()
        self.level_filter.addItems(["Все", "Инфо", "Предупреждение", "Ошибка"])
        self.level_filter.currentTextChanged.connect(
            lambda _: self.action_requested.emit("refresh", None)
        )

        actions.addWidget(refresh_btn)
        actions.addWidget(QLabel("Уровень:"))
        actions.addWidget(self.level_filter)
        actions.addStretch(1)
        layout.addWidget(actions_card)

        timeline_card = GlowCard(elevated=False)
        timeline_card.setObjectName("AuditTimelineBlock")
        timeline_layout = QVBoxLayout(timeline_card)
        timeline_layout.setContentsMargins(*CARD_INSET)
        timeline_layout.setSpacing(ROW_GAP)
        timeline_layout.addWidget(SectionHeader("Таймлайн событий", "События системы, AI, обновлений и рабочего цикла"))

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Время", "Источник", "Действие", "Результат", "Профиль", "Канал"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(130)
        self.table.setObjectName("AuditTimelineTable")
        timeline_layout.addWidget(self.table)
        layout.addWidget(timeline_card, stretch=1)

        errors_card = GlowCard(elevated=False)
        errors_card.setObjectName("AuditErrorsBlock")
        errors_layout = QVBoxLayout(errors_card)
        errors_layout.setContentsMargins(*CARD_INSET)
        errors_layout.setSpacing(ROW_GAP)
        errors_layout.addWidget(SectionHeader("Последние сбои", "Ошибки выполнения и события запрета политик"))

        self.errors = QListWidget()
        self.errors.setObjectName("AuditErrorsList")
        self.errors.setMinimumHeight(120)
        errors_layout.addWidget(self.errors)
        layout.addWidget(errors_card)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        selected_label = self.level_filter.currentText()
        selected_map = {
            "Все": "all",
            "Инфо": "info",
            "Предупреждение": "warning",
            "Ошибка": "error",
        }
        selected = selected_map.get(selected_label, "all")
        items = _safe_list(snapshot.get("audit_log"))
        errors = _safe_list(snapshot.get("error_log"))

        self.table.setRowCount(0)
        for event in items:
            result = str(event.get("result", "-")).lower()
            level = "info"
            if "error" in result or "ошиб" in result or "denied" in result or "failed" in result:
                level = "error"
            elif "warn" in result or "предупр" in result:
                level = "warning"

            if selected != "all" and selected != level:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(_fmt_ts(event.get("created_at"))))
            self.table.setItem(row, 1, QTableWidgetItem(str(event.get("actor_type", "system"))))
            self.table.setItem(row, 2, QTableWidgetItem(str(event.get("action_type", "-"))))
            self.table.setItem(row, 3, QTableWidgetItem(str(event.get("result", "-"))))
            self.table.setItem(row, 4, QTableWidgetItem(str(event.get("profile_id", "-"))))
            self.table.setItem(row, 5, QTableWidgetItem(str(event.get("source", "workspace"))))

        self.errors.clear()
        for err in errors[:20]:
            self.errors.addItem(
                f"{_fmt_ts(err.get('created_at'))} | {err.get('action_type', '-')} | {err.get('error_text', '-') }"
            )
        if self.errors.count() == 0:
            self.errors.addItem("Критичных ошибок пока нет.")


class UpdatesPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("UpdatesPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)

        layout.addWidget(SectionHeader("Обновления", "Версия, состояние патча и проверка после обновления"))

        cards = QHBoxLayout()
        cards.setSpacing(ROW_GAP)
        self.current_version = MetricCard("Текущая версия", "-", "runtime")
        self.available_version = MetricCard("Доступно", "-", "manifest")
        self.patch_status = MetricCard("Статус патча", "-", "локальный цикл патча")
        self.post_verify = MetricCard("Пост-проверка", "-", "машинный гейт")
        cards.addWidget(self.current_version)
        cards.addWidget(self.available_version)
        cards.addWidget(self.patch_status)
        cards.addWidget(self.post_verify)
        layout.addLayout(cards)

        actions = QGridLayout()
        actions.setHorizontalSpacing(GRID_GAP)
        actions.setVerticalSpacing(GRID_GAP)
        check_btn = MotionButton("Проверить обновления")
        check_btn.setObjectName("PrimaryCTA")
        check_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        check_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        check_btn.clicked.connect(lambda: self.action_requested.emit("check_updates", None))
        post_btn = MotionButton("Запустить пост-проверку")
        post_btn.setObjectName("SecondaryCTA")
        post_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        post_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        post_btn.clicked.connect(lambda: self.action_requested.emit("run_post_verify", None))
        actions.addWidget(check_btn, 0, 0)
        actions.addWidget(post_btn, 0, 1)
        actions.setColumnStretch(0, 1)
        actions.setColumnStretch(1, 1)
        layout.addLayout(actions)

        details_card = GlowCard(elevated=False)
        details_card.setObjectName("UpdatesDiagnosticsBlock")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(*CARD_INSET)
        details_layout.setSpacing(ROW_GAP)
        details_layout.addWidget(SectionHeader("Диагностика обновлений", "Машиночитаемая сводка для оператора"))

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        details_layout.addWidget(self.details)

        layout.addWidget(details_card, stretch=1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        updates = _safe_dict(snapshot.get("updates"))
        ver = _safe_dict(updates.get("version"))
        check = _safe_dict(updates.get("check"))
        patch = _safe_dict(updates.get("patch_result"))
        post = _safe_dict(updates.get("post_verify"))

        current_label = str(ver.get("version_label") or ver.get("version") or "неизвестно")
        self.current_version.set_data(current_label, f"build={ver.get('build', '-')}")

        avail = str(check.get("available_version") or check.get("available") or "н/д")
        self.available_version.set_data(avail, "совместимо" if check.get("is_compatible") else "манифест не найден")

        patch_status = str(patch.get("status") or updates.get("patch_status") or "idle")
        self.patch_status.set_data(_ru_patch_status(patch_status), str(patch.get("message", "локальный цикл патча")))

        post_status = str(post.get("status") or updates.get("post_verify_status") or "unknown")
        self.post_verify.set_data(_ru_gate(post_status), "ручной тест только при PASS")

        lines = [
            f"Проверено: {_fmt_ts(datetime.now().isoformat())}",
            f"Текущая версия: {current_label}",
            f"Доступная версия: {avail}",
            f"Совместимость: {check.get('is_compatible', False)}",
            f"Статус патча: {_ru_patch_status(patch_status)}",
            f"Статус пост-проверки: {_ru_gate(post_status)}",
            "",
            "Примечания к патчу:",
        ]

        for note in _safe_list(check.get("patch_notes"))[:10]:
            lines.append(f"- {note}")

        details = post.get("details")
        if isinstance(details, dict):
            lines.append("")
            lines.append("Детали пост-проверки:")
            for key, value in details.items():
                lines.append(f"- {key}: {value}")

        self.details.setPlainText("\n".join(lines).strip())


class SettingsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("SettingsPage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)

        layout.addWidget(SectionHeader("Настройки", "Параметры рабочего пространства/runtime и ссылки на диагностику"))

        card = GlowCard(elevated=False)
        card.setObjectName("SettingsRuntimeBlock")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(*CARD_INSET)
        card_layout.setSpacing(ROW_GAP)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(8)

        self.mode = QLabel("-")
        self.api_base = QLabel("-")
        self.data_dir = QLabel("-")
        self.logs_dir = QLabel("-")
        self.db_path = QLabel("-")
        self.verification_state = QLabel("-")

        form.addRow("Режим:", self.mode)
        form.addRow("Базовый URL API:", self.api_base)
        form.addRow("Каталог данных:", self.data_dir)
        form.addRow("Каталог логов:", self.logs_dir)
        form.addRow("Путь к БД:", self.db_path)
        form.addRow("Гейт верификации:", self.verification_state)

        card_layout.addLayout(form)

        actions = QGridLayout()
        actions.setHorizontalSpacing(GRID_GAP)
        actions.setVerticalSpacing(GRID_GAP)
        diagnostics_btn = MotionButton("Открыть диагностику")
        diagnostics_btn.setObjectName("OutlineCTA")
        diagnostics_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        diagnostics_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        diagnostics_btn.clicked.connect(lambda: self.action_requested.emit("open_diagnostics", None))
        reload_btn = MotionButton("Обновить настройки")
        reload_btn.setObjectName("PrimaryCTA")
        reload_btn.setMinimumHeight(ACTION_BUTTON_HEIGHT)
        reload_btn.setMinimumWidth(PRIMARY_ACTION_MIN_WIDTH)
        reload_btn.clicked.connect(lambda: self.action_requested.emit("refresh", None))
        actions.addWidget(diagnostics_btn, 0, 0)
        actions.addWidget(reload_btn, 0, 1)
        actions.setColumnStretch(0, 1)
        actions.setColumnStretch(1, 1)
        card_layout.addLayout(actions)

        layout.addWidget(card)
        layout.addStretch(1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        config = _safe_dict(snapshot.get("runtime_config"))
        mode = str(config.get("mode", "user"))
        self.mode.setText("Пользовательский" if mode == "user" else mode)
        self.api_base.setText(str(snapshot.get("api_base_url", "-")))
        self.data_dir.setText(str(config.get("data_dir", "runtime/data")))
        self.logs_dir.setText(str(config.get("logs_dir", "runtime/logs")))
        self.db_path.setText(str(config.get("db_path", "runtime/data/workspace_state.db")))
        self.verification_state.setText(str(snapshot.get("verification_state", "UNKNOWN")))


class PlaceholderPage(BasePage):
    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PAGE_GAP)
        layout.addWidget(SectionHeader(title, subtitle))
        card = GlowCard(elevated=False)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(*CARD_INSET)
        card_layout.setSpacing(ROW_GAP)
        label = QLabel("Модуль экрана подключается к живым данным.")
        label.setWordWrap(True)
        card_layout.addWidget(label)
        layout.addWidget(card)
        layout.addStretch(1)

    def update_snapshot(self, snapshot: dict[str, Any]) -> None:
        _ = snapshot
