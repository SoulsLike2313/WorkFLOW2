from __future__ import annotations

import configparser
from pathlib import Path

from .base import BaseExtractor


class IniExtractor(BaseExtractor):
    extensions = {"ini"}

    def extract(self, path: Path, *, project_id: int, rel_path: str):
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(path, encoding="utf-8-sig")
        records = []
        for section in parser.sections():
            for key, value in parser.items(section):
                text = value.strip()
                if not text:
                    continue
                records.append(
                    self.make_record(
                        project_id=project_id,
                        line_id=f"{section}_{key}",
                        rel_path=rel_path,
                        text=text,
                        tags=[section, "config"],
                        metadata={"section": section, "key": key},
                    )
                )
        return records
