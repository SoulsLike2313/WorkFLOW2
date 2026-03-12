from __future__ import annotations


def default_export_targets() -> list[dict]:
    return [
        {"target": "texts_patch", "enabled": True, "mode": "replace_localized_strings"},
        {"target": "voice_patch", "enabled": True, "mode": "add_generated_voice_assets"},
        {"target": "subtitle_patch", "enabled": True, "mode": "timed_text_update"},
        {"target": "report_bundle", "enabled": True, "mode": "evidence_and_quality_reports"},
    ]

