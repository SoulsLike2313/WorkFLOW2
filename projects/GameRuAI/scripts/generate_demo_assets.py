from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import wave
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml


CHARACTERS = [
    {
        "speaker_id": "CHR_AELA",
        "name": "Aela Vorn",
        "region": "Northreach Federation",
        "primary_language": "en",
        "additional_languages": ["de"],
        "speech_style": "tactical and direct",
        "speech_tempo": "medium-fast",
        "emotional_profile": {"baseline": "focused", "stress": "sharp", "humor": "dry"},
    },
    {
        "speaker_id": "CHR_LUCIEN",
        "name": "Lucien Mireau",
        "region": "Cendre Republic",
        "primary_language": "fr",
        "additional_languages": ["en", "it"],
        "speech_style": "elegant and ironic",
        "speech_tempo": "medium",
        "emotional_profile": {"baseline": "composed", "stress": "sarcastic", "humor": "witty"},
    },
    {
        "speaker_id": "CHR_GRETA",
        "name": "Greta Eisen",
        "region": "Ironstadt League",
        "primary_language": "de",
        "additional_languages": ["en"],
        "speech_style": "precise and strict",
        "speech_tempo": "steady",
        "emotional_profile": {"baseline": "controlled", "stress": "commanding", "humor": "minimal"},
    },
    {
        "speaker_id": "CHR_SANTIAGO",
        "name": "Santiago Rojas",
        "region": "Solmar Coalition",
        "primary_language": "es",
        "additional_languages": ["pt"],
        "speech_style": "warm and confident",
        "speech_tempo": "fast",
        "emotional_profile": {"baseline": "energetic", "stress": "intense", "humor": "playful"},
    },
    {
        "speaker_id": "CHR_VIOLA",
        "name": "Viola Conti",
        "region": "Aurelia Compact",
        "primary_language": "it",
        "additional_languages": ["fr"],
        "speech_style": "dramatic and poetic",
        "speech_tempo": "medium",
        "emotional_profile": {"baseline": "expressive", "stress": "passionate", "humor": "theatrical"},
    },
    {
        "speaker_id": "CHR_DUARTE",
        "name": "Duarte Silva",
        "region": "Verde Straits",
        "primary_language": "pt",
        "additional_languages": ["es"],
        "speech_style": "calm and practical",
        "speech_tempo": "slow-medium",
        "emotional_profile": {"baseline": "relaxed", "stress": "grounded", "humor": "friendly"},
    },
    {
        "speaker_id": "CHR_MAJA",
        "name": "Maja Kowalska",
        "region": "Amber Frontier",
        "primary_language": "pl",
        "additional_languages": ["en"],
        "speech_style": "blunt and loyal",
        "speech_tempo": "medium",
        "emotional_profile": {"baseline": "direct", "stress": "protective", "humor": "dry"},
    },
    {
        "speaker_id": "CHR_AKIRA",
        "name": "Akira Sato",
        "region": "Kairo Arcology",
        "primary_language": "ja",
        "additional_languages": ["en"],
        "speech_style": "formal and concise",
        "speech_tempo": "measured",
        "emotional_profile": {"baseline": "calm", "stress": "focused", "humor": "subtle"},
    },
    {
        "speaker_id": "CHR_EMRE",
        "name": "Emre Demir",
        "region": "Anat Sol Dominion",
        "primary_language": "tr",
        "additional_languages": ["en", "de"],
        "speech_style": "street-smart and bold",
        "speech_tempo": "fast",
        "emotional_profile": {"baseline": "assertive", "stress": "impatient", "humor": "teasing"},
    },
    {
        "speaker_id": "CHR_HANA",
        "name": "Hana Park",
        "region": "Neon Han District",
        "primary_language": "ko",
        "additional_languages": ["ja", "en"],
        "speech_style": "soft but analytical",
        "speech_tempo": "medium",
        "emotional_profile": {"baseline": "gentle", "stress": "urgent", "humor": "quiet"},
    },
]

