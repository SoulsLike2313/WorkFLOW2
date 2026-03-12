from __future__ import annotations

import json

from app.config import load_config
from app.update import UpdateManifest, UpdateService
from app.version import APP_VERSION


def test_update_manifest_validation(tmp_path):
    service = UpdateService(load_config())
    manifest = UpdateManifest(
        current_version=APP_VERSION,
        available_version="0.4.1",
        patch_notes=["test patch"],
        compatibility_info={"marker": "v1"},
    )
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False), encoding="utf-8")
    loaded = service.load_manifest(path)
    ok, reason = service.validate_manifest(loaded)
    assert ok is True
    assert reason == "ok"

