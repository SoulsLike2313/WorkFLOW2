from __future__ import annotations

from threading import RLock
from typing import Any

from .models import (
    AILearningRecord,
    AIHypothesis,
    AIOutcomeLink,
    AIPerceptionFrame,
    AIPerceptionResult,
    AIPatternConfidenceHistory,
    AIRecommendationFeedback,
    AIAssetReview,
    ActionPlan,
    AudioGenerationBrief,
    AssistiveScreenState,
    AuditLog,
    CreativeManifest,
    ContentItem,
    ContentMetricsSnapshot,
    ContentPattern,
    ContentRecommendation,
    ContentStatus,
    ErrorLog,
    GenerationAssetBundle,
    Profile,
    ProfileConnection,
    ProfilePerformanceSnapshot,
    PromptPack,
    ScriptGenerationBrief,
    SessionWindow,
    TextGenerationBrief,
    VideoGenerationBrief,
    WorkspaceSummary,
)
from .persistence import SQLiteWorkspacePersistence


class WorkspaceRepository:
    """
    Thread-safe in-memory state store for the workspace domain.

    First iteration keeps storage simple and deterministic.
    This can be replaced by sqlite/postgres adapters later without
    changing service interfaces.
    """

    def __init__(self, persistence: SQLiteWorkspacePersistence | None = None) -> None:
        self._lock = RLock()
        self._persistence = persistence

        self._profiles: dict[str, Profile] = {}
        self._connections: dict[str, ProfileConnection] = {}
        self._sessions: dict[str, SessionWindow] = {}

        self._content_items: dict[str, ContentItem] = {}
        self._metrics: dict[str, ContentMetricsSnapshot] = {}
        self._profile_performance: dict[str, list[ProfilePerformanceSnapshot]] = {}
        self._content_patterns: dict[str, list[ContentPattern]] = {}
        self._recommendations: dict[str, list[ContentRecommendation]] = {}
        self._action_plans: dict[str, list[ActionPlan]] = {}

        self._screen_states: dict[str, list[AssistiveScreenState]] = {}
        self._perception_frames: dict[str, list[AIPerceptionFrame]] = {}
        self._perception_results: dict[str, list[AIPerceptionResult]] = {}
        self._asset_reviews: dict[str, list[AIAssetReview]] = {}
        self._learning_records: dict[str, list[AILearningRecord]] = {}
        self._hypotheses: dict[str, list[AIHypothesis]] = {}
        self._outcome_links: dict[str, list[AIOutcomeLink]] = {}
        self._recommendation_feedback: dict[str, list[AIRecommendationFeedback]] = {}
        self._pattern_confidence_history: dict[str, list[AIPatternConfidenceHistory]] = {}
        self._video_briefs: dict[str, list[VideoGenerationBrief]] = {}
        self._audio_briefs: dict[str, list[AudioGenerationBrief]] = {}
        self._script_briefs: dict[str, list[ScriptGenerationBrief]] = {}
        self._text_briefs: dict[str, list[TextGenerationBrief]] = {}
        self._prompt_packs: dict[str, list[PromptPack]] = {}
        self._creative_manifests: dict[str, list[CreativeManifest]] = {}
        self._generation_bundles: dict[str, list[GenerationAssetBundle]] = {}

        self._audit_logs: list[AuditLog] = []
        self._error_logs: list[ErrorLog] = []

        if self._persistence is not None:
            self._load_snapshot_from_persistence()

    # Profiles
    def save_profile(self, profile: Profile) -> Profile:
        with self._lock:
            self._profiles[profile.id] = profile
            self._persist_snapshot()
            return profile

    def get_profile(self, profile_id: str) -> Profile | None:
        with self._lock:
            return self._profiles.get(profile_id)

    def list_profiles(self) -> list[Profile]:
        with self._lock:
            return list(self._profiles.values())

    def count_profiles(self) -> int:
        with self._lock:
            return len(self._profiles)

    # Profile connections
    def save_connection(self, connection: ProfileConnection) -> ProfileConnection:
        with self._lock:
            self._connections[connection.profile_id] = connection
            self._persist_snapshot()
            return connection

    def get_connection(self, profile_id: str) -> ProfileConnection | None:
        with self._lock:
            return self._connections.get(profile_id)

    # Session windows
    def save_session(self, session: SessionWindow) -> SessionWindow:
        with self._lock:
            self._sessions[session.profile_id] = session
            self._persist_snapshot()
            return session

    def get_session(self, profile_id: str) -> SessionWindow | None:
        with self._lock:
            return self._sessions.get(profile_id)

    def list_sessions(self) -> list[SessionWindow]:
        with self._lock:
            return list(self._sessions.values())

    # Content
    def save_content_item(self, item: ContentItem) -> ContentItem:
        with self._lock:
            self._content_items[item.id] = item
            self._persist_snapshot()
            return item

    def get_content_item(self, content_id: str) -> ContentItem | None:
        with self._lock:
            return self._content_items.get(content_id)

    def list_content_items(
        self,
        *,
        profile_id: str | None = None,
        status: ContentStatus | None = None,
    ) -> list[ContentItem]:
        with self._lock:
            items = list(self._content_items.values())
        if profile_id is not None:
            items = [item for item in items if item.profile_id == profile_id]
        if status is not None:
            items = [item for item in items if item.status == status]
        return items

    # Metrics and analytics artefacts
    def save_metrics_snapshot(self, snapshot: ContentMetricsSnapshot) -> ContentMetricsSnapshot:
        with self._lock:
            self._metrics[snapshot.id] = snapshot
            self._persist_snapshot()
            return snapshot

    def list_metrics_snapshots(
        self,
        *,
        profile_id: str | None = None,
        content_id: str | None = None,
        limit: int | None = None,
    ) -> list[ContentMetricsSnapshot]:
        with self._lock:
            snapshots = list(self._metrics.values())
        if profile_id is not None:
            snapshots = [item for item in snapshots if item.profile_id == profile_id]
        if content_id is not None:
            snapshots = [item for item in snapshots if item.content_id == content_id]
        snapshots.sort(key=lambda item: item.collected_at, reverse=True)
        if limit is not None:
            snapshots = snapshots[:limit]
        return snapshots

    def save_profile_performance(self, snapshot: ProfilePerformanceSnapshot) -> ProfilePerformanceSnapshot:
        with self._lock:
            bucket = self._profile_performance.setdefault(snapshot.profile_id, [])
            bucket.append(snapshot)
            self._persist_snapshot()
            return snapshot

    def list_profile_performance(
        self,
        profile_id: str,
        *,
        limit: int | None = None,
    ) -> list[ProfilePerformanceSnapshot]:
        with self._lock:
            items = list(self._profile_performance.get(profile_id, []))
        items.sort(key=lambda item: item.collected_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_content_pattern(self, pattern: ContentPattern) -> ContentPattern:
        with self._lock:
            bucket = self._content_patterns.setdefault(pattern.profile_id, [])
            bucket.append(pattern)
            self._persist_snapshot()
            return pattern

    def replace_content_patterns(self, profile_id: str, patterns: list[ContentPattern]) -> list[ContentPattern]:
        with self._lock:
            self._content_patterns[profile_id] = list(patterns)
            self._persist_snapshot()
            return patterns

    def list_content_patterns(self, profile_id: str, *, limit: int | None = None) -> list[ContentPattern]:
        with self._lock:
            items = list(self._content_patterns.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_recommendation(self, recommendation: ContentRecommendation) -> ContentRecommendation:
        with self._lock:
            bucket = self._recommendations.setdefault(recommendation.profile_id, [])
            bucket.append(recommendation)
            self._persist_snapshot()
            return recommendation

    def replace_recommendations(
        self,
        profile_id: str,
        recommendations: list[ContentRecommendation],
    ) -> list[ContentRecommendation]:
        with self._lock:
            self._recommendations[profile_id] = list(recommendations)
            self._persist_snapshot()
            return recommendations

    def list_recommendations(self, profile_id: str, *, limit: int | None = None) -> list[ContentRecommendation]:
        with self._lock:
            items = list(self._recommendations.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_action_plan(self, plan: ActionPlan) -> ActionPlan:
        with self._lock:
            bucket = self._action_plans.setdefault(plan.profile_id, [])
            bucket.append(plan)
            self._persist_snapshot()
            return plan

    def get_latest_action_plan(self, profile_id: str) -> ActionPlan | None:
        plans = self.list_action_plans(profile_id, limit=1)
        return plans[0] if plans else None

    def list_action_plans(self, profile_id: str, *, limit: int | None = None) -> list[ActionPlan]:
        with self._lock:
            items = list(self._action_plans.get(profile_id, []))
        items.sort(key=lambda item: item.generated_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    # AI data
    def save_screen_state(self, item: AssistiveScreenState) -> AssistiveScreenState:
        with self._lock:
            bucket = self._screen_states.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_screen_states(self, profile_id: str, *, limit: int | None = None) -> list[AssistiveScreenState]:
        with self._lock:
            items = list(self._screen_states.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_perception_frame(self, item: AIPerceptionFrame) -> AIPerceptionFrame:
        with self._lock:
            bucket = self._perception_frames.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_perception_frames(self, profile_id: str, *, limit: int | None = None) -> list[AIPerceptionFrame]:
        with self._lock:
            items = list(self._perception_frames.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_perception_result(self, item: AIPerceptionResult) -> AIPerceptionResult:
        with self._lock:
            bucket = self._perception_results.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_perception_results(self, profile_id: str, *, limit: int | None = None) -> list[AIPerceptionResult]:
        with self._lock:
            items = list(self._perception_results.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_asset_review(self, item: AIAssetReview) -> AIAssetReview:
        with self._lock:
            bucket = self._asset_reviews.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_asset_reviews(self, profile_id: str, *, limit: int | None = None) -> list[AIAssetReview]:
        with self._lock:
            items = list(self._asset_reviews.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_learning_record(self, item: AILearningRecord) -> AILearningRecord:
        with self._lock:
            bucket = self._learning_records.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_learning_records(self, profile_id: str, *, limit: int | None = None) -> list[AILearningRecord]:
        with self._lock:
            items = list(self._learning_records.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_hypothesis(self, item: AIHypothesis) -> AIHypothesis:
        with self._lock:
            bucket = self._hypotheses.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_hypotheses(self, profile_id: str, *, limit: int | None = None) -> list[AIHypothesis]:
        with self._lock:
            items = list(self._hypotheses.get(profile_id, []))
        items.sort(key=lambda item: item.updated_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def replace_hypotheses(self, profile_id: str, items: list[AIHypothesis]) -> list[AIHypothesis]:
        with self._lock:
            self._hypotheses[profile_id] = list(items)
            self._persist_snapshot()
            return items

    def save_outcome_link(self, item: AIOutcomeLink) -> AIOutcomeLink:
        with self._lock:
            bucket = self._outcome_links.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_outcome_links(self, profile_id: str, *, limit: int | None = None) -> list[AIOutcomeLink]:
        with self._lock:
            items = list(self._outcome_links.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_recommendation_feedback(self, item: AIRecommendationFeedback) -> AIRecommendationFeedback:
        with self._lock:
            bucket = self._recommendation_feedback.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_recommendation_feedback(
        self,
        profile_id: str,
        *,
        limit: int | None = None,
    ) -> list[AIRecommendationFeedback]:
        with self._lock:
            items = list(self._recommendation_feedback.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_pattern_confidence_history(self, item: AIPatternConfidenceHistory) -> AIPatternConfidenceHistory:
        with self._lock:
            bucket = self._pattern_confidence_history.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_pattern_confidence_history(
        self,
        profile_id: str,
        *,
        limit: int | None = None,
    ) -> list[AIPatternConfidenceHistory]:
        with self._lock:
            items = list(self._pattern_confidence_history.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_video_brief(self, item: VideoGenerationBrief) -> VideoGenerationBrief:
        with self._lock:
            bucket = self._video_briefs.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_video_briefs(self, profile_id: str, *, limit: int | None = None) -> list[VideoGenerationBrief]:
        with self._lock:
            items = list(self._video_briefs.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def get_video_brief(self, brief_id: str) -> VideoGenerationBrief | None:
        with self._lock:
            for items in self._video_briefs.values():
                for item in items:
                    if item.id == brief_id:
                        return item
        return None

    def save_audio_brief(self, item: AudioGenerationBrief) -> AudioGenerationBrief:
        with self._lock:
            bucket = self._audio_briefs.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_audio_briefs(self, profile_id: str, *, limit: int | None = None) -> list[AudioGenerationBrief]:
        with self._lock:
            items = list(self._audio_briefs.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_script_brief(self, item: ScriptGenerationBrief) -> ScriptGenerationBrief:
        with self._lock:
            bucket = self._script_briefs.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_script_briefs(self, profile_id: str, *, limit: int | None = None) -> list[ScriptGenerationBrief]:
        with self._lock:
            items = list(self._script_briefs.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_text_brief(self, item: TextGenerationBrief) -> TextGenerationBrief:
        with self._lock:
            bucket = self._text_briefs.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_text_briefs(self, profile_id: str, *, limit: int | None = None) -> list[TextGenerationBrief]:
        with self._lock:
            items = list(self._text_briefs.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_prompt_pack(self, item: PromptPack) -> PromptPack:
        with self._lock:
            bucket = self._prompt_packs.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_prompt_packs(self, profile_id: str, *, limit: int | None = None) -> list[PromptPack]:
        with self._lock:
            items = list(self._prompt_packs.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_creative_manifest(self, item: CreativeManifest) -> CreativeManifest:
        with self._lock:
            bucket = self._creative_manifests.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_creative_manifests(self, profile_id: str, *, limit: int | None = None) -> list[CreativeManifest]:
        with self._lock:
            items = list(self._creative_manifests.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_generation_bundle(self, item: GenerationAssetBundle) -> GenerationAssetBundle:
        with self._lock:
            bucket = self._generation_bundles.setdefault(item.profile_id, [])
            bucket.append(item)
            self._persist_snapshot()
            return item

    def list_generation_bundles(self, profile_id: str, *, limit: int | None = None) -> list[GenerationAssetBundle]:
        with self._lock:
            items = list(self._generation_bundles.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    # Logs
    def append_audit(self, event: AuditLog) -> AuditLog:
        with self._lock:
            self._audit_logs.append(event)
            self._persist_snapshot()
            return event

    def list_audit_logs(self, *, profile_id: str | None = None, limit: int = 100) -> list[AuditLog]:
        with self._lock:
            logs = list(self._audit_logs)
        if profile_id is not None:
            logs = [item for item in logs if item.profile_id == profile_id]
        logs.sort(key=lambda item: item.created_at, reverse=True)
        return logs[:limit]

    def append_error(self, event: ErrorLog) -> ErrorLog:
        with self._lock:
            self._error_logs.append(event)
            self._persist_snapshot()
            return event

    def list_error_logs(self, *, profile_id: str | None = None, limit: int = 100) -> list[ErrorLog]:
        with self._lock:
            logs = list(self._error_logs)
        if profile_id is not None:
            logs = [item for item in logs if item.profile_id == profile_id]
        logs.sort(key=lambda item: item.created_at, reverse=True)
        return logs[:limit]

    # Persistence snapshot
    def _persist_snapshot(self) -> None:
        if self._persistence is None:
            return
        state = self._serialize_state()
        self._persistence.save_state(state)

    def _serialize_state(self) -> dict[str, Any]:
        return {
            "profiles": {key: value.model_dump(mode="json") for key, value in self._profiles.items()},
            "connections": {key: value.model_dump(mode="json") for key, value in self._connections.items()},
            "sessions": {key: value.model_dump(mode="json") for key, value in self._sessions.items()},
            "content_items": {key: value.model_dump(mode="json") for key, value in self._content_items.items()},
            "metrics": {key: value.model_dump(mode="json") for key, value in self._metrics.items()},
            "profile_performance": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._profile_performance.items()
            },
            "content_patterns": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._content_patterns.items()
            },
            "recommendations": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._recommendations.items()
            },
            "action_plans": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._action_plans.items()
            },
            "screen_states": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._screen_states.items()
            },
            "perception_frames": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._perception_frames.items()
            },
            "perception_results": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._perception_results.items()
            },
            "asset_reviews": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._asset_reviews.items()
            },
            "learning_records": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._learning_records.items()
            },
            "hypotheses": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._hypotheses.items()
            },
            "outcome_links": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._outcome_links.items()
            },
            "recommendation_feedback": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._recommendation_feedback.items()
            },
            "pattern_confidence_history": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._pattern_confidence_history.items()
            },
            "video_briefs": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._video_briefs.items()
            },
            "audio_briefs": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._audio_briefs.items()
            },
            "script_briefs": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._script_briefs.items()
            },
            "text_briefs": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._text_briefs.items()
            },
            "prompt_packs": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._prompt_packs.items()
            },
            "creative_manifests": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._creative_manifests.items()
            },
            "generation_bundles": {
                key: [item.model_dump(mode="json") for item in values]
                for key, values in self._generation_bundles.items()
            },
            "audit_logs": [item.model_dump(mode="json") for item in self._audit_logs],
            "error_logs": [item.model_dump(mode="json") for item in self._error_logs],
        }

    def _load_snapshot_from_persistence(self) -> None:
        if self._persistence is None:
            return
        state = self._persistence.load_state()
        if not state:
            return

        self._profiles = self._load_model_dict(state.get("profiles"), Profile)
        self._connections = self._load_model_dict(state.get("connections"), ProfileConnection)
        self._sessions = self._load_model_dict(state.get("sessions"), SessionWindow)
        self._content_items = self._load_model_dict(state.get("content_items"), ContentItem)
        self._metrics = self._load_model_dict(state.get("metrics"), ContentMetricsSnapshot)
        self._profile_performance = self._load_model_bucket_list(
            state.get("profile_performance"), ProfilePerformanceSnapshot
        )
        self._content_patterns = self._load_model_bucket_list(state.get("content_patterns"), ContentPattern)
        self._recommendations = self._load_model_bucket_list(state.get("recommendations"), ContentRecommendation)
        self._action_plans = self._load_model_bucket_list(state.get("action_plans"), ActionPlan)
        self._screen_states = self._load_model_bucket_list(state.get("screen_states"), AssistiveScreenState)
        self._perception_frames = self._load_model_bucket_list(state.get("perception_frames"), AIPerceptionFrame)
        self._perception_results = self._load_model_bucket_list(state.get("perception_results"), AIPerceptionResult)
        self._asset_reviews = self._load_model_bucket_list(state.get("asset_reviews"), AIAssetReview)
        self._learning_records = self._load_model_bucket_list(state.get("learning_records"), AILearningRecord)
        self._hypotheses = self._load_model_bucket_list(state.get("hypotheses"), AIHypothesis)
        self._outcome_links = self._load_model_bucket_list(state.get("outcome_links"), AIOutcomeLink)
        self._recommendation_feedback = self._load_model_bucket_list(
            state.get("recommendation_feedback"), AIRecommendationFeedback
        )
        self._pattern_confidence_history = self._load_model_bucket_list(
            state.get("pattern_confidence_history"), AIPatternConfidenceHistory
        )
        self._video_briefs = self._load_model_bucket_list(state.get("video_briefs"), VideoGenerationBrief)
        self._audio_briefs = self._load_model_bucket_list(state.get("audio_briefs"), AudioGenerationBrief)
        self._script_briefs = self._load_model_bucket_list(state.get("script_briefs"), ScriptGenerationBrief)
        self._text_briefs = self._load_model_bucket_list(state.get("text_briefs"), TextGenerationBrief)
        self._prompt_packs = self._load_model_bucket_list(state.get("prompt_packs"), PromptPack)
        self._creative_manifests = self._load_model_bucket_list(state.get("creative_manifests"), CreativeManifest)
        self._generation_bundles = self._load_model_bucket_list(state.get("generation_bundles"), GenerationAssetBundle)
        self._audit_logs = self._load_model_list(state.get("audit_logs"), AuditLog)
        self._error_logs = self._load_model_list(state.get("error_logs"), ErrorLog)

    @staticmethod
    def _load_model_dict(raw: Any, model_cls: Any) -> dict[str, Any]:
        if not isinstance(raw, dict):
            return {}
        loaded: dict[str, Any] = {}
        for key, value in raw.items():
            try:
                loaded[str(key)] = model_cls.model_validate(value)
            except Exception:
                continue
        return loaded

    @staticmethod
    def _load_model_list(raw: Any, model_cls: Any) -> list[Any]:
        if not isinstance(raw, list):
            return []
        loaded: list[Any] = []
        for value in raw:
            try:
                loaded.append(model_cls.model_validate(value))
            except Exception:
                continue
        return loaded

    @classmethod
    def _load_model_bucket_list(cls, raw: Any, model_cls: Any) -> dict[str, list[Any]]:
        if not isinstance(raw, dict):
            return {}
        loaded: dict[str, list[Any]] = {}
        for key, values in raw.items():
            loaded[str(key)] = cls._load_model_list(values, model_cls)
        return loaded

    # Summary
    def build_summary(self, *, audit_limit: int = 20) -> WorkspaceSummary:
        profiles = self.list_profiles()
        sessions = self.list_sessions()
        queued = self.list_content_items(status=ContentStatus.QUEUED)
        active = [item for item in profiles if item.status.value == "active"]
        open_windows = [item for item in sessions if item.is_open]
        return WorkspaceSummary(
            profile_count=len(profiles),
            active_profiles=len(active),
            queued_content_items=len(queued),
            open_session_windows=len(open_windows),
            latest_audit_events=self.list_audit_logs(limit=audit_limit),
        )