LANGUAGE_POOL = [
    "en",
    "fr",
    "de",
    "es",
    "it",
    "pt",
    "pl",
    "ja",
    "tr",
    "ko",
    "zh",
]

TEMPLATES = {
    "en": [
        "Commander, the gate in Sector {money} is unstable.",
        "Press [E] to activate beacon %PLAYER_NAME%.",
        "Warning: <b>reactor</b> heat reached {money}.",
        "Shop is open, bring 3 crystal shards.",
    ],
    "fr": [
        "Bonjour, la mission commence dans la zone {money}.",
        "Appuie sur [E] pour ouvrir le terminal.",
        "Le marchand attend %PLAYER_NAME% au pont central.",
        "Alerte: le signal <b>orbital</b> chute vite.",
    ],
    "de": [
        "Hallo, die Mission im Korridor {money} beginnt jetzt.",
        "Druecke [E], um das Modul zu starten.",
        "Achtung: der <b>Reaktor</b> ist nicht stabil.",
        "Bitte bringe %PLAYER_NAME% zum Handelsposten.",
    ],
    "es": [
        "Hola, la mision secundaria empieza en nodo {money}.",
        "Pulsa [E] para abrir la compuerta.",
        "Peligro: el <b>motor</b> pierde energia.",
        "El comerciante espera a %PLAYER_NAME% en la plaza.",
    ],
    "it": [
        "Ciao, la missione richiede accesso al livello {money}.",
        "Premi [E] per confermare il percorso.",
        "Pericolo: il <b>reattore</b> vibra troppo.",
        "Il negozio offre sconti per %PLAYER_NAME%.",
    ],
    "pt": [
        "Ola, a missao principal muda no setor {money}.",
        "Pressione [E] para destravar o painel.",
        "Perigo: o <b>nucleo</b> esta sobrecarga.",
        "A loja guarda itens para %PLAYER_NAME%.",
    ],
    "pl": [
        "Czesc, misja boczna jest przy punkcie {money}.",
        "Nacisnij [E], aby otworzyc wlaz.",
        "Uwaga: <b>reaktor</b> traci moc.",
        "Kupiec czeka na %PLAYER_NAME% przy rynku.",
    ],
    "ja": [
        "任務はセクター{money}で開始します。",
        "[E]を押してゲートを開いてください。",
        "警告：<b>リアクター</b>温度が上昇中です。",
        "%PLAYER_NAME% は中央通路へ移動してください。",
    ],
    "tr": [
        "Merhaba, gorev {money} bolgesinde basliyor.",
        "Kapak acmak icin [E] tusuna bas.",
        "Tehlike: <b>reaktor</b> dengesiz durumda.",
        "Dukkan %PLAYER_NAME% icin malzeme ayirdi.",
    ],
    "ko": [
        "임무는 구역 {money} 에서 시작됩니다.",
        "[E] 키를 눌러 문을 여세요.",
        "경고: <b>반응로</b> 온도가 상승합니다.",
        "%PLAYER_NAME% 는 중앙 통로로 이동하세요.",
    ],
    "zh": [
        "任务将在区域{money}开始。",
        "按下[E]打开控制台。",
        "警告：<b>反应堆</b>温度过高。",
        "%PLAYER_NAME%请前往中央平台。",
    ],
}


def _sine_wav(path: Path, duration_ms: int, frequency: int) -> None:
    sample_rate = 22050
    total = int(sample_rate * duration_ms / 1000)
    amplitude = 9000
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(total):
            value = int(amplitude * math.sin(2 * math.pi * frequency * (i / sample_rate)))
            frames += value.to_bytes(2, byteorder="little", signed=True)
        wav.writeframes(frames)


def _pick_speaker(lang: str, idx: int) -> dict[str, Any]:
    by_lang = [char for char in CHARACTERS if char["primary_language"] == lang]
    if by_lang:
        return by_lang[idx % len(by_lang)]
    return CHARACTERS[idx % len(CHARACTERS)]


