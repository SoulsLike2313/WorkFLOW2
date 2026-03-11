from __future__ import annotations

from app.voice.speaker_grouping import SpeakerGroupingService


def test_speaker_grouping_aggregates_counts() -> None:
    service = SpeakerGroupingService()
    groups = service.build_groups(
        [
            {"speaker_id": "CHR_A", "voice_link": "audio/a.wav", "link_valid": True, "link_confidence": 0.8, "scene_id": "S1"},
            {"speaker_id": "CHR_A", "voice_link": "audio/b.wav", "link_valid": False, "link_confidence": 0.4, "scene_id": "S2"},
            {"speaker_id": "CHR_B", "voice_link": "audio/c.wav", "link_valid": True, "link_confidence": 0.9, "scene_id": "S1"},
        ]
    )
    assert len(groups) == 2
    a_group = next(item for item in groups if item["speaker_id"] == "CHR_A")
    assert a_group["line_count"] == 2
    assert a_group["broken_links"] == 1
    assert a_group["scene_count"] == 2

