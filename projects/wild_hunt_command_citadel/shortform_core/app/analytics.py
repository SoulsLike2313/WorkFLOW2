from __future__ import annotations

from collections import defaultdict

from .config import Thresholds
from .models import (
    AccountAssessment,
    AccountState,
    AnalyticsReport,
    CreativeAsset,
    CreativeEvaluation,
    MetricSnapshot,
    PerformanceLabel,
)


def _clamp_score(value: float) -> int:
    return int(max(0, min(100, round(value))))


def _aggregate_metrics(metrics: list[MetricSnapshot]) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "count": 0,
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "saves": 0,
            "engagement_sum": 0.0,
        }
    )
    for metric in metrics:
        if not metric.creative_id:
            continue
        bucket = totals[metric.creative_id]
        bucket["count"] += 1
        bucket["views"] += metric.views
        bucket["likes"] += metric.likes
        bucket["comments"] += metric.comments
        bucket["shares"] += metric.shares
        bucket["saves"] += metric.saves
        bucket["engagement_sum"] += metric.engagement_rate
    return totals


def evaluate_creatives(
    creatives: list[CreativeAsset],
    metrics: list[MetricSnapshot],
    thresholds: Thresholds,
) -> list[CreativeEvaluation]:
    aggregates = _aggregate_metrics(metrics)
    evaluations: list[CreativeEvaluation] = []

    for creative in creatives:
        aggregate = aggregates.get(creative.creative_id)
        if not aggregate:
            evaluations.append(
                CreativeEvaluation(
                    creative_id=creative.creative_id,
                    score=25,
                    label=PerformanceLabel.INSUFFICIENT_DATA,
                    summary="Недостаточно метрик для оценки этого креатива.",
                    recommendations=[
                        "Соберите хотя бы один полный цикл метрик.",
                        "Оставьте креатив в тесте до набора достаточных просмотров.",
                    ],
                    metrics_count=0,
                    total_views=0,
                    average_engagement_rate=0.0,
                )
            )
            continue

        total_views = int(aggregate["views"])
        metrics_count = int(aggregate["count"])
        average_engagement = aggregate["engagement_sum"] / float(max(metrics_count, 1))

        score = 50.0
        label = PerformanceLabel.MEDIUM
        summary = "Результат стабильный, продолжайте контролируемое тестирование."
        recommendations = [
            "Запустите один точечный вариант для проверки устойчивости хука.",
            "Отслеживайте качество комментариев вместе с engagement rate.",
        ]

        if total_views < thresholds.min_views_for_evaluation:
            score -= 20
            label = PerformanceLabel.INSUFFICIENT_DATA
            summary = "Трафик ниже порога для корректной оценки."
            recommendations = [
                "Увеличьте охват до принятия ключевых решений.",
                "Отложите крупные правки, пока не наберете достаточно просмотров.",
            ]
        elif average_engagement >= thresholds.strong_engagement_rate:
            score += 30
            label = PerformanceLabel.HIGH
            summary = "Креатив показывает высокий результат и готов к масштабированию."
            recommendations = [
                "Масштабируйте формат с небольшими вариациями темы.",
                "Переиспользуйте структуру хука для соседних контент-кластеров.",
            ]
        elif average_engagement <= thresholds.low_engagement_rate:
            score -= 25
            label = PerformanceLabel.LOW
            summary = "Креатив проседает и требует структурных правок."
            recommendations = [
                "Перепишите хук в первые 2 секунды.",
                "Проверьте более явный CTA и более плотный темп подачи.",
            ]

        evaluations.append(
            CreativeEvaluation(
                creative_id=creative.creative_id,
                score=_clamp_score(score),
                label=label,
                summary=summary,
                recommendations=recommendations,
                metrics_count=metrics_count,
                total_views=total_views,
                average_engagement_rate=round(average_engagement, 4),
            )
        )

    evaluations.sort(key=lambda item: (item.score, item.total_views), reverse=True)
    return evaluations


def evaluate_account(
    account: AccountState,
    metrics: list[MetricSnapshot],
    thresholds: Thresholds,
) -> AccountAssessment:
    if not metrics:
        return AccountAssessment(
            account_id=account.account_id,
            health_score=20,
            label=PerformanceLabel.INSUFFICIENT_DATA,
            summary="Нет метрик для оценки. Сначала запустите сбор данных.",
            risk_flags=["missing_metrics"],
            next_focus=["Соберите базовые метрики по активным креативам."],
        )

    total_views = sum(metric.views for metric in metrics)
    avg_engagement = sum(metric.engagement_rate for metric in metrics) / float(len(metrics))

    score = 55.0
    label = PerformanceLabel.MEDIUM
    risk_flags: list[str] = []
    focus: list[str] = []
    summary = "Аккаунт стабилен, есть потенциал для оптимизации."

    if total_views < thresholds.min_views_for_evaluation:
        score -= 20
        label = PerformanceLabel.INSUFFICIENT_DATA
        risk_flags.append("low_total_views")
        focus.append("Увеличьте выборку перед стратегическими изменениями.")
        summary = "Суммарных просмотров пока недостаточно для надежных выводов."
    elif avg_engagement >= thresholds.strong_engagement_rate:
        score += 25
        label = PerformanceLabel.HIGH
        focus.append("Масштабируйте выигрышные паттерны и контролируйте качество.")
        summary = "Аккаунт в сильной динамике, engagement выше целевого."
    elif avg_engagement <= thresholds.low_engagement_rate:
        score -= 25
        label = PerformanceLabel.LOW
        risk_flags.append("low_engagement")
        focus.append("В следующем спринте приоритет: хук и сторителлинг.")
        summary = "Engagement просел ниже порога и требует корректировки."
    else:
        focus.append("Продолжайте еженедельные A/B-тесты для хуков и CTA.")

    return AccountAssessment(
        account_id=account.account_id,
        health_score=_clamp_score(score),
        label=label,
        summary=summary,
        risk_flags=risk_flags,
        next_focus=focus,
    )


def run_analytics(
    account: AccountState,
    creatives: list[CreativeAsset],
    metrics: list[MetricSnapshot],
    thresholds: Thresholds,
) -> AnalyticsReport:
    creative_evaluations = evaluate_creatives(creatives=creatives, metrics=metrics, thresholds=thresholds)
    account_assessment = evaluate_account(account=account, metrics=metrics, thresholds=thresholds)
    return AnalyticsReport(
        account_assessment=account_assessment,
        creative_evaluations=creative_evaluations,
        metric_count=len(metrics),
    )
