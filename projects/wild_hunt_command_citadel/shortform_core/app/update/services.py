from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import AppConfig
from ..readiness import ReadinessService
from ..version import APP_NAME, APP_VERSION, BUILD_VERSION, PATCH_VERSION
from ..workspace.diagnostics import diag_log
from .models import (
    AppVersionInfo,
    PatchApplicationResult,
    PatchBundle,
    PatchStatus,
    UpdateAuditRecord,
    UpdateManifest,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UpdateService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.audit: list[UpdateAuditRecord] = []

    def get_current_version(self) -> AppVersionInfo:
        return AppVersionInfo(
            app_name=APP_NAME,
            app_version=APP_VERSION,
            build_version=BUILD_VERSION,
            patch_version=PATCH_VERSION,
            compatibility_marker="v1",
        )

    def load_manifest(self, manifest_path: Path) -> UpdateManifest:
        payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        manifest = UpdateManifest.model_validate(payload)
        self._audit("load_manifest", "ok", {"manifest_path": str(manifest_path), "manifest_id": manifest.manifest_id})
        diag_log("update_logs", "manifest_loaded", payload={"path": str(manifest_path), "manifest_id": manifest.manifest_id})
        return manifest

    def validate_manifest(self, manifest: UpdateManifest) -> tuple[bool, str]:
        current = self.get_current_version()
        if manifest.current_version != current.app_version:
            return False, f"Manifest current_version={manifest.current_version} does not match app_version={current.app_version}"
        compat = manifest.compatibility_info.get("marker")
        if compat and compat != current.compatibility_marker:
            return False, f"Incompatible marker '{compat}', expected '{current.compatibility_marker}'"
        return True, "ok"

    def check_for_update(self, manifest_path: Path) -> dict[str, Any]:
        manifest = self.load_manifest(manifest_path)
        ok, reason = self.validate_manifest(manifest)
        payload = {
            "manifest_id": manifest.manifest_id,
            "available_version": manifest.available_version,
            "is_compatible": ok,
            "reason": reason,
            "patch_notes": manifest.patch_notes,
        }
        self._audit("check_for_update", "ok" if ok else "warning", payload)
        diag_log("update_logs", "check_for_update", payload=payload, level="INFO" if ok else "WARNING")
        return payload

    def apply_local_patch(self, bundle: PatchBundle) -> PatchApplicationResult:
        patch_root = self.config.storage.patch_dir
        patch_root.mkdir(parents=True, exist_ok=True)
        backup_path = patch_root / f"{bundle.bundle_id}-workspace_state.backup.db"

        try:
            if self.config.storage.workspace_state_path.exists():
                shutil.copy2(self.config.storage.workspace_state_path, backup_path)
            else:
                backup_path = patch_root / f"{bundle.bundle_id}-empty.backup"
                backup_path.write_text("empty", encoding="utf-8")

            extracted_to = Path(tempfile.mkdtemp(prefix=f"{bundle.bundle_id}-", dir=patch_root))
            if bundle.bundle_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(bundle.bundle_path, "r") as archive:
                    archive.extractall(extracted_to)
            else:
                shutil.copy2(bundle.bundle_path, extracted_to / bundle.bundle_path.name)

            post_verify = self.post_update_verification()
            status = PatchStatus.APPLIED if post_verify.get("status") in {"PASS", "PASS_WITH_WARNINGS"} else PatchStatus.FAILED
            message = "Patch applied with post-update verification." if status == PatchStatus.APPLIED else "Patch applied but verification failed."
            result = PatchApplicationResult(
                patch_id=bundle.bundle_id,
                status=status,
                message=message,
                backup_path=backup_path,
                extracted_to=extracted_to,
                post_update_verification=post_verify,
            )
            self._audit("apply_patch", result.status.value, result.model_dump(mode="json"))
            diag_log(
                "patch_logs",
                "patch_applied",
                payload={"patch_id": bundle.bundle_id, "status": result.status.value, "backup_path": str(backup_path)},
                level="INFO" if status == PatchStatus.APPLIED else "ERROR",
            )
            return result
        except Exception as exc:
            result = PatchApplicationResult(
                patch_id=bundle.bundle_id,
                status=PatchStatus.FAILED,
                message=str(exc),
                backup_path=backup_path if backup_path.exists() else None,
                post_update_verification={"status": "FAIL", "reason": str(exc)},
            )
            self._audit("apply_patch", "failed", result.model_dump(mode="json"))
            diag_log("patch_logs", "patch_failed", level="ERROR", payload={"patch_id": bundle.bundle_id, "error": str(exc)})
            return result

    def post_update_verification(self) -> dict[str, Any]:
        readiness = ReadinessService().evaluate_local(config=self.config, workspace_runtime=None)
        status = "PASS" if readiness.get("overall_ready") else "FAIL"
        if status == "PASS":
            # If local checks pass but some optional items are unavailable, downgrade to warnings.
            warnings = [item for item in readiness.get("items", []) if not item.get("ready", False)]
            if warnings:
                status = "PASS_WITH_WARNINGS"
        payload = {"status": status, "checked_at": _utc_now().isoformat(), "readiness": readiness}
        self._audit("post_update_verification", status.lower(), payload)
        diag_log("update_logs", "post_update_verification", payload=payload, level="INFO" if status != "FAIL" else "ERROR")
        return payload

    @staticmethod
    def compute_checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with Path(path).open("rb") as fh:
            while True:
                chunk = fh.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

    def _audit(self, action: str, result: str, payload: dict[str, Any]) -> None:
        self.audit.append(UpdateAuditRecord(action=action, result=result, payload=payload))

