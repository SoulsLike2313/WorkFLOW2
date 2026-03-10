from __future__ import annotations

from dataclasses import dataclass

from .errors import PolicyDeniedError
from .models import ManagementMode


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    requires_confirmation: bool = False


class PolicyGuard:
    """
    Guard layer that ensures management mode constraints are enforced
    before any state-changing action is performed.
    """

    def evaluate(self, management_mode: ManagementMode, action_type: str) -> PolicyDecision:
        mode = management_mode
        action = action_type.lower().strip()

        manual_allowed = {
            "connect_profile",
            "disconnect_profile",
            "open_session_window",
            "close_session_window",
            "sync_profile_state",
            "create_content_item",
            "validate_content_item",
            "generate_action_plan",
            "analyze_frame",
            "generate_video_brief",
            "read_only",
        }
        guided_allowed = manual_allowed | {
            "queue_content_item",
            "generate_recommendations",
            "suggest_next_step",
            "run_guided_sync",
        }
        managed_allowed = guided_allowed | {
            "connect_profile",
            "disconnect_profile",
            "refresh_metrics",
            "apply_recommendation_bundle",
            "submit_official_posting_flow",
        }

        if mode == ManagementMode.MANUAL:
            if action in manual_allowed:
                return PolicyDecision(allowed=True, reason="manual mode allows assistive actions")
            return PolicyDecision(allowed=False, reason="manual mode blocks autonomous execution")

        if mode == ManagementMode.GUIDED:
            if action in guided_allowed:
                needs_confirm = action in {"queue_content_item", "run_guided_sync", "apply_recommendation_bundle"}
                return PolicyDecision(
                    allowed=True,
                    reason="guided mode allows suggested actions",
                    requires_confirmation=needs_confirm,
                )
            return PolicyDecision(allowed=False, reason="guided mode denies unsupported action")

        if action in managed_allowed:
            needs_confirm = action in {"submit_official_posting_flow"}
            return PolicyDecision(
                allowed=True,
                reason="managed mode allows policy-approved system actions",
                requires_confirmation=needs_confirm,
            )
        return PolicyDecision(allowed=False, reason="managed mode denies unknown action")

    def enforce(
        self,
        management_mode: ManagementMode,
        action_type: str,
        *,
        confirmed: bool = False,
    ) -> None:
        decision = self.evaluate(management_mode, action_type)
        if not decision.allowed:
            raise PolicyDeniedError(action_type, management_mode.value, decision.reason)
        if decision.requires_confirmation and not confirmed:
            raise PolicyDeniedError(action_type, management_mode.value, "confirmation required")
