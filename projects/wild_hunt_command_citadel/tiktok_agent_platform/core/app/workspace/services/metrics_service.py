from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..diagnostics import diag_log
from ..errors import NotFoundError, ValidationError
from ..metrics_providers import CsvJsonImportMetricsProvider, MetricsProviderRegistry
from ..models import (
    ActionResult,
    ContentMetricsSnapshot,
    MetricsSourceType,
    ProfilePerformanceSnapshot,
)
from ..repository import WorkspaceRepository
from .analytics_services import AnalyticsFormulaService, TopContentService
from .audit_service import AuditService


class MetricsIngestionService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        formulas: AnalyticsFormulaService,
        top_content_service: TopContentService,
        provider_registry: MetricsProviderRegistry,
        audit_service: AuditService,
    ) -> None:
        self.repository = repository
        self.formulas = formulas
        self.top_content_service = top_content_service
        self.provider_registry = provider_registry
        self.audit_service = audit_service

    def ingest_metrics_snapshot(self, snapshot: ContentMetricsSnapshot) -> ContentMetricsSnapshot:
        profile = self.repository.get_profile(snapshot.profile_id)
        if profile is None:
            raise NotFoundError("profile", snapshot.profile_id)
        content = self.repository.get_content_item(snapshot.content_id)
        if content is None:
            raise NotFoundError("content_item", snapshot.content_id)

        normalized = self.formulas.enrich_snapshot(snapshot)
        self.repository.save_metrics_snapshot(normalized)
        diag_log(
            "import_provider_logs",
            "metrics_snapshot_ingested",
            payload={
                "profile_id": snapshot.profile_id,
                "content_id": snapshot.content_id,
                "source_type": snapshot.source_type.value,
                "weighted_engagement_score": normalized.weighted_engagement_score,
            },
        )
        self.audit_service.log_action(
            action_type="ingest_metrics_snapshot",
            profile_id=snapshot.profile_id,
            action_payload={
                "content_id": snapshot.content_id,
                "source_type": snapshot.source_type.value,
                "weighted_engagement_score": normalized.weighted_engagement_score,
            },
            result=ActionResult.SUCCESS,
        )
        return normalized

    def import_metrics_from_file(
        self,
        *,
        profile_id: str,
        path: str,
        source_type: MetricsSourceType = MetricsSourceType.CSV_JSON_IMPORT,
    ) -> dict[str, Any]:
        profile = self.repository.get_profile(profile_id)
        if profile is None:
            raise NotFoundError("profile", profile_id)
        file_path = Path(path)
        if not file_path.exists():
            raise ValidationError(f"Metrics file does not exist: {path}")

        if source_type != MetricsSourceType.CSV_JSON_IMPORT:
            raise ValidationError("File import currently supports csv_json_import_provider only.")

        rows = CsvJsonImportMetricsProvider.read_file(file_path)
        diag_log(
            "import_provider_logs",
            "metrics_import_started",
            payload={"profile_id": profile_id, "path": str(file_path), "row_count": len(rows)},
        )
        inserted = 0
        for row in rows:
            content_id = str(row.get("content_id") or row.get("contentId") or "").strip()
            if not content_id:
                continue
            if self.repository.get_content_item(content_id) is None:
                continue

            snapshot = ContentMetricsSnapshot(
                profile_id=profile_id,
                content_id=content_id,
                source_type=source_type,
                views=self._as_int(row.get("views")),
                likes=self._as_int(row.get("likes")),
                comments_count=self._as_int(row.get("comments_count") or row.get("comments")),
                shares=self._as_int(row.get("shares")),
                favorites=self._as_int(row.get("favorites") or row.get("saves")),
                avg_watch_time=self._as_float_or_none(row.get("avg_watch_time")),
                completion_rate=self._as_float_or_none(row.get("completion_rate")),
                publish_time=self._parse_datetime(row.get("publish_time")),
                collected_at=self._parse_datetime(row.get("collected_at")) or datetime.now(timezone.utc),
            )
            normalized = self.formulas.enrich_snapshot(snapshot)
            self.repository.save_metrics_snapshot(normalized)
            inserted += 1
        diag_log(
            "import_provider_logs",
            "metrics_import_finished",
            payload={"profile_id": profile_id, "path": str(file_path), "inserted": inserted},
        )

        self.audit_service.log_action(
            action_type="import_metrics_from_file",
            profile_id=profile_id,
            action_payload={"path": str(file_path), "inserted": inserted, "source_type": source_type.value},
            result=ActionResult.SUCCESS,
        )
        return {"profile_id": profile_id, "path": str(file_path), "inserted": inserted}

    def get_profile_performance_summary(self, profile_id: str, window: str = "30d") -> ProfilePerformanceSnapshot:
        profile = self.repository.get_profile(profile_id)
        if profile is None:
            raise NotFoundError("profile", profile_id)

        snapshots = self.repository.list_metrics_snapshots(profile_id=profile_id, limit=500)
        total_views = sum(item.views for item in snapshots)
        total_engagement = sum(item.engagement_rate for item in snapshots)
        top_content = self.top_content_service.get_top_content(profile_id, window=window, limit=5)
        momentum = self.formulas.profile_momentum_score(snapshots)

        perf = ProfilePerformanceSnapshot(
            profile_id=profile_id,
            follower_count=0,
            total_views_window=total_views,
            total_engagement_window=total_engagement,
            top_content_ids=[item.content_id for item in top_content],
            snapshot_window=window,
            momentum_score=momentum,
        )
        self.repository.save_profile_performance(perf)
        diag_log(
            "runtime_logs",
            "profile_performance_summary_built",
            payload={
                "profile_id": profile_id,
                "window": window,
                "total_views_window": total_views,
                "momentum_score": momentum,
            },
        )
        self.audit_service.log_action(
            action_type="build_profile_performance_summary",
            profile_id=profile_id,
            action_payload={"window": window, "top_content_count": len(perf.top_content_ids)},
            result=ActionResult.SUCCESS,
        )
        return perf

    @staticmethod
    def _as_int(value: Any) -> int:
        if value is None:
            return 0
        if isinstance(value, bool):
            return int(value)
        try:
            return max(int(float(value)), 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _as_float_or_none(value: Any) -> float | None:
        if value in (None, ""):
            return None
        try:
            return max(float(value), 0.0)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
