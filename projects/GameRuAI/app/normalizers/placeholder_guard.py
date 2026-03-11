from __future__ import annotations

import re

PLACEHOLDER_PATTERNS = [
    re.compile(r"%[A-Z0-9_]+%"),
    re.compile(r"\{[a-zA-Z0-9_]+\}"),
    re.compile(r"\[[A-Z0-9_]+\]"),
]


def extract_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        placeholders.extend(pattern.findall(text))
    seen: set[str] = set()
    ordered: list[str] = []
    for token in placeholders:
        if token not in seen:
            ordered.append(token)
            seen.add(token)
    return ordered


def placeholders_preserved(source: str, translated: str) -> bool:
    src = set(extract_placeholders(source))
    dst = set(extract_placeholders(translated))
    return src.issubset(dst)
