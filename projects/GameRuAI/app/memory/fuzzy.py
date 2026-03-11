from __future__ import annotations

from difflib import SequenceMatcher


def similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()
