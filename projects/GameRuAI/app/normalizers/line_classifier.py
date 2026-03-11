from __future__ import annotations

from pathlib import Path

from app.core.enums import EntryType


def classify_context(file_path: str, tags: list[str]) -> str:
    low = file_path.lower()
    low_tags = {tag.lower() for tag in tags}

    if "ui" in low or "ui" in low_tags:
        return EntryType.UI.value
    if "tutorial" in low or "tutorial" in low_tags:
        return EntryType.TUTORIAL.value
    if "combat" in low or "combat" in low_tags:
        return EntryType.COMBAT.value
    if "radio" in low or "radio" in low_tags:
        return EntryType.RADIO.value
    if "quest" in low or "quest" in low_tags:
        return EntryType.QUEST.value
    if "codex" in low or "codex" in low_tags:
        return EntryType.CODEX.value
    if "shop" in low or "shop" in low_tags:
        return EntryType.SHOP.value
    if "dialogue" in low or "banter" in low:
        return EntryType.DIALOGUE.value
    return EntryType.UNKNOWN.value
