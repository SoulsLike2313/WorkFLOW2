from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from .config import load_config
from .demo_data import build_demo_bundle
from .repository import SQLiteRepository
from .workspace.demo_seed import seed_workspace_runtime
from .workspace.diagnostics import configure_diagnostics, diag_log
from .workspace.runtime import build_workspace_runtime


VERIFIED = "verified"
PARTIALLY_VERIFIED = "partially verified"
STUB = "stub / not tested"
FAILED = "failed"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat()


@dataclass
class StageResult:
    name: str
    status: str
    started_at: str
    finished_at: str
    duration_seconds: float
    details: dict[str, Any] = field(default_factory=dict)
    command: str | None = None
    stdout_log: str | None = None
    stderr_log: str | None = None


class VerificationRunner:
    def __init__(self) -> None:
        self.config = load_config()
        self.project_root = self.config.storage.project_root
        timestamp = _utc_now().strftime("%Y%m%dT%H%M%SZ")
        self.run_id = f"verify-{timestamp}"
        self.run_dir = self.config.storage.verification_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = self.run_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        configure_diagnostics(self.log_dir, debug=True)

        self.stages: list[StageResult] = []
        self.commands: list[str] = []
        self.module_status: dict[str, str] = {}
        self.seed_summary: dict[str, Any] = {}
        self.db_path = self.run_dir / "verification.db"
        self.started_at = _utc_now()

    def run(self) -> int:
        self._stage_prepare_environment()
        self._stage_sqlite_bootstrap()
        self._stage_workspace_seed()
        self._stage_tests("unit_tests", "app/tests/unit")
        self._stage_tests("integration_tests", "app/tests/integration")
        self._stage_tests("api_smoke_tests", "app/tests/smoke")
        self._stage_service_checks()
        report = self._write_reports()
        overall = FAILED if any(stage.status == FAILED for stage in self.stages) else VERIFIED
        print(f"[verify] overall_status={overall}")
        print(f"[verify] summary_json={report['json_path']}")
        print(f"[verify] summary_md={report['md_path']}")
        return 1 if overall == FAILED else 0

    def _stage_prepare_environment(self) -> None:
        name = "prepare_environment"
        started = _utc_now()
        stage_details: dict[str, Any] = {}
        try:
            venv_active = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
            stage_details["venv_active"] = venv_active
            if not venv_active:
                stage_details["warning"] = "Python venv is not active. Using current interpreter."

            cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.project_root / "requirements.txt")]
            result = self._run_command(name, cmd)
            stage_details["pip_exit_code"] = result["exit_code"]
            stage_details["packages_installed"] = result["exit_code"] == 0

            status = VERIFIED if result["exit_code"] == 0 and venv_active else PARTIALLY_VERIFIED if result["exit_code"] == 0 else FAILED
            finished = _utc_now()
            self.stages.append(
                StageResult(
                    name=name,
                    status=status,
                    started_at=_iso(started),
                    finished_at=_iso(finished),
                    duration_seconds=round((finished - started).total_seconds(), 3),
                    details=stage_details,
                    command=result["command"],
                    stdout_log=result["stdout_log"],
                    stderr_log=result["stderr_log"],
                )
            )
            diag_log("verification_logs", name, payload={"status": status, **stage_details})
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_sqlite_bootstrap(self) -> None:
        name = "sqlite_bootstrap"
        started = _utc_now()
        try:
            repository = SQLiteRepository(self.db_path)
            repository.init_schema()
            bundle = build_demo_bundle(self.config.storage.tiktok_snapshot_dir)
            repository.save_bundle(bundle)
            metrics = repository.list_metrics(bundle.account.account_id, limit=10)
            finished = _utc_now()
            details = {
                "database_path": str(self.db_path),
                "account_id": bundle.account.account_id,
                "creatives": len(bundle.creatives),
                "metrics_loaded": len(metrics),
                "events_loaded": len(bundle.events),
            }
            self.stages.append(
                StageResult(
                    name=name,
                    status=VERIFIED,
                    started_at=_iso(started),
                    finished_at=_iso(finished),
                    duration_seconds=round((finished - started).total_seconds(), 3),
                    details=details,
                )
            )
            diag_log("verification_logs", name, payload={"status": VERIFIED, **details})
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_workspace_seed(self) -> None:
        name = "workspace_seed"
        started = _utc_now()
        try:
            runtime = build_workspace_runtime(
                max_profiles=self.config.workspace.max_profiles,
                analytics_weights=self.config.workspace.analytics_weights.model_dump(),
                log_dir=self.log_dir,
                debug_logs=True,
            )
            self.seed_summary = seed_workspace_runtime(runtime)
            finished = _utc_now()
            details = {
                "profile_id": self.seed_summary.get("profile_id"),
                "content_items": len(self.seed_summary.get("content_ids", [])),
                "metrics_snapshots": len(self.seed_summary.get("metric_snapshot_ids", [])),
                "generation_bundle_id": self.seed_summary.get("generation", {}).get("bundle_id"),
            }
            self.stages.append(
                StageResult(
                    name=name,
                    status=VERIFIED,
                    started_at=_iso(started),
                    finished_at=_iso(finished),
                    duration_seconds=round((finished - started).total_seconds(), 3),
                    details=details,
                )
            )
            diag_log("verification_logs", name, payload={"status": VERIFIED, **details})
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_tests(self, stage_name: str, start_dir: str) -> None:
        started = _utc_now()
        try:
            cmd = [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                start_dir,
                "-t",
                ".",
                "-p",
                "test_*.py",
            ]
            env = {
                "SFCO_DEBUG_LOGS": "1",
                "SFCO_LOGS_DIR": str(self.log_dir),
                "SFCO_VERIFICATION_DIR": str(self.run_dir),
                "SFCO_DATABASE_PATH": str(self.db_path),
            }
            result = self._run_command(stage_name, cmd, env_overrides=env)
            status = VERIFIED if result["exit_code"] == 0 else FAILED
            finished = _utc_now()
            details = {
                "start_dir": start_dir,
                "exit_code": result["exit_code"],
            }
            self.stages.append(
                StageResult(
                    name=stage_name,
                    status=status,
                    started_at=_iso(started),
                    finished_at=_iso(finished),
                    duration_seconds=round((finished - started).total_seconds(), 3),
                    details=details,
                    command=result["command"],
                    stdout_log=result["stdout_log"],
                    stderr_log=result["stderr_log"],
                )
            )
            diag_log("verification_logs", stage_name, payload={"status": status, **details})
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(stage_name, started, exc)

    def _stage_service_checks(self) -> None:
        name = "service_status_classification"
        started = _utc_now()
        try:
            by_name = {item.name: item.status for item in self.stages}
            tests_ok = (
                by_name.get("unit_tests") == VERIFIED
                and by_name.get("integration_tests") == VERIFIED
                and by_name.get("api_smoke_tests") == VERIFIED
            )

            self.module_status = {
                "profiles": VERIFIED if by_name.get("unit_tests") == VERIFIED else FAILED,
                "sessions": VERIFIED if by_name.get("unit_tests") == VERIFIED else FAILED,
                "content": VERIFIED if by_name.get("unit_tests") == VERIFIED else FAILED,
                "metrics_analytics": VERIFIED if tests_ok else PARTIALLY_VERIFIED,
                "ai_subsystem": VERIFIED if tests_ok else PARTIALLY_VERIFIED,
                "audit_observability": VERIFIED if by_name.get("unit_tests") == VERIFIED else PARTIALLY_VERIFIED,
                "api_workspace": VERIFIED if by_name.get("api_smoke_tests") == VERIFIED else FAILED,
                "sqlite_bootstrap": VERIFIED if by_name.get("sqlite_bootstrap") == VERIFIED else FAILED,
                "workspace_sqlite_profile_persistence": STUB,
                "official_auth_connector": STUB,
                "device_remote_provider": PARTIALLY_VERIFIED,
                "video_generator_real_integration": STUB,
            }

            details = {"module_status": self.module_status}
            stage_status = FAILED if any(value == FAILED for value in self.module_status.values()) else VERIFIED
            finished = _utc_now()
            self.stages.append(
                StageResult(
                    name=name,
                    status=stage_status,
                    started_at=_iso(started),
                    finished_at=_iso(finished),
                    duration_seconds=round((finished - started).total_seconds(), 3),
                    details=details,
                )
            )
            diag_log("verification_logs", name, payload={"status": stage_status, **details})
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _run_command(
        self,
        stage_name: str,
        cmd: list[str],
        *,
        env_overrides: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)
        command_text = " ".join(cmd)
        self.commands.append(command_text)

        process = subprocess.run(
            cmd,
            cwd=self.project_root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        stdout_log = self.run_dir / f"{stage_name}.stdout.log"
        stderr_log = self.run_dir / f"{stage_name}.stderr.log"
        stdout_log.write_text(process.stdout or "", encoding="utf-8")
        stderr_log.write_text(process.stderr or "", encoding="utf-8")

        return {
            "exit_code": process.returncode,
            "command": command_text,
            "stdout_log": str(stdout_log),
            "stderr_log": str(stderr_log),
        }

    def _record_stage_exception(self, name: str, started: datetime, exc: Exception) -> None:
        finished = _utc_now()
        details = {
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        self.stages.append(
            StageResult(
                name=name,
                status=FAILED,
                started_at=_iso(started),
                finished_at=_iso(finished),
                duration_seconds=round((finished - started).total_seconds(), 3),
                details=details,
            )
        )
        diag_log("verification_logs", name, level="ERROR", payload={"status": FAILED, **details})

    def _write_reports(self) -> dict[str, str]:
        finished_at = _utc_now()
        logs = sorted(path.name for path in self.log_dir.glob("*.jsonl"))
        copied_logs_dir = self.run_dir / "diagnostics"
        copied_logs_dir.mkdir(exist_ok=True)
        for source in self.log_dir.glob("*.jsonl"):
            shutil.copy2(source, copied_logs_dir / source.name)

        payload = {
            "run_id": self.run_id,
            "started_at": _iso(self.started_at),
            "finished_at": _iso(finished_at),
            "duration_seconds": round((finished_at - self.started_at).total_seconds(), 3),
            "commands": self.commands,
            "stages": [self._stage_to_dict(item) for item in self.stages],
            "module_status": self.module_status,
            "seed_summary": self.seed_summary,
            "artifacts": {
                "run_dir": str(self.run_dir),
                "database_path": str(self.db_path),
                "diagnostics_dir": str(copied_logs_dir),
                "diagnostic_logs": logs,
            },
        }
        json_path = self.run_dir / "verification_summary.json"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        md_path = self.run_dir / "verification_summary.md"
        md_path.write_text(self._render_markdown(payload), encoding="utf-8")
        return {"json_path": str(json_path), "md_path": str(md_path)}

    @staticmethod
    def _stage_to_dict(stage: StageResult) -> dict[str, Any]:
        return {
            "name": stage.name,
            "status": stage.status,
            "started_at": stage.started_at,
            "finished_at": stage.finished_at,
            "duration_seconds": stage.duration_seconds,
            "details": stage.details,
            "command": stage.command,
            "stdout_log": stage.stdout_log,
            "stderr_log": stage.stderr_log,
        }

    @staticmethod
    def _render_markdown(payload: dict[str, Any]) -> str:
        lines = [
            f"# Verification Summary ({payload['run_id']})",
            "",
            f"- Started: `{payload['started_at']}`",
            f"- Finished: `{payload['finished_at']}`",
            f"- Duration (s): `{payload['duration_seconds']}`",
            "",
            "## Module Status",
        ]
        module_status = payload.get("module_status", {})
        for key, value in module_status.items():
            lines.append(f"- `{key}`: **{value}**")

        lines.append("")
        lines.append("## Stages")
        for stage in payload.get("stages", []):
            lines.append(f"- `{stage['name']}`: **{stage['status']}** (`{stage['duration_seconds']}s`)")

        lines.append("")
        lines.append("## Artifacts")
        artifacts = payload.get("artifacts", {})
        for key, value in artifacts.items():
            lines.append(f"- `{key}`: `{value}`")
        return "\n".join(lines) + "\n"


def main() -> int:
    runner = VerificationRunner()
    return runner.run()


if __name__ == "__main__":
    raise SystemExit(main())

