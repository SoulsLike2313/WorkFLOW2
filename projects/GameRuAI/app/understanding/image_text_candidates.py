from __future__ import annotations

from pathlib import Path


def detect_image_text_candidate(path: Path) -> dict:
    ext = path.suffix.lower().lstrip(".")
    is_image = ext in {"png", "jpg", "jpeg", "bmp", "dds", "tga", "webp"}
    name_low = path.name.lower()
    likely_text = any(token in name_low for token in ("ui", "hud", "menu", "button", "subtitle", "sign"))
    confidence = 0.0
    if is_image:
        confidence += 0.35
    if likely_text:
        confidence += 0.45
    return {
        "is_image": is_image,
        "candidate_text_overlay": bool(is_image and likely_text),
        "confidence": round(min(0.99, confidence), 3),
        "note": "OCR not implemented in MVP; candidate detection only",
    }

