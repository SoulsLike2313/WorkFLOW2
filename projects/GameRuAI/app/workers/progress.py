from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Progress:
    current: int = 0
    total: int = 0
    stage: str = "idle"

    @property
    def percent(self) -> float:
        if self.total <= 0:
            return 0.0
        return round((self.current / self.total) * 100, 2)
