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
            "background": "#06070C",
            "surface": "#101726",
            "elevated_surface": "#162035",
            "border_subtle": "#303A52",
            "border_active": "#9C78FF",
            "primary_text": "#EEF2FF",
            "secondary_text": "#C1CAE4",
            "muted_text": "#8E99B7",
            "primary_accent": "#9A74FF",
            "accent_glow": "#C0A7FF",
            "success": "#33D69F",
            "warning": "#FFB85C",
            "danger": "#FF6E8A",
            "info": "#68C7FF",
            "sidebar_bg": "#0B1220",
            "topbar_bg": "#111A2B",
            "context_bg": "#0D1525",
            "session_frame": "#1C2740",
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
            "display": "Bahnschrift",
            "title": "Segoe UI Semibold",
            "body": "Segoe UI",
            "mono": "Cascadia Mono",
        },
        shadow={
            "soft": "rgba(0, 0, 0, 0.55)",
            "deep": "rgba(0, 0, 0, 0.75)",
        },
        glow={
            "subtle": "rgba(154, 116, 255, 0.32)",
            "focus": "rgba(192, 167, 255, 0.72)",
            "ai": "rgba(176, 146, 255, 0.78)",
        },
        motion={
            "fast": 130,
            "normal": 190,
            "slow": 280,
        },
    )


