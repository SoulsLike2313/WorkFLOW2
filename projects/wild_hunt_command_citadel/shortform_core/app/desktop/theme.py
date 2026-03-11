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
            "display": "Segoe UI Variable Display, Segoe UI",
            "title": "Segoe UI Semibold",
            "body": "Segoe UI",
            "label": "Segoe UI Variable Text, Segoe UI",
            "metric": "Bahnschrift SemiBold, Segoe UI Variable Display",
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
        font-size: 27px;
        font-weight: 650;
        color: {c['primary_text']};
    }}

    QLabel#AppSubtitle {{
        color: {c['muted_text']};
        font-size: 12px;
        font-family: '{tokens.typography['label']}';
        font-weight: 450;
    }}

    QPushButton[navButton='true'] {{
        text-align: left;
        padding: 12px 14px 12px 16px;
        border-radius: {r['lg']}px;
        border: 1px solid rgba(154, 116, 255, 0.10);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255,255,255,0.02), stop:1 rgba(255,255,255,0.00));
        color: {c['secondary_text']};
        font-family: '{tokens.typography['label']}';
        font-size: 13px;
        font-weight: 520;
    }}

    QPushButton[navButton='true']:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(154, 116, 255, 0.24), stop:1 rgba(154, 116, 255, 0.11));
        border-color: rgba(184, 149, 255, 0.58);
        color: {c['primary_text']};
    }}

    QPushButton[navButton='true']:checked {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(154, 116, 255, 0.34), stop:1 rgba(154, 116, 255, 0.15));
        border-color: {c['border_active']};
        border-left: 2px solid rgba(208, 186, 255, 0.88);
        color: {c['primary_text']};
        padding-left: 18px;
    }}

    QPushButton[navButton='true']:pressed {{
        background: rgba(154, 116, 255, 0.22);
    }}

    QPushButton[navButton='true']:focus {{
        border-color: rgba(201, 179, 255, 0.78);
    }}

    QPushButton[navButton='true']:disabled {{
        color: rgba(193, 202, 228, 0.45);
        border-color: rgba(154, 116, 255, 0.08);
        background: rgba(255, 255, 255, 0.01);
    }}

    QWidget#TopStatusBar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(22, 31, 50, 0.98), stop:0.58 rgba(16, 24, 40, 0.98), stop:1 rgba(12, 19, 32, 0.98));
        border: 1px solid rgba(168, 136, 246, 0.20);
        border-top: 1px solid rgba(223, 206, 255, 0.30);
        border-bottom: 1px solid rgba(7, 11, 18, 0.78);
        border-radius: {r['xl']}px;
    }}

    QFrame[card='true'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(24, 34, 54, 0.97), stop:0.52 rgba(16, 24, 39, 0.98), stop:1 rgba(13, 20, 33, 0.99));
        border: 1px solid rgba(164, 132, 241, 0.14);
        border-top: 1px solid rgba(214, 196, 255, 0.22);
        border-bottom: 1px solid rgba(8, 12, 20, 0.72);
        border-radius: {r['xl']}px;
    }}

    QFrame[card='elevated'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(31, 44, 70, 0.98), stop:0.55 rgba(23, 33, 54, 0.98), stop:1 rgba(17, 24, 40, 0.98));
        border: 1px solid rgba(176, 145, 250, 0.24);
        border-top: 1px solid rgba(224, 207, 255, 0.34);
        border-bottom: 1px solid rgba(8, 12, 20, 0.84);
        border-radius: {r['xl']}px;
    }}

    QFrame#MetricCard {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(34, 48, 76, 0.98), stop:0.5 rgba(24, 35, 58, 0.98), stop:1 rgba(17, 25, 42, 0.99));
        border: 1px solid rgba(183, 151, 255, 0.28);
        border-top: 1px solid rgba(233, 218, 255, 0.42);
        border-bottom: 1px solid rgba(9, 13, 22, 0.88);
    }}

    QFrame#DashboardQuickActions,
    QFrame#DashboardAuditBlock,
    QFrame#DashboardRecommendationBlock,
    QFrame#AuditTimelineBlock,
    QFrame#AuditErrorsBlock,
    QFrame#UpdatesDiagnosticsBlock,
    QFrame#SettingsRuntimeBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(23, 33, 53, 0.97), stop:0.6 rgba(16, 24, 39, 0.98), stop:1 rgba(12, 19, 31, 0.99));
        border: 1px solid rgba(164, 131, 240, 0.16);
        border-top: 1px solid rgba(215, 197, 255, 0.24);
        border-bottom: 1px solid rgba(8, 12, 19, 0.72);
    }}

    QFrame#DashboardAuditBlock:hover,
    QFrame#DashboardRecommendationBlock:hover,
    QFrame#AuditTimelineBlock:hover,
    QFrame#AuditErrorsBlock:hover,
    QFrame#UpdatesDiagnosticsBlock:hover,
    QFrame#SettingsRuntimeBlock:hover {{
        border-color: rgba(186, 156, 255, 0.30);
    }}

    QFrame#AIRecommendationBlock,
    QFrame#AILearningBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(31, 43, 69, 0.98), stop:0.58 rgba(22, 32, 52, 0.98), stop:1 rgba(16, 24, 40, 0.99));
        border: 1px solid rgba(188, 158, 255, 0.28);
        border-top: 1px solid rgba(229, 211, 255, 0.38);
        border-bottom: 1px solid rgba(9, 13, 21, 0.82);
    }}

    QLabel#CardTitle {{
        color: rgba(202, 213, 241, 0.90);
        font-family: '{tokens.typography['label']}';
        font-size: 11px;
        font-weight: 560;
    }}

    QLabel#CardValue {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['metric']}';
        font-size: 31px;
        font-weight: 620;
        margin-top: 2px;
        margin-bottom: 1px;
    }}

    QLabel#CardMeta {{
        color: rgba(154, 165, 194, 0.95);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 500;
    }}

    QFrame#SessionFrame {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(36, 51, 82, 0.98), stop:1 rgba(24, 36, 60, 0.98));
        border: 1px solid rgba(190, 159, 255, 0.52);
        border-top: 1px solid rgba(232, 214, 255, 0.44);
        border-radius: {r['xl']}px;
    }}

    QLabel#SectionTitle {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['title']}';
        font-size: 17px;
        font-weight: 620;
    }}

    QLabel#SectionHint {{
        color: rgba(154, 166, 196, 0.96);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 470;
    }}

    QPushButton {{
        min-height: 38px;
        padding: 8px 14px;
        border-radius: 13px;
        border: 1px solid rgba(154, 116, 255, 0.20);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(35, 49, 77, 0.94), stop:1 rgba(21, 30, 49, 0.95));
        color: {c['primary_text']};
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 560;
    }}

    QPushButton:hover {{
        border-color: rgba(192, 167, 255, 0.62);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(153, 121, 235, 0.30), stop:1 rgba(118, 89, 196, 0.22));
    }}

    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(115, 88, 191, 0.34), stop:1 rgba(93, 68, 158, 0.28));
        border-color: rgba(181, 151, 255, 0.62);
        padding-top: 9px;
        padding-bottom: 7px;
    }}

    QPushButton:focus {{
        border-color: rgba(205, 186, 255, 0.78);
    }}

    QPushButton:disabled {{
        color: rgba(238, 242, 255, 0.46);
        border-color: rgba(154, 116, 255, 0.10);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(28, 35, 52, 0.70), stop:1 rgba(19, 24, 37, 0.74));
    }}

    QPushButton#PrimaryCTA {{
        border-color: rgba(201, 179, 255, 0.84);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(120, 88, 214, 0.96), stop:1 rgba(163, 126, 248, 0.96));
        color: #FCF9FF;
        font-family: '{tokens.typography['label']}';
        font-weight: 620;
    }}

    QPushButton#PrimaryCTA:hover {{
        border-color: rgba(212, 191, 255, 0.90);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(133, 99, 228, 0.98), stop:1 rgba(176, 139, 255, 0.98));
    }}

    QPushButton#PrimaryCTA:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(100, 73, 178, 0.98), stop:1 rgba(140, 108, 219, 0.98));
    }}

    QPushButton#SecondaryCTA {{
        border-color: rgba(154, 116, 255, 0.22);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(34, 47, 74, 0.94), stop:1 rgba(20, 29, 48, 0.94));
        color: {c['secondary_text']};
    }}

    QPushButton#SecondaryCTA:hover {{
        border-color: rgba(188, 160, 255, 0.62);
        color: {c['primary_text']};
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(70, 56, 108, 0.52), stop:1 rgba(45, 36, 77, 0.40));
    }}

    QPushButton#OutlineCTA {{
        border-color: rgba(172, 140, 255, 0.54);
        background: rgba(22, 30, 47, 0.42);
        color: #D8C8FF;
    }}

    QPushButton#OutlineCTA:hover {{
        border-color: rgba(202, 177, 255, 0.80);
        background: rgba(98, 74, 168, 0.24);
        color: #F4EDFF;
    }}

    QPushButton#DangerCTA {{
        border-color: rgba(255, 110, 138, 0.65);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(121, 50, 73, 0.35), stop:1 rgba(70, 31, 43, 0.32));
        color: {c['danger']};
    }}

    QPushButton#DangerCTA:hover {{
        border-color: rgba(255, 146, 170, 0.76);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(146, 64, 90, 0.42), stop:1 rgba(86, 38, 55, 0.36));
    }}

    QListWidget, QTableWidget, QTextEdit, QPlainTextEdit, QComboBox, QLineEdit {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(16, 24, 39, 0.98), stop:1 rgba(10, 16, 27, 0.98));
        border: 1px solid rgba(157, 124, 232, 0.14);
        border-top: 1px solid rgba(209, 190, 255, 0.22);
        border-radius: {r['md']}px;
        color: {c['primary_text']};
        selection-background-color: rgba(143, 109, 255, 0.25);
        selection-color: {c['primary_text']};
        padding: 4px;
    }}

    QListWidget::item, QTableWidget::item {{
        padding: 7px 8px;
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        color: rgba(232, 238, 255, 0.94);
    }}

    QListWidget::item:hover, QTableWidget::item:hover {{
        background: rgba(154, 116, 255, 0.14);
    }}

    QListWidget#DashboardAuditList,
    QListWidget#DashboardRecommendationList,
    QListWidget#AIRecommendationList,
    QListWidget#AIBundleList,
    QListWidget#AuditErrorsList {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(13, 20, 33, 0.98), stop:1 rgba(9, 14, 24, 0.98));
        border: 1px solid rgba(149, 116, 224, 0.12);
        border-top: 1px solid rgba(202, 183, 252, 0.20);
        padding: 6px;
    }}

    QTableWidget#AuditTimelineTable,
    QTextEdit#AILearningSummary {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(14, 21, 35, 0.98), stop:1 rgba(9, 14, 24, 0.98));
        border: 1px solid rgba(155, 121, 232, 0.14);
        border-top: 1px solid rgba(208, 188, 255, 0.24);
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QListWidget:focus, QTableWidget:focus {{
        border: 1px solid rgba(192, 167, 255, 0.74);
    }}

    QHeaderView::section {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1C2740, stop:1 #172034);
        color: rgba(208, 219, 246, 0.95);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        border: 0px;
        border-bottom: 1px solid rgba(154, 116, 255, 0.22);
        padding: 9px;
        font-weight: 560;
    }}

    QLabel[statusPill='true'] {{
        border-radius: 11px;
        padding: 5px 10px;
        font-size: 11px;
        font-family: '{tokens.typography['label']}';
        font-weight: 540;
        min-width: 98px;
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
        font-size: 16px;
        font-weight: 620;
    }}

    QWidget#ContextPanel {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(21, 31, 50, 0.98), stop:0.58 rgba(15, 23, 39, 0.98), stop:1 rgba(11, 18, 30, 0.99));
        border: 1px solid rgba(174, 144, 248, 0.22);
        border-top: 1px solid rgba(226, 209, 255, 0.36);
        border-bottom: 1px solid rgba(8, 12, 20, 0.82);
        border-radius: {r['xl']}px;
    }}

    QWidget#AIStudioPage QFrame[card='true'],
    QWidget#AIStudioPage QFrame[card='elevated'] {{
        border: 1px solid rgba(189, 158, 255, 0.30);
        border-top: 1px solid rgba(231, 214, 255, 0.42);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(31, 44, 72, 0.99), stop:0.58 rgba(23, 33, 54, 0.99), stop:1 rgba(17, 25, 42, 0.99));
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
