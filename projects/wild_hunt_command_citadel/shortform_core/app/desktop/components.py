from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class NavRailButton(QPushButton):
    def __init__(self, title: str, *, page_key: str) -> None:
        super().__init__(title)
        self.page_key = page_key
        self.setProperty("navButton", "true")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)


class StatusPill(QLabel):
    def __init__(self, text: str = "unknown", level: str = "info") -> None:
        super().__init__(text)
        self.setProperty("statusPill", "true")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(24)
        self.set_level(level)

    def set_level(self, level: str) -> None:
        if level not in {"ok", "warn", "danger", "info"}:
            level = "info"
        self.setProperty("statusLevel", level)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_state(self, text: str, level: str) -> None:
        self.setText(text)
        self.set_level(level)


class GlowCard(QFrame):
    clicked = Signal()

    def __init__(self, *, elevated: bool = False) -> None:
        super().__init__()
        self.setProperty("card", "elevated" if elevated else "true")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 0)
        self._shadow.setBlurRadius(16)
        self._shadow.setColor(QColor(143, 109, 255, 52))
        self.setGraphicsEffect(self._shadow)

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._apply_glow)
        self._current_blur = 16.0

    def _apply_glow(self, value: Any) -> None:
        blur = float(value)
        self._current_blur = blur
        self._shadow.setBlurRadius(blur)
        alpha = max(35, min(145, int(blur * 5)))
        self._shadow.setColor(QColor(170, 137, 255, alpha))
        self._shadow.setOffset(0, -0.06 * max(0.0, blur - 14.0))

    def _animate_to(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._current_blur)
        self._anim.setEndValue(target)
        self._anim.start()

    def enterEvent(self, event) -> None:  # type: ignore[override]
        super().enterEvent(event)
        self._animate_to(28.0)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        super().leaveEvent(event)
        self._animate_to(16.0)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        super().mousePressEvent(event)
        self.clicked.emit()


class MetricCard(GlowCard):
    def __init__(self, title: str, value: str = "-", meta: str = "") -> None:
        super().__init__(elevated=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(2)

        self.title = QLabel(title)
        self.title.setObjectName("CardTitle")
        self.value = QLabel(value)
        self.value.setObjectName("CardValue")
        self.meta = QLabel(meta)
        self.meta.setObjectName("CardMeta")

        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.meta)
        layout.addStretch(1)

    def set_data(self, value: str, meta: str = "") -> None:
        self.value.setText(value)
        self.meta.setText(meta)


class SectionHeader(QWidget):
    def __init__(self, title: str, hint: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title = QLabel(title)
        self.title.setObjectName("SectionTitle")
        layout.addWidget(self.title)

        self.hint = QLabel(hint)
        self.hint.setObjectName("SectionHint")
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
        self.setMinimumHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.pills: dict[str, StatusPill] = {
            "profiles": StatusPill("profiles: --", "info"),
            "sessions": StatusPill("sessions: --", "info"),
            "queue": StatusPill("queue: --", "info"),
            "verification": StatusPill("verify: --", "warn"),
            "ai": StatusPill("ai: --", "info"),
            "runtime": StatusPill("runtime: --", "info"),
            "alerts": StatusPill("alerts: --", "warn"),
        }
        for pill in self.pills.values():
            layout.addWidget(pill)

        layout.addStretch(1)
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.setObjectName("PrimaryCTA")
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(self.refresh_button)

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
        self.pills["profiles"].set_state(f"profiles: {profile_count}", "ok" if profile_count > 0 else "info")
        self.pills["sessions"].set_state(f"sessions: {session_count}", "ok" if session_count > 0 else "warn")
        self.pills["queue"].set_state(f"queue: {queue_count}", "warn" if queue_count > 0 else "ok")

        verification_level = "ok" if verification == "PASS" else "warn"
        self.pills["verification"].set_state(f"verify: {verification}", verification_level)

        self.pills["ai"].set_state(f"ai: {ai_state}", "info" if ai_state != "ready" else "ok")
        self.pills["runtime"].set_state(f"runtime: {runtime_state}", "ok" if runtime_state == "ready" else "warn")
        self.pills["alerts"].set_state(f"alerts: {alerts_count}", "danger" if alerts_count > 0 else "ok")


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
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        title = QLabel("Context + Next Actions")
        title.setObjectName("ContextPanelTitle")
        layout.addWidget(title)

        self.profile_title = QLabel("No profile selected")
        self.profile_title.setObjectName("SectionTitle")
        self.profile_title.setWordWrap(True)
        layout.addWidget(self.profile_title)

        self.profile_meta = QLabel("Select profile from Profiles page.")
        self.profile_meta.setObjectName("SectionHint")
        self.profile_meta.setWordWrap(True)
        layout.addWidget(self.profile_meta)

        self.alerts_block = QLabel("Alerts: none")
        self.alerts_block.setObjectName("SectionHint")
        self.alerts_block.setWordWrap(True)
        layout.addWidget(self.alerts_block)

        self.recommendations_hint = QLabel("AI hints will appear here.")
        self.recommendations_hint.setObjectName("SectionHint")
        self.recommendations_hint.setWordWrap(True)
        layout.addWidget(self.recommendations_hint)

        self.next_actions = QLabel("Next: refresh workspace and open session.")
        self.next_actions.setObjectName("SectionHint")
        self.next_actions.setWordWrap(True)
        layout.addWidget(self.next_actions)

        btn_row = QHBoxLayout()
        quick_ai = QPushButton("Open AI Studio")
        quick_ai.setObjectName("PrimaryCTA")
        quick_ai.clicked.connect(lambda: self.action_requested.emit("open_ai_studio"))
        quick_updates = QPushButton("Check Updates")
        quick_updates.clicked.connect(lambda: self.action_requested.emit("check_updates"))
        btn_row.addWidget(quick_ai)
        btn_row.addWidget(quick_updates)
        layout.addLayout(btn_row)

        layout.addStretch(1)

    def update_context(self, *, profile_name: str, profile_meta: str, alerts: list[str], recommendation_hint: str, next_actions: str) -> None:
        self.profile_title.setText(profile_name)
        self.profile_meta.setText(profile_meta)
        self.alerts_block.setText("Alerts: none" if not alerts else "Alerts:\n- " + "\n- ".join(alerts[:4]))
        self.recommendations_hint.setText(recommendation_hint)
        self.next_actions.setText(next_actions)