def _build_line(line_id: str, lang: str, idx: int, category: str) -> dict[str, Any]:
    speaker = _pick_speaker(lang, idx)
    text = random.choice(TEMPLATES[lang])
    text = text.replace("{money}", str((idx * 7) % 900 + 100))
    text = text.replace("%PLAYER_NAME%", "%PLAYER_NAME%")
    voice_link = f"audio/voice_{line_id}.wav" if category not in {"ui", "codex"} and (idx % 2 == 0 or idx % 5 == 0) else ""
    return {
        "line_id": line_id,
        "language": lang,
        "speaker_id": speaker["speaker_id"],
        "text": text,
        "voice_link": voice_link,
        "tags": [category, f"lang_{lang}"],
        "context": category,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _build_voice_profiles() -> list[dict[str, Any]]:
    styles = ["neutral", "dramatic", "calm", "radio"]
    profiles = []
    for idx, char in enumerate(CHARACTERS):
        profiles.append(
            {
                "speaker_id": char["speaker_id"],
                "display_name": char["name"],
                "style_preset": styles[idx % len(styles)],
                "speech_rate": round(0.85 + (idx % 4) * 0.15, 2),
                "base_frequency": 180 + idx * 17,
                "emotion_bias": char["emotional_profile"]["baseline"],
                "region": char["region"],
            }
        )
    return profiles


def _assert_no_cyrillic(lines: list[dict[str, Any]]) -> None:
    cyrillic = re.compile(r"[А-Яа-яЁё]")
    offenders = [line["line_id"] for line in lines if cyrillic.search(str(line.get("text", "")))]
    if offenders:
        raise ValueError(f"Source demo lines must not contain Russian/Cyrillic. Offenders: {offenders[:10]}")


def generate_demo_assets(project_root: Path, *, seed: int = 42, line_count: int = 340) -> dict[str, Any]:
    random.seed(seed)
    base = project_root / "fixtures" / "demo_game_world"
    texts_dir = base / "texts"
    audio_dir = base / "audio"
    metadata_dir = base / "metadata"
    config_dir = base / "config"
    for folder in (texts_dir, audio_dir, metadata_dir, config_dir):
        folder.mkdir(parents=True, exist_ok=True)

    categories = [
        ("ui", 35),
        ("dialogues_main", 60),
        ("dialogues_sidequests", 50),
        ("quests", 30),
        ("tutorial", 25),
        ("combat_barks", 30),
        ("codex_entries", 35),
        ("radio_chatter", 30),
        ("npc_banter", 25),
        ("shops", 20),
    ]

    all_lines: list[dict[str, Any]] = []
    language_map: dict[str, str] = {}
    line_idx = 1
    lang_cycle = LANGUAGE_POOL * 40

    for category, amount in categories:
        for _ in range(amount):
            line_id = f"L{line_idx:04d}"
            lang = lang_cycle[(line_idx - 1) % len(lang_cycle)]
            line = _build_line(line_id, lang, line_idx, category)
            all_lines.append(line)
            language_map[line_id] = lang
            line_idx += 1

    _assert_no_cyrillic(all_lines)

    # texts/ui.json
    _write_json(texts_dir / "ui.json", {"lines": [line for line in all_lines if line["context"] == "ui"]})

    # dialogues_main.csv
    _write_csv(
        texts_dir / "dialogues_main.csv",
        [line for line in all_lines if line["context"] == "dialogues_main"],
    )

    # dialogues_sidequests.csv
    _write_csv(
        texts_dir / "dialogues_sidequests.csv",
        [line for line in all_lines if line["context"] == "dialogues_sidequests"],
    )

    # quests.xml
    quests_root = ET.Element("quests")
    for line in [line for line in all_lines if line["context"] == "quests"]:
        ET.SubElement(
            quests_root,
            "quest_line",
            {
                "line_id": line["line_id"],
                "speaker_id": line["speaker_id"],
                "voice_link": line["voice_link"],
                "tags": ",".join(line["tags"]),
                "text": line["text"],
            },
        )
    ET.ElementTree(quests_root).write(texts_dir / "quests.xml", encoding="utf-8", xml_declaration=True)

    # tutorial.txt
    tutorial_lines = []
    for line in [line for line in all_lines if line["context"] == "tutorial"]:
        tutorial_lines.append(
            "|".join(
                [
                    line["line_id"],
                    line["speaker_id"],
                    line["context"],
                    line["voice_link"],
                    ",".join(line["tags"]),
                    line["text"],
                ]
            )
        )
    (texts_dir / "tutorial.txt").write_text("\n".join(tutorial_lines) + "\n", encoding="utf-8")

    # combat_barks.yaml
    combat_payload = {"combat": [line for line in all_lines if line["context"] == "combat_barks"]}
    (texts_dir / "combat_barks.yaml").write_text(yaml.safe_dump(combat_payload, sort_keys=False, allow_unicode=True), encoding="utf-8")

    # codex_entries.json
    codex_lines = [line for line in all_lines if line["context"] == "codex_entries"]
    codex_payload = {
        "categories": [
            {"name": "factions", "entries": codex_lines[:18]},
            {"name": "technology", "entries": codex_lines[18:]},
        ]
    }
    _write_json(texts_dir / "codex_entries.json", codex_payload)

    # radio_chatter.csv
    _write_csv(
        texts_dir / "radio_chatter.csv",
        [line for line in all_lines if line["context"] == "radio_chatter"],
    )

    # npc_banter.yaml
    banter_payload = {"banter": [line for line in all_lines if line["context"] == "npc_banter"]}
    (texts_dir / "npc_banter.yaml").write_text(yaml.safe_dump(banter_payload, sort_keys=False, allow_unicode=True), encoding="utf-8")

    # shops.xml
    shops_root = ET.Element("shops")
    for line in [line for line in all_lines if line["context"] == "shops"]:
        ET.SubElement(
            shops_root,
            "shop_line",
            {
                "line_id": line["line_id"],
                "speaker_id": line["speaker_id"],
                "voice_link": line["voice_link"],
                "tags": ",".join(line["tags"]),
                "text": line["text"],
            },
        )
    ET.ElementTree(shops_root).write(texts_dir / "shops.xml", encoding="utf-8", xml_declaration=True)

    # metadata
    _write_json(metadata_dir / "characters.json", CHARACTERS)
    _write_json(metadata_dir / "voice_profiles.json", _build_voice_profiles())
    scenes = []
    chunk_size = 20
    for idx in range(0, len(all_lines), chunk_size):
        scene_lines = all_lines[idx : idx + chunk_size]
        scenes.append(
            {
                "scene_id": f"SCENE_{idx // chunk_size + 1:02d}",
                "title": f"Demo Scene {idx // chunk_size + 1}",
                "line_ids": [line["line_id"] for line in scene_lines],
            }
        )
    _write_json(metadata_dir / "scenes.json", scenes)
    _write_json(metadata_dir / "language_map.json", language_map)

    # game config
    (config_dir / "game.ini").write_text(
        "\n".join(
            [
                "[game]",
                "title=Neon Frontier: Echo Rift",
                "build=0.9.7-demo",
                "locale_default=en",
                "",
                "[ui]",
                "prompt_interact=Press [E] to interact",
                "currency_name=credits",
                "network_mode=offline",
                "",
                "[audio]",
                "master_volume=82",
                "voice_pack=original_demo",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # placeholder audio for voice-linked lines
    voiced_lines = [line for line in all_lines if line["voice_link"]]
    for idx, line in enumerate(voiced_lines):
        wav_path = base / line["voice_link"]
        _sine_wav(wav_path, duration_ms=1000 + (idx % 7) * 120, frequency=190 + (idx % 10) * 20)

    return {
        "base": str(base),
        "total_lines": len(all_lines),
        "voice_assets": len(voiced_lines),
        "languages": sorted(set(language_map.values())),
        "characters": len(CHARACTERS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic GameRuAI demo game assets.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--line-count", type=int, default=340)
    args = parser.parse_args()

    summary = generate_demo_assets(args.project_root, seed=args.seed, line_count=args.line_count)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
