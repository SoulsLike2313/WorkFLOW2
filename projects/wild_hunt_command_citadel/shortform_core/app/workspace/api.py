from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from .errors import LimitExceededError, NotFoundError, PolicyDeniedError, ValidationError, WorkspaceError
from .models import (
    ContentItem,
    ContentMetricsSnapshot,
    ContentStatus,
    DeviceProviderType,
)
from .runtime import WorkspaceRuntime
from .schemas import (
    AddContentItemRequest,
    AnalyzeAssetRequest,
    AnalyzeFrameRequest,
    AttachSessionSourceRequest,
    BuildGenerationBundleRequest,
    ConnectProfileRequest,
    CreateProfileRequest,
    EvaluateContentRequest,
    GenerateAudioBriefRequest,
    GenerateActionPlanRequest,
    GenerateRecommendationsRequest,
    GenerateScriptBriefRequest,
    GenerateTextBriefRequest,
    GenerateVideoBriefRequest,
    IngestAIOutcomeFeedbackRequest,
    IngestAIRecommendationFeedbackRequest,
    ImportMetricsFromFileRequest,
    IngestAIFeedbackRequest,
    IngestMetricsSnapshotRequest,
    OpenSessionWindowRequest,
    QueueContentItemRequest,
    SetManagementModeRequest,
    SetViewportPresetRequest,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _raise_http(error: Exception) -> None:
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=str(error))
    if isinstance(error, PolicyDeniedError):
        raise HTTPException(status_code=403, detail=str(error))
    if isinstance(error, (ValidationError, LimitExceededError)):
        raise HTTPException(status_code=400, detail=str(error))
    if isinstance(error, WorkspaceError):
        raise HTTPException(status_code=400, detail=str(error))
    raise HTTPException(status_code=500, detail=f"Unexpected workspace error: {error}")


