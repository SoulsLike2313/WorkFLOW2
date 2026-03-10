from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..errors import NotFoundError, ValidationError
from ..models import (
    ActionResult,
    AttachedSourceType,
    SessionRuntimeState,
    SessionWindow,
    ViewportPreset,
)
from ..policy import PolicyGuard
from ..repository import WorkspaceRepository
from .audit_service import AuditService


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


VIEWPORT_PRESETS: dict[ViewportPreset, tuple[int, int]] = {
    ViewportPreset.SMARTPHONE_DEFAULT: (414, 736),
    ViewportPreset.ANDROID_TALL: (412, 915),
    ViewportPreset.IPHONE_LIKE: (390, 844),
}


class SessionWindowService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        policy_guard: PolicyGuard,
        audit_service: AuditService,
    ) -> None:
        self.repository = repository
        self.policy_guard = policy_guard
        self.audit_service = audit_service

    def open_session_window(
        self,
        profile_id: str,
        *,
        viewport_preset: ViewportPreset = ViewportPreset.SMARTPHONE_DEFAULT,
        width: int | None = None,
        height: int | None = None,
        attached_source_type: AttachedSourceType = AttachedSourceType.NONE,
        attached_source_id: str | None = None,
        confirmed: bool = False,
    ) -> SessionWindow:
        profile = self._require_profile(profile_id)
        self.policy_guard.enforce(profile.management_mode, "open_session_window", confirmed=confirmed)

        dimensions = self._resolve_dimensions(viewport_preset, width, height)
        now = _utc_now()
        current = self.repository.get_session(profile_id)
        session = (current or SessionWindow(profile_id=profile_id)).model_copy(
            update={
                "viewport_preset": viewport_preset,
                "width": dimensions[0],
                "height": dimensions[1],
                "aspect_ratio": "9:16",
                "attached_source_type": attached_source_type,
                "attached_source_id": attached_source_id,
                "runtime_state": SessionRuntimeState.OPEN,
                "is_open": True,
                "updated_at": now,
            }
        )
        self.repository.save_session(session)
        self.repository.save_profile(profile.model_copy(update={"session_state": SessionRuntimeState.OPEN, "updated_at": now}))
        self.audit_service.log_action(
            action_type="open_session_window",
            profile_id=profile_id,
            action_payload={"preset": viewport_preset.value, "width": session.width, "height": session.height},
            result=ActionResult.SUCCESS,
        )
        return session

    def restore_session_window(self, profile_id: str) -> SessionWindow:
        session = self.repository.get_session(profile_id)
        if session is None:
            raise NotFoundError("session_window", profile_id)
        return self.open_session_window(
            profile_id=profile_id,
            viewport_preset=session.viewport_preset,
            width=session.width,
            height=session.height,
            attached_source_type=session.attached_source_type,
            attached_source_id=session.attached_source_id,
            confirmed=True,
        )

    def close_session_window(self, profile_id: str, *, confirmed: bool = False) -> SessionWindow:
        profile = self._require_profile(profile_id)
        self.policy_guard.enforce(profile.management_mode, "close_session_window", confirmed=confirmed)
        session = self.repository.get_session(profile_id)
        if session is None:
            raise NotFoundError("session_window", profile_id)

        updated = session.model_copy(
            update={
                "runtime_state": SessionRuntimeState.CLOSED,
                "is_open": False,
                "updated_at": _utc_now(),
            }
        )
        self.repository.save_session(updated)
        self.repository.save_profile(
            profile.model_copy(update={"session_state": SessionRuntimeState.CLOSED, "updated_at": _utc_now()})
        )
        self.audit_service.log_action(
            action_type="close_session_window",
            profile_id=profile_id,
            action_payload={"preset": session.viewport_preset.value},
            result=ActionResult.SUCCESS,
        )
        return updated

    def set_viewport_preset(
        self,
        profile_id: str,
        *,
        viewport_preset: ViewportPreset,
        width: int | None = None,
        height: int | None = None,
    ) -> SessionWindow:
        session = self.repository.get_session(profile_id)
        if session is None:
            raise NotFoundError("session_window", profile_id)
        dimensions = self._resolve_dimensions(viewport_preset, width, height)
        updated = session.model_copy(
            update={
                "viewport_preset": viewport_preset,
                "width": dimensions[0],
                "height": dimensions[1],
                "updated_at": _utc_now(),
            }
        )
        self.repository.save_session(updated)
        self.audit_service.log_action(
            action_type="set_viewport_preset",
            profile_id=profile_id,
            action_payload={"preset": viewport_preset.value, "width": dimensions[0], "height": dimensions[1]},
            result=ActionResult.SUCCESS,
        )
        return updated

    def attach_source(
        self,
        profile_id: str,
        *,
        source_type: AttachedSourceType,
        source_id: str,
    ) -> SessionWindow:
        session = self.repository.get_session(profile_id)
        if session is None:
            raise NotFoundError("session_window", profile_id)
        updated = session.model_copy(
            update={"attached_source_type": source_type, "attached_source_id": source_id, "updated_at": _utc_now()}
        )
        self.repository.save_session(updated)
        self.audit_service.log_action(
            action_type="attach_session_source",
            profile_id=profile_id,
            action_payload={"source_type": source_type.value, "source_id": source_id},
            result=ActionResult.SUCCESS,
        )
        return updated

    def get_session_state(self, profile_id: str) -> SessionWindow:
        session = self.repository.get_session(profile_id)
        if session is None:
            raise NotFoundError("session_window", profile_id)
        return session

    def _resolve_dimensions(
        self,
        viewport_preset: ViewportPreset,
        width: int | None,
        height: int | None,
    ) -> tuple[int, int]:
        if viewport_preset == ViewportPreset.CUSTOM:
            if width is None or height is None:
                raise ValidationError("Custom viewport requires width and height.")
            if width < 100 or height < 100:
                raise ValidationError("Custom viewport width/height must be >= 100.")
            return width, height
        return VIEWPORT_PRESETS[viewport_preset]

    def _require_profile(self, profile_id: str):
        profile = self.repository.get_profile(profile_id)
        if profile is None:
            raise NotFoundError("profile", profile_id)
        return profile


class SessionRuntimeController:
    """
    Thin orchestration layer between UI/runtime and SessionWindowService.
    """

    def __init__(self, service: SessionWindowService) -> None:
        self.service = service

    def open(self, profile_id: str, **kwargs: Any) -> SessionWindow:
        return self.service.open_session_window(profile_id, **kwargs)

    def restore(self, profile_id: str) -> SessionWindow:
        return self.service.restore_session_window(profile_id)

    def close(self, profile_id: str, *, confirmed: bool = False) -> SessionWindow:
        return self.service.close_session_window(profile_id, confirmed=confirmed)

    def state(self, profile_id: str) -> SessionWindow:
        return self.service.get_session_state(profile_id)
