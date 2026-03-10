import csv
import json
import math
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "RPG-Трекер Жизни"
DATA_FILE = Path(__file__).with_name("life_rpg_quests.json")

STATUS_NOT_STARTED = "Не начат"
STATUS_IN_PROGRESS = "В процессе"
STATUS_COMPLETED = "Выполнен"

TYPE_VALUES = ["Основной", "Побочный", "Ежедневный", "Привычка"]
STAT_VALUES = ["Тело", "Разум", "Карьера", "Социум", "Дух"]

TYPE_ALIASES = {
    "main": "Основной",
    "side": "Побочный",
    "daily": "Ежедневный",
    "habit": "Привычка",
    "основной": "Основной",
    "побочный": "Побочный",
    "ежедневный": "Ежедневный",
    "привычка": "Привычка",
}

STAT_ALIASES = {
    "body": "Тело",
    "mind": "Разум",
    "career": "Карьера",
    "social": "Социум",
    "spirit": "Дух",
    "тело": "Тело",
    "разум": "Разум",
    "карьера": "Карьера",
    "социум": "Социум",
    "дух": "Дух",
}


class LifeRPGTrackerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.quests = []
        self.selected_quest_id = None

        self.title_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Ежедневный")
        self.stat_var = tk.StringVar(value="Тело")
        self.difficulty_var = tk.IntVar(value=1)
        self.base_xp_var = tk.IntVar(value=40)
        self.progress_var = tk.IntVar(value=0)
        self.reward_var = tk.StringVar()
        self.preview_var = tk.StringVar()

        self.total_xp_var = tk.StringVar(value="0")
        self.level_var = tk.StringVar(value="1")
        self.next_level_var = tk.StringVar(value="100")
        self.completed_var = tk.StringVar(value="0 / 0")

        self._configure_root()
        self._configure_styles()
        self._build_layout()
        self._load_quests()
        self._refresh_view()

        self.difficulty_var.trace_add("write", self._update_preview)
        self.base_xp_var.trace_add("write", self._update_preview)
        self.progress_var.trace_add("write", self._update_preview)
        self._update_preview()

    def _configure_root(self) -> None:
        self.root.title(APP_TITLE)
        self.root.geometry("1460x820")
        self.root.minsize(1180, 690)
        self.root.configure(bg="#0E1412")

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", font=("Segoe UI", 10))
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 19, "bold"),
            foreground="#DDF9CF",
            background="#0E1412",
        )
        style.configure("Subtitle.TLabel", foreground="#98B79C", background="#0E1412")
        style.configure("Card.TFrame", background="#15201A")
        style.configure("Card.TLabel", background="#15201A", foreground="#DFF7D5")
        style.configure("Panel.TLabelframe", background="#111916", foreground="#BFE4B1")
        style.configure(
            "Panel.TLabelframe.Label",
            background="#111916",
            foreground="#BFE4B1",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Segoe UI", 10),
            background="#121B17",
            foreground="#E8F7E1",
            fieldbackground="#121B17",
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#1F3327",
            foreground="#E8F7E1",
        )
        style.map("Treeview", background=[("selected", "#2D523A")], foreground=[("selected", "#F6FFF1")])

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=14, style="Card.TFrame")
        container.pack(fill="both", expand=True)

        hero = ttk.Frame(container, style="Card.TFrame")
        hero.pack(fill="x", pady=(0, 10))
        ttk.Label(hero, text="RPG-ТРЕКЕР ПРОГРЕССА", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            hero,
            text="Прокачивай реальную жизнь как RPG: квесты, XP, уровни и награды.",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        stats = ttk.Frame(container, style="Card.TFrame")
        stats.pack(fill="x", pady=(0, 10))
        self._build_stat_card(stats, "Всего XP", self.total_xp_var, 0)
        self._build_stat_card(stats, "Уровень", self.level_var, 1)
        self._build_stat_card(stats, "XP до следующего", self.next_level_var, 2)
        self._build_stat_card(stats, "Выполнено квестов", self.completed_var, 3)

        editor = ttk.LabelFrame(container, text="Редактор квестов", style="Panel.TLabelframe", padding=12)
        editor.pack(fill="x", pady=(0, 10))
        editor.columnconfigure(1, weight=2)
        editor.columnconfigure(3, weight=1)
        editor.columnconfigure(5, weight=1)
        editor.columnconfigure(7, weight=2)

        ttk.Label(editor, text="Квест").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(editor, textvariable=self.title_var).grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=4)

        ttk.Label(editor, text="Тип").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Combobox(
            editor,
            textvariable=self.type_var,
            values=TYPE_VALUES,
            state="readonly",
        ).grid(row=0, column=3, sticky="ew", padx=(0, 10), pady=4)

        ttk.Label(editor, text="Характеристика").grid(row=0, column=4, sticky="w", padx=(0, 6), pady=4)
        ttk.Combobox(
            editor,
            textvariable=self.stat_var,
            values=STAT_VALUES,
            state="readonly",
        ).grid(row=0, column=5, sticky="ew", padx=(0, 10), pady=4)

        ttk.Label(editor, text="Награда").grid(row=0, column=6, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(editor, textvariable=self.reward_var).grid(row=0, column=7, sticky="ew", pady=4)

        ttk.Label(editor, text="Сложность (1-5)").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=4)
        ttk.Spinbox(editor, from_=1, to=5, textvariable=self.difficulty_var, width=8).grid(
            row=1,
            column=1,
            sticky="w",
            pady=4,
        )

        ttk.Label(editor, text="Базовый XP").grid(row=1, column=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Spinbox(
            editor,
            from_=5,
            to=5000,
            increment=5,
            textvariable=self.base_xp_var,
            width=10,
        ).grid(row=1, column=3, sticky="w", pady=4)

        ttk.Label(editor, text="Прогресс %").grid(row=1, column=4, sticky="w", padx=(0, 6), pady=4)
        ttk.Spinbox(
            editor,
            from_=0,
            to=100,
            increment=5,
            textvariable=self.progress_var,
            width=10,
        ).grid(row=1, column=5, sticky="w", pady=4)

        ttk.Label(editor, textvariable=self.preview_var, foreground="#9FDFA0").grid(
            row=1,
            column=6,
            columnspan=2,
            sticky="w",
            pady=4,
        )

        actions = ttk.Frame(editor, style="Card.TFrame")
        actions.grid(row=2, column=0, columnspan=8, sticky="ew", pady=(10, 2))
        for col_idx in range(6):
            actions.columnconfigure(col_idx, weight=1)

        ttk.Button(actions, text="Добавить квест", command=self._add_quest).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6),
        )
        ttk.Button(actions, text="Обновить выбранный", command=self._update_quest).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 6),
        )
        ttk.Button(actions, text="Удалить выбранный", command=self._delete_selected).grid(
            row=0,
            column=2,
            sticky="ew",
            padx=(0, 6),
        )
        ttk.Button(actions, text="Очистить форму", command=self._clear_form).grid(
            row=0,
            column=3,
            sticky="ew",
            padx=(0, 6),
        )
        ttk.Button(actions, text="Сохранить", command=lambda: self._save_quests(show_message=True)).grid(
            row=0,
            column=4,
            sticky="ew",
            padx=(0, 6),
        )
        ttk.Button(actions, text="Экспорт CSV", command=self._export_csv).grid(row=0, column=5, sticky="ew")

        table_box = ttk.LabelFrame(container, text="Таблица квестов", style="Panel.TLabelframe", padding=10)
        table_box.pack(fill="both", expand=True)
        table_box.rowconfigure(0, weight=1)
        table_box.columnconfigure(0, weight=1)

        columns = (
            "id",
            "title",
            "type",
            "stat",
            "difficulty",
            "base_xp",
            "progress",
            "status",
            "earned_xp",
            "reward",
        )
        self.tree = ttk.Treeview(table_box, columns=columns, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        y_scroll = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        headings = {
            "id": ("ID", 90),
            "title": ("Квест", 275),
            "type": ("Тип", 115),
            "stat": ("Характеристика", 140),
            "difficulty": ("Сложн.", 80),
            "base_xp": ("Базовый XP", 100),
            "progress": ("Прогресс %", 100),
            "status": ("Статус", 120),
            "earned_xp": ("Получено XP", 110),
            "reward": ("Награда", 285),
        }
        for key, (label, width) in headings.items():
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, anchor="center")
        self.tree.column("title", anchor="w")
        self.tree.column("reward", anchor="w")

    def _build_stat_card(self, parent: ttk.Frame, title: str, value_var: tk.StringVar, column: int) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 0))
        parent.columnconfigure(column, weight=1)
        ttk.Label(card, text=title, style="Card.TLabel", foreground="#A8C7A5").pack(anchor="w")
        ttk.Label(
            card,
            textvariable=value_var,
            style="Card.TLabel",
            font=("Segoe UI", 18, "bold"),
            foreground="#D3FFD0",
        ).pack(anchor="w")

    def _default_quests(self) -> list[dict]:
        samples = [
            {
                "id": "Q-001",
                "title": "Тренировка 30 минут",
                "type": "Ежедневный",
                "stat": "Тело",
                "difficulty": 2,
                "base_xp": 40,
                "progress": 100,
                "reward": "+1 выносливость",
            },
            {
                "id": "Q-002",
                "title": "Прочитать 20 страниц",
                "type": "Ежедневный",
                "stat": "Разум",
                "difficulty": 1,
                "base_xp": 25,
                "progress": 60,
                "reward": "+1 знание",
            },
            {
                "id": "Q-003",
                "title": "Закрыть рабочую задачу",
                "type": "Побочный",
                "stat": "Карьера",
                "difficulty": 4,
                "base_xp": 120,
                "progress": 80,
                "reward": "+200 золота",
            },
            {
                "id": "Q-004",
                "title": "Пройти модуль курса",
                "type": "Основной",
                "stat": "Разум",
                "difficulty": 5,
                "base_xp": 300,
                "progress": 0,
                "reward": "Новый уровень",
            },
        ]
        return [self._normalize_quest(item) for item in samples]

    def _normalize_quest(self, raw: dict) -> dict:
        quest = {
            "id": str(raw.get("id", self._next_quest_id())),
            "title": str(raw.get("title", "Новый квест")).strip() or "Новый квест",
            "type": self._normalize_type(raw.get("type")),
            "stat": self._normalize_stat(raw.get("stat")),
            "difficulty": self._clamp_int(raw.get("difficulty", 1), 1, 5, 1),
            "base_xp": self._clamp_int(raw.get("base_xp", 20), 5, 5000, 20),
            "progress": self._clamp_int(raw.get("progress", 0), 0, 100, 0),
            "reward": str(raw.get("reward", "")).strip(),
        }
        quest["status"] = self._status_from_progress(quest["progress"])
        quest["earned_xp"] = self._earned_xp(
            quest["base_xp"],
            quest["difficulty"],
            quest["progress"],
            quest["status"],
        )
        return quest

    def _refresh_view(self) -> None:
        self._refresh_table()
        self._refresh_profile_stats()
        self._update_preview()

    def _refresh_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for quest in self.quests:
            quest["status"] = self._status_from_progress(quest["progress"])
            quest["earned_xp"] = self._earned_xp(
                quest["base_xp"],
                quest["difficulty"],
                quest["progress"],
                quest["status"],
            )
            self.tree.insert(
                "",
                "end",
                iid=quest["id"],
                values=(
                    quest["id"],
                    quest["title"],
                    quest["type"],
                    quest["stat"],
                    quest["difficulty"],
                    quest["base_xp"],
                    quest["progress"],
                    quest["status"],
                    quest["earned_xp"],
                    quest["reward"],
                ),
            )

    def _refresh_profile_stats(self) -> None:
        total_xp = sum(quest["earned_xp"] for quest in self.quests)
        completed = sum(1 for quest in self.quests if quest["status"] == STATUS_COMPLETED)
        level = int(math.sqrt(total_xp / 100)) + 1
        xp_to_next = max(0, (level * level * 100) - total_xp)

        self.total_xp_var.set(str(total_xp))
        self.level_var.set(str(level))
        self.next_level_var.set(str(xp_to_next))
        self.completed_var.set(f"{completed} / {len(self.quests)}")

    def _update_preview(self, *_args) -> None:
        base_xp = self._clamp_int(self.base_xp_var.get(), 5, 5000, 20)
        difficulty = self._clamp_int(self.difficulty_var.get(), 1, 5, 1)
        progress = self._clamp_int(self.progress_var.get(), 0, 100, 0)

        status = self._status_from_progress(progress)
        earned = self._earned_xp(base_xp, difficulty, progress, status)
        self.preview_var.set(f"Статус: {status} | Получено XP: {earned}")

    def _on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return

        quest_id = selected[0]
        quest = self._get_quest(quest_id)
        if quest is None:
            return

        self.selected_quest_id = quest_id
        self.title_var.set(quest["title"])
        self.type_var.set(quest["type"])
        self.stat_var.set(quest["stat"])
        self.difficulty_var.set(quest["difficulty"])
        self.base_xp_var.set(quest["base_xp"])
        self.progress_var.set(quest["progress"])
        self.reward_var.set(quest["reward"])
        self._update_preview()

    def _clear_form(self) -> None:
        self.selected_quest_id = None
        self.title_var.set("")
        self.type_var.set("Ежедневный")
        self.stat_var.set("Тело")
        self.difficulty_var.set(1)
        self.base_xp_var.set(40)
        self.progress_var.set(0)
        self.reward_var.set("")
        self.tree.selection_remove(*self.tree.selection())
        self._update_preview()

    def _build_quest_from_form(self, quest_id: str) -> dict:
        title = self.title_var.get().strip()
        if not title:
            raise ValueError("Введите название квеста.")

        quest = {
            "id": quest_id,
            "title": title,
            "type": self._normalize_type(self.type_var.get()),
            "stat": self._normalize_stat(self.stat_var.get()),
            "difficulty": self._clamp_int(self.difficulty_var.get(), 1, 5, 1),
            "base_xp": self._clamp_int(self.base_xp_var.get(), 5, 5000, 20),
            "progress": self._clamp_int(self.progress_var.get(), 0, 100, 0),
            "reward": self.reward_var.get().strip(),
        }
        quest["status"] = self._status_from_progress(quest["progress"])
        quest["earned_xp"] = self._earned_xp(
            quest["base_xp"],
            quest["difficulty"],
            quest["progress"],
            quest["status"],
        )
        return quest

    def _add_quest(self) -> None:
        try:
            quest = self._build_quest_from_form(self._next_quest_id())
        except ValueError as exc:
            messagebox.showwarning(APP_TITLE, str(exc))
            return

        self.quests.append(quest)
        self._save_quests(show_message=False)
        self._refresh_view()
        self._clear_form()

    def _update_quest(self) -> None:
        if not self.selected_quest_id:
            messagebox.showinfo(APP_TITLE, "Выберите квест в таблице для обновления.")
            return

        quest_index = next(
            (idx for idx, quest in enumerate(self.quests) if quest["id"] == self.selected_quest_id),
            None,
        )
        if quest_index is None:
            messagebox.showerror(APP_TITLE, "Квест не найден.")
            return

        try:
            self.quests[quest_index] = self._build_quest_from_form(self.selected_quest_id)
        except ValueError as exc:
            messagebox.showwarning(APP_TITLE, str(exc))
            return

        self._save_quests(show_message=False)
        self._refresh_view()

    def _delete_selected(self) -> None:
        if not self.selected_quest_id:
            messagebox.showinfo(APP_TITLE, "Выберите квест в таблице для удаления.")
            return

        self.quests = [quest for quest in self.quests if quest["id"] != self.selected_quest_id]
        self._save_quests(show_message=False)
        self._refresh_view()
        self._clear_form()

    def _save_quests(self, show_message: bool) -> None:
        payload = []
        for quest in self.quests:
            payload.append(
                {
                    "id": quest["id"],
                    "title": quest["title"],
                    "type": quest["type"],
                    "stat": quest["stat"],
                    "difficulty": quest["difficulty"],
                    "base_xp": quest["base_xp"],
                    "progress": quest["progress"],
                    "reward": quest["reward"],
                }
            )

        DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if show_message:
            messagebox.showinfo(APP_TITLE, f"Сохранено в {DATA_FILE.name}")

    def _load_quests(self) -> None:
        if not DATA_FILE.exists():
            self.quests = self._default_quests()
            self._save_quests(show_message=False)
            return

        try:
            raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("Некорректный формат данных.")
            self.quests = [self._normalize_quest(item) for item in raw if isinstance(item, dict)]
        except Exception:
            messagebox.showwarning(
                APP_TITLE,
                "Не удалось прочитать файл данных. Загружены стартовые квесты.",
            )
            self.quests = self._default_quests()
            self._save_quests(show_message=False)

    def _export_csv(self) -> None:
        default_name = "rpg_treker_export.csv"
        path = filedialog.asksaveasfilename(
            title="Экспорт CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")],
        )
        if not path:
            return

        headers = [
            "ID",
            "Квест",
            "Тип",
            "Характеристика",
            "Сложность",
            "Базовый XP",
            "Прогресс %",
            "Статус",
            "Получено XP",
            "Награда",
        ]
        with open(path, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            for quest in self.quests:
                writer.writerow(
                    [
                        quest["id"],
                        quest["title"],
                        quest["type"],
                        quest["stat"],
                        quest["difficulty"],
                        quest["base_xp"],
                        quest["progress"],
                        quest["status"],
                        quest["earned_xp"],
                        quest["reward"],
                    ]
                )

        messagebox.showinfo(APP_TITLE, "CSV экспортирован успешно.")

    def _next_quest_id(self) -> str:
        max_idx = 0
        for quest in self.quests:
            match = re.fullmatch(r"Q-(\d+)", quest.get("id", ""))
            if match:
                max_idx = max(max_idx, int(match.group(1)))
        return f"Q-{max_idx + 1:03d}"

    def _get_quest(self, quest_id: str) -> dict | None:
        return next((quest for quest in self.quests if quest["id"] == quest_id), None)

    @staticmethod
    def _normalize_type(value) -> str:
        key = str(value or "").strip().lower()
        return TYPE_ALIASES.get(key, "Ежедневный")

    @staticmethod
    def _normalize_stat(value) -> str:
        key = str(value or "").strip().lower()
        return STAT_ALIASES.get(key, "Тело")

    @staticmethod
    def _status_from_progress(progress: int) -> str:
        if progress <= 0:
            return STATUS_NOT_STARTED
        if progress >= 100:
            return STATUS_COMPLETED
        return STATUS_IN_PROGRESS

    @staticmethod
    def _earned_xp(base_xp: int, difficulty: int, progress: int, status: str) -> int:
        if status == STATUS_COMPLETED:
            return round(base_xp * (1 + difficulty / 10))
        return round(base_xp * (progress / 100))

    @staticmethod
    def _clamp_int(value, min_value: int, max_value: int, fallback: int) -> int:
        try:
            parsed = int(float(value))
        except (ValueError, TypeError, tk.TclError):
            parsed = fallback
        return max(min_value, min(max_value, parsed))


def main() -> None:
    root = tk.Tk()
    LifeRPGTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
