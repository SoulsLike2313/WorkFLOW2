from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TEXT_EXTENSIONS = {"txt", "json", "xml", "csv", "ini", "yaml", "yml", "srt", "ass", "vtt"}
SUBTITLE_EXTENSIONS = {"srt", "ass", "vtt"}
AUDIO_EXTENSIONS = {"wav", "ogg", "mp3", "flac"}
VIDEO_EXTENSIONS = {"mp4", "mkv", "webm", "bik", "wmv", "avi"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp", "tga", "dds"}
ARCHIVE_EXTENSIONS = {"zip", "7z", "rar", "pak", "pck", "cpk", "vpk", "bundle", "dat"}


@dataclass(slots=True)
class AssetDescriptor:
    file_path: str
    extension: str
    media_type: str
    content_role: str


def classify_asset(path: Path, scanned_file_type: str = "other") -> AssetDescriptor:
    ext = path.suffix.lower().lstrip(".")
    media_type = "binary"
    content_role = "unknown"

    if ext in SUBTITLE_EXTENSIONS:
        media_type = "subtitle"
        content_role = "timed_text"
    elif ext in TEXT_EXTENSIONS or scanned_file_type in {"text", "config", "metadata"}:
        media_type = "text"
        content_role = "localizable_text"
    elif ext in AUDIO_EXTENSIONS:
        media_type = "audio"
        content_role = "voice_or_sfx"
    elif ext in VIDEO_EXTENSIONS:
        media_type = "video"
        content_role = "video_media"
    elif ext in IMAGE_EXTENSIONS:
        media_type = "image"
        content_role = "ui_or_texture"
    elif ext in ARCHIVE_EXTENSIONS:
        media_type = "container"
        content_role = "archive_bundle"

    return AssetDescriptor(
        file_path=path.as_posix(),
        extension=ext or "unknown",
        media_type=media_type,
        content_role=content_role,
    )

