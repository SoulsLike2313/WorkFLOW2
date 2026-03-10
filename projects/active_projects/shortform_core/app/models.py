from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Platform(str, Enum):
    TIKTOK = "tiktok"
    REELS = "reels"
    SHORTS = "shorts"


class CreativeStatus(str, Enum):
    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class HypothesisStatus(str, Enum):
    OPEN = "open"
    VALIDATED = "validated"
    REJECTED = "rejected"
    PAUSED = "paused"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class ActionType(str, Enum):
    COLLECT_DATA = "collect_data"
    SCALE_CREATIVE = "scale_creative"
    REFINE_HOOK = "refine_hook"
    TUNE_CTA = "tune_cta"
    RUN_AB_TEST = "run_ab_test"
    MONITOR_PROFILE = "monitor_profile"
    EXECUTE_TASK = "execute_task"


class PerformanceLabel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT_DATA = "insufficient_data"


class AccountState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str = Field(default_factory=lambda: f"acc-{uuid4().hex[:8]}")
    platform: Platform = Platform.TIKTOK
    handle: str = "@unknown"
    followers: int = Field(default=0, ge=0)
    following: int = Field(default=0, ge=0)
    total_likes: int = Field(default=0, ge=0)
    last_sync_at: datetime = Field(default_factory=utc_now)
    tags: list[str] = Field(default_factory=list)


class CreativeAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    creative_id: str = Field(default_factory=lambda: f"cr-{uuid4().hex[:8]}")
    account_id: str
    platform: Platform = Platform.TIKTOK
    title: str
    topic: str = ""
    hook: str = ""
    cta: str = ""
    hypothesis_id: str | None = None
    status: CreativeStatus = CreativeStatus.TESTING
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Hypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hypothesis_id: str = Field(default_factory=lambda: f"hp-{uuid4().hex[:8]}")
    account_id: str
    statement: str
    success_criteria: str
    status: HypothesisStatus = HypothesisStatus.OPEN
    related_creative_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    owner: str = "content-team"


class TaskItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(default_factory=lambda: f"ts-{uuid4().hex[:8]}")
    account_id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: int = Field(default=3, ge=1, le=5)
    due_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: str = Field(default_factory=lambda: f"ms-{uuid4().hex[:8]}")
    account_id: str
    platform: Platform = Platform.TIKTOK
    creative_id: str | None = None
    captured_at: datetime = Field(default_factory=utc_now)
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    watch_time_seconds: float | None = Field(default=None, ge=0.0)
    source: str = "manual"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def engagement_rate(self) -> float:
        if self.views <= 0:
            return 0.0
        return (self.likes + self.comments + self.shares + self.saves) / float(self.views)


class ExternalEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: f"ev-{uuid4().hex[:8]}")
    account_id: str
    source: str
    event_type: str
    event_time: datetime = Field(default_factory=utc_now)
    payload: dict[str, Any] = Field(default_factory=dict)


class CreativeEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    creative_id: str
    score: int = Field(ge=0, le=100)
    label: PerformanceLabel
    summary: str
    recommendations: list[str] = Field(default_factory=list)
    metrics_count: int = 0
    total_views: int = 0
    average_engagement_rate: float = 0.0


class AccountAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    health_score: int = Field(ge=0, le=100)
    label: PerformanceLabel
    summary: str
    risk_flags: list[str] = Field(default_factory=list)
    next_focus: list[str] = Field(default_factory=list)


class AnalyticsReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: datetime = Field(default_factory=utc_now)
    account_assessment: AccountAssessment
    creative_evaluations: list[CreativeEvaluation]
    metric_count: int


class PlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(default_factory=lambda: f"st-{uuid4().hex[:8]}")
    action_type: ActionType
    title: str
    rationale: str
    priority: int = Field(default=3, ge=1, le=5)
    payload: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class PlanBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bundle_id: str = Field(default_factory=lambda: f"pl-{uuid4().hex[:8]}")
    account_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    summary: str
    steps: list[PlanStep] = Field(default_factory=list)


class CoreBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account: AccountState
    creatives: list[CreativeAsset] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    tasks: list[TaskItem] = Field(default_factory=list)
    metrics: list[MetricSnapshot] = Field(default_factory=list)
    events: list[ExternalEvent] = Field(default_factory=list)
