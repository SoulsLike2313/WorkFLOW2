from __future__ import annotations

from .analytics import run_analytics
from .config import load_config
from .demo_data import build_demo_bundle
from .io_utils import write_json
from .planner import generate_plan
from .repository import SQLiteRepository


def bootstrap() -> dict[str, object]:
    config = load_config()
    bundle = build_demo_bundle(config.storage.tiktok_snapshot_dir)

    repository = SQLiteRepository(config.storage.database_path)
    repository.init_schema()
    repository.save_bundle(bundle)

    metrics = repository.list_metrics(bundle.account.account_id, limit=config.thresholds.metric_window_size)
    report = run_analytics(
        account=bundle.account,
        creatives=bundle.creatives,
        metrics=metrics,
        thresholds=config.thresholds,
    )
    plan = generate_plan(
        account=bundle.account,
        report=report,
        tasks=bundle.tasks,
        planner_config=config.planner,
    )
    repository.store_plan(plan)

    payload = {
        "status": "инициализировано",
        "account_id": bundle.account.account_id,
        "creatives": len(bundle.creatives),
        "metrics": len(metrics),
        "tasks": len(bundle.tasks),
        "events": len(bundle.events),
        "plan_steps": len(plan.steps),
    }
    write_json(config.storage.output_dir / "bootstrap_v2.json", payload)
    return payload


def main() -> int:
    payload = bootstrap()
    print("Bootstrap v2 завершен.")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
