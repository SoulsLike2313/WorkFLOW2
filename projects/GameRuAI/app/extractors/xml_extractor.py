from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .base import BaseExtractor


class XmlExtractor(BaseExtractor):
    extensions = {"xml"}

    def extract(self, path: Path, *, project_id: int, rel_path: str):
        tree = ET.parse(path)
        root = tree.getroot()
        records = []

        for idx, node in enumerate(root.iter(), start=1):
            text_attr = node.attrib.get("text", "").strip()
            text_node = (node.text or "").strip()
            text = text_attr or text_node
            if not text:
                continue
            line_id = node.attrib.get("line_id") or node.attrib.get("id") or f"{path.stem}_{idx}"
            speaker = node.attrib.get("speaker_id") or node.attrib.get("speaker")
            voice_link = node.attrib.get("voice_link") or node.attrib.get("voice")
            tags = [node.tag]
            if "tags" in node.attrib:
                tags.extend([tag.strip() for tag in node.attrib["tags"].split(",") if tag.strip()])
            records.append(
                self.make_record(
                    project_id=project_id,
                    line_id=str(line_id),
                    rel_path=rel_path,
                    text=text,
                    speaker_id=speaker,
                    tags=tags,
                    voice_link=voice_link,
                    metadata={"xml_tag": node.tag, "attrib": dict(node.attrib)},
                )
            )
        return records
