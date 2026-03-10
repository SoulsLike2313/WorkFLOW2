from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..errors import NotFoundError
from ..models import (
    ActionResult,
    ContentItem,
    ContentStatus,
    ValidationState,
)
from ..policy import PolicyGuard
from ..repository import WorkspaceRepository
from .audit_service import AuditService


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ContentService:
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

    def add_content_item(self, item: ContentItem) -> ContentItem:
        profile = self.repository.get_profile(item.profile_id)
        if profile is None:
            raise NotFoundError("profile", item.profile_id)
        self.policy_guard.enforce(profile.management_mode, "create_content_item", confirmed=True)

        created = item.model_copy(update={"updated_at": _utc_now()})
        self.repository.save_content_item(created)
        self.audit_service.log_action(
            action_type="add_content_item",
            profile_id=item.profile_id,
            action_payload={"content_id": created.id, "status": created.status.value},
            result=ActionResult.SUCCESS,
        )
        return created

    def list_content_items(
        self,
        *,
        profile_id: str | None = None,
        status: ContentStatus | None = None,
    ) -> list[ContentItem]:
        return self.repository.list_content_items(profile_id=profile_id, status=status)

    def get_content_item(self, content_id: str) -> ContentItem:
        item = self.repository.get_content_item(content_id)
        if item is None:
            raise NotFoundError("content_item", content_id)
        return item

    def validate_content_item(self, content_id: str) -> dict[str, object]:
        item = self.get_content_item(content_id)
        profile = self.repository.get_profile(item.profile_id)
        if profile is None:
            raise NotFoundError("profile", item.profile_id)
        self.policy_guard.enforce(profile.management_mode, "validate_content_item", confirmed=True)

        issues: list[str] = []
        warnings: list[str] = []

        if not item.local_path:
            issues.append("local_path is required")
        else:
            suffix = Path(item.local_path).suffix.lower()
            if suffix not in {".mp4", ".mov", ".mkv", ".webm"}:
                warnings.append(f"unusual format '{suffix or 'none'}' for short-form video")

        if not item.title.strip():
            issues.append("title is required")
        if item.duration is not None and item.duration > 180:
            warnings.append("duration is greater than 180s for short-form format")
        if item.duration is not None and item.duration < 5:
            warnings.append("duration is very short (<5s)")
        if not item.hook_label:
            warnings.append("hook_label is missing")
        if not item.format_label:
            warnings.append("format_label is missing")

        state = ValidationState.VALID
        if issues:
            state = ValidationState.INVALID
        elif warnings:
            state = ValidationState.WARNING

        updated = item.model_copy(update={"validation_state": state, "updated_at": _utc_now()})
        if state == ValidationState.VALID and item.status == ContentStatus.DRAFT:
            updated = updated.model_copy(update={"status": ContentStatus.READY, "updated_at": _utc_now()})
        self.repository.save_content_item(updated)

        payload = {
            "content_id": content_id,
            "validation_state": state.value,
            "issues": issues,
            "warnings": warnings,
            "ready_for_queue": state != ValidationState.INVALID,
        }
        self.audit_service.log_action(
            action_type="validate_content_item",
            profile_id=item.profile_id,
            action_payload=payload,
            result=ActionResult.SUCCESS if state != ValidationState.INVALID else ActionResult.FAILURE,
            error_text="; ".join(issues) if issues else None,
        )
        return payload

    def check_publish_readiness(self, content_id: str) -> dict[str, object]:
        item = self.get_content_item(content_id)
        issues: list[str] = []
        if item.validation_state == ValidationState.INVALID:
            issues.append("content item validation is invalid")
        if not item.local_path:
            issues.append("missing local_path")
        if not item.title:
            issues.append("missing title")
        if item.status == ContentStatus.FAILED:
            issues.append("content status is failed")

        return {
            "content_id": item.id,
            "profile_id": item.profile_id,
            "is_ready": len(issues) == 0,
            "issues": issues,
            "status": item.status.value,
            "validation_state": item.validation_state.value,
        }

    def queue_content_item(
        self,
        content_id: str,
        *,
        scheduled_at: datetime | None = None,
        confirmed: bool = False,
    ) -> ContentItem:
        item = self.get_content_item(content_id)
        profile = self.repository.get_profile(item.profile_id)
        if profile is None:
            raise NotFoundError("profile", item.profile_id)
        self.policy_guard.enforce(profile.management_mode, "queue_content_item", confirmed=confirmed)

        readiness = self.check_publish_readiness(content_id)
        if not readiness["is_ready"]:
            updated_failed = item.model_copy(update={"status": ContentStatus.FAILED, "updated_at": _utc_now()})
            self.repository.save_content_item(updated_failed)
            self.audit_service.log_action(
                action_type="queue_content_item",
                profile_id=item.profile_id,
                action_payload=readiness,
                result=ActionResult.FAILURE,
                error_text="content item not ready for queue",
            )
            return updated_failed

        queued = item.model_copy(
            update={
                "status": ContentStatus.QUEUED,
                "scheduled_at": scheduled_at or item.scheduled_at,
                "updated_at": _utc_now(),
            }
        )
        self.repository.save_content_item(queued)
        self.audit_service.log_action(
            action_type="queue_content_item",
            profile_id=item.profile_id,
            action_payload={"content_id": content_id, "scheduled_at": queued.scheduled_at.isoformat() if queued.scheduled_at else None},
            result=ActionResult.SUCCESS,
        )
        return queued
