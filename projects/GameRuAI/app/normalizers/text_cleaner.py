from __future__ import annotations

import re


def clean_text(text: str) -> str:
    compact = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    return compact
