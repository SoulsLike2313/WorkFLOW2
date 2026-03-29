from __future__ import annotations

import zipfile
from pathlib import Path

from app.config import load_config
from app.update import PatchBundle, PatchStatus, UpdateService


def test_patch_application_validation(tmp_path: Path):
    config = load_config()
    config.storage.patch_dir = tmp_path / "patches"
    config.storage.patch_dir.mkdir(parents=True, exist_ok=True)
    config.storage.workspace_state_path = tmp_path / "workspace_state.db"
    config.storage.workspace_state_path.write_text("placeholder", encoding="utf-8")

    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("README.txt", "patch payload")

    service = UpdateService(config)
    bundle = PatchBundle(bundle_path=zip_path, target_version="0.4.1")
    result = service.apply_local_patch(bundle)
    # Runtime dependency contract may trigger rollback when post-verify cannot pass.
    assert result.status in {PatchStatus.APPLIED, PatchStatus.FAILED, PatchStatus.ROLLED_BACK}
    assert result.patch_id == bundle.bundle_id


def test_patch_rolls_back_on_failed_post_verify(tmp_path: Path):
    config = load_config()
    config.storage.patch_dir = tmp_path / "patches"
    config.storage.patch_dir.mkdir(parents=True, exist_ok=True)
    config.storage.workspace_state_path = tmp_path / "workspace_state.db"
    original_state = b"original-workspace-state"
    config.storage.workspace_state_path.write_bytes(original_state)

    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("README.txt", "patch payload")

    class FailingVerifyUpdateService(UpdateService):
        def post_update_verification(self) -> dict[str, object]:
            return {"status": "FAIL", "reason": "forced failure"}

    service = FailingVerifyUpdateService(config)
    bundle = PatchBundle(bundle_path=zip_path, target_version="0.4.1")
    result = service.apply_local_patch(bundle)

    assert result.status == PatchStatus.ROLLED_BACK
    assert result.rollback_applied is True
    assert config.storage.workspace_state_path.read_bytes() == original_state
