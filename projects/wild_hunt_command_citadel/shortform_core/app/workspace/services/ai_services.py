from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from ..diagnostics import diag_log
from ..errors import NotFoundError
from ..models import (
    AILearningRecord,
    AIHypothesis,
    AIOutcomeLink,
    AIPatternConfidenceHistory,
    AIPerceptionFrame,
    AIPerceptionResult,
    AIRecommendationFeedback,
    AIAssetReview,
    ActionResult,
    AssistiveScreenState,
    ContentRecommendation,
    LearningType,
    OutcomeLabel,
    PriorityLevel,
    RecommendationFeedbackStatus,
    RecommendationType,
    SourceType,
    VideoGenerationBrief,
)
from ..repository import WorkspaceRepository
from .analytics_services import ContentPlanningService
from .audit_service import AuditService


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AIPerceptionService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        audit_service: AuditService,
    ) -> None:
        self.repository = repository
        self.audit_service = audit_service

    def analyze_frame(
        self,
        *,
        profile_id: str,
        source_kind: SourceType,
        source_ref: str,
    ) -> AIPerceptionFrame:
        self._require_profile(profile_id)
        detected_objects = self.detect_scene_elements(source_ref)
        detected_text = self.extract_on_screen_text(source_ref)
        layout = {"focus_zone": "center", "density": "medium", "grid_balance": "stable"}
        inferred_context = self.summarize_visual_state(detected_objects, detected_text)
        confidence = 0.58

        frame = AIPerceptionFrame(
            profile_id=profile_id,
            source_kind=source_kind,
            source_ref=source_ref,
            detected_objects=detected_objects,
            detected_text=detected_text,
            detected_layout=layout,
            inferred_context=inferred_context,
            confidence=max(0.0, min(confidence, 1.0)),
        )
        self.repository.save_perception_frame(frame)

        result = self._build_perception_result(frame)
        self.repository.save_perception_result(result)

        self.repository.save_screen_state(
            AssistiveScreenState(
                profile_id=profile_id,
                screen_name="workspace_preview",
                detected_elements=[{"label": item, "kind": "object"} for item in detected_objects],
                confidence=frame.confidence,
                screenshot_ref=source_ref if source_kind in {SourceType.SCREENSHOT, SourceType.UPLOADED_FRAME} else None,
            )
        )
        self.audit_service.log_action(
            action_type="ai_perception_analyze_frame",
            profile_id=profile_id,
            action_payload={
                "source_kind": source_kind.value,
                "objects": len(frame.detected_objects),
                "text_blocks": len(frame.detected_text),
                "result_id": result.id,
            },
            result=ActionResult.SUCCESS,
        )
        diag_log(
            "ai_learning_logs",
            "ai_perception_frame",
            payload={
                "profile_id": profile_id,
                "frame_id": frame.id,
                "result_id": result.id,
                "readability_score": result.readability_score,
                "hook_strength_score": result.hook_strength_score,
            },
        )
        return frame

    def analyze_asset_preview(self, *, profile_id: str, source_ref: str) -> dict[str, Any]:
        frame = self.analyze_frame(profile_id=profile_id, source_kind=SourceType.ASSET_PREVIEW, source_ref=source_ref)
        result = self.repository.list_perception_results(profile_id, limit=1)[0]
        review = AIAssetReview(
            profile_id=profile_id,
            source_kind=SourceType.ASSET_PREVIEW,
            source_ref=source_ref,
            quality_score=max(0.0, min((result.readability_score + result.hook_strength_score) / 2.0, 1.0)),
            findings=[
                f"probable_format={result.probable_format}",
                f"visual_overload={result.visual_overload_score:.2f}",
            ],
            recommendation="Increase hook contrast in first 2 seconds." if result.hook_strength_score < 0.5 else "Hook looks clear.",
        )
        self.repository.save_asset_review(review)
        diag_log(
            "ai_learning_logs",
            "ai_asset_review",
            payload={"profile_id": profile_id, "review_id": review.id, "quality_score": review.quality_score},
        )
        return {
            "frame": frame.model_dump(mode="json"),
            "perception_result": result.model_dump(mode="json"),
            "asset_review": review.model_dump(mode="json"),
        }

    @staticmethod
    def detect_scene_elements(source_ref: str) -> list[str]:
        ref = source_ref.lower()
        candidates = {
            "face": ["face", "portrait", "person"],
            "caption_overlay": ["caption", "text", "subtitle"],
            "product": ["product", "item", "showcase"],
            "transition": ["transition", "cut", "scene"],
            "cta_block": ["cta", "follow", "save", "subscribe"],
        }
        result: list[str] = []
        for label, keywords in candidates.items():
            if any(keyword in ref for keyword in keywords):
                result.append(label)
        if not result:
            result = ["primary_subject", "background_context"]
        return result

    @staticmethod
    def extract_on_screen_text(source_ref: str) -> list[str]:
        tokens = source_ref.replace("_", " ").replace("-", " ").split()
        filtered = [token for token in tokens if len(token) >= 4][:8]
        return filtered

    @staticmethod
    def summarize_visual_state(detected_objects: list[str], detected_text: list[str]) -> str:
        objects = ", ".join(detected_objects[:3]) if detected_objects else "no major objects"
        text = ", ".join(detected_text[:3]) if detected_text else "no readable text"
        return f"Scene focus: {objects}. Visible text tokens: {text}."

    def _build_perception_result(self, frame: AIPerceptionFrame) -> AIPerceptionResult:
        probable_format = "talking_head" if "face" in frame.detected_objects else "visual_demo"
        readability = 0.78 if frame.detected_text else 0.45
        overload = min(len(frame.detected_objects) / 8.0, 1.0)
        hook_strength = 0.75 if any("hook" in token.lower() for token in frame.detected_text) else 0.52
        return AIPerceptionResult(
            profile_id=frame.profile_id,
            frame_id=frame.id,
            probable_format=probable_format,
            readability_score=readability,
            visual_overload_score=overload,
            hook_strength_score=hook_strength,
            structured_summary={
                "detected_objects": frame.detected_objects,
                "detected_text": frame.detected_text,
                "layout": frame.detected_layout,
            },
        )

    def _require_profile(self, profile_id: str) -> None:
        if self.repository.get_profile(profile_id) is None:
            raise NotFoundError("profile", profile_id)


