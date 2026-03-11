from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import (
    AttachedSourceType,
    ConnectionType,
    LearningType,
    ManagementMode,
    MetricsSourceType,
    OutcomeLabel,
    Platform,
    RecommendationFeedbackStatus,
    SourceType,
    ViewportPreset,
)


class CreateProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1, max_length=120)
    platform: Platform = Platform.TIKTOK
    connection_type: ConnectionType
    management_mode: ManagementMode = ManagementMode.MANUAL
    notes: str = ""
    tags: list[str] = Field(default_factory=list)


class ConnectProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cdp_url: str | None = None
    auth_provider: str | None = None
    device_id: str | None = None
    remote_provider: str | None = None
    confirmed: bool = False


class SetManagementModeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    management_mode: ManagementMode


class OpenSessionWindowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    viewport_preset: ViewportPreset = ViewportPreset.SMARTPHONE_DEFAULT
    width: int | None = None
    height: int | None = None
    attached_source_type: AttachedSourceType = AttachedSourceType.NONE
    attached_source_id: str | None = None
    confirmed: bool = False


class SetViewportPresetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    viewport_preset: ViewportPreset
    width: int | None = None
    height: int | None = None


class AttachSessionSourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: AttachedSourceType
    source_id: str


class AddContentItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    local_path: str
    title: str
    caption: str = ""
    hashtags: list[str] = Field(default_factory=list)
    thumbnail_path: str | None = None
    duration: float | None = Field(default=None, ge=0.0)
    content_type: str = "video"
    format_label: str = ""
    topic_label: str = ""
    hook_label: str = ""
    cta_label: str = ""
    scheduled_at: datetime | None = None


class QueueContentItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scheduled_at: datetime | None = None
    confirmed: bool = False


class IngestMetricsSnapshotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    content_id: str
    source_type: MetricsSourceType = MetricsSourceType.MANUAL
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    favorites: int = Field(default=0, ge=0)
    avg_watch_time: float | None = Field(default=None, ge=0.0)
    completion_rate: float | None = Field(default=None, ge=0.0)
    publish_time: datetime | None = None
    collected_at: datetime | None = None


class ImportMetricsFromFileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    path: str
    source_type: MetricsSourceType = MetricsSourceType.CSV_JSON_IMPORT


class GenerateActionPlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    window: str = "30d"


class AnalyzeFrameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    source_kind: SourceType = SourceType.SCREENSHOT
    source_ref: str


class AnalyzeAssetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    source_ref: str


class EvaluateContentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_id: str


class GenerateRecommendationsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    limit: int = Field(default=10, ge=1, le=50)


class GenerateVideoBriefRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    source_recommendation_ids: list[str] = Field(default_factory=list)
    creative_goal: str
    target_format: str
    target_duration: str
    visual_style: str
    hook: str
    cta: str


class IngestAIFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    learning_type: LearningType
    input_ref: str
    outcome_summary: str
    adjustment_summary: str
    confidence_delta: float = 0.0


class IngestAIRecommendationFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    recommendation_id: str
    feedback_status: RecommendationFeedbackStatus
    user_notes: str = ""
    manual_score: float | None = Field(default=None, ge=0.0, le=1.0)


class IngestAIOutcomeFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    recommendation_id: str
    content_id: str
    metrics_snapshot_ids: list[str] = Field(default_factory=list)
    outcome_label: OutcomeLabel
    outcome_summary: str


class GenerateAudioBriefRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_goal: str
    music_mood: str = ""
    voice_style: str = ""


class GenerateScriptBriefRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_goal: str
    hook: str = ""
    cta: str = ""


class GenerateTextBriefRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_goal: str
    cta_options: list[str] = Field(default_factory=list)


class BuildGenerationBundleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content_goal: str
    creative_angle: str
    format_target: str
    duration_target: str
