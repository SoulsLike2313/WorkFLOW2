from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .contracts import BaseVideoGeneratorAdapter
from .models import ContentItem, GenerationStatus, VideoGenerationBrief


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MockVideoGeneratorAdapter(BaseVideoGeneratorAdapter):
    adapter_name = "mock_video_generator"

    def submit_generation_brief(self, brief: VideoGenerationBrief) -> dict[str, Any]:
        return {
            "status": GenerationStatus.NOT_IMPLEMENTED.value,
            "adapter": self.adapter_name,
            "external_job_id": f"mock-job-{brief.id}",
            "submitted_at": _utc_iso(),
            "message": "Generator adapter is currently a stub contract.",
        }

    def check_generation_status(self, external_job_id: str) -> dict[str, Any]:
        return {
            "status": GenerationStatus.NOT_IMPLEMENTED.value,
            "external_job_id": external_job_id,
            "adapter": self.adapter_name,
        }

    def fetch_generated_assets(self, external_job_id: str) -> list[dict[str, Any]]:
        return [
            {
                "external_job_id": external_job_id,
                "asset_path": None,
                "status": GenerationStatus.NOT_IMPLEMENTED.value,
                "message": "No generated assets available in mock adapter.",
            }
        ]

    def validate_output(self, content_item: ContentItem) -> dict[str, Any]:
        return {
            "content_id": content_item.id,
            "is_valid": bool(content_item.title and content_item.local_path),
            "checks": ["title_present", "path_present"],
        }

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "submit_generation_brief": True,
            "check_generation_status": True,
            "fetch_generated_assets": True,
            "validate_output": True,
            "real_generation": False,
        }
