from __future__ import annotations

from .config import PlannerConfig
from .models import (
    ActionType,
    AccountState,
    AnalyticsReport,
    PerformanceLabel,
    PlanBundle,
    PlanStep,
    TaskItem,
    TaskStatus,
)


def _step_for_evaluation(creative_id: str, label: PerformanceLabel, summary: str) -> PlanStep:
    if label == PerformanceLabel.HIGH:
        return PlanStep(
            action_type=ActionType.SCALE_CREATIVE,
            title=f"Масштабировать креатив {creative_id}",
            rationale=summary,
            priority=2,
            payload={"creative_id": creative_id, "mode": "scale"},
        )
    if label == PerformanceLabel.LOW:
        return PlanStep(
            action_type=ActionType.REFINE_HOOK,
            title=f"Усилить хук для {creative_id}",
            rationale=summary,
            priority=1,
            payload={"creative_id": creative_id, "mode": "rewrite_intro"},
        )
    if label == PerformanceLabel.INSUFFICIENT_DATA:
        return PlanStep(
            action_type=ActionType.COLLECT_DATA,
            title=f"Собрать больше данных для {creative_id}",
            rationale=summary,
            priority=3,
            payload={"creative_id": creative_id, "target_views": 500},
        )
    return PlanStep(
        action_type=ActionType.RUN_AB_TEST,
        title=f"Запустить A/B-тест для {creative_id}",
        rationale=summary,
        priority=3,
        payload={"creative_id": creative_id, "variant_count": 2},
    )


def _step_for_task(task: TaskItem) -> PlanStep:
    return PlanStep(
        action_type=ActionType.EXECUTE_TASK,
        title=f"Задача: {task.title}",
        rationale=task.description or "Ожидающая задача из бэклога.",
        priority=task.priority,
        payload={"task_id": task.task_id},
    )


def generate_plan(
    account: AccountState,
    report: AnalyticsReport,
    tasks: list[TaskItem],
    planner_config: PlannerConfig,
) -> PlanBundle:
    steps: list[PlanStep] = []

    for evaluation in report.creative_evaluations:
        steps.append(_step_for_evaluation(evaluation.creative_id, evaluation.label, evaluation.summary))

    for task in tasks:
        if task.status in (TaskStatus.TODO, TaskStatus.IN_PROGRESS):
            steps.append(_step_for_task(task))

    if report.account_assessment.label == PerformanceLabel.HIGH:
        steps.append(
            PlanStep(
                action_type=ActionType.MONITOR_PROFILE,
                title="Контролировать стабильность профиля после масштабирования",
                rationale="Этап роста требует более плотного мониторинга на уровне профиля.",
                priority=2,
            )
        )
    elif report.account_assessment.label in (PerformanceLabel.LOW, PerformanceLabel.INSUFFICIENT_DATA):
        steps.append(
            PlanStep(
                action_type=ActionType.COLLECT_DATA,
                title="Провести базовый спринт сбора данных",
                rationale=report.account_assessment.summary,
                priority=1,
                payload={"window_days": 7},
            )
        )

    steps.sort(key=lambda step: step.priority)
    steps = steps[: planner_config.max_steps]

    summary = (
        f"План для {account.handle}: шагов={len(steps)}, "
        f"score={report.account_assessment.health_score}, "
        f"label={report.account_assessment.label.value}."
    )

    return PlanBundle(account_id=account.account_id, summary=summary, steps=steps)