def build_stylesheet(tokens: ThemeTokens) -> str:
    c = tokens.colors
    r = tokens.radius
    return f"""
    QMainWindow, QWidget {{
        background: transparent;
        color: {c['primary_text']};
        font-family: '{tokens.typography['body']}';
        font-size: 13px;
    }}

    QWidget#RootShell {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #070A12, stop:0.35 #090D18, stop:0.75 #060910, stop:1 #05070C);
    }}

    QWidget#Sidebar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #0C1423, stop:1 #0A1120);
        border-right: 1px solid rgba(154, 116, 255, 0.24);
        border-top-left-radius: {r['lg']}px;
        border-bottom-left-radius: {r['lg']}px;
    }}

    QLabel#AppTitle {{
        font-family: '{tokens.typography['display']}';
        font-size: 24px;
        font-weight: 700;
        color: {c['primary_text']};
    }}

    QLabel#AppSubtitle {{
        color: {c['muted_text']};
        font-size: 12px;
        line-height: 1.4em;
    }}

    QPushButton[navButton='true'] {{
        text-align: left;
        padding: 12px 14px 12px 16px;
        border-radius: {r['lg']}px;
        border: 1px solid rgba(154, 116, 255, 0.06);
        background: rgba(255, 255, 255, 0.01);
        color: {c['secondary_text']};
        font-family: '{tokens.typography['title']}';
        font-size: 13px;
        font-weight: 600;
    }}

    QPushButton[navButton='true']:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(154, 116, 255, 0.20), stop:1 rgba(154, 116, 255, 0.10));
        border-color: rgba(154, 116, 255, 0.52);
        color: {c['primary_text']};
    }}

    QPushButton[navButton='true']:checked {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(154, 116, 255, 0.30), stop:1 rgba(154, 116, 255, 0.14));
        border-color: {c['border_active']};
        border-left: 2px solid rgba(208, 186, 255, 0.95);
        color: {c['primary_text']};
        padding-left: 18px;
    }}

    QPushButton[navButton='true']:pressed {{
        background: rgba(154, 116, 255, 0.28);
    }}

    QWidget#TopStatusBar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #121C2E, stop:1 #0F1828);
        border: 1px solid rgba(154, 116, 255, 0.32);
        border-radius: {r['xl']}px;
    }}

    QFrame[card='true'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #131C2E, stop:1 #101726);
        border: 1px solid rgba(154, 116, 255, 0.18);
        border-radius: {r['xl']}px;
    }}

    QFrame[card='elevated'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #192640, stop:1 #141D30);
        border: 1px solid rgba(154, 116, 255, 0.38);
        border-radius: {r['xl']}px;
    }}

    QLabel#CardTitle {{
        color: {c['secondary_text']};
        font-size: 12px;
        font-weight: 600;
    }}

    QLabel#CardValue {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['display']}';
        font-size: 27px;
        font-weight: 700;
    }}

    QLabel#CardMeta {{
        color: {c['muted_text']};
        font-size: 11px;
    }}

    QFrame#SessionFrame {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #1E2A46, stop:1 #18233A);
        border: 1px solid rgba(182, 145, 255, 0.74);
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
        line-height: 1.4em;
    }}

    QPushButton {{
        padding: 10px 14px;
        border-radius: {r['md']}px;
        border: 1px solid rgba(154, 116, 255, 0.22);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1A2439, stop:1 #131C2E);
        color: {c['primary_text']};
        font-size: 12px;
        font-weight: 600;
    }}

    QPushButton:hover {{
        border-color: rgba(192, 167, 255, 0.74);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(154, 116, 255, 0.36), stop:1 rgba(154, 116, 255, 0.18));
    }}

    QPushButton:pressed {{
        background: rgba(154, 116, 255, 0.25);
        padding-top: 11px;
    }}

    QPushButton#PrimaryCTA {{
        border-color: rgba(192, 167, 255, 0.88);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(118, 84, 223, 0.96), stop:1 rgba(157, 121, 255, 0.98));
        color: #FCF9FF;
        font-family: '{tokens.typography['title']}';
        font-weight: 600;
    }}

    QPushButton#PrimaryCTA:hover {{
        border-color: rgba(208, 186, 255, 0.96);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(132, 95, 235, 1.0), stop:1 rgba(172, 137, 255, 1.0));
    }}

    QPushButton#DangerCTA {{
        border-color: rgba(255, 110, 138, 0.65);
        background: rgba(255, 110, 138, 0.16);
        color: {c['danger']};
    }}

    QListWidget, QTableWidget, QTextEdit, QPlainTextEdit, QComboBox, QLineEdit {{
        background: rgba(15, 23, 38, 0.96);
        border: 1px solid rgba(154, 116, 255, 0.18);
        border-radius: {r['md']}px;
        color: {c['primary_text']};
        selection-background-color: rgba(143, 109, 255, 0.25);
        selection-color: {c['primary_text']};
        padding: 4px;
    }}

    QListWidget::item, QTableWidget::item {{
        padding: 6px;
    }}

    QListWidget::item:hover, QTableWidget::item:hover {{
        background: rgba(154, 116, 255, 0.14);
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QListWidget:focus, QTableWidget:focus {{
        border: 1px solid rgba(192, 167, 255, 0.74);
    }}

    QHeaderView::section {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1C2740, stop:1 #172034);
        color: {c['secondary_text']};
        border: 0px;
        border-bottom: 1px solid rgba(154, 116, 255, 0.22);
        padding: 9px;
        font-weight: 600;
    }}

    QLabel[statusPill='true'] {{
        border-radius: 11px;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 600;
        min-width: 84px;
        border: 1px solid rgba(154, 116, 255, 0.22);
        background: rgba(255, 255, 255, 0.04);
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
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #101A2D, stop:1 #0D1626);
        border: 1px solid rgba(154, 116, 255, 0.24);
        border-radius: {r['xl']}px;
    }}

    QWidget#AIStudioPage QFrame[card='true'],
    QWidget#AIStudioPage QFrame[card='elevated'] {{
        border: 1px solid rgba(184, 149, 255, 0.40);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(29, 40, 66, 0.98), stop:1 rgba(20, 29, 49, 0.98));
    }}

    QWidget#AIStudioPage QLabel#SectionTitle {{
        color: #F0E9FF;
    }}

    QScrollBar:vertical {{
        width: 10px;
        background: transparent;
        margin: 4px;
    }}

    QScrollBar::handle:vertical {{
        background: rgba(154, 116, 255, 0.42);
        min-height: 28px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: rgba(192, 167, 255, 0.62);
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
        height: 0px;
    }}

    QScrollBar:horizontal {{
        height: 10px;
        background: transparent;
        margin: 4px;
    }}

    QScrollBar::handle:horizontal {{
        background: rgba(154, 116, 255, 0.42);
        min-width: 28px;
        border-radius: 5px;
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        border: none;
        background: none;
        width: 0px;
    }}

    QToolTip {{
        background: #1B2741;
        color: {c['primary_text']};
        border: 1px solid rgba(192, 167, 255, 0.56);
        padding: 6px 8px;
        border-radius: {r['sm']}px;
    }}
    """
