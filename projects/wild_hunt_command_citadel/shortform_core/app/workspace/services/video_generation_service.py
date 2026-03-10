from __future__ import annotations

from typing import Any

from ..contracts import BaseVideoGeneratorAdapter
from ..errors import NotFoundError
from ..models import ActionResult
from ..repository import WorkspaceRepository
from .audit_service import AuditService


class VideoGenerationService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        adapter: BaseVideoGeneratorAdapter,
        audit_service: AuditService,
    ) -> None:
        self.repository = repository
        self.adapter = adapter
        self.audit_service = audit_service

    def submit_generation_brief(self, brief_id: str) -> dict[str, Any]:
        brief = self.repository.get_video_brief(brief_id)
        if brief is None:
            raise NotFoundError("video_generation_brief", brief_id)
        response = self.adapter.submit_generation_brief(brief)
        self.audit_service.log_action(
            action_type="video_generator_submit_brief",
            profile_id=brief.profile_id,
            action_payload={"brief_id": brief_id, "adapter": self.adapter.adapter_name, "response": response},
            result=ActionResult.SUCCESS,
        )
        return response

    def check_generation_status(self, external_job_id: str) -> dict[str, Any]:
        return self.adapter.check_generation_status(external_job_id)

    def fetch_generated_assets(self, external_job_id: str) -> list[dict[str, Any]]:
        return self.adapter.fetch_generated_assets(external_job_id)
