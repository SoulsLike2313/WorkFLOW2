from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import (
    AccountState,
    CoreBundle,
    CreativeAsset,
    ExternalEvent,
    Hypothesis,
    MetricSnapshot,
    TaskItem,
)


class OpsRegistry:
    """In-memory state registry used by analytics and planning layers."""

    def __init__(self) -> None:
        self.accounts: dict[str, AccountState] = {}
        self.creatives: dict[str, CreativeAsset] = {}
        self.hypotheses: dict[str, Hypothesis] = {}
        self.tasks: dict[str, TaskItem] = {}
        self.metrics: list[MetricSnapshot] = []
        self.events: list[ExternalEvent] = []
        self._metrics_by_account: dict[str, list[MetricSnapshot]] = defaultdict(list)
        self._metrics_by_creative: dict[str, list[MetricSnapshot]] = defaultdict(list)

    @classmethod
    def from_bundle(cls, bundle: CoreBundle) -> "OpsRegistry":
        registry = cls()
        registry.register_account(bundle.account)
        for creative in bundle.creatives:
            registry.register_creative(creative)
        for hypothesis in bundle.hypotheses:
            registry.register_hypothesis(hypothesis)
        for task in bundle.tasks:
            registry.register_task(task)
        for metric in bundle.metrics:
            registry.add_metric(metric)
        for event in bundle.events:
            registry.add_event(event)
        return registry

    def register_account(self, account: AccountState) -> None:
        self.accounts[account.account_id] = account

    def register_creative(self, creative: CreativeAsset) -> None:
        self.creatives[creative.creative_id] = creative

    def register_hypothesis(self, hypothesis: Hypothesis) -> None:
        self.hypotheses[hypothesis.hypothesis_id] = hypothesis

    def register_task(self, task: TaskItem) -> None:
        self.tasks[task.task_id] = task

    def add_metric(self, snapshot: MetricSnapshot) -> None:
        self.metrics.append(snapshot)
        self._metrics_by_account[snapshot.account_id].append(snapshot)
        if snapshot.creative_id:
            self._metrics_by_creative[snapshot.creative_id].append(snapshot)

    def add_event(self, event: ExternalEvent) -> None:
        self.events.append(event)

    def list_account_creatives(self, account_id: str) -> list[CreativeAsset]:
        return [creative for creative in self.creatives.values() if creative.account_id == account_id]

    def list_account_tasks(self, account_id: str) -> list[TaskItem]:
        return [task for task in self.tasks.values() if task.account_id == account_id]

    def list_account_metrics(self, account_id: str) -> list[MetricSnapshot]:
        return list(self._metrics_by_account.get(account_id, []))

    def list_creative_metrics(self, creative_id: str) -> list[MetricSnapshot]:
        return list(self._metrics_by_creative.get(creative_id, []))

    def iter_accounts(self) -> Iterable[AccountState]:
        return self.accounts.values()
