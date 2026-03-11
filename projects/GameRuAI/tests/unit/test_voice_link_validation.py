from __future__ import annotations

from pathlib import Path


def test_voice_link_validation_detects_broken_link(services, tmp_path: Path) -> None:
    game_root = tmp_path / "voice_link_validation"
    texts = game_root / "texts"
    texts.mkdir(parents=True, exist_ok=True)
    (texts / "tutorial.txt").write_text(
        "L9001|CHR_AELA|tutorial|audio/missing_voice.wav|tutorial,lang_en|Press [E] now.\n",
        encoding="utf-8",
    )

    project = services.ensure_project("Voice Link Validation", game_root)
    pid = int(project["id"])
    services.scan(pid, game_root)
    services.extract(pid, game_root)

    analyzed = services.voice_linker.analyze_links(pid, game_root=game_root, scene_index={})
    target = next(item for item in analyzed if item.get("line_id") == "L9001")
    assert target["voice_link"] == "audio/missing_voice.wav"
    assert target["link_valid"] is False
    assert 0.0 < float(target["link_confidence"]) < 1.0

