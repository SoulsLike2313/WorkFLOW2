from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


class PatchStatus(str, Enum):
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class AppVersionInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: str
    app_version: str
    build_version: str
    patch_version: str
    compatibility_marker: str = "v1"


class UpdateManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_id: str = Field(default_factory=lambda: _new_id("manifest"))
    current_version: str
    available_version: str
    patch_notes: list[str] = Field(default_factory=list)
    required_migrations: list[str] = Field(default_factory=list)
    checksum: str = ""
    signature: str = ""
    compatibility_info: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=_utc_now)


class PatchBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bundle_id: str = Field(default_factory=lambda: _new_id("patch"))
    bundle_path: Path
    target_version: str
    migration_hooks: list[str] = Field(default_factory=list)
    checksum: str = ""
    notes: list[str] = Field(default_factory=list)


class PatchApplicationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patch_id: str
    status: PatchStatus
    message: str
    applied_at: datetime = Field(default_factory=_utc_now)
    backup_path: Path | None = None
    extracted_to: Path | None = None
    post_update_verification: dict[str, Any] = Field(default_factory=dict)


class UpdateAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(default_factory=lambda: _new_id("upd"))
    action: str
    result: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utc_now)

