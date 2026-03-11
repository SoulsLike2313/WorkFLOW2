from __future__ import annotations

from pathlib import Path

from app.assets.type_classifier import classify_asset_type, preview_status_for_asset, preview_type_for_asset, relevance_score


def test_asset_classifier_basic_types() -> None:
    assert classify_asset_type(Path("textures/ui.png"), "other", "png") == "texture"
    assert classify_asset_type(Path("audio/voice.wav"), "audio", "wav") == "audio"
    assert classify_asset_type(Path("packs/data.pak"), "other", "pak") == "archive"
    assert classify_asset_type(Path("texts/tutorial.txt"), "text", "txt") == "textual"


def test_preview_eligibility_mapping() -> None:
    assert preview_type_for_asset("texture", "png") == "texture"
    assert preview_status_for_asset("texture", "png") == "ready"
    assert preview_type_for_asset("audio", "wav") == "audio"
    assert preview_status_for_asset("audio", "wav") == "ready"
    assert preview_status_for_asset("audio", "mp3") == "metadata_only"
    assert preview_type_for_asset("binary", "dat") == "metadata"


def test_relevance_score_in_range() -> None:
    score = relevance_score(Path("texts/quests.xml"), "textual", 1024, suspected_container=False)
    assert 0.0 <= score <= 1.0
    assert score >= 0.6

