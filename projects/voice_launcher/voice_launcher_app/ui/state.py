from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class UiState:
    listening: bool = False
    paused: bool = False
    has_microphone: bool = True
    active_engine: str = "whisper"
    last_heard_phrase: str = ""
    last_action_result: str = ""
    recent_events: List[str] = field(default_factory=list)

    def push_event(self, text: str, limit: int = 100) -> None:
        self.recent_events.append(text)
        if len(self.recent_events) > limit:
            self.recent_events = self.recent_events[-limit:]

