from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from app.extractors.csv_extractor import CsvExtractor
from app.extractors.ini_extractor import IniExtractor
from app.extractors.json_extractor import JsonExtractor
from app.extractors.plain_text_extractor import PlainTextExtractor
from app.extractors.xml_extractor import XmlExtractor
from app.extractors.yaml_extractor import YamlExtractor


def test_plain_text_extractor(tmp_path: Path) -> None:
    path = tmp_path / "tutorial.txt"
    path.write_text("L1|CHR_AELA|tutorial|audio/voice_L1.wav|tutorial,ui|Press [E] now.\n", encoding="utf-8")
    rows = PlainTextExtractor().extract(path, project_id=1, rel_path="texts/tutorial.txt")
    assert len(rows) == 1
    assert rows[0].line_id == "L1"
    assert rows[0].voice_link == "audio/voice_L1.wav"


def test_json_extractor(tmp_path: Path) -> None:
    path = tmp_path / "ui.json"
    payload = {"lines": [{"line_id": "L2", "speaker_id": "CHR_AELA", "text": "Hello mission", "tags": ["ui"]}]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    rows = JsonExtractor().extract(path, project_id=1, rel_path="texts/ui.json")
    assert any(row.line_id == "L2" for row in rows)


def test_xml_extractor(tmp_path: Path) -> None:
    path = tmp_path / "quests.xml"
    root = ET.Element("quests")
    ET.SubElement(root, "quest_line", {"line_id": "L3", "speaker_id": "CHR_AELA", "text": "Quest active"})
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    rows = XmlExtractor().extract(path, project_id=1, rel_path="texts/quests.xml")
    assert len(rows) == 1
    assert rows[0].line_id == "L3"


def test_csv_extractor(tmp_path: Path) -> None:
    path = tmp_path / "dialogues.csv"
    path.write_text(
        "line_id,speaker_id,text,voice_link,tags\nL4,CHR_AELA,Hello,audio/voice_L4.wav,dialogue\n",
        encoding="utf-8",
    )
    rows = CsvExtractor().extract(path, project_id=1, rel_path="texts/dialogues.csv")
    assert len(rows) == 1
    assert rows[0].line_id == "L4"


def test_ini_extractor(tmp_path: Path) -> None:
    path = tmp_path / "game.ini"
    path.write_text("[ui]\nprompt=Press [E]\n", encoding="utf-8")
    rows = IniExtractor().extract(path, project_id=1, rel_path="config/game.ini")
    assert len(rows) == 1
    assert rows[0].line_id == "ui_prompt"


def test_yaml_extractor(tmp_path: Path) -> None:
    path = tmp_path / "combat.yaml"
    payload = {"combat": [{"line_id": "L5", "speaker_id": "CHR_AELA", "text": "Danger incoming"}]}
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    rows = YamlExtractor().extract(path, project_id=1, rel_path="texts/combat.yaml")
    assert any(row.line_id == "L5" for row in rows)
