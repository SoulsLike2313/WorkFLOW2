from __future__ import annotations

from typing import Any

from ..diagnostics import diag_log
from ..models import ActionResult, ActorType, AuditLog, ErrorLog
from ..repository import WorkspaceRepository


class AuditService:
    def __init__(self, repository: WorkspaceRepository) -> None:
        self.repository = repository

    def log_action(
        self,
        *,
        action_type: str,
        profile_id: str | None = None,
        actor_type: ActorType = ActorType.SYSTEM,
        action_payload: dict[str, Any] | None = None,
        result: ActionResult = ActionResult.INFO,
        error_text: str | None = None,
    ) -> AuditLog:
        event = AuditLog(
            profile_id=profile_id,
            actor_type=actor_type,
            action_type=action_type,
            action_payload=action_payload or {},
            result=result,
            error_text=error_text,
        )
        self.repository.append_audit(event)
        diag_log(
            "audit_logs",
            "audit_action",
            payload={
                "action_type": action_type,
                "profile_id": profile_id,
                "actor_type": actor_type.value,
                "result": result.value,
                "error_text": error_text,
            },
        )
        if error_text:
            self.repository.append_error(
                ErrorLog(
                    profile_id=profile_id,
                    source=action_type,
                    message=error_text,
                    details=action_payload or {},
                )
            )
            diag_log(
                "runtime_logs",
                "audit_action_error",
                level="ERROR",
                payload={
                    "action_type": action_type,
                    "profile_id": profile_id,
                    "error_text": error_text,
                },
            )
        return event

    def log_error(
        self,
        *,
        source: str,
        message: str,
        profile_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> ErrorLog:
        event = ErrorLog(profile_id=profile_id, source=source, message=message, details=details or {})
        self.repository.append_error(event)
        diag_log(
            "error_logs",
            "error",
            level="ERROR",
            payload={"source": source, "profile_id": profile_id, "message": message, "details": details or {}},
        )
        self.repository.append_audit(
            AuditLog(
                profile_id=profile_id,
                actor_type=ActorType.SYSTEM,
                action_type=source,
                action_payload=details or {},
                result=ActionResult.FAILURE,
                error_text=message,
            )
        )
        return event

    def list_audit(self, *, profile_id: str | None = None, limit: int = 100) -> list[AuditLog]:
        return self.repository.list_audit_logs(profile_id=profile_id, limit=limit)

    def list_errors(self, *, profile_id: str | None = None, limit: int = 100) -> list[ErrorLog]:
        return self.repository.list_error_logs(profile_id=profile_id, limit=limit)