class AIWorkflowService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        planning_service: ContentPlanningService,
    ) -> None:
        self.repository = repository
        self.planning_service = planning_service

    def summarize_current_state(self, profile_id: str) -> dict[str, Any]:
        profile = self.repository.get_profile(profile_id)
        if profile is None:
            raise NotFoundError("profile", profile_id)
        session = self.repository.get_session(profile_id)
        queued = self.repository.list_content_items(profile_id=profile_id, status=None)
        latest_plan = self.repository.get_latest_action_plan(profile_id)
        latest_perception = self.repository.list_perception_frames(profile_id, limit=1)
        summary = {
            "profile_id": profile_id,
            "management_mode": profile.management_mode.value,
            "status": profile.status.value,
            "session_state": session.runtime_state.value if session else "not_opened",
            "queued_content_count": len([item for item in queued if item.status.value == "queued"]),
            "latest_plan_generated_at": latest_plan.generated_at if latest_plan else None,
            "latest_perception_summary": latest_perception[0].inferred_context if latest_perception else None,
        }
        diag_log("runtime_logs", "ai_workflow_summary", payload=summary)
        return summary

    def infer_next_step(self, profile_id: str) -> str:
        summary = self.summarize_current_state(profile_id)
        if summary["session_state"] == "not_opened":
            return "Open a 9:16 session window for this profile."
        if summary["queued_content_count"] == 0:
            return "Validate draft content and queue at least one item."
        if summary["latest_plan_generated_at"] is None:
            return "Generate a fresh action plan from current metrics."
        return "Run metrics ingestion and compare recent vs baseline performance."

    def build_operator_guidance(self, profile_id: str) -> list[str]:
        suggestion = self.infer_next_step(profile_id)
        return [
            suggestion,
            "Check policy-bound actions before executing managed operations.",
            "Review explainable recommendations in AI Studio panel.",
        ]


