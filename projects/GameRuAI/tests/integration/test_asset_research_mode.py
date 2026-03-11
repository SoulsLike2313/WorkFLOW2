from __future__ import annotations

from pathlib import Path


def test_asset_indexing_on_demo_world(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    manifest = services.scan(pid, root)

    assert "asset_index" in manifest
    assert manifest["asset_index"]["indexed_files"] == manifest["files_total"]

    snapshot = services.asset_snapshot(pid)
    assert snapshot["totals"]["assets"] == manifest["files_total"]
    assert any(item.get("asset_type") == "audio" for item in snapshot["assets"])
    assert any(item.get("asset_type") == "textual" for item in snapshot["assets"])


def test_supported_audio_preview_generation(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)

    snapshot = services.asset_snapshot(pid)
    wav_asset = next(
        item for item in snapshot["assets"] if item.get("asset_type") == "audio" and item.get("preview_status") == "ready"
    )
    details = services.asset_details(pid, str(wav_asset["file_path"]))
    assert details["preview"]["preview_status"] == "ready"
    assert int(details["preview"]["metadata_json"].get("duration_ms", 0)) > 0


def test_metadata_fallback_for_unsupported_binary(services, tmp_path: Path) -> None:
    game_root = tmp_path / "asset_meta_only_game"
    (game_root / "packs").mkdir(parents=True, exist_ok=True)
    (game_root / "packs" / "resource.mesh").write_bytes(b"mesh-binary-demo")

    project = services.ensure_project("Asset Meta Fallback", game_root)
    pid = int(project["id"])
    services.scan(pid, game_root)

    snapshot = services.asset_snapshot(pid)
    row = next(item for item in snapshot["assets"] if item["file_path"] == "packs/resource.mesh")
    assert row["preview_type"] == "metadata"
    assert row["preview_status"] == "metadata_only"
    details = services.asset_details(pid, "packs/resource.mesh")
    assert details["preview"]["preview_status"] == "metadata_only"

