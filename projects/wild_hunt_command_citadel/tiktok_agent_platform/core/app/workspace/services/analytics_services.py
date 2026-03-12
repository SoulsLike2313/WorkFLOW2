from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import mean, pstdev

from ..diagnostics import diag_log
from ..errors import NotFoundError
from ..models import (
    ActionPlan,
    ConfidenceLevel,
    ContentMetricsSnapshot,
    ContentPattern,
    ContentRecommendation,
    PatternType,
    PriorityLevel,
    RecommendationType,
)
from ..repository import WorkspaceRepository


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_window_days(window: str) -> int:
    normalized = window.strip().lower()
    if normalized.endswith("d") and normalized[:-1].isdigit():
        return max(1, int(normalized[:-1]))
    return 30


class AnalyticsFormulaService:
    def __init__(self, *, weights: dict[str, float]) -> None:
        self.weights = weights

    @staticmethod
    def engagement_rate(*, views: int, likes: int, comments_count: int, shares: int, favorites: int) -> float:
        if views <= 0:
            return 0.0
        return (likes + comments_count + shares + favorites) / views

    @staticmethod
    def like_to_view_ratio(*, views: int, likes: int) -> float:
        return likes / views if views > 0 else 0.0

    @staticmethod
    def comment_to_view_ratio(*, views: int, comments_count: int) -> float:
        return comments_count / views if views > 0 else 0.0

    @staticmethod
    def share_to_view_ratio(*, views: int, shares: int) -> float:
        return shares / views if views > 0 else 0.0

    def weighted_engagement_score(self, snapshot: ContentMetricsSnapshot) -> float:
        w = self.weights
        base = (
            (snapshot.views * w["views_weight"])
            + (snapshot.likes * w["likes_weight"])
            + (snapshot.comments_count * w["comments_weight"])
            + (snapshot.shares * w["shares_weight"])
            + (snapshot.favorites * w["favorites_weight"])
        )
        if snapshot.avg_watch_time is not None:
            base += snapshot.avg_watch_time * w["watch_time_weight"]
        if snapshot.completion_rate is not None:
            base += snapshot.completion_rate * w["completion_weight"] * 100
        return max(base, 0.0)

    @staticmethod
    def velocity_score(snapshot: ContentMetricsSnapshot) -> float:
        publish_time = snapshot.publish_time or snapshot.collected_at
        elapsed_hours = max((snapshot.collected_at - publish_time).total_seconds() / 3600.0, 1.0)
        return snapshot.views / elapsed_hours

    @staticmethod
    def consistency_score(values: list[float]) -> float:
        if not values:
            return 0.0
        if len(values) == 1:
            return 1.0
        mu = mean(values)
        if mu <= 0:
            return 0.0
        sigma = pstdev(values)
        coefficient = sigma / mu
        return max(0.0, 1.0 - min(coefficient, 1.0))

    def enrich_snapshot(self, snapshot: ContentMetricsSnapshot) -> ContentMetricsSnapshot:
        engagement = self.engagement_rate(
            views=snapshot.views,
            likes=snapshot.likes,
            comments_count=snapshot.comments_count,
            shares=snapshot.shares,
            favorites=snapshot.favorites,
        )
        weighted = self.weighted_engagement_score(snapshot)
        return snapshot.model_copy(update={"engagement_rate": engagement, "weighted_engagement_score": weighted})

    def profile_momentum_score(self, snapshots: list[ContentMetricsSnapshot]) -> float:
        if not snapshots:
            return 0.0
        ordered = sorted(snapshots, key=lambda item: item.collected_at)
        midpoint = len(ordered) // 2
        baseline = ordered[:midpoint] if midpoint > 0 else ordered
        recent = ordered[midpoint:] if midpoint > 0 else ordered
        baseline_avg = mean([item.weighted_engagement_score for item in baseline]) if baseline else 0.0
        recent_avg = mean([item.weighted_engagement_score for item in recent]) if recent else 0.0
        if baseline_avg <= 0:
            return recent_avg
        return (recent_avg - baseline_avg) / baseline_avg


