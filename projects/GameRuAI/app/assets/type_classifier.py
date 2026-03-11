from __future__ import annotations

from pathlib import Path


TEXT_EXTENSIONS = {"txt", "json", "xml", "csv", "ini", "yaml", "yml", "md"}
TEXTURE_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}
AUDIO_EXTENSIONS = {"wav", "ogg", "mp3", "flac"}
ARCHIVE_EXTENSIONS = {"zip", "7z", "rar", "pak", "pck", "cpk", "vpk", "bundle", "dat"}


def classify_asset_type(path: Path, scanned_file_type: str, file_ext: str) -> str:
    ext = file_ext.lower().lstrip(".")
    if ext in TEXTURE_EXTENSIONS:
        return "texture"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in ARCHIVE_EXTENSIONS:
        return "archive"
    if scanned_file_type in {"text", "metadata", "config"} or ext in TEXT_EXTENSIONS:
        return "textual"
    if not ext:
        return "binary_unknown"
    return "binary"


def preview_type_for_asset(asset_type: str, file_ext: str) -> str:
    ext = file_ext.lower().lstrip(".")
    if asset_type == "texture" and ext in TEXTURE_EXTENSIONS:
        return "texture"
    if asset_type == "audio" and ext in AUDIO_EXTENSIONS:
        return "audio"
    return "metadata"


def preview_status_for_asset(asset_type: str, file_ext: str) -> str:
    ext = file_ext.lower().lstrip(".")
    if asset_type == "texture":
        return "ready" if ext in TEXTURE_EXTENSIONS else "metadata_only"
    if asset_type == "audio":
        # We only generate deep audio preview for wav; other audio is metadata-only for now.
        return "ready" if ext == "wav" else "metadata_only"
    return "metadata_only"


def relevance_score(path: Path, asset_type: str, size_bytes: int, suspected_container: bool) -> float:
    parts = {part.lower() for part in path.parts}
    base = 0.2
    if "texts" in parts:
        base += 0.55
    if "metadata" in parts:
        base += 0.45
    if "config" in parts:
        base += 0.4
    if "audio" in parts:
        base += 0.35

    type_boost = {
        "textual": 0.25,
        "audio": 0.18,
        "texture": 0.16,
        "archive": 0.22,
        "binary": 0.05,
        "binary_unknown": 0.02,
    }.get(asset_type, 0.0)
    base += type_boost

    if suspected_container:
        base += 0.12
    if size_bytes > 4 * 1024 * 1024:
        base += 0.08
    elif size_bytes > 512 * 1024:
        base += 0.04

    return round(min(1.0, base), 3)

