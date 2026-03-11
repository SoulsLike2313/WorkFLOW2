from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GlossaryTerm:
    source_term: str
    target_term: str
    source_lang: str
    case_sensitive: bool = False
    priority: int = 100
