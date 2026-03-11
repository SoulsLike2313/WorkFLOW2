from __future__ import annotations

from typing import Dict, Iterable, Tuple


PREMIUM_PALETTE: Dict[str, str] = {
    "bg": "#130B24",
    "card": "#1C1235",
    "card_alt": "#281A46",
    "text": "#FFF4DE",
    "muted": "#F8DFA7",
    "accent": "#FFD24A",
    "accent_hover": "#FFE17A",
    "accent_deep": "#E7A81A",
    "danger": "#FF8A58",
    "danger_hover": "#FFA476",
    "soft": "#342353",
    "border": "#FF9B2A",
    "tab": "#341D58",
    "tab_active": "#63359B",
    "hero_left": "#5620A0",
    "hero_right": "#8F35DF",
}

THEME_FONTS: Dict[str, str] = {
    "title": "Segoe Script",
    "body": "Segoe UI Semibold",
}


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def mix_hex(start_hex: str, end_hex: str, t: float) -> str:
    start = hex_to_rgb(start_hex)
    end = hex_to_rgb(end_hex)
    mixed = tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))
    return rgb_to_hex(mixed)


def premium_glow_colors() -> Iterable[str]:
    return (
        "#6B3FB2",
        "#7A45C4",
        "#8A4CD4",
        "#A95AE8",
        "#C569FF",
        "#D684FF",
        "#E79BFF",
        "#FFCF6A",
        "#FFB848",
    )


def setup_styles(style, palette: Dict[str, str], title_font: str, body_font: str) -> None:
    button_font = body_font or title_font
    style.theme_use("clam")
    style.configure("Root.TFrame", background=palette["bg"])
    style.configure("Card.TFrame", background=palette["card"])
    style.configure("Panel.TFrame", background=palette["card_alt"])

    style.configure(
        "Title.TLabel",
        background=palette["hero_left"],
        foreground=palette["text"],
        font=(title_font, 28),
    )
    style.configure(
        "Sub.TLabel",
        background=palette["card"],
        foreground=palette["muted"],
        font=(body_font, 12),
    )
    style.configure(
        "PanelLabel.TLabel",
        background=palette["card_alt"],
        foreground=palette["muted"],
        font=(body_font, 12),
    )
    style.configure(
        "Status.TLabel",
        background=palette["soft"],
        foreground=palette["text"],
        font=(body_font, 12),
        padding=(14, 11),
        borderwidth=1,
        relief="solid",
        bordercolor=palette["border"],
    )
    style.configure(
        "HeroStatus.TLabel",
        background=mix_hex(palette["tab_active"], palette["hero_right"], 0.45),
        foreground="#FFF8E8",
        font=(body_font, 13),
        padding=(16, 14),
        borderwidth=1,
        relief="solid",
        bordercolor=palette["border"],
    )

    style.configure(
        "Primary.TButton",
        font=(button_font, 12),
        padding=(18, 12),
        borderwidth=2,
        relief="solid",
        foreground="#28130A",
        background=palette["accent"],
        bordercolor=palette["border"],
        lightcolor=palette["border"],
        darkcolor=palette["accent_deep"],
        focuscolor=palette["border"],
    )
    style.map(
        "Primary.TButton",
        background=[("active", palette["accent_hover"]), ("pressed", palette["accent_deep"])],
        bordercolor=[("active", "#FFC45B"), ("pressed", palette["border"])],
        foreground=[("disabled", "#A88A3E")],
    )

    style.configure(
        "Soft.TButton",
        font=(button_font, 12),
        padding=(18, 12),
        borderwidth=2,
        foreground=palette["text"],
        background=palette["card_alt"],
        bordercolor=palette["border"],
        relief="solid",
        lightcolor=palette["border"],
        darkcolor=palette["tab_active"],
        focuscolor=palette["border"],
    )
    style.map(
        "Soft.TButton",
        background=[("active", palette["tab_active"])],
        bordercolor=[("active", "#FFC45B"), ("pressed", palette["border"])],
    )

    style.configure(
        "Danger.TButton",
        font=(button_font, 12),
        padding=(18, 12),
        borderwidth=2,
        foreground="#FFF6F2",
        background=palette["danger"],
        bordercolor=palette["border"],
        relief="solid",
        lightcolor=palette["border"],
        darkcolor="#B95A22",
        focuscolor=palette["border"],
    )
    style.map(
        "Danger.TButton",
        background=[("active", palette["danger_hover"])],
        bordercolor=[("active", "#FFC45B"), ("pressed", palette["border"])],
    )

    style.configure(
        "Futuristic.TCheckbutton",
        background=palette["card_alt"],
        foreground=palette["text"],
        font=(body_font, 12),
        indicatorcolor=palette["accent"],
    )
    style.map(
        "Futuristic.TCheckbutton",
        background=[("active", palette["card_alt"])],
        indicatorcolor=[("selected", palette["accent"]), ("!selected", palette["card_alt"])],
    )

    style.configure(
        "Futuristic.TNotebook",
        background=palette["card"],
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "Futuristic.TNotebook.Tab",
        background=palette["tab"],
        foreground=palette["muted"],
        padding=(22, 12),
        font=(body_font, 12),
        borderwidth=0,
    )
    style.map(
        "Futuristic.TNotebook.Tab",
        background=[("selected", palette["tab_active"]), ("active", palette["tab_active"])],
        foreground=[("selected", palette["text"]), ("active", palette["text"])],
    )

    style.configure(
        "Custom.Treeview",
        font=(body_font, 12),
        rowheight=44,
        background=palette["card_alt"],
        fieldbackground=palette["card_alt"],
        foreground=palette["text"],
        borderwidth=1,
        relief="solid",
        bordercolor=palette["border"],
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", "#6A3DB0")],
        foreground=[("selected", "#FFF7E8")],
    )
    style.configure(
        "Custom.Treeview.Heading",
        font=(body_font, 12),
        foreground=palette["text"],
        background=palette["tab"],
        relief="solid",
        padding=(10, 10),
        borderwidth=1,
        bordercolor=palette["border"],
    )


def paint_hero_gradient(
    canvas,
    palette: Dict[str, str],
    title_font: str,
    body_font: str,
    title_text: str = "Voice Launcher",
) -> None:
    canvas.delete("all")
    width = max(1, canvas.winfo_width())
    height = max(1, canvas.winfo_height())
    steps = max(80, width // 3)
    for i in range(steps):
        t = i / max(1, steps - 1)
        color = mix_hex(palette["hero_left"], palette["hero_right"], t)
        x0 = int((i / steps) * width)
        x1 = int(((i + 1) / steps) * width)
        canvas.create_rectangle(x0, 0, x1, height, outline="", fill=color)

    canvas.create_line(0, height - 2, width, height - 2, fill="#FFC34A", width=2)
    canvas.create_line(0, 1, width, 1, fill="#FFE4A8", width=1)
    canvas.create_oval(width - 180, -120, width + 100, 140, outline="", fill="#FFB431")
    canvas.create_oval(width - 230, -80, width + 70, 160, outline="", fill="#D96AFF")

    canvas.create_text(
        28,
        34,
        anchor="w",
        text=title_text,
        fill=palette["text"],
        font=(title_font, 30),
    )
    canvas.create_text(
        30,
        74,
        anchor="w",
        text="Premium Neon Flow • Быстрый, точный и красивый голосовой запуск",
        fill="#FFEFC5",
        font=(body_font, 13),
    )