class AILearningService:
    def __init__(self, *, repository: WorkspaceRepository, audit_service: AuditService) -> None:
        self.repository = repository
        self.audit_service = audit_service

    def ingest_feedback(
        self,
        *,
        profile_id: str,
        learning_type: LearningType,
        input_ref: str,
        outcome_summary: str,
        adjustment_summary: str,
        confidence_delta: float,
    ) -> AILearningRecord:
        self._require_profile(profile_id)
        record = AILearningRecord(
            profile_id=profile_id,
            learning_type=learning_type,
            input_ref=input_ref,
            outcome_summary=outcome_summary,
            adjustment_summary=adjustment_summary,
            confidence_delta=confidence_delta,
        )
        self.repository.save_learning_record(record)
        self.audit_service.log_action(
            action_type="ai_learning_ingest_feedback",
            profile_id=profile_id,
            action_payload={"learning_type": learning_type.value, "confidence_delta": confidence_delta},
            result=ActionResult.SUCCESS,
        )
        diag_log(
            "ai_learning_logs",
            "learning_feedback_ingested",
            payload={"profile_id": profile_id, "record_id": record.id, "confidence_delta": confidence_delta},
        )
        return record

    def ingest_user_feedback(
        self,
        *,
        profile_id: str,
        recommendation_id: str,
        feedback_status: RecommendationFeedbackStatus,
        user_notes: str = "",
        manual_score: float | None = None,
    ) -> AIRecommendationFeedback:
        self._require_profile(profile_id)
        feedback = AIRecommendationFeedback(
            profile_id=profile_id,
            recommendation_id=recommendation_id,
            feedback_status=feedback_status,
            user_notes=user_notes,
            manual_score=manual_score,
        )
        self.repository.save_recommendation_feedback(feedback)
        delta = self._feedback_to_delta(feedback_status, manual_score)
        self.adjust_confidence(
            profile_id=profile_id,
            pattern_label=f"recommendation:{recommendation_id}",
            confidence_delta=delta,
            reason=f"user_feedback:{feedback_status.value}",
        )
        diag_log(
            "ai_learning_logs",
            "user_feedback_ingested",
            payload={
                "profile_id": profile_id,
                "feedback_id": feedback.id,
                "recommendation_id": recommendation_id,
                "feedback_status": feedback_status.value,
            },
        )
        return feedback

    def ingest_content_performance_feedback(
        self,
        *,
        profile_id: str,
        recommendation_id: str,
        content_id: str,
        metrics_snapshot_ids: list[str],
        outcome_label: OutcomeLabel,
        outcome_summary: str,
    ) -> AIOutcomeLink:
        self._require_profile(profile_id)
        link = AIOutcomeLink(
            profile_id=profile_id,
            recommendation_id=recommendation_id,
            content_id=content_id,
            metrics_snapshot_ids=metrics_snapshot_ids,
            outcome_label=outcome_label,
            outcome_summary=outcome_summary,
        )
        self.repository.save_outcome_link(link)
        if outcome_label == OutcomeLabel.SUCCESS:
            self.promote_successful_patterns(profile_id=profile_id, pattern_labels=[f"recommendation:{recommendation_id}"])
        elif outcome_label == OutcomeLabel.FAILED:
            self.demote_failed_patterns(profile_id=profile_id, pattern_labels=[f"recommendation:{recommendation_id}"])
        diag_log(
            "ai_learning_logs",
            "performance_feedback_ingested",
            payload={
                "profile_id": profile_id,
                "outcome_link_id": link.id,
                "recommendation_id": recommendation_id,
                "outcome_label": outcome_label.value,
            },
        )
        return link

    def update_recommendation_weights(self, profile_id: str) -> dict[str, float]:
        records = self.repository.list_learning_records(profile_id, limit=200)
        positive = sum(item.confidence_delta for item in records if item.confidence_delta > 0)
        negative = abs(sum(item.confidence_delta for item in records if item.confidence_delta < 0))
        total = positive + negative
        boost = (positive / total) if total > 0 else 0.5
        damping = (negative / total) if total > 0 else 0.5
        return {"boost_factor": boost, "damping_factor": damping}

    def adjust_confidence(
        self,
        *,
        profile_id: str,
        pattern_label: str,
        confidence_delta: float,
        reason: str,
    ) -> AIPatternConfidenceHistory:
        self._require_profile(profile_id)
        hypotheses = self.repository.list_hypotheses(profile_id)
        hypothesis = next((item for item in hypotheses if item.label == pattern_label), None)
        if hypothesis is None:
            hypothesis = AIHypothesis(
                profile_id=profile_id,
                label=pattern_label,
                hypothesis_text=f"Pattern {pattern_label} impacts content performance.",
                confidence=0.5,
            )
            self.repository.save_hypothesis(hypothesis)

        before = hypothesis.confidence
        after = max(0.0, min(before + confidence_delta, 1.0))
        updated = hypothesis.model_copy(update={"confidence": after, "updated_at": _utc_now()})
        self._replace_hypothesis(profile_id, updated)

        history = AIPatternConfidenceHistory(
            profile_id=profile_id,
            pattern_label=pattern_label,
            confidence_before=before,
            confidence_after=after,
            reason=reason,
        )
        self.repository.save_pattern_confidence_history(history)
        return history

    def promote_successful_patterns(self, *, profile_id: str, pattern_labels: list[str]) -> list[AIPatternConfidenceHistory]:
        return [
            self.adjust_confidence(profile_id=profile_id, pattern_label=label, confidence_delta=0.08, reason="outcome_success")
            for label in pattern_labels
        ]

    def demote_failed_patterns(self, *, profile_id: str, pattern_labels: list[str]) -> list[AIPatternConfidenceHistory]:
        return [
            self.adjust_confidence(profile_id=profile_id, pattern_label=label, confidence_delta=-0.08, reason="outcome_failed")
            for label in pattern_labels
        ]

    def record_outcome(
        self,
        *,
        profile_id: str,
        input_ref: str,
        outcome_summary: str,
    ) -> AILearningRecord:
        return self.ingest_feedback(
            profile_id=profile_id,
            learning_type=LearningType.PERFORMANCE_FEEDBACK,
            input_ref=input_ref,
            outcome_summary=outcome_summary,
            adjustment_summary="auto-captured performance outcome",
            confidence_delta=0.05,
        )

    def summarize_learnings(self, profile_id: str) -> dict[str, Any]:
        records = self.repository.list_learning_records(profile_id, limit=100)
        hypotheses = self.repository.list_hypotheses(profile_id, limit=20)
        feedback = self.repository.list_recommendation_feedback(profile_id, limit=20)
        outcomes = self.repository.list_outcome_links(profile_id, limit=20)
        if not records and not hypotheses and not feedback and not outcomes:
            return {"profile_id": profile_id, "total_records": 0, "summary": "No learning records yet."}

        by_type: dict[str, int] = defaultdict(int)
        avg_delta = 0.0
        for item in records:
            by_type[item.learning_type.value] += 1
            avg_delta += item.confidence_delta
        avg_delta = avg_delta / len(records) if records else 0.0
        return {
            "profile_id": profile_id,
            "total_records": len(records),
            "feedback_count": len(feedback),
            "outcome_links": len(outcomes),
            "by_type": dict(by_type),
            "average_confidence_delta": avg_delta,
            "top_hypotheses": [item.model_dump(mode="json") for item in sorted(hypotheses, key=lambda x: x.confidence, reverse=True)[:5]],
            "latest": records[0].outcome_summary if records else "No direct learning records",
        }

    def _replace_hypothesis(self, profile_id: str, updated: AIHypothesis) -> None:
        current = self.repository.list_hypotheses(profile_id)
        replaced: list[AIHypothesis] = []
        found = False
        for item in current:
            if item.id == updated.id:
                replaced.append(updated)
                found = True
            else:
                replaced.append(item)
        if not found:
            replaced.append(updated)
        self.repository.replace_hypotheses(profile_id, replaced)

    @staticmethod
    def _feedback_to_delta(status: RecommendationFeedbackStatus, manual_score: float | None) -> float:
        if status == RecommendationFeedbackStatus.ACCEPTED:
            return 0.06 if manual_score is None else (manual_score - 0.5) * 0.2
        if status == RecommendationFeedbackStatus.EDITED:
            return 0.02 if manual_score is None else (manual_score - 0.5) * 0.1
        return -0.06 if manual_score is None else (manual_score - 0.5) * 0.2

    def _require_profile(self, profile_id: str) -> None:
        if self.repository.get_profile(profile_id) is None:
            raise NotFoundError("profile", profile_id)


