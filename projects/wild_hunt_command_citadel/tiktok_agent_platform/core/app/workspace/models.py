from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"


class Platform(str, Enum):
    TIKTOK = "tiktok"
    REELS = "reels"
    SHORTS = "shorts"


class ConnectionType(str, Enum):
    CDP = "cdp"
    OFFICIAL_AUTH = "official_auth"
    DEVICE = "device"


class ManagementMode(str, Enum):
    MANUAL = "manual"
    GUIDED = "guided"
    MANAGED = "managed"


class ProfileStatus(str, Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    WARNING = "warning"
    DISABLED = "disabled"


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"
    NOT_IMPLEMENTED = "not_implemented"


class SessionRuntimeState(str, Enum):
    IDLE = "idle"
    OPENING = "opening"
    OPEN = "open"
    CLOSED = "closed"
    ERROR = "error"


class ViewportPreset(str, Enum):
    SMARTPHONE_DEFAULT = "smartphone_default"
    ANDROID_TALL = "android_tall"
    IPHONE_LIKE = "iphone_like"
    CUSTOM = "custom"


class SourceType(str, Enum):
    SESSION_WINDOW = "session_window"
    ASSET_PREVIEW = "asset_preview"
    UPLOADED_FRAME = "uploaded_frame"
    SCREENSHOT = "screenshot"


class AttachedSourceType(str, Enum):
    CDP = "cdp"
    OFFICIAL_AUTH = "official_auth"
    DEVICE = "device"
    NONE = "none"


class DeviceProviderType(str, Enum):
    LOCAL_ANDROID = "local_android"
    EMULATOR = "emulator"
    REMOTE_DEVICE = "remote_device"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    UNKNOWN = "unknown"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    QUEUED = "queued"
    POSTED = "posted"
    FAILED = "failed"


class ValidationState(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"


class MetricsSourceType(str, Enum):
    OFFICIAL_API = "official_api_provider"
    IMPORTED_SNAPSHOT = "imported_snapshot_provider"
    CSV_JSON_IMPORT = "csv_json_import_provider"
    MANUAL = "manual_metrics_provider"
    DEMO = "demo_metrics_provider"


class PatternType(str, Enum):
    FORMAT = "format"
    TOPIC = "topic"
    HOOK = "hook"
    CTA = "cta"
    POSTING_WINDOW = "posting_window"
    DURATION = "duration"


class RecommendationType(str, Enum):
    REPEAT = "repeat"
    TEST = "test"
    STOP = "stop"
    IMPROVE = "improve"
    TIMING = "timing"


class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LearningType(str, Enum):
    PERFORMANCE_FEEDBACK = "performance_feedback"
    USER_FEEDBACK = "user_feedback"
    CONTENT_FEEDBACK = "content_feedback"
    PLANNER_FEEDBACK = "planner_feedback"


class RecommendationFeedbackStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EDITED = "edited"


class OutcomeLabel(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


class GenerationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    GENERATED = "generated"
    FAILED = "failed"
    NOT_IMPLEMENTED = "not_implemented"


class ActorType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    AI = "ai"


class ActionResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"
    INFO = "info"


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("prf"))
    display_name: str
    platform: Platform = Platform.TIKTOK
    connection_type: ConnectionType
    management_mode: ManagementMode = ManagementMode.MANUAL
    status: ProfileStatus = ProfileStatus.DISCONNECTED
    session_state: SessionRuntimeState = SessionRuntimeState.CLOSED
    health_state: HealthState = HealthState.UNKNOWN
    notes: str = ""
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ProfileConnection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    connection_type: ConnectionType
    cdp_url: str | None = None
    auth_provider: str | None = None
    device_id: str | None = None
    remote_provider: str | None = None
    connection_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_connected_at: datetime | None = None
    runtime_metadata: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None


class SessionWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    viewport_preset: ViewportPreset = ViewportPreset.SMARTPHONE_DEFAULT
    width: int = Field(default=414, ge=100)
    height: int = Field(default=736, ge=100)
    aspect_ratio: str = "9:16"
    attached_source_type: AttachedSourceType = AttachedSourceType.NONE
    attached_source_id: str | None = None
    runtime_state: SessionRuntimeState = SessionRuntimeState.CLOSED
    is_open: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DeviceSession(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("dev"))
    provider_type: DeviceProviderType
    provider_name: str
    device_label: str
    device_status: DeviceStatus = DeviceStatus.UNKNOWN
    stream_capabilities: list[str] = Field(default_factory=list)
    input_capabilities: list[str] = Field(default_factory=list)
    last_seen_at: datetime | None = None


class ContentItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("cnt"))
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
    status: ContentStatus = ContentStatus.DRAFT
    scheduled_at: datetime | None = None
    posted_at: datetime | None = None
    validation_state: ValidationState = ValidationState.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ContentMetricsSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("cms"))
    profile_id: str
    content_id: str
    source_type: MetricsSourceType
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    favorites: int = Field(default=0, ge=0)
    avg_watch_time: float | None = Field(default=None, ge=0)
    completion_rate: float | None = Field(default=None, ge=0)
    engagement_rate: float = Field(default=0.0, ge=0)
    weighted_engagement_score: float = Field(default=0.0, ge=0)
    publish_time: datetime | None = None
    collected_at: datetime = Field(default_factory=utc_now)


class ProfilePerformanceSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("pps"))
    profile_id: str
    follower_count: int = Field(default=0, ge=0)
    total_views_window: int = Field(default=0, ge=0)
    total_engagement_window: float = Field(default=0.0, ge=0)
    top_content_ids: list[str] = Field(default_factory=list)
    snapshot_window: str = "30d"
    momentum_score: float = Field(default=0.0)
    collected_at: datetime = Field(default_factory=utc_now)


class ContentPattern(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("pat"))
    profile_id: str
    pattern_type: PatternType
    label: str
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)


class ContentRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("rec"))
    profile_id: str
    recommendation_type: RecommendationType
    priority: PriorityLevel
    title: str
    rationale: str
    suggested_format: str = ""
    suggested_hook: str = ""
    suggested_duration_range: str = ""
    suggested_posting_window: str = ""
    based_on_snapshot_ids: list[str] = Field(default_factory=list)
    supporting_signals: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list)
    suggested_action: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class ActionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("apl"))
    profile_id: str
    performance_summary: str
    top_content_findings: list[str] = Field(default_factory=list)
    weak_content_findings: list[str] = Field(default_factory=list)
    recommended_content_angles: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    required_manual_checks: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)
    source_context: dict[str, Any] = Field(default_factory=dict)


class AssistiveScreenState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("scr"))
    profile_id: str
    screen_name: str
    detected_elements: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1.0)
    screenshot_ref: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class AIPerceptionFrame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("aif"))
    profile_id: str
    source_kind: SourceType
    source_ref: str
    detected_objects: list[str] = Field(default_factory=list)
    detected_text: list[str] = Field(default_factory=list)
    detected_layout: dict[str, Any] = Field(default_factory=dict)
    inferred_context: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)


class AIPerceptionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("apr"))
    profile_id: str
    frame_id: str
    probable_format: str = ""
    readability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    visual_overload_score: float = Field(default=0.0, ge=0.0, le=1.0)
    hook_strength_score: float = Field(default=0.0, ge=0.0, le=1.0)
    structured_summary: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class AIAssetReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("arv"))
    profile_id: str
    source_kind: SourceType
    source_ref: str
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    findings: list[str] = Field(default_factory=list)
    recommendation: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class AILearningRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("lrn"))
    profile_id: str
    learning_type: LearningType
    input_ref: str
    outcome_summary: str
    adjustment_summary: str
    confidence_delta: float = 0.0
    created_at: datetime = Field(default_factory=utc_now)


class AIHypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("aih"))
    profile_id: str
    label: str
    hypothesis_text: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class AIOutcomeLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("aol"))
    profile_id: str
    recommendation_id: str
    content_id: str | None = None
    metrics_snapshot_ids: list[str] = Field(default_factory=list)
    outcome_label: OutcomeLabel = OutcomeLabel.INCONCLUSIVE
    outcome_summary: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class AIRecommendationFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("arf"))
    profile_id: str
    recommendation_id: str
    feedback_status: RecommendationFeedbackStatus
    user_notes: str = ""
    manual_score: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)


class AIPatternConfidenceHistory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("pch"))
    profile_id: str
    pattern_label: str
    confidence_before: float = Field(ge=0.0, le=1.0)
    confidence_after: float = Field(ge=0.0, le=1.0)
    reason: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class VideoGenerationBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("vgb"))
    profile_id: str
    source_recommendation_ids: list[str] = Field(default_factory=list)
    creative_goal: str
    target_format: str
    target_duration: str
    visual_style: str
    hook: str
    narrative_steps: list[str] = Field(default_factory=list)
    shot_plan: list[str] = Field(default_factory=list)
    voiceover_notes: str = ""
    on_screen_text: list[str] = Field(default_factory=list)
    cta: str = ""
    safety_notes: list[str] = Field(default_factory=list)
    generation_status: GenerationStatus = GenerationStatus.DRAFT
    created_at: datetime = Field(default_factory=utc_now)


class AudioGenerationBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("agb"))
    profile_id: str
    content_goal: str
    music_mood: str = ""
    voice_style: str = ""
    pacing_notes: str = ""
    narration_notes: str = ""
    generation_status: GenerationStatus = GenerationStatus.DRAFT
    created_at: datetime = Field(default_factory=utc_now)


class ScriptGenerationBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("sgb"))
    profile_id: str
    content_goal: str
    hook: str = ""
    script_outline: list[str] = Field(default_factory=list)
    cta: str = ""
    generation_status: GenerationStatus = GenerationStatus.DRAFT
    created_at: datetime = Field(default_factory=utc_now)


class TextGenerationBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("tgb"))
    profile_id: str
    content_goal: str
    captions: list[str] = Field(default_factory=list)
    hashtag_groups: list[list[str]] = Field(default_factory=list)
    cta_options: list[str] = Field(default_factory=list)
    generation_status: GenerationStatus = GenerationStatus.DRAFT
    created_at: datetime = Field(default_factory=utc_now)


class ReferenceAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("ref"))
    profile_id: str
    asset_type: str
    path_or_url: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class PromptPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("ppk"))
    profile_id: str
    prompts: dict[str, str] = Field(default_factory=dict)
    model_hints: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class CreativeManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("cmf"))
    profile_id: str
    title: str
    scene_descriptions: list[str] = Field(default_factory=list)
    pacing_notes: str = ""
    safety_notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class GenerationAssetBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("gab"))
    profile_id: str
    content_goal: str
    creative_angle: str
    source_recommendations: list[str] = Field(default_factory=list)
    source_patterns: list[str] = Field(default_factory=list)
    source_metrics_summary: dict[str, Any] = Field(default_factory=dict)
    selected_visual_references: list[str] = Field(default_factory=list)
    selected_audio_references: list[str] = Field(default_factory=list)
    script_outline: list[str] = Field(default_factory=list)
    voiceover_draft: str = ""
    caption_draft: str = ""
    on_screen_text_blocks: list[str] = Field(default_factory=list)
    shot_plan: list[str] = Field(default_factory=list)
    duration_target: str = ""
    format_target: str = ""
    generation_ready_flag: bool = False
    validation_notes: list[str] = Field(default_factory=list)
    prompt_pack_id: str | None = None
    manifest_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class AuditLog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("aud"))
    profile_id: str | None = None
    actor_type: ActorType
    action_type: str
    action_payload: dict[str, Any] = Field(default_factory=dict)
    result: ActionResult = ActionResult.INFO
    error_text: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ErrorLog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: _new_id("err"))
    profile_id: str | None = None
    source: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class WorkspaceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_count: int
    active_profiles: int
    queued_content_items: int
    open_session_windows: int
    latest_audit_events: list[AuditLog] = Field(default_factory=list)