class TopContentService:
    def __init__(self, *, repository: WorkspaceRepository, formulas: AnalyticsFormulaService) -> None:
        self.repository = repository
        self.formulas = formulas

    def get_top_content(self, profile_id: str, window: str = "30d", limit: int = 5) -> list[ContentMetricsSnapshot]:
        days = _parse_window_days(window)
        cutoff = _utc_now() - timedelta(days=days)
        snapshots = [
            item
            for item in self.repository.list_metrics_snapshots(profile_id=profile_id)
            if item.collected_at >= cutoff
        ]
        ranked = self.rank_by_weighted_score(snapshots=snapshots, limit=limit)
        return ranked

    def rank_by_weighted_score(
        self,
        *,
        snapshots: list[ContentMetricsSnapshot],
        limit: int = 5,
    ) -> list[ContentMetricsSnapshot]:
        normalized = [self.formulas.enrich_snapshot(item) for item in snapshots]
        normalized.sort(key=lambda item: item.weighted_engagement_score, reverse=True)
        return normalized[:limit]

    def detect_outliers(self, profile_id: str, window: str = "30d") -> dict[str, list[str]]:
        snapshots = self.get_top_content(profile_id, window=window, limit=200)
        scores = [item.weighted_engagement_score for item in snapshots]
        if len(scores) < 4:
            return {"strong_spikes": [], "weak_outliers": []}
        mu = mean(scores)
        sigma = pstdev(scores)
        if sigma <= 0:
            return {"strong_spikes": [], "weak_outliers": []}
        strong = [item.content_id for item in snapshots if item.weighted_engagement_score > mu + (1.5 * sigma)]
        weak = [item.content_id for item in snapshots if item.weighted_engagement_score < mu - (1.5 * sigma)]
        return {"strong_spikes": strong, "weak_outliers": weak}

    def compare_recent_vs_baseline(
        self,
        profile_id: str,
        *,
        recent_days: int = 7,
        baseline_days: int = 30,
    ) -> dict[str, float]:
        now = _utc_now()
        all_snapshots = self.repository.list_metrics_snapshots(profile_id=profile_id)
        recent_cutoff = now - timedelta(days=recent_days)
        baseline_cutoff = now - timedelta(days=baseline_days)

        recent = [item for item in all_snapshots if item.collected_at >= recent_cutoff]
        baseline = [item for item in all_snapshots if baseline_cutoff <= item.collected_at < recent_cutoff]

        recent_score = mean([self.formulas.enrich_snapshot(item).weighted_engagement_score for item in recent]) if recent else 0.0
        baseline_score = (
            mean([self.formulas.enrich_snapshot(item).weighted_engagement_score for item in baseline]) if baseline else 0.0
        )
        delta = recent_score - baseline_score
        delta_ratio = (delta / baseline_score) if baseline_score > 0 else 0.0
        return {
            "recent_score": recent_score,
            "baseline_score": baseline_score,
            "delta": delta,
            "delta_ratio": delta_ratio,
        }


