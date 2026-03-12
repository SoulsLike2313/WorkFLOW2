from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import AccountState, AnalyticsReport, CreativeAsset, MetricSnapshot, PlanBundle


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    database_path: str
    snapshot_dir: str


class LoadDemoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    creatives_loaded: int
    hypotheses_loaded: int
    tasks_loaded: int
    metrics_loaded: int
    events_loaded: int


class IngestMetricItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    creative_id: str | None = None
    captured_at: datetime | None = None
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    watch_time_seconds: float | None = Field(default=None, ge=0)
    source: str = "api_ingest"
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestMetricsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    items: list[IngestMetricItem]


class IngestMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    inserted: int


class GeneratePlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    max_steps: int | None = Field(default=None, ge=1, le=100)


class GeneratePlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report: AnalyticsReport
    plan: PlanBundle


class AccountSnapshotResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account: AccountState
    creatives: list[CreativeAsset]
    metrics: list[MetricSnapshot]
