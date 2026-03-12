from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


ExtractorHook = Callable[[str], dict]


@dataclass(slots=True)
class AssetPlugin:
    media_type: str
    plugin_name: str
    extract_hook: ExtractorHook


class AssetRegistry:
    """Foundation-only plugin registry for future per-media extraction."""

    def __init__(self) -> None:
        self._plugins: dict[str, AssetPlugin] = {}

    def register(self, plugin: AssetPlugin) -> None:
        self._plugins[plugin.media_type] = plugin

    def resolve(self, media_type: str) -> AssetPlugin | None:
        return self._plugins.get(media_type)

    def list_media_types(self) -> list[str]:
        return sorted(self._plugins)

