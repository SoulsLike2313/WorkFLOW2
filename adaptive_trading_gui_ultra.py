import os
import queue
import random
import re
import subprocess
import sys
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_PATH = os.path.join(BASE_DIR, "adaptive_trading_bot.py")

TOP_COINS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT",
    "TRX/USDT",
    "AVAX/USDT",
    "LINK/USDT",
]

LOOP_RE = re.compile(
    r"loop=(?P<loop>\d+)\s+equity=(?P<equity>-?\d+(?:\.\d+)?)\s+target=(?P<target>-?\d+(?:\.\d+)?)\s+cash=(?P<cash>-?\d+(?:\.\d+)?)\s+positions=(?P<positions>\d+)"
)
BUY_RE = re.compile(
    r"BUY\s+(?P<symbol>[A-Z0-9/\-_.:]+)\s+qty=(?P<qty>-?\d+(?:\.\d+)?)\s+price=(?P<price>-?\d+(?:\.\d+)?)\s+strategy=(?P<strategy>[A-Z_]+)"
)
SELL_RE = re.compile(
    r"SELL\s+(?P<symbol>[A-Z0-9/\-_.:]+)\s+qty=(?P<qty>-?\d+(?:\.\d+)?)\s+price=(?P<price>-?\d+(?:\.\d+)?)\s+reason=(?P<reason>[a-z_]+)\s+pnl=(?P<pnl>-?\d+(?:\.\d+)?)(?:\s+pnl_pct=(?P<pnl_pct>-?\d+(?:\.\d+)?)%)?"
)
STRAT_RE = re.compile(
    r"\[(?P<symbol>[A-Z0-9/\-_.:]+)\]\s+strategy=(?P<strategy>[A-Z_]+).*test_win=(?P<win>-?\d+(?:\.\d+)?)%"
)
TOP_RE = re.compile(
    r"\[(?P<symbol>[A-Z0-9/\-_.:]+)\]\s+TOP(?P<rank>\d+)\s+(?P<strategy>[A-Z_]+)\s+params=.*?test_win=(?P<win>-?\d+(?:\.\d+)?)%.*"
)
SUCCESS_RE = re.compile(
    r"\[(?P<symbol>[A-Z0-9/\-_.:]+)\]\s+SUCCESS(?P<rank>\d+)\s+(?P<strategy>[A-Z_]+)\s+params=.*?test_win=(?P<win>-?\d+(?:\.\d+)?)%.*test_ret=(?P<ret>-?\d+(?:\.\d+)?)%"
)
POOL_RE = re.compile(
    r"Strategy pool:\s+pack=(?P<pack>[a-z_]+)\s+count=(?P<count>\d+)\s+selection=(?P<selection>[a-z_]+)"
)
FREQ_RE = re.compile(
    r"Trade frequency profile:\s+(?P<mode>[a-z_]+)\s+\|\s+poll=(?P<poll>\d+)s\s+reoptimize_every=(?P<reopt>\d+)\s+hold=(?P<hold>\d+)\s+cooldown=(?P<cool>\d+)\s+delay=(?P<delay>\d+)"
)
SUCCESS_SCAN_RE = re.compile(
    r"Success scan:\s+enabled=(?P<enabled>True|False)\s+fallback=(?P<fallback>True|False)\s+min_win=(?P<win>-?\d+(?:\.\d+)?)%\s+min_ret=(?P<ret>-?\d+(?:\.\d+)?)%"
)
HOLD_MODE_RE = re.compile(
    r"Time-hold mode:\s+every trade is closed after (?P<bars>\d+) bar\(s\)\."
)
TRAINED_RE = re.compile(
    r"\[(?P<idx>\d+)\/(?P<total>\d+)\]\s+TRAINED\s+(?P<symbol>[A-Z0-9/\-_.:]+)\s+->\s+(?P<strategy>[A-Z_]+)\s+win=(?P<win>-?\d+(?:\.\d+)?)%\s+ret=(?P<ret>-?\d+(?:\.\d+)?)%"
)
SIGNAL_RE = re.compile(
    r"\[(?P<symbol>[A-Z0-9/\-_.:]+)\]\s+close=(?P<close>-?\d+(?:\.\d+)?)\s+signal=(?P<signal>-?\d+)\s+strategy=(?P<strategy>[A-Z_]+)"
)


class UltraSimpleGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Auto Trader - Demo Dashboard")
        self.geometry("1320x900")
        self.minsize(1100, 720)

        self.proc = None
        self.worker = None
        self.events: queue.Queue = queue.Queue()
        self.last_tv_open = ("", 0.0)

        self.mode_var = tk.StringVar(value="DEMO")
        self.exchange_var = tk.StringVar(value="binance")
        self.interval_var = tk.StringVar(value="5m")
        self.balance_var = tk.StringVar(value="10")
        self.target_var = tk.StringVar(value="100")
        self.win_min_var = tk.StringVar(value="70")
        self.win_max_var = tk.StringVar(value="75")
        self.pnl_min_var = tk.StringVar(value="20")
        self.pnl_max_var = tk.StringVar(value="30")
        self.min_hold_var = tk.StringVar(value="3")
        self.cooldown_var = tk.StringVar(value="2")
        self.entry_delay_var = tk.StringVar(value="5")
        self.strategy_pack_var = tk.StringVar(value="MAX")
        self.selection_mode_var = tk.StringVar(value="WINRATE")
        self.frequency_var = tk.StringVar(value="FREQUENT")
        self.simple_mode_var = tk.BooleanVar(value=True)
        self.hold_minutes_var = tk.StringVar(value="5")
        self.train_all_var = tk.BooleanVar(value=True)
        self.train_max_symbols_var = tk.StringVar(value="0")
        self.learned_model_path_var = tk.StringVar(value="learned_crypto_model.json")
        self.success_scan_var = tk.BooleanVar(value=True)
        self.success_fallback_var = tk.BooleanVar(value=True)
        self.success_win_min_var = tk.StringVar(value="55")
        self.success_ret_min_var = tk.StringVar(value="0")
        self.coins_mode_var = tk.StringVar(value="TOP")
        self.custom_coins_var = tk.StringVar(value="BTC/USDT ETH/USDT")
        self.api_key_var = tk.StringVar(value="")
        self.api_secret_var = tk.StringVar(value="")
        self.api_password_var = tk.StringVar(value="")
        self.auto_tv_var = tk.BooleanVar(value=False)
        self.show_raw_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")

        self.start_balance = 0.0
        self.target_balance = 0.0
        self.current_equity = 0.0
        self.trades_closed = 0
        self.wins = 0
        self.losses = 0
        self.synthetic_window = None
        self.syn_vars = {}
        self.syn_canvas = None
        self.syn_text = None
        self.syn_status_var = tk.StringVar(value="Ready")

        self.metric_vars = {
            "start": tk.StringVar(value="0.00"),
            "equity": tk.StringVar(value="0.00"),
            "pnl": tk.StringVar(value="0.00"),
            "pnl_pct": tk.StringVar(value="0.00%"),
            "target": tk.StringVar(value="0.00"),
            "progress": tk.StringVar(value="0%"),
            "trades": tk.StringVar(value="0"),
            "win_rate": tk.StringVar(value="0%"),
            "open_pos": tk.StringVar(value="0"),
            "last_signal": tk.StringVar(value="-"),
        }

        self._build_ui()
        self._refresh_inputs()
        self.after(120, self._drain_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True, padx=10, pady=10)

        title = ttk.Label(
            root,
            text="Simple Demo: set balance, coins, win-rate target and press START",
            font=("Segoe UI", 13, "bold"),
        )
        title.pack(anchor="w", pady=(0, 10))

        cfg = ttk.LabelFrame(root, text="Run Setup")
        cfg.pack(fill="x")
        for c in range(7):
            cfg.columnconfigure(c, weight=1)

        ttk.Label(cfg, text="Mode").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        mode_cb = ttk.Combobox(cfg, textvariable=self.mode_var, values=["DEMO", "LIVE", "TRAIN"], state="readonly")
        mode_cb.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))
        mode_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_inputs())

        ttk.Label(cfg, text="Exchange").grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ttk.Combobox(
            cfg,
            textvariable=self.exchange_var,
            values=["binance", "bybit", "okx"],
            state="readonly",
        ).grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(cfg, text="Interval").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        ttk.Combobox(
            cfg,
            textvariable=self.interval_var,
            values=["1m", "5m", "15m", "30m", "60m", "1d"],
            state="readonly",
        ).grid(row=1, column=2, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(cfg, text="Start Balance").grid(row=0, column=3, sticky="w", padx=6, pady=6)
        ttk.Entry(cfg, textvariable=self.balance_var).grid(row=1, column=3, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(cfg, text="Target Balance").grid(row=0, column=4, sticky="w", padx=6, pady=6)
        ttk.Entry(cfg, textvariable=self.target_var).grid(row=1, column=4, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(cfg, text="Win-rate range (%)").grid(row=0, column=5, sticky="w", padx=6, pady=6)
        win_frame = ttk.Frame(cfg)
        win_frame.grid(row=1, column=5, sticky="ew", padx=6, pady=(0, 8))
        ttk.Entry(win_frame, textvariable=self.win_min_var, width=7).pack(side="left", fill="x", expand=True)
        ttk.Label(win_frame, text="to").pack(side="left", padx=4)
        ttk.Entry(win_frame, textvariable=self.win_max_var, width=7).pack(side="left", fill="x", expand=True)

        ttk.Button(cfg, text="Open TradingView", command=self.open_tradingview).grid(
            row=1, column=6, sticky="ew", padx=6, pady=(0, 8)
        )

        mode_row = ttk.Frame(cfg)
        mode_row.grid(row=2, column=0, columnspan=7, sticky="ew", padx=6, pady=4)
        ttk.Radiobutton(
            mode_row,
            text="Top coins (recommended)",
            variable=self.coins_mode_var,
            value="TOP",
            command=self._refresh_inputs,
        ).pack(side="left")
        ttk.Radiobutton(
            mode_row,
            text="Custom coins",
            variable=self.coins_mode_var,
            value="CUSTOM",
            command=self._refresh_inputs,
        ).pack(side="left", padx=(14, 0))
        self.custom_entry = ttk.Entry(mode_row, textvariable=self.custom_coins_var, width=44)
        self.custom_entry.pack(side="left", padx=(14, 0))

        opts = ttk.Frame(cfg)
        opts.grid(row=3, column=0, columnspan=7, sticky="ew", padx=6, pady=4)
        ttk.Checkbutton(opts, text="Auto-open TradingView on BUY/SELL", variable=self.auto_tv_var).pack(
            side="left"
        )
        ttk.Checkbutton(opts, text="Show raw log tab", variable=self.show_raw_var, command=self._toggle_raw_tab).pack(
            side="left", padx=(16, 0)
        )

        rules = ttk.Frame(cfg)
        rules.grid(row=4, column=0, columnspan=7, sticky="ew", padx=6, pady=(0, 8))
        ttk.Checkbutton(
            rules,
            text="Simple mode: broad scan by win-rate",
            variable=self.simple_mode_var,
            command=self._refresh_inputs,
        ).pack(side="left")
        ttk.Label(rules, text="Trade hold").pack(side="left", padx=(16, 6))
        ttk.Combobox(
            rules,
            textvariable=self.hold_minutes_var,
            values=["5", "15", "30", "60"],
            state="readonly",
            width=6,
        ).pack(side="left")
        ttk.Label(rules, text="min").pack(side="left", padx=(4, 10))

        ttk.Label(rules, text="Close trade at PL %").pack(side="left")
        ttk.Entry(rules, textvariable=self.pnl_min_var, width=6).pack(side="left", padx=(6, 0))
        ttk.Label(rules, text="to").pack(side="left", padx=4)
        ttk.Entry(rules, textvariable=self.pnl_max_var, width=6).pack(side="left")
        ttk.Label(rules, text="Hold bars").pack(side="left", padx=(16, 6))
        ttk.Entry(rules, textvariable=self.min_hold_var, width=6).pack(side="left")
        ttk.Label(rules, text="Cooldown").pack(side="left", padx=(16, 6))
        ttk.Entry(rules, textvariable=self.cooldown_var, width=6).pack(side="left")
        ttk.Label(rules, text="Entry delay").pack(side="left", padx=(16, 6))
        ttk.Entry(rules, textvariable=self.entry_delay_var, width=6).pack(side="left")
        ttk.Label(rules, text="Strategies").pack(side="left", padx=(16, 6))
        ttk.Combobox(
            rules,
            textvariable=self.strategy_pack_var,
            values=["BASIC", "EXTENDED", "MAX"],
            state="readonly",
            width=10,
        ).pack(side="left")
        ttk.Label(rules, text="Pick by").pack(side="left", padx=(16, 6))
        ttk.Combobox(
            rules,
            textvariable=self.selection_mode_var,
            values=["WINRATE", "SCORE"],
            state="readonly",
            width=10,
        ).pack(side="left")
        ttk.Label(rules, text="Frequency").pack(side="left", padx=(16, 6))
        ttk.Combobox(
            rules,
            textvariable=self.frequency_var,
            values=["CALM", "NORMAL", "FREQUENT", "VERY_FREQUENT"],
            state="readonly",
            width=14,
        ).pack(side="left")

        success_row = ttk.Frame(cfg)
        success_row.grid(row=5, column=0, columnspan=7, sticky="ew", padx=6, pady=(0, 8))
        ttk.Checkbutton(
            success_row,
            text="Parallel success scan",
            variable=self.success_scan_var,
        ).pack(side="left")
        ttk.Checkbutton(
            success_row,
            text="Fallback to success",
            variable=self.success_fallback_var,
        ).pack(side="left", padx=(14, 0))
        ttk.Label(success_row, text="Success win >=").pack(side="left", padx=(16, 6))
        ttk.Entry(success_row, textvariable=self.success_win_min_var, width=6).pack(side="left")
        ttk.Label(success_row, text="ret >=").pack(side="left", padx=(16, 6))
        ttk.Entry(success_row, textvariable=self.success_ret_min_var, width=6).pack(side="left")

        train_row = ttk.Frame(cfg)
        train_row.grid(row=6, column=0, columnspan=7, sticky="ew", padx=6, pady=(0, 8))
        ttk.Checkbutton(
            train_row,
            text="Train all crypto symbols (quote)",
            variable=self.train_all_var,
        ).pack(side="left")
        ttk.Label(train_row, text="Train max").pack(side="left", padx=(16, 6))
        ttk.Entry(train_row, textvariable=self.train_max_symbols_var, width=8).pack(side="left")
        ttk.Label(train_row, text="Model file").pack(side="left", padx=(16, 6))
        ttk.Entry(train_row, textvariable=self.learned_model_path_var, width=34).pack(side="left")

        self.api_frame = ttk.LabelFrame(root, text="API Credentials (LIVE only)")
        self.api_frame.pack(fill="x", pady=(8, 0))
        for c in range(3):
            self.api_frame.columnconfigure(c, weight=1)
        ttk.Label(self.api_frame, text="API key").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Label(self.api_frame, text="API secret").grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(self.api_frame, text="Password (optional)").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        self.api_key_entry = ttk.Entry(self.api_frame, textvariable=self.api_key_var)
        self.api_secret_entry = ttk.Entry(self.api_frame, textvariable=self.api_secret_var, show="*")
        self.api_password_entry = ttk.Entry(self.api_frame, textvariable=self.api_password_var, show="*")
        self.api_key_entry.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))
        self.api_secret_entry.grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 8))
        self.api_password_entry.grid(row=1, column=2, sticky="ew", padx=6, pady=(0, 8))

        controls = ttk.Frame(root)
        controls.pack(fill="x", pady=(8, 8))
        self.start_btn = ttk.Button(controls, text="START", command=self.start_bot)
        self.start_btn.pack(side="left", padx=(0, 8))
        self.stop_btn = ttk.Button(controls, text="STOP", command=self.stop_bot, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))
        self.synthetic_btn = ttk.Button(
            controls, text="SYNTH TEST", command=self.open_synthetic_test_window
        )
        self.synthetic_btn.pack(side="left", padx=(0, 8))
        ttk.Label(controls, textvariable=self.status_var).pack(side="right")

        metrics = ttk.LabelFrame(root, text="Demo Dashboard")
        metrics.pack(fill="x", pady=(0, 8))
        for c in range(5):
            metrics.columnconfigure(c, weight=1)

        self._metric_card(metrics, 0, "Start", self.metric_vars["start"])
        self._metric_card(metrics, 1, "Equity", self.metric_vars["equity"])
        self._metric_card(metrics, 2, "PnL", self.metric_vars["pnl"])
        self._metric_card(metrics, 3, "PnL %", self.metric_vars["pnl_pct"])
        self._metric_card(metrics, 4, "Target", self.metric_vars["target"])

        self._metric_card(metrics, 5, "Trades", self.metric_vars["trades"])
        self._metric_card(metrics, 6, "Win rate", self.metric_vars["win_rate"])
        self._metric_card(metrics, 7, "Open pos", self.metric_vars["open_pos"])
        self._metric_card(metrics, 8, "Last signal", self.metric_vars["last_signal"])
        self._metric_card(metrics, 9, "Progress", self.metric_vars["progress"])

        self.progress = ttk.Progressbar(metrics, orient="horizontal", mode="determinate", maximum=100)
        self.progress.grid(row=2, column=0, columnspan=5, sticky="ew", padx=6, pady=(2, 8))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.events_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.events_tab, text="Events")
        self.events_tab.rowconfigure(0, weight=1)
        self.events_tab.columnconfigure(0, weight=1)
        cols = ("time", "symbol", "event", "price", "qty", "pnl", "pnl_pct", "note")
        self.event_tree = ttk.Treeview(self.events_tab, columns=cols, show="headings")
        widths = {"time": 100, "symbol": 120, "event": 120, "price": 90, "qty": 90, "pnl": 90, "pnl_pct": 90, "note": 320}
        headers = {
            "time": "Time",
            "symbol": "Symbol",
            "event": "Event",
            "price": "Price",
            "qty": "Qty",
            "pnl": "PnL",
            "pnl_pct": "PnL %",
            "note": "Note",
        }
        for c in cols:
            self.event_tree.heading(c, text=headers[c])
            self.event_tree.column(c, width=widths[c], anchor="center")
        self.event_tree.grid(row=0, column=0, sticky="nsew")
        ev_sb = ttk.Scrollbar(self.events_tab, orient="vertical", command=self.event_tree.yview)
        ev_sb.grid(row=0, column=1, sticky="ns")
        self.event_tree.configure(yscrollcommand=ev_sb.set)
        self.event_tree.tag_configure("buy", foreground="#0b8f38")
        self.event_tree.tag_configure("sell_win", foreground="#0b8f38")
        self.event_tree.tag_configure("sell_loss", foreground="#d94848")
        self.event_tree.tag_configure("warn", foreground="#d18d00")
        self.event_tree.tag_configure("info", foreground="#2f73c0")

        self.raw_tab = ttk.Frame(self.notebook)
        self.raw_log = scrolledtext.ScrolledText(self.raw_tab, state="disabled", wrap="word", font=("Consolas", 10))
        self.raw_log.pack(fill="both", expand=True, padx=6, pady=6)

    def _metric_card(self, parent, index, title, var):
        row = 0 if index < 5 else 1
        col = index if index < 5 else index - 5
        box = ttk.Frame(parent)
        box.grid(row=row, column=col, sticky="ew", padx=6, pady=6)
        ttk.Label(box, text=title).pack(anchor="w")
        ttk.Label(box, textvariable=var, font=("Segoe UI", 13, "bold")).pack(anchor="w")

    def _refresh_inputs(self) -> None:
        is_live = self.mode_var.get().strip().upper() == "LIVE"
        st = "normal" if is_live else "disabled"
        self.api_key_entry.configure(state=st)
        self.api_secret_entry.configure(state=st)
        self.api_password_entry.configure(state=st)
        self.custom_entry.configure(state=("normal" if self.coins_mode_var.get() == "CUSTOM" else "disabled"))
        if self.simple_mode_var.get():
            self.strategy_pack_var.set("MAX")
            self.selection_mode_var.set("WINRATE")

    def _toggle_raw_tab(self) -> None:
        show = self.show_raw_var.get()
        tabs = self.notebook.tabs()
        raw_id = str(self.raw_tab)
        if show and raw_id not in tabs:
            self.notebook.add(self.raw_tab, text="Raw log")
        if not show and raw_id in tabs:
            self.notebook.forget(self.raw_tab)

    def _parse_symbols(self):
        if self.coins_mode_var.get() == "TOP":
            return list(TOP_COINS)
        return [x.strip().upper() for x in re.split(r"[,\s]+", self.custom_coins_var.get()) if x.strip()]

    def _build_cmd(self):
        if not os.path.exists(BOT_PATH):
            raise ValueError("Bot file not found.")
        symbols = self._parse_symbols()
        if not symbols:
            raise ValueError("Add at least one symbol.")

        bal = self._as_float(self.balance_var.get(), "Start balance", 0.01)
        target = self._as_float(self.target_var.get(), "Target balance", 0.01)
        simple_mode = self.simple_mode_var.get()
        hold_minutes = self._as_int(self.hold_minutes_var.get(), "Hold minutes", 5, 60)
        if hold_minutes not in {5, 15, 30, 60}:
            raise ValueError("Hold minutes: use 5, 15, 30 or 60.")
        if simple_mode:
            win_min = 0.0
            win_max = 100.0
            pnl_min = 0.0
            pnl_max = 0.0
            min_hold = 0
            cooldown = 0
            entry_delay = 0
        else:
            win_min = self._as_float(self.win_min_var.get(), "Win-rate min", 1, 100)
            win_max = self._as_float(self.win_max_var.get(), "Win-rate max", 1, 100)
            if win_max < win_min:
                raise ValueError("Win-rate max must be >= min.")
            pnl_min = self._as_float(self.pnl_min_var.get(), "Close PL min", 0, 500)
            pnl_max = self._as_float(self.pnl_max_var.get(), "Close PL max", 0, 500)
            if pnl_max < pnl_min:
                raise ValueError("Close PL max must be >= min.")
            min_hold = self._as_int(self.min_hold_var.get(), "Hold bars", 0, 5000)
            cooldown = self._as_int(self.cooldown_var.get(), "Cooldown bars", 0, 5000)
            entry_delay = self._as_int(self.entry_delay_var.get(), "Entry delay", 0, 5000)
        mode_raw = self.mode_var.get().strip().upper()
        if mode_raw != "TRAIN" and target <= bal:
            raise ValueError("Target must be greater than start balance.")
        strategy_pack = self.strategy_pack_var.get().strip().lower()
        selection_mode = self.selection_mode_var.get().strip().lower()
        frequency = self.frequency_var.get().strip().lower()
        success_win_min = self._as_float(self.success_win_min_var.get(), "Success win min", 0, 100)
        success_ret_min = self._as_float(self.success_ret_min_var.get(), "Success return min", -100, 1000)
        train_max_symbols = self._as_int(self.train_max_symbols_var.get(), "Train max symbols", 0, 100000)
        model_path = self.learned_model_path_var.get().strip() or "learned_crypto_model.json"

        is_live = mode_raw == "LIVE"
        is_train = mode_raw == "TRAIN"
        mode = "train" if is_train else ("live" if is_live else "demo")
        broker_mode = "live" if is_live else "paper"

        cmd = [
            sys.executable,
            "-u",
            BOT_PATH,
            "--mode",
            mode,
            "--broker-mode",
            broker_mode,
            "--exchange",
            self.exchange_var.get().strip(),
            "--symbols",
            *symbols,
            "--interval",
            self.interval_var.get().strip(),
            "--strategy",
            "AUTO",
            "--strategy-pack",
            strategy_pack,
            "--selection-mode",
            selection_mode,
            "--trade-frequency",
            frequency,
            "--hold-minutes",
            str(hold_minutes),
            "--learned-model-path",
            model_path,
            "--success-win-min",
            str(success_win_min),
            "--success-return-min",
            str(success_ret_min),
            "--initial-capital",
            str(bal),
            "--target-capital",
            str(target),
            "--required-win-min",
            str(win_min),
            "--required-win-max",
            str(win_max),
            "--lookback-bars",
            "700",
            "--poll-seconds",
            "20",
            "--reoptimize-every",
            "8",
            "--top-n",
            "5",
            "--min-trades",
            "6",
            "--demo-train-fraction",
            "0.7",
            "--demo-speed-ms",
            "120",
            "--fee-rate",
            "0.0005",
            "--slippage",
            "0.0003",
            "--risk-per-trade",
            "0.01",
            "--max-position-pct",
            "0.2",
            "--stop-loss-pct",
            "0.02",
            "--take-profit-pct",
            "0",
            "--pnl-close-min-pct",
            str(pnl_min),
            "--pnl-close-max-pct",
            str(pnl_max),
            "--min-hold-bars",
            str(min_hold),
            "--cooldown-bars",
            str(cooldown),
            "--entry-delay-bars",
            str(entry_delay),
            "--max-open-positions",
            "3",
            "--quote-currency",
            "USDT",
            "--max-loops",
            "0",
        ]
        if is_train:
            if self.train_all_var.get():
                cmd.append("--train-all-symbols")
            cmd.extend(["--train-max-symbols", str(train_max_symbols)])
        if simple_mode:
            cmd.append("--simple-mode")
        if not self.success_scan_var.get():
            cmd.append("--no-success-scan")
        if not self.success_fallback_var.get():
            cmd.append("--no-success-fallback")
        if is_live:
            key = self.api_key_var.get().strip()
            secret = self.api_secret_var.get().strip()
            if not key or not secret:
                raise ValueError("LIVE mode requires API key and API secret.")
            cmd.extend(["--api-key", key, "--api-secret", secret])
            password = self.api_password_var.get().strip()
            if password:
                cmd.extend(["--api-password", password])
        rule_text = (
            f"win {win_min:.1f}-{win_max:.1f}% | close PL {pnl_min:.1f}-{pnl_max:.1f}% | "
            f"hold {min_hold} bars | cooldown {cooldown} bars | entry delay {entry_delay} bars | "
            f"strategies {strategy_pack} | pick {selection_mode} | freq {frequency} | "
            f"simple={simple_mode} | hold={hold_minutes}m | "
            f"mode={mode} | train_all={self.train_all_var.get()} train_max={train_max_symbols} | "
            f"success_scan={self.success_scan_var.get()} fallback={self.success_fallback_var.get()} "
            f"win>={success_win_min:.1f}% ret>={success_ret_min:.1f}% | model={model_path}"
        )
        return cmd, bal, target, rule_text

    def start_bot(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            messagebox.showinfo("Already running", "Bot is already running.")
            return
        try:
            cmd, bal, target, rule_text = self._build_cmd()
        except ValueError as exc:
            messagebox.showerror("Invalid setup", str(exc))
            return

        self._reset_dashboard(bal, target)
        self._append_event("-", "RULES", "", "", "", "", rule_text, "info")
        self._set_running(True)
        self.status_var.set("Starting...")
        self._append_raw(" ".join(cmd))
        self.worker = threading.Thread(target=self._run_proc, args=(cmd,), daemon=True)
        self.worker.start()

    def stop_bot(self) -> None:
        if self.proc is None or self.proc.poll() is not None:
            self._set_running(False)
            return
        self.status_var.set("Stopping...")
        try:
            self.proc.terminate()
        except OSError:
            pass

    def _run_proc(self, cmd):
        try:
            self.proc = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as exc:
            self.events.put(("error", f"Start error: {exc}"))
            return

        assert self.proc.stdout is not None
        try:
            for raw in self.proc.stdout:
                self.events.put(("line", raw.rstrip("\n")))
        finally:
            rc = self.proc.wait()
            self.events.put(("done", rc))

    def _drain_events(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "line":
                    self._append_raw(payload)
                    self._parse_line(payload)
                elif kind == "error":
                    self._append_event("-", "ERROR", "", "", "", "", payload, "warn")
                    self.status_var.set("Error")
                    self._set_running(False)
                elif kind == "done":
                    self.status_var.set(f"Stopped (code {payload})")
                    self._set_running(False)
        except queue.Empty:
            pass
        self.after(120, self._drain_events)

    def _parse_line(self, line: str) -> None:
        loop = LOOP_RE.search(line)
        if loop:
            self.current_equity = float(loop.group("equity"))
            pnl = self.current_equity - self.start_balance
            pnl_pct = (pnl / self.start_balance * 100.0) if self.start_balance > 0 else 0.0
            denom = (self.target_balance - self.start_balance)
            progress = 0.0 if denom <= 0 else ((self.current_equity - self.start_balance) / denom * 100.0)
            progress = max(0.0, min(100.0, progress))
            self.metric_vars["equity"].set(f"{self.current_equity:.2f}")
            self.metric_vars["pnl"].set(f"{pnl:+.2f}")
            self.metric_vars["pnl_pct"].set(f"{pnl_pct:+.2f}%")
            self.metric_vars["open_pos"].set(loop.group("positions"))
            self.metric_vars["progress"].set(f"{progress:.1f}%")
            self.progress["value"] = progress
            self.status_var.set(
                f"Loop {loop.group('loop')} | Equity {self.current_equity:.2f} | Open {loop.group('positions')}"
            )
            return

        strat = STRAT_RE.search(line)
        if strat:
            symbol = strat.group("symbol")
            note = f"{strat.group('strategy')} | test_win={float(strat.group('win')):.2f}%"
            self._append_event(symbol, "STRATEGY", "", "", "", "", note, "info")
            return

        top = TOP_RE.search(line)
        if top:
            symbol = top.group("symbol")
            note = f"TOP{top.group('rank')} {top.group('strategy')} | test_win={float(top.group('win')):.2f}%"
            self._append_event(symbol, "RANK", "", "", "", "", note, "info")
            return

        success = SUCCESS_RE.search(line)
        if success:
            symbol = success.group("symbol")
            note = (
                f"SUCCESS{success.group('rank')} {success.group('strategy')} | "
                f"win={float(success.group('win')):.2f}% ret={float(success.group('ret')):.2f}%"
            )
            self._append_event(symbol, "SUCCESS", "", "", "", "", note, "buy")
            return

        pool = POOL_RE.search(line)
        if pool:
            note = f"pool={pool.group('pack')} | strategies={pool.group('count')} | select={pool.group('selection')}"
            self._append_event("-", "POOL", "", "", "", "", note, "info")
            return

        freq = FREQ_RE.search(line)
        if freq:
            note = (
                f"{freq.group('mode')} | poll={freq.group('poll')}s | reopt={freq.group('reopt')} | "
                f"hold={freq.group('hold')} cool={freq.group('cool')} delay={freq.group('delay')}"
            )
            self._append_event("-", "FREQUENCY", "", "", "", "", note, "info")
            return

        success_scan = SUCCESS_SCAN_RE.search(line)
        if success_scan:
            note = (
                f"enabled={success_scan.group('enabled')} fallback={success_scan.group('fallback')} "
                f"win>={float(success_scan.group('win')):.2f}% ret>={float(success_scan.group('ret')):.2f}%"
            )
            self._append_event("-", "SUCCESS_SCAN", "", "", "", "", note, "info")
            return

        hold_mode = HOLD_MODE_RE.search(line)
        if hold_mode:
            note = f"fixed hold = {hold_mode.group('bars')} bars"
            self._append_event("-", "HOLD_MODE", "", "", "", "", note, "info")
            return

        trained = TRAINED_RE.search(line)
        if trained:
            symbol = trained.group("symbol")
            note = (
                f"{trained.group('idx')}/{trained.group('total')} {trained.group('strategy')} | "
                f"win={float(trained.group('win')):.2f}% ret={float(trained.group('ret')):.2f}%"
            )
            self._append_event(symbol, "TRAINED", "", "", "", "", note, "buy")
            self.metric_vars["last_signal"].set(f"TRAIN {symbol}")
            self.status_var.set(
                f"Training {trained.group('idx')}/{trained.group('total')} | {symbol} | {trained.group('strategy')}"
            )
            return

        buy = BUY_RE.search(line)
        if buy:
            symbol = buy.group("symbol")
            self.metric_vars["last_signal"].set(f"BUY {symbol}")
            self._append_event(
                symbol,
                "BUY",
                buy.group("price"),
                buy.group("qty"),
                "",
                "",
                buy.group("strategy"),
                "buy",
            )
            if self.auto_tv_var.get():
                self._open_tv_for_symbol(symbol)
            return

        sell = SELL_RE.search(line)
        if sell:
            symbol = sell.group("symbol")
            pnl = float(sell.group("pnl"))
            self.trades_closed += 1
            if pnl > 0:
                self.wins += 1
            else:
                self.losses += 1
            win_rate = self.wins / max(1, self.trades_closed) * 100.0
            self.metric_vars["trades"].set(str(self.trades_closed))
            self.metric_vars["win_rate"].set(f"{win_rate:.1f}%")
            self.metric_vars["last_signal"].set(f"SELL {symbol}")
            tag = "sell_win" if pnl > 0 else "sell_loss"
            pnl_pct = sell.group("pnl_pct")
            self._append_event(
                symbol,
                "SELL",
                sell.group("price"),
                sell.group("qty"),
                f"{pnl:+.2f}",
                (f"{float(pnl_pct):+.2f}%" if pnl_pct is not None else ""),
                sell.group("reason"),
                tag,
            )
            if self.auto_tv_var.get():
                self._open_tv_for_symbol(symbol)
            return

        sig = SIGNAL_RE.search(line)
        if sig and int(sig.group("signal")) != 0:
            symbol = sig.group("symbol")
            signal_val = int(sig.group("signal"))
            marker = "Signal BUY" if signal_val > 0 else "Signal SELL"
            self._append_event(symbol, marker, sig.group("close"), "", "", "", sig.group("strategy"), "info")
            return

        if "Target reached" in line:
            self._append_event("-", "TARGET", "", "", "", "", line, "buy")
            return
        if "No strategy matched" in line:
            self._append_event("-", "NO MATCH", "", "", "", "", line, "warn")
            return
        if "Training completed" in line:
            self._append_event("-", "TRAIN_DONE", "", "", "", "", line, "buy")
            return

    def _append_event(self, symbol, event, price, qty, pnl, pnl_pct, note, tag):
        ts = time.strftime("%H:%M:%S")
        self.event_tree.insert("", 0, values=(ts, symbol, event, price, qty, pnl, pnl_pct, note), tags=(tag,))

    def _append_raw(self, line):
        if not self.show_raw_var.get():
            return
        self.raw_log.configure(state="normal")
        self.raw_log.insert(tk.END, line + "\n")
        self.raw_log.see(tk.END)
        self.raw_log.configure(state="disabled")

    def _reset_dashboard(self, start, target):
        self.start_balance = start
        self.target_balance = target
        self.current_equity = start
        self.trades_closed = 0
        self.wins = 0
        self.losses = 0

        self.metric_vars["start"].set(f"{start:.2f}")
        self.metric_vars["equity"].set(f"{start:.2f}")
        self.metric_vars["pnl"].set("+0.00")
        self.metric_vars["pnl_pct"].set("+0.00%")
        self.metric_vars["target"].set(f"{target:.2f}")
        self.metric_vars["progress"].set("0.0%")
        self.metric_vars["trades"].set("0")
        self.metric_vars["win_rate"].set("0.0%")
        self.metric_vars["open_pos"].set("0")
        self.metric_vars["last_signal"].set("-")
        self.progress["value"] = 0

        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        self.raw_log.configure(state="normal")
        self.raw_log.delete("1.0", tk.END)
        self.raw_log.configure(state="disabled")

    def _set_running(self, running):
        self.start_btn.configure(state=("disabled" if running else "normal"))
        self.stop_btn.configure(state=("normal" if running else "disabled"))

    def _selected_symbol_for_tv(self):
        selected = self.event_tree.selection()
        if selected:
            vals = self.event_tree.item(selected[0]).get("values", [])
            if len(vals) >= 2 and vals[1]:
                return str(vals[1])
        symbols = self._parse_symbols()
        return symbols[0] if symbols else ""

    def _tv_symbol(self, symbol):
        symbol = symbol.upper().replace(":", "")
        if "/" in symbol:
            base, quote = symbol.split("/", 1)
            pair = f"{base}{quote}"
        else:
            pair = symbol.replace("-", "").replace("_", "")
        exchange = self.exchange_var.get().strip().upper()
        mapping = {"BINANCE": "BINANCE", "BYBIT": "BYBIT", "OKX": "OKX"}
        prefix = mapping.get(exchange, exchange)
        return f"{prefix}:{pair}"

    def _open_tv_for_symbol(self, symbol):
        now = time.time()
        if self.last_tv_open[0] == symbol and now - self.last_tv_open[1] < 20:
            return
        tv_symbol = self._tv_symbol(symbol)
        url = f"https://www.tradingview.com/chart/?symbol={tv_symbol}"
        webbrowser.open_new_tab(url)
        self.last_tv_open = (symbol, now)

    def open_tradingview(self):
        symbol = self._selected_symbol_for_tv()
        if not symbol:
            messagebox.showinfo("TradingView", "No symbol selected.")
            return
        self._open_tv_for_symbol(symbol)

    def open_synthetic_test_window(self):
        if self.synthetic_window is not None and self.synthetic_window.winfo_exists():
            self.synthetic_window.lift()
            self.synthetic_window.focus_force()
            return

        win = tk.Toplevel(self)
        win.title("Quick Synthetic Test")
        win.geometry("980x700")
        win.minsize(860, 620)
        self.synthetic_window = win

        panel = ttk.LabelFrame(win, text="Synthetic Scenario")
        panel.pack(fill="x", padx=10, pady=10)
        for col in range(6):
            panel.columnconfigure(col, weight=1)

        self.syn_vars = {
            "start": tk.StringVar(value=self.balance_var.get() or "10"),
            "target": tk.StringVar(value=self.target_var.get() or "100"),
            "max_trades": tk.StringVar(value="180"),
            "hold_minutes": tk.StringVar(value=self.hold_minutes_var.get() or "5"),
            "win_rate": tk.StringVar(value="75"),
            "stake_pct": tk.StringVar(value="65"),
            "win_min": tk.StringVar(value="6"),
            "win_max": tk.StringVar(value="12"),
            "loss_min": tk.StringVar(value="2"),
            "loss_max": tk.StringVar(value="6"),
            "goal_bias": tk.BooleanVar(value=True),
            "attempts": tk.StringVar(value="8"),
        }

        labels = [
            ("Start $", "start"),
            ("Target $", "target"),
            ("Max trades", "max_trades"),
            ("Hold min", "hold_minutes"),
            ("Win-rate %", "win_rate"),
            ("Stake %", "stake_pct"),
            ("Win % min", "win_min"),
            ("Win % max", "win_max"),
            ("Loss % min", "loss_min"),
            ("Loss % max", "loss_max"),
            ("Retry runs", "attempts"),
        ]
        for idx, (title, key) in enumerate(labels):
            row = (idx // 6) * 2
            col = idx % 6
            ttk.Label(panel, text=title).grid(row=row, column=col, sticky="w", padx=6, pady=(6, 2))
            ttk.Entry(panel, textvariable=self.syn_vars[key]).grid(
                row=row + 1, column=col, sticky="ew", padx=6, pady=(0, 8)
            )

        ttk.Checkbutton(
            panel,
            text="Goal bias (push scenario toward reaching target)",
            variable=self.syn_vars["goal_bias"],
        ).grid(row=4, column=0, columnspan=4, sticky="w", padx=6, pady=(2, 8))

        ttk.Button(panel, text="RUN SYNTH TEST", command=self.run_synthetic_test).grid(
            row=4, column=4, columnspan=2, sticky="ew", padx=6, pady=(2, 8)
        )

        status_line = ttk.Frame(win)
        status_line.pack(fill="x", padx=10, pady=(0, 6))
        ttk.Label(status_line, textvariable=self.syn_status_var, font=("Segoe UI", 10, "bold")).pack(side="left")

        self.syn_canvas = tk.Canvas(win, height=280, bg="#0f1720", highlightthickness=1, highlightbackground="#314157")
        self.syn_canvas.pack(fill="x", padx=10, pady=(0, 8))

        log_box = ttk.LabelFrame(win, text="Synthetic Trade Log")
        log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.syn_text = scrolledtext.ScrolledText(log_box, wrap="word", font=("Consolas", 10))
        self.syn_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.syn_text.insert("1.0", "Press RUN SYNTH TEST.\n")
        self.syn_text.configure(state="disabled")

        def _on_close():
            try:
                win.destroy()
            finally:
                self.synthetic_window = None

        win.protocol("WM_DELETE_WINDOW", _on_close)

    def run_synthetic_test(self):
        if self.synthetic_window is None or not self.synthetic_window.winfo_exists():
            return
        try:
            start = self._as_float(self.syn_vars["start"].get(), "Start", 0.01, 1_000_000)
            target = self._as_float(self.syn_vars["target"].get(), "Target", 0.02, 10_000_000)
            if target <= start:
                raise ValueError("Target must be greater than start.")
            max_trades = self._as_int(self.syn_vars["max_trades"].get(), "Max trades", 10, 5000)
            hold_minutes = self._as_int(self.syn_vars["hold_minutes"].get(), "Hold min", 5, 60)
            if hold_minutes not in {5, 15, 30, 60}:
                raise ValueError("Hold min: use 5, 15, 30 or 60.")
            win_rate = self._as_float(self.syn_vars["win_rate"].get(), "Win-rate", 1, 99.9)
            stake_pct = self._as_float(self.syn_vars["stake_pct"].get(), "Stake %", 1, 100)
            win_min = self._as_float(self.syn_vars["win_min"].get(), "Win % min", 0.1, 300)
            win_max = self._as_float(self.syn_vars["win_max"].get(), "Win % max", 0.1, 300)
            loss_min = self._as_float(self.syn_vars["loss_min"].get(), "Loss % min", 0.1, 300)
            loss_max = self._as_float(self.syn_vars["loss_max"].get(), "Loss % max", 0.1, 300)
            attempts = self._as_int(self.syn_vars["attempts"].get(), "Retry runs", 1, 50)
            if win_max < win_min:
                raise ValueError("Win % max must be >= Win % min.")
            if loss_max < loss_min:
                raise ValueError("Loss % max must be >= Loss % min.")
            goal_bias = bool(self.syn_vars["goal_bias"].get())
        except ValueError as exc:
            messagebox.showerror("Synthetic test", str(exc))
            return

        result = self._simulate_synthetic_test(
            start=start,
            target=target,
            max_trades=max_trades,
            hold_minutes=hold_minutes,
            base_win_rate=win_rate,
            stake_pct=stake_pct,
            win_min=win_min,
            win_max=win_max,
            loss_min=loss_min,
            loss_max=loss_max,
            goal_bias=goal_bias,
            attempts=attempts,
        )

        reached = result["reached"]
        final_eq = result["final_equity"]
        trades = result["trades"]
        win_pct = result["win_rate"]
        summary = (
            f"Reached: {reached} | Equity: {final_eq:.2f} | Trades: {trades} | "
            f"Win-rate: {win_pct:.1f}% | Hold: {hold_minutes}m"
        )
        self.syn_status_var.set(summary)

        if self.syn_text is not None:
            self.syn_text.configure(state="normal")
            self.syn_text.delete("1.0", tk.END)
            self.syn_text.insert(tk.END, result["log"])
            self.syn_text.configure(state="disabled")
            self.syn_text.see("1.0")

        self._draw_synthetic_curve(result["equity_curve"], start, target)
        tag = "buy" if reached else "warn"
        self._append_event(
            "-",
            "SYNTH_PASS" if reached else "SYNTH_FAIL",
            "",
            "",
            f"{final_eq:+.2f}",
            "",
            summary,
            tag,
        )

    def _simulate_synthetic_test(
        self,
        start,
        target,
        max_trades,
        hold_minutes,
        base_win_rate,
        stake_pct,
        win_min,
        win_max,
        loss_min,
        loss_max,
        goal_bias,
        attempts,
    ):
        best = None
        tries = max(1, attempts if goal_bias else 1)
        for i in range(tries):
            random.seed(time.time_ns() + i * 7919)
            equity = float(start)
            curve = [equity]
            rows = []
            wins = 0
            losses = 0
            for t in range(1, max_trades + 1):
                gap = max(0.0, target - equity) / max(target, 1.0)
                p = float(base_win_rate) / 100.0
                if goal_bias:
                    p = min(0.96, max(0.05, p + 0.24 * gap))
                is_win = random.random() < p
                if is_win:
                    move_pct = random.uniform(win_min, win_max)
                    if goal_bias:
                        move_pct *= 1.0 + 0.45 * gap
                    signed_pct = move_pct / 100.0
                    wins += 1
                    side = "WIN"
                else:
                    move_pct = random.uniform(loss_min, loss_max)
                    if goal_bias:
                        move_pct *= max(0.5, 1.0 - 0.35 * gap)
                    signed_pct = -move_pct / 100.0
                    losses += 1
                    side = "LOSS"

                exposure = equity * (stake_pct / 100.0)
                pnl = exposure * signed_pct
                equity = max(0.01, equity + pnl)
                curve.append(equity)
                rows.append(
                    {
                        "trade": t,
                        "side": side,
                        "pnl": pnl,
                        "equity": equity,
                        "move": signed_pct * 100.0,
                    }
                )
                if equity >= target:
                    break

            total = len(rows)
            reached = equity >= target
            win_rate = (wins / total * 100.0) if total else 0.0
            item = {
                "reached": reached,
                "final_equity": equity,
                "equity_curve": curve,
                "rows": rows,
                "trades": total,
                "win_rate": win_rate,
                "wins": wins,
                "losses": losses,
                "hold_minutes": hold_minutes,
                "attempt": i + 1,
            }
            if reached:
                best = item
                break
            if best is None or item["final_equity"] > best["final_equity"]:
                best = item

        assert best is not None
        preview = []
        preview.append(
            f"Synthetic quick test | attempt={best['attempt']} | hold={hold_minutes}m | "
            f"start={start:.2f} -> target={target:.2f}"
        )
        preview.append(
            f"result: reached={best['reached']} final={best['final_equity']:.2f} "
            f"trades={best['trades']} wins={best['wins']} losses={best['losses']} "
            f"win_rate={best['win_rate']:.1f}%"
        )
        preview.append("")
        preview.append("trade  side   move%   pnl      equity")
        preview.append("-------------------------------------------")
        rows = best["rows"]
        head = rows[:15]
        tail = rows[-8:] if len(rows) > 23 else []
        for r in head:
            preview.append(
                f"{r['trade']:>5}  {r['side']:<5} {r['move']:>6.2f}  {r['pnl']:>7.2f}  {r['equity']:>8.2f}"
            )
        if tail:
            preview.append("...")
            for r in tail:
                preview.append(
                    f"{r['trade']:>5}  {r['side']:<5} {r['move']:>6.2f}  {r['pnl']:>7.2f}  {r['equity']:>8.2f}"
                )
        best["log"] = "\n".join(preview) + "\n"
        return best

    def _draw_synthetic_curve(self, values, start, target):
        if self.syn_canvas is None or not values:
            return
        c = self.syn_canvas
        c.delete("all")
        c.update_idletasks()
        w = max(640, int(c.winfo_width()))
        h = max(220, int(c.winfo_height()))
        left, top, right, bottom = 48, 24, w - 20, h - 36
        c.create_rectangle(left, top, right, bottom, outline="#314157")

        lo = min(min(values), start, target)
        hi = max(max(values), start, target)
        if hi <= lo:
            hi = lo + 1.0

        def x_of(idx):
            if len(values) == 1:
                return left
            return left + (right - left) * idx / (len(values) - 1)

        def y_of(v):
            return bottom - (v - lo) / (hi - lo) * (bottom - top)

        c.create_line(left, y_of(start), right, y_of(start), fill="#6d7b8a", dash=(3, 3))
        c.create_line(left, y_of(target), right, y_of(target), fill="#8f5a2a", dash=(3, 3))
        c.create_text(left + 4, y_of(start) - 8, text=f"start {start:.2f}", fill="#9fb2bf", anchor="w")
        c.create_text(left + 4, y_of(target) - 8, text=f"target {target:.2f}", fill="#c99a6a", anchor="w")

        points = []
        for i, v in enumerate(values):
            points.extend([x_of(i), y_of(v)])
        color = "#3bc16e" if values[-1] >= target else "#3a8dde"
        c.create_line(points, fill=color, width=2)
        c.create_text(right, top - 8, text=f"last {values[-1]:.2f}", fill="#d6dee6", anchor="e")

    def _as_float(self, raw, field, min_val, max_val=None):
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{field}: enter a number") from exc
        if value < min_val:
            raise ValueError(f"{field}: minimum is {min_val}")
        if max_val is not None and value > max_val:
            raise ValueError(f"{field}: maximum is {max_val}")
        return value

    def _as_int(self, raw, field, min_val, max_val=None):
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{field}: enter an integer") from exc
        if value < min_val:
            raise ValueError(f"{field}: minimum is {min_val}")
        if max_val is not None and value > max_val:
            raise ValueError(f"{field}: maximum is {max_val}")
        return value

    def _on_close(self):
        self.stop_bot()
        self.after(250, self.destroy)


def main():
    app = UltraSimpleGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
