from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _clamp(value: Any, default: float, lo: float, hi: float) -> float:
    try:
        numeric = float(value)
    except Exception:
        return default
    return max(lo, min(hi, numeric))


def _sanitize_preset(raw: Any, defaults: dict[str, float]) -> dict[str, float]:
    result = dict(defaults)
    if not isinstance(raw, dict):
        return result
    for key, value in raw.items():
        if key not in result:
            continue
        if key.endswith("_radius"):
            result[key] = _clamp(value, result[key], 8.0, 28.0)
        elif key.endswith("_height"):
            result[key] = _clamp(value, result[key], 30.0, 56.0)
        else:
            result[key] = _clamp(value, result[key], 0.5, 1.6)
    return result


def default_ui_customization() -> dict[str, Any]:
    return {
        "layout_mode": "default",
        "spacing_scale": 1.0,
        "radius_scale": 1.0,
        "glow_intensity": 1.0,
        "typography_scale": 1.0,
        "button_presets": {
            "base_radius": 13.0,
            "quick_radius": 14.0,
            "base_height": 38.0,
            "action_height": 40.0,
        },
        "panel_presets": {
            "card_radius": 22.0,
            "elevated_radius": 22.0,
            "session_radius": 22.0,
            "context_radius": 22.0,
        },
    }


def load_ui_customization_profile(override_path: str | None = None) -> dict[str, Any]:
    profile = default_ui_customization()
    candidates: list[Path] = []
    if override_path:
        candidates.append(Path(override_path))
    env_path = os.getenv("SHORTFORM_UI_THEME_OVERRIDES", "").strip()
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path("runtime/ui/theme_overrides.json"))

    override_file = next((path for path in candidates if path.exists()), None)
    if override_file is None:
        return profile

    try:
        payload = json.loads(override_file.read_text(encoding="utf-8"))
    except Exception:
        return profile
    if not isinstance(payload, dict):
        return profile

    profile["layout_mode"] = str(payload.get("layout_mode", profile["layout_mode"]))
    profile["spacing_scale"] = _clamp(payload.get("spacing_scale"), profile["spacing_scale"], 0.85, 1.25)
    profile["radius_scale"] = _clamp(payload.get("radius_scale"), profile["radius_scale"], 0.85, 1.25)
    profile["glow_intensity"] = _clamp(payload.get("glow_intensity"), profile["glow_intensity"], 0.75, 1.35)
    profile["typography_scale"] = _clamp(payload.get("typography_scale"), profile["typography_scale"], 0.92, 1.18)
    profile["button_presets"] = _sanitize_preset(payload.get("button_presets"), profile["button_presets"])
    profile["panel_presets"] = _sanitize_preset(payload.get("panel_presets"), profile["panel_presets"])
    return profile


def build_customization_stylesheet(profile: dict[str, Any]) -> str:
    spacing_scale = _clamp(profile.get("spacing_scale"), 1.0, 0.85, 1.25)
    radius_scale = _clamp(profile.get("radius_scale"), 1.0, 0.85, 1.25)
    typography_scale = _clamp(profile.get("typography_scale"), 1.0, 0.92, 1.18)
    glow_intensity = _clamp(profile.get("glow_intensity"), 1.0, 0.75, 1.35)

    button_presets = _sanitize_preset(profile.get("button_presets"), default_ui_customization()["button_presets"])
    panel_presets = _sanitize_preset(profile.get("panel_presets"), default_ui_customization()["panel_presets"])

    base_radius = int(round(button_presets["base_radius"] * radius_scale))
    quick_radius = int(round(button_presets["quick_radius"] * radius_scale))
    base_height = int(round(button_presets["base_height"] * spacing_scale))
    action_height = int(round(button_presets["action_height"] * spacing_scale))

    card_radius = int(round(panel_presets["card_radius"] * radius_scale))
    elevated_radius = int(round(panel_presets["elevated_radius"] * radius_scale))
    session_radius = int(round(panel_presets["session_radius"] * radius_scale))
    context_radius = int(round(panel_presets["context_radius"] * radius_scale))
    title_size = int(round(16 * typography_scale))
    body_size = int(round(13 * typography_scale))
    glow_alpha = int(round(0.62 * glow_intensity * 255))
    glow_alpha = max(120, min(240, glow_alpha))

    return f"""
    QPushButton {{
        min-height: {base_height}px;
        border-radius: {base_radius}px;
        font-size: {max(11, body_size - 1)}px;
    }}

    QPushButton#PrimaryCTA,
    QPushButton#SecondaryCTA,
    QPushButton#OutlineCTA,
    QPushButton#DangerCTA {{
        min-height: {action_height}px;
        border-radius: {base_radius}px;
    }}

    QFrame#DashboardQuickActions QPushButton[dashboardQuickButton='true'],
    QFrame#ProfilesQuickActionsBlock QPushButton[profilesQuickAction='true'],
    QFrame#ProfilesIdentityBlock QPushButton[profilesSelectedAction='true'] {{
        border-radius: {quick_radius}px;
    }}

    QFrame[card='true'] {{
        border-radius: {card_radius}px;
    }}

    QFrame[card='elevated'] {{
        border-radius: {elevated_radius}px;
    }}

    QFrame#SessionFrame {{
        border-radius: {session_radius}px;
    }}

    QWidget#ContextPanel {{
        border-radius: {context_radius}px;
    }}

    QLabel#SectionTitle {{
        font-size: {title_size}px;
    }}

    QLabel#SectionHint {{
        font-size: {body_size}px;
    }}

    QPushButton:hover {{
        border-color: rgba(192, 167, 255, {glow_alpha});
    }}
    """
