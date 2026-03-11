from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import BaseExtractor


class JsonExtractor(BaseExtractor):
    extensions = {"json"}

    def extract(self, path: Path, *, project_id: int, rel_path: str):
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        records: list[Any] = []

        def walk(node: Any, breadcrumb: str) -> None:
            if isinstance(node, dict):
                text = node.get("text")
                if isinstance(text, str) and text.strip():
                    line_id = str(node.get("line_id") or node.get("id") or breadcrumb.replace("/", "_"))
                    speaker = str(node.get("speaker_id") or node.get("speaker") or "").strip() or None
                    voice_link = str(node.get("voice_link") or node.get("voice") or "").strip() or None
                    tags = node.get("tags") if isinstance(node.get("tags"), list) else []
                    records.append(
                        self.make_record(
                            project_id=project_id,
                            line_id=line_id,
                            rel_path=rel_path,
                            text=text,
                            speaker_id=speaker,
                            tags=[str(tag) for tag in tags],
                            voice_link=voice_link,
                            metadata={"source_json_path": breadcrumb},
                        )
                    )
                for key, value in node.items():
                    walk(value, f"{breadcrumb}/{key}")
            elif isinstance(node, list):
                for idx, value in enumerate(node):
                    walk(value, f"{breadcrumb}/{idx}")
            elif isinstance(node, str):
                stripped = node.strip()
                if stripped:
                    records.append(
                        self.make_record(
                            project_id=project_id,
                            line_id=f"{path.stem}_{len(records)+1}",
                            rel_path=rel_path,
                            text=stripped,
                            metadata={"source_json_path": breadcrumb},
                        )
                    )

        walk(payload, path.stem)
        return records
