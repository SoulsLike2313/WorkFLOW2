from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeTokens:
    colors: dict[str, str]
    spacing: dict[str, int]
    radius: dict[str, int]
    typography: dict[str, str]
    shadow: dict[str, str]
    glow: dict[str, str]
    motion: dict[str, int]


def build_theme_tokens() -> ThemeTokens:
    return ThemeTokens(
        colors={
            "background": "#07080D",
            "surface": "#0E1421",
            "elevated_surface": "#151D2E",
            "border_subtle": "#2B3446",
            "border_active": "#8B6CFF",
            "primary_text": "#E8ECFF",
            "secondary_text": "#B5BED9",
            "muted_text": "#8690AC",
            "primary_accent": "#8F6DFF",
            "accent_glow": "#B59BFF",
            "success": "#33D69F",
            "warning": "#FFB85C",
            "danger": "#FF6E8A",
            "info": "#68C7FF",
            "sidebar_bg": "#0A101C",
            "topbar_bg": "#0D1422",
            "context_bg": "#0B1220",
            "session_frame": "#1A2337",
        },
        spacing={
            "xs": 6,
            "sm": 10,
            "md": 14,
            "lg": 20,
            "xl": 28,
            "xxl": 36,
        },
        radius={
            "sm": 10,
            "md": 14,
            "lg": 18,
            "xl": 22,
        },
        typography={
            "display": "Bahnschrift SemiBold",
            "title": "Segoe UI Semibold",
            "body": "Segoe UI",
            "mono": "Cascadia Mono",
        },
        shadow={
            "soft": "rgba(0, 0, 0, 0.55)",
            "deep": "rgba(0, 0, 0, 0.75)",
        },
        glow={
            "subtle": "rgba(143, 109, 255, 0.25)",
            "focus": "rgba(176, 147, 255, 0.60)",
            "ai": "rgba(156, 134, 255, 0.70)",
        },
        motion={
            "fast": 120,
            "normal": 180,
            "slow": 260,
        },
    )


def build_stylesheet(tokens: ThemeTokens) -> str:
    c = tokens.colors
    r = tokens.radius
    return f"""
    QMainWindow, QWidget {{
        background: {c['background']};
        color: {c['primary_text']};
        font-family: '{tokens.typography['body']}';
        font-size: 13px;
    }}

    QWidget#RootShell {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {c['background']}, stop:0.5 #0B0F19, stop:1 #07080D);
    }}

    QWidget#Sidebar {{
        background: {c['sidebar_bg']};
        border-right: 1px solid {c['border_subtle']};
    }}

    QLabel#AppTitle {{
        font-family: '{tokens.typography['display']}';
        font-size: 22px;
        font-weight: 700;
        color: {c['primary_text']};
    }}

    QLabel#AppSubtitle {{
        color: {c['secondary_text']};
        font-size: 12px;
    }}

    QPushButton[navButton='true'] {{
        text-align: left;
        padding: 12px 14px;
        border-radius: {r['md']}px;
        border: 1px solid transparent;
        background: transparent;
        color: {c['secondary_text']};
        font-family: '{tokens.typography['title']}';
        font-size: 13px;
    }}

    QPushButton[navButton='true']:hover {{
        background: rgba(143, 109, 255, 0.12);
        border-color: rgba(143, 109, 255, 0.45);
        color: {c['primary_text']};
    }}

    QPushButton[navButton='true']:checked {{
        background: rgba(143, 109, 255, 0.18);
        border-color: {c['border_active']};
        color: {c['primary_text']};
    }}

    QWidget#TopStatusBar {{
        background: {c['topbar_bg']};
        border: 1px solid {c['border_subtle']};
        border-radius: {r['lg']}px;
    }}

    QFrame[card='true'] {{
        background: {c['surface']};
        border: 1px solid {c['border_subtle']};
        border-radius: {r['lg']}px;
    }}

    QFrame[card='elevated'] {{
        background: {c['elevated_surface']};
        border: 1px solid rgba(143, 109, 255, 0.30);
        border-radius: {r['xl']}px;
    }}

    QLabel#CardTitle {{
        color: {c['secondary_text']};
        font-size: 12px;
    }}

    QLabel#CardValue {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['display']}';
        font-size: 25px;
        font-weight: 700;
    }}

    QLabel#CardMeta {{
        color: {c['muted_text']};
        font-size: 11px;
    }}

    QFrame#SessionFrame {{
        background: {c['session_frame']};
        border: 1px solid rgba(165, 124, 255, 0.65);
        border-radius: {r['xl']}px;
    }}

    QLabel#SectionTitle {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['title']}';
        font-size: 16px;
        font-weight: 600;
    }}

    QLabel#SectionHint {{
        color: {c['muted_text']};
        font-size: 12px;
    }}

    QPushButton {{
        padding: 9px 12px;
        border-radius: {r['md']}px;
        border: 1px solid {c['border_subtle']};
        background: {c['surface']};
        color: {c['primary_text']};
        font-size: 12px;
    }}

    QPushButton:hover {{
        border-color: rgba(143, 109, 255, 0.70);
        background: rgba(143, 109, 255, 0.12);
    }}

    QPushButton:pressed {{
        background: rgba(143, 109, 255, 0.20);
    }}

    QPushButton#PrimaryCTA {{
        border-color: rgba(143, 109, 255, 0.85);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(98, 74, 189, 0.90), stop:1 rgba(143, 109, 255, 0.95));
        color: #F5F0FF;
        font-family: '{tokens.typography['title']}';
        font-weight: 600;
    }}

    QPushButton#DangerCTA {{
        border-color: rgba(255, 110, 138, 0.70);
        background: rgba(255, 110, 138, 0.14);
        color: {c['danger']};
    }}

    QListWidget, QTableWidget, QTextEdit, QPlainTextEdit, QComboBox, QLineEdit {{
        background: {c['surface']};
        border: 1px solid {c['border_subtle']};
        border-radius: {r['md']}px;
        color: {c['primary_text']};
        selection-background-color: rgba(143, 109, 255, 0.25);
        selection-color: {c['primary_text']};
    }}

    QHeaderView::section {{
        background: #151E2F;
        color: {c['secondary_text']};
        border: 0px;
        border-bottom: 1px solid {c['border_subtle']};
        padding: 8px;
    }}

    QLabel[statusPill='true'] {{
        border-radius: 10px;
        padding: 4px 9px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid {c['border_subtle']};
        background: rgba(255, 255, 255, 0.03);
    }}

    QLabel[statusLevel='ok'] {{
        color: {c['success']};
        border-color: rgba(51, 214, 159, 0.50);
        background: rgba(51, 214, 159, 0.11);
    }}

    QLabel[statusLevel='warn'] {{
        color: {c['warning']};
        border-color: rgba(255, 184, 92, 0.50);
        background: rgba(255, 184, 92, 0.11);
    }}

    QLabel[statusLevel='danger'] {{
        color: {c['danger']};
        border-color: rgba(255, 110, 138, 0.50);
        background: rgba(255, 110, 138, 0.11);
    }}

    QLabel[statusLevel='info'] {{
        color: {c['info']};
        border-color: rgba(104, 199, 255, 0.50);
        background: rgba(104, 199, 255, 0.11);
    }}

    QLabel#ContextPanelTitle {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['title']}';
        font-size: 15px;
        font-weight: 600;
    }}

    QWidget#ContextPanel {{
        background: {c['context_bg']};
        border: 1px solid {c['border_subtle']};
        border-radius: {r['lg']}px;
    }}
    """
