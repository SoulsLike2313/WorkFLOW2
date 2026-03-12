from __future__ import annotations

from app.workspace.models import ConnectionType, ManagementMode, Platform
from app.workspace.policy import PolicyGuard
from app.workspace.services.analytics_services import AnalyticsFormulaService


def test_policy_evaluation():
    guard = PolicyGuard()
    denied = guard.evaluate(ManagementMode.MANUAL, "submit_official_posting_flow")
    assert denied.allowed is False
    allowed = guard.evaluate(ManagementMode.GUIDED, "queue_content_item")
    assert allowed.allowed is True
    assert allowed.requires_confirmation is True


def test_formula_engagement_rate():
    formulas = AnalyticsFormulaService(
        weights={
            "views_weight": 0.05,
            "likes_weight": 1.0,
            "comments_weight": 2.5,
            "shares_weight": 3.0,
            "favorites_weight": 1.5,
            "watch_time_weight": 0.5,
            "completion_weight": 1.0,
        }
    )
    rate = formulas.engagement_rate(views=1000, likes=100, comments_count=20, shares=10, favorites=5)
    assert rate > 0

