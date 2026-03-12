from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class BotSettings:
    cdp_url: str
    profile_url: str
    output_dir: Path = Path("output")
    for_you_url: str = "https://www.tiktok.com/foryou"

    watch_enabled: bool = True
    watch_videos: int = 10

    collect_stats_enabled: bool = True
    monitor_enabled: bool = False

    comment_enabled: bool = False
    max_comments: int = 2
    comments: List[str] = field(default_factory=list)

    visit_profiles_enabled: bool = False
    max_profiles_to_visit: int = 5
    profiles: List[str] = field(default_factory=list)

    upload_enabled: bool = False
    upload_file: str = ""
    upload_caption: str = ""
    publish_upload: bool = False

    min_delay_seconds: float = 3.0
    max_delay_seconds: float = 8.0

    retry_attempts: int = 2
    action_timeout_seconds: float = 12.0
    selector_timeout_ms: int = 4500
    health_check_enabled: bool = True
    strict_health_check: bool = False

    def normalized(self) -> "BotSettings":
        min_delay = max(0.5, self.min_delay_seconds)
        max_delay = max(min_delay, self.max_delay_seconds)
        return BotSettings(
            cdp_url=self.cdp_url.strip(),
            profile_url=self.profile_url.strip(),
            output_dir=Path(self.output_dir),
            for_you_url=self.for_you_url.strip() or "https://www.tiktok.com/foryou",
            watch_enabled=self.watch_enabled,
            watch_videos=max(0, self.watch_videos),
            collect_stats_enabled=self.collect_stats_enabled,
            monitor_enabled=self.monitor_enabled,
            comment_enabled=self.comment_enabled and bool(self.comments),
            max_comments=max(0, self.max_comments),
            comments=[value.strip() for value in self.comments if value.strip()],
            visit_profiles_enabled=self.visit_profiles_enabled and bool(self.profiles),
            max_profiles_to_visit=max(0, self.max_profiles_to_visit),
            profiles=[value.strip() for value in self.profiles if value.strip()],
            upload_enabled=self.upload_enabled and bool(self.upload_file.strip()),
            upload_file=self.upload_file.strip(),
            upload_caption=self.upload_caption.strip(),
            publish_upload=self.publish_upload,
            min_delay_seconds=min_delay,
            max_delay_seconds=max_delay,
            retry_attempts=max(1, int(self.retry_attempts)),
            action_timeout_seconds=max(2.0, float(self.action_timeout_seconds)),
            selector_timeout_ms=max(500, int(self.selector_timeout_ms)),
            health_check_enabled=bool(self.health_check_enabled),
            strict_health_check=bool(self.strict_health_check),
        )
