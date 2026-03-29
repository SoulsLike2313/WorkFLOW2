from __future__ import annotations

import argparse
import json
import os
import re
import socket
import shutil
import subprocess
import sys
import traceback
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import httpx

from .config import load_config
from .demo_data import build_demo_bundle
from .readiness import ReadinessService
from .repository import SQLiteRepository
from .startup_manager import StartupManager
from .update import PatchBundle, UpdateManifest, UpdateService
from .version import APP_VERSION
from .workspace.demo_seed import seed_workspace_runtime
from .workspace.diagnostics import configure_diagnostics, diag_log
from .workspace.runtime import build_workspace_runtime


VERIFIED = "verified"
PARTIALLY_VERIFIED = "partially verified"
STUB = "stub / not tested"
FAILED = "failed"

GATE_PASS = "PASS"
GATE_WARN = "PASS_WITH_WARNINGS"
GATE_FAIL = "FAIL"

RUNTIME_DEPENDENCY_PIP_PACKAGES = {
    "fastapi": "fastapi>=0.115.0",
    "uvicorn": "uvicorn[standard]>=0.30.0",
    "pydantic": "pydantic>=2.8.0",
    "httpx": "httpx>=0.27.0",
}


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
    def __init__(self, *, install_deps: bool = True) -> None:
        self.install_deps = install_deps
        self.config = load_config()
        self.project_root = self.config.storage.project_root
        timestamp = _utc_now().strftime("%Y%m%dT%H%M%SZ")
        self.run_id = f"verify-{timestamp}"
        self.run_dir = self.config.storage.verification_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = self.run_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.test_artifacts_dir = self.run_dir / "test_artifacts"
        self.test_artifacts_dir.mkdir(parents=True, exist_ok=True)
        configure_diagnostics(self.log_dir, debug=True)

        self.stages: list[StageResult] = []
        self.commands: list[str] = []
        self.module_status: dict[str, str] = {}
        self.seed_summary: dict[str, Any] = {}
        self.started_at = _utc_now()
        self.db_path = self.run_dir / "verification_core.db"
        self.workspace_state_path = self.run_dir / "verification_workspace_state.db"
        self.ui_validation_max_age_minutes = 360

    @staticmethod
    def _is_local_port_available(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
            except OSError:
                return False
        return True

    @staticmethod
    def _allocate_ephemeral_local_port(host: str) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, 0))
            return int(sock.getsockname()[1])

    def _resolve_backend_port(self, *, host: str, preferred_port: int) -> tuple[int, bool]:
        if self._is_local_port_available(host, preferred_port):
            return preferred_port, False
        return self._allocate_ephemeral_local_port(host), True

    def run(self) -> int:
        self._stage_prepare_environment()
        self._stage_runtime_dependency_contract_bootstrap()
        self._stage_config_validation()
        self._stage_sqlite_bootstrap()
        self._stage_workspace_seed()
        self._stage_unittest_suite("unit_tests", "app/tests/unit")
        self._stage_unittest_suite("integration_tests", "app/tests/integration")
        self._stage_unittest_suite("api_smoke_tests", "app/tests/smoke")
        self._stage_pytest_suite("pytest_suite", "app/tests_pytest")
        self._stage_runtime_readiness()
        self._stage_ai_contract_checks()
        self._stage_ui_backend_connectivity()
        self._stage_update_patch_checks()
        self._stage_ui_validation_truth_alignment()
        self._stage_service_classification()

        report = self._write_reports()
        gate_status = report["gate_status"]
        print(f"[verify] gate_status={gate_status}")
        print(f"[verify] summary_json={report['json_path']}")
        print(f"[verify] summary_md={report['md_path']}")
        return 0 if gate_status == GATE_PASS else 1

    @staticmethod
    def _missing_runtime_dependencies() -> list[str]:
        missing: list[str] = []
        for module in RUNTIME_DEPENDENCY_PIP_PACKAGES:
            if find_spec(module) is None:
                missing.append(module)
        return sorted(set(missing))

    @staticmethod
    def _pip_specs_for_modules(modules: list[str]) -> list[str]:
        specs: list[str] = []
        for module in modules:
            spec = RUNTIME_DEPENDENCY_PIP_PACKAGES.get(module)
            if spec:
                specs.append(spec)
        return specs

    def _stage_prepare_environment(self) -> None:
        name = "prepare_environment"
        started = _utc_now()
        try:
            venv_active = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
            details: dict[str, Any] = {
                "venv_active": venv_active,
                "python_executable": sys.executable,
            }
            if self.install_deps:
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.project_root / "requirements.txt")]
                result = self._run_command(name, cmd)
                details["pip_exit_code"] = result["exit_code"]
                status = VERIFIED if result["exit_code"] == 0 else FAILED
                self._add_stage(
                    name=name,
                    status=status,
                    started=started,
                    details=details,
                    command=result["command"],
                    stdout_log=result["stdout_log"],
                    stderr_log=result["stderr_log"],
                )
            else:
                details["skipped"] = True
                self._add_stage(name=name, status=PARTIALLY_VERIFIED, started=started, details=details)
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_config_validation(self) -> None:
        name = "config_validation"
        started = _utc_now()
        try:
            required_dirs = [
                self.config.storage.output_dir,
                self.config.storage.logs_dir,
                self.config.storage.verification_dir,
                self.config.storage.patch_dir,
            ]
            missing = [str(path) for path in required_dirs if not path.exists()]
            details = {
                "api_host": self.config.api_host,
                "api_port": self.config.api_port,
                "missing_dirs": missing,
            }
            status = VERIFIED if not missing else FAILED
            self._add_stage(name=name, status=status, started=started, details=details)
            diag_log("verification_logs", name, payload={"status": status, **details}, level="INFO" if status == VERIFIED else "ERROR")
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
            metrics = repository.list_metrics(bundle.account.account_id, limit=20)
            details = {
                "database_path": str(self.db_path),
                "account_id": bundle.account.account_id,
                "creatives": len(bundle.creatives),
                "metrics_loaded": len(metrics),
                "events_loaded": len(bundle.events),
            }
            self._add_stage(name=name, status=VERIFIED, started=started, details=details)
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
                persistence_path=self.workspace_state_path,
            )
            self.seed_summary = seed_workspace_runtime(runtime)
            details = {
                "workspace_state_path": str(self.workspace_state_path),
                "profile_id": self.seed_summary.get("profile_id"),
                "content_items": len(self.seed_summary.get("content_ids", [])),
                "metrics_snapshots": len(self.seed_summary.get("metric_snapshot_ids", [])),
            }
            self._add_stage(name=name, status=VERIFIED, started=started, details=details)
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_unittest_suite(self, stage_name: str, start_dir: str) -> None:
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
            result = self._run_command(stage_name, cmd, env_overrides=self._verify_env())
            dependency_missing = self._extract_dependency_gaps(
                stdout_text=result.get("stdout_text", ""),
                stderr_text=result.get("stderr_text", ""),
            )
            skipped_count = self._extract_unittest_skips(
                stdout_text=result.get("stdout_text", ""),
                stderr_text=result.get("stderr_text", ""),
            )
            details = {
                "suite": "unittest",
                "start_dir": start_dir,
                "exit_code": result["exit_code"],
                "dependency_missing": dependency_missing,
                "skipped_count": skipped_count,
            }
            if result["exit_code"] == 0 and not dependency_missing and skipped_count == 0:
                status = VERIFIED
            elif dependency_missing:
                status = PARTIALLY_VERIFIED
                details["classification"] = "dependency_gap_detected"
            elif result["exit_code"] == 0 and skipped_count > 0:
                status = PARTIALLY_VERIFIED
                details["classification"] = "tests_skipped"
            else:
                status = FAILED
            self._add_stage(
                name=stage_name,
                status=status,
                started=started,
                details=details,
                command=result["command"],
                stdout_log=result["stdout_log"],
                stderr_log=result["stderr_log"],
            )
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(stage_name, started, exc)

    def _stage_pytest_suite(self, stage_name: str, suite_dir: str) -> None:
        started = _utc_now()
        try:
            cmd = [sys.executable, "-m", "pytest", suite_dir, "-q"]
            result = self._run_command(stage_name, cmd, env_overrides=self._verify_env())
            dependency_missing = self._extract_dependency_gaps(
                stdout_text=result.get("stdout_text", ""),
                stderr_text=result.get("stderr_text", ""),
            )
            skipped_count = self._extract_pytest_skips(
                stdout_text=result.get("stdout_text", ""),
                stderr_text=result.get("stderr_text", ""),
            )
            details = {
                "suite": "pytest",
                "suite_dir": suite_dir,
                "exit_code": result["exit_code"],
                "dependency_missing": dependency_missing,
                "skipped_count": skipped_count,
            }
            if result["exit_code"] == 0 and not dependency_missing and skipped_count == 0:
                status = VERIFIED
            elif dependency_missing:
                status = PARTIALLY_VERIFIED
                details["classification"] = "dependency_gap_detected"
            elif result["exit_code"] == 0 and skipped_count > 0:
                status = PARTIALLY_VERIFIED
                details["classification"] = "tests_skipped"
            else:
                status = FAILED
            self._add_stage(
                name=stage_name,
                status=status,
                started=started,
                details=details,
                command=result["command"],
                stdout_log=result["stdout_log"],
                stderr_log=result["stderr_log"],
            )
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(stage_name, started, exc)

    def _stage_runtime_readiness(self) -> None:
        name = "runtime_readiness_checks"
        started = _utc_now()
        manager = StartupManager()
        bind_host = "127.0.0.1"
        preferred_port = 8123
        selected_port, fallback_used = self._resolve_backend_port(host=bind_host, preferred_port=preferred_port)
        manager.config.api_host = bind_host
        manager.config.api_port = selected_port
        manager.config.storage.workspace_state_path = self.workspace_state_path
        try:
            context = manager.initialize_local_runtime()
            manager.start_internal_backend(host=bind_host, port=selected_port)
            probe = manager.probe_backend_readiness(timeout_seconds=15.0, host=bind_host, port=selected_port)
            backend_ready = probe.ready
            status = VERIFIED if context.readiness.get("overall_ready") and probe.ready else FAILED
            details = {
                "local_readiness": context.readiness,
                "backend_ready": backend_ready,
                "api_host": bind_host,
                "api_port": selected_port,
                "preferred_port": preferred_port,
                "port_fallback_used": fallback_used,
                "proxy_bypass_enabled": True,
                "failure_reason": probe.failure_reason,
                "recovery_signal": probe.recovery_signal,
                "probe_endpoint_statuses": probe.endpoint_statuses,
                "probe_attempts_count": len(probe.attempts),
                "probe_duration_seconds": probe.duration_seconds,
            }
            self._add_stage(name=name, status=status, started=started, details=details)
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)
        finally:
            manager.stop_internal_backend()

    def _stage_ai_contract_checks(self) -> None:
        name = "ai_contract_checks"
        started = _utc_now()
        try:
            runtime = build_workspace_runtime(
                max_profiles=5,
                log_dir=self.log_dir,
                debug_logs=True,
                persistence_path=self.workspace_state_path,
            )
            capabilities = {
                "perception": runtime.perception_provider.get_capabilities(),
                "reasoning": runtime.reasoning_provider.get_capabilities(),
                "creative": runtime.creative_provider.get_capabilities(),
                "generation": runtime.generation_adapter.get_capabilities(),
                "learning_scorer": runtime.learning_scorer.get_capabilities(),
            }
            status = VERIFIED if all(value for value in capabilities.values()) else FAILED
            self._add_stage(name=name, status=status, started=started, details={"capabilities": capabilities})
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_ui_backend_connectivity(self) -> None:
        name = "ui_backend_connectivity_checks"
        started = _utc_now()
        manager = StartupManager()
        bind_host = "127.0.0.1"
        preferred_port = 8124
        selected_port, fallback_used = self._resolve_backend_port(host=bind_host, preferred_port=preferred_port)
        manager.config.api_host = bind_host
        manager.config.api_port = selected_port
        manager.config.storage.workspace_state_path = self.workspace_state_path
        try:
            manager.initialize_local_runtime()
            manager.start_internal_backend(host=bind_host, port=selected_port)
            probe = manager.probe_backend_readiness(timeout_seconds=15.0, host=bind_host, port=selected_port)
            details: dict[str, Any] = {
                "backend_ready": probe.ready,
                "api_host": bind_host,
                "api_port": selected_port,
                "preferred_port": preferred_port,
                "port_fallback_used": fallback_used,
                "proxy_bypass_enabled": True,
                "failure_reason": probe.failure_reason,
                "recovery_signal": probe.recovery_signal,
                "probe_endpoint_statuses": probe.endpoint_statuses,
                "probe_attempts_count": len(probe.attempts),
                "probe_duration_seconds": probe.duration_seconds,
            }
            if probe.ready:
                with httpx.Client(timeout=4.0, trust_env=False) as client:
                    base_url = f"http://{bind_host}:{selected_port}"
                    r1 = client.get(f"{base_url}/workspace/health")
                    r2 = client.get(f"{base_url}/workspace/profiles")
                    r3 = client.get(f"{base_url}/workspace/readiness")
                    r4 = client.get(f"{base_url}/workspace/prompt-lineage")
                details["statuses"] = {
                    "workspace_health": r1.status_code,
                    "workspace_profiles": r2.status_code,
                    "workspace_readiness": r3.status_code,
                    "workspace_prompt_lineage": r4.status_code,
                }
                status = (
                    VERIFIED
                    if r1.status_code == 200
                    and r2.status_code == 200
                    and r3.status_code == 200
                    and r4.status_code == 200
                    else FAILED
                )
            else:
                status = FAILED
            self._add_stage(name=name, status=status, started=started, details=details)
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)
        finally:
            manager.stop_internal_backend()

    def _stage_update_patch_checks(self) -> None:
        name = "update_patch_checks"
        started = _utc_now()
        try:
            update_service = UpdateService(self.config)

            manifest = UpdateManifest(
                current_version=APP_VERSION,
                available_version=f"{APP_VERSION}-patch1",
                patch_notes=["verification manifest"],
                compatibility_info={"marker": "v1"},
            )
            manifest_path = self.run_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False), encoding="utf-8")
            check_result = update_service.check_for_update(manifest_path)

            patch_zip = self.run_dir / "patch_bundle.zip"
            with zipfile.ZipFile(patch_zip, "w") as archive:
                archive.writestr("patch.txt", "verification patch bundle")
            bundle = PatchBundle(bundle_path=patch_zip, target_version=manifest.available_version)
            patch_result = update_service.apply_local_patch(bundle)
            patch_result_payload = patch_result.model_dump(mode="json")
            update_audit = [record.model_dump(mode="json") for record in update_service.audit]

            details = {
                "check_result": check_result,
                "patch_result": patch_result_payload,
                "audit_records_count": len(update_audit),
                "audit_records": update_audit,
            }
            post_status = patch_result_payload.get("post_update_verification", {}).get("status")
            patch_ok = (
                patch_result_payload.get("status") == "applied"
                and post_status in {GATE_PASS, GATE_WARN}
            )
            status = VERIFIED if check_result.get("is_compatible") and patch_ok else FAILED
            self._add_stage(name=name, status=status, started=started, details=details)
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_runtime_dependency_contract_bootstrap(self) -> None:
        name = "runtime_dependency_contract_bootstrap"
        started = _utc_now()
        try:
            missing_before = self._missing_runtime_dependencies()
            details: dict[str, Any] = {
                "required_modules": sorted(RUNTIME_DEPENDENCY_PIP_PACKAGES.keys()),
                "missing_before": missing_before,
            }
            if not missing_before:
                self._add_stage(name=name, status=VERIFIED, started=started, details=details)
                return

            pip_specs = self._pip_specs_for_modules(missing_before)
            details["attempted_install_specs"] = pip_specs
            if not pip_specs:
                details["classification"] = "dependency_contract_missing_with_no_spec_mapping"
                self._add_stage(name=name, status=PARTIALLY_VERIFIED, started=started, details=details)
                return

            cmd = [sys.executable, "-m", "pip", "install", *pip_specs]
            result = self._run_command(name, cmd, env_overrides=self._verify_env())
            missing_after = self._missing_runtime_dependencies()
            details.update(
                {
                    "install_exit_code": result["exit_code"],
                    "missing_after": missing_after,
                    "install_attempted": True,
                }
            )
            if not missing_after:
                status = VERIFIED
            else:
                status = PARTIALLY_VERIFIED
                details["classification"] = "dependency_contract_still_open"
            self._add_stage(
                name=name,
                status=status,
                started=started,
                details=details,
                command=result["command"],
                stdout_log=result["stdout_log"],
                stderr_log=result["stderr_log"],
            )
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_ui_validation_truth_alignment(self) -> None:
        name = "ui_validation_truth_alignment"
        started = _utc_now()
        try:
            cmd = [sys.executable, "scripts/ui_validate.py", "--api-base-url", "http://127.0.0.1:9"]
            result = self._run_command(name, cmd, env_overrides=self._verify_env())

            summary_path = self.project_root / "ui_validation_summary.json"
            latest_run_path = self.project_root / "runtime" / "ui_validation" / "latest_run.json"
            details: dict[str, Any] = {
                "summary_path": str(summary_path),
                "latest_run_path": str(latest_run_path),
                "ui_validate_exit_code": result["exit_code"],
                "stale_threshold_minutes": self.ui_validation_max_age_minutes,
            }

            if not summary_path.exists():
                details["error"] = "ui_validation_summary_missing"
                self._add_stage(
                    name=name,
                    status=FAILED,
                    started=started,
                    details=details,
                    command=result["command"],
                    stdout_log=result["stdout_log"],
                    stderr_log=result["stderr_log"],
                )
                return

            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            validation_status = str(summary.get("overall_status", "FAIL"))
            run_id = str(summary.get("run_id", "unknown"))
            finished_at_raw = str(summary.get("finished_at", ""))
            stale = True
            age_minutes: float | None = None
            if finished_at_raw:
                try:
                    finished_at = datetime.fromisoformat(finished_at_raw.replace("Z", "+00:00"))
                    age_minutes = round((_utc_now() - finished_at).total_seconds() / 60.0, 2)
                    stale = bool(age_minutes > self.ui_validation_max_age_minutes)
                except Exception:
                    stale = True

            artifacts = summary.get("artifacts", {}) if isinstance(summary.get("artifacts"), dict) else {}
            manifest_rel = str(artifacts.get("root_screenshots_manifest", "")).strip()
            trace_rel = str(artifacts.get("root_walkthrough_trace", "")).strip()
            manifest_path = (self.project_root / manifest_rel).resolve() if manifest_rel else self.project_root / "ui_screenshots_manifest.json"
            trace_path = (self.project_root / trace_rel).resolve() if trace_rel else self.project_root / "ui_walkthrough_trace.json"
            latest_run_id = "unknown"
            latest_run_status = "UNKNOWN"
            latest_run_matches_root = False
            if latest_run_path.exists():
                try:
                    latest_payload = json.loads(latest_run_path.read_text(encoding="utf-8"))
                    latest_run_id = str(latest_payload.get("run_id", "unknown"))
                    latest_run_status = str(latest_payload.get("status", "UNKNOWN"))
                    latest_run_matches_root = latest_run_id == run_id
                except Exception:
                    latest_run_id = "parse_error"
                    latest_run_status = "UNKNOWN"
                    latest_run_matches_root = False
            expected_screens = {
                "dashboard",
                "profiles",
                "sessions",
                "content",
                "analytics",
                "ai_studio",
                "audit",
                "updates",
                "settings",
            }
            covered_screens: set[str] = set()
            screenshot_count = 0
            trace_steps_count = 0
            trace_pass_count = 0
            trace_warn_count = 0
            trace_fail_count = 0

            if manifest_path.exists():
                try:
                    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                    screenshots = manifest_payload.get("screenshots", [])
                    if isinstance(screenshots, list):
                        screenshot_count = len(screenshots)
                        for item in screenshots:
                            if not isinstance(item, dict):
                                continue
                            screen = str(item.get("screen_name") or item.get("page") or "").strip()
                            if screen:
                                covered_screens.add(screen)
                except Exception:
                    screenshot_count = 0
                    covered_screens = set()

            if trace_path.exists():
                try:
                    trace_payload = json.loads(trace_path.read_text(encoding="utf-8"))
                    steps = trace_payload.get("steps", [])
                    if isinstance(steps, list):
                        trace_steps_count = len(steps)
                        for step in steps:
                            result_value = str((step or {}).get("result", "")).strip().lower()
                            if result_value == "pass":
                                trace_pass_count += 1
                            elif result_value in {"warning", "warn"}:
                                trace_warn_count += 1
                            elif result_value in {"fail", "failed", "error"}:
                                trace_fail_count += 1
                except Exception:
                    trace_steps_count = 0

            missing_screens = sorted(expected_screens - covered_screens)
            failed_checks_raw = summary.get("failed_checks", []) if isinstance(summary.get("failed_checks"), list) else []
            warned_checks_raw = summary.get("warned_checks", []) if isinstance(summary.get("warned_checks"), list) else []
            failed_checks = [str(item) for item in failed_checks_raw]
            warned_checks = [str(item) for item in warned_checks_raw]
            missing_loaded_states = sorted(
                [
                    item.split(":", 1)[1]
                    for item in failed_checks
                    if item.startswith("missing_loaded_state:")
                ]
            )
            critical_walkthrough_misses = sorted(
                [
                    item.split(":", 1)[1]
                    for item in failed_checks
                    if item.startswith("walkthrough_action_missing:")
                ]
            )
            state_observation_gaps = sorted(
                [
                    item.split(":", 1)[1]
                    for item in warned_checks
                    if item.startswith("state_not_observed:")
                ]
            )
            required_release_shape_states = {
                "dashboard:initial_state",
                "dashboard:loaded_state",
                "profiles:no_selection_state",
                "sessions:no_selection_state",
                "content:no_selection_state",
            }
            release_shape_payload = summary.get("release_shape_truth", {})
            payload_missing_release_shape = []
            if isinstance(release_shape_payload, dict):
                payload_missing_release_shape = [str(item) for item in release_shape_payload.get("missing_required_states", [])]
            missing_release_shape_states = sorted(
                set(payload_missing_release_shape)
                or {item for item in state_observation_gaps if item in required_release_shape_states}
            )
            behavior_depth_ready = (
                trace_steps_count >= 120
                and screenshot_count >= 180
                and not missing_screens
                and trace_fail_count == 0
                and not missing_loaded_states
                and not critical_walkthrough_misses
            )
            verification_ui_alignment_ready = (
                latest_run_matches_root
                and latest_run_status == "PASS"
                and not missing_loaded_states
                and not critical_walkthrough_misses
                and not missing_release_shape_states
            )
            release_shape_truth_ready = bool(
                summary.get("manual_testing_allowed", False)
                and validation_status == "PASS"
                and not stale
                and behavior_depth_ready
                and verification_ui_alignment_ready
            )

            details.update(
                {
                    "run_id": run_id,
                    "latest_run_id": latest_run_id,
                    "latest_run_status": latest_run_status,
                    "latest_run_matches_root": latest_run_matches_root,
                    "ui_validation_status": validation_status,
                    "manual_testing_allowed": bool(summary.get("manual_testing_allowed", False)),
                    "stale": stale,
                    "age_minutes": age_minutes,
                    "failed_checks_count": len(summary.get("failed_checks", []) if isinstance(summary.get("failed_checks"), list) else []),
                    "warned_checks_count": len(summary.get("warned_checks", []) if isinstance(summary.get("warned_checks"), list) else []),
                    "behavior_verification_depth": {
                        "trace_steps_count": trace_steps_count,
                        "trace_pass_count": trace_pass_count,
                        "trace_warn_count": trace_warn_count,
                        "trace_fail_count": trace_fail_count,
                        "screenshot_count": screenshot_count,
                        "covered_screens": sorted(covered_screens),
                        "missing_screens": missing_screens,
                        "required_release_shape_states": sorted(required_release_shape_states),
                        "missing_release_shape_states": missing_release_shape_states,
                        "ready": behavior_depth_ready,
                    },
                    "false_stability_cleanup": {
                        "missing_loaded_states": missing_loaded_states,
                        "critical_walkthrough_action_misses": critical_walkthrough_misses,
                        "state_observation_gaps": state_observation_gaps,
                        "latest_run_matches_root": latest_run_matches_root,
                        "verification_ui_alignment_ready": verification_ui_alignment_ready,
                        "status": (
                            "PROVEN_STRENGTHENED"
                            if verification_ui_alignment_ready
                            else "PROVEN_MINIMUM"
                            if not missing_loaded_states and not critical_walkthrough_misses and latest_run_matches_root
                            else "OPEN_GAPS"
                        ),
                    },
                    "release_shape_truth_cleanup": {
                        "manifest_path": str(manifest_path),
                        "trace_path": str(trace_path),
                        "required_release_shape_states": sorted(required_release_shape_states),
                        "missing_release_shape_states": missing_release_shape_states,
                        "latest_run_id": latest_run_id,
                        "latest_run_matches_root": latest_run_matches_root,
                        "ready": release_shape_truth_ready,
                        "claim_boundary": "release-grade-claim-forbidden-until-wave-1-and-gate-d",
                        "open_actions": [
                            "behavior_depth_ready_required",
                            "release_shape_required_states_observed",
                            "latest_run_must_match_root_summary",
                            "owner_gate_d_required_for_release_claim",
                        ],
                    },
                }
            )

            if result["exit_code"] not in {0, 1, 2}:
                status = FAILED
            elif validation_status == "PASS" and not stale and release_shape_truth_ready:
                status = VERIFIED
            elif validation_status == "PASS_WITH_WARNINGS":
                status = PARTIALLY_VERIFIED
            elif validation_status == "PASS" and stale:
                status = PARTIALLY_VERIFIED
            else:
                status = FAILED

            self._add_stage(
                name=name,
                status=status,
                started=started,
                details=details,
                command=result["command"],
                stdout_log=result["stdout_log"],
                stderr_log=result["stderr_log"],
            )
        except Exception as exc:  # pragma: no cover
            self._record_stage_exception(name, started, exc)

    def _stage_service_classification(self) -> None:
        name = "service_status_classification"
        started = _utc_now()
        by_name = {item.name: item.status for item in self.stages}
        tests_core_ok = (
            by_name.get("unit_tests") == VERIFIED
            and by_name.get("integration_tests") == VERIFIED
        )
        api_smoke_status = by_name.get("api_smoke_tests", FAILED)
        pytest_suite_status = by_name.get("pytest_suite", FAILED)
        tests_all_verified = tests_core_ok and api_smoke_status == VERIFIED and pytest_suite_status == VERIFIED
        ui_truth_status = by_name.get("ui_validation_truth_alignment", FAILED)
        api_workspace_status = (
            VERIFIED
            if api_smoke_status == VERIFIED and pytest_suite_status == VERIFIED
            else PARTIALLY_VERIFIED
            if api_smoke_status in {PARTIALLY_VERIFIED, VERIFIED}
            and pytest_suite_status in {PARTIALLY_VERIFIED, VERIFIED}
            else FAILED
        )
        ui_connectivity_stage = self._stage_by_name("ui_backend_connectivity_checks")
        ui_statuses = ui_connectivity_stage.details.get("statuses", {}) if ui_connectivity_stage else {}
        prompt_lineage_verified = ui_statuses.get("workspace_prompt_lineage") == 200
        self.module_status = {
            "profiles": VERIFIED if tests_core_ok else PARTIALLY_VERIFIED,
            "sessions": VERIFIED if tests_core_ok else PARTIALLY_VERIFIED,
            "content": VERIFIED if tests_core_ok else PARTIALLY_VERIFIED,
            "metrics_analytics": VERIFIED if tests_core_ok else PARTIALLY_VERIFIED,
            "ai_subsystem": VERIFIED if by_name.get("ai_contract_checks") == VERIFIED and tests_core_ok else PARTIALLY_VERIFIED,
            "audit_observability": VERIFIED if tests_core_ok else PARTIALLY_VERIFIED,
            "api_workspace": api_workspace_status,
            "runtime_readiness": VERIFIED if by_name.get("runtime_readiness_checks") == VERIFIED else FAILED,
            "ui_backend_integration": VERIFIED if by_name.get("ui_backend_connectivity_checks") == VERIFIED else FAILED,
            "ui_validation_truth_lane": ui_truth_status,
            "prompt_lineage_observability": VERIFIED if prompt_lineage_verified else FAILED,
            "update_patch_flow": VERIFIED if by_name.get("update_patch_checks") == VERIFIED and tests_all_verified else PARTIALLY_VERIFIED,
            "official_auth_connector": STUB,
            "video_generator_real_integration": STUB,
        }
        stage_status = FAILED if any(value == FAILED for value in self.module_status.values()) else VERIFIED
        self._add_stage(
            name=name,
            status=stage_status,
            started=started,
            details={
                "module_status": self.module_status,
                "prompt_lineage_observability": {
                    "verified": prompt_lineage_verified,
                    "status_code": ui_statuses.get("workspace_prompt_lineage"),
                },
            },
        )

    def _verify_env(self) -> dict[str, str]:
        return {
            "SFCO_DEBUG_LOGS": "1",
            "SFCO_LOGS_DIR": str(self.log_dir),
            "SFCO_VERIFICATION_DIR": str(self.run_dir),
            "SFCO_DATABASE_PATH": str(self.db_path),
            "SFCO_WORKSPACE_STATE_PATH": str(self.workspace_state_path),
            "SFCO_PATCH_DIR": str(self.run_dir / "patches"),
        }

    def _extract_dependency_gaps(self, *, stdout_text: str, stderr_text: str) -> list[str]:
        payload = f"{stdout_text}\n{stderr_text}"
        missing: list[str] = []
        for module in re.findall(r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]", payload):
            item = str(module).strip()
            if item:
                missing.append(item)
        for module in re.findall(r"ImportError:\s+No module named ['\"]([^'\"]+)['\"]", payload):
            item = str(module).strip()
            if item:
                missing.append(item)
        return sorted(set(missing))

    def _extract_unittest_skips(self, *, stdout_text: str, stderr_text: str) -> int:
        payload = f"{stdout_text}\n{stderr_text}"
        match = re.search(r"skipped=(\d+)", payload)
        if not match:
            return 0
        try:
            return int(match.group(1))
        except Exception:
            return 0

    def _extract_pytest_skips(self, *, stdout_text: str, stderr_text: str) -> int:
        payload = f"{stdout_text}\n{stderr_text}"
        total = 0
        for item in re.findall(r"(\d+)\s+skipped", payload):
            try:
                total += int(item)
            except Exception:
                continue
        return total

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
        stdout_log = self.test_artifacts_dir / f"{stage_name}.stdout.log"
        stderr_log = self.test_artifacts_dir / f"{stage_name}.stderr.log"
        stdout_log.write_text(process.stdout or "", encoding="utf-8")
        stderr_log.write_text(process.stderr or "", encoding="utf-8")
        return {
            "exit_code": process.returncode,
            "command": command_text,
            "stdout_log": str(stdout_log),
            "stderr_log": str(stderr_log),
            "stdout_text": process.stdout or "",
            "stderr_text": process.stderr or "",
        }

    def _add_stage(
        self,
        *,
        name: str,
        status: str,
        started: datetime,
        details: dict[str, Any],
        command: str | None = None,
        stdout_log: str | None = None,
        stderr_log: str | None = None,
    ) -> None:
        finished = _utc_now()
        self.stages.append(
            StageResult(
                name=name,
                status=status,
                started_at=_iso(started),
                finished_at=_iso(finished),
                duration_seconds=round((finished - started).total_seconds(), 3),
                details=details,
                command=command,
                stdout_log=stdout_log,
                stderr_log=stderr_log,
            )
        )
        diag_log("verification_logs", name, payload={"status": status, **details}, level="INFO" if status != FAILED else "ERROR")

    def _record_stage_exception(self, name: str, started: datetime, exc: Exception) -> None:
        self._add_stage(
            name=name,
            status=FAILED,
            started=started,
            details={"error": str(exc), "traceback": traceback.format_exc()},
        )

    def _gate_status(self) -> str:
        if any(stage.status == FAILED for stage in self.stages):
            return GATE_FAIL
        if any(value == FAILED for value in self.module_status.values()):
            return GATE_FAIL

        key_modules = {
            "profiles",
            "sessions",
            "content",
            "metrics_analytics",
            "ai_subsystem",
            "audit_observability",
            "api_workspace",
            "runtime_readiness",
            "ui_backend_integration",
            "ui_validation_truth_lane",
            "update_patch_flow",
        }
        for module in key_modules:
            if self.module_status.get(module) != VERIFIED:
                return GATE_FAIL

        allowed_stub_modules = {"official_auth_connector", "video_generator_real_integration"}
        warning_modules = [
            module
            for module, status in self.module_status.items()
            if status in {PARTIALLY_VERIFIED, STUB} and module not in allowed_stub_modules
        ]
        if warning_modules:
            return GATE_WARN
        return GATE_PASS

    def _stage_by_name(self, name: str) -> StageResult | None:
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    def _write_json_artifact(self, filename: str, payload: dict[str, Any]) -> Path:
        target = self.run_dir / filename
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def _build_readiness_summary(self, *, gate_status: str) -> dict[str, Any]:
        runtime_stage = self._stage_by_name("runtime_readiness_checks")
        ui_stage = self._stage_by_name("ui_backend_connectivity_checks")
        ui_validation_stage = self._stage_by_name("ui_validation_truth_alignment")
        update_stage = self._stage_by_name("update_patch_checks")

        startup_readiness = (runtime_stage.details.get("local_readiness", {}) if runtime_stage else {})
        startup_items = startup_readiness.get("items", []) if isinstance(startup_readiness, dict) else []
        startup_all_ready = bool(startup_readiness.get("overall_ready")) if isinstance(startup_readiness, dict) else False
        backend_ready = bool(runtime_stage.details.get("backend_ready")) if runtime_stage else False
        ui_statuses = ui_stage.details.get("statuses", {}) if ui_stage else {}
        ui_validation = ui_validation_stage.details if ui_validation_stage else {}

        patch_result = update_stage.details.get("patch_result", {}) if update_stage else {}
        post_update = patch_result.get("post_update_verification", {}) if isinstance(patch_result, dict) else {}
        post_update_status = post_update.get("status", GATE_FAIL)
        post_update_readiness = post_update.get("readiness", {})

        if not startup_all_ready or not backend_ready:
            status = GATE_FAIL
        elif post_update_status == GATE_FAIL:
            status = GATE_FAIL
        elif post_update_status == GATE_WARN:
            status = GATE_WARN
        elif any(not bool(item.get("ready")) for item in startup_items if isinstance(item, dict)):
            status = GATE_WARN
        else:
            status = GATE_PASS

        return {
            "run_id": self.run_id,
            "status": status,
            "gate_status": gate_status,
            "startup_readiness": startup_readiness,
            "backend_ready": backend_ready,
            "ui_backend_statuses": ui_statuses,
            "ui_validation_truth_alignment": ui_validation,
            "post_update_status": post_update_status,
            "post_update_readiness": post_update_readiness,
            "usage_points": [
                "app.startup_manager.StartupManager.initialize_local_runtime",
                "app.verify.VerificationRunner._stage_runtime_readiness",
                "app.update.services.UpdateService.post_update_verification",
            ],
        }

    def _build_patch_application_summary(self, *, gate_status: str) -> dict[str, Any]:
        update_stage = self._stage_by_name("update_patch_checks")
        details = update_stage.details if update_stage else {}
        check_result = details.get("check_result", {}) if isinstance(details, dict) else {}
        patch_result = details.get("patch_result", {}) if isinstance(details, dict) else {}

        patch_status = patch_result.get("status", "failed") if isinstance(patch_result, dict) else "failed"
        post_status = (
            patch_result.get("post_update_verification", {}).get("status", GATE_FAIL)
            if isinstance(patch_result, dict)
            else GATE_FAIL
        )
        if patch_status == "applied" and post_status == GATE_PASS:
            status = GATE_PASS
        elif patch_status == "applied" and post_status == GATE_WARN:
            status = GATE_WARN
        else:
            status = GATE_FAIL

        return {
            "run_id": self.run_id,
            "status": status,
            "gate_status": gate_status,
            "manifest_check": check_result,
            "patch_result": patch_result,
            "rollback_applied": patch_result.get("rollback_applied", False) if isinstance(patch_result, dict) else False,
        }

    def _build_update_audit_summary(self, *, gate_status: str) -> dict[str, Any]:
        update_stage = self._stage_by_name("update_patch_checks")
        details = update_stage.details if update_stage else {}
        records = details.get("audit_records", []) if isinstance(details, dict) else []
        if not isinstance(records, list):
            records = []

        expected_actions = ["load_manifest", "check_for_update", "post_update_verification", "apply_patch"]
        present_actions = sorted({str(item.get("action")) for item in records if isinstance(item, dict) and item.get("action")})
        missing_actions = [action for action in expected_actions if action not in present_actions]

        by_result: dict[str, int] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            result = str(record.get("result", "unknown"))
            by_result[result] = by_result.get(result, 0) + 1

        if not records:
            status = GATE_FAIL
        elif missing_actions:
            status = GATE_WARN
        else:
            status = GATE_PASS

        return {
            "run_id": self.run_id,
            "status": status,
            "gate_status": gate_status,
            "record_count": len(records),
            "expected_actions": expected_actions,
            "present_actions": present_actions,
            "missing_actions": missing_actions,
            "results_breakdown": by_result,
            "records": records,
        }

    def _build_consolidated_status(self, *, gate_status: str) -> dict[str, Any]:
        verified = sorted([name for name, status in self.module_status.items() if status == VERIFIED])
        partial = sorted([name for name, status in self.module_status.items() if status == PARTIALLY_VERIFIED])
        stubbed = sorted([name for name, status in self.module_status.items() if status == STUB])
        failed = sorted([name for name, status in self.module_status.items() if status == FAILED])

        stages = [
            {
                "name": stage.name,
                "status": stage.status,
                "duration_seconds": stage.duration_seconds,
            }
            for stage in self.stages
        ]

        return {
            "run_id": self.run_id,
            "status": gate_status,
            "manual_testing_allowed": gate_status == GATE_PASS,
            "modules": {
                "verified": verified,
                "partially_verified": partial,
                "stub_not_tested": stubbed,
                "failed": failed,
            },
            "stages": stages,
            "module_status": self.module_status,
            "notes": {
                "gate_policy": "Manual testing is allowed only when status is PASS.",
            },
        }

    def _build_diagnostics_manifest(
        self,
        *,
        gate_status: str,
        diagnostics_dir: Path,
        readiness_path: Path,
        consolidated_path: Path,
        test_results_path: Path,
        patch_summary_path: Path,
        update_audit_path: Path,
        summary_json_path: Path,
        summary_md_path: Path,
    ) -> dict[str, Any]:
        warnings = sorted([name for name, status in self.module_status.items() if status == PARTIALLY_VERIFIED])
        failures = sorted([name for name, status in self.module_status.items() if status == FAILED])
        stubs = sorted([name for name, status in self.module_status.items() if status == STUB])

        stage_warnings = sorted([stage.name for stage in self.stages if stage.status == PARTIALLY_VERIFIED])
        stage_failures = sorted([stage.name for stage in self.stages if stage.status == FAILED])

        diagnostic_files = sorted([item.name for item in diagnostics_dir.glob("*.jsonl") if item.is_file()])
        test_artifact_files = sorted([item.name for item in self.test_artifacts_dir.glob("*") if item.is_file()])

        return {
            "run_id": self.run_id,
            "generated_at": _iso(_utc_now()),
            "verification_entrypoint": "python -m app.verify",
            "gate_status": gate_status,
            "manual_testing_allowed": gate_status == GATE_PASS,
            "warnings": warnings,
            "failures": failures,
            "stubs": stubs,
            "stage_warnings": stage_warnings,
            "stage_failures": stage_failures,
            "artifacts": {
                "verification_summary_json": str(summary_json_path),
                "verification_summary_md": str(summary_md_path),
                "readiness_summary_json": str(readiness_path),
                "consolidated_status_json": str(consolidated_path),
                "test_results_json": str(test_results_path),
                "patch_application_summary_json": str(patch_summary_path),
                "update_audit_summary_json": str(update_audit_path),
                "diagnostics_dir": str(diagnostics_dir),
                "diagnostics_files": diagnostic_files,
                "test_artifacts_dir": str(self.test_artifacts_dir),
                "test_artifact_files": test_artifact_files,
            },
        }

    def _build_test_results(self, *, gate_status: str, started_at: datetime, finished_at: datetime) -> dict[str, Any]:
        executed_suites = [stage.name for stage in self.stages]
        passed_checks = sorted([stage.name for stage in self.stages if stage.status == VERIFIED])
        warned_checks = sorted([stage.name for stage in self.stages if stage.status == PARTIALLY_VERIFIED])
        failed_checks = sorted([stage.name for stage in self.stages if stage.status == FAILED])
        stub_components = sorted([name for name, status in self.module_status.items() if status == STUB])
        duration_seconds = round((finished_at - started_at).total_seconds(), 3)

        test_stage_names = {"unit_tests", "integration_tests", "api_smoke_tests", "pytest_suite"}
        suites: dict[str, Any] = {}
        for stage in self.stages:
            if stage.name not in test_stage_names:
                continue
            suites[stage.name] = {
                "status": stage.status,
                "duration_seconds": stage.duration_seconds,
                "suite_type": stage.details.get("suite"),
                "source": stage.details.get("start_dir") or stage.details.get("suite_dir"),
                "exit_code": stage.details.get("exit_code"),
                "stdout_log": stage.stdout_log,
                "stderr_log": stage.stderr_log,
            }

        return {
            "run_id": self.run_id,
            "started_at": _iso(started_at),
            "finished_at": _iso(finished_at),
            "duration_seconds": duration_seconds,
            "overall_gate_status": gate_status,
            "executed_suites": executed_suites,
            "passed_checks": passed_checks,
            "warned_checks": warned_checks,
            "failed_checks": failed_checks,
            "stub_components": stub_components,
            "manual_testing_allowed": gate_status == GATE_PASS,
            "suites": suites,
        }

    def _write_reports(self) -> dict[str, str]:
        finished_at = _utc_now()
        diagnostics_dir = self.run_dir / "diagnostics"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)
        for source in self.log_dir.glob("*.jsonl"):
            shutil.copy2(source, diagnostics_dir / source.name)

        gate_status = self._gate_status()
        readiness_summary = self._build_readiness_summary(gate_status=gate_status)
        consolidated_status = self._build_consolidated_status(gate_status=gate_status)
        patch_application_summary = self._build_patch_application_summary(gate_status=gate_status)
        update_audit_summary = self._build_update_audit_summary(gate_status=gate_status)
        test_results = self._build_test_results(gate_status=gate_status, started_at=self.started_at, finished_at=finished_at)

        readiness_path = self._write_json_artifact("readiness_summary.json", readiness_summary)
        consolidated_path = self._write_json_artifact("consolidated_status.json", consolidated_status)
        test_results_path = self._write_json_artifact("test_results.json", test_results)
        patch_summary_path = self._write_json_artifact("patch_application_summary.json", patch_application_summary)
        update_audit_path = self._write_json_artifact("update_audit_summary.json", update_audit_summary)

        passed_checks = sorted([stage.name for stage in self.stages if stage.status == VERIFIED])
        warned_checks = sorted([stage.name for stage in self.stages if stage.status == PARTIALLY_VERIFIED])
        failed_checks = sorted([stage.name for stage in self.stages if stage.status == FAILED])
        stub_components = sorted([name for name, status in self.module_status.items() if status == STUB])

        artifacts_list = [
            str(self.run_dir / "verification_summary.json"),
            str(self.run_dir / "verification_summary.md"),
            str(readiness_path),
            str(consolidated_path),
            str(test_results_path),
            str(patch_summary_path),
            str(update_audit_path),
            str(self.run_dir / "diagnostics_manifest.json"),
        ]

        payload = {
            "run_id": self.run_id,
            "started_at": _iso(self.started_at),
            "finished_at": _iso(finished_at),
            "duration_seconds": round((finished_at - self.started_at).total_seconds(), 3),
            "overall_gate_status": gate_status,
            "commands": self.commands,
            "executed_suites": [stage.name for stage in self.stages],
            "passed_checks": passed_checks,
            "warned_checks": warned_checks,
            "failed_checks": failed_checks,
            "stub_components": stub_components,
            "artifacts_list": artifacts_list,
            "stages": [self._stage_to_dict(item) for item in self.stages],
            "module_status": self.module_status,
            "seed_summary": self.seed_summary,
            "gate_status": gate_status,
            "manual_testing_allowed": gate_status == GATE_PASS,
            "artifacts": {
                "run_dir": str(self.run_dir),
                "database_path": str(self.db_path),
                "workspace_state_path": str(self.workspace_state_path),
                "logs_dir": str(self.log_dir),
                "diagnostics_dir": str(diagnostics_dir),
                "test_artifacts_dir": str(self.test_artifacts_dir),
                "readiness_summary_path": str(readiness_path),
                "consolidated_status_path": str(consolidated_path),
                "test_results_path": str(test_results_path),
                "patch_application_summary_path": str(patch_summary_path),
                "update_audit_summary_path": str(update_audit_path),
            },
        }
        json_path = self.run_dir / "verification_summary.json"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        md_path = self.run_dir / "verification_summary.md"
        md_path.write_text(self._render_markdown(payload), encoding="utf-8")

        diagnostics_manifest = self._build_diagnostics_manifest(
            gate_status=gate_status,
            diagnostics_dir=diagnostics_dir,
            readiness_path=readiness_path,
            consolidated_path=consolidated_path,
            test_results_path=test_results_path,
            patch_summary_path=patch_summary_path,
            update_audit_path=update_audit_path,
            summary_json_path=json_path,
            summary_md_path=md_path,
        )
        diagnostics_manifest_path = self._write_json_artifact("diagnostics_manifest.json", diagnostics_manifest)

        payload["artifacts"]["diagnostics_manifest_path"] = str(diagnostics_manifest_path)
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(self._render_markdown(payload), encoding="utf-8")

        return {"json_path": str(json_path), "md_path": str(md_path), "gate_status": gate_status}

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
            f"- Gate status: `{payload['gate_status']}`",
            f"- Overall gate status: `{payload['overall_gate_status']}`",
            f"- Manual testing allowed: `{payload['manual_testing_allowed']}`",
            f"- Started: `{payload['started_at']}`",
            f"- Finished: `{payload['finished_at']}`",
            f"- Duration: `{payload['duration_seconds']}s`",
            "",
            "## Check Summary",
            f"- Passed checks: `{len(payload.get('passed_checks', []))}`",
            f"- Warned checks: `{len(payload.get('warned_checks', []))}`",
            f"- Failed checks: `{len(payload.get('failed_checks', []))}`",
            f"- Stub components: `{len(payload.get('stub_components', []))}`",
            "",
            "### Warned checks",
        ]
        for check in payload.get("warned_checks", []):
            lines.append(f"- `{check}`")
        if not payload.get("warned_checks"):
            lines.append("- none")
        lines.extend(
            [
                "",
                "### Failed checks",
            ]
        )
        for check in payload.get("failed_checks", []):
            lines.append(f"- `{check}`")
        if not payload.get("failed_checks"):
            lines.append("- none")
        lines.extend(
            [
                "",
                "### Stub components",
            ]
        )
        for component in payload.get("stub_components", []):
            lines.append(f"- `{component}`")
        if not payload.get("stub_components"):
            lines.append("- none")
        lines.extend(
            [
                "",
            "## Module Status",
            ]
        )
        for key, value in payload.get("module_status", {}).items():
            lines.append(f"- `{key}`: **{value}**")
        lines.append("")
        lines.append("## Stages")
        for stage in payload.get("stages", []):
            lines.append(f"- `{stage['name']}`: **{stage['status']}** ({stage['duration_seconds']}s)")
        lines.append("")
        lines.append("## Artifacts")
        for key, value in payload.get("artifacts", {}).items():
            lines.append(f"- `{key}`: `{value}`")
        return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Machine verification pipeline")
    parser.add_argument("--skip-install", action="store_true", help="Skip dependency installation step")
    args = parser.parse_args(argv)
    runner = VerificationRunner(install_deps=not args.skip_install)
    return runner.run()


if __name__ == "__main__":
    raise SystemExit(main())
