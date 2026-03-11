from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

from .type_classifier import TEXTURE_EXTENSIONS


def can_preview_texture(path: Path) -> bool:
    return path.suffix.lower().lstrip(".") in TEXTURE_EXTENSIONS and path.exists() and path.is_file()


def texture_metadata(path: Path) -> dict[str, Any]:
    ext = path.suffix.lower().lstrip(".")
    metadata: dict[str, Any] = {
        "extension": ext,
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }
    if ext == "png":
        metadata.update(_png_dimensions(path))
    return metadata


def build_texture_preview(path: Path) -> tuple[str, str, dict[str, Any]]:
    if not can_preview_texture(path):
        return "texture", "metadata_only", texture_metadata(path)
    metadata = texture_metadata(path)
    metadata["preview_source"] = str(path)
    return "texture", "ready", metadata


def _png_dimensions(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as fh:
            signature = fh.read(8)
            if signature != b"\x89PNG\r\n\x1a\n":
                return {}
            chunk_len = struct.unpack(">I", fh.read(4))[0]
            chunk_type = fh.read(4)
            if chunk_type != b"IHDR" or chunk_len < 8:
                return {}
            width = struct.unpack(">I", fh.read(4))[0]
            height = struct.unpack(">I", fh.read(4))[0]
            return {"width": width, "height": height}
    except Exception:
        return {}

