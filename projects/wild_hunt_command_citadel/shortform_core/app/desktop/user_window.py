from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..workspace.diagnostics import diag_log
from .components import ContextPanel, NavRailButton, TopStatusBar
from .pages import (
    AIStudioPage,
    AnalyticsPage,
    BasePage,
    ContentPage,
    DashboardPage,
    ProfilesPage,
    SessionsPage,
)
from .pages_extra import AuditPage, SettingsPage, UpdatesPage
from .theme import build_stylesheet, build_theme_tokens


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


class UserWorkspaceWindow(QMainWindow):
    def __init__(self, *, api_base_url: str) -> None:
        super().__init__()
        self.api_base_url = api_base_url.rstrip("/")
        self.setWindowTitle("Shortform: мультипрофильный центр")
        self.resize(1540, 920)
        self.setMinimumSize(1260, 760)

        self._snapshot: dict[str, Any] = {}
        self._selected_profile_id: str | None = None
        self._last_action_plan_by_profile: dict[str, dict[str, Any]] = {}
        self._last_patch_result: dict[str, Any] = {}
        self._last_update_check: dict[str, Any] = {}

        self._nav_buttons: dict[str, NavRailButton] = {}
        self._pages: dict[str, BasePage] = {}
        self._page_order: list[str] = []
        self._page_fade_anim: QPropertyAnimation | None = None

        self._build_ui()
        self.setStyleSheet(build_stylesheet(build_theme_tokens()))
        self.refresh_workspace()

        self._auto_refresh = QTimer(self)
        self._auto_refresh.setInterval(20_000)
        self._auto_refresh.timeout.connect(self.refresh_workspace)
        self._auto_refresh.start()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("RootShell")
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(274)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 16, 14, 16)
        sidebar_layout.setSpacing(11)

        app_title = QLabel("ЦИТАДЕЛЬ ДИКОЙ ОХОТЫ")
        app_title.setObjectName("AppTitle")
        app_subtitle = QLabel("Премиальный центр управления профилями, сессиями, аналитикой и AI.")
        app_subtitle.setObjectName("AppSubtitle")
        app_subtitle.setWordWrap(True)

        brand_block = QWidget()
        brand_block.setObjectName("SidebarBrandBlock")
        brand_layout = QHBoxLayout(brand_block)
        brand_layout.setContentsMargins(12, 10, 12, 12)
        brand_layout.setSpacing(10)

        emblem = QLabel("W")
        emblem.setObjectName("SidebarEmblem")
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emblem.setFixedSize(42, 42)
        brand_layout.addWidget(emblem)

        title_block = QWidget()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(1)
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        brand_layout.addWidget(title_block, stretch=1)

        sidebar_layout.addWidget(brand_block)

        self._register_nav_button(sidebar_layout, "dashboard", "Обзор")
        self._register_nav_button(sidebar_layout, "profiles", "Профили")
        self._register_nav_button(sidebar_layout, "sessions", "Сессии")
        self._register_nav_button(sidebar_layout, "content", "Контент")
        self._register_nav_button(sidebar_layout, "analytics", "Аналитика")
        self._register_nav_button(sidebar_layout, "ai_studio", "AI-студия")
        self._register_nav_button(sidebar_layout, "audit", "Журнал")
        self._register_nav_button(sidebar_layout, "updates", "Обновления")
        self._register_nav_button(sidebar_layout, "settings", "Настройки")
        sidebar_layout.addStretch(1)

        self.sidebar_status = QLabel("Система: инициализация")
        self.sidebar_status.setObjectName("SidebarRuntimeStatus")
        self.sidebar_status.setWordWrap(True)
        sidebar_layout.addWidget(self.sidebar_status)

        layout.addWidget(sidebar)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)

        self.top_status = TopStatusBar()
        self.top_status.refresh_requested.connect(self.refresh_workspace)
        center_layout.addWidget(self.top_status)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)

        self.workspace_stack = QStackedWidget()
        split.addWidget(self.workspace_stack)

        self.context_panel = ContextPanel()
        self.context_panel.action_requested.connect(lambda action: self._on_page_action(action, None))
        self.context_panel.setMinimumWidth(320)
        split.addWidget(self.context_panel)

        split.setSizes([1080, 340])
        center_layout.addWidget(split, stretch=1)
        layout.addWidget(center, stretch=1)

        self._register_pages()
        self._switch_page("dashboard")

    def _register_nav_button(self, layout: QVBoxLayout, key: str, label: str) -> None:
        button = NavRailButton(label, page_key=key)
        button.clicked.connect(lambda _=False, k=key: self._switch_page(k))
        layout.addWidget(button)
        self._nav_buttons[key] = button

    def _register_pages(self) -> None:
        registry: list[tuple[str, BasePage]] = [
            ("dashboard", DashboardPage()),
            ("profiles", ProfilesPage()),
            ("sessions", SessionsPage()),
            ("content", ContentPage()),
            ("analytics", AnalyticsPage()),
            ("ai_studio", AIStudioPage()),
            ("audit", AuditPage()),
            ("updates", UpdatesPage()),
            ("settings", SettingsPage()),
        ]
        for key, page in registry:
            page.action_requested.connect(self._on_page_action)
            self._pages[key] = page
            self._page_order.append(key)
            self.workspace_stack.addWidget(page)

    def _switch_page(self, key: str) -> None:
        if key not in self._pages:
            return
        index = self._page_order.index(key)
        self.workspace_stack.setCurrentIndex(index)
        self._animate_page_transition(self.workspace_stack.currentWidget())
        for nav_key, button in self._nav_buttons.items():
            button.setChecked(nav_key == key)
        diag_log("runtime_logs", "desktop_switch_page", payload={"page": key})

    def _animate_page_transition(self, page: QWidget | None) -> None:
        if page is None:
            return
        if self._page_fade_anim is not None:
            self._page_fade_anim.stop()
            self._page_fade_anim = None

        effect = QGraphicsOpacityEffect(page)
        effect.setOpacity(0.0)
        page.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(170)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)

        def _cleanup() -> None:
            page.setGraphicsEffect(None)
            self._page_fade_anim = None

        anim.finished.connect(_cleanup)
        self._page_fade_anim = anim
        anim.start()

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.api_base_url, timeout=7.0)

    def _request_json(
        self,
        client: httpx.Client,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> tuple[Any | None, str | None]:
        try:
            response = client.request(method, path, params=params, json=json_body)
            response.raise_for_status()
            if not response.content:
                return {}, None
            return response.json(), None
        except Exception as exc:
            return None, str(exc)

    def refresh_workspace(self) -> None:
        started = datetime.now()
        self.top_status.set_loading(True)
        api_errors: list[str] = []
        try:
            with self._client() as client:
                root_health, err = self._request_json(client, "GET", "/health")
                if err:
                    api_errors.append(f"Ошибка /health: {err}")
                workspace_health, err = self._request_json(client, "GET", "/workspace/health")
                if err:
                    api_errors.append(f"Ошибка /workspace/health: {err}")
                readiness, err = self._request_json(client, "GET", "/workspace/readiness")
                if err:
                    api_errors.append(f"Ошибка /workspace/readiness: {err}")
                profiles_payload, err = self._request_json(client, "GET", "/workspace/profiles")
                if err:
                    api_errors.append(f"Ошибка /workspace/profiles: {err}")
                audit_payload, err = self._request_json(client, "GET", "/workspace/audit/log", params={"limit": 80})
                if err:
                    api_errors.append(f"Ошибка /workspace/audit/log: {err}")
                error_payload, err = self._request_json(client, "GET", "/workspace/audit/errors", params={"limit": 80})
                if err:
                    api_errors.append(f"Ошибка /workspace/audit/errors: {err}")
                content_payload, err = self._request_json(client, "GET", "/workspace/content")
                if err:
                    api_errors.append(f"Ошибка /workspace/content: {err}")
                updates_version, err = self._request_json(client, "GET", "/updates/version")
                if err:
                    api_errors.append(f"Ошибка /updates/version: {err}")
                updates_post_verify, err = self._request_json(client, "GET", "/updates/post-verify")
                if err:
                    api_errors.append(f"Ошибка /updates/post-verify: {err}")
        except Exception as exc:
            self.sidebar_status.setText(f"Система: ошибка подключения | {exc}")
            diag_log("runtime_logs", "desktop_refresh_exception", level="ERROR", payload={"error": str(exc)})
            self.top_status.set_loading(False)
            return

        profiles = _safe_list(_safe_dict(profiles_payload).get("items"))
        profile_ids = {str(item.get("id")) for item in profiles if item.get("id")}
        if self._selected_profile_id not in profile_ids:
            self._selected_profile_id = str(profiles[0].get("id")) if profiles else None

        selected_profile = next((item for item in profiles if item.get("id") == self._selected_profile_id), None)

        sessions_by_profile: dict[str, dict[str, Any]] = {}
        analytics_performance: dict[str, Any] = {}
        analytics_top: list[dict[str, Any]] = []
        analytics_patterns: list[dict[str, Any]] = []
        analytics_recommendations: list[dict[str, Any]] = []
        ai_recommendations: list[dict[str, Any]] = []
        ai_learning_summary: dict[str, Any] = {}
        generation_bundles: list[dict[str, Any]] = []

        try:
            with self._client() as client:
                for item in profiles:
                    pid = item.get("id")
                    if not pid:
                        continue
                    session_payload, err = self._request_json(client, "GET", f"/workspace/sessions/{pid}")
                    if err:
                        sessions_by_profile[str(pid)] = {}
                        continue
                    sessions_by_profile[str(pid)] = _safe_dict(session_payload).get("session", {}) or {}

                if self._selected_profile_id:
                    perf_payload, err = self._request_json(
                        client,
                        "GET",
                        f"/workspace/analytics/profiles/{self._selected_profile_id}/performance",
                        params={"window": "30d"},
                    )
                    if err:
                        api_errors.append(f"Ошибка analytics/performance: {err}")
                    analytics_performance = _safe_dict(perf_payload).get("snapshot", {}) or _safe_dict(perf_payload)

                    top_payload, err = self._request_json(
                        client,
                        "GET",
                        f"/workspace/analytics/profiles/{self._selected_profile_id}/top-content",
                        params={"window": "30d", "limit": 10},
                    )
                    if err:
                        api_errors.append(f"Ошибка analytics/top-content: {err}")
                    analytics_top = _safe_list(_safe_dict(top_payload).get("items"))

                    patterns_payload, err = self._request_json(
                        client,
                        "GET",
                        f"/workspace/analytics/profiles/{self._selected_profile_id}/patterns",
                        params={"window": "30d"},
                    )
                    if err:
                        api_errors.append(f"Ошибка analytics/patterns: {err}")
                    analytics_patterns = _safe_list(_safe_dict(patterns_payload).get("items"))

                    rec_payload, err = self._request_json(
                        client,
                        "GET",
                        f"/workspace/analytics/profiles/{self._selected_profile_id}/recommendations/latest",
                        params={"limit": 12},
                    )
                    if err:
                        api_errors.append(f"Ошибка analytics/recommendations/latest: {err}")
                    analytics_recommendations = _safe_list(_safe_dict(rec_payload).get("items"))

                    ai_rec_payload, err = self._request_json(
                        client,
                        "GET",
                        f"/workspace/profiles/{self._selected_profile_id}/ai/recommendations",
                        params={"limit": 16},
                    )
                    if err:
                        api_errors.append(f"Ошибка ai/recommendations: {err}")
                    ai_recommendations = _safe_list(_safe_dict(ai_rec_payload).get("items"))

                    ai_learning_payload, err = self._request_json(
                        client,
                        "GET",
                        f"/workspace/profiles/{self._selected_profile_id}/ai/learnings",
                    )
                    if err:
                        api_errors.append(f"Ошибка ai/learnings: {err}")
                    ai_learning_summary = _safe_dict(ai_learning_payload)

                    bundles_payload, err = self._request_json(
                        client,
                        "GET",
                        f"/workspace/profiles/{self._selected_profile_id}/generation/bundles",
                        params={"limit": 20},
                    )
                    if err:
                        api_errors.append(f"Ошибка generation/bundles: {err}")
                    generation_bundles = _safe_list(_safe_dict(bundles_payload).get("items"))
        except Exception as exc:
            api_errors.append(f"Ошибка загрузки данных профиля: {exc}")

        workspace_health_data = _safe_dict(workspace_health)
        workspace_summary = _safe_dict(workspace_health_data.get("summary"))
        readiness_data = _safe_dict(readiness)
        updates_post_data = _safe_dict(updates_post_verify)
        updates_version_data = _safe_dict(updates_version)

        selected_session = sessions_by_profile.get(self._selected_profile_id or "", {})
        selected_profile_name = (
            str(selected_profile.get("display_name"))
            if isinstance(selected_profile, dict) and selected_profile.get("display_name")
            else "Профиль не выбран"
        )
        verification_state = str(updates_post_data.get("status", "UNKNOWN")).upper()
        if verification_state not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
            verification_state = "UNKNOWN"

        alerts: list[str] = []
        if api_errors:
            alerts.extend(api_errors[:4])
        for name, ready in _safe_dict(readiness_data.get("items")).items():
            if not bool(ready):
                alerts.append(f"{name} не готов")

        runtime_config = {
            "mode": "user",
            "db_path": _safe_dict(root_health).get("database_path", "runtime/shortform_core.db"),
            "logs_dir": "runtime/logs",
            "data_dir": "runtime",
        }

        self._snapshot = {
            "api_base_url": self.api_base_url,
            "workspace_summary": workspace_summary,
            "workspace_readiness": readiness_data,
            "verification_state": verification_state,
            "profiles": profiles,
            "selected_profile_id": self._selected_profile_id,
            "selected_profile_name": selected_profile_name,
            "selected_session": selected_session,
            "sessions_by_profile": sessions_by_profile,
            "content_items": _safe_list(_safe_dict(content_payload).get("items")),
            "analytics_performance": analytics_performance,
            "analytics_top_content": analytics_top,
            "analytics_patterns": analytics_patterns,
            "analytics_recommendations": analytics_recommendations,
            "analytics_action_plan": self._last_action_plan_by_profile.get(self._selected_profile_id or ""),
            "ai_recommendations": ai_recommendations,
            "ai_learning_summary": ai_learning_summary,
            "generation_bundles": generation_bundles,
            "audit_log": _safe_list(_safe_dict(audit_payload).get("items")),
            "error_log": _safe_list(_safe_dict(error_payload).get("items")),
            "runtime_config": runtime_config,
            "updates": {
                "version": _safe_dict(updates_version_data.get("version")),
                "check": self._last_update_check,
                "patch_result": self._last_patch_result,
                "post_verify": updates_post_data,
                "post_verify_status": verification_state,
            },
            "alerts": alerts,
        }

        self._push_snapshot()
        elapsed_ms = int((datetime.now() - started).total_seconds() * 1000)
        runtime_status_map = {
            "ready": "готова",
            "degraded": "ограничена",
        }
        runtime_status = str(readiness_data.get("status", "degraded"))
        self.sidebar_status.setText(
            "Система: "
            f"{runtime_status_map.get(runtime_status, runtime_status)} | "
            f"обновлено={datetime.now().strftime('%H:%M:%S')} | "
            f"запрос={elapsed_ms}мс"
        )
        diag_log(
            "runtime_logs",
            "desktop_refresh_completed",
            payload={
                "profile_count": len(profiles),
                "selected_profile_id": self._selected_profile_id,
                "alerts_count": len(alerts),
                "api_errors_count": len(api_errors),
                "elapsed_ms": elapsed_ms,
            },
        )
        self.top_status.set_loading(False)

    def _push_snapshot(self) -> None:
        for key, page in self._pages.items():
            try:
                page.update_snapshot(self._snapshot)
            except Exception as exc:
                diag_log(
                    "runtime_logs",
                    "desktop_page_update_failed",
                    level="WARNING",
                    payload={"page": key, "error": str(exc)},
                )

        summary = _safe_dict(self._snapshot.get("workspace_summary"))
        sessions = _safe_dict(self._snapshot.get("sessions_by_profile"))
        session_count = sum(1 for item in sessions.values() if _safe_dict(item).get("is_open"))
        readiness = _safe_dict(self._snapshot.get("workspace_readiness"))

        self.top_status.update_state(
            profile_count=int(summary.get("profile_count", len(_safe_list(self._snapshot.get("profiles"))))),
            session_count=session_count,
            queue_count=int(summary.get("queued_content_items", 0)),
            verification=str(self._snapshot.get("verification_state", "UNKNOWN")),
            ai_state="ready" if bool(_safe_dict(readiness.get("items")).get("ai_ready", False)) else "degraded",
            runtime_state=str(readiness.get("status", "degraded")),
            alerts_count=len(_safe_list(self._snapshot.get("alerts"))),
        )
        self._update_context_panel()

    def _update_context_panel(self) -> None:
        selected_id = self._snapshot.get("selected_profile_id")
        profiles = _safe_list(self._snapshot.get("profiles"))
        profile = next((item for item in profiles if item.get("id") == selected_id), None)

        if isinstance(profile, dict):
            profile_name = str(profile.get("display_name", "Профиль"))
            profile_meta = (
                f"подключение={profile.get('connection_type', '-')} | "
                f"режим={profile.get('management_mode', '-')} | "
                f"состояние={profile.get('health_state', '-')}"
            )
        else:
            profile_name = "Профиль не выбран"
            profile_meta = "Выберите профиль в разделе «Профили»."

        recs = _safe_list(self._snapshot.get("ai_recommendations")) or _safe_list(
            self._snapshot.get("analytics_recommendations")
        )
        rec_hint = (
            str(recs[0].get("title", recs[0].get("recommendation_type", "Пока без рекомендации")))
            if recs
            else "Сформируйте рекомендации после загрузки метрик."
        )

        next_actions = "1) Добавить профиль 2) Открыть сессию 3) Добавить контент 4) Загрузить метрики 5) Сформировать план"
        if profiles and not self._snapshot.get("selected_session"):
            next_actions = "Откройте сессию для выбранного профиля, затем перейдите в «Контент» или «AI-студию»."
        if self._snapshot.get("verification_state") != "PASS":
            next_actions = "Гейт верификации не PASS. Работайте в контролируемом режиме и проверьте обновления/диагностику."

        self.context_panel.update_context(
            profile_name=profile_name,
            profile_meta=profile_meta,
            alerts=_safe_list(self._snapshot.get("alerts")),
            recommendation_hint=rec_hint,
            next_actions=next_actions,
        )

    def create_demo_profile(self) -> None:
        payload = {
            "display_name": f"Демо-профиль {datetime.now().strftime('%H:%M:%S')}",
            "platform": "tiktok",
            "connection_type": "cdp",
            "management_mode": "guided",
            "notes": "Создано из пользовательского десктоп-режима.",
            "tags": ["desktop", "user_mode"],
        }
        try:
            with self._client() as client:
                response = client.post("/workspace/profiles", json=payload)
            response.raise_for_status()
            self.refresh_workspace()
            diag_log("runtime_logs", "desktop_profile_created", payload={"display_name": payload["display_name"]})
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось создать профиль", str(exc))

    def check_api_health(self) -> None:
        try:
            with self._client() as client:
                response = client.get("/health")
            response.raise_for_status()
            body = response.json()
            QMessageBox.information(
                self,
                "Состояние API",
                f"статус={body.get('status')}\nбаза={body.get('database_path')}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "API недоступен", str(exc))

    def _on_page_action(self, action: str, payload: object) -> None:
        if action == "refresh":
            self.refresh_workspace()
            return
        if action == "select_profile":
            self._selected_profile_id = str(payload) if payload else None
            self.refresh_workspace()
            return
        if action == "add_profile":
            self.create_demo_profile()
            return
        if action == "connect_profile":
            self._connect_profile(payload)
            return
        if action == "open_session":
            self._open_session(payload)
            return
        if action == "close_session":
            self._close_session(payload)
            return
        if action == "open_analytics":
            self._switch_page("analytics")
            return
        if action == "open_content":
            self._switch_page("content")
            return
        if action == "open_ai_studio":
            self._switch_page("ai_studio")
            return
        if action == "validate_content":
            self._validate_content(payload)
            return
        if action == "queue_content":
            self._queue_content(payload)
            return
        if action == "add_placeholder_content":
            self._add_placeholder_content()
            return
        if action == "import_metrics":
            self._ingest_demo_metrics()
            return
        if action == "generate_plan":
            self._generate_action_plan()
            return
        if action == "generate_ai_recommendations":
            self._generate_ai_recommendations()
            return
        if action == "build_generation_bundle":
            self._build_generation_bundle()
            return
        if action == "check_updates":
            self._refresh_updates()
            return
        if action == "run_post_verify":
            self._refresh_updates(force_post_verify=True)
            return
        if action == "open_diagnostics":
            QMessageBox.information(
                self,
                "Диагностика",
                "Артефакты диагностики и верификации лежат в каталоге runtime/.",
            )
            return

    def _selected_profile_or_warn(self) -> str | None:
        if self._selected_profile_id:
            return self._selected_profile_id
        QMessageBox.warning(self, "Требуется профиль", "Сначала выберите профиль на экране «Профили».")
        return None

    def _connect_profile(self, payload: object) -> None:
        profile_id = str(payload) if payload else self._selected_profile_or_warn()
        if not profile_id:
            return
        cdp_url, ok = QInputDialog.getText(self, "Подключение профиля", "CDP URL:", text="http://127.0.0.1:9222")
        if not ok or not cdp_url.strip():
            return
        try:
            with self._client() as client:
                response = client.post(
                    f"/workspace/profiles/{profile_id}/connect",
                    json={"cdp_url": cdp_url.strip(), "confirmed": True},
                )
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось подключить профиль", str(exc))

    def _open_session(self, payload: object) -> None:
        profile_id = self._selected_profile_or_warn()
        viewport = "smartphone_default"
        if isinstance(payload, dict):
            candidate = payload.get("profile_id") or profile_id
            profile_id = str(candidate) if candidate else None
            viewport = str(payload.get("viewport_preset") or viewport)
        if not profile_id:
            return
        try:
            with self._client() as client:
                response = client.post(
                    f"/workspace/sessions/{profile_id}/open",
                    json={"viewport_preset": viewport, "confirmed": True},
                )
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось открыть сессию", str(exc))

    def _close_session(self, payload: object) -> None:
        profile_id = self._selected_profile_or_warn()
        if isinstance(payload, dict) and payload.get("profile_id"):
            profile_id = str(payload["profile_id"])
        if not profile_id:
            return
        try:
            with self._client() as client:
                response = client.post(f"/workspace/sessions/{profile_id}/close", params={"confirmed": "true"})
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось закрыть сессию", str(exc))

    def _validate_content(self, payload: object) -> None:
        content_id = str(payload) if payload else ""
        if not content_id:
            QMessageBox.warning(self, "Требуется контент", "Сначала выберите элемент контента.")
            return
        try:
            with self._client() as client:
                response = client.post(f"/workspace/content/{content_id}/validate")
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка валидации", str(exc))

    def _queue_content(self, payload: object) -> None:
        content_id = str(payload) if payload else ""
        if not content_id:
            QMessageBox.warning(self, "Требуется контент", "Сначала выберите элемент контента.")
            return
        try:
            with self._client() as client:
                response = client.post(
                    f"/workspace/content/{content_id}/queue",
                    json={"confirmed": True},
                )
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось поставить в очередь", str(exc))

    def _add_placeholder_content(self) -> None:
        profile_id = self._selected_profile_or_warn()
        if not profile_id:
            return
        stamp = datetime.now().strftime("%H%M%S")
        payload = {
            "profile_id": profile_id,
            "local_path": f"runtime/assets/demo_{stamp}.mp4",
            "title": f"Демо-клип {stamp}",
            "caption": "Быстро добавленный контент из десктоп-интерфейса.",
            "hashtags": ["shortform", "workspace", "demo"],
            "duration": 17.0,
            "format_label": "talking_head",
            "topic_label": "workspace",
            "hook_label": "first_2s",
            "cta_label": "follow_for_more",
        }
        try:
            with self._client() as client:
                response = client.post("/workspace/content", json=payload)
            response.raise_for_status()
            self._switch_page("content")
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось добавить контент", str(exc))

    def _ingest_demo_metrics(self) -> None:
        profile_id = self._selected_profile_or_warn()
        if not profile_id:
            return
        items = [item for item in _safe_list(self._snapshot.get("content_items")) if item.get("profile_id") == profile_id]
        if not items:
            QMessageBox.warning(self, "Нет контента", "Добавьте контент перед загрузкой метрик.")
            return
        content_id = str(items[0].get("id"))
        payload = {
            "profile_id": profile_id,
            "content_id": content_id,
            "views": 1200,
            "likes": 185,
            "comments_count": 14,
            "shares": 21,
            "favorites": 36,
            "avg_watch_time": 9.7,
            "completion_rate": 0.61,
        }
        try:
            with self._client() as client:
                response = client.post("/workspace/metrics/ingest", json=payload)
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось загрузить метрики", str(exc))

    def _generate_action_plan(self) -> None:
        profile_id = self._selected_profile_or_warn()
        if not profile_id:
            return
        try:
            with self._client() as client:
                response = client.post(
                    f"/workspace/analytics/profiles/{profile_id}/action-plan",
                    json={"window": "30d"},
                )
            response.raise_for_status()
            body = response.json()
            plan = _safe_dict(body).get("plan")
            if isinstance(plan, dict):
                self._last_action_plan_by_profile[profile_id] = plan
            self._switch_page("analytics")
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось сформировать план", str(exc))

    def _generate_ai_recommendations(self) -> None:
        profile_id = self._selected_profile_or_warn()
        if not profile_id:
            return
        try:
            with self._client() as client:
                response = client.post("/workspace/ai/recommendations/generate", json={"profile_id": profile_id, "limit": 10})
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось получить AI-рекомендации", str(exc))

    def _build_generation_bundle(self) -> None:
        profile_id = self._selected_profile_or_warn()
        if not profile_id:
            return
        payload = {
            "content_goal": "Повысить досмотры в следующих 5 публикациях",
            "creative_angle": "сильный хук в начале и чёткая прогрессия сцен",
            "format_target": "short_talking_head_with_overlay",
            "duration_target": "15-20s",
        }
        try:
            with self._client() as client:
                response = client.post(f"/workspace/profiles/{profile_id}/generation/bundles/build", json=payload)
            response.raise_for_status()
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось собрать пакет генерации", str(exc))

    def _refresh_updates(self, *, force_post_verify: bool = False) -> None:
        manifest_path, ok = QInputDialog.getText(
            self,
            "Манифест обновления",
            "Необязательный путь к локальному манифесту для проверки:",
            text="",
        )
        if not ok:
            return
        try:
            with self._client() as client:
                if manifest_path.strip():
                    check_resp = client.post("/updates/check", params={"manifest_path": manifest_path.strip()})
                    check_resp.raise_for_status()
                    self._last_update_check = _safe_dict(check_resp.json())

                if force_post_verify or not self._last_patch_result:
                    post_resp = client.get("/updates/post-verify")
                    post_resp.raise_for_status()
                    self._last_patch_result = {"post_update_verification": _safe_dict(post_resp.json())}

            self._switch_page("updates")
            self.refresh_workspace()
        except Exception as exc:
            QMessageBox.critical(self, "Не удалось проверить обновления", str(exc))
