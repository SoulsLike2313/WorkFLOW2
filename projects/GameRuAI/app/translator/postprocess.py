from __future__ import annotations

from app.normalizers.placeholder_guard import extract_placeholders
from app.normalizers.tag_guard import extract_tags


def postprocess_translation(source: str, translated: str) -> tuple[str, list[str]]:
    decisions: list[str] = []
    result = translated.strip()

    for placeholder in extract_placeholders(source):
        if placeholder not in result:
            result += f" {placeholder}"
            decisions.append(f"placeholder restored: {placeholder}")

    for tag in extract_tags(source):
        if tag not in result:
            result = f"{tag}{result}"
            decisions.append(f"tag restored: {tag}")

    return result.strip(), decisions
