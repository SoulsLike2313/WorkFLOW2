from __future__ import annotations

from threading import RLock

from .models import (
    AILearningRecord,
    AIPerceptionFrame,
    ActionPlan,
    AssistiveScreenState,
    AuditLog,
    ContentItem,
    ContentMetricsSnapshot,
    ContentPattern,
    ContentRecommendation,
    ContentStatus,
    ErrorLog,
    Profile,
    ProfileConnection,
    ProfilePerformanceSnapshot,
    SessionWindow,
    VideoGenerationBrief,
    WorkspaceSummary,
)


class WorkspaceRepository:
    """
    Thread-safe in-memory state store for the workspace domain.

    First iteration keeps storage simple and deterministic.
    This can be replaced by sqlite/postgres adapters later without
    changing service interfaces.
    """

    def __init__(self) -> None:
        self._lock = RLock()

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
        self._learning_records: dict[str, list[AILearningRecord]] = {}
        self._video_briefs: dict[str, list[VideoGenerationBrief]] = {}

        self._audit_logs: list[AuditLog] = []
        self._error_logs: list[ErrorLog] = []

    # Profiles
    def save_profile(self, profile: Profile) -> Profile:
        with self._lock:
            self._profiles[profile.id] = profile
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
            return connection

    def get_connection(self, profile_id: str) -> ProfileConnection | None:
        with self._lock:
            return self._connections.get(profile_id)

    # Session windows
    def save_session(self, session: SessionWindow) -> SessionWindow:
        with self._lock:
            self._sessions[session.profile_id] = session
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
            return pattern

    def replace_content_patterns(self, profile_id: str, patterns: list[ContentPattern]) -> list[ContentPattern]:
        with self._lock:
            self._content_patterns[profile_id] = list(patterns)
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
            return recommendation

    def replace_recommendations(
        self,
        profile_id: str,
        recommendations: list[ContentRecommendation],
    ) -> list[ContentRecommendation]:
        with self._lock:
            self._recommendations[profile_id] = list(recommendations)
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
            return item

    def list_perception_frames(self, profile_id: str, *, limit: int | None = None) -> list[AIPerceptionFrame]:
        with self._lock:
            items = list(self._perception_frames.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_learning_record(self, item: AILearningRecord) -> AILearningRecord:
        with self._lock:
            bucket = self._learning_records.setdefault(item.profile_id, [])
            bucket.append(item)
            return item

    def list_learning_records(self, profile_id: str, *, limit: int | None = None) -> list[AILearningRecord]:
        with self._lock:
            items = list(self._learning_records.get(profile_id, []))
        items.sort(key=lambda item: item.created_at, reverse=True)
        if limit is not None:
            items = items[:limit]
        return items

    def save_video_brief(self, item: VideoGenerationBrief) -> VideoGenerationBrief:
        with self._lock:
            bucket = self._video_briefs.setdefault(item.profile_id, [])
            bucket.append(item)
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

    # Logs
    def append_audit(self, event: AuditLog) -> AuditLog:
        with self._lock:
            self._audit_logs.append(event)
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
            return event

    def list_error_logs(self, *, profile_id: str | None = None, limit: int = 100) -> list[ErrorLog]:
        with self._lock:
            logs = list(self._error_logs)
        if profile_id is not None:
            logs = [item for item in logs if item.profile_id == profile_id]
        logs.sort(key=lambda item: item.created_at, reverse=True)
        return logs[:limit]

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
