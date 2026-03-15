from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    bg_root: str
    bg_surface: str
    bg_surface_alt: str
    border: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent: str
    accent_hover: str
    accent_soft: str
    success: str
    warning: str
    danger: str


PALETTE = Palette(
    bg_root="#0f1016",
    bg_surface="#171926",
    bg_surface_alt="#1d2030",
    border="#2b2f43",
    text_primary="#f6f3ff",
    text_secondary="#bcb8d3",
    text_muted="#8f8aa8",
    accent="#8d5cff",
    accent_hover="#9c73ff",
    accent_soft="#312450",
    success="#3ecf8e",
    warning="#f3bf4b",
    danger="#ff5f76",
)

SPACE_1 = 8
SPACE_2 = 12
SPACE_3 = 16
SPACE_4 = 20
SPACE_5 = 24
SPACE_6 = 32

WINDOW_MIN_WIDTH = 1120
WINDOW_MIN_HEIGHT = 760


def build_stylesheet() -> str:
    return f"""
QMainWindow#RepoControlWindow {{
    background: {PALETTE.bg_root};
    color: {PALETTE.text_primary};
}}
QWidget {{
    color: {PALETTE.text_primary};
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}}
QFrame#Panel {{
    background: {PALETTE.bg_surface};
    border: 1px solid {PALETTE.border};
    border-radius: 14px;
}}
QFrame#HeroCard {{
    background: {PALETTE.bg_surface_alt};
    border: 1px solid {PALETTE.border};
    border-radius: 18px;
}}
QLabel#MetaLabel {{
    color: {PALETTE.text_secondary};
    font-size: 12px;
}}
QLabel#MetaValue {{
    color: {PALETTE.text_primary};
    font-size: 13px;
    font-weight: 600;
}}
QLabel#HeroVerdict {{
    font-size: 44px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#HeroSubtitle {{
    color: {PALETTE.text_secondary};
    font-size: 14px;
}}
QLabel#SectionTitle {{
    font-size: 16px;
    font-weight: 600;
}}
QLabel#SectionHint {{
    color: {PALETTE.text_secondary};
    font-size: 12px;
}}
QLabel#StatusName {{
    font-size: 13px;
    color: {PALETTE.text_secondary};
}}
QLabel#StatusText {{
    font-size: 16px;
    font-weight: 700;
}}
QLabel#StatusSummary {{
    font-size: 12px;
    color: {PALETTE.text_secondary};
}}
QLabel#StatusBadge {{
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 700;
}}
QListWidget#IssuesList {{
    border: none;
    background: transparent;
    color: {PALETTE.text_primary};
    padding-left: 2px;
}}
QListWidget#IssuesList::item {{
    padding: 6px 4px;
    border-bottom: 1px solid #24283a;
}}
QToolButton#CollapseButton {{
    border: none;
    color: {PALETTE.text_secondary};
    text-align: left;
    font-weight: 600;
    padding: 4px 0;
}}
QTextEdit#TechnicalText {{
    border: 1px solid {PALETTE.border};
    border-radius: 10px;
    background: #121420;
    color: {PALETTE.text_secondary};
    font-family: 'Consolas', 'JetBrains Mono', monospace;
    font-size: 12px;
}}
QPushButton {{
    min-height: 34px;
    border-radius: 10px;
    border: 1px solid {PALETTE.border};
    background: #1b1f31;
    color: {PALETTE.text_primary};
    padding: 0 14px;
    font-weight: 600;
}}
QPushButton:hover {{
    border-color: #3a3f59;
    background: #20263a;
}}
QPushButton:focus {{
    border: 1px solid {PALETTE.accent};
}}
QPushButton#PrimaryButton {{
    background: {PALETTE.accent};
    border-color: {PALETTE.accent};
    color: #ffffff;
}}
QPushButton#PrimaryButton:hover {{
    background: {PALETTE.accent_hover};
    border-color: {PALETTE.accent_hover};
}}
QPushButton#DangerSecondaryButton {{
    background: #2a2238;
    border-color: #4a356c;
    color: #d8c8ff;
}}
QPushButton#DangerSecondaryButton:hover {{
    background: #332847;
    border-color: #67459a;
}}
"""
