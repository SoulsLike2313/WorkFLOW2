from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

from pydantic import BaseModel, ConfigDict, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Thresholds(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_views_for_evaluation: int = Field(default=300, ge=0)
    low_engagement_rate: float = Field(default=0.03, ge=0.0)
    strong_engagement_rate: float = Field(default=0.08, ge=0.0)
    metric_window_size: int = Field(default=60, ge=1)


class PlannerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_steps: int = Field(default=8, ge=1, le=100)


class AnalyticsWeightsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    views_weight: float = Field(default=0.05, ge=0.0)
    likes_weight: float = Field(default=1.0, ge=0.0)
    comments_weight: float = Field(default=2.5, ge=0.0)
    shares_weight: float = Field(default=3.0, ge=0.0)
    favorites_weight: float = Field(default=1.5, ge=0.0)
    watch_time_weight: float = Field(default=0.5, ge=0.0)
    completion_weight: float = Field(default=1.0, ge=0.0)


class WorkspaceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_profiles: int = Field(default=10, ge=1, le=100)
    analytics_weights: AnalyticsWeightsConfig = Field(default_factory=AnalyticsWeightsConfig)


class StorageConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_root: Path = PROJECT_ROOT
    database_path: Path = PROJECT_ROOT / "runtime" / "shortform_core.db"
    output_dir: Path = PROJECT_ROOT / "runtime" / "output"
    tiktok_snapshot_dir: Path = PROJECT_ROOT / "external_data" / "tiktok_automation_snapshot"


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thresholds: Thresholds = Field(default_factory=Thresholds)
    planner: PlannerConfig = Field(default_factory=PlannerConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)


def _env_int(env: Mapping[str, str], key: str, default: int) -> int:
    value = env.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(env: Mapping[str, str], key: str, default: float) -> float:
    value = env.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_path(env: Mapping[str, str], key: str, default: Path) -> Path:
    value = env.get(key)
    if not value:
        return default
    return Path(value).expanduser()


def load_config(env: Mapping[str, str] | None = None) -> AppConfig:
    source = env or os.environ

    thresholds = Thresholds(
        min_views_for_evaluation=_env_int(source, "SFCO_MIN_VIEWS_FOR_EVAL", 300),
        low_engagement_rate=_env_float(source, "SFCO_LOW_ENGAGEMENT_RATE", 0.03),
        strong_engagement_rate=_env_float(source, "SFCO_STRONG_ENGAGEMENT_RATE", 0.08),
        metric_window_size=_env_int(source, "SFCO_METRIC_WINDOW_SIZE", 60),
    )

    planner = PlannerConfig(
        max_steps=_env_int(source, "SFCO_MAX_PLAN_STEPS", 8),
    )

    workspace = WorkspaceConfig(
        max_profiles=_env_int(source, "SFCO_MAX_PROFILES", 10),
        analytics_weights=AnalyticsWeightsConfig(
            views_weight=_env_float(source, "SFCO_VIEWS_WEIGHT", 0.05),
            likes_weight=_env_float(source, "SFCO_LIKES_WEIGHT", 1.0),
            comments_weight=_env_float(source, "SFCO_COMMENTS_WEIGHT", 2.5),
            shares_weight=_env_float(source, "SFCO_SHARES_WEIGHT", 3.0),
            favorites_weight=_env_float(source, "SFCO_FAVORITES_WEIGHT", 1.5),
            watch_time_weight=_env_float(source, "SFCO_WATCH_TIME_WEIGHT", 0.5),
            completion_weight=_env_float(source, "SFCO_COMPLETION_WEIGHT", 1.0),
        ),
    )

    storage = StorageConfig(
        project_root=_env_path(source, "SFCO_PROJECT_ROOT", PROJECT_ROOT),
        database_path=_env_path(source, "SFCO_DATABASE_PATH", PROJECT_ROOT / "runtime" / "shortform_core.db"),
        output_dir=_env_path(source, "SFCO_OUTPUT_DIR", PROJECT_ROOT / "runtime" / "output"),
        tiktok_snapshot_dir=_env_path(
            source,
            "SFCO_TIKTOK_SNAPSHOT_DIR",
            PROJECT_ROOT / "external_data" / "tiktok_automation_snapshot",
        ),
    )

    storage.database_path.parent.mkdir(parents=True, exist_ok=True)
    storage.output_dir.mkdir(parents=True, exist_ok=True)

    return AppConfig(
        thresholds=thresholds,
        planner=planner,
        storage=storage,
        workspace=workspace,
        api_host=source.get("SFCO_API_HOST", "127.0.0.1"),
        api_port=_env_int(source, "SFCO_API_PORT", 8000),
    )
