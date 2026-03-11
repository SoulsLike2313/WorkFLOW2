from __future__ import annotations

from pathlib import Path

from .base import BaseExtractor
from .csv_extractor import CsvExtractor
from .ini_extractor import IniExtractor
from .json_extractor import JsonExtractor
from .plain_text_extractor import PlainTextExtractor
from .xml_extractor import XmlExtractor
from .yaml_extractor import YamlExtractor


class ExtractorRegistry:
    def __init__(self):
        self.extractors: list[BaseExtractor] = [
            PlainTextExtractor(),
            JsonExtractor(),
            XmlExtractor(),
            CsvExtractor(),
            IniExtractor(),
            YamlExtractor(),
        ]

    def get_for_path(self, path: Path) -> BaseExtractor | None:
        for extractor in self.extractors:
            if extractor.supports(path):
                return extractor
        return None

    def supported_extensions(self) -> set[str]:
        exts: set[str] = set()
        for extractor in self.extractors:
            exts.update(extractor.extensions)
        return exts