class ContentIntelligenceService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        top_content_service: TopContentService,
    ) -> None:
        self.repository = repository
        self.top_content_service = top_content_service

    def extract_patterns(self, profile_id: str, window: str = "30d") -> list[ContentPattern]:
        items = {item.id: item for item in self.repository.list_content_items(profile_id=profile_id)}
        top = self.top_content_service.get_top_content(profile_id=profile_id, window=window, limit=50)
        if not items or not top:
            self.repository.replace_content_patterns(profile_id, [])
            return []

        grouped: dict[PatternType, dict[str, int]] = {
            PatternType.FORMAT: defaultdict(int),
            PatternType.TOPIC: defaultdict(int),
            PatternType.HOOK: defaultdict(int),
            PatternType.CTA: defaultdict(int),
            PatternType.DURATION: defaultdict(int),
            PatternType.POSTING_WINDOW: defaultdict(int),
        }
        for snapshot in top:
            item = items.get(snapshot.content_id)
            if item is None:
                continue
            grouped[PatternType.FORMAT][item.format_label or "unknown"] += 1
            grouped[PatternType.TOPIC][item.topic_label or "unknown"] += 1
            grouped[PatternType.HOOK][item.hook_label or "unknown"] += 1
            grouped[PatternType.CTA][item.cta_label or "unknown"] += 1
            grouped[PatternType.DURATION][self._duration_bucket(item.duration)] += 1
            grouped[PatternType.POSTING_WINDOW][self._posting_bucket(item.scheduled_at)] += 1

        patterns: list[ContentPattern] = []
        total = max(len(top), 1)
        for pattern_type, bucket in grouped.items():
            for label, count in sorted(bucket.items(), key=lambda x: x[1], reverse=True)[:3]:
                confidence = min(count / total, 1.0)
                patterns.append(
                    ContentPattern(
                        profile_id=profile_id,
                        pattern_type=pattern_type,
                        label=label,
                        evidence=[f"observed in {count} top snapshots"],
                        confidence=confidence,
                    )
                )
        self.repository.replace_content_patterns(profile_id, patterns)
        diag_log(
            "runtime_logs",
            "content_patterns_extracted",
            payload={"profile_id": profile_id, "pattern_count": len(patterns), "window": window},
        )
        return patterns

    def detect_successful_angles(self, profile_id: str, window: str = "30d") -> list[str]:
        patterns = self.extract_patterns(profile_id, window=window)
        top_patterns = sorted(patterns, key=lambda item: item.confidence, reverse=True)[:5]
        return [f"{item.pattern_type.value}: {item.label}" for item in top_patterns]

    def detect_weak_angles(self, profile_id: str, window: str = "30d") -> list[str]:
        items = {item.id: item for item in self.repository.list_content_items(profile_id=profile_id)}
        snapshots = self.repository.list_metrics_snapshots(profile_id=profile_id)
        if not snapshots:
            return []
        sorted_scores = sorted(snapshots, key=lambda x: x.weighted_engagement_score)
        weak = sorted_scores[: min(5, len(sorted_scores))]
        reasons: list[str] = []
        for entry in weak:
            item = items.get(entry.content_id)
            if item is None:
                continue
            reasons.append(
                f"{item.id}: topic={item.topic_label or 'unknown'}, format={item.format_label or 'unknown'} "
                f"(score={entry.weighted_engagement_score:.2f})"
            )
        return reasons

    def build_profile_content_summary(self, profile_id: str, window: str = "30d") -> dict[str, object]:
        patterns = self.extract_patterns(profile_id, window=window)
        successful = self.detect_successful_angles(profile_id, window=window)
        weak = self.detect_weak_angles(profile_id, window=window)
        return {
            "profile_id": profile_id,
            "window": window,
            "pattern_count": len(patterns),
            "successful_angles": successful,
            "weak_angles": weak,
        }

    @staticmethod
    def _duration_bucket(duration: float | None) -> str:
        if duration is None:
            return "unknown"
        if duration < 15:
            return "short_0_15"
        if duration < 30:
            return "mid_15_30"
        if duration < 60:
            return "long_30_60"
        return "extended_60_plus"

    @staticmethod
    def _posting_bucket(scheduled_at: datetime | None) -> str:
        if scheduled_at is None:
            return "unscheduled"
        hour = scheduled_at.hour
        if 6 <= hour < 12:
            return "morning"
        if 12 <= hour < 18:
            return "daytime"
        if 18 <= hour < 24:
            return "evening"
        return "night"


