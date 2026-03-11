from __future__ import annotations

import re

TAG_PATTERN = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*[^>]*>")


def extract_tags(text: str) -> list[str]:
    tags = TAG_PATTERN.findall(text)
    seen: set[str] = set()
    ordered: list[str] = []
    for tag in tags:
        if tag not in seen:
            ordered.append(tag)
            seen.add(tag)
    return ordered


def tags_preserved(source: str, translated: str) -> bool:
    return set(extract_tags(source)).issubset(set(extract_tags(translated)))