class AICreativeDirectorService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        planning_service: ContentPlanningService,
        audit_service: AuditService,
    ) -> None:
        self.repository = repository
        self.planning_service = planning_service
        self.audit_service = audit_service

    def evaluate_content_item(self, content_id: str) -> dict[str, Any]:
        item = self.repository.get_content_item(content_id)
        if item is None:
            raise NotFoundError("content_item", content_id)

        score = 0.0
        feedback: list[str] = []
        if item.hook_label:
            score += 0.25
        else:
            feedback.append("Добавь явный hook в первые 1-2 секунды.")
        if item.duration is not None and 12 <= item.duration <= 45:
            score += 0.25
        else:
            feedback.append("Проверь длительность: для short-form чаще работает 12-45 сек.")
        if item.caption and len(item.caption) <= 220:
            score += 0.2
        else:
            feedback.append("Сделай caption короче и конкретнее.")
        if item.cta_label:
            score += 0.15
        else:
            feedback.append("Добавь CTA (что сделать после просмотра).")
        if item.format_label and item.topic_label:
            score += 0.15
        else:
            feedback.append("Уточни format/topic labels для аналитики и планирования.")

        result = {
            "content_id": content_id,
            "profile_id": item.profile_id,
            "quality_score": round(score, 3),
            "quality_level": "strong" if score >= 0.75 else "medium" if score >= 0.5 else "weak",
            "feedback": feedback or ["Контент выглядит структурированно для теста публикации."],
            "visual_direction": self.suggest_visual_direction(item.topic_label or "generic"),
            "audio_direction": self.suggest_audio_direction(item.topic_label or "generic"),
            "caption_variants": self.suggest_caption_variants(item.topic_label or "generic"),
        }
        self.audit_service.log_action(
            action_type="ai_evaluate_content_item",
            profile_id=item.profile_id,
            action_payload={"content_id": content_id, "quality_score": result["quality_score"]},
            result=ActionResult.SUCCESS,
        )
        diag_log(
            "ai_learning_logs",
            "content_evaluated",
            payload={"profile_id": item.profile_id, "content_id": content_id, "quality_score": result["quality_score"]},
        )
        return result

    def generate_video_brief(
        self,
        *,
        profile_id: str,
        source_recommendation_ids: list[str] | None = None,
        creative_goal: str,
        target_format: str,
        target_duration: str,
        visual_style: str,
        hook: str,
        cta: str,
    ) -> VideoGenerationBrief:
        self._require_profile(profile_id)
        brief = VideoGenerationBrief(
            profile_id=profile_id,
            source_recommendation_ids=source_recommendation_ids or [],
            creative_goal=creative_goal,
            target_format=target_format,
            target_duration=target_duration,
            visual_style=visual_style,
            hook=hook,
            narrative_steps=self.suggest_script_outline(hook=hook, topic=creative_goal),
            shot_plan=[
                "Shot 1: Hook scene with immediate tension.",
                "Shot 2: Context explanation with visual proof.",
                "Shot 3: Resolution + CTA frame.",
            ],
            voiceover_notes="Use concise energetic tone with one clear promise.",
            on_screen_text=[hook, "Main value in 3-5 words", cta],
            cta=cta,
            safety_notes=[
                "Avoid misleading claims.",
                "Respect platform policy and rights for assets.",
                "Run manual quality check before publishing.",
            ],
        )
        self.repository.save_video_brief(brief)
        self.audit_service.log_action(
            action_type="ai_generate_video_brief",
            profile_id=profile_id,
            action_payload={"brief_id": brief.id, "target_format": target_format},
            result=ActionResult.SUCCESS,
        )
        return brief

    def generate_variant_ideas(self, profile_id: str, count: int = 3) -> list[str]:
        self._require_profile(profile_id)
        angles = self.planning_service.suggest_content_angles(profile_id)
        variants: list[str] = []
        for index in range(count):
            angle = angles[index % len(angles)] if angles else "baseline angle"
            variants.append(f"Variant {index + 1}: reinterpret '{angle}' with a new opening visual.")
        return variants

    @staticmethod
    def suggest_hooks(topic: str, count: int = 3) -> list[str]:
        base = topic.strip() or "your topic"
        return [
            f"Stop scrolling: here's the hidden mistake in {base}.",
            f"Most creators miss this step in {base}.",
            f"Try this 10-second trick before your next {base} post.",
        ][:count]

    def suggest_script_outline(self, *, hook: str, topic: str) -> list[str]:
        return [
            f"Hook: {hook}",
            f"Problem setup around {topic}",
            "Evidence/example with one clear metric",
            "Resolution with practical next step",
            "Final CTA",
        ]

    @staticmethod
    def suggest_visual_direction(topic: str) -> str:
        return f"High-contrast visual narrative for topic '{topic}', with clean focal composition."

    @staticmethod
    def suggest_audio_direction(topic: str) -> str:
        return f"Rhythmic but unobtrusive bed track, clear spoken voice for '{topic}'."

    @staticmethod
    def suggest_caption_variants(topic: str) -> list[str]:
        return [
            f"{topic}: tactical breakdown in 30 seconds.",
            f"{topic}: do this before your next post.",
            f"{topic}: 1 change that improves retention.",
        ]

    def _require_profile(self, profile_id: str) -> None:
        if self.repository.get_profile(profile_id) is None:
            raise NotFoundError("profile", profile_id)


