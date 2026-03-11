from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class MotionButton(QPushButton):
    def __init__(self, title: str) -> None:
        super().__init__(title)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setProperty("motionButton", "true")

        self._is_hovered = False
        self._is_pressed = False
        self._is_focused = False
        self._motion_value = 0.0

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 0)
        self._shadow.setBlurRadius(0.0)
        self._shadow.setColor(QColor(176, 146, 255, 0))
        self.setGraphicsEffect(self._shadow)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(145)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._apply_motion)

        if self.isCheckable():
            self.toggled.connect(lambda _: self._refresh_motion())

    def _apply_motion(self, value: Any) -> None:
        glow = float(value)
        self._motion_value = glow
        alpha = max(0, min(108, int(glow * 5.0)))
        self._shadow.setBlurRadius(glow)
        self._shadow.setColor(QColor(182, 152, 255, alpha))
        self._shadow.setOffset(0, 0.8 if self._is_pressed else -0.18 * max(0.0, glow - 7.0))

    def _target(self) -> float:
        if not self.isEnabled():
            return 0.0
        target = 0.0
        if self._is_focused:
            target = max(target, 8.0)
        if self._is_hovered:
            target = max(target, 14.0)
        if self.isCheckable() and self.isChecked():
            target = max(target, 12.0)
        if self._is_pressed:
            target = 7.0
        return target

    def _animate_to(self, target: float) -> None:
        self._anim.stop()
        if self._is_pressed:
            duration = 105
        elif self._is_hovered or self._is_focused:
            duration = 165
        else:
            duration = 135
        self._anim.setDuration(duration)
        self._anim.setStartValue(self._motion_value)
        self._anim.setEndValue(target)
        self._anim.start()

    def _refresh_motion(self) -> None:
        self._animate_to(self._target())

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._is_hovered = True
        self._refresh_motion()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._is_hovered = False
        self._is_pressed = False
        self._refresh_motion()
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:  # type: ignore[override]
        self._is_focused = True
        self._refresh_motion()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:  # type: ignore[override]
        self._is_focused = False
        self._refresh_motion()
        super().focusOutEvent(event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self._is_pressed = True
        self._refresh_motion()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._is_pressed = False
        self._refresh_motion()
        super().mouseReleaseEvent(event)

    def setChecked(self, checked: bool) -> None:  # type: ignore[override]
        super().setChecked(checked)
        self._refresh_motion()


class NavRailButton(MotionButton):
    def __init__(self, title: str, *, page_key: str) -> None:
        super().__init__(title)
        self.page_key = page_key
        self.setProperty("navButton", "true")
        self.setCheckable(True)
        self.toggled.connect(lambda _: self._refresh_motion())
        self.setMinimumHeight(46)


class StatusPill(QLabel):
    def __init__(self, text: str = "неизв.", level: str = "info") -> None:
        super().__init__(text)
        self.setProperty("statusPill", "true")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(28)
        self._level = level
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 0)
        self._shadow.setBlurRadius(0.0)
        self._shadow.setColor(QColor(176, 146, 255, 0))
        self.setGraphicsEffect(self._shadow)

        self._pulse = QVariantAnimation(self)
        self._pulse.setDuration(200)
        self._pulse.setStartValue(0.0)
        self._pulse.setEndValue(1.0)
        self._pulse.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._pulse.valueChanged.connect(self._apply_pulse)

        self.set_level(level)

    def _apply_pulse(self, value: Any) -> None:
        phase = 1.0 - abs(2.0 * float(value) - 1.0)
        color_by_level = {
            "ok": QColor(51, 214, 159),
            "warn": QColor(255, 184, 92),
            "danger": QColor(255, 110, 138),
            "info": QColor(104, 199, 255),
        }
        base = color_by_level.get(self._level, QColor(176, 146, 255))
        alpha = int(phase * 76)
        self._shadow.setBlurRadius(4.0 + 8.0 * phase)
        self._shadow.setColor(QColor(base.red(), base.green(), base.blue(), alpha))

    def _pulse_once(self) -> None:
        self._pulse.stop()
        self._pulse.start()

    def set_level(self, level: str) -> None:
        if level not in {"ok", "warn", "danger", "info"}:
            level = "info"
        self._level = level
        self.setProperty("statusLevel", level)
        self.style().unpolish(self)
        self.style().polish(self)
        self._pulse_once()

    def set_state(self, text: str, level: str) -> None:
        text_changed = self.text() != text
        level_changed = self._level != level
        if text_changed:
            self.setText(text)
        if level_changed:
            self.set_level(level)
        elif text_changed:
            self._pulse_once()


