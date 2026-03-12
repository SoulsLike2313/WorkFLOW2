from __future__ import annotations

from typing import Any

from ..diagnostics import diag_log
from ..errors import NotFoundError
from ..models import (
    AudioGenerationBrief,
    CreativeManifest,
    GenerationAssetBundle,
    PromptPack,
    ScriptGenerationBrief,
    TextGenerationBrief,
    VideoGenerationBrief,
)
from ..repository import WorkspaceRepository
from .audit_service import AuditService


class GenerationPreparationService:
    def __init__(self, *, repository: WorkspaceRepository, audit_service: AuditService) -> None:
        self.repository = repository
        self.audit_service = audit_service

    def generate_video_brief(
        self,
        *,
        profile_id: str,
        content_goal: str,
        creative_angle: str,
        hook: str,
        format_target: str,
        duration_target: str,
    ) -> VideoGenerationBrief:
        self._require_profile(profile_id)
        brief = VideoGenerationBrief(
            profile_id=profile_id,
            creative_goal=content_goal,
            target_format=format_target,
            target_duration=duration_target,
            visual_style=creative_angle,
            hook=hook,
            narrative_steps=[f"Hook: {hook}", "Problem framing", "Main value", "CTA"],
            shot_plan=["Shot 1: hook", "Shot 2: proof", "Shot 3: CTA"],
            voiceover_notes="Concise, clear, energetic.",
            on_screen_text=[hook, "Main benefit", "CTA"],
            cta="Follow for next part",
        )
        self.repository.save_video_brief(brief)
        diag_log(
            "ai_learning_logs",
            "video_brief_generated",
            payload={"profile_id": profile_id, "brief_id": brief.id, "content_goal": content_goal},
        )
        return brief

    def generate_audio_brief(
        self,
        *,
        profile_id: str,
        content_goal: str,
        music_mood: str,
        voice_style: str,
    ) -> AudioGenerationBrief:
        self._require_profile(profile_id)
        brief = AudioGenerationBrief(
            profile_id=profile_id,
            content_goal=content_goal,
            music_mood=music_mood,
            voice_style=voice_style,
            pacing_notes="Pace up in hook, slow down at CTA.",
            narration_notes="Keep words under 120 for short-form clip.",
        )
        self.repository.save_audio_brief(brief)
        diag_log("ai_learning_logs", "audio_brief_generated", payload={"profile_id": profile_id, "brief_id": brief.id})
        return brief

    def generate_script_brief(
        self,
        *,
        profile_id: str,
        content_goal: str,
        hook: str,
        cta: str,
    ) -> ScriptGenerationBrief:
        self._require_profile(profile_id)
        brief = ScriptGenerationBrief(
            profile_id=profile_id,
            content_goal=content_goal,
            hook=hook,
            cta=cta,
            script_outline=[
                f"Hook line: {hook}",
                "State one pain point",
                "Show one tactical fix",
                f"Close with CTA: {cta}",
            ],
        )
        self.repository.save_script_brief(brief)
        diag_log("ai_learning_logs", "script_brief_generated", payload={"profile_id": profile_id, "brief_id": brief.id})
        return brief

    def generate_text_brief(
        self,
        *,
        profile_id: str,
        content_goal: str,
        cta_options: list[str] | None = None,
    ) -> TextGenerationBrief:
        self._require_profile(profile_id)
        brief = TextGenerationBrief(
            profile_id=profile_id,
            content_goal=content_goal,
            captions=[
                f"{content_goal}: tactical version",
                f"{content_goal}: beginner version",
            ],
            hashtag_groups=[["#shorts", "#growth"], ["#content", "#strategy"]],
            cta_options=cta_options or ["Save this", "Follow for more", "Try this today"],
        )
        self.repository.save_text_brief(brief)
        diag_log("ai_learning_logs", "text_brief_generated", payload={"profile_id": profile_id, "brief_id": brief.id})
        return brief

    def build_generation_bundle(
        self,
        *,
        profile_id: str,
        content_goal: str,
        creative_angle: str,
        format_target: str,
        duration_target: str,
    ) -> GenerationAssetBundle:
        self._require_profile(profile_id)
        recommendations = self.repository.list_recommendations(profile_id, limit=5)
        patterns = self.repository.list_content_patterns(profile_id, limit=5)
        latest_perf = self.repository.list_profile_performance(profile_id, limit=1)
        metrics_summary: dict[str, Any] = latest_perf[0].model_dump(mode="json") if latest_perf else {}

        prompt_pack = PromptPack(
            profile_id=profile_id,
            prompts={
                "video_prompt": f"{creative_angle} style, {duration_target}, {format_target}",
                "script_prompt": f"Build short-form script for goal: {content_goal}",
            },
            model_hints={"safety": "keep factual", "tone": "clear and practical"},
        )
        self.repository.save_prompt_pack(prompt_pack)

        manifest = CreativeManifest(
            profile_id=profile_id,
            title=f"{content_goal} manifest",
            scene_descriptions=["Hook scene", "Proof scene", "CTA scene"],
            pacing_notes="Fast opening, stable middle, strong ending.",
            safety_notes=["No misleading claims", "Check rights for assets"],
        )
        self.repository.save_creative_manifest(manifest)

        bundle = GenerationAssetBundle(
            profile_id=profile_id,
            content_goal=content_goal,
            creative_angle=creative_angle,
            source_recommendations=[item.id for item in recommendations],
            source_patterns=[item.label for item in patterns],
            source_metrics_summary=metrics_summary,
            selected_visual_references=[],
            selected_audio_references=[],
            script_outline=["Hook", "Value", "CTA"],
            voiceover_draft="Hook quickly, explain one fix, close with CTA.",
            caption_draft=f"{content_goal}. Keep it practical and concise.",
            on_screen_text_blocks=["Hook", "Value", "CTA"],
            shot_plan=["Shot 1", "Shot 2", "Shot 3"],
            duration_target=duration_target,
            format_target=format_target,
            generation_ready_flag=True,
            validation_notes=["Manual QA required before publishing."],
            prompt_pack_id=prompt_pack.id,
            manifest_id=manifest.id,
        )
        self.repository.save_generation_bundle(bundle)
        diag_log(
            "ai_learning_logs",
            "generation_asset_bundle_built",
            payload={
                "profile_id": profile_id,
                "bundle_id": bundle.id,
                "recommendation_count": len(bundle.source_recommendations),
                "pattern_count": len(bundle.source_patterns),
            },
        )
        return bundle

    def list_generation_bundles(self, profile_id: str, limit: int = 20) -> list[GenerationAssetBundle]:
        return self.repository.list_generation_bundles(profile_id, limit=limit)

    def _require_profile(self, profile_id: str) -> None:
        if self.repository.get_profile(profile_id) is None:
            raise NotFoundError("profile", profile_id)
