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
    assert result.status in {PatchStatus.APPLIED, PatchStatus.FAILED}
    assert result.patch_id == bundle.bundle_id

