from __future__ import annotations

from pathlib import Path

from .analytics import run_analytics
from .config import AppConfig, load_config
from .demo_data import build_demo_bundle
from .io_utils import write_json, write_jsonl
from .planner import generate_plan
from .repository import SQLiteRepository


def run_demo(config: AppConfig | None = None) -> dict[str, object]:
    cfg = config or load_config()
    bundle = build_demo_bundle(cfg.storage.tiktok_snapshot_dir)

    repository = SQLiteRepository(cfg.storage.database_path)
    repository.init_schema()
    repository.save_bundle(bundle)

    metrics = repository.list_metrics(bundle.account.account_id, limit=cfg.thresholds.metric_window_size)
    report = run_analytics(
        account=bundle.account,
        creatives=bundle.creatives,
        metrics=metrics,
        thresholds=cfg.thresholds,
    )
    plan = generate_plan(
        account=bundle.account,
        report=report,
        tasks=bundle.tasks,
        planner_config=cfg.planner,
    )
    repository.store_plan(plan)

    output_dir = cfg.storage.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "analytics_report.json"
    plan_path = output_dir / "plan_bundle.json"
    events_path = output_dir / "events_export.jsonl"
    summary_path = output_dir / "demo_summary.json"

    write_json(report_path, report)
    write_json(plan_path, plan)
    write_jsonl(events_path, bundle.events)

    summary_payload = {
        "account_id": bundle.account.account_id,
        "handle": bundle.account.handle,
        "database_path": str(cfg.storage.database_path),
        "snapshot_dir": str(cfg.storage.tiktok_snapshot_dir),
        "metrics_used": len(metrics),
        "creatives": len(bundle.creatives),
        "tasks": len(bundle.tasks),
        "plan_steps": len(plan.steps),
        "files": {
            "analytics_report": str(report_path),
            "plan_bundle": str(plan_path),
            "events_export": str(events_path),
        },
    }
    write_json(summary_path, summary_payload)
    return summary_payload


def _print_summary(summary: dict[str, object]) -> None:
    print("Демо-запуск Shortform Core завершен.")
    print(f"Аккаунт: {summary['account_id']} ({summary['handle']})")
    print(f"Шагов плана: {summary['plan_steps']}")
    files = summary.get("files", {})
    if isinstance(files, dict):
        for label, path in files.items():
            print(f"- {label}: {path}")


def main() -> int:
    summary = run_demo()
    _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
