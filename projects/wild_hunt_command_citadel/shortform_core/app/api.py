from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from .analytics import run_analytics
from .config import AppConfig, load_config
from .demo_data import build_demo_bundle
from .models import MetricSnapshot
from .planner import generate_plan
from .readiness import ReadinessService
from .repository import SQLiteRepository
from .update import PatchBundle, UpdateService
from .schemas import (
    AccountSnapshotResponse,
    GeneratePlanRequest,
    GeneratePlanResponse,
    HealthResponse,
    IngestMetricsRequest,
    IngestMetricsResponse,
    LoadDemoResponse,
)
from .workspace.api import build_workspace_router
from .workspace.runtime import WorkspaceRuntime, build_workspace_runtime


def _build_runtime() -> tuple[AppConfig, SQLiteRepository, WorkspaceRuntime]:
    config = load_config()
    repository = SQLiteRepository(config.storage.database_path)
    repository.init_schema()
    workspace_runtime = build_workspace_runtime(
        max_profiles=config.workspace.max_profiles,
        analytics_weights=config.workspace.analytics_weights.model_dump(),
        log_dir=config.storage.logs_dir,
        debug_logs=config.workspace.debug_logs,
        persistence_path=config.storage.workspace_state_path,
    )
    return config, repository, workspace_runtime


CONFIG, REPOSITORY, WORKSPACE = _build_runtime()
READINESS = ReadinessService()
UPDATES = UpdateService(CONFIG)

app = FastAPI(
    title="Ядро Shortform Content Ops",
    description="API для оркестрации и поддержки решений в short-form workflow.",
    version="0.1.0",
)
app.include_router(build_workspace_router(WORKSPACE))


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        database_path=str(CONFIG.storage.database_path),
        snapshot_dir=str(CONFIG.storage.tiktok_snapshot_dir),
    )


@app.get("/readiness")
def readiness() -> dict[str, object]:
    payload = READINESS.evaluate_local(config=CONFIG, workspace_runtime=WORKSPACE)
    api_check = READINESS.evaluate_api(base_url=f"http://{CONFIG.api_host}:{CONFIG.api_port}")
    payload["api_ready"] = {"ready": api_check.ready, "reason": api_check.reason}
    return payload


@app.get("/updates/version")
def updates_version() -> dict[str, object]:
    return {"version": UPDATES.get_current_version().model_dump(mode="json")}


@app.post("/updates/check")
def updates_check(manifest_path: str) -> dict[str, object]:
    return UPDATES.check_for_update(Path(manifest_path))


@app.post("/updates/apply-local")
def updates_apply_local(bundle_path: str, target_version: str) -> dict[str, object]:
    bundle = PatchBundle(bundle_path=Path(bundle_path), target_version=target_version)
    return {"result": UPDATES.apply_local_patch(bundle).model_dump(mode="json")}


@app.get("/updates/post-verify")
def updates_post_verify() -> dict[str, object]:
    return UPDATES.post_update_verification()


@app.post("/bootstrap/load-demo", response_model=LoadDemoResponse)
def load_demo() -> LoadDemoResponse:
    bundle = build_demo_bundle(CONFIG.storage.tiktok_snapshot_dir)
    REPOSITORY.save_bundle(bundle)
    return LoadDemoResponse(
        account_id=bundle.account.account_id,
        creatives_loaded=len(bundle.creatives),
        hypotheses_loaded=len(bundle.hypotheses),
        tasks_loaded=len(bundle.tasks),
        metrics_loaded=len(bundle.metrics),
        events_loaded=len(bundle.events),
    )


@app.get("/accounts/{account_id}/snapshot", response_model=AccountSnapshotResponse)
def account_snapshot(account_id: str, metric_limit: int = 100) -> AccountSnapshotResponse:
    account = REPOSITORY.get_account(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Аккаунт '{account_id}' не найден")
    creatives = REPOSITORY.list_creatives(account_id)
    metrics = REPOSITORY.list_metrics(account_id, limit=metric_limit)
    return AccountSnapshotResponse(account=account, creatives=creatives, metrics=metrics)


@app.post("/metrics/ingest", response_model=IngestMetricsResponse)
def ingest_metrics(request: IngestMetricsRequest) -> IngestMetricsResponse:
    account = REPOSITORY.get_account(request.account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Аккаунт '{request.account_id}' не найден")

    inserted = 0
    for item in request.items:
        snapshot = MetricSnapshot(
            account_id=request.account_id,
            platform=account.platform,
            creative_id=item.creative_id,
            captured_at=item.captured_at or account.last_sync_at,
            views=item.views,
            likes=item.likes,
            comments=item.comments,
            shares=item.shares,
            saves=item.saves,
            watch_time_seconds=item.watch_time_seconds,
            source=item.source,
            metadata=item.metadata,
        )
        REPOSITORY.add_metric(snapshot)
        inserted += 1

    return IngestMetricsResponse(account_id=request.account_id, inserted=inserted)


@app.post("/plan/generate", response_model=GeneratePlanResponse)
def plan_generate(request: GeneratePlanRequest) -> GeneratePlanResponse:
    account = REPOSITORY.get_account(request.account_id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Аккаунт '{request.account_id}' не найден")
    creatives = REPOSITORY.list_creatives(request.account_id)
    tasks = REPOSITORY.list_tasks(request.account_id)
    metrics = REPOSITORY.list_metrics(request.account_id, limit=CONFIG.thresholds.metric_window_size)

    report = run_analytics(account=account, creatives=creatives, metrics=metrics, thresholds=CONFIG.thresholds)
    planner_cfg = CONFIG.planner if request.max_steps is None else CONFIG.planner.model_copy(update={"max_steps": request.max_steps})
    plan = generate_plan(account=account, report=report, tasks=tasks, planner_config=planner_cfg)
    REPOSITORY.store_plan(plan)
    return GeneratePlanResponse(report=report, plan=plan)


@app.get("/plan/{account_id}/latest")
def plan_latest(account_id: str) -> dict[str, object]:
    plan = REPOSITORY.get_latest_plan(account_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Для аккаунта '{account_id}' план не найден")
    return {"plan": plan.model_dump(mode="json")}
