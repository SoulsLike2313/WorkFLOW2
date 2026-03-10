import json
import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, ttk


LOOP_RE = re.compile(
    r"loop=(?P<loop>\d+)\s+equity=(?P<equity>-?\d+(?:\.\d+)?)\s+target=(?P<target>-?\d+(?:\.\d+)?)\s+cash=(?P<cash>-?\d+(?:\.\d+)?)\s+positions=(?P<positions>\d+)"
)
BUY_RE = re.compile(
    r"BUY\s+(?P<symbol>[A-Z0-9.\-]+)\s+qty=(?P<qty>\d+(?:\.\d+)?)\s+price=(?P<price>\d+(?:\.\d+)?)\s+strategy=(?P<strategy>[A-Z_]+)"
)
SELL_RE = re.compile(
    r"SELL\s+(?P<symbol>[A-Z0-9.\-]+)\s+qty=(?P<qty>\d+(?:\.\d+)?)\s+price=(?P<price>\d+(?:\.\d+)?)\s+reason=(?P<reason>[a-z_]+)\s+pnl=(?P<pnl>-?\d+(?:\.\d+)?)"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_SCRIPT = os.path.join(BASE_DIR, "adaptive_trading_bot.py")
PROFILE_FILE = os.path.join(BASE_DIR, "bot_profiles_easy.json")
WALLET_FILE = os.path.join(BASE_DIR, "demo_wallet.json")

STRATEGY_OPTIONS = {
    "Авто (лучший вариант)": "AUTO",
    "Только SMA": "SMA_CROSS",
    "Только RSI": "RSI_REVERSION",
    "Только MACD": "MACD_CROSS",
    "Только Breakout": "BREAKOUT",
}

DEFAULT_PROFILES = {
    "Быстрый демо 70-75 (Recommended)": {
        "mode": "demo",
        "symbols": "AAPL MSFT NVDA",
        "interval": "5m",
        "target_capital": 100.0,
        "required_win_min": 70.0,
        "required_win_max": 75.0,
        "strategy": "AUTO",
        "lookback_bars": 600,
        "poll_seconds": 30,
        "reoptimize_every": 8,
        "top_n": 3,
        "min_trades": 5,
        "max_loops": 0,
        "demo_train_fraction": 0.7,
        "demo_speed_ms": 60,
        "risk": {
            "fee_rate": 0.0005,
            "slippage": 0.0002,
            "risk_per_trade": 0.01,
            "max_position_pct": 0.25,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.04,
            "max_open_positions": 3,
        },
    },
    "Мягкий 65-80": {
        "mode": "demo",
        "symbols": "AAPL MSFT",
        "interval": "15m",
        "target_capital": 120.0,
        "required_win_min": 65.0,
        "required_win_max": 80.0,
        "strategy": "AUTO",
        "lookback_bars": 700,
        "poll_seconds": 30,
        "reoptimize_every": 10,
        "top_n": 5,
        "min_trades": 6,
        "max_loops": 0,
        "demo_train_fraction": 0.75,
        "demo_speed_ms": 80,
        "risk": {
            "fee_rate": 0.0005,
            "slippage": 0.0003,
            "risk_per_trade": 0.008,
            "max_position_pct": 0.2,
            "stop_loss_pct": 0.015,
            "take_profit_pct": 0.03,
            "max_open_positions": 2,
        },
    },
}


class SimpleTradingGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CVV Trading Bot - Simple UI (Paper)")
        self.geometry("1240x820")
        self.minsize(1080, 700)

        self.process = None
        self.worker = None
        self.events: queue.Queue = queue.Queue()
        self.equity_points: list[tuple[int, float]] = []
        self.symbol_strategy: dict[str, str] = {}
        self.latest_equity = None
        self.wallet_balance = 10.0
        self.custom_profiles: dict[str, dict] = {}
        self.profiles: dict[str, dict] = {}
        self.advanced_visible = False

        self._build_vars()
        self._load_wallet()
        self._load_profiles()
        self._build_ui()
        self._refresh_profile_list()
        self.apply_selected_profile()

        self.after(120, self._drain_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_vars(self) -> None:
        self.profile_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="demo")
        self.symbols_var = tk.StringVar(value="AAPL MSFT NVDA")
        self.interval_var = tk.StringVar(value="5m")
        self.strategy_var = tk.StringVar(value="Авто (лучший вариант)")

        self.target_var = tk.StringVar(value="100")
        self.win_min_var = tk.StringVar(value="70")
        self.win_max_var = tk.StringVar(value="75")

        self.wallet_balance_var = tk.StringVar(value="10.00")
        self.wallet_delta_var = tk.StringVar(value="10")
        self.sync_wallet_var = tk.BooleanVar(value=True)

        self.lookback_var = tk.StringVar(value="600")
        self.poll_var = tk.StringVar(value="30")
        self.reoptimize_var = tk.StringVar(value="8")
        self.top_n_var = tk.StringVar(value="3")
        self.min_trades_var = tk.StringVar(value="5")
        self.max_loops_var = tk.StringVar(value="0")
        self.demo_train_var = tk.StringVar(value="0.7")
        self.demo_speed_var = tk.StringVar(value="60")
        self.fee_var = tk.StringVar(value="0.0005")
        self.slippage_var = tk.StringVar(value="0.0002")
        self.risk_trade_var = tk.StringVar(value="0.01")
        self.max_pos_var = tk.StringVar(value="0.25")
        self.sl_var = tk.StringVar(value="0.02")
        self.tp_var = tk.StringVar(value="0.04")
        self.max_open_var = tk.StringVar(value="3")

        self.status_var = tk.StringVar(value="Готово к запуску")

    def _build_ui(self) -> None:
        quick = ttk.LabelFrame(self, text="Быстрый старт")
        quick.pack(fill="x", padx=10, pady=(10, 6))
        for col in range(12):
            quick.columnconfigure(col, weight=1)

        ttk.Label(quick, text="Профиль").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.profile_cb = ttk.Combobox(quick, textvariable=self.profile_var, state="readonly")
        self.profile_cb.grid(row=1, column=0, columnspan=3, sticky="ew", padx=6, pady=(0, 8))
        self.profile_cb.bind("<<ComboboxSelected>>", lambda _: self.apply_selected_profile())

        ttk.Button(quick, text="Применить", command=self.apply_selected_profile).grid(
            row=1, column=3, sticky="ew", padx=6, pady=(0, 8)
        )
        ttk.Button(quick, text="Сохранить как мою стратегию", command=self.save_profile).grid(
            row=1, column=4, columnspan=2, sticky="ew", padx=6, pady=(0, 8)
        )
        ttk.Button(quick, text="Удалить мой профиль", command=self.delete_profile).grid(
            row=1, column=6, columnspan=2, sticky="ew", padx=6, pady=(0, 8)
        )

        ttk.Label(quick, text="Режим").grid(row=0, column=8, sticky="w", padx=6, pady=6)
        ttk.Combobox(
            quick,
            textvariable=self.mode_var,
            values=["demo", "live", "backtest"],
            state="readonly",
            width=10,
        ).grid(row=1, column=8, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(quick, text="Стратегия").grid(row=0, column=9, sticky="w", padx=6, pady=6)
        ttk.Combobox(
            quick,
            textvariable=self.strategy_var,
            values=list(STRATEGY_OPTIONS.keys()),
            state="readonly",
        ).grid(row=1, column=9, columnspan=3, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(quick, text="Тикеры").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(quick, textvariable=self.symbols_var).grid(row=3, column=0, columnspan=3, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(quick, text="Таймфрейм").grid(row=2, column=3, sticky="w", padx=6, pady=6)
        ttk.Combobox(
            quick,
            textvariable=self.interval_var,
            values=["1m", "5m", "15m", "30m", "60m", "1d"],
            state="readonly",
        ).grid(row=3, column=3, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(quick, text="Цель капитала").grid(row=2, column=4, sticky="w", padx=6, pady=6)
        ttk.Entry(quick, textvariable=self.target_var).grid(row=3, column=4, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(quick, text="Win min %").grid(row=2, column=5, sticky="w", padx=6, pady=6)
        ttk.Entry(quick, textvariable=self.win_min_var).grid(row=3, column=5, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(quick, text="Win max %").grid(row=2, column=6, sticky="w", padx=6, pady=6)
        ttk.Entry(quick, textvariable=self.win_max_var).grid(row=3, column=6, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(quick, text="Демо-кошелек").grid(row=2, column=7, sticky="w", padx=6, pady=6)
        ttk.Label(quick, textvariable=self.wallet_balance_var).grid(row=3, column=7, sticky="w", padx=6, pady=(0, 8))

        ttk.Entry(quick, textvariable=self.wallet_delta_var).grid(row=3, column=8, sticky="ew", padx=6, pady=(0, 8))
        ttk.Button(quick, text="Пополнить", command=self.deposit_wallet).grid(
            row=3, column=9, sticky="ew", padx=6, pady=(0, 8)
        )
        ttk.Button(quick, text="Снять", command=self.withdraw_wallet).grid(
            row=3, column=10, sticky="ew", padx=6, pady=(0, 8)
        )
        ttk.Checkbutton(quick, text="Синхр. кошелек с equity", variable=self.sync_wallet_var).grid(
            row=3, column=11, sticky="w", padx=6, pady=(0, 8)
        )

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0, 8))
        self.start_btn = ttk.Button(bar, text="Старт", command=self.start_bot)
        self.start_btn.pack(side="left", padx=(0, 8))
        self.stop_btn = ttk.Button(bar, text="Стоп", command=self.stop_bot, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="Расширенные настройки", command=self.toggle_advanced).pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="Очистить лог", command=self.clear_log).pack(side="left")
        ttk.Label(bar, textvariable=self.status_var).pack(side="right")

        self.advanced_frame = ttk.LabelFrame(self, text="Расширенные настройки")
        for col in range(8):
            self.advanced_frame.columnconfigure(col, weight=1)

        fields = [
            ("Lookback", self.lookback_var),
            ("Poll sec", self.poll_var),
            ("Reoptimize", self.reoptimize_var),
            ("Top N", self.top_n_var),
            ("Min trades", self.min_trades_var),
            ("Max loops", self.max_loops_var),
            ("Train frac", self.demo_train_var),
            ("Demo speed ms", self.demo_speed_var),
            ("Fee", self.fee_var),
            ("Slippage", self.slippage_var),
            ("Risk/trade", self.risk_trade_var),
            ("Max pos %", self.max_pos_var),
            ("SL %", self.sl_var),
            ("TP %", self.tp_var),
            ("Max open", self.max_open_var),
        ]
        for i, (label, var) in enumerate(fields):
            r = (i // 8) * 2
            c = i % 8
            ttk.Label(self.advanced_frame, text=label).grid(row=r, column=c, sticky="w", padx=6, pady=6)
            ttk.Entry(self.advanced_frame, textvariable=var).grid(row=r + 1, column=c, sticky="ew", padx=6, pady=(0, 8))

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=3)
        body.add(right, weight=2)

        left.rowconfigure(0, weight=2)
        left.rowconfigure(1, weight=2)
        left.columnconfigure(0, weight=1)

        chart_wrap = ttk.LabelFrame(left, text="Equity")
        chart_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        self.chart = tk.Canvas(chart_wrap, bg="#101418", highlightthickness=0)
        self.chart.pack(fill="both", expand=True)
        self.chart.bind("<Configure>", lambda _: self._redraw_chart())

        trades_wrap = ttk.LabelFrame(left, text="Сделки")
        trades_wrap.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(6, 0))
        trades_wrap.rowconfigure(0, weight=1)
        trades_wrap.columnconfigure(0, weight=1)
        cols = ("ts", "symbol", "side", "qty", "price", "pnl", "reason", "strategy")
        self.trade_tree = ttk.Treeview(trades_wrap, columns=cols, show="headings")
        for c, w in {
            "ts": 150,
            "symbol": 80,
            "side": 60,
            "qty": 80,
            "price": 90,
            "pnl": 80,
            "reason": 90,
            "strategy": 120,
        }.items():
            self.trade_tree.heading(c, text=c.upper())
            self.trade_tree.column(c, width=w, anchor="center")
        self.trade_tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(trades_wrap, orient="vertical", command=self.trade_tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.trade_tree.configure(yscrollcommand=sb.set)

        logs_wrap = ttk.LabelFrame(right, text="Логи")
        logs_wrap.pack(fill="both", expand=True, padx=(6, 0))
        self.log_box = scrolledtext.ScrolledText(logs_wrap, state="disabled", wrap="word", font=("Consolas", 10))
        self.log_box.pack(fill="both", expand=True, padx=6, pady=6)

    def _load_wallet(self) -> None:
        if os.path.exists(WALLET_FILE):
            try:
                with open(WALLET_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.wallet_balance = float(data.get("balance", 10.0))
            except Exception:
                self.wallet_balance = 10.0
        else:
            self.wallet_balance = 10.0
        self._update_wallet_text()

    def _save_wallet(self) -> None:
        with open(WALLET_FILE, "w", encoding="utf-8") as f:
            json.dump({"balance": round(self.wallet_balance, 6)}, f, indent=2)

    def _update_wallet_text(self) -> None:
        self.wallet_balance_var.set(f"{self.wallet_balance:.2f} USD")

    def deposit_wallet(self) -> None:
        delta = self._as_float(self.wallet_delta_var.get(), "Сумма пополнения", 0.01)
        self.wallet_balance += delta
        self._save_wallet()
        self._update_wallet_text()
        self.status_var.set(f"Кошелек пополнен на {delta:.2f}")

    def withdraw_wallet(self) -> None:
        delta = self._as_float(self.wallet_delta_var.get(), "Сумма снятия", 0.01)
        if delta > self.wallet_balance:
            messagebox.showerror("Недостаточно средств", "Нельзя снять больше текущего баланса кошелька.")
            return
        self.wallet_balance -= delta
        self._save_wallet()
        self._update_wallet_text()
        self.status_var.set(f"Снято из кошелька: {delta:.2f}")

    def _load_profiles(self) -> None:
        self.custom_profiles = {}
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if isinstance(raw, dict):
                    self.custom_profiles = {k: v for k, v in raw.items() if isinstance(v, dict)}
            except Exception:
                self.custom_profiles = {}
        self.profiles = dict(DEFAULT_PROFILES)
        self.profiles.update(self.custom_profiles)

    def _save_custom_profiles(self) -> None:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.custom_profiles, f, indent=2, ensure_ascii=False)

    def _refresh_profile_list(self) -> None:
        names = list(DEFAULT_PROFILES.keys()) + sorted([x for x in self.custom_profiles if x not in DEFAULT_PROFILES])
        self.profile_cb.configure(values=names)
        if not names:
            self.profile_var.set("")
            return
        if self.profile_var.get() not in names:
            self.profile_var.set(names[0])

    def apply_selected_profile(self) -> None:
        name = self.profile_var.get().strip()
        if not name:
            return
        p = self.profiles.get(name, {})
        risk = p.get("risk", {})
        self.mode_var.set(str(p.get("mode", "demo")))
        self.symbols_var.set(str(p.get("symbols", "AAPL")))
        self.interval_var.set(str(p.get("interval", "5m")))
        self.target_var.set(str(p.get("target_capital", 100)))
        self.win_min_var.set(str(p.get("required_win_min", 70)))
        self.win_max_var.set(str(p.get("required_win_max", 75)))
        strategy_code = str(p.get("strategy", "AUTO"))
        reverse = {v: k for k, v in STRATEGY_OPTIONS.items()}
        self.strategy_var.set(reverse.get(strategy_code, "Авто (лучший вариант)"))
        self.lookback_var.set(str(p.get("lookback_bars", 600)))
        self.poll_var.set(str(p.get("poll_seconds", 30)))
        self.reoptimize_var.set(str(p.get("reoptimize_every", 8)))
        self.top_n_var.set(str(p.get("top_n", 3)))
        self.min_trades_var.set(str(p.get("min_trades", 5)))
        self.max_loops_var.set(str(p.get("max_loops", 0)))
        self.demo_train_var.set(str(p.get("demo_train_fraction", 0.7)))
        self.demo_speed_var.set(str(p.get("demo_speed_ms", 60)))
        self.fee_var.set(str(risk.get("fee_rate", 0.0005)))
        self.slippage_var.set(str(risk.get("slippage", 0.0002)))
        self.risk_trade_var.set(str(risk.get("risk_per_trade", 0.01)))
        self.max_pos_var.set(str(risk.get("max_position_pct", 0.25)))
        self.sl_var.set(str(risk.get("stop_loss_pct", 0.02)))
        self.tp_var.set(str(risk.get("take_profit_pct", 0.04)))
        self.max_open_var.set(str(risk.get("max_open_positions", 3)))
        self.status_var.set(f"Профиль применен: {name}")

    def save_profile(self) -> None:
        settings = self._current_settings()
        name = simpledialog.askstring("Сохранить профиль", "Имя профиля:", initialvalue="Моя стратегия")
        if not name:
            return
        name = name.strip()
        if not name:
            return
        self.custom_profiles[name] = settings
        self.profiles[name] = settings
        self._save_custom_profiles()
        self._refresh_profile_list()
        self.profile_var.set(name)
        self.status_var.set(f"Профиль сохранен: {name}")

    def delete_profile(self) -> None:
        name = self.profile_var.get().strip()
        if not name:
            return
        if name in DEFAULT_PROFILES:
            messagebox.showinfo("Защищено", "Базовый профиль удалить нельзя.")
            return
        if name not in self.custom_profiles:
            return
        del self.custom_profiles[name]
        if name in self.profiles:
            del self.profiles[name]
        self._save_custom_profiles()
        self._refresh_profile_list()
        self.apply_selected_profile()
        self.status_var.set(f"Профиль удален: {name}")

    def toggle_advanced(self) -> None:
        self.advanced_visible = not self.advanced_visible
        if self.advanced_visible:
            self.advanced_frame.pack(fill="x", padx=10, pady=(0, 8))
        else:
            self.advanced_frame.pack_forget()

    def clear_log(self) -> None:
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.configure(state="disabled")

    def _current_settings(self) -> dict:
        strategy_code = STRATEGY_OPTIONS.get(self.strategy_var.get().strip(), "AUTO")
        symbols = " ".join([x.strip().upper() for x in re.split(r"[,\s]+", self.symbols_var.get()) if x.strip()])
        if not symbols:
            raise ValueError("Укажи хотя бы один тикер.")
        win_min = self._as_float(self.win_min_var.get(), "Win min", 0, 100)
        win_max = self._as_float(self.win_max_var.get(), "Win max", 0, 100)
        if win_max < win_min:
            raise ValueError("Win max должен быть больше или равен Win min.")
        return {
            "mode": self.mode_var.get().strip(),
            "symbols": symbols,
            "interval": self.interval_var.get().strip(),
            "strategy": strategy_code,
            "target_capital": self._as_float(self.target_var.get(), "Цель капитала", 0.01),
            "required_win_min": win_min,
            "required_win_max": win_max,
            "lookback_bars": self._as_int(self.lookback_var.get(), "Lookback", 120),
            "poll_seconds": self._as_int(self.poll_var.get(), "Poll", 1),
            "reoptimize_every": self._as_int(self.reoptimize_var.get(), "Reoptimize", 1),
            "top_n": self._as_int(self.top_n_var.get(), "Top N", 1),
            "min_trades": self._as_int(self.min_trades_var.get(), "Min trades", 0),
            "max_loops": self._as_int(self.max_loops_var.get(), "Max loops", 0),
            "demo_train_fraction": self._as_float(self.demo_train_var.get(), "Train fraction", 0.5, 0.9),
            "demo_speed_ms": self._as_float(self.demo_speed_var.get(), "Demo speed", 0),
            "risk": {
                "fee_rate": self._as_float(self.fee_var.get(), "Fee", 0),
                "slippage": self._as_float(self.slippage_var.get(), "Slippage", 0),
                "risk_per_trade": self._as_float(self.risk_trade_var.get(), "Risk/trade", 0, 1),
                "max_position_pct": self._as_float(self.max_pos_var.get(), "Max position", 0, 1),
                "stop_loss_pct": self._as_float(self.sl_var.get(), "SL", 0, 1),
                "take_profit_pct": self._as_float(self.tp_var.get(), "TP", 0, 5),
                "max_open_positions": self._as_int(self.max_open_var.get(), "Max open", 1),
            },
        }

    def _build_command(self) -> list[str]:
        if not os.path.exists(BOT_SCRIPT):
            raise ValueError(f"Не найден файл бота: {BOT_SCRIPT}")
        settings = self._current_settings()
        cmd = [
            sys.executable,
            "-u",
            BOT_SCRIPT,
            "--mode",
            settings["mode"],
            "--symbols",
            *settings["symbols"].split(),
            "--interval",
            settings["interval"],
            "--strategy",
            settings["strategy"],
            "--initial-capital",
            str(self.wallet_balance),
            "--target-capital",
            str(settings["target_capital"]),
            "--required-win-min",
            str(settings["required_win_min"]),
            "--required-win-max",
            str(settings["required_win_max"]),
            "--lookback-bars",
            str(settings["lookback_bars"]),
            "--poll-seconds",
            str(settings["poll_seconds"]),
            "--reoptimize-every",
            str(settings["reoptimize_every"]),
            "--top-n",
            str(settings["top_n"]),
            "--min-trades",
            str(settings["min_trades"]),
            "--max-loops",
            str(settings["max_loops"]),
            "--demo-train-fraction",
            str(settings["demo_train_fraction"]),
            "--demo-speed-ms",
            str(settings["demo_speed_ms"]),
            "--fee-rate",
            str(settings["risk"]["fee_rate"]),
            "--slippage",
            str(settings["risk"]["slippage"]),
            "--risk-per-trade",
            str(settings["risk"]["risk_per_trade"]),
            "--max-position-pct",
            str(settings["risk"]["max_position_pct"]),
            "--stop-loss-pct",
            str(settings["risk"]["stop_loss_pct"]),
            "--take-profit-pct",
            str(settings["risk"]["take_profit_pct"]),
            "--max-open-positions",
            str(settings["risk"]["max_open_positions"]),
        ]
        return cmd

    def start_bot(self) -> None:
        if self.process is not None and self.process.poll() is None:
            messagebox.showinfo("Уже запущено", "Бот уже работает.")
            return
        try:
            cmd = self._build_command()
        except ValueError as exc:
            messagebox.showerror("Ошибка параметров", str(exc))
            return
        self._reset_run_views()
        self._set_running(True)
        self.status_var.set("Запуск...")
        self._append_log(" ".join(cmd))
        self.worker = threading.Thread(target=self._run_process, args=(cmd,), daemon=True)
        self.worker.start()

    def stop_bot(self) -> None:
        proc = self.process
        if proc is None or proc.poll() is not None:
            self._set_running(False)
            self.status_var.set("Остановлено")
            return
        self.status_var.set("Остановка...")
        try:
            proc.terminate()
        except OSError:
            pass

    def _run_process(self, cmd: list[str]) -> None:
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as exc:
            self.events.put(("error", f"Ошибка запуска: {exc}"))
            return
        assert self.process.stdout is not None
        try:
            for raw in self.process.stdout:
                self.events.put(("line", raw.rstrip("\n")))
        finally:
            code = self.process.wait()
            self.events.put(("done", code))

    def _drain_events(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "line":
                    self._append_log(payload)
                    self._parse_log_line(payload)
                elif kind == "error":
                    self._append_log(payload)
                    self.status_var.set("Ошибка")
                    self._set_running(False)
                elif kind == "done":
                    self._set_running(False)
                    if self.sync_wallet_var.get() and self.latest_equity is not None and self.latest_equity > 0:
                        self.wallet_balance = float(self.latest_equity)
                        self._save_wallet()
                        self._update_wallet_text()
                    self.status_var.set(f"Остановлено (код {payload})")
        except queue.Empty:
            pass
        self.after(120, self._drain_events)

    def _parse_log_line(self, line: str) -> None:
        ts = line.split("|", 1)[0].strip() if "|" in line else ""
        b = BUY_RE.search(line)
        if b:
            sym = b.group("symbol")
            strategy = b.group("strategy")
            self.symbol_strategy[sym] = strategy
            self.trade_tree.insert("", 0, values=(ts, sym, "BUY", b.group("qty"), b.group("price"), "", "", strategy))
            return
        s = SELL_RE.search(line)
        if s:
            sym = s.group("symbol")
            strategy = self.symbol_strategy.get(sym, "")
            self.trade_tree.insert(
                "",
                0,
                values=(ts, sym, "SELL", s.group("qty"), s.group("price"), s.group("pnl"), s.group("reason"), strategy),
            )
            return
        m = LOOP_RE.search(line)
        if m:
            loop_n = int(m.group("loop"))
            equity = float(m.group("equity"))
            self.latest_equity = equity
            self.equity_points.append((loop_n, equity))
            if len(self.equity_points) > 600:
                self.equity_points = self.equity_points[-600:]
            self.status_var.set(
                f"Работаю: loop={loop_n}, equity={equity:.2f}, pos={m.group('positions')}, wallet={self.wallet_balance:.2f}"
            )
            self._redraw_chart()

    def _append_log(self, line: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, line + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def _reset_run_views(self) -> None:
        self.latest_equity = None
        self.equity_points.clear()
        self.symbol_strategy.clear()
        for item in self.trade_tree.get_children():
            self.trade_tree.delete(item)
        self._redraw_chart()

    def _redraw_chart(self) -> None:
        c = self.chart
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 50 or h < 50:
            return
        x0, y0, x1, y1 = 54, 18, w - 20, h - 34
        c.create_rectangle(x0, y0, x1, y1, outline="#4b5962")
        if not self.equity_points:
            c.create_text(w // 2, h // 2, text="Пока нет данных", fill="#c8d3da")
            return
        loops = [p[0] for p in self.equity_points]
        vals = [p[1] for p in self.equity_points]
        mn, mx = min(vals), max(vals)
        if abs(mx - mn) < 1e-9:
            mn -= 1
            mx += 1
        l0, l1 = min(loops), max(loops)
        if l0 == l1:
            l1 += 1

        def sx(n: int) -> float:
            return x0 + (n - l0) * (x1 - x0) / (l1 - l0)

        def sy(v: float) -> float:
            return y1 - (v - mn) * (y1 - y0) / (mx - mn)

        pts = []
        for ln, eq in self.equity_points:
            pts.extend([sx(ln), sy(eq)])
        if len(pts) >= 4:
            c.create_line(*pts, fill="#4cc2ff", width=2)
        c.create_text(x0, y0 - 8, text=f"max {mx:.2f}", fill="#a4b6c2", anchor="w")
        c.create_text(x0, y1 + 12, text=f"min {mn:.2f}", fill="#a4b6c2", anchor="w")
        c.create_text(x1, y0 - 8, text=f"latest {vals[-1]:.2f}", fill="#a4b6c2", anchor="e")

    def _set_running(self, running: bool) -> None:
        self.start_btn.configure(state="disabled" if running else "normal")
        self.stop_btn.configure(state="normal" if running else "disabled")

    def _as_int(self, raw: str, name: str, min_value: int) -> int:
        try:
            v = int(raw)
        except ValueError as exc:
            raise ValueError(f"{name}: нужно целое число") from exc
        if v < min_value:
            raise ValueError(f"{name}: минимум {min_value}")
        return v

    def _as_float(self, raw: str, name: str, min_value: float, max_value: float | None = None) -> float:
        try:
            v = float(raw)
        except ValueError as exc:
            raise ValueError(f"{name}: нужно число") from exc
        if v < min_value:
            raise ValueError(f"{name}: минимум {min_value}")
        if max_value is not None and v > max_value:
            raise ValueError(f"{name}: максимум {max_value}")
        return v

    def _on_close(self) -> None:
        self.stop_bot()
        self.after(250, self.destroy)


def main() -> None:
    app = SimpleTradingGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
