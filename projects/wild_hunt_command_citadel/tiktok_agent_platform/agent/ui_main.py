from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QTime, QTimer, Signal, Qt
from PySide6.QtGui import QColor, QDragEnterEvent, QDragLeaveEvent, QDropEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QDoubleSpinBox,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QInputDialog,
    QVBoxLayout,
    QWidget,
)

from dashboard_data import load_dashboard_snapshot
from first_run_wizard import FirstRunWizardDialog, inspect_environment
from profile_parser import parse_profile_payload
from profiles_store import ProfileStore
from settings import BotSettings
from task_scheduler import RunQueue, TaskScheduler, WEEKDAY_LABELS_RU
from worker import BotWorker, CoreWorker

THEME_NAMES = {
    "wolf": "Волк",
    "nilfgaard": "Нильфгаард",
    "skellige": "Скеллиге",
}

def _build_theme_preset(
    *,
    accent: str,
    accent_soft: str,
    accent_deep: str,
    accent_text: str,
    info: str,
) -> Dict[str, str]:
    return {
        "root_bg": "#090c14",
        "text_base": "#f1f4ff",
        "label": "#b8bfd7",
        "header_border": "rgba(170, 182, 240, 0.18)",
        "header_g1": "#131a2b",
        "header_g2": "#0f1423",
        "header_g3": "#0b101c",
        "title": "#f4f6ff",
        "subtitle": "#9aa4c8",
        "status_border": "rgba(154, 125, 255, 0.46)",
        "status_bg": "rgba(119, 93, 205, 0.18)",
        "status_text": "#efe9ff",
        "ready_bg": "rgba(76, 146, 112, 0.22)",
        "ready_border": "rgba(111, 204, 152, 0.58)",
        "ready_text": "#d8ffeb",
        "running_bg": "rgba(138, 108, 255, 0.24)",
        "running_border": "rgba(179, 153, 255, 0.72)",
        "running_text": "#f4ecff",
        "drop_border": "rgba(155, 135, 230, 0.56)",
        "drop_bg": "rgba(119, 101, 192, 0.11)",
        "drop_active_border": "rgba(192, 170, 255, 0.92)",
        "drop_active_bg": "rgba(165, 136, 255, 0.20)",
        "drop_title": "#e3d7ff",
        "drop_hint": "#b9aedf",
        "panel_border": "rgba(145, 157, 214, 0.22)",
        "panel_g1": "#141c2f",
        "panel_g2": "#0f1626",
        "panel_title_bg": "rgba(16, 23, 39, 0.95)",
        "panel_title_text": "#e4e9ff",
        "tag_text": "#d4dcff",
        "tag_border": "rgba(142, 156, 218, 0.32)",
        "tag_bg": "rgba(67, 82, 130, 0.22)",
        "input_border": "rgba(138, 149, 203, 0.40)",
        "input_bg": "#12192b",
        "input_text": "#f6f8ff",
        "input_focus_border": accent,
        "input_focus_bg": "#162039",
        "checkbox_text": "#cfd6f2",
        "checkbox_border": "rgba(142, 155, 212, 0.52)",
        "checkbox_bg": "#0f1423",
        "checkbox_checked_bg": accent_soft,
        "checkbox_checked_border": accent,
        "button_border": "rgba(143, 154, 208, 0.45)",
        "button_text": "#ecf1ff",
        "button_g1": "#252f4c",
        "button_g2": "#1b233b",
        "button_hover_border": accent,
        "button_hover_g1": "#2d3a5e",
        "button_hover_g2": "#212c49",
        "button_pressed": "#171f34",
        "button_disabled_text": "#7f88a6",
        "button_disabled_border": "rgba(95, 103, 136, 0.42)",
        "button_disabled_bg": "#1a2032",
        "start_border": "rgba(125, 203, 160, 0.60)",
        "start_g1": "#234d40",
        "start_g2": "#1c3d34",
        "start_hover_border": "rgba(165, 242, 201, 0.88)",
        "start_hover_g1": "#2d6654",
        "start_hover_g2": "#245344",
        "stop_border": "rgba(217, 116, 140, 0.65)",
        "stop_g1": "#5b2d44",
        "stop_g2": "#432235",
        "stop_hover_border": "rgba(255, 154, 178, 0.88)",
        "stop_hover_g1": "#753451",
        "stop_hover_g2": "#5d2a43",
        "log_bg": "#10162a",
        "log_border": "rgba(134, 148, 206, 0.32)",
        "log_text": "#e9efff",
        "medallion_bg": "#141d34",
        "medallion_border": accent,
        "medallion_text": accent_text,
        "sidebar_bg": "#0d1220",
        "sidebar_border": "rgba(142, 156, 226, 0.24)",
        "sidebar_item_bg": "rgba(121, 102, 201, 0.14)",
        "sidebar_item_hover_bg": "rgba(149, 126, 240, 0.24)",
        "sidebar_item_active_bg": "rgba(174, 147, 255, 0.31)",
        "sidebar_item_text": "#cfd8f8",
        "sidebar_caption": "#8d97bf",
        "elevated_panel": "#151f35",
        "accent": accent,
        "accent_soft": accent_soft,
        "accent_deep": accent_deep,
        "accent_glow": "rgba(157, 130, 255, 0.34)",
        "success": "#6dd3a7",
        "warning": "#eac37b",
        "danger": "#f188a1",
        "info": info,
        "border_subtle": "rgba(137, 149, 204, 0.23)",
        "border_active": accent,
    }


THEME_PRESETS: Dict[str, Dict[str, str]] = {
    "wolf": _build_theme_preset(
        accent="#9a7dff",
        accent_soft="#7d65d8",
        accent_deep="#5f4cae",
        accent_text="#efe7ff",
        info="#8ec1ff",
    ),
    "nilfgaard": _build_theme_preset(
        accent="#b489ff",
        accent_soft="#8a62d2",
        accent_deep="#6e4eb0",
        accent_text="#f4e9ff",
        info="#a0c8ff",
    ),
    "skellige": _build_theme_preset(
        accent="#8b90ff",
        accent_soft="#6268d6",
        accent_deep="#4c53af",
        accent_text="#e8ebff",
        info="#8eb8ff",
    ),
}

THEME_MEDALLION = {
    "wolf": "ВОЛК",
    "nilfgaard": "СОЛН",
    "skellige": "СКЕЛ",
}

THEME_DROP_TITLE = {
    "wolf": "ПРИЕМ ШКОЛЫ ВОЛКА",
    "nilfgaard": "КОМАНДОВАНИЕ НИЛЬФГААРДА",
    "skellige": "БЕРЕГ СКЕЛЛИГЕ",
}


