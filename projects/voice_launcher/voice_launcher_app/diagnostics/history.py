from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EventHistory:
    limit: int = 30
    heard: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)

    def _push(self, buf: List[str], value: str) -> None:
        text = str(value or "").strip()
        if not text:
            return
        buf.append(text)
        if len(buf) > int(self.limit):
            del buf[:-int(self.limit)]

    def add_heard(self, text: str) -> None:
        self._push(self.heard, text)

    def add_action(self, text: str) -> None:
        self._push(self.actions, text)

    def snapshot(self, tail: int = 20) -> Dict[str, List[str]]:
        tail = max(1, int(tail))
        return {
            "heard": list(self.heard[-tail:]),
            "actions": list(self.actions[-tail:]),
        }
