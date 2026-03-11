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
            "display": "Segoe UI Semibold",
            "title": "Segoe UI Semibold",
            "body": "Segoe UI",
            "label": "Segoe UI",
            "metric": "Segoe UI Semibold",
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
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(15, 23, 39, 0.98), stop:0.45 rgba(11, 18, 31, 0.98), stop:1 rgba(9, 15, 26, 0.98));
        border: 1px solid rgba(164, 132, 242, 0.14);
        border-right: 1px solid rgba(192, 162, 255, 0.24);
        border-top: 1px solid rgba(226, 210, 255, 0.22);
        border-top-left-radius: {r['lg']}px;
        border-bottom-left-radius: {r['lg']}px;
    }}

    QWidget#SidebarBrandBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(30, 43, 68, 0.72), stop:1 rgba(18, 28, 46, 0.70));
        border: 1px solid rgba(183, 150, 255, 0.20);
        border-top: 1px solid rgba(234, 217, 255, 0.30);
        border-radius: 17px;
    }}

    QLabel#SidebarEmblem {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(147, 114, 235, 0.92), stop:1 rgba(105, 80, 176, 0.92));
        color: #F9F4FF;
        border: 1px solid rgba(228, 210, 255, 0.55);
        border-radius: 21px;
        font-family: '{tokens.typography['display']}';
        font-size: 16px;
        font-weight: 640;
    }}

    QLabel#AppTitle {{
        font-family: '{tokens.typography['display']}';
        font-size: 18px;
        font-weight: 570;
        letter-spacing: 0.15px;
        color: {c['primary_text']};
    }}

    QLabel#AppSubtitle {{
        color: rgba(163, 175, 205, 0.95);
        font-size: 12px;
        font-family: '{tokens.typography['label']}';
        font-weight: 430;
        line-height: 1.35em;
    }}

    QLabel#SidebarRuntimeStatus {{
        color: rgba(162, 174, 204, 0.92);
        font-family: '{tokens.typography['label']}';
        font-size: 11px;
        font-weight: 500;
        padding: 8px 10px;
        border-radius: 12px;
        border: 1px solid rgba(170, 138, 245, 0.14);
        border-top: 1px solid rgba(214, 197, 255, 0.20);
        background: rgba(20, 30, 49, 0.68);
    }}

    QPushButton[navButton='true'] {{
        text-align: left;
        padding: 11px 13px 11px 15px;
        border-radius: 15px;
        border: 1px solid rgba(154, 116, 255, 0.09);
        border-top: 1px solid rgba(214, 196, 255, 0.11);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255,255,255,0.018), stop:1 rgba(255,255,255,0.00));
        color: rgba(199, 210, 237, 0.96);
        font-family: '{tokens.typography['label']}';
        font-size: 13px;
        font-weight: 500;
    }}

    QPushButton[navButton='true']:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(154, 116, 255, 0.28), stop:1 rgba(154, 116, 255, 0.12));
        border-color: rgba(196, 164, 255, 0.52);
        border-top: 1px solid rgba(230, 215, 255, 0.32);
        color: {c['primary_text']};
    }}

    QPushButton[navButton='true']:checked {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(161, 123, 246, 0.37), stop:0.55 rgba(146, 109, 231, 0.26), stop:1 rgba(120, 91, 196, 0.16));
        border-color: rgba(202, 173, 255, 0.66);
        border-top: 1px solid rgba(237, 223, 255, 0.40);
        border-left: 1px solid rgba(228, 208, 255, 0.82);
        color: {c['primary_text']};
        padding-left: 16px;
    }}

    QPushButton[navButton='true']:pressed {{
        background: rgba(154, 116, 255, 0.20);
    }}

    QPushButton[navButton='true']:focus {{
        border-color: rgba(214, 192, 255, 0.74);
    }}

    QPushButton[navButton='true']:disabled {{
        color: rgba(193, 202, 228, 0.45);
        border-color: rgba(154, 116, 255, 0.08);
        background: rgba(255, 255, 255, 0.01);
    }}

    QWidget#TopStatusBar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(24, 35, 56, 0.98), stop:0.52 rgba(17, 26, 43, 0.98), stop:1 rgba(13, 21, 35, 0.98));
        border: 1px solid rgba(176, 145, 250, 0.18);
        border-top: 1px solid rgba(230, 214, 255, 0.32);
        border-bottom: 1px solid rgba(7, 11, 18, 0.78);
        border-radius: {r['xl']}px;
    }}

    QWidget#TopStatusBar QPushButton#PrimaryCTA {{
        min-height: 36px;
        padding-left: 16px;
        padding-right: 16px;
    }}

    QWidget#WorkspaceStack {{
        background: transparent;
    }}

    QSplitter#MainWorkspaceSplit::handle,
    QSplitter#DashboardSplit::handle,
    QSplitter#AnalyticsSplit::handle,
    QSplitter#AIStudioSplit::handle {{
        background: rgba(145, 116, 220, 0.16);
        border-radius: 4px;
        margin: 8px 1px;
    }}

    QSplitter#MainWorkspaceSplit::handle:hover,
    QSplitter#DashboardSplit::handle:hover,
    QSplitter#AnalyticsSplit::handle:hover,
    QSplitter#AIStudioSplit::handle:hover {{
        background: rgba(182, 152, 255, 0.34);
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

    QFrame[cardHover='true'] {{
        border-color: rgba(184, 153, 255, 0.30);
        border-top: 1px solid rgba(233, 216, 255, 0.42);
    }}

    QFrame[cardPressed='true'] {{
        border-color: rgba(170, 140, 240, 0.24);
        border-top: 1px solid rgba(209, 189, 250, 0.30);
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
    QFrame#AuditActionBar,
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

    QWidget#DashboardPage QFrame#MetricCard[dashboardMetric='primary'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(39, 56, 88, 0.99), stop:0.54 rgba(27, 40, 65, 0.99), stop:1 rgba(18, 27, 45, 0.99));
        border: 1px solid rgba(196, 165, 255, 0.34);
        border-top: 1px solid rgba(240, 224, 255, 0.45);
    }}

    QWidget#DashboardPage QFrame#MetricCard[dashboardMetric='system'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(30, 43, 68, 0.98), stop:0.56 rgba(22, 32, 52, 0.98), stop:1 rgba(15, 22, 37, 0.99));
        border: 1px solid rgba(171, 140, 247, 0.22);
        border-top: 1px solid rgba(224, 206, 255, 0.34);
    }}

    QWidget#DashboardPage QFrame#DashboardQuickActions {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(29, 42, 67, 0.98), stop:0.52 rgba(20, 30, 49, 0.98), stop:1 rgba(13, 21, 35, 0.99));
        border: 1px solid rgba(190, 158, 255, 0.24);
        border-top: 1px solid rgba(234, 217, 255, 0.36);
    }}

    QLabel#DashboardRowCaption {{
        color: rgba(187, 199, 229, 0.95);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 520;
        letter-spacing: 0.2px;
        padding-left: 2px;
        margin-top: 2px;
    }}

    QFrame#DashboardQuickActions QPushButton[dashboardQuickButton='true'] {{
        min-height: 40px;
        border-radius: 14px;
    }}

    QWidget#DashboardPage QFrame#DashboardAuditBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(22, 32, 51, 0.98), stop:0.56 rgba(15, 24, 39, 0.98), stop:1 rgba(11, 18, 30, 0.99));
        border: 1px solid rgba(158, 128, 232, 0.16);
        border-top: 1px solid rgba(214, 197, 255, 0.24);
    }}

    QWidget#DashboardPage QFrame#DashboardRecommendationBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(34, 48, 77, 0.99), stop:0.56 rgba(24, 35, 58, 0.99), stop:1 rgba(16, 24, 40, 0.99));
        border: 1px solid rgba(194, 163, 255, 0.28);
        border-top: 1px solid rgba(236, 221, 255, 0.40);
    }}

    QFrame#DashboardAuditBlock:hover,
    QFrame#DashboardRecommendationBlock:hover,
    QFrame#AuditActionBar:hover,
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

    QWidget#ProfilesPage QFrame#MetricCard[profilesMetric='true'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(31, 44, 69, 0.98), stop:0.58 rgba(22, 32, 52, 0.98), stop:1 rgba(15, 22, 37, 0.99));
        border: 1px solid rgba(177, 145, 252, 0.24);
        border-top: 1px solid rgba(229, 211, 255, 0.34);
    }}

    QFrame#ProfilesQuickActionsBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(27, 40, 64, 0.98), stop:0.56 rgba(19, 29, 47, 0.98), stop:1 rgba(13, 21, 35, 0.99));
        border: 1px solid rgba(183, 151, 255, 0.22);
        border-top: 1px solid rgba(233, 216, 255, 0.34);
    }}

    QFrame#ProfilesQuickActionsBlock QPushButton[profilesQuickAction='true'] {{
        min-height: 40px;
        border-radius: 14px;
    }}

    QTableWidget#ProfilesTable {{
        border: 1px solid rgba(171, 139, 246, 0.20);
        border-top: 1px solid rgba(223, 205, 255, 0.30);
        gridline-color: rgba(141, 116, 214, 0.16);
    }}

    QTableWidget#ProfilesTable::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(156, 121, 242, 0.34), stop:1 rgba(125, 95, 204, 0.24));
        border: 1px solid rgba(204, 176, 255, 0.48);
        color: #F5EEFF;
    }}

    QFrame#SessionsControlBlock,
    QFrame#SessionsRegistryBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(24, 35, 56, 0.98), stop:0.56 rgba(17, 26, 43, 0.98), stop:1 rgba(12, 19, 31, 0.99));
        border: 1px solid rgba(172, 140, 248, 0.20);
        border-top: 1px solid rgba(223, 207, 255, 0.30);
    }}

    QFrame#SessionsWorkspaceBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(29, 43, 68, 0.99), stop:0.52 rgba(20, 31, 50, 0.99), stop:1 rgba(14, 22, 36, 0.99));
        border: 1px solid rgba(193, 162, 255, 0.28);
        border-top: 1px solid rgba(236, 221, 255, 0.40);
        border-bottom: 1px solid rgba(8, 12, 20, 0.78);
    }}

    QWidget#SessionsPage QFrame#MetricCard[sessionsMetric='true'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(34, 49, 77, 0.98), stop:0.56 rgba(24, 35, 57, 0.98), stop:1 rgba(16, 24, 40, 0.99));
        border: 1px solid rgba(184, 152, 255, 0.26);
        border-top: 1px solid rgba(233, 216, 255, 0.38);
    }}

    QListWidget#SessionsList::item {{
        padding: 11px 12px;
        border-radius: 12px;
        margin-bottom: 6px;
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(168, 136, 244, 0.08);
    }}

    QListWidget#SessionsList::item:hover {{
        border: 1px solid rgba(191, 161, 255, 0.36);
        background: rgba(154, 116, 255, 0.14);
    }}

    QListWidget#SessionsList::item:selected {{
        border: 1px solid rgba(204, 176, 255, 0.46);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(154, 116, 255, 0.22), stop:1 rgba(116, 90, 191, 0.14));
    }}

    QLabel#SessionMobilePreview {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(20, 31, 50, 0.985), stop:0.52 rgba(14, 22, 36, 0.985), stop:1 rgba(10, 17, 28, 0.985));
        border: 1px solid rgba(199, 170, 255, 0.58);
        border-top: 1px solid rgba(240, 226, 255, 0.60);
        border-radius: 28px;
        color: rgba(228, 237, 255, 0.96);
        font-family: '{tokens.typography['label']}';
        font-size: 13px;
        font-weight: 520;
        letter-spacing: 0.12px;
        padding: 18px;
        line-height: 1.42em;
    }}

    QLabel[sessionChip='true'] {{
        border-radius: 11px;
        padding: 5px 10px;
        min-height: 28px;
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 520;
        color: rgba(231, 238, 255, 0.96);
        border: 1px solid rgba(178, 147, 252, 0.28);
        border-top: 1px solid rgba(226, 210, 255, 0.34);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(39, 55, 86, 0.58), stop:1 rgba(24, 35, 56, 0.54));
    }}

    QLabel[sessionChipLevel='ok'] {{
        border-color: rgba(103, 230, 183, 0.42);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(43, 99, 82, 0.46), stop:1 rgba(28, 66, 54, 0.40));
    }}

    QLabel[sessionChipLevel='warn'] {{
        border-color: rgba(255, 195, 116, 0.46);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(112, 84, 38, 0.42), stop:1 rgba(82, 60, 26, 0.36));
    }}

    QLabel[sessionChipLevel='info'] {{
        border-color: rgba(146, 215, 255, 0.44);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(47, 92, 123, 0.42), stop:1 rgba(32, 66, 91, 0.36));
    }}

    QWidget#SessionContextBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(34, 48, 76, 0.42), stop:1 rgba(20, 30, 49, 0.38));
        border: 1px solid rgba(182, 151, 255, 0.20);
        border-top: 1px solid rgba(227, 210, 255, 0.26);
        border-radius: 13px;
    }}

    QLabel#SessionContextHint {{
        color: rgba(210, 222, 248, 0.95);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 480;
        line-height: 1.38em;
    }}

    QLabel#SessionNextStep {{
        color: rgba(225, 233, 255, 0.97);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 520;
        line-height: 1.4em;
    }}

    QWidget#AnalyticsPage QFrame#MetricCard[analyticsMetric='true'] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(35, 49, 76, 0.99), stop:0.55 rgba(24, 35, 57, 0.99), stop:1 rgba(17, 25, 41, 0.99));
        border: 1px solid rgba(187, 155, 255, 0.28);
        border-top: 1px solid rgba(236, 220, 255, 0.40);
    }}

    QFrame#AnalyticsTopWeakBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(23, 34, 54, 0.98), stop:0.56 rgba(16, 24, 39, 0.98), stop:1 rgba(12, 19, 31, 0.99));
        border: 1px solid rgba(165, 133, 240, 0.18);
        border-top: 1px solid rgba(216, 199, 255, 0.28);
    }}

    QFrame#AnalyticsInsightsBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(31, 44, 70, 0.99), stop:0.56 rgba(22, 32, 53, 0.99), stop:1 rgba(15, 23, 39, 0.99));
        border: 1px solid rgba(188, 157, 255, 0.26);
        border-top: 1px solid rgba(234, 217, 255, 0.38);
    }}

    QFrame#AnalyticsStoryBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(34, 49, 78, 0.99), stop:0.52 rgba(24, 35, 58, 0.99), stop:1 rgba(17, 25, 41, 0.99));
        border: 1px solid rgba(197, 166, 255, 0.30);
        border-top: 1px solid rgba(239, 225, 255, 0.42);
    }}

    QLabel#AnalyticsStoryHeadline {{
        color: rgba(237, 243, 255, 0.98);
        font-family: '{tokens.typography['title']}';
        font-size: 15px;
        font-weight: 560;
        line-height: 1.38em;
    }}

    QLabel#AnalyticsStorySubline {{
        color: rgba(185, 198, 229, 0.96);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 450;
        line-height: 1.42em;
    }}

    QLabel[analyticsCue='true'] {{
        border-radius: 11px;
        padding: 5px 11px;
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 520;
        color: rgba(230, 238, 255, 0.97);
        border: 1px solid rgba(181, 150, 255, 0.30);
        border-top: 1px solid rgba(228, 212, 255, 0.38);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(38, 55, 86, 0.56), stop:1 rgba(24, 36, 58, 0.50));
    }}

    QLabel[analyticsCueLevel='ok'] {{
        border-color: rgba(104, 231, 184, 0.42);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(45, 103, 85, 0.44), stop:1 rgba(29, 67, 55, 0.38));
    }}

    QLabel[analyticsCueLevel='warn'] {{
        border-color: rgba(255, 194, 115, 0.45);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(111, 84, 38, 0.42), stop:1 rgba(81, 60, 27, 0.36));
    }}

    QLabel[analyticsCueLevel='danger'] {{
        border-color: rgba(255, 140, 170, 0.44);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(111, 44, 63, 0.40), stop:1 rgba(80, 32, 46, 0.34));
    }}

    QLabel[analyticsCueLevel='info'] {{
        border-color: rgba(150, 217, 255, 0.44);
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(48, 93, 124, 0.40), stop:1 rgba(33, 66, 91, 0.34));
    }}

    QListWidget#AnalyticsTopList::item,
    QListWidget#AnalyticsWeakList::item,
    QListWidget#AnalyticsPatternsList::item,
    QListWidget#AnalyticsRecommendationList::item {{
        padding: 10px 11px;
        border-radius: 11px;
        margin-bottom: 4px;
        border: 1px solid transparent;
    }}

    QListWidget#AnalyticsTopList::item {{
        background: rgba(154, 116, 255, 0.10);
    }}

    QListWidget#AnalyticsWeakList::item {{
        background: rgba(255, 184, 92, 0.09);
    }}

    QListWidget#AnalyticsPatternsList::item {{
        background: rgba(104, 199, 255, 0.08);
    }}

    QListWidget#AnalyticsRecommendationList::item {{
        background: rgba(154, 116, 255, 0.10);
    }}

    QListWidget#AnalyticsTopList::item:hover,
    QListWidget#AnalyticsWeakList::item:hover,
    QListWidget#AnalyticsPatternsList::item:hover,
    QListWidget#AnalyticsRecommendationList::item:hover {{
        border: 1px solid rgba(190, 159, 255, 0.34);
    }}

    QTextEdit#AnalyticsPlanText {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(14, 21, 35, 0.99), stop:1 rgba(10, 15, 26, 0.99));
        border: 1px solid rgba(167, 134, 242, 0.18);
        border-top: 1px solid rgba(220, 203, 255, 0.28);
    }}

    QWidget#AIStudioPage QFrame#AIActionBlock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(34, 48, 76, 0.99), stop:0.56 rgba(24, 35, 58, 0.99), stop:1 rgba(16, 24, 41, 0.99));
        border: 1px solid rgba(195, 164, 255, 0.30);
        border-top: 1px solid rgba(237, 222, 255, 0.44);
    }}

    QWidget#AIStudioPage QFrame#MetricCard[aiMetric='true'] {{
        border: 1px solid rgba(197, 166, 255, 0.32);
        border-top: 1px solid rgba(238, 223, 255, 0.44);
    }}

    QWidget#DashboardPage QWidget#DashboardOverviewHeader QLabel#SectionTitle,
    QWidget#DashboardPage QWidget#DashboardQuickHeader QLabel#SectionTitle,
    QWidget#DashboardPage QWidget#DashboardAuditHeader QLabel#SectionTitle,
    QWidget#DashboardPage QWidget#DashboardRecommendationHeader QLabel#SectionTitle {{
        font-size: 16px;
        font-weight: 570;
    }}

    QWidget#DashboardPage QWidget#DashboardOverviewHeader QLabel#SectionHint,
    QWidget#DashboardPage QWidget#DashboardQuickHeader QLabel#SectionHint,
    QWidget#DashboardPage QWidget#DashboardAuditHeader QLabel#SectionHint,
    QWidget#DashboardPage QWidget#DashboardRecommendationHeader QLabel#SectionHint {{
        color: rgba(170, 182, 212, 0.95);
    }}

    QLabel#CardTitle {{
        color: rgba(202, 213, 241, 0.90);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 530;
        letter-spacing: 0.15px;
    }}

    QLabel#CardValue {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['metric']}';
        font-size: 30px;
        font-weight: 560;
        letter-spacing: 0.15px;
        margin-top: 2px;
        margin-bottom: 2px;
    }}

    QLabel#CardMeta {{
        color: rgba(154, 165, 194, 0.95);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 470;
        line-height: 1.35em;
    }}

    QFrame#SessionFrame {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(42, 58, 90, 0.985), stop:0.52 rgba(30, 44, 72, 0.985), stop:1 rgba(22, 34, 56, 0.99));
        border: 1px solid rgba(200, 171, 255, 0.56);
        border-top: 1px solid rgba(242, 228, 255, 0.62);
        border-bottom: 1px solid rgba(9, 14, 23, 0.88);
        border-radius: {r['xl']}px;
    }}

    QLabel#SectionTitle {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['title']}';
        font-size: 16px;
        font-weight: 560;
        letter-spacing: 0.1px;
    }}

    QLabel#SectionHint {{
        color: rgba(154, 166, 196, 0.96);
        font-family: '{tokens.typography['label']}';
        font-size: 13px;
        font-weight: 430;
        line-height: 1.4em;
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
        font-size: 13px;
        font-weight: 520;
    }}

    QPushButton[motionButton='true'] {{
        border-color: rgba(162, 129, 237, 0.22);
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
        font-weight: 580;
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

    QListWidget#DashboardAuditList::item,
    QListWidget#DashboardRecommendationList::item {{
        padding: 10px 11px;
        border-radius: 11px;
        margin-bottom: 4px;
        border: 1px solid transparent;
    }}

    QListWidget#DashboardAuditList::item {{
        background: rgba(255, 255, 255, 0.012);
    }}

    QListWidget#DashboardRecommendationList::item {{
        background: rgba(154, 116, 255, 0.08);
    }}

    QListWidget#DashboardAuditList::item:hover {{
        border: 1px solid rgba(164, 131, 240, 0.28);
        background: rgba(154, 116, 255, 0.11);
    }}

    QListWidget#DashboardRecommendationList::item:hover {{
        border: 1px solid rgba(195, 164, 255, 0.34);
        background: rgba(154, 116, 255, 0.16);
    }}

    QListWidget#AIRecommendationList::item,
    QListWidget#AIBundleList::item {{
        padding: 10px 11px;
        border-radius: 11px;
        margin-bottom: 4px;
        border: 1px solid transparent;
    }}

    QListWidget#AIRecommendationList::item {{
        background: rgba(154, 116, 255, 0.14);
    }}

    QListWidget#AIBundleList::item {{
        background: rgba(104, 199, 255, 0.09);
    }}

    QListWidget#AIRecommendationList::item:hover,
    QListWidget#AIBundleList::item:hover {{
        border: 1px solid rgba(201, 171, 255, 0.38);
        background: rgba(154, 116, 255, 0.18);
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
        border-radius: 12px;
        padding: 6px 12px;
        font-size: 12px;
        font-family: '{tokens.typography['label']}';
        font-weight: 520;
        min-width: 96px;
        border: 1px solid rgba(174, 143, 247, 0.14);
        border-top: 1px solid rgba(223, 207, 255, 0.22);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(30, 41, 66, 0.62), stop:1 rgba(18, 26, 43, 0.62));
    }}

    QLabel[statusLevel='ok'] {{
        color: #8CE5C9;
        border-color: rgba(78, 221, 173, 0.34);
        border-top: 1px solid rgba(173, 255, 225, 0.34);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(36, 97, 79, 0.32), stop:1 rgba(26, 68, 56, 0.24));
    }}

    QLabel[statusLevel='warn'] {{
        color: #FFD08B;
        border-color: rgba(255, 192, 110, 0.35);
        border-top: 1px solid rgba(255, 223, 170, 0.34);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(109, 80, 33, 0.30), stop:1 rgba(79, 57, 22, 0.22));
    }}

    QLabel[statusLevel='danger'] {{
        color: #FFA0B5;
        border-color: rgba(255, 135, 163, 0.36);
        border-top: 1px solid rgba(255, 198, 214, 0.34);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(112, 45, 62, 0.30), stop:1 rgba(82, 32, 46, 0.22));
    }}

    QLabel[statusLevel='info'] {{
        color: #8EDBFF;
        border-color: rgba(132, 210, 255, 0.35);
        border-top: 1px solid rgba(203, 237, 255, 0.35);
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(42, 86, 116, 0.30), stop:1 rgba(29, 63, 86, 0.22));
    }}

    QLabel#ContextPanelTitle {{
        color: {c['primary_text']};
        font-family: '{tokens.typography['title']}';
        font-size: 16px;
        font-weight: 580;
    }}

    QWidget#ContextPanel {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(21, 31, 50, 0.98), stop:0.58 rgba(15, 23, 39, 0.98), stop:1 rgba(11, 18, 30, 0.99));
        border: 1px solid rgba(174, 144, 248, 0.22);
        border-top: 1px solid rgba(226, 209, 255, 0.36);
        border-bottom: 1px solid rgba(8, 12, 20, 0.82);
        border-radius: {r['xl']}px;
    }}

    QLabel#ContextActionCaption {{
        color: rgba(194, 206, 236, 0.95);
        font-family: '{tokens.typography['label']}';
        font-size: 12px;
        font-weight: 520;
        letter-spacing: 0.18px;
        padding-left: 2px;
    }}

    QWidget#ContextActionDock {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(31, 44, 70, 0.46), stop:1 rgba(17, 26, 43, 0.42));
        border: 1px solid rgba(180, 149, 255, 0.24);
        border-top: 1px solid rgba(228, 211, 255, 0.30);
        border-radius: 14px;
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