def build_workspace_router(runtime: WorkspaceRuntime) -> APIRouter:
    router = APIRouter(prefix="/workspace", tags=["workspace"])

    @router.get("/health")
    def workspace_health() -> dict[str, Any]:
        return {
            "status": "ok",
            "summary": runtime.repository.build_summary().model_dump(mode="json"),
            "metrics_providers": runtime.metrics_provider_registry.list_capabilities(),
        }

    # Profiles
    @router.post("/profiles")
    def create_profile(request: CreateProfileRequest):
        try:
            profile = runtime.profiles.create_profile(
                display_name=request.display_name,
                platform=request.platform,
                connection_type=request.connection_type,
                management_mode=request.management_mode,
                notes=request.notes,
                tags=request.tags,
            )
            connection = runtime.profiles.get_connection(profile.id)
            return {"profile": profile, "connection": connection}
        except Exception as error:
            _raise_http(error)

    @router.get("/profiles")
    def list_profiles():
        return {"items": runtime.profiles.list_profiles(), "max_profiles": runtime.profiles.max_profiles}

    @router.get("/profiles/{profile_id}")
    def get_profile(profile_id: str):
        try:
            profile = runtime.profiles.get_profile(profile_id)
            connection = runtime.profiles.get_connection(profile_id)
            session = runtime.repository.get_session(profile_id)
            return {"profile": profile, "connection": connection, "session": session}
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/connect")
    def connect_profile(profile_id: str, request: ConnectProfileRequest):
        try:
            connection = runtime.profiles.connect_profile(
                profile_id,
                cdp_url=request.cdp_url,
                auth_provider=request.auth_provider,
                device_id=request.device_id,
                remote_provider=request.remote_provider,
                confirmed=request.confirmed,
            )
            return {"connection": connection, "profile": runtime.profiles.get_profile(profile_id)}
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/disconnect")
    def disconnect_profile(profile_id: str, confirmed: bool = False):
        try:
            connection = runtime.profiles.disconnect_profile(profile_id, confirmed=confirmed)
            return {"connection": connection, "profile": runtime.profiles.get_profile(profile_id)}
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/management-mode")
    def set_management_mode(profile_id: str, request: SetManagementModeRequest):
        try:
            profile = runtime.profiles.set_management_mode(profile_id, request.management_mode)
            return {"profile": profile}
        except Exception as error:
            _raise_http(error)

    @router.get("/profiles/{profile_id}/health")
    def profile_health(profile_id: str):
        try:
            return runtime.profiles.health_check(profile_id)
        except Exception as error:
            _raise_http(error)

    @router.get("/profiles/{profile_id}/runtime")
    def profile_runtime_info(profile_id: str):
        try:
            return runtime.profiles.get_runtime_info(profile_id)
        except Exception as error:
            _raise_http(error)

    # Sessions
    @router.post("/sessions/{profile_id}/open")
    def open_session(profile_id: str, request: OpenSessionWindowRequest):
        try:
            session = runtime.sessions.open_session_window(
                profile_id=profile_id,
                viewport_preset=request.viewport_preset,
                width=request.width,
                height=request.height,
                attached_source_type=request.attached_source_type,
                attached_source_id=request.attached_source_id,
                confirmed=request.confirmed,
            )
            return {"session": session}
        except Exception as error:
            _raise_http(error)

    @router.post("/sessions/{profile_id}/close")
    def close_session(profile_id: str, confirmed: bool = False):
        try:
            session = runtime.sessions.close_session_window(profile_id=profile_id, confirmed=confirmed)
            return {"session": session}
        except Exception as error:
            _raise_http(error)

    @router.post("/sessions/{profile_id}/viewport")
    def set_viewport(profile_id: str, request: SetViewportPresetRequest):
        try:
            session = runtime.sessions.set_viewport_preset(
                profile_id=profile_id,
                viewport_preset=request.viewport_preset,
                width=request.width,
                height=request.height,
            )
            return {"session": session}
        except Exception as error:
            _raise_http(error)

    @router.post("/sessions/{profile_id}/attach-source")
    def attach_source(profile_id: str, request: AttachSessionSourceRequest):
        try:
            session = runtime.sessions.attach_source(
                profile_id=profile_id,
                source_type=request.source_type,
                source_id=request.source_id,
            )
            return {"session": session}
        except Exception as error:
            _raise_http(error)

    @router.get("/sessions/{profile_id}")
    def get_session(profile_id: str):
        try:
            return {"session": runtime.sessions.get_session_state(profile_id)}
        except Exception as error:
            _raise_http(error)

    # Devices
    @router.get("/devices")
    def list_devices(provider_type: DeviceProviderType | None = None):
        if provider_type is None:
            return {"items": runtime.device_registry.list_all_devices()}
        provider = runtime.device_registry.get(provider_type)
        return {"items": provider.list_devices()}

    # Content
    @router.post("/content")
    def add_content_item(request: AddContentItemRequest):
        try:
            item = ContentItem(
                profile_id=request.profile_id,
                local_path=request.local_path,
                title=request.title,
                caption=request.caption,
                hashtags=request.hashtags,
                thumbnail_path=request.thumbnail_path,
                duration=request.duration,
                content_type=request.content_type,
                format_label=request.format_label,
                topic_label=request.topic_label,
                hook_label=request.hook_label,
                cta_label=request.cta_label,
                scheduled_at=request.scheduled_at,
            )
            created = runtime.content.add_content_item(item)
            return {"item": created}
        except Exception as error:
            _raise_http(error)

    @router.get("/content")
    def list_content(
        profile_id: str | None = None,
        status: ContentStatus | None = None,
    ):
        items = runtime.content.list_content_items(profile_id=profile_id, status=status)
        return {"items": items, "count": len(items)}

    @router.post("/content/{content_id}/validate")
    def validate_content(content_id: str):
        try:
            return runtime.content.validate_content_item(content_id)
        except Exception as error:
            _raise_http(error)

    @router.get("/content/{content_id}/readiness")
    def content_readiness(content_id: str):
        try:
            return runtime.content.check_publish_readiness(content_id)
        except Exception as error:
            _raise_http(error)

    @router.post("/content/{content_id}/queue")
    def queue_content(content_id: str, request: QueueContentItemRequest):
        try:
            item = runtime.content.queue_content_item(
                content_id=content_id,
                scheduled_at=request.scheduled_at,
                confirmed=request.confirmed,
            )
            return {"item": item}
        except Exception as error:
            _raise_http(error)

    # Metrics and analytics
    @router.post("/metrics/ingest")
    def ingest_metrics(request: IngestMetricsSnapshotRequest):
        try:
            snapshot = ContentMetricsSnapshot(
                profile_id=request.profile_id,
                content_id=request.content_id,
                source_type=request.source_type,
                views=request.views,
                likes=request.likes,
                comments_count=request.comments_count,
                shares=request.shares,
                favorites=request.favorites,
                avg_watch_time=request.avg_watch_time,
                completion_rate=request.completion_rate,
                publish_time=request.publish_time,
                collected_at=request.collected_at or _utc_now(),
            )
            created = runtime.metrics.ingest_metrics_snapshot(snapshot)
            return {"snapshot": created}
        except Exception as error:
            _raise_http(error)

    @router.post("/metrics/import")
    def import_metrics(request: ImportMetricsFromFileRequest):
        try:
            return runtime.metrics.import_metrics_from_file(
                profile_id=request.profile_id,
                path=request.path,
                source_type=request.source_type,
            )
        except Exception as error:
            _raise_http(error)

    @router.get("/analytics/profiles/{profile_id}/performance")
    def profile_performance(profile_id: str, window: str = "30d"):
        try:
            perf = runtime.metrics.get_profile_performance_summary(profile_id, window=window)
            return {"snapshot": perf}
        except Exception as error:
            _raise_http(error)

    @router.get("/analytics/profiles/{profile_id}/top-content")
    def top_content(profile_id: str, window: str = "30d", limit: int = Query(default=5, ge=1, le=50)):
        try:
            items = runtime.top_content.get_top_content(profile_id, window=window, limit=limit)
            return {"items": items}
        except Exception as error:
            _raise_http(error)

    @router.get("/analytics/profiles/{profile_id}/patterns")
    def content_patterns(profile_id: str, window: str = "30d"):
        try:
            patterns = runtime.intelligence.extract_patterns(profile_id, window=window)
            return {"items": patterns}
        except Exception as error:
            _raise_http(error)

    @router.post("/analytics/profiles/{profile_id}/action-plan")
    def generate_action_plan(profile_id: str, request: GenerateActionPlanRequest):
        try:
            plan = runtime.planning.generate_next_content_plan(profile_id, window=request.window)
            return {"plan": plan}
        except Exception as error:
            _raise_http(error)

    @router.get("/analytics/profiles/{profile_id}/recommendations/latest")
    def latest_recommendations(profile_id: str, limit: int = Query(default=10, ge=1, le=50)):
        try:
            items = runtime.planning.get_latest_recommendations(profile_id, limit=limit)
            return {"items": items}
        except Exception as error:
            _raise_http(error)

    # AI mode
    @router.post("/ai/analyze/frame")
    @router.post("/ai/perception/analyze")
    def ai_analyze_frame(request: AnalyzeFrameRequest):
        try:
            frame = runtime.ai_perception.analyze_frame(
                profile_id=request.profile_id,
                source_kind=request.source_kind,
                source_ref=request.source_ref,
            )
            return {"frame": frame}
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/analyze/asset")
    def ai_analyze_asset(request: AnalyzeAssetRequest):
        try:
            return runtime.ai_perception.analyze_asset_preview(
                profile_id=request.profile_id,
                source_ref=request.source_ref,
            )
        except Exception as error:
            _raise_http(error)

    @router.get("/ai/workflow/{profile_id}/summary")
    def ai_workflow_summary(profile_id: str):
        try:
            return runtime.ai_workflow.summarize_current_state(profile_id)
        except Exception as error:
            _raise_http(error)

    @router.get("/ai/workflow/{profile_id}/guidance")
    def ai_workflow_guidance(profile_id: str):
        try:
            return {"guidance": runtime.ai_workflow.build_operator_guidance(profile_id)}
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/evaluate/content")
    def ai_evaluate_content_request(request: EvaluateContentRequest):
        try:
            return runtime.ai_creative.evaluate_content_item(request.content_id)
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/content/{content_id}/evaluate")
    def ai_evaluate_content(content_id: str):
        try:
            return runtime.ai_creative.evaluate_content_item(content_id)
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/recommendations/generate")
    def ai_generate_recommendations(request: GenerateRecommendationsRequest):
        try:
            items = runtime.ai_recommendation.generate_explainable_recommendations(
                profile_id=request.profile_id,
                limit=request.limit,
            )
            return {"items": items}
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/profiles/{profile_id}/video-brief")
    def ai_generate_video_brief(profile_id: str, request: GenerateVideoBriefRequest):
        try:
            if request.profile_id != profile_id:
                raise ValidationError("Request profile_id must match path profile_id.")
            brief = runtime.ai_creative.generate_video_brief(
                profile_id=profile_id,
                source_recommendation_ids=request.source_recommendation_ids,
                creative_goal=request.creative_goal,
                target_format=request.target_format,
                target_duration=request.target_duration,
                visual_style=request.visual_style,
                hook=request.hook,
                cta=request.cta,
            )
            return {"brief": brief}
        except Exception as error:
            _raise_http(error)

    @router.get("/ai/profiles/{profile_id}/recommendations")
    def ai_list_recommendations(profile_id: str, limit: int = Query(default=10, ge=1, le=50)):
        try:
            items = runtime.ai_recommendation.generate_explainable_recommendations(profile_id, limit=limit)
            return {"items": items}
        except Exception as error:
            _raise_http(error)

    @router.get("/profiles/{profile_id}/ai/recommendations")
    def ai_list_profile_recommendations(profile_id: str, limit: int = Query(default=10, ge=1, le=50)):
        try:
            items = runtime.ai_recommendation.generate_explainable_recommendations(profile_id, limit=limit)
            return {"items": items}
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/feedback/ingest")
    @router.post("/ai/feedback")
    def ai_ingest_feedback(request: IngestAIFeedbackRequest):
        try:
            record = runtime.ai_learning.ingest_feedback(
                profile_id=request.profile_id,
                learning_type=request.learning_type,
                input_ref=request.input_ref,
                outcome_summary=request.outcome_summary,
                adjustment_summary=request.adjustment_summary,
                confidence_delta=request.confidence_delta,
            )
            return {"record": record}
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/feedback/recommendation")
    def ai_ingest_recommendation_feedback(request: IngestAIRecommendationFeedbackRequest):
        try:
            feedback = runtime.ai_learning.ingest_user_feedback(
                profile_id=request.profile_id,
                recommendation_id=request.recommendation_id,
                feedback_status=request.feedback_status,
                user_notes=request.user_notes,
                manual_score=request.manual_score,
            )
            return {"feedback": feedback}
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/feedback/outcome")
    def ai_ingest_outcome_feedback(request: IngestAIOutcomeFeedbackRequest):
        try:
            outcome = runtime.ai_learning.ingest_content_performance_feedback(
                profile_id=request.profile_id,
                recommendation_id=request.recommendation_id,
                content_id=request.content_id,
                metrics_snapshot_ids=request.metrics_snapshot_ids,
                outcome_label=request.outcome_label,
                outcome_summary=request.outcome_summary,
            )
            return {"outcome_link": outcome}
        except Exception as error:
            _raise_http(error)

    @router.get("/ai/profiles/{profile_id}/learning-summary")
    def ai_learning_summary(profile_id: str):
        try:
            return runtime.ai_learning.summarize_learnings(profile_id)
        except Exception as error:
            _raise_http(error)

    @router.get("/profiles/{profile_id}/ai/learnings")
    def ai_profile_learnings(profile_id: str):
        try:
            return runtime.ai_learning.summarize_learnings(profile_id)
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/generation/video-brief")
    def generation_video_brief(profile_id: str, request: GenerateVideoBriefRequest):
        try:
            if request.profile_id != profile_id:
                raise ValidationError("Request profile_id must match path profile_id.")
            brief = runtime.generation_prep.generate_video_brief(
                profile_id=profile_id,
                content_goal=request.creative_goal,
                creative_angle=request.visual_style,
                hook=request.hook,
                format_target=request.target_format,
                duration_target=request.target_duration,
            )
            return {"brief": brief}
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/generation/audio-brief")
    def generation_audio_brief(profile_id: str, request: GenerateAudioBriefRequest):
        try:
            brief = runtime.generation_prep.generate_audio_brief(
                profile_id=profile_id,
                content_goal=request.content_goal,
                music_mood=request.music_mood,
                voice_style=request.voice_style,
            )
            return {"brief": brief}
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/generation/script-brief")
    def generation_script_brief(profile_id: str, request: GenerateScriptBriefRequest):
        try:
            brief = runtime.generation_prep.generate_script_brief(
                profile_id=profile_id,
                content_goal=request.content_goal,
                hook=request.hook,
                cta=request.cta,
            )
            return {"brief": brief}
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/generation/text-brief")
    def generation_text_brief(profile_id: str, request: GenerateTextBriefRequest):
        try:
            brief = runtime.generation_prep.generate_text_brief(
                profile_id=profile_id,
                content_goal=request.content_goal,
                cta_options=request.cta_options,
            )
            return {"brief": brief}
        except Exception as error:
            _raise_http(error)

    @router.post("/profiles/{profile_id}/generation/bundles/build")
    def generation_build_bundle(profile_id: str, request: BuildGenerationBundleRequest):
        try:
            bundle = runtime.generation_prep.build_generation_bundle(
                profile_id=profile_id,
                content_goal=request.content_goal,
                creative_angle=request.creative_angle,
                format_target=request.format_target,
                duration_target=request.duration_target,
            )
            return {"bundle": bundle}
        except Exception as error:
            _raise_http(error)

    @router.get("/profiles/{profile_id}/generation/bundles")
    def generation_list_bundles(profile_id: str, limit: int = Query(default=20, ge=1, le=100)):
        try:
            return {"items": runtime.generation_prep.list_generation_bundles(profile_id=profile_id, limit=limit)}
        except Exception as error:
            _raise_http(error)

    @router.post("/ai/video-briefs/{brief_id}/submit")
    def ai_submit_brief(brief_id: str):
        try:
            return runtime.video_generation.submit_generation_brief(brief_id)
        except Exception as error:
            _raise_http(error)

    @router.get("/ai/video-jobs/{external_job_id}/status")
    def ai_job_status(external_job_id: str):
        return runtime.video_generation.check_generation_status(external_job_id)

    @router.get("/ai/video-jobs/{external_job_id}/assets")
    def ai_job_assets(external_job_id: str):
        return {"items": runtime.video_generation.fetch_generated_assets(external_job_id)}

    # Audit and observability
    @router.get("/audit/log")
    def audit_log(profile_id: str | None = None, limit: int = Query(default=100, ge=1, le=500)):
        return {"items": runtime.audit.list_audit(profile_id=profile_id, limit=limit)}

    @router.get("/audit/errors")
    def error_log(profile_id: str | None = None, limit: int = Query(default=100, ge=1, le=500)):
        return {"items": runtime.audit.list_errors(profile_id=profile_id, limit=limit)}

    return router
