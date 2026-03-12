from __future__ import annotations

from pathlib import Path

from app.assets.asset_manifest import AssetManifestEntry, build_asset_manifest
from app.assets.asset_types import classify_asset
from app.assets.container_heuristics import evaluate_container
from app.assets.relevance_scoring import score_relevance


def test_classify_asset_by_extension() -> None:
    assert classify_asset(Path("texts/ui.json")).media_type == "text"
    assert classify_asset(Path("audio/voice_001.wav")).media_type == "audio"
    assert classify_asset(Path("movies/cutscene.mp4")).media_type == "video"
    assert classify_asset(Path("textures/menu.png")).media_type == "image"
    assert classify_asset(Path("data/assets.pak")).media_type == "container"


def test_container_heuristics_and_relevance() -> None:
    result = evaluate_container(Path("packs/main_assets.pak"), media_type="container", size_bytes=4_000_000)
    assert result.suspected_container is True
    score = score_relevance(
        Path("texts/dialogues.csv"),
        media_type="text",
        has_voice_link=False,
        suspected_container=False,
    )
    assert 0.0 < score <= 1.0


def test_asset_manifest_builder_counts() -> None:
    manifest = build_asset_manifest(
        [
            AssetManifestEntry(
                file_path="texts/ui.json",
                media_type="text",
                content_role="localizable_text",
                extension="json",
                size_bytes=10,
                relevance_score=0.8,
                suspected_container=False,
            ),
            AssetManifestEntry(
                file_path="audio/voice_001.wav",
                media_type="audio",
                content_role="voice_or_sfx",
                extension="wav",
                size_bytes=20,
                relevance_score=0.6,
                suspected_container=False,
            ),
        ],
        root=Path("demo"),
    )
    assert manifest["assets_total"] == 2
    assert manifest["by_media_type"]["text"] == 1
    assert manifest["by_media_type"]["audio"] == 1