class GlowCard(QFrame):
    clicked = Signal()

    def __init__(self, *, elevated: bool = False) -> None:
        super().__init__()
        self.setProperty("card", "elevated" if elevated else "true")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 0)
        self._shadow.setBlurRadius(14)
        self._shadow.setColor(QColor(130, 102, 214, 40))
        self.setGraphicsEffect(self._shadow)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(190)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._apply_glow)
        self._current_blur = 14.0
        self._is_hovered = False
        self._is_pressed = False
        self.setProperty("cardHover", "false")
        self.setProperty("cardPressed", "false")

    def _apply_glow(self, value: Any) -> None:
        blur = float(value)
        self._current_blur = blur
        self._shadow.setBlurRadius(blur)
        alpha = max(28, min(110, int(blur * 4)))
        self._shadow.setColor(QColor(168, 138, 255, alpha))
        self._shadow.setOffset(0, -0.05 * max(0.0, blur - 12.0))

    def _animate_to(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._current_blur)
        self._anim.setEndValue(target)
        self._anim.start()

    def _target_blur(self) -> float:
        if self._is_pressed:
            return 9.5
        if self._is_hovered:
            return 21.0
        return 14.0

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._is_hovered = True
        self.setProperty("cardHover", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)
        self._animate_to(self._target_blur())

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._is_hovered = False
        self._is_pressed = False
        self.setProperty("cardHover", "false")
        self.setProperty("cardPressed", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)
        self._animate_to(self._target_blur())

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self._is_pressed = True
        self.setProperty("cardPressed", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        self._animate_to(self._target_blur())
        super().mousePressEvent(event)
        self.clicked.emit()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._is_pressed = False
        self.setProperty("cardPressed", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._animate_to(self._target_blur())
        super().mouseReleaseEvent(event)


class MetricCard(GlowCard):
    def __init__(self, title: str, value: str = "-", meta: str = "") -> None:
        super().__init__(elevated=True)
        self.setObjectName("MetricCard")
        self.setMinimumHeight(148)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        self.title = QLabel(title)
        self.title.setObjectName("CardTitle")
        self.title.setWordWrap(True)
        self.value = QLabel(value)
        self.value.setObjectName("CardValue")
        self.value.setProperty("cardValueDense", "false")
        self.meta = QLabel(meta)
        self.meta.setObjectName("CardMeta")
        self.meta.setWordWrap(True)

        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.meta)
        layout.addStretch(1)

    def set_data(self, value: str, meta: str = "") -> None:
        self.value.setText(value)
        self.meta.setText(meta)
        dense = len(value) > 7 or any(ch.isalpha() for ch in value)
        target = "true" if dense else "false"
        if self.value.property("cardValueDense") != target:
            self.value.setProperty("cardValueDense", target)
            self.value.style().unpolish(self.value)
            self.value.style().polish(self.value)


class SectionHeader(QWidget):
    def __init__(self, title: str, hint: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.title = QLabel(title)
        self.title.setObjectName("SectionTitle")
        self.title.setWordWrap(True)
        layout.addWidget(self.title)

        self.hint = QLabel(hint)
        self.hint.setObjectName("SectionHint")
        self.hint.setWordWrap(True)
        self.hint.setVisible(bool(hint))
        layout.addWidget(self.hint)

    def set_hint(self, hint: str) -> None:
        self.hint.setText(hint)
        self.hint.setVisible(bool(hint))


class TopStatusBar(GlowCard):
    refresh_requested = Signal()

    def __init__(self) -> None:
        super().__init__(elevated=False)
        self.setObjectName("TopStatusBar")
        self.setMinimumHeight(108)
        self._is_loading = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(14)

        self.pills: dict[str, StatusPill] = {
            "profiles": StatusPill("профили: --", "info"),
            "sessions": StatusPill("сессии: --", "info"),
            "queue": StatusPill("очередь: --", "info"),
            "verification": StatusPill("гейт: --", "warn"),
            "ai": StatusPill("AI: --", "info"),
            "runtime": StatusPill("система: --", "info"),
            "alerts": StatusPill("сигналы: --", "warn"),
        }
        pill_grid = QGridLayout()
        pill_grid.setHorizontalSpacing(8)
        pill_grid.setVerticalSpacing(8)
        order = ["profiles", "sessions", "queue", "verification", "ai", "runtime", "alerts"]
        for idx, key in enumerate(order):
            # Use 3 columns to preserve readable pill widths on 125%/150% scaling.
            row = idx // 3
            col = idx % 3
            self.pills[key].setMinimumWidth(110)
            self.pills[key].setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
            pill_grid.addWidget(self.pills[key], row, col)
        pill_grid.setColumnStretch(0, 1)
        pill_grid.setColumnStretch(1, 1)
        pill_grid.setColumnStretch(2, 1)
        layout.addLayout(pill_grid, stretch=1)

        self.refresh_button = MotionButton("Обновить данные")
        self.refresh_button.setObjectName("PrimaryCTA")
        self.refresh_button.setMinimumHeight(40)
        self.refresh_button.setMinimumWidth(156)
        self.refresh_button.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(self.refresh_button)

    def set_loading(self, loading: bool) -> None:
        if self._is_loading == loading:
            return
        self._is_loading = loading
        if loading:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("Обновление...")
            self._animate_to(19.0)
        else:
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText("Обновить данные")
            self._animate_to(self._target_blur())

    def update_state(
        self,
        *,
        profile_count: int,
        session_count: int,
        queue_count: int,
        verification: str,
        ai_state: str,
        runtime_state: str,
        alerts_count: int,
    ) -> None:
        ai_map = {"ready": "готов", "degraded": "ограничено"}
        runtime_map = {"ready": "готова", "degraded": "ограничена"}
        verify_map = {
            "PASS": "PASS",
            "PASS_WITH_WARNINGS": "PASS+",
            "FAIL": "FAIL",
            "UNKNOWN": "н/д",
        }

        self.pills["profiles"].set_state(f"профили: {profile_count}", "ok" if profile_count > 0 else "info")
        self.pills["sessions"].set_state(f"сессии: {session_count}", "ok" if session_count > 0 else "warn")
        self.pills["queue"].set_state(f"очередь: {queue_count}", "warn" if queue_count > 0 else "ok")

        verification_level = "ok" if verification == "PASS" else "warn"
        self.pills["verification"].set_state(
            f"вериф.: {verify_map.get(verification, verification)}",
            verification_level,
        )

        ai_view = ai_map.get(ai_state)
        if ai_view is None:
            ai_view = "огр." if ai_state else "н/д"
        self.pills["ai"].set_state(f"AI: {ai_view}", "info" if ai_state != "ready" else "ok")

        runtime_view = runtime_map.get(runtime_state)
        if runtime_view is None:
            runtime_view = "огр." if runtime_state else "н/д"
        self.pills["runtime"].set_state(
            f"система: {runtime_view}",
            "ok" if runtime_state == "ready" else "warn",
        )
        self.pills["alerts"].set_state(f"сигналы: {alerts_count}", "danger" if alerts_count > 0 else "ok")


class EmptyStateCard(GlowCard):
    def __init__(self, title: str, details: str) -> None:
        super().__init__(elevated=False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        layout.addWidget(title_label)

        details_label = QLabel(details)
        details_label.setObjectName("SectionHint")
        details_label.setWordWrap(True)
        layout.addWidget(details_label)


class ContextPanel(GlowCard):
    action_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__(elevated=False)
        self.setObjectName("ContextPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("Контекст и действия")
        title.setObjectName("ContextPanelTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        self.profile_title = QLabel("Профиль не выбран")
        self.profile_title.setObjectName("SectionTitle")
        self.profile_title.setWordWrap(True)
        layout.addWidget(self.profile_title)

        self.profile_meta = QLabel("Выберите профиль в разделе «Профили», чтобы увидеть детали.")
        self.profile_meta.setObjectName("SectionHint")
        self.profile_meta.setWordWrap(True)
        layout.addWidget(self.profile_meta)

        self.alerts_block = QLabel("Сигналы: нет активных предупреждений")
        self.alerts_block.setObjectName("SectionHint")
        self.alerts_block.setWordWrap(True)
        layout.addWidget(self.alerts_block)

        self.recommendations_hint = QLabel("Здесь появятся рекомендации AI и подсказки по шагам.")
        self.recommendations_hint.setObjectName("SectionHint")
        self.recommendations_hint.setWordWrap(True)
        layout.addWidget(self.recommendations_hint)

        self.next_actions = QLabel("Следующий шаг: обновите данные и откройте рабочую сессию.")
        self.next_actions.setObjectName("SectionHint")
        self.next_actions.setWordWrap(True)
        layout.addWidget(self.next_actions)

        layout.addStretch(1)

        action_caption = QLabel("Быстрые действия")
        action_caption.setObjectName("ContextActionCaption")
        layout.addWidget(action_caption)

        action_dock = QWidget()
        action_dock.setObjectName("ContextActionDock")
        btn_col = QVBoxLayout(action_dock)
        btn_col.setContentsMargins(10, 10, 10, 10)
        btn_col.setSpacing(10)
        quick_ai = MotionButton("Открыть AI-студию")
        quick_ai.setObjectName("PrimaryCTA")
        quick_ai.setMinimumHeight(40)
        quick_ai.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        quick_ai.clicked.connect(lambda: self.action_requested.emit("open_ai_studio"))
        quick_updates = MotionButton("Проверить апдейты")
        quick_updates.setObjectName("OutlineCTA")
        quick_updates.setMinimumHeight(40)
        quick_updates.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        quick_updates.clicked.connect(lambda: self.action_requested.emit("check_updates"))
        btn_col.addWidget(quick_ai)
        btn_col.addWidget(quick_updates)
        layout.addWidget(action_dock)

    def update_context(self, *, profile_name: str, profile_meta: str, alerts: list[str], recommendation_hint: str, next_actions: str) -> None:
        self.profile_title.setText(profile_name)
        self.profile_meta.setText(profile_meta)
        self.alerts_block.setText("Сигналы: нет активных предупреждений" if not alerts else "Сигналы:\n• " + "\n• ".join(alerts[:4]))
        self.recommendations_hint.setText(recommendation_hint)
        self.next_actions.setText(next_actions)
