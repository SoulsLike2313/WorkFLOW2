import os
import threading
import time
import tkinter as tk
from tkinter import messagebox

import pygame


CALM_TRACK = "calm.mp3"
FAST_TRACK = "fast.mp3"
THRESHOLD = 150


def calculate_area(length: float, width: float) -> float:
    return length * width


class AreaApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Cortex Area Analyzer")
        self.root.geometry("780x500")
        self.root.minsize(700, 450)
        self.root.configure(bg="#070b07")

        self.length_var = tk.StringVar(value="12")
        self.width_var = tk.StringVar(value="14")
        self.area_var = tk.StringVar(value="0")
        self.mode_var = tk.StringVar(value="Режим: ожидание")
        self.track_var = tk.StringVar(value="Трек: -")

        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg="#070b07")
        header.pack(fill="x", padx=24, pady=(20, 8))

        title = tk.Label(
            header,
            text="CORTEX STYLE AREA UI",
            font=("Segoe UI Black", 24),
            fg="#78ff00",
            bg="#070b07",
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Расчёт площади + авто-плей музыки 3 сек по порогу",
            font=("Segoe UI", 10),
            fg="#8ca18c",
            bg="#070b07",
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        neon_line = tk.Frame(self.root, bg="#39ff14", height=2)
        neon_line.pack(fill="x", padx=24, pady=(0, 16))

        body = tk.Frame(self.root, bg="#070b07")
        body.pack(fill="both", expand=True, padx=24, pady=8)

        input_card = tk.Frame(
            body,
            bg="#0f160f",
            highlightbackground="#2cff2c",
            highlightthickness=1,
            bd=0,
        )
        input_card.pack(fill="x", ipady=8)

        tk.Label(
            input_card,
            text="Параметры прямоугольника",
            font=("Segoe UI Semibold", 13),
            fg="#ddffdd",
            bg="#0f160f",
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 10))

        tk.Label(
            input_card,
            text="Длина",
            font=("Segoe UI", 11),
            fg="#9fb89f",
            bg="#0f160f",
        ).grid(row=1, column=0, sticky="w", padx=(16, 8), pady=(0, 12))
        tk.Entry(
            input_card,
            textvariable=self.length_var,
            font=("Consolas", 13),
            bg="#050805",
            fg="#7dff4b",
            insertbackground="#7dff4b",
            relief="flat",
            width=12,
        ).grid(row=1, column=1, sticky="w", padx=(0, 24), pady=(0, 12))

        tk.Label(
            input_card,
            text="Ширина",
            font=("Segoe UI", 11),
            fg="#9fb89f",
            bg="#0f160f",
        ).grid(row=1, column=2, sticky="w", padx=(0, 8), pady=(0, 12))
        tk.Entry(
            input_card,
            textvariable=self.width_var,
            font=("Consolas", 13),
            bg="#050805",
            fg="#7dff4b",
            insertbackground="#7dff4b",
            relief="flat",
            width=12,
        ).grid(row=1, column=3, sticky="w", padx=(0, 16), pady=(0, 12))

        action_bar = tk.Frame(body, bg="#070b07")
        action_bar.pack(fill="x", pady=14)

        calc_btn = tk.Button(
            action_bar,
            text="РАССЧИТАТЬ И ВОСПРОИЗВЕСТИ",
            command=self.on_calculate_click,
            font=("Segoe UI Semibold", 11),
            bg="#2cff2c",
            fg="#001a00",
            activebackground="#80ff80",
            activeforeground="#002000",
            relief="flat",
            padx=16,
            pady=9,
            cursor="hand2",
        )
        calc_btn.pack(anchor="w")

        result_card = tk.Frame(
            body,
            bg="#0f160f",
            highlightbackground="#1d901d",
            highlightthickness=1,
            bd=0,
        )
        result_card.pack(fill="x", ipady=10)

        tk.Label(
            result_card,
            text="Результат",
            font=("Segoe UI Semibold", 13),
            fg="#ddffdd",
            bg="#0f160f",
        ).pack(anchor="w", padx=16, pady=(10, 8))

        self.area_label = tk.Label(
            result_card,
            textvariable=self.area_var,
            font=("Consolas", 34, "bold"),
            fg="#7dff4b",
            bg="#0f160f",
        )
        self.area_label.pack(anchor="w", padx=16)

        tk.Label(
            result_card,
            textvariable=self.mode_var,
            font=("Segoe UI", 11),
            fg="#98b998",
            bg="#0f160f",
        ).pack(anchor="w", padx=16, pady=(8, 2))

        tk.Label(
            result_card,
            textvariable=self.track_var,
            font=("Segoe UI", 11),
            fg="#98b998",
            bg="#0f160f",
        ).pack(anchor="w", padx=16, pady=(0, 10))

    def on_calculate_click(self) -> None:
        try:
            length = float(self.length_var.get().replace(",", "."))
            width = float(self.width_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ошибка", "Введи корректные числа для длины и ширины.")
            return

        if length < 0 or width < 0:
            messagebox.showerror("Ошибка", "Длина и ширина не могут быть отрицательными.")
            return

        area = calculate_area(length, width)
        self.area_var.set(f"{area:.2f}")

        if area > THRESHOLD:
            self.mode_var.set(f"Режим: Calm (площадь > {THRESHOLD})")
            self.track_var.set(f"Трек: {CALM_TRACK}")
            self.area_label.configure(fg="#5df18f")
            self._play_track_async(CALM_TRACK)
        else:
            self.mode_var.set(f"Режим: Fast (площадь <= {THRESHOLD})")
            self.track_var.set(f"Трек: {FAST_TRACK}")
            self.area_label.configure(fg="#ffb347")
            self._play_track_async(FAST_TRACK)

    def _play_track_async(self, track_path: str) -> None:
        thread = threading.Thread(target=self._play_track_for_3_seconds, args=(track_path,), daemon=True)
        thread.start()

    @staticmethod
    def _play_track_for_3_seconds(track_path: str) -> None:
        if not os.path.exists(track_path):
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            time.sleep(3)
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        finally:
            try:
                pygame.mixer.quit()
            except pygame.error:
                pass


def main() -> None:
    root = tk.Tk()
    AreaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
