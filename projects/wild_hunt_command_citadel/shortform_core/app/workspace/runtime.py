from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .connectors import ConnectorRegistry
from .diagnostics import configure_diagnostics
from .device_providers import DeviceProviderRegistry
from .metrics_providers import MetricsProviderRegistry
from .policy import PolicyGuard
from .repository import WorkspaceRepository
from .services import (
    AICreativeDirectorService,
    AILearningService,
    AIPerceptionService,
    AIRecommendationService,
    AIWorkflowService,
    AnalyticsFormulaService,
    AuditService,
    ContentIntelligenceService,
    ContentPlanningService,
    ContentService,
    MetricsIngestionService,
    ProfileService,
    SessionRuntimeController,
    SessionWindowService,
    TopContentService,
    VideoGenerationService,
)
from .video_generator import MockVideoGeneratorAdapter


@dataclass
class WorkspaceRuntime:
    repository: WorkspaceRepository
    audit: AuditService
    profiles: ProfileService
    sessions: SessionWindowService
    session_runtime: SessionRuntimeController
    content: ContentService
    metrics: MetricsIngestionService
    formulas: AnalyticsFormulaService
    top_content: TopContentService
    intelligence: ContentIntelligenceService
    planning: ContentPlanningService
    ai_perception: AIPerceptionService
    ai_workflow: AIWorkflowService
    ai_learning: AILearningService
    ai_creative: AICreativeDirectorService
    ai_recommendation: AIRecommendationService
    video_generation: VideoGenerationService
    device_registry: DeviceProviderRegistry
    metrics_provider_registry: MetricsProviderRegistry


def build_workspace_runtime(
    *,
    max_profiles: int = 10,
    analytics_weights: dict[str, float] | None = None,
    log_dir: Path | None = None,
    debug_logs: bool = False,
) -> WorkspaceRuntime:
    if log_dir is not None:
        configure_diagnostics(log_dir, debug=debug_logs)

    repository = WorkspaceRepository()
    policy_guard = PolicyGuard()
    audit = AuditService(repository)

    device_registry = DeviceProviderRegistry()
    connector_registry = ConnectorRegistry(device_registry)
    metrics_provider_registry = MetricsProviderRegistry()

    formulas = AnalyticsFormulaService(
        weights=analytics_weights
        or {
            "views_weight": 0.05,
            "likes_weight": 1.0,
            "comments_weight": 2.5,
            "shares_weight": 3.0,
            "favorites_weight": 1.5,
            "watch_time_weight": 0.5,
            "completion_weight": 1.0,
        }
    )
    top_content = TopContentService(repository=repository, formulas=formulas)
    intelligence = ContentIntelligenceService(repository=repository, top_content_service=top_content)
    planning = ContentPlanningService(
        repository=repository,
        formulas=formulas,
        top_content_service=top_content,
        intelligence_service=intelligence,
    )

    profile_service = ProfileService(
        repository=repository,
        connector_registry=connector_registry,
        policy_guard=policy_guard,
        audit_service=audit,
        max_profiles=max_profiles,
    )
    sessions = SessionWindowService(repository=repository, policy_guard=policy_guard, audit_service=audit)
    session_runtime = SessionRuntimeController(sessions)
    content = ContentService(repository=repository, policy_guard=policy_guard, audit_service=audit)
    metrics = MetricsIngestionService(
        repository=repository,
        formulas=formulas,
        top_content_service=top_content,
        provider_registry=metrics_provider_registry,
        audit_service=audit,
    )

    ai_perception = AIPerceptionService(repository=repository, audit_service=audit)
    ai_workflow = AIWorkflowService(repository=repository, planning_service=planning)
    ai_learning = AILearningService(repository=repository, audit_service=audit)
    ai_creative = AICreativeDirectorService(repository=repository, planning_service=planning, audit_service=audit)
    ai_recommendation = AIRecommendationService(repository=repository, planning_service=planning)

    video_generation = VideoGenerationService(
        repository=repository,
        adapter=MockVideoGeneratorAdapter(),
        audit_service=audit,
    )

    return WorkspaceRuntime(
        repository=repository,
        audit=audit,
        profiles=profile_service,
        sessions=sessions,
        session_runtime=session_runtime,
        content=content,
        metrics=metrics,
        formulas=formulas,
        top_content=top_content,
        intelligence=intelligence,
        planning=planning,
        ai_perception=ai_perception,
        ai_workflow=ai_workflow,
        ai_learning=ai_learning,
        ai_creative=ai_creative,
        ai_recommendation=ai_recommendation,
        video_generation=video_generation,
        device_registry=device_registry,
        metrics_provider_registry=metrics_provider_registry,
    )