class ContentPlanningService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        formulas: AnalyticsFormulaService,
        top_content_service: TopContentService,
        intelligence_service: ContentIntelligenceService,
    ) -> None:
        self.repository = repository
        self.formulas = formulas
        self.top_content_service = top_content_service
        self.intelligence_service = intelligence_service

    def generate_next_content_plan(self, profile_id: str, window: str = "30d") -> ActionPlan:
        if self.repository.get_profile(profile_id) is None:
            raise NotFoundError("profile", profile_id)
        top_snapshots = self.top_content_service.get_top_content(profile_id, window=window, limit=5)
        weak_angles = self.intelligence_service.detect_weak_angles(profile_id, window=window)
        successful_angles = self.intelligence_service.detect_successful_angles(profile_id, window=window)
        comparison = self.top_content_service.compare_recent_vs_baseline(profile_id)

        next_actions = self.build_experiment_queue(profile_id)
        recommended_angles = self.suggest_content_angles(profile_id)
        posting_windows = self.suggest_posting_windows(profile_id)
        confidence = self._confidence_from_data(top_snapshots)

        plan = ActionPlan(
            profile_id=profile_id,
            performance_summary=self.summarize_content_direction(profile_id),
            top_content_findings=[
                f"{entry.content_id}: weighted={entry.weighted_engagement_score:.2f}, "
                f"engagement={entry.engagement_rate:.3f}"
                for entry in top_snapshots
            ],
            weak_content_findings=weak_angles or ["No weak content signals yet"],
            recommended_content_angles=recommended_angles,
            next_actions=next_actions
            + [f"Preferred posting windows: {', '.join(posting_windows)}"]
            + [f"Recent vs baseline delta ratio: {comparison['delta_ratio']:.2f}"],
            confidence_level=confidence,
            required_manual_checks=[
                "Confirm compliance and rights for media assets.",
                "Review captions and hashtags before posting.",
                "Verify final content quality in preview.",
            ],
            source_context={
                "window": window,
                "top_snapshot_count": len(top_snapshots),
                "successful_angles": successful_angles,
            },
        )
        self.repository.save_action_plan(plan)
        self.repository.replace_recommendations(profile_id, self._build_recommendations(profile_id, successful_angles, weak_angles))
        diag_log(
            "runtime_logs",
            "content_action_plan_generated",
            payload={
                "profile_id": profile_id,
                "window": window,
                "next_actions_count": len(plan.next_actions),
                "recommendation_count": len(self.repository.list_recommendations(profile_id)),
            },
        )
        return plan

    def build_experiment_queue(self, profile_id: str, count: int = 3) -> list[str]:
        angles = self.suggest_content_angles(profile_id)
        queue = []
        for index in range(min(count, len(angles))):
            queue.append(f"Experiment {index + 1}: produce one variant for '{angles[index]}'")
        if not queue:
            queue = [
                "Experiment 1: test a strong hook in first 2 seconds",
                "Experiment 2: test shorter 15-25 second format",
                "Experiment 3: test explicit CTA in final scene",
            ]
        return queue

    def suggest_content_angles(self, profile_id: str) -> list[str]:
        summary = self.intelligence_service.build_profile_content_summary(profile_id)
        successful = summary.get("successful_angles", [])
        if isinstance(successful, list) and successful:
            return [str(item) for item in successful[:5]]
        return ["format: concise storytelling", "hook: problem-solution", "cta: explicit next step"]

    def suggest_posting_windows(self, profile_id: str) -> list[str]:
        metrics = self.repository.list_metrics_snapshots(profile_id=profile_id, limit=200)
        if not metrics:
            return ["evening", "daytime"]
        buckets: dict[str, list[float]] = defaultdict(list)
        for metric in metrics:
            hour = metric.collected_at.hour
            bucket = "morning" if 6 <= hour < 12 else "daytime" if 12 <= hour < 18 else "evening" if 18 <= hour < 24 else "night"
            buckets[bucket].append(metric.weighted_engagement_score)
        ranking = sorted(buckets.items(), key=lambda item: mean(item[1]), reverse=True)
        return [item[0] for item in ranking[:3]]

    def summarize_content_direction(self, profile_id: str) -> str:
        comparison = self.top_content_service.compare_recent_vs_baseline(profile_id)
        if comparison["delta_ratio"] > 0.15:
            return "Momentum is positive; repeat best-performing angles and scale variants."
        if comparison["delta_ratio"] < -0.15:
            return "Momentum is declining; narrow scope and retest proven hooks."
        return "Momentum is stable; run controlled experiments and monitor variance."

    def get_latest_recommendations(self, profile_id: str, limit: int = 10) -> list[ContentRecommendation]:
        return self.repository.list_recommendations(profile_id, limit=limit)

    @staticmethod
    def _confidence_from_data(top_snapshots: list[ContentMetricsSnapshot]) -> ConfidenceLevel:
        if len(top_snapshots) >= 10:
            return ConfidenceLevel.HIGH
        if len(top_snapshots) >= 4:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def _build_recommendations(
        self,
        profile_id: str,
        successful_angles: list[str],
        weak_angles: list[str],
    ) -> list[ContentRecommendation]:
        recommendations: list[ContentRecommendation] = []
        for angle in successful_angles[:3]:
            recommendations.append(
                ContentRecommendation(
                    profile_id=profile_id,
                    recommendation_type=RecommendationType.REPEAT,
                    priority=PriorityLevel.HIGH,
                    title=f"Repeat strong angle: {angle}",
                    rationale="Consistently appears in top-performing content patterns.",
                    suggested_format=angle if angle.startswith("format:") else "",
                    based_on_snapshot_ids=[],
                )
            )
        for angle in weak_angles[:2]:
            recommendations.append(
                ContentRecommendation(
                    profile_id=profile_id,
                    recommendation_type=RecommendationType.STOP,
                    priority=PriorityLevel.MEDIUM,
                    title="Reduce weak angle exposure",
                    rationale=angle,
                    based_on_snapshot_ids=[],
                )
            )
        if not recommendations:
            recommendations.append(
                ContentRecommendation(
                    profile_id=profile_id,
                    recommendation_type=RecommendationType.TEST,
                    priority=PriorityLevel.MEDIUM,
                    title="Run baseline experiment queue",
                    rationale="Not enough data for confident specialization.",
                )
            )
        return recommendations