class ProfileDropZone(QFrame):
    profile_parsed = Signal(str, str)
    log_signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setProperty("dragActive", False)
        self.setMinimumHeight(112)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.setSpacing(5)

        self.title_label = QLabel("ПРИЕМ ШКОЛЫ ВОЛКА")
        self.title_label.setObjectName("dropTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)

        label = QLabel(
            "Перетащи JSON/текст профиля из браузера сюда\n"
            "или вставь CDP URL в поле ниже."
        )
        label.setObjectName("dropHint")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(label)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime = event.mimeData()
        if mime.hasUrls() or mime.hasText():
            self._set_drag_state(True)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        self._set_drag_state(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        self._set_drag_state(False)
        mime = event.mimeData()
        text = ""
        file_path: Optional[str] = None

        if mime.hasUrls():
            url = mime.urls()[0]
            if url.isLocalFile():
                file_path = url.toLocalFile()
                try:
                    text = Path(file_path).read_text(encoding="utf-8")
                except Exception:
                    text = file_path

        if not text and mime.hasText():
            text = mime.text()

        cdp_url, profile_url = parse_profile_payload(text, file_path=file_path)
        if cdp_url:
            self.profile_parsed.emit(cdp_url, profile_url or "")
            self.log_signal.emit(f"Профиль распознан. CDP endpoint: {cdp_url}")
        else:
            self.log_signal.emit("Не удалось извлечь CDP URL из перетаскиваемых данных.")

        event.acceptProposedAction()

    def _set_drag_state(self, active: bool) -> None:
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_theme_title(self, title: str) -> None:
        self.title_label.setText(title)


class MiniLineChart(QWidget):
    def __init__(self, title: str, color_hex: str = "#d4ae67") -> None:
        super().__init__()
        self.title = title
        self.values: List[float] = []
        self.color = QColor(color_hex)
        self.setMinimumHeight(126)

    def set_values(self, values: List[float]) -> None:
        self.values = [float(value) for value in values if value is not None]
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(6, 6, -6, -6)
        painter.setPen(QPen(QColor(255, 255, 255, 26), 1))
        painter.drawRoundedRect(rect, 8, 8)

        title_rect = rect.adjusted(10, 8, -10, -rect.height() + 22)
        painter.setPen(QColor(240, 226, 195))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.title)

        chart_rect = rect.adjusted(12, 28, -12, -12)
        painter.setPen(QPen(QColor(255, 255, 255, 34), 1))
        painter.drawLine(chart_rect.left(), chart_rect.bottom(), chart_rect.right(), chart_rect.bottom())

        if len(self.values) < 2:
            painter.setPen(QColor(200, 200, 200, 120))
            painter.drawText(chart_rect, Qt.AlignmentFlag.AlignCenter, "Недостаточно данных")
            return

        low = min(self.values)
        high = max(self.values)
        spread = max(1.0, high - low)
        step_x = chart_rect.width() / max(1, len(self.values) - 1)

        points = []
        for idx, value in enumerate(self.values):
            normalized = (float(value) - low) / spread
            x = chart_rect.left() + idx * step_x
            y = chart_rect.bottom() - normalized * chart_rect.height()
            points.append((x, y))

        painter.setPen(QPen(QColor(self.color.red(), self.color.green(), self.color.blue(), 190), 2.2))
        for idx in range(1, len(points)):
            prev_x, prev_y = points[idx - 1]
            cur_x, cur_y = points[idx]
            painter.drawLine(int(prev_x), int(prev_y), int(cur_x), int(cur_y))

        painter.setPen(QColor(212, 174, 103))
        last_x, last_y = points[-1]
        painter.drawEllipse(int(last_x) - 3, int(last_y) - 3, 6, 6)
        painter.setPen(QColor(245, 240, 226))
        painter.drawText(
            chart_rect.adjusted(0, 0, -2, -2),
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
            f"{int(self.values[-1])}",
        )


class MetricTile(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("metricTile")
        self.setMinimumHeight(118)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("metricTileTitle")
        self.value_label = QLabel("—")
        self.value_label.setObjectName("metricTileValue")
        self.delta_label = QLabel("—")
        self.delta_label.setObjectName("metricTileDelta")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.delta_label)

    def set_value(self, value: str, delta: str = "—") -> None:
        self.value_label.setText(value)
        self.delta_label.setText(delta)


class SessionViewportFrame(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sessionViewportFrame")
        self.setMinimumSize(220, 420)
        self.setMaximumWidth(320)
        self.is_online = False
        self.status_text = "Отключено"
        self.source_text = "Источник не подключен"

    def set_state(self, *, online: bool, status: str, source: str) -> None:
        self.is_online = online
        self.status_text = status
        self.source_text = source
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)

        painter.setPen(QPen(QColor(126, 136, 170, 78), 1.2))
        painter.setBrush(QColor(14, 19, 34, 225))
        painter.drawRoundedRect(rect, 24, 24)

        inner_width = int(rect.height() * (9 / 16))
        inner_width = min(inner_width, rect.width() - 28)
        inner_height = int(inner_width * (16 / 9))
        if inner_height > rect.height() - 28:
            inner_height = rect.height() - 28
            inner_width = int(inner_height * (9 / 16))

        inner_x = rect.center().x() - (inner_width // 2)
        inner_y = rect.center().y() - (inner_height // 2)
        inner_rect = rect.adjusted(0, 0, 0, 0)
        inner_rect.setX(inner_x)
        inner_rect.setY(inner_y)
        inner_rect.setWidth(inner_width)
        inner_rect.setHeight(inner_height)

        glow_color = QColor(156, 132, 255, 190 if self.is_online else 95)
        painter.setPen(QPen(glow_color, 2.0))
        painter.setBrush(QColor(19, 25, 43, 248))
        painter.drawRoundedRect(inner_rect, 20, 20)

        screen = inner_rect.adjusted(12, 16, -12, -16)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(10, 14, 28))
        painter.drawRoundedRect(screen, 14, 14)

        painter.setPen(QColor(224, 230, 255))
        painter.drawText(
            screen.adjusted(0, 16, 0, -screen.height() + 40),
            Qt.AlignmentFlag.AlignHCenter,
            "9:16 Session",
        )
        painter.setPen(QColor(150, 162, 198))
        painter.drawText(
            screen.adjusted(0, 44, 0, -screen.height() + 66),
            Qt.AlignmentFlag.AlignHCenter,
            self.status_text,
        )
        painter.setPen(QColor(128, 141, 177))
        painter.drawText(
            screen.adjusted(18, 0, -18, -18),
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            self.source_text,
        )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Witcher Command Deck | TikTok Ops")
        self.resize(1560, 940)
        self.setMinimumSize(1320, 820)
        self.app_root = Path(__file__).resolve().parent
        self.worker: Optional[BotWorker] = None
        self.core_worker: Optional[CoreWorker] = None
        self.active_run_source = "manual"
        self._workspace_sections: Dict[str, QWidget] = {}

        self.profile_store = ProfileStore(self.app_root / "runtime" / "profiles.json")
        self.scheduler = TaskScheduler(self.app_root / "runtime" / "scheduler_jobs.json")
        self.scheduler.task_due.connect(self._on_scheduled_task_due)
        self.run_queue = RunQueue()

        self.dashboard_timer = QTimer(self)
        self.dashboard_timer.setInterval(30000)
        self.dashboard_timer.timeout.connect(self._refresh_dashboard)

        self.core_root = self._default_core_root()
        self.current_theme_key = "wolf"
        self._build_ui()
        self._refresh_profile_combo()
        self._refresh_scheduler_profile_combo()
        self._refresh_scheduler_view()
        self._refresh_environment_badge()
        self._refresh_dashboard()
        self._apply_theme(self.current_theme_key)
        self._close_session_preview()
        self._set_running_state(False)
        self._set_core_running_state(False)
        self.scheduler.start()
        self.dashboard_timer.start()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(12)

        root.addWidget(self._build_header())
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("workspaceSplitter")
        splitter.setHandleWidth(1)

        sidebar = self._build_sidebar()
        center = self._build_center_workspace()
        right = self._build_context_panel()

        splitter.addWidget(sidebar)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([248, 980, 360])

        root.addWidget(splitter, stretch=1)

    def _build_sidebar(self) -> QFrame:
        rail = QFrame()
        rail.setObjectName("sidebarRail")
        rail.setMinimumWidth(222)
        rail.setMaximumWidth(280)
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        brand = QLabel("WITCHER COMMAND CENTER")
        brand.setObjectName("sidebarBrand")
        brand.setWordWrap(True)
        layout.addWidget(brand)

        caption = QLabel("TACTICAL NAVIGATION")
        caption.setObjectName("sidebarCaption")
        layout.addWidget(caption)

        nav_items = [
            "Profiles",
            "Session Window",
            "Content Desk",
            "Performance",
            "AI Studio",
            "Audit / Timeline",
            "Settings",
        ]
        self.nav_buttons: List[QPushButton] = []
        for item in nav_items:
            button = QPushButton(item)
            button.setObjectName("sidebarNavButton")
            button.clicked.connect(lambda _checked=False, label=item: self._focus_section(label))
            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addSpacing(6)
        stats_caption = QLabel("SYSTEM SNAPSHOT")
        stats_caption.setObjectName("sidebarCaption")
        layout.addWidget(stats_caption)

        self.sidebar_profiles_badge = QLabel("Профили: 0")
        self.sidebar_profiles_badge.setObjectName("smallTag")
        self.sidebar_queue_badge = QLabel("Очередь: 0")
        self.sidebar_queue_badge.setObjectName("smallTag")
        self.sidebar_schedule_badge = QLabel("Задачи: 0")
        self.sidebar_schedule_badge.setObjectName("smallTag")
        layout.addWidget(self.sidebar_profiles_badge)
        layout.addWidget(self.sidebar_queue_badge)
        layout.addWidget(self.sidebar_schedule_badge)

        layout.addStretch(1)
        safety = QLabel("Assistive mode only.\nNo stealth/evasion behavior.")
        safety.setObjectName("sidebarSafety")
        safety.setWordWrap(True)
        layout.addWidget(safety)
        return rail

    def _build_center_workspace(self) -> QWidget:
        self.workspace_scroll = QScrollArea()
        self.workspace_scroll.setObjectName("mainScroll")
        self.workspace_scroll.setWidgetResizable(True)
        self.workspace_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.workspace_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.workspace_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("scrollContent")
        grid = QGridLayout(content)
        grid.setContentsMargins(4, 4, 6, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.drop_zone = ProfileDropZone()
        self.drop_zone.profile_parsed.connect(self._on_profile_parsed)
        self.drop_zone.log_signal.connect(self._append_log)
        grid.addWidget(self.drop_zone, 0, 0, 1, 2)
        self._workspace_sections["Session Window"] = self.drop_zone

        connection_box = self._build_connection_box()
        session_box = self._build_session_window_box()
        grid.addWidget(connection_box, 1, 0)
        grid.addWidget(session_box, 1, 1)

        profiles_box = self._build_profiles_box()
        scheduler_box = self._build_scheduler_box()
        grid.addWidget(profiles_box, 2, 0)
        grid.addWidget(scheduler_box, 2, 1)
        self._workspace_sections["Profiles"] = profiles_box

        content_box = self._build_scenario_box()
        upload_box = self._build_upload_box()
        grid.addWidget(content_box, 3, 0)
        grid.addWidget(upload_box, 3, 1)
        self._workspace_sections["Content Desk"] = content_box

        runtime_box = self._build_runtime_box()
        core_box = self._build_core_box()
        grid.addWidget(runtime_box, 4, 0)
        grid.addWidget(core_box, 4, 1)
        self._workspace_sections["Settings"] = runtime_box

        bootstrap_box = self._build_bootstrap_box()
        controls_box = self._build_controls_box()
        grid.addWidget(bootstrap_box, 5, 0)
        grid.addWidget(controls_box, 5, 1)

        self.workspace_scroll.setWidget(content)
        return self.workspace_scroll

    def _build_context_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("contextPanel")
        frame.setMinimumWidth(328)
        frame.setMaximumWidth(420)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setObjectName("contextScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        container.setObjectName("contextContent")
        col = QVBoxLayout(container)
        col.setContentsMargins(4, 4, 4, 8)
        col.setSpacing(10)

        perf_box = self._build_performance_overview_box()
        dashboard_box = self._build_dashboard_box()
        top_box = self._build_top_content_box()
        weak_box = self._build_weak_content_box()
        reco_box = self._build_recommendations_box()
        ai_box = self._build_ai_studio_box()
        log_box = self._build_log_panel()

        col.addWidget(perf_box)
        col.addWidget(dashboard_box)
        col.addWidget(top_box)
        col.addWidget(weak_box)
        col.addWidget(reco_box)
        col.addWidget(ai_box)
        col.addWidget(log_box)
        col.addStretch(1)

        self._workspace_sections["Performance"] = perf_box
        self._workspace_sections["AI Studio"] = ai_box
        self._workspace_sections["Audit / Timeline"] = log_box

        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)
        return frame

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        self.medallion_badge = QLabel("ВОЛК")
        self.medallion_badge.setObjectName("medallionBadge")
        self.medallion_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.medallion_badge.setFixedSize(64, 64)
        layout.addWidget(self.medallion_badge)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title = QLabel("WITCHER COMMAND DECK")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Premium short-form operations hub: profiles, sessions, analytics, AI assist.")
        subtitle.setObjectName("subtitleLabel")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        status_column = QVBoxLayout()
        status_column.setSpacing(6)

        self.status_chip = QLabel("Ожидание")
        self.status_chip.setObjectName("statusChip")
        self.status_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_chip.setMinimumWidth(180)
        status_column.addWidget(self.status_chip)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        self.global_profiles_chip = QLabel("Профили: 0")
        self.global_profiles_chip.setObjectName("smallTag")
        self.global_queue_chip = QLabel("Очередь: 0")
        self.global_queue_chip.setObjectName("smallTag")
        self.global_mode_chip = QLabel("Режим: manual")
        self.global_mode_chip.setObjectName("smallTag")
        status_row.addWidget(self.global_profiles_chip)
        status_row.addWidget(self.global_queue_chip)
        status_row.addWidget(self.global_mode_chip)
        status_column.addLayout(status_row)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(6)
        theme_caption = QLabel("Тема:")
        theme_caption.setObjectName("themeCaption")

        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("themeCombo")
        for key in ("wolf", "nilfgaard", "skellige"):
            self.theme_combo.addItem(THEME_NAMES[key], userData=key)
        self.theme_combo.setCurrentText(THEME_NAMES[self.current_theme_key])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

        theme_row.addWidget(theme_caption)
        theme_row.addWidget(self.theme_combo)
        right_col.addLayout(theme_row)
        status_column_widget = QWidget()
        right_col.addWidget(status_column_widget)
        status_column_widget.setLayout(status_column)
        status_column_widget.setObjectName("headerStatusWrap")

        layout.addLayout(title_col, stretch=1)
        layout.addLayout(right_col)
        return frame

    def _on_theme_changed(self, display_name: str) -> None:
        for key, label in THEME_NAMES.items():
            if label == display_name:
                self.current_theme_key = key
                break
        self._apply_theme(self.current_theme_key)
        if hasattr(self, "log_edit"):
            self._append_log(f"Тема изменена: {display_name}")

    def _build_bootstrap_box(self) -> QGroupBox:
        box = QGroupBox("Setup Wizard")
        box.setObjectName("panel")
        layout = QHBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(8)

        self.environment_status_label = QLabel("Проверка окружения...")
        self.environment_status_label.setObjectName("smallTag")

        self.run_wizard_button = QPushButton("Мастер Настройки")
        self.run_wizard_button.clicked.connect(self._open_first_run_wizard)
        refresh_button = QPushButton("Обновить статус")
        refresh_button.clicked.connect(self._refresh_environment_badge)

        layout.addWidget(self.environment_status_label, stretch=1)
        layout.addWidget(self.run_wizard_button)
        layout.addWidget(refresh_button)
        return box

    def _build_profiles_box(self) -> QGroupBox:
        box = QGroupBox("Profiles")
        box.setObjectName("panel")
        layout = QGridLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)
        layout.setColumnStretch(1, 1)

        self.profile_combo = QComboBox()
        self.profile_combo.setPlaceholderText("Выбери профиль")
        self.profile_name_input = QLineEdit()
        self.profile_name_input.setPlaceholderText("Имя профиля для сохранения")
        self.profile_combo.currentTextChanged.connect(self.profile_name_input.setText)

        apply_button = QPushButton("Применить")
        save_button = QPushButton("Сохранить как")
        update_button = QPushButton("Обновить")
        delete_button = QPushButton("Удалить")

        apply_button.clicked.connect(self._apply_selected_profile)
        save_button.clicked.connect(self._save_profile_as)
        update_button.clicked.connect(self._update_selected_profile)
        delete_button.clicked.connect(self._delete_selected_profile)

        layout.addWidget(QLabel("Сохраненные профили:"), 0, 0)
        layout.addWidget(self.profile_combo, 0, 1)
        layout.addWidget(apply_button, 0, 2)

        layout.addWidget(QLabel("Имя нового/текущего:"), 1, 0)
        layout.addWidget(self.profile_name_input, 1, 1)
        row_buttons = QWidget()
        row_buttons_layout = QHBoxLayout(row_buttons)
        row_buttons_layout.setContentsMargins(0, 0, 0, 0)
        row_buttons_layout.setSpacing(6)
        row_buttons_layout.addWidget(save_button)
        row_buttons_layout.addWidget(update_button)
        row_buttons_layout.addWidget(delete_button)
        layout.addWidget(row_buttons, 1, 2)
        return box

    def _build_scheduler_box(self) -> QGroupBox:
        box = QGroupBox("Session Queue")
        box.setObjectName("panel")
        layout = QGridLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        self.schedule_name_input = QLineEdit("Контракт")
        self.schedule_profile_combo = QComboBox()
        self.schedule_time_edit = QTimeEdit(QTime.currentTime())
        self.schedule_time_edit.setDisplayFormat("HH:mm")
        self.schedule_time_edit.setObjectName("scheduleTimeEdit")

        layout.addWidget(QLabel("Название задачи:"), 0, 0)
        layout.addWidget(self.schedule_name_input, 0, 1)
        layout.addWidget(QLabel("Профиль:"), 0, 2)
        layout.addWidget(self.schedule_profile_combo, 0, 3)

        layout.addWidget(QLabel("Время запуска:"), 1, 0)
        layout.addWidget(self.schedule_time_edit, 1, 1)

        day_row = QWidget()
        day_layout = QHBoxLayout(day_row)
        day_layout.setContentsMargins(0, 0, 0, 0)
        day_layout.setSpacing(4)
        self.day_checkboxes: Dict[int, QCheckBox] = {}
        for day in range(7):
            checkbox = QCheckBox(WEEKDAY_LABELS_RU[day])
            checkbox.setChecked(day < 5)
            self.day_checkboxes[day] = checkbox
            day_layout.addWidget(checkbox)
        layout.addWidget(QLabel("Дни недели:"), 1, 2)
        layout.addWidget(day_row, 1, 3)

        add_task_button = QPushButton("Добавить задачу")
        remove_task_button = QPushButton("Удалить задачу")
        queue_now_button = QPushButton("В очередь сейчас")
        clear_queue_button = QPushButton("Очистить очередь")
        add_task_button.clicked.connect(self._add_scheduler_task)
        remove_task_button.clicked.connect(self._remove_scheduler_task)
        queue_now_button.clicked.connect(self._queue_current_run)
        clear_queue_button.clicked.connect(self._clear_queue)

        action_row = QWidget()
        action_row_layout = QHBoxLayout(action_row)
        action_row_layout.setContentsMargins(0, 0, 0, 0)
        action_row_layout.setSpacing(6)
        action_row_layout.addWidget(add_task_button)
        action_row_layout.addWidget(remove_task_button)
        action_row_layout.addWidget(queue_now_button)
        action_row_layout.addWidget(clear_queue_button)
        layout.addWidget(action_row, 2, 0, 1, 4)

        self.schedule_list = QListWidget()
        self.schedule_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.schedule_list.setMinimumHeight(88)
        self.schedule_list.itemDoubleClicked.connect(self._toggle_selected_schedule_item)

        self.queue_list = QListWidget()
        self.queue_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.queue_list.setMinimumHeight(88)

        layout.addWidget(QLabel("Задачи по расписанию:"), 3, 0, 1, 2)
        layout.addWidget(QLabel("Очередь запусков:"), 3, 2, 1, 2)
        layout.addWidget(self.schedule_list, 4, 0, 1, 2)
        layout.addWidget(self.queue_list, 4, 2, 1, 2)
        return box

    def _build_dashboard_box(self) -> QGroupBox:
        box = QGroupBox("Performance Overview")
        box.setObjectName("panel")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        self.dashboard_status_label = QLabel("Последнее обновление: -")
        self.dashboard_status_label.setObjectName("smallTag")
        refresh_button = QPushButton("Обновить дашборд")
        refresh_button.clicked.connect(self._refresh_dashboard)
        top.addWidget(self.dashboard_status_label)
        top.addStretch(1)
        top.addWidget(refresh_button)
        layout.addLayout(top)

        self.dashboard_table = QTableWidget(0, 2)
        self.dashboard_table.setHorizontalHeaderLabels(["Метрика", "Значение"])
        self.dashboard_table.verticalHeader().setVisible(False)
        self.dashboard_table.horizontalHeader().setStretchLastSection(True)
        self.dashboard_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dashboard_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.dashboard_table.setMinimumHeight(180)
        layout.addWidget(self.dashboard_table)

        chart_row = QHBoxLayout()
        chart_row.setSpacing(8)
        self.likes_chart = MiniLineChart("Лайки (динамика)", "#d4ae67")
        self.followers_chart = MiniLineChart("Подписчики (динамика)", "#7cc19c")
        self.plan_chart = MiniLineChart("Приоритет плана core", "#8ab8df")
        chart_row.addWidget(self.likes_chart, stretch=1)
        chart_row.addWidget(self.followers_chart, stretch=1)
        chart_row.addWidget(self.plan_chart, stretch=1)
        layout.addLayout(chart_row)
        return box

    def _build_session_window_box(self) -> QGroupBox:
        box = QGroupBox("Session Window")
        box.setObjectName("panel")
        layout = QHBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(12)

        self.session_preview = SessionViewportFrame()
        layout.addWidget(self.session_preview, stretch=0)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        self.session_status_label = QLabel("Статус: disconnected")
        self.session_status_label.setObjectName("smallTag")
        self.session_source_label = QLabel("Источник: не подключен")
        self.session_source_label.setObjectName("smallTag")
        self.session_mode_label = QLabel("Режим: manual")
        self.session_mode_label.setObjectName("smallTag")
        right_col.addWidget(self.session_status_label)
        right_col.addWidget(self.session_source_label)
        right_col.addWidget(self.session_mode_label)

        controls = QHBoxLayout()
        controls.setSpacing(6)
        self.session_open_btn = QPushButton("Открыть 9:16")
        self.session_close_btn = QPushButton("Закрыть")
        self.session_attach_btn = QPushButton("Привязать source")
        self.session_open_btn.clicked.connect(self._open_session_preview)
        self.session_close_btn.clicked.connect(self._close_session_preview)
        self.session_attach_btn.clicked.connect(self._attach_session_preview_source)
        controls.addWidget(self.session_open_btn)
        controls.addWidget(self.session_close_btn)
        controls.addWidget(self.session_attach_btn)
        right_col.addLayout(controls)

        right_col.addStretch(1)
        layout.addLayout(right_col, stretch=1)
        return box

    def _build_performance_overview_box(self) -> QGroupBox:
        box = QGroupBox("Performance Snapshot")
        box.setObjectName("panel")
        layout = QGridLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(8)

        self.metric_watch_tile = MetricTile("Просмотры")
        self.metric_engagement_tile = MetricTile("Вовлечение")
        self.metric_momentum_tile = MetricTile("Momentum")
        self.metric_core_health_tile = MetricTile("Core Health")

        layout.addWidget(self.metric_watch_tile, 0, 0)
        layout.addWidget(self.metric_engagement_tile, 0, 1)
        layout.addWidget(self.metric_momentum_tile, 1, 0)
        layout.addWidget(self.metric_core_health_tile, 1, 1)
        return box

    def _build_top_content_box(self) -> QGroupBox:
        box = QGroupBox("Top Content")
        box.setObjectName("panel")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(6)
        self.top_content_list = QListWidget()
        self.top_content_list.setMinimumHeight(110)
        self.top_content_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.top_content_list)
        return box

    def _build_weak_content_box(self) -> QGroupBox:
        box = QGroupBox("Weak Content")
        box.setObjectName("panel")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(6)
        self.weak_content_list = QListWidget()
        self.weak_content_list.setMinimumHeight(96)
        self.weak_content_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.weak_content_list)
        return box

    def _build_recommendations_box(self) -> QGroupBox:
        box = QGroupBox("Recommendations")
        box.setObjectName("panel")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(6)
        self.recommendations_list = QListWidget()
        self.recommendations_list.setMinimumHeight(96)
        self.recommendations_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.recommendations_list)
        return box

    def _build_ai_studio_box(self) -> QGroupBox:
        box = QGroupBox("AI Studio")
        box.setObjectName("panel")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(8)

        self.ai_perception_tag = QLabel("Perception: waiting for data")
        self.ai_perception_tag.setObjectName("smallTag")
        layout.addWidget(self.ai_perception_tag)

        self.ai_eval_output = QPlainTextEdit()
        self.ai_eval_output.setReadOnly(True)
        self.ai_eval_output.setPlaceholderText("Content evaluation preview...")
        self.ai_eval_output.setFixedHeight(92)
        layout.addWidget(self.ai_eval_output)

        self.ai_brief_output = QPlainTextEdit()
        self.ai_brief_output.setReadOnly(True)
        self.ai_brief_output.setPlaceholderText("Video brief preview...")
        self.ai_brief_output.setFixedHeight(92)
        layout.addWidget(self.ai_brief_output)

        self.ai_learning_tag = QLabel("Learning summary: no feedback yet")
        self.ai_learning_tag.setObjectName("smallTag")
        layout.addWidget(self.ai_learning_tag)
        return box

    def _refresh_environment_badge(self) -> None:
        health = inspect_environment(self.app_root)
        if health.all_ok:
            self.environment_status_label.setText("Окружение готово: venv, зависимости и Chromium в порядке")
            return

        problems = [item.title for item in health.checks if not item.ok]
        self.environment_status_label.setText("Требуется настройка: " + ", ".join(problems))

    def _open_first_run_wizard(self) -> None:
        dialog = FirstRunWizardDialog(self.app_root, self)
        dialog.setup_completed.connect(lambda _ok: self._refresh_environment_badge())
        dialog.exec()

    def _refresh_profile_combo(self) -> None:
        current_name = self.profile_combo.currentData() if hasattr(self, "profile_combo") else None
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for name in self.profile_store.names():
            self.profile_combo.addItem(name, userData=name)
        self.profile_combo.blockSignals(False)

        if current_name:
            index = self.profile_combo.findData(current_name)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
        self._refresh_global_badges()

    def _refresh_scheduler_profile_combo(self) -> None:
        current = self.schedule_profile_combo.currentData() if hasattr(self, "schedule_profile_combo") else None
        self.schedule_profile_combo.blockSignals(True)
        self.schedule_profile_combo.clear()
        self.schedule_profile_combo.addItem("Текущие настройки", userData="")
        for name in self.profile_store.names():
            self.schedule_profile_combo.addItem(name, userData=name)
        self.schedule_profile_combo.blockSignals(False)

        if current is not None:
            index = self.schedule_profile_combo.findData(current)
            if index >= 0:
                self.schedule_profile_combo.setCurrentIndex(index)

    def _save_profile_as(self) -> None:
        name = self.profile_name_input.text().strip()
        if not name:
            text, ok = QInputDialog.getText(self, "Сохранить профиль", "Введите имя профиля:")
            if not ok:
                return
            name = text.strip()
        if not name:
            QMessageBox.warning(self, "Профиль", "Имя профиля не может быть пустым.")
            return

        payload = self._collect_form_payload()
        self.profile_store.upsert(name, payload)
        self.profile_name_input.setText(name)
        self._refresh_profile_combo()
        self._refresh_scheduler_profile_combo()
        self._append_log(f"Профиль сохранен: {name}")

    def _update_selected_profile(self) -> None:
        name = str(self.profile_combo.currentData() or "").strip()
        if not name:
            QMessageBox.information(self, "Профиль", "Сначала выбери профиль для обновления.")
            return
        payload = self._collect_form_payload()
        self.profile_store.upsert(name, payload)
        self.profile_name_input.setText(name)
        self._refresh_profile_combo()
        self._append_log(f"Профиль обновлен: {name}")

    def _apply_selected_profile(self) -> None:
        name = str(self.profile_combo.currentData() or "").strip()
        if not name:
            QMessageBox.information(self, "Профиль", "Нет выбранного профиля.")
            return

        profile = self.profile_store.get(name)
        if not profile:
            QMessageBox.warning(self, "Профиль", f"Профиль не найден: {name}")
            self._refresh_profile_combo()
            return

        self._apply_form_payload(profile.payload)
        self.profile_name_input.setText(name)
        self._append_log(f"Профиль применен: {name}")

    def _delete_selected_profile(self) -> None:
        name = str(self.profile_combo.currentData() or "").strip()
        if not name:
            QMessageBox.information(self, "Профиль", "Нет выбранного профиля.")
            return

        if QMessageBox.question(self, "Удалить профиль", f"Удалить профиль '{name}'?") != QMessageBox.StandardButton.Yes:
            return

        if self.profile_store.delete(name):
            self._refresh_profile_combo()
            self._refresh_scheduler_profile_combo()
            self._append_log(f"Профиль удален: {name}")

    def _selected_weekdays(self) -> List[int]:
        days = [day for day, checkbox in self.day_checkboxes.items() if checkbox.isChecked()]
        return sorted(days or list(range(7)))

    def _add_scheduler_task(self) -> None:
        profile_name = str(self.schedule_profile_combo.currentData() or "").strip()
        selected_time = self.schedule_time_edit.time()
        task = self.scheduler.add_task(
            name=self.schedule_name_input.text().strip() or "Контракт",
            profile_name=profile_name,
            hour=selected_time.hour(),
            minute=selected_time.minute(),
            weekdays=self._selected_weekdays(),
        )
        self._append_log(f"Добавлена задача расписания: {task.name} ({task.schedule_label()})")
        self._refresh_scheduler_view()

    def _remove_scheduler_task(self) -> None:
        selected = self.schedule_list.currentItem()
        if selected is None:
            QMessageBox.information(self, "Планировщик", "Выбери задачу для удаления.")
            return

        task_id = str(selected.data(Qt.ItemDataRole.UserRole) or "")
        if not task_id:
            return

        if self.scheduler.remove_task(task_id):
            self._append_log("Задача расписания удалена.")
            self._refresh_scheduler_view()

    def _toggle_selected_schedule_item(self, item: QListWidgetItem) -> None:
        task_id = str(item.data(Qt.ItemDataRole.UserRole) or "")
        enabled = bool(item.data(Qt.ItemDataRole.UserRole + 1))
        if not task_id:
            return
        self.scheduler.set_task_enabled(task_id, not enabled)
        self._refresh_scheduler_view()

    def _refresh_scheduler_view(self) -> None:
        self.schedule_list.clear()
        for task in self.scheduler.list_tasks():
            state = "ON" if task.enabled else "OFF"
            profile_label = task.profile_name or "текущие настройки"
            text = f"[{state}] {task.name} -> {task.schedule_label()} | {profile_label}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, task.task_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, task.enabled)
            self.schedule_list.addItem(item)
        self._refresh_queue_view()
        self._refresh_global_badges()

    def _refresh_queue_view(self) -> None:
        self.queue_list.clear()
        for index, item in enumerate(self.run_queue.items(), start=1):
            profile_label = item.payload.get("profile_name") or "текущие"
            name = item.payload.get("name") or "Контракт"
            self.queue_list.addItem(f"{index}. [{item.source}] {name} ({profile_label})")
        self._refresh_global_badges()

    def _queue_current_run(self) -> None:
        profile_name = str(self.schedule_profile_combo.currentData() or "").strip()
        payload = self._resolve_payload_for_profile(profile_name)
        queue_item = self.run_queue.enqueue(
            source="manual",
            payload={
                "name": self.schedule_name_input.text().strip() or "Контракт",
                "profile_name": profile_name,
                "payload": payload,
            },
        )
        self._append_log(f"Добавлено в очередь: {queue_item.queue_id[:8]}")
        self._refresh_queue_view()
        self._try_run_next_from_queue()

    def _clear_queue(self) -> None:
        self.run_queue.clear()
        self._refresh_queue_view()
        self._append_log("Очередь запусков очищена.")

    def _on_scheduled_task_due(self, payload: dict) -> None:
        profile_name = str(payload.get("profile_name", "")).strip()
        form_payload = self._resolve_payload_for_profile(profile_name)
        queue_item = self.run_queue.enqueue(
            source="schedule",
            payload={
                "name": str(payload.get("name", "Контракт")),
                "profile_name": profile_name,
                "payload": form_payload,
            },
        )
        self._append_log(
            f"Триггер расписания: {payload.get('name', 'Контракт')} "
            f"({payload.get('scheduled_for', '-')}) -> очередь #{queue_item.queue_id[:8]}"
        )
        self._refresh_queue_view()
        self._try_run_next_from_queue()

    def _resolve_payload_for_profile(self, profile_name: str) -> Dict[str, object]:
        if not profile_name:
            return self._collect_form_payload()
        profile = self.profile_store.get(profile_name)
        if profile:
            return dict(profile.payload)
        return self._collect_form_payload()

    def _try_run_next_from_queue(self) -> None:
        if self.worker and self.worker.isRunning():
            return
        item = self.run_queue.pop()
        if item is None:
            self._refresh_queue_view()
            return

        payload = item.payload.get("payload", {})
        if not isinstance(payload, dict):
            self._append_log("Очередь: некорректный payload, пропуск.")
            self._try_run_next_from_queue()
            return

        settings = self._settings_from_payload(payload)
        source_name = f"очередь/{item.source}"
        started = self._start_worker_with_settings(settings, source=source_name)
        self._refresh_queue_view()
        if not started:
            self._try_run_next_from_queue()

    def _refresh_dashboard(self) -> None:
        output_dir = Path(self.output_dir_input.text().strip() or "output")
        core_root = Path(self.core_root_input.text().strip() or self.core_root)
        snapshot = load_dashboard_snapshot(output_dir=output_dir, core_root=core_root)

        self.dashboard_table.setRowCount(len(snapshot.rows))
        for row_index, (name, value) in enumerate(snapshot.rows):
            self.dashboard_table.setItem(row_index, 0, QTableWidgetItem(name))
            self.dashboard_table.setItem(row_index, 1, QTableWidgetItem(value))

        self.likes_chart.set_values(snapshot.likes_series)
        self.followers_chart.set_values(snapshot.followers_series)
        self.plan_chart.set_values(snapshot.plan_priority_series)
        self.dashboard_status_label.setText(f"Последнее обновление: {datetime.now().strftime('%H:%M:%S')}")
        self._refresh_performance_tiles(snapshot)
        self._refresh_content_insights(snapshot, output_dir)
        self._refresh_ai_studio(snapshot, core_root)
        self._refresh_global_badges()

    def _refresh_performance_tiles(self, snapshot) -> None:
        rows = list(snapshot.rows or [])
        watch_count = self._safe_int_from_metric(rows, 0)
        comments_count = self._safe_int_from_metric(rows, 1)
        profile_visits = self._safe_int_from_metric(rows, 2)
        uploads = self._safe_int_from_metric(rows, 3)
        core_steps = self._safe_int_from_metric(rows, 5)
        core_health = self._safe_text_from_metric(rows, 6)

        engagement_proxy = comments_count + profile_visits + uploads
        momentum = "Rising" if len(snapshot.likes_series) > 1 and snapshot.likes_series[-1] >= snapshot.likes_series[0] else "Stable"
        momentum_delta = f"{len(snapshot.likes_series)} pts" if snapshot.likes_series else "No data"

        self.metric_watch_tile.set_value(str(watch_count), f"events: {len(snapshot.likes_series)}")
        self.metric_engagement_tile.set_value(str(engagement_proxy), f"comments: {comments_count}")
        self.metric_momentum_tile.set_value(momentum, momentum_delta)
        self.metric_core_health_tile.set_value(core_health, f"plan steps: {core_steps}")

    def _refresh_content_insights(self, snapshot, output_dir: Path) -> None:
        stats_path = output_dir / "session_stats.jsonl"
        content_rows: List[Dict[str, object]] = []
        if stats_path.exists():
            for raw in stats_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if not isinstance(payload, dict):
                    continue
                video_stats = payload.get("video_stats") if isinstance(payload.get("video_stats"), dict) else payload
                if not isinstance(video_stats, dict):
                    continue
                likes = self._compact_to_float(video_stats.get("likes"))
                views = self._compact_to_float(video_stats.get("views"))
                if likes is None and views is None:
                    continue
                content_rows.append(
                    {
                        "label": str(video_stats.get("url") or payload.get("profile_url") or "content_item"),
                        "likes": likes or 0.0,
                        "views": views or 0.0,
                    }
                )

        if not content_rows and snapshot.likes_series:
            content_rows = [
                {"label": f"auto_content_{idx + 1}", "likes": float(value), "views": float(value) * 10.0}
                for idx, value in enumerate(snapshot.likes_series[-8:])
            ]

        content_rows.sort(key=lambda item: float(item.get("likes", 0.0)), reverse=True)

        self.top_content_list.clear()
        self.weak_content_list.clear()
        self.recommendations_list.clear()

        for idx, item in enumerate(content_rows[:5], start=1):
            label = str(item.get("label", "content"))
            likes = int(float(item.get("likes", 0.0)))
            views = int(float(item.get("views", 0.0)))
            self.top_content_list.addItem(f"{idx}. {label} | likes: {likes} | views: {views}")

        for idx, item in enumerate(list(reversed(content_rows[-4:])), start=1):
            label = str(item.get("label", "content"))
            likes = int(float(item.get("likes", 0.0)))
            self.weak_content_list.addItem(f"{idx}. {label} | weak likes: {likes}")

        if content_rows:
            best = content_rows[0]
            worst = content_rows[-1]
            self.recommendations_list.addItem(
                f"Repeat angle from top item: {str(best.get('label', 'content'))[:48]}"
            )
            self.recommendations_list.addItem(
                f"Rework weak item: {str(worst.get('label', 'content'))[:48]}"
            )
        else:
            self.recommendations_list.addItem("Collect at least 5 content snapshots to unlock recommendations.")

        self.recommendations_list.addItem("Test 2 hook variants in first 2 seconds.")
        self.recommendations_list.addItem("Schedule strongest format in evening window.")

    def _refresh_ai_studio(self, snapshot, core_root: Path) -> None:
        perception_count = len(snapshot.likes_series) + len(snapshot.followers_series)
        self.ai_perception_tag.setText(f"Perception summary: {perception_count} visual signals in timeline")

        eval_lines = [
            "Quality Evaluation",
            "- Hook clarity: medium",
            "- Text readability: good",
            "- Scene density: controlled",
            "- CTA presence: requires manual check",
        ]
        self.ai_eval_output.setPlainText("\n".join(eval_lines))

        brief_lines = [
            "Video Brief Preview",
            "- Goal: boost completion and shares",
            "- Format: short tactical tutorial",
            "- Duration: 20-35 sec",
            "- Shot plan: Hook -> Proof -> CTA",
        ]
        plan_path = core_root / "runtime" / "output" / "plan_bundle.json"
        if plan_path.exists():
            try:
                payload = json.loads(plan_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    steps = payload.get("steps", [])
                    if isinstance(steps, list) and steps:
                        brief_lines.append(f"- Core actions loaded: {len(steps)}")
            except Exception:
                pass
        self.ai_brief_output.setPlainText("\n".join(brief_lines))

        self.ai_learning_tag.setText(
            f"Learning summary: likes points={len(snapshot.likes_series)}, followers points={len(snapshot.followers_series)}"
        )

    def _safe_int_from_metric(self, rows: List[tuple], index: int) -> int:
        try:
            value = rows[index][1]
        except Exception:
            return 0
        return self._to_int(value, 0)

    def _safe_text_from_metric(self, rows: List[tuple], index: int) -> str:
        try:
            return str(rows[index][1])
        except Exception:
            return "—"

    def _compact_to_float(self, value: object) -> Optional[float]:
        if value is None:
            return None
        text = str(value).strip().replace(" ", "").replace(",", ".")
        if not text:
            return None
        number_part = "".join(ch for ch in text if ch.isdigit() or ch == ".")
        if not number_part:
            return None
        try:
            base = float(number_part)
        except ValueError:
            return None
        suffix = text[-1].upper()
        if suffix == "K":
            base *= 1000
        elif suffix == "M":
            base *= 1_000_000
        elif suffix == "B":
            base *= 1_000_000_000
        return base

    def _refresh_global_badges(self) -> None:
        if not hasattr(self, "sidebar_profiles_badge"):
            return
        profiles_count = len(self.profile_store.names())
        queue_count = len(self.run_queue.items())
        schedules_count = len(self.scheduler.list_tasks()) if hasattr(self, "scheduler") else 0
        mode = "managed" if self.worker and self.worker.isRunning() else "manual"

        self.sidebar_profiles_badge.setText(f"Профили: {profiles_count}")
        self.sidebar_queue_badge.setText(f"Очередь: {queue_count}")
        self.sidebar_schedule_badge.setText(f"Задачи: {schedules_count}")
        self.global_profiles_chip.setText(f"Профили: {profiles_count}")
        self.global_queue_chip.setText(f"Очередь: {queue_count}")
        self.global_mode_chip.setText(f"Режим: {mode}")

    def _focus_section(self, section_name: str) -> None:
        widget = self._workspace_sections.get(section_name)
        if widget is None:
            self._append_log(f"[NAV] {section_name}")
            return
        if hasattr(self, "workspace_scroll"):
            scroll_root = self.workspace_scroll.widget()
            if scroll_root is not None and scroll_root.isAncestorOf(widget):
                self.workspace_scroll.ensureWidgetVisible(widget, 0, 36)
        self._append_log(f"[NAV] Переход к секции: {section_name}")

    def _open_session_preview(self) -> None:
        source = "CDP" if self.cdp_input.text().strip() else "manual"
        self.session_preview.set_state(online=True, status="online", source=source)
        self.session_status_label.setText("Статус: online")
        self.session_source_label.setText(f"Источник: {source}")
        self.session_mode_label.setText("Режим: guided")
        self._append_log("[SESSION] Открыто окно 9:16.")

    def _close_session_preview(self) -> None:
        self.session_preview.set_state(online=False, status="offline", source="not attached")
        self.session_status_label.setText("Статус: disconnected")
        self.session_source_label.setText("Источник: не подключен")
        self.session_mode_label.setText("Режим: manual")
        self._append_log("[SESSION] Окно сессии закрыто.")

    def _attach_session_preview_source(self) -> None:
        source = self.cdp_input.text().strip() or self.profile_url_input.text().strip() or "workspace_source"
        self.session_preview.set_state(online=True, status="attached", source=source[:44])
        self.session_source_label.setText(f"Источник: {source[:52]}")
        self._append_log("[SESSION] Источник привязан к session window.")

    def _collect_form_payload(self) -> Dict[str, object]:
        return {
            "cdp_url": self.cdp_input.text(),
            "profile_url": self.profile_url_input.text(),
            "output_dir": str(Path(self.output_dir_input.text().strip() or "output")),
            "for_you_url": self.for_you_input.text(),
            "watch_enabled": self.watch_checkbox.isChecked(),
            "watch_videos": self.watch_count_spin.value(),
            "collect_stats_enabled": self.collect_stats_checkbox.isChecked(),
            "monitor_enabled": self.monitor_checkbox.isChecked(),
            "comment_enabled": self.comment_checkbox.isChecked(),
            "max_comments": self.comment_limit_spin.value(),
            "comments_text": self.comments_edit.toPlainText(),
            "visit_profiles_enabled": self.visit_profiles_checkbox.isChecked(),
            "max_profiles_to_visit": self.profiles_limit_spin.value(),
            "profiles_text": self.profiles_edit.toPlainText(),
            "upload_enabled": self.upload_checkbox.isChecked(),
            "upload_file": self.video_file_input.text(),
            "upload_caption": self.caption_input.text(),
            "publish_upload": self.publish_checkbox.isChecked(),
            "min_delay_seconds": float(self.min_delay_spin.value()),
            "max_delay_seconds": float(self.max_delay_spin.value()),
            "retry_attempts": self.retry_attempts_spin.value(),
            "action_timeout_seconds": float(self.action_timeout_spin.value()),
            "selector_timeout_ms": self.selector_timeout_spin.value(),
            "health_check_enabled": self.health_check_checkbox.isChecked(),
            "strict_health_check": self.strict_health_checkbox.isChecked(),
        }

    def _apply_form_payload(self, payload: Dict[str, object]) -> None:
        self.cdp_input.setText(str(payload.get("cdp_url", "")))
        self.profile_url_input.setText(str(payload.get("profile_url", "https://www.tiktok.com/@username")))
        self.output_dir_input.setText(str(payload.get("output_dir", str(Path.cwd() / "output"))))
        self.for_you_input.setText(str(payload.get("for_you_url", "https://www.tiktok.com/foryou")))

        self.watch_checkbox.setChecked(bool(payload.get("watch_enabled", True)))
        self.watch_count_spin.setValue(self._to_int(payload.get("watch_videos"), 10))
        self.collect_stats_checkbox.setChecked(bool(payload.get("collect_stats_enabled", True)))
        self.monitor_checkbox.setChecked(bool(payload.get("monitor_enabled", True)))

        self.comment_checkbox.setChecked(bool(payload.get("comment_enabled", False)))
        self.comment_limit_spin.setValue(self._to_int(payload.get("max_comments"), 2))
        self.comments_edit.setPlainText(str(payload.get("comments_text", "")))

        self.visit_profiles_checkbox.setChecked(bool(payload.get("visit_profiles_enabled", False)))
        self.profiles_limit_spin.setValue(self._to_int(payload.get("max_profiles_to_visit"), 5))
        self.profiles_edit.setPlainText(str(payload.get("profiles_text", "")))

        self.upload_checkbox.setChecked(bool(payload.get("upload_enabled", False)))
        self.video_file_input.setText(str(payload.get("upload_file", "")))
        self.caption_input.setText(str(payload.get("upload_caption", "")))
        self.publish_checkbox.setChecked(bool(payload.get("publish_upload", False)))

        self.min_delay_spin.setValue(self._to_float(payload.get("min_delay_seconds"), 3.0))
        self.max_delay_spin.setValue(self._to_float(payload.get("max_delay_seconds"), 8.0))
        self.retry_attempts_spin.setValue(self._to_int(payload.get("retry_attempts"), 2))
        self.action_timeout_spin.setValue(self._to_float(payload.get("action_timeout_seconds"), 12.0))
        self.selector_timeout_spin.setValue(self._to_int(payload.get("selector_timeout_ms"), 4500))
        self.health_check_checkbox.setChecked(bool(payload.get("health_check_enabled", True)))
        self.strict_health_checkbox.setChecked(bool(payload.get("strict_health_check", False)))

    def _build_log_panel(self) -> QGroupBox:
        box = QGroupBox("Audit / Timeline")
        box.setObjectName("panel")
        box.setMinimumHeight(250)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        mode_label = QLabel("Observability feed")
        mode_label.setObjectName("smallTag")
        clear_button = QPushButton("Очистить таймлайн")

        self.log_edit = QTextEdit()
        clear_button.clicked.connect(self.log_edit.clear)
        top.addWidget(mode_label)
        top.addStretch(1)
        top.addWidget(clear_button)
        layout.addLayout(top)

        self.log_edit.setReadOnly(True)
        self.log_edit.setObjectName("logOutput")
        self.log_edit.setPlaceholderText("Timeline событий, ошибок, AI решений и статуса профиля...")
        layout.addWidget(self.log_edit, stretch=1)
        return box

    def _build_connection_box(self) -> QGroupBox:
        box = QGroupBox("Profile Connection")
        box.setObjectName("panel")
        form = QFormLayout(box)
        form.setContentsMargins(12, 22, 12, 12)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.cdp_input = QLineEdit()
        self.cdp_input.setPlaceholderText("http://127.0.0.1:9222 или ws://127.0.0.1:9222/devtools/browser/...")
        form.addRow("CDP URL:", self.cdp_input)

        self.profile_url_input = QLineEdit("https://www.tiktok.com/@username")
        form.addRow("URL профиля:", self.profile_url_input)

        self.for_you_input = QLineEdit("https://www.tiktok.com/foryou")
        form.addRow("URL ленты:", self.for_you_input)

        return box

    def _build_scenario_box(self) -> QGroupBox:
        box = QGroupBox("Content Desk")
        box.setObjectName("panel")
        grid = QGridLayout(box)
        grid.setContentsMargins(12, 22, 12, 12)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 2)

        self.watch_checkbox = QCheckBox("Смотреть ленту")
        self.watch_checkbox.setChecked(True)
        self.watch_count_spin = QSpinBox()
        self.watch_count_spin.setRange(0, 1000)
        self.watch_count_spin.setValue(10)

        self.collect_stats_checkbox = QCheckBox("Собирать метрики видео")
        self.collect_stats_checkbox.setChecked(True)

        self.monitor_checkbox = QCheckBox("Собирать метрики профиля")
        self.monitor_checkbox.setChecked(True)

        self.comment_checkbox = QCheckBox("Писать комментарии")
        self.comment_checkbox.setChecked(False)
        self.comment_limit_spin = QSpinBox()
        self.comment_limit_spin.setRange(0, 200)
        self.comment_limit_spin.setValue(2)
        self.comments_edit = QPlainTextEdit()
        self.comments_edit.setObjectName("commentsEdit")
        self.comments_edit.setPlaceholderText("Один комментарий на строку")
        self.comments_edit.setFixedHeight(120)

        self.visit_profiles_checkbox = QCheckBox("Посещать профили")
        self.visit_profiles_checkbox.setChecked(False)
        self.profiles_limit_spin = QSpinBox()
        self.profiles_limit_spin.setRange(0, 500)
        self.profiles_limit_spin.setValue(5)
        self.profiles_edit = QPlainTextEdit()
        self.profiles_edit.setObjectName("profilesEdit")
        self.profiles_edit.setPlaceholderText("URL профиля TikTok, по одному на строку")
        self.profiles_edit.setFixedHeight(120)

        grid.addWidget(self.watch_checkbox, 0, 0)
        grid.addWidget(QLabel("Лимит видео:"), 0, 1)
        grid.addWidget(self.watch_count_spin, 0, 2)
        grid.addWidget(self.collect_stats_checkbox, 1, 0, 1, 2)
        grid.addWidget(self.monitor_checkbox, 1, 2)

        grid.addWidget(self.comment_checkbox, 2, 0)
        grid.addWidget(QLabel("Лимит комментариев:"), 2, 1)
        grid.addWidget(self.comment_limit_spin, 2, 2)
        grid.addWidget(self.comments_edit, 3, 0, 1, 3)

        grid.addWidget(self.visit_profiles_checkbox, 4, 0)
        grid.addWidget(QLabel("Лимит профилей:"), 4, 1)
        grid.addWidget(self.profiles_limit_spin, 4, 2)
        grid.addWidget(self.profiles_edit, 5, 0, 1, 3)
        return box

    def _build_upload_box(self) -> QGroupBox:
        box = QGroupBox("Publish Queue")
        box.setObjectName("panel")
        form = QFormLayout(box)
        form.setContentsMargins(12, 22, 12, 12)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.upload_checkbox = QCheckBox("Включить загрузку видео")
        self.upload_checkbox.setChecked(False)
        form.addRow(self.upload_checkbox)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        self.video_file_input = QLineEdit()
        self.video_file_input.setPlaceholderText("Путь к видеофайлу")
        browse = QPushButton("Выбрать")
        browse.clicked.connect(self._pick_video_file)
        row_layout.addWidget(self.video_file_input)
        row_layout.addWidget(browse)
        form.addRow("Видео:", row)

        self.caption_input = QLineEdit()
        self.caption_input.setPlaceholderText("Описание к видео")
        form.addRow("Описание:", self.caption_input)

        self.publish_checkbox = QCheckBox("Публиковать автоматически")
        self.publish_checkbox.setChecked(False)
        form.addRow(self.publish_checkbox)
        return box

    def _build_runtime_box(self) -> QGroupBox:
        box = QGroupBox("Settings")
        box.setObjectName("panel")
        form = QFormLayout(box)
        form.setContentsMargins(12, 22, 12, 12)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.min_delay_spin = QDoubleSpinBox()
        self.min_delay_spin.setRange(0.5, 300.0)
        self.min_delay_spin.setValue(3.0)
        self.min_delay_spin.setSingleStep(0.5)
        form.addRow("Мин. пауза (сек):", self.min_delay_spin)

        self.max_delay_spin = QDoubleSpinBox()
        self.max_delay_spin.setRange(0.5, 300.0)
        self.max_delay_spin.setValue(8.0)
        self.max_delay_spin.setSingleStep(0.5)
        form.addRow("Макс. пауза (сек):", self.max_delay_spin)

        output_row = QWidget()
        output_layout = QHBoxLayout(output_row)
        output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_dir_input = QLineEdit(str(Path.cwd() / "output"))
        output_browse = QPushButton("Папка")
        output_browse.clicked.connect(self._pick_output_dir)
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(output_browse)
        form.addRow("Путь вывода:", output_row)

        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(1, 10)
        self.retry_attempts_spin.setValue(2)
        form.addRow("Ретраи действий:", self.retry_attempts_spin)

        self.action_timeout_spin = QDoubleSpinBox()
        self.action_timeout_spin.setRange(2.0, 180.0)
        self.action_timeout_spin.setValue(12.0)
        self.action_timeout_spin.setSingleStep(1.0)
        form.addRow("Таймаут шага (сек):", self.action_timeout_spin)

        self.selector_timeout_spin = QSpinBox()
        self.selector_timeout_spin.setRange(500, 30000)
        self.selector_timeout_spin.setSingleStep(250)
        self.selector_timeout_spin.setValue(4500)
        form.addRow("Таймаут селектора (мс):", self.selector_timeout_spin)

        self.health_check_checkbox = QCheckBox("Health-check профиля перед запуском")
        self.health_check_checkbox.setChecked(True)
        form.addRow(self.health_check_checkbox)

        self.strict_health_checkbox = QCheckBox("Останавливать контракт при провале health-check")
        self.strict_health_checkbox.setChecked(False)
        form.addRow(self.strict_health_checkbox)

        return box

    def _build_controls_box(self) -> QGroupBox:
        box = QGroupBox("Contract Controls")
        box.setObjectName("panel")
        layout = QHBoxLayout(box)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(8)

        self.start_button = QPushButton("Старт Контракта")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Стоп")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self._start_worker)
        self.stop_button.clicked.connect(self._stop_worker)

        layout.addWidget(self.start_button, stretch=2)
        layout.addWidget(self.stop_button, stretch=1)
        return box

    def _default_core_root(self) -> Path:
        agent_root = Path(__file__).resolve().parents[1]
        sibling_core = agent_root.parent / "core"
        if sibling_core.exists():
            return sibling_core
        legacy_core = Path(__file__).resolve().parents[1] / "shortform_core"
        return legacy_core

    def _build_core_box(self) -> QGroupBox:
        box = QGroupBox("AI / Core Integration")
        box.setObjectName("panel")
        layout = QGridLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)
        layout.setColumnStretch(1, 1)

        self.core_root_input = QLineEdit(str(self.core_root))
        self.core_root_input.setPlaceholderText("Путь к корню core layer")
        root_pick_button = QPushButton("Папка")
        root_pick_button.clicked.connect(self._pick_core_root)
        layout.addWidget(QLabel("Корень core:"), 0, 0)
        layout.addWidget(self.core_root_input, 0, 1)
        layout.addWidget(root_pick_button, 0, 2)

        self.core_use_live_output = QCheckBox("Использовать текущий TikTok output как источник snapshot")
        self.core_use_live_output.setChecked(True)
        layout.addWidget(self.core_use_live_output, 1, 0, 1, 3)

        self.core_bootstrap_button = QPushButton("Инициализация Core v2")
        self.core_demo_button = QPushButton("Анализ + План Core")
        self.core_show_plan_button = QPushButton("Показать План Core")
        self.core_show_plan_button.clicked.connect(self._show_core_plan)
        self.core_bootstrap_button.clicked.connect(lambda: self._run_core_action("bootstrap"))
        self.core_demo_button.clicked.connect(lambda: self._run_core_action("demo"))

        layout.addWidget(self.core_bootstrap_button, 2, 0)
        layout.addWidget(self.core_demo_button, 2, 1)
        layout.addWidget(self.core_show_plan_button, 2, 2)
        return box

    def _apply_theme(self, theme_key: str) -> None:
        palette = THEME_PRESETS.get(theme_key, THEME_PRESETS["wolf"])
        stylesheet = """
            QWidget#root {
                background-color: __ROOT_BG__;
                color: __TEXT_BASE__;
                font-family: "Bahnschrift", "Segoe UI", sans-serif;
                font-size: 14px;
            }

            QLabel {
                color: __LABEL__;
                font-size: 13px;
            }

            QSplitter#workspaceSplitter::handle {
                background: transparent;
            }

            QScrollArea#mainScroll,
            QWidget#scrollContent,
            QScrollArea#mainScroll QWidget#qt_scrollarea_viewport,
            QScrollArea#contextScroll,
            QWidget#contextContent,
            QScrollArea#contextScroll QWidget#qt_scrollarea_viewport {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                width: 10px;
                background: transparent;
                margin: 2px 0 2px 0;
            }

            QScrollBar::handle:vertical {
                min-height: 30px;
                border-radius: 5px;
                background: rgba(175, 184, 225, 0.35);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }

            QFrame#headerBar {
                border: 1px solid __HEADER_BORDER__;
                border-radius: 22px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 __HEADER_G1__,
                    stop: 0.55 __HEADER_G2__,
                    stop: 1 __HEADER_G3__
                );
            }

            QWidget#headerStatusWrap {
                background: transparent;
            }

            QLabel#medallionBadge {
                border: 1px solid __MEDALLION_BORDER__;
                border-radius: 32px;
                min-width: 64px;
                min-height: 64px;
                max-width: 64px;
                max-height: 64px;
                background-color: __MEDALLION_BG__;
                color: __MEDALLION_TEXT__;
                font-weight: 700;
                font-family: "Bahnschrift", "Segoe UI", sans-serif;
                font-size: 12px;
            }

            QLabel#titleLabel {
                color: __TITLE__;
                font-family: "Bahnschrift", "Segoe UI Semibold", sans-serif;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 0.6px;
            }

            QLabel#subtitleLabel {
                color: __SUBTITLE__;
                font-size: 13px;
            }

            QLabel#themeCaption {
                color: __LABEL__;
                font-weight: 700;
            }

            QComboBox#themeCombo {
                border: 1px solid __INPUT_BORDER__;
                border-radius: 12px;
                padding: 7px 10px;
                min-width: 128px;
                background-color: __INPUT_BG__;
                color: __INPUT_TEXT__;
            }

            QComboBox#themeCombo:hover {
                border-color: __INPUT_FOCUS_BORDER__;
            }

            QComboBox#themeCombo QAbstractItemView {
                border: 1px solid __INPUT_BORDER__;
                background: __INPUT_BG__;
                color: __INPUT_TEXT__;
                selection-background-color: __INPUT_FOCUS_BG__;
                selection-color: __INPUT_TEXT__;
            }

            QLabel#statusChip {
                border: 1px solid __STATUS_BORDER__;
                border-radius: 15px;
                padding: 8px 14px;
                background-color: __STATUS_BG__;
                color: __STATUS_TEXT__;
                font-weight: 700;
                font-size: 13px;
            }

            QLabel#statusChip[state="ready"] {
                background-color: __READY_BG__;
                border-color: __READY_BORDER__;
                color: __READY_TEXT__;
            }

            QLabel#statusChip[state="running"] {
                background-color: __RUNNING_BG__;
                border-color: __RUNNING_BORDER__;
                color: __RUNNING_TEXT__;
            }

            QFrame#sidebarRail {
                border: 1px solid __SIDEBAR_BORDER__;
                border-radius: 22px;
                background-color: __SIDEBAR_BG__;
            }

            QLabel#sidebarBrand {
                color: __TEXT_BASE__;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 0.6px;
            }

            QLabel#sidebarCaption {
                color: __SIDEBAR_CAPTION__;
                font-size: 11px;
                letter-spacing: 0.8px;
                font-weight: 700;
            }

            QLabel#sidebarSafety {
                color: __SIDEBAR_CAPTION__;
                font-size: 11px;
            }

            QPushButton#sidebarNavButton {
                text-align: left;
                border: 1px solid __BORDER_SUBTLE__;
                border-radius: 14px;
                padding: 8px 10px;
                background-color: __SIDEBAR_ITEM_BG__;
                color: __SIDEBAR_ITEM_TEXT__;
                font-weight: 600;
            }

            QPushButton#sidebarNavButton:hover {
                border-color: __BORDER_ACTIVE__;
                background-color: __SIDEBAR_ITEM_HOVER_BG__;
            }

            QFrame#dropZone {
                border: 2px dashed __DROP_BORDER__;
                border-radius: 20px;
                background-color: __DROP_BG__;
            }

            QFrame#dropZone[dragActive="true"] {
                border-color: __DROP_ACTIVE_BORDER__;
                background-color: __DROP_ACTIVE_BG__;
            }

            QLabel#dropTitle {
                color: __DROP_TITLE__;
                font-family: "Bahnschrift", "Segoe UI Semibold", sans-serif;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#dropHint {
                color: __DROP_HINT__;
                font-size: 13px;
            }

            QGroupBox#panel {
                border: 1px solid __PANEL_BORDER__;
                border-radius: 20px;
                margin-top: 8px;
                padding-top: 12px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 __PANEL_G1__,
                    stop: 1 __PANEL_G2__
                );
            }

            QGroupBox#panel::title {
                subcontrol-origin: padding;
                subcontrol-position: top left;
                left: 14px;
                top: 2px;
                padding: 0 10px;
                background-color: __PANEL_TITLE_BG__;
                color: __PANEL_TITLE_TEXT__;
                font-weight: 700;
                font-size: 12px;
                letter-spacing: 0.4px;
            }

            QLabel#smallTag {
                color: __TAG_TEXT__;
                border: 1px solid __TAG_BORDER__;
                border-radius: 11px;
                padding: 5px 9px;
                background-color: __TAG_BG__;
            }

            QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid __INPUT_BORDER__;
                border-radius: 12px;
                background-color: __INPUT_BG__;
                color: __INPUT_TEXT__;
                padding: 7px;
                selection-background-color: __INPUT_FOCUS_BORDER__;
                selection-color: __INPUT_TEXT__;
            }

            QPlainTextEdit#commentsEdit,
            QPlainTextEdit#profilesEdit {
                border-radius: 16px;
                border: 1px solid __INPUT_BORDER__;
                background-color: __INPUT_BG__;
                padding: 8px;
            }

            QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid __INPUT_FOCUS_BORDER__;
                background-color: __INPUT_FOCUS_BG__;
            }

            QTableWidget, QListWidget, QTimeEdit {
                border: 1px solid __INPUT_BORDER__;
                border-radius: 12px;
                background-color: __INPUT_BG__;
                color: __INPUT_TEXT__;
                selection-background-color: __INPUT_FOCUS_BG__;
                selection-color: __INPUT_TEXT__;
            }

            QListWidget::item {
                border-radius: 8px;
                padding: 4px 6px;
                margin: 2px 3px;
            }

            QListWidget::item:hover {
                background-color: rgba(151, 124, 255, 0.14);
            }

            QHeaderView::section {
                background-color: __PANEL_TITLE_BG__;
                color: __PANEL_TITLE_TEXT__;
                border: 1px solid __INPUT_BORDER__;
                padding: 6px;
                font-weight: 700;
            }

            QCheckBox {
                spacing: 8px;
                color: __CHECKBOX_TEXT__;
                min-height: 22px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid __CHECKBOX_BORDER__;
                border-radius: 4px;
                background: __CHECKBOX_BG__;
            }

            QCheckBox::indicator:checked {
                background: __CHECKBOX_CHECKED_BG__;
                border: 1px solid __CHECKBOX_CHECKED_BORDER__;
            }

            QPushButton {
                border: 1px solid __BUTTON_BORDER__;
                border-radius: 13px;
                padding: 8px 12px;
                color: __BUTTON_TEXT__;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 __BUTTON_G1__,
                    stop: 1 __BUTTON_G2__
                );
            }

            QPushButton:hover {
                border-color: __BUTTON_HOVER_BORDER__;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 __BUTTON_HOVER_G1__,
                    stop: 1 __BUTTON_HOVER_G2__
                );
            }

            QPushButton:pressed {
                background-color: __BUTTON_PRESSED__;
            }

            QPushButton:disabled {
                color: __BUTTON_DISABLED_TEXT__;
                border-color: __BUTTON_DISABLED_BORDER__;
                background: __BUTTON_DISABLED_BG__;
            }

            QPushButton#startButton {
                font-size: 14px;
                font-weight: 700;
                border: 1px solid __START_BORDER__;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 __START_G1__, stop: 1 __START_G2__);
            }

            QPushButton#startButton:hover {
                border-color: __START_HOVER_BORDER__;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 __START_HOVER_G1__,
                    stop: 1 __START_HOVER_G2__
                );
            }

            QPushButton#stopButton {
                font-size: 14px;
                font-weight: 700;
                border: 1px solid __STOP_BORDER__;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 __STOP_G1__, stop: 1 __STOP_G2__);
            }

            QPushButton#stopButton:hover {
                border-color: __STOP_HOVER_BORDER__;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 __STOP_HOVER_G1__,
                    stop: 1 __STOP_HOVER_G2__
                );
            }

            QTextEdit#logOutput {
                background-color: __LOG_BG__;
                border: 1px solid __LOG_BORDER__;
                color: __LOG_TEXT__;
                font-family: "Consolas", "Lucida Console", monospace;
                font-size: 13px;
            }

            QFrame#metricTile {
                border: 1px solid __BORDER_SUBTLE__;
                border-radius: 18px;
                background-color: __ELEVATED_PANEL__;
            }

            QLabel#metricTileTitle {
                color: __LABEL__;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.4px;
            }

            QLabel#metricTileValue {
                color: __TEXT_BASE__;
                font-family: "Bahnschrift", "Segoe UI Semibold", sans-serif;
                font-size: 25px;
                font-weight: 700;
            }

            QLabel#metricTileDelta {
                color: __INFO__;
                font-size: 12px;
            }

            QWidget#sessionViewportFrame {
                background: transparent;
            }
            """

        for name, value in palette.items():
            token = "__" + name.upper() + "__"
            stylesheet = stylesheet.replace(token, value)

        self.setStyleSheet(stylesheet)
        self.current_theme_key = theme_key
        self.medallion_badge.setText(THEME_MEDALLION.get(theme_key, "WOLF"))
        self.drop_zone.set_theme_title(THEME_DROP_TITLE.get(theme_key, "WOLF SCHOOL INTAKE"))
        if hasattr(self, "likes_chart"):
            self.likes_chart.color = QColor(palette["accent"])
            self.followers_chart.color = QColor(palette["success"])
            self.plan_chart.color = QColor(palette["info"])
            self.likes_chart.update()
            self.followers_chart.update()
            self.plan_chart.update()

    def _on_profile_parsed(self, cdp_url: str, profile_url: str) -> None:
        self.cdp_input.setText(cdp_url)
        if profile_url and "tiktok.com" in profile_url:
            self.profile_url_input.setText(profile_url)

    def _pick_video_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать видео",
            str(Path.home()),
            "Video files (*.mp4 *.mov *.avi *.mkv);;All files (*.*)",
        )
        if path:
            self.video_file_input.setText(path)

    def _pick_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Выбрать папку вывода", str(Path.cwd()))
        if path:
            self.output_dir_input.setText(path)

    def _pick_core_root(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Выбрать папку shortform_core", str(self.core_root))
        if path:
            self.core_root_input.setText(path)

    def _resolve_core_snapshot_dir(self) -> Path:
        output_dir = Path(self.output_dir_input.text().strip() or "output")
        if output_dir.name.lower() == "output":
            return output_dir.parent
        if (output_dir / "output").exists():
            return output_dir
        return output_dir.parent

    def _set_core_running_state(self, running: bool) -> None:
        self.core_bootstrap_button.setEnabled(not running)
        self.core_demo_button.setEnabled(not running)

    def _run_core_action(self, action: str) -> None:
        if self.core_worker and self.core_worker.isRunning():
            QMessageBox.information(self, "Core Engine", "Команда Core уже выполняется.")
            return

        core_root = Path(self.core_root_input.text().strip())
        if not core_root.exists():
            QMessageBox.warning(self, "Core Engine", f"Корень core не найден:\n{core_root}")
            return

        snapshot_dir: Optional[Path] = None
        if self.core_use_live_output.isChecked():
            snapshot_dir = self._resolve_core_snapshot_dir()

        self.core_worker = CoreWorker(core_root=core_root, action=action, snapshot_dir=snapshot_dir)
        self.core_worker.log_signal.connect(self._append_log)
        self.core_worker.done_signal.connect(self._on_core_done)
        self._set_core_running_state(True)
        self._append_log(f"[CORE] Старт действия: {action}")
        self.core_worker.start()

    def _on_core_done(self, success: bool, details: str) -> None:
        self._set_core_running_state(False)
        if success:
            self._append_log(f"[CORE] {details}")
            self._show_core_plan()
            self._refresh_dashboard()
            return
        self._append_log(f"[CORE] ОШИБКА: {details}")
        QMessageBox.critical(self, "Core Engine", details)

    def _show_core_plan(self) -> None:
        core_root = Path(self.core_root_input.text().strip())
        plan_path = core_root / "runtime" / "output" / "plan_bundle.json"
        report_path = core_root / "runtime" / "output" / "analytics_report.json"
        action_labels = {
            "collect_data": "сбор_данных",
            "scale_creative": "масштабирование",
            "refine_hook": "доработка_хука",
            "tune_cta": "настройка_cta",
            "run_ab_test": "ab_тест",
            "monitor_profile": "мониторинг_профиля",
            "execute_task": "выполнение_задачи",
        }
        label_map = {
            "high": "высокий",
            "medium": "средний",
            "low": "низкий",
            "insufficient_data": "недостаточно_данных",
        }
        if not plan_path.exists():
            self._append_log(f"[CORE] файл плана не найден: {plan_path}")
            return

        try:
            plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
            self._append_log("[CORE] Сводка плана:")
            self._append_log(f"bundle_id={plan_data.get('bundle_id')} шагов={len(plan_data.get('steps', []))}")
            for index, step in enumerate(plan_data.get("steps", [])[:8], start=1):
                action = action_labels.get(step.get("action_type", "-"), step.get("action_type", "-"))
                title = step.get("title", "-")
                priority = step.get("priority", "-")
                self._append_log(f"  {index}. [{action}] {title} (приоритет={priority})")
        except Exception as error:
            self._append_log(f"[CORE] Не удалось прочитать план: {error}")

        if report_path.exists():
            try:
                report_data = json.loads(report_path.read_text(encoding="utf-8"))
                assessment = report_data.get("account_assessment", {})
                score = assessment.get("health_score", "-")
                raw_label = assessment.get("label", "-")
                label = label_map.get(raw_label, raw_label)
                self._append_log(f"[CORE] Оценка аккаунта: score={score}, label={label}")
            except Exception as error:
                self._append_log(f"[CORE] Не удалось прочитать отчет: {error}")

    def _start_worker(self) -> None:
        settings = self._collect_settings()
        self._start_worker_with_settings(settings, source="manual")

    def _start_worker_with_settings(self, settings: BotSettings, source: str) -> bool:
        if self.worker and self.worker.isRunning():
            return False
        if not settings.cdp_url.strip():
            self._append_log("Пропуск запуска: не указан CDP URL.")
            if source == "manual":
                QMessageBox.warning(self, "CDP URL", "Укажи CDP URL или перетащи профиль браузера.")
            return False

        self.active_run_source = source
        self.worker = BotWorker(settings)
        self.worker.log_signal.connect(self._append_log)
        self.worker.done_signal.connect(self._on_worker_done)
        self.worker.start()
        self._set_running_state(True)
        if source == "manual":
            self._append_log("Контракт запущен.")
        else:
            self._append_log(f"Контракт запущен из источника: {source}")
        return True

    def _stop_worker(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._append_log("Запрос на остановку отправлен.")

    def _on_worker_done(self, success: bool, details: str) -> None:
        self._set_running_state(False)
        if success:
            self._append_log(details)
        else:
            self._append_log("Ошибка выполнения:\n" + details)
            if self.active_run_source == "manual":
                QMessageBox.critical(self, "Ошибка", "Сценарий завершился с ошибкой. Смотри лог.")
        self._refresh_dashboard()
        self._try_run_next_from_queue()

    def _set_running_state(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.status_chip.setProperty("state", "running" if running else "ready")
        self.status_chip.setText("Контракт активен" if running else "Ожидание")
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)
        self.status_chip.update()
        self._refresh_global_badges()

    def _collect_settings(self) -> BotSettings:
        return self._settings_from_payload(self._collect_form_payload())

    def _settings_from_payload(self, payload: Dict[str, object]) -> BotSettings:
        comments = self._split_lines(str(payload.get("comments_text", "")))
        profiles = self._split_lines(str(payload.get("profiles_text", "")))
        return BotSettings(
            cdp_url=str(payload.get("cdp_url", "")),
            profile_url=str(payload.get("profile_url", "")),
            output_dir=Path(str(payload.get("output_dir", "output"))),
            for_you_url=str(payload.get("for_you_url", "https://www.tiktok.com/foryou")),
            watch_enabled=bool(payload.get("watch_enabled", True)),
            watch_videos=self._to_int(payload.get("watch_videos"), 10),
            collect_stats_enabled=bool(payload.get("collect_stats_enabled", True)),
            monitor_enabled=bool(payload.get("monitor_enabled", True)),
            comment_enabled=bool(payload.get("comment_enabled", False)),
            max_comments=self._to_int(payload.get("max_comments"), 2),
            comments=comments,
            visit_profiles_enabled=bool(payload.get("visit_profiles_enabled", False)),
            max_profiles_to_visit=self._to_int(payload.get("max_profiles_to_visit"), 5),
            profiles=profiles,
            upload_enabled=bool(payload.get("upload_enabled", False)),
            upload_file=str(payload.get("upload_file", "")),
            upload_caption=str(payload.get("upload_caption", "")),
            publish_upload=bool(payload.get("publish_upload", False)),
            min_delay_seconds=self._to_float(payload.get("min_delay_seconds"), 3.0),
            max_delay_seconds=self._to_float(payload.get("max_delay_seconds"), 8.0),
            retry_attempts=self._to_int(payload.get("retry_attempts"), 2),
            action_timeout_seconds=self._to_float(payload.get("action_timeout_seconds"), 12.0),
            selector_timeout_ms=self._to_int(payload.get("selector_timeout_ms"), 4500),
            health_check_enabled=bool(payload.get("health_check_enabled", True)),
            strict_health_check=bool(payload.get("strict_health_check", False)),
        )

    def _split_lines(self, text: str) -> List[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _to_int(self, value: object, default: int) -> int:
        try:
            return int(float(str(value)))
        except Exception:
            return default

    def _to_float(self, value: object, default: float) -> float:
        try:
            return float(str(value))
        except Exception:
            return default

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f"[{timestamp}] {message}")

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.scheduler.stop()
        self.dashboard_timer.stop()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        super().closeEvent(event)

