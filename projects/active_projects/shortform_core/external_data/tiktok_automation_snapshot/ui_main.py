from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import (
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
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QDoubleSpinBox,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from profile_parser import parse_profile_payload
from settings import BotSettings
from worker import BotWorker

THEME_NAMES = {
    "wolf": "Wolf",
    "nilfgaard": "Nilfgaard",
    "skellige": "Skellige",
}

THEME_PRESETS: Dict[str, Dict[str, str]] = {
    "wolf": {
        "root_bg": "#121a24",
        "text_base": "#f2e8d2",
        "label": "#f2e7ce",
        "header_border": "#655334",
        "header_g1": "#231f19",
        "header_g2": "#1a1713",
        "header_g3": "#12100d",
        "title": "#e4cb8f",
        "subtitle": "#ccb892",
        "status_border": "#6a5a3b",
        "status_bg": "#2e2619",
        "status_text": "#fff4db",
        "ready_bg": "#1f3020",
        "ready_border": "#4f7752",
        "ready_text": "#cae2be",
        "running_bg": "#3b2d15",
        "running_border": "#b58d41",
        "running_text": "#ffe3ab",
        "drop_border": "#8b6b35",
        "drop_bg": "rgba(140, 108, 50, 0.10)",
        "drop_active_border": "#d4ae67",
        "drop_active_bg": "rgba(212, 174, 103, 0.22)",
        "drop_title": "#f2ddad",
        "drop_hint": "#ead8b3",
        "panel_border": "#6d5937",
        "panel_g1": "#1a2431",
        "panel_g2": "#131b26",
        "panel_title_bg": "#111a25",
        "panel_title_text": "#f3cd85",
        "tag_text": "#a9c298",
        "tag_border": "#48633c",
        "tag_bg": "rgba(74, 104, 60, 0.20)",
        "input_border": "#81683f",
        "input_bg": "#182434",
        "input_text": "#fff6e4",
        "input_focus_border": "#e0b56a",
        "input_focus_bg": "#1e2e43",
        "checkbox_text": "#f2e7ce",
        "checkbox_border": "#6b5c3f",
        "checkbox_bg": "#0c1015",
        "checkbox_checked_bg": "#b28d49",
        "checkbox_checked_border": "#d2b26e",
        "button_border": "#7a6236",
        "button_text": "#f0e2c3",
        "button_g1": "#5b4624",
        "button_g2": "#3c2f18",
        "button_hover_border": "#c4a366",
        "button_hover_g1": "#6a542d",
        "button_hover_g2": "#483720",
        "button_pressed": "#2f2413",
        "button_disabled_text": "#857f71",
        "button_disabled_border": "#433c31",
        "button_disabled_bg": "#22252b",
        "start_border": "#6b7f45",
        "start_g1": "#3b4f2c",
        "start_g2": "#2c3c22",
        "start_hover_border": "#8fb36b",
        "start_hover_g1": "#466236",
        "start_hover_g2": "#31482a",
        "stop_border": "#81524a",
        "stop_g1": "#5a2f2a",
        "stop_g2": "#43211d",
        "stop_hover_border": "#bb6b5f",
        "stop_hover_g1": "#67332f",
        "stop_hover_g2": "#4f2521",
        "log_bg": "#182233",
        "log_border": "#7b643d",
        "log_text": "#f5f8ff",
        "medallion_bg": "#2a3447",
        "medallion_border": "#d4ae67",
        "medallion_text": "#fff3d4",
    },
    "nilfgaard": {
        "root_bg": "#14110c",
        "text_base": "#f3e7c7",
        "label": "#f5e8c8",
        "header_border": "#8b6a2d",
        "header_g1": "#2b2315",
        "header_g2": "#1d160d",
        "header_g3": "#0f0b06",
        "title": "#f0ce7d",
        "subtitle": "#d3ba84",
        "status_border": "#8f7138",
        "status_bg": "#2f2412",
        "status_text": "#fff1ca",
        "ready_bg": "#253522",
        "ready_border": "#5e8552",
        "ready_text": "#d3edc7",
        "running_bg": "#4a3614",
        "running_border": "#cca357",
        "running_text": "#ffebb8",
        "drop_border": "#ad8340",
        "drop_bg": "rgba(162, 122, 53, 0.16)",
        "drop_active_border": "#efc679",
        "drop_active_bg": "rgba(224, 177, 93, 0.28)",
        "drop_title": "#f6dfac",
        "drop_hint": "#f0daab",
        "panel_border": "#8a6b37",
        "panel_g1": "#1f170d",
        "panel_g2": "#171109",
        "panel_title_bg": "#120d06",
        "panel_title_text": "#f1cb7d",
        "tag_text": "#d6c089",
        "tag_border": "#715c35",
        "tag_bg": "rgba(118, 94, 51, 0.26)",
        "input_border": "#9a7942",
        "input_bg": "#1e1710",
        "input_text": "#fff2d2",
        "input_focus_border": "#f2c978",
        "input_focus_bg": "#2c2115",
        "checkbox_text": "#f2e4c3",
        "checkbox_border": "#886f44",
        "checkbox_bg": "#15100b",
        "checkbox_checked_bg": "#c89b4a",
        "checkbox_checked_border": "#f2cb80",
        "button_border": "#9a7a42",
        "button_text": "#fff0c8",
        "button_g1": "#6b5329",
        "button_g2": "#4b391d",
        "button_hover_border": "#e5be70",
        "button_hover_g1": "#7b6133",
        "button_hover_g2": "#5b4524",
        "button_pressed": "#3a2b16",
        "button_disabled_text": "#9c8f74",
        "button_disabled_border": "#5a4c34",
        "button_disabled_bg": "#2a241b",
        "start_border": "#7d9158",
        "start_g1": "#465f34",
        "start_g2": "#344726",
        "start_hover_border": "#9dbf70",
        "start_hover_g1": "#547640",
        "start_hover_g2": "#3f5a2f",
        "stop_border": "#8a4f4b",
        "stop_g1": "#6a3430",
        "stop_g2": "#4f2623",
        "stop_hover_border": "#c1695f",
        "stop_hover_g1": "#7c3d39",
        "stop_hover_g2": "#5c2a26",
        "log_bg": "#1b140d",
        "log_border": "#8c6c3a",
        "log_text": "#fff7e1",
        "medallion_bg": "#2f2514",
        "medallion_border": "#f0c677",
        "medallion_text": "#fff0c8",
    },
    "skellige": {
        "root_bg": "#0f1a2b",
        "text_base": "#e9f3ff",
        "label": "#e5f2ff",
        "header_border": "#4f7ea6",
        "header_g1": "#1a2e47",
        "header_g2": "#15253a",
        "header_g3": "#0d1728",
        "title": "#b8dcff",
        "subtitle": "#a9c7e6",
        "status_border": "#6f9ac0",
        "status_bg": "#21364f",
        "status_text": "#e6f5ff",
        "ready_bg": "#1f4840",
        "ready_border": "#4d8b79",
        "ready_text": "#cbf0e7",
        "running_bg": "#4b3d24",
        "running_border": "#bda26d",
        "running_text": "#fff0cb",
        "drop_border": "#6da3d4",
        "drop_bg": "rgba(88, 135, 188, 0.18)",
        "drop_active_border": "#9ccbf2",
        "drop_active_bg": "rgba(137, 183, 228, 0.28)",
        "drop_title": "#d5ecff",
        "drop_hint": "#d3e7fb",
        "panel_border": "#4c7299",
        "panel_g1": "#182a42",
        "panel_g2": "#122036",
        "panel_title_bg": "#0d1a2c",
        "panel_title_text": "#9fcbf2",
        "tag_text": "#c6e2ff",
        "tag_border": "#4b739a",
        "tag_bg": "rgba(74, 113, 156, 0.28)",
        "input_border": "#628eb4",
        "input_bg": "#1a2f47",
        "input_text": "#f0f8ff",
        "input_focus_border": "#9fd2ff",
        "input_focus_bg": "#223d5d",
        "checkbox_text": "#e8f3ff",
        "checkbox_border": "#729ec4",
        "checkbox_bg": "#14253b",
        "checkbox_checked_bg": "#6eadda",
        "checkbox_checked_border": "#a9d8ff",
        "button_border": "#6289ad",
        "button_text": "#eef6ff",
        "button_g1": "#3a5b7b",
        "button_g2": "#2a435d",
        "button_hover_border": "#9bc4e8",
        "button_hover_g1": "#46709a",
        "button_hover_g2": "#34557a",
        "button_pressed": "#20384e",
        "button_disabled_text": "#8d9fb4",
        "button_disabled_border": "#4c6077",
        "button_disabled_bg": "#223347",
        "start_border": "#4a8d73",
        "start_g1": "#2f6b5a",
        "start_g2": "#244f43",
        "start_hover_border": "#74be9f",
        "start_hover_g1": "#3d8671",
        "start_hover_g2": "#2e6657",
        "stop_border": "#91625f",
        "stop_g1": "#734340",
        "stop_g2": "#5c3431",
        "stop_hover_border": "#c1847f",
        "stop_hover_g1": "#8a5550",
        "stop_hover_g2": "#6d403b",
        "log_bg": "#14253a",
        "log_border": "#5e87b0",
        "log_text": "#eff8ff",
        "medallion_bg": "#1b324f",
        "medallion_border": "#8ec1e8",
        "medallion_text": "#eaf6ff",
    },
}

THEME_MEDALLION = {
    "wolf": "WOLF",
    "nilfgaard": "SUN",
    "skellige": "SKELL",
}

THEME_DROP_TITLE = {
    "wolf": "WOLF SCHOOL INTAKE",
    "nilfgaard": "NILFGAARD COMMAND",
    "skellige": "SKELLIGE LONGSHIP BAY",
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

        self.title_label = QLabel("WOLF SCHOOL INTAKE")
        self.title_label.setObjectName("dropTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)

        label = QLabel(
            "Перетащи JSON профиля/текст из антидетект браузера сюда\n"
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
            self.log_signal.emit("Не удалось извлечь CDP URL из drop-данных.")

        event.acceptProposedAction()

    def _set_drag_state(self, active: bool) -> None:
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_theme_title(self, title: str) -> None:
        self.title_label.setText(title)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Witcher Command Deck | TikTok Ops")
        self.resize(1260, 860)
        self.setMinimumSize(1080, 760)
        self.worker: Optional[BotWorker] = None
        self.current_theme_key = "wolf"
        self._build_ui()
        self._apply_theme(self.current_theme_key)
        self._set_running_state(False)

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addWidget(self._build_header())

        scroll = QScrollArea()
        scroll.setObjectName("mainScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(4, 4, 6, 8)
        content_layout.setSpacing(12)

        self.drop_zone = ProfileDropZone()
        self.drop_zone.profile_parsed.connect(self._on_profile_parsed)
        self.drop_zone.log_signal.connect(self._append_log)
        content_layout.addWidget(self.drop_zone)

        content_layout.addWidget(self._build_connection_box())
        content_layout.addWidget(self._build_scenario_box())
        content_layout.addWidget(self._build_upload_box())
        content_layout.addWidget(self._build_runtime_box())
        content_layout.addWidget(self._build_controls_box())
        content_layout.addWidget(self._build_log_panel())
        content_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        root.addWidget(scroll, stretch=1)

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerBar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.medallion_badge = QLabel("WOLF")
        self.medallion_badge.setObjectName("medallionBadge")
        self.medallion_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.medallion_badge.setFixedSize(64, 64)
        layout.addWidget(self.medallion_badge)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("THE WITCHER: CONTRACT BOARD")
        title.setObjectName("titleLabel")
        subtitle = QLabel("TikTok automation command table for anti-detect browser profiles.")
        subtitle.setObjectName("subtitleLabel")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self.status_chip = QLabel("Ожидание")
        self.status_chip.setObjectName("statusChip")
        self.status_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_chip.setMinimumWidth(180)

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
        right_col.addWidget(self.status_chip)

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
            self._append_log(f"Тема интерфейса: {display_name}")

    def _build_log_panel(self) -> QGroupBox:
        box = QGroupBox("Боевой журнал")
        box.setObjectName("panel")
        box.setMinimumHeight(210)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 22, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        mode_label = QLabel("Режим: ручной контроль")
        mode_label.setObjectName("smallTag")
        clear_button = QPushButton("Очистить лог")

        self.log_edit = QTextEdit()
        clear_button.clicked.connect(self.log_edit.clear)
        top.addWidget(mode_label)
        top.addStretch(1)
        top.addWidget(clear_button)
        layout.addLayout(top)

        self.log_edit.setReadOnly(True)
        self.log_edit.setObjectName("logOutput")
        self.log_edit.setPlaceholderText("Здесь будет журнал действий, ошибок и статуса профиля...")
        layout.addWidget(self.log_edit, stretch=1)
        return box

    def _build_connection_box(self) -> QGroupBox:
        box = QGroupBox("Подключение")
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
        box = QGroupBox("Контракт и сценарии")
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

        self.monitor_checkbox = QCheckBox("Снимать метрики профиля")
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

        self.visit_profiles_checkbox = QCheckBox("Открывать профили")
        self.visit_profiles_checkbox.setChecked(False)
        self.profiles_limit_spin = QSpinBox()
        self.profiles_limit_spin.setRange(0, 500)
        self.profiles_limit_spin.setValue(5)
        self.profiles_edit = QPlainTextEdit()
        self.profiles_edit.setObjectName("profilesEdit")
        self.profiles_edit.setPlaceholderText("URL профиля TikTok, по одному в строке")
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
        box = QGroupBox("Загрузка видео")
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
        self.caption_input.setPlaceholderText("Описание для видео")
        form.addRow("Описание:", self.caption_input)

        self.publish_checkbox = QCheckBox("Публиковать автоматически")
        self.publish_checkbox.setChecked(False)
        form.addRow(self.publish_checkbox)
        return box

    def _build_runtime_box(self) -> QGroupBox:
        box = QGroupBox("Параметры боя")
        box.setObjectName("panel")
        form = QFormLayout(box)
        form.setContentsMargins(12, 22, 12, 12)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.min_delay_spin = QDoubleSpinBox()
        self.min_delay_spin.setRange(0.5, 300.0)
        self.min_delay_spin.setValue(3.0)
        self.min_delay_spin.setSingleStep(0.5)
        form.addRow("Min пауза (сек):", self.min_delay_spin)

        self.max_delay_spin = QDoubleSpinBox()
        self.max_delay_spin.setRange(0.5, 300.0)
        self.max_delay_spin.setValue(8.0)
        self.max_delay_spin.setSingleStep(0.5)
        form.addRow("Max пауза (сек):", self.max_delay_spin)

        output_row = QWidget()
        output_layout = QHBoxLayout(output_row)
        output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_dir_input = QLineEdit(str(Path.cwd() / "output"))
        output_browse = QPushButton("Папка")
        output_browse.clicked.connect(self._pick_output_dir)
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(output_browse)
        form.addRow("Вывод данных:", output_row)

        return box

    def _build_controls_box(self) -> QGroupBox:
        box = QGroupBox("Управление контрактом")
        box.setObjectName("panel")
        layout = QHBoxLayout(box)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(8)

        self.start_button = QPushButton("Start Contract")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self._start_worker)
        self.stop_button.clicked.connect(self._stop_worker)

        layout.addWidget(self.start_button, stretch=2)
        layout.addWidget(self.stop_button, stretch=1)
        return box

    def _apply_theme(self, theme_key: str) -> None:
        palette = THEME_PRESETS.get(theme_key, THEME_PRESETS["wolf"])
        stylesheet = """
            QWidget#root {
                background-color: __ROOT_BG__;
                color: __TEXT_BASE__;
                font-family: "Trebuchet MS", "Segoe UI", sans-serif;
                font-size: 14px;
            }

            QLabel {
                color: __LABEL__;
                font-size: 13px;
            }

            QScrollArea#mainScroll,
            QWidget#scrollContent,
            QScrollArea#mainScroll QWidget#qt_scrollarea_viewport {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                width: 11px;
                background: transparent;
                margin: 2px 0 2px 0;
            }

            QScrollBar::handle:vertical {
                min-height: 26px;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.28);
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
                border-radius: 12px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 __HEADER_G1__,
                    stop: 0.55 __HEADER_G2__,
                    stop: 1 __HEADER_G3__
                );
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
                font-family: "Georgia", "Palatino Linotype", serif;
                font-size: 12px;
            }

            QLabel#titleLabel {
                color: __TITLE__;
                font-family: "Georgia", "Palatino Linotype", serif;
                font-size: 23px;
                font-weight: 700;
            }

            QLabel#subtitleLabel {
                color: __SUBTITLE__;
                font-size: 12px;
            }

            QLabel#themeCaption {
                color: __LABEL__;
                font-weight: 700;
            }

            QComboBox#themeCombo {
                border: 1px solid __INPUT_BORDER__;
                border-radius: 7px;
                padding: 6px 8px;
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
                border-radius: 13px;
                padding: 6px 12px;
                background-color: __STATUS_BG__;
                color: __STATUS_TEXT__;
                font-weight: 700;
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

            QFrame#dropZone {
                border: 2px dashed __DROP_BORDER__;
                border-radius: 12px;
                background-color: __DROP_BG__;
            }

            QFrame#dropZone[dragActive="true"] {
                border-color: __DROP_ACTIVE_BORDER__;
                background-color: __DROP_ACTIVE_BG__;
            }

            QLabel#dropTitle {
                color: __DROP_TITLE__;
                font-family: "Georgia", "Palatino Linotype", serif;
                font-size: 16px;
                font-weight: 700;
            }

            QLabel#dropHint {
                color: __DROP_HINT__;
                font-size: 13px;
            }

            QGroupBox#panel {
                border: 1px solid __PANEL_BORDER__;
                border-radius: 11px;
                margin-top: 4px;
                padding-top: 10px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 __PANEL_G1__,
                    stop: 1 __PANEL_G2__
                );
            }

            QGroupBox#panel::title {
                subcontrol-origin: padding;
                subcontrol-position: top left;
                left: 10px;
                top: 0px;
                padding: 0 8px;
                background-color: __PANEL_TITLE_BG__;
                color: __PANEL_TITLE_TEXT__;
                font-weight: 700;
            }

            QLabel#smallTag {
                color: __TAG_TEXT__;
                border: 1px solid __TAG_BORDER__;
                border-radius: 8px;
                padding: 4px 8px;
                background-color: __TAG_BG__;
            }

            QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid __INPUT_BORDER__;
                border-radius: 8px;
                background-color: __INPUT_BG__;
                color: __INPUT_TEXT__;
                padding: 6px;
                selection-background-color: __INPUT_FOCUS_BORDER__;
                selection-color: __INPUT_TEXT__;
            }

            QPlainTextEdit#commentsEdit,
            QPlainTextEdit#profilesEdit {
                border-radius: 12px;
                border: 1px solid __INPUT_BORDER__;
                background-color: __INPUT_BG__;
                padding: 8px;
            }

            QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid __INPUT_FOCUS_BORDER__;
                background-color: __INPUT_FOCUS_BG__;
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
                border-radius: 8px;
                padding: 7px 12px;
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
            """

        for name, value in palette.items():
            token = "__" + name.upper() + "__"
            stylesheet = stylesheet.replace(token, value)

        self.setStyleSheet(stylesheet)
        self.current_theme_key = theme_key
        self.medallion_badge.setText(THEME_MEDALLION.get(theme_key, "WOLF"))
        self.drop_zone.set_theme_title(THEME_DROP_TITLE.get(theme_key, "WOLF SCHOOL INTAKE"))

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

    def _start_worker(self) -> None:
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Выполнение", "Сценарий уже выполняется.")
            return

        settings = self._collect_settings()
        if not settings.cdp_url.strip():
            QMessageBox.warning(self, "CDP URL", "Укажите CDP URL или перетащите профиль.")
            return

        self.worker = BotWorker(settings)
        self.worker.log_signal.connect(self._append_log)
        self.worker.done_signal.connect(self._on_worker_done)
        self.worker.start()
        self._set_running_state(True)
        self._append_log("Контракт запущен.")

    def _stop_worker(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._append_log("Отправлен запрос на остановку.")

    def _on_worker_done(self, success: bool, details: str) -> None:
        self._set_running_state(False)
        if success:
            self._append_log(details)
        else:
            self._append_log("Ошибка выполнения:\n" + details)
            QMessageBox.critical(self, "Ошибка", "Сценарий завершился с ошибкой. Смотри лог.")

    def _set_running_state(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.status_chip.setProperty("state", "running" if running else "ready")
        self.status_chip.setText("Контракт активен" if running else "Ожидание")
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)
        self.status_chip.update()

    def _collect_settings(self) -> BotSettings:
        comments = self._split_lines(self.comments_edit.toPlainText())
        profiles = self._split_lines(self.profiles_edit.toPlainText())
        return BotSettings(
            cdp_url=self.cdp_input.text(),
            profile_url=self.profile_url_input.text(),
            output_dir=Path(self.output_dir_input.text().strip() or "output"),
            for_you_url=self.for_you_input.text(),
            watch_enabled=self.watch_checkbox.isChecked(),
            watch_videos=self.watch_count_spin.value(),
            collect_stats_enabled=self.collect_stats_checkbox.isChecked(),
            monitor_enabled=self.monitor_checkbox.isChecked(),
            comment_enabled=self.comment_checkbox.isChecked(),
            max_comments=self.comment_limit_spin.value(),
            comments=comments,
            visit_profiles_enabled=self.visit_profiles_checkbox.isChecked(),
            max_profiles_to_visit=self.profiles_limit_spin.value(),
            profiles=profiles,
            upload_enabled=self.upload_checkbox.isChecked(),
            upload_file=self.video_file_input.text(),
            upload_caption=self.caption_input.text(),
            publish_upload=self.publish_checkbox.isChecked(),
            min_delay_seconds=float(self.min_delay_spin.value()),
            max_delay_seconds=float(self.max_delay_spin.value()),
        )

    def _split_lines(self, text: str) -> List[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f"[{timestamp}] {message}")