class AIRecommendationService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        planning_service: ContentPlanningService,
    ) -> None:
        self.repository = repository
        self.planning_service = planning_service

    def merge_analytics_and_perception(self, profile_id: str) -> dict[str, Any]:
        analytics = self.planning_service.get_latest_recommendations(profile_id, limit=10)
        perception = self.repository.list_perception_results(profile_id, limit=10)
        learning = self.repository.list_learning_records(profile_id, limit=10)
        merged = {
            "profile_id": profile_id,
            "analytics_recommendations": [item.model_dump(mode="json") for item in analytics],
            "perception_signals": [item.model_dump(mode="json") for item in perception],
            "learning_signals": [item.model_dump(mode="json") for item in learning],
        }
        diag_log("ai_learning_logs", "analytics_perception_merged", payload={"profile_id": profile_id})
        return merged

    def generate_explainable_recommendations(self, profile_id: str, limit: int = 10) -> list[ContentRecommendation]:
        merged = self.merge_analytics_and_perception(profile_id)
        existing = self.planning_service.get_latest_recommendations(profile_id, limit=limit)
        if existing:
            return self.rank_recommendations(existing)[:limit]

        perception_count = len(merged["perception_signals"])
        fallback = [
            ContentRecommendation(
                profile_id=profile_id,
                recommendation_type=RecommendationType.TEST,
                priority=PriorityLevel.MEDIUM,
                title="Collect more baseline data",
                rationale="No stable analytics recommendations available yet.",
                supporting_signals=[f"perception_signals={perception_count}", "analytics_missing"],
                confidence=0.42,
                alternatives=["Run 3 baseline formats", "Collect 7-day engagement trend"],
                suggested_action="Ingest at least 5 metrics snapshots and rerun planning.",
                suggested_duration_range="15-30 sec",
                suggested_posting_window="evening",
            ),
            ContentRecommendation(
                profile_id=profile_id,
                recommendation_type=RecommendationType.IMPROVE,
                priority=PriorityLevel.LOW,
                title="Use perception summaries in review",
                rationale=f"Perception frames available: {perception_count}",
                supporting_signals=["visual_state_summary"],
                confidence=0.38,
                alternatives=["Manual visual QA checklist", "Hook readability pre-check"],
                suggested_action="Review on-screen text clarity before queueing content.",
            ),
        ]
        self.repository.replace_recommendations(profile_id, fallback)
        return fallback

    @staticmethod
    def rank_recommendations(recommendations: list[ContentRecommendation]) -> list[ContentRecommendation]:
        priority_rank = {PriorityLevel.HIGH: 3, PriorityLevel.MEDIUM: 2, PriorityLevel.LOW: 1}
        return sorted(
            recommendations,
            key=lambda item: (priority_rank.get(item.priority, 0), item.confidence, item.created_at),
            reverse=True,
        )
