import os
import json
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


PROFILE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_profiles.json")
DEFAULT_PROFILES = {
    "Target 70-75 (Recommended)": {
        "mode": "demo",
        "symbols": "AAPL MSFT NVDA",
        "interval": "5m",
        "lookback_bars": 600,
        "poll_seconds": 30,
        "reoptimize_every": 10,
        "initial_capital": 10,
        "target_capital": 100,
        "top_n": 3,
        "min_trades": 5,
        "required_win_min": 70,
        "required_win_max": 75,
        "demo_train_fraction": 0.7,
        "demo_speed_ms": 80,
        "max_loops": 0,
        "stop_on_target": True,
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
    "Balanced 65-80": {
        "mode": "demo",
        "symbols": "AAPL MSFT NVDA",
        "interval": "5m",
        "lookback_bars": 700,
        "poll_seconds": 20,
        "reoptimize_every": 6,
        "initial_capital": 50,
        "target_capital": 150,
        "top_n": 5,
        "min_trades": 6,
        "required_win_min": 65,
        "required_win_max": 80,
        "demo_train_fraction": 0.7,
        "demo_speed_ms": 50,
        "max_loops": 0,
        "stop_on_target": True,
        "risk": {
            "fee_rate": 0.0005,
            "slippage": 0.0004,
            "risk_per_trade": 0.012,
            "max_position_pct": 0.25,
            "stop_loss_pct": 0.02,
            "take_profit_pct": 0.05,
            "max_open_positions": 3,
        },
    },
    "Conservative 70-72": {
        "mode": "demo",
        "symbols": "AAPL MSFT",
        "interval": "15m",
        "lookback_bars": 800,
        "poll_seconds": 30,
        "reoptimize_every": 8,
        "initial_capital": 100,
        "target_capital": 150,
        "top_n": 5,
        "min_trades": 8,
        "required_win_min": 70,
        "required_win_max": 72,
        "demo_train_fraction": 0.75,
        "demo_speed_ms": 60,
        "max_loops": 0,
        "stop_on_target": True,
        "risk": {
            "fee_rate": 0.0005,
            "slippage": 0.0002,
            "risk_per_trade": 0.006,
            "max_position_pct": 0.18,
            "stop_loss_pct": 0.015,
            "take_profit_pct": 0.03,
            "max_open_positions": 2,
        },
    },
}


class TradingBotGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Adaptive Trading Bot GUI (Paper Mode)")
        self.geometry("1260x820")
        self.minsize(1080, 700)

        self.process: subprocess.Popen | None = None
        self.worker: threading.Thread | None = None
        self.events: queue.Queue = queue.Queue()
        self.equity_points: list[tuple[int, float]] = []
        self.symbol_strategy: dict[str, str] = {}
        self.custom_profiles: dict[str, dict] = {}
        self.profiles: dict[str, dict] = {}

        self._build_vars()
        self._build_ui()
        self._load_profiles()
        self._refresh_profile_list()
        if self.profile_var.get():
            self._apply_profile(self.profile_var.get())

        self.after(120, self._drain_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_vars(self) -> None:
        self.profile_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="demo")
        self.symbols_var = tk.StringVar(value="AAPL MSFT NVDA")
        self.interval_var = tk.StringVar(value="5m")
        self.lookback_var = tk.StringVar(value="600")
        self.poll_var = tk.StringVar(value="30")
        self.reoptimize_var = tk.StringVar(value="10")
        self.initial_capital_var = tk.StringVar(value="10")
        self.target_capital_var = tk.StringVar(value="100")
        self.top_n_var = tk.StringVar(value="3")
        self.min_trades_var = tk.StringVar(value="5")
        self.required_win_min_var = tk.StringVar(value="70")
        self.required_win_max_var = tk.StringVar(value="75")
        self.demo_train_fraction_var = tk.StringVar(value="0.7")
        self.demo_speed_ms_var = tk.StringVar(value="80")
        self.max_loops_var = tk.StringVar(value="0")
        self.fee_rate_var = tk.StringVar(value="0.0005")
        self.slippage_var = tk.StringVar(value="0.0002")
        self.risk_per_trade_var = tk.StringVar(value="0.01")
        self.max_position_pct_var = tk.StringVar(value="0.25")
        self.stop_loss_pct_var = tk.StringVar(value="0.02")
        self.take_profit_pct_var = tk.StringVar(value="0.04")
        self.max_open_positions_var = tk.StringVar(value="3")
        self.stop_on_target_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Idle")

    def _build_ui(self) -> None:
        profile_frame = ttk.LabelFrame(self, text="Profiles")
        profile_frame.pack(fill="x", padx=10, pady=(10, 6))
        profile_frame.columnconfigure(1, weight=1)
        ttk.Label(profile_frame, text="Profile").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.profile_cb = ttk.Combobox(profile_frame, textvariable=self.profile_var, state="readonly")
        self.profile_cb.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        self.profile_cb.bind("<<ComboboxSelected>>", lambda _: self.apply_selected_profile())
        ttk.Button(profile_frame, text="Apply", command=self.apply_selected_profile).grid(
            row=0, column=2, padx=6, pady=6
        )
        ttk.Button(profile_frame, text="Save Current", command=self.save_current_profile).grid(
            row=0, column=3, padx=6, pady=6
        )
        ttk.Button(profile_frame, text="Delete Custom", command=self.delete_selected_profile).grid(
            row=0, column=4, padx=6, pady=6
        )

        controls = ttk.LabelFrame(self, text="Run Settings")
        controls.pack(fill="x", padx=10, pady=6)
        for col in range(8):
            controls.columnconfigure(col, weight=1)

        ttk.Label(controls, text="Mode").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        mode_cb = ttk.Combobox(
            controls, textvariable=self.mode_var, values=["demo", "live", "backtest"], state="readonly", width=10
        )
        mode_cb.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Symbols").grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.symbols_var).grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Interval").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        interval_cb = ttk.Combobox(
            controls,
            textvariable=self.interval_var,
            values=["1m", "5m", "15m", "30m", "60m", "1d"],
            state="readonly",
            width=10,
        )
        interval_cb.grid(row=1, column=2, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Lookback Bars").grid(row=0, column=3, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.lookback_var).grid(row=1, column=3, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Poll Seconds").grid(row=0, column=4, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.poll_var).grid(row=1, column=4, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Reoptimize Every").grid(row=0, column=5, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.reoptimize_var).grid(row=1, column=5, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Initial Capital").grid(row=0, column=6, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.initial_capital_var).grid(row=1, column=6, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Target Capital").grid(row=0, column=7, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.target_capital_var).grid(row=1, column=7, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Top N Strategies").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.top_n_var).grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Min Trades").grid(row=2, column=1, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.min_trades_var).grid(row=3, column=1, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Win Min %").grid(row=2, column=2, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.required_win_min_var).grid(row=3, column=2, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Win Max %").grid(row=2, column=3, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.required_win_max_var).grid(row=3, column=3, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Demo Train Fraction").grid(row=2, column=4, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.demo_train_fraction_var).grid(
            row=3, column=4, sticky="ew", padx=6, pady=(0, 8)
        )

        ttk.Label(controls, text="Demo Speed (ms)").grid(row=2, column=5, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.demo_speed_ms_var).grid(row=3, column=5, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(controls, text="Max Loops (0 = no limit)").grid(row=2, column=6, sticky="w", padx=6, pady=6)
        ttk.Entry(controls, textvariable=self.max_loops_var).grid(row=3, column=6, sticky="ew", padx=6, pady=(0, 8))

        ttk.Checkbutton(controls, text="Stop on target", variable=self.stop_on_target_var).grid(
            row=3, column=7, sticky="w", padx=6, pady=(0, 8)
        )

        risk_frame = ttk.LabelFrame(self, text="Risk Parameters")
        risk_frame.pack(fill="x", padx=10, pady=6)
        for col in range(7):
            risk_frame.columnconfigure(col, weight=1)

        ttk.Label(risk_frame, text="Fee Rate").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(risk_frame, textvariable=self.fee_rate_var).grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(risk_frame, text="Slippage").grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ttk.Entry(risk_frame, textvariable=self.slippage_var).grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(risk_frame, text="Risk per Trade").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        ttk.Entry(risk_frame, textvariable=self.risk_per_trade_var).grid(
            row=1, column=2, sticky="ew", padx=6, pady=(0, 8)
        )

        ttk.Label(risk_frame, text="Max Position %").grid(row=0, column=3, sticky="w", padx=6, pady=6)
        ttk.Entry(risk_frame, textvariable=self.max_position_pct_var).grid(
            row=1, column=3, sticky="ew", padx=6, pady=(0, 8)
        )

        ttk.Label(risk_frame, text="Stop Loss %").grid(row=0, column=4, sticky="w", padx=6, pady=6)
        ttk.Entry(risk_frame, textvariable=self.stop_loss_pct_var).grid(
            row=1, column=4, sticky="ew", padx=6, pady=(0, 8)
        )

        ttk.Label(risk_frame, text="Take Profit %").grid(row=0, column=5, sticky="w", padx=6, pady=6)
        ttk.Entry(risk_frame, textvariable=self.take_profit_pct_var).grid(
            row=1, column=5, sticky="ew", padx=6, pady=(0, 8)
        )

        ttk.Label(risk_frame, text="Max Open Positions").grid(row=0, column=6, sticky="w", padx=6, pady=6)
        ttk.Entry(risk_frame, textvariable=self.max_open_positions_var).grid(
            row=1, column=6, sticky="ew", padx=6, pady=(0, 8)
        )

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_bot)
        self.start_btn.pack(side="left", padx=(0, 8))
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_bot, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side="left")

        ttk.Label(self, textvariable=self.status_var).pack(fill="x", padx=12, pady=(0, 8))

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=3)
        body.add(right, weight=2)

        left.rowconfigure(0, weight=2)
        left.rowconfigure(1, weight=2)
        left.columnconfigure(0, weight=1)

        chart_wrap = ttk.LabelFrame(left, text="Equity Chart")
        chart_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        self.chart = tk.Canvas(chart_wrap, bg="#101418", highlightthickness=0)
        self.chart.pack(fill="both", expand=True)
        self.chart.bind("<Configure>", lambda _: self._redraw_chart())

        trades_wrap = ttk.LabelFrame(left, text="Trade Events")
        trades_wrap.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=(6, 0))
        trades_wrap.rowconfigure(0, weight=1)
        trades_wrap.columnconfigure(0, weight=1)

        columns = ("ts", "symbol", "side", "qty", "price", "pnl", "reason", "strategy")
        self.trade_tree = ttk.Treeview(trades_wrap, columns=columns, show="headings", height=12)
        headings = {
            "ts": "Time",
            "symbol": "Symbol",
            "side": "Side",
            "qty": "Qty",
            "price": "Price",
            "pnl": "PnL",
            "reason": "Reason",
            "strategy": "Strategy",
        }
        widths = {"ts": 150, "symbol": 70, "side": 60, "qty": 70, "price": 70, "pnl": 70, "reason": 80, "strategy": 120}
        for col in columns:
            self.trade_tree.heading(col, text=headings[col])
            self.trade_tree.column(col, width=widths[col], anchor="center")
        self.trade_tree.grid(row=0, column=0, sticky="nsew")
        trade_scroll = ttk.Scrollbar(trades_wrap, orient="vertical", command=self.trade_tree.yview)
        trade_scroll.grid(row=0, column=1, sticky="ns")
        self.trade_tree.configure(yscrollcommand=trade_scroll.set)

        logs_wrap = ttk.LabelFrame(right, text="Live Logs")
        logs_wrap.pack(fill="both", expand=True, padx=(6, 0))
        self.log_box = scrolledtext.ScrolledText(
            logs_wrap, state="disabled", wrap="word", font=("Consolas", 10)
        )
        self.log_box.pack(fill="both", expand=True, padx=6, pady=6)

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
        names = sorted(self.profiles.keys())
        self.profile_cb.configure(values=names)
        if not names:
            self.profile_var.set("")
            return
        if self.profile_var.get() not in names:
            recommended = "Target 70-75 (Recommended)"
            self.profile_var.set(recommended if recommended in names else names[0])

    def apply_selected_profile(self) -> None:
        name = self.profile_var.get()
        if not name:
            return
        self._apply_profile(name)
        self.status_var.set(f"Profile applied: {name}")

    def _apply_profile(self, name: str) -> None:
        data = self.profiles.get(name)
        if not data:
            return
        risk = data.get("risk", {})
        self.mode_var.set(str(data.get("mode", "demo")))
        self.symbols_var.set(str(data.get("symbols", "AAPL")))
        self.interval_var.set(str(data.get("interval", "5m")))
        self.lookback_var.set(str(data.get("lookback_bars", 600)))
        self.poll_var.set(str(data.get("poll_seconds", 30)))
        self.reoptimize_var.set(str(data.get("reoptimize_every", 10)))
        self.initial_capital_var.set(str(data.get("initial_capital", 10)))
        self.target_capital_var.set(str(data.get("target_capital", 100)))
        self.top_n_var.set(str(data.get("top_n", 3)))
        self.min_trades_var.set(str(data.get("min_trades", 5)))
        self.required_win_min_var.set(str(data.get("required_win_min", 70)))
        self.required_win_max_var.set(str(data.get("required_win_max", 75)))
        self.demo_train_fraction_var.set(str(data.get("demo_train_fraction", 0.7)))
        self.demo_speed_ms_var.set(str(data.get("demo_speed_ms", 80)))
        self.max_loops_var.set(str(data.get("max_loops", 0)))
        self.stop_on_target_var.set(bool(data.get("stop_on_target", True)))
        self.fee_rate_var.set(str(risk.get("fee_rate", 0.0005)))
        self.slippage_var.set(str(risk.get("slippage", 0.0002)))
        self.risk_per_trade_var.set(str(risk.get("risk_per_trade", 0.01)))
        self.max_position_pct_var.set(str(risk.get("max_position_pct", 0.25)))
        self.stop_loss_pct_var.set(str(risk.get("stop_loss_pct", 0.02)))
        self.take_profit_pct_var.set(str(risk.get("take_profit_pct", 0.04)))
        self.max_open_positions_var.set(str(risk.get("max_open_positions", 3)))

    def _collect_profile(self) -> dict:
        return {
            "mode": self.mode_var.get().strip(),
            "symbols": self.symbols_var.get().strip(),
            "interval": self.interval_var.get().strip(),
            "lookback_bars": int(self.lookback_var.get().strip()),
            "poll_seconds": int(self.poll_var.get().strip()),
            "reoptimize_every": int(self.reoptimize_var.get().strip()),
            "initial_capital": float(self.initial_capital_var.get().strip()),
            "target_capital": float(self.target_capital_var.get().strip()),
            "top_n": int(self.top_n_var.get().strip()),
            "min_trades": int(self.min_trades_var.get().strip()),
            "required_win_min": float(self.required_win_min_var.get().strip()),
            "required_win_max": float(self.required_win_max_var.get().strip()),
            "demo_train_fraction": float(self.demo_train_fraction_var.get().strip()),
            "demo_speed_ms": float(self.demo_speed_ms_var.get().strip()),
            "max_loops": int(self.max_loops_var.get().strip()),
            "stop_on_target": bool(self.stop_on_target_var.get()),
            "risk": {
                "fee_rate": float(self.fee_rate_var.get().strip()),
                "slippage": float(self.slippage_var.get().strip()),
                "risk_per_trade": float(self.risk_per_trade_var.get().strip()),
                "max_position_pct": float(self.max_position_pct_var.get().strip()),
                "stop_loss_pct": float(self.stop_loss_pct_var.get().strip()),
                "take_profit_pct": float(self.take_profit_pct_var.get().strip()),
                "max_open_positions": int(self.max_open_positions_var.get().strip()),
            },
        }

    def save_current_profile(self) -> None:
        try:
            profile = self._collect_profile()
        except Exception as exc:
            messagebox.showerror("Invalid settings", f"Cannot save profile: {exc}")
            return
        default_name = self.profile_var.get().strip() or "My Profile"
        name = simpledialog.askstring("Save Profile", "Profile name:", initialvalue=default_name)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        self.custom_profiles[name] = profile
        self.profiles[name] = profile
        self._save_custom_profiles()
        self._refresh_profile_list()
        self.profile_var.set(name)
        self.status_var.set(f"Profile saved: {name}")

    def delete_selected_profile(self) -> None:
        name = self.profile_var.get().strip()
        if not name:
            return
        if name in DEFAULT_PROFILES:
            messagebox.showinfo("Protected profile", "Default profiles cannot be deleted.")
            return
        if name not in self.custom_profiles:
            return
        del self.custom_profiles[name]
        if name in self.profiles:
            del self.profiles[name]
        self._save_custom_profiles()
        self._refresh_profile_list()
        if self.profile_var.get():
            self._apply_profile(self.profile_var.get())
        self.status_var.set(f"Profile deleted: {name}")

    def clear_log(self) -> None:
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.configure(state="disabled")

    def start_bot(self) -> None:
        if self.process is not None and self.process.poll() is None:
            messagebox.showinfo("Already running", "Bot is already running.")
            return

        try:
            cmd = self._build_command()
        except ValueError as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return

        self._reset_run_views()
        self._set_running(True)
        self.status_var.set("Starting...")
        self._append_log(" ".join(cmd))

        self.worker = threading.Thread(target=self._run_process, args=(cmd,), daemon=True)
        self.worker.start()

    def stop_bot(self) -> None:
        proc = self.process
        if proc is None or proc.poll() is not None:
            self._set_running(False)
            self.status_var.set("Idle")
            return
        self.status_var.set("Stopping...")
        self._append_log("Stopping process...")
        try:
            proc.terminate()
        except OSError:
            pass

    def _run_process(self, cmd: list[str]) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as exc:
            self.events.put(("error", f"Failed to start process: {exc}"))
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
                    self.status_var.set("Error")
                    self._set_running(False)
                elif kind == "done":
                    self.status_var.set(f"Stopped (exit code {payload})")
                    self._set_running(False)
        except queue.Empty:
            pass
        self.after(120, self._drain_events)

    def _build_command(self) -> list[str]:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adaptive_trading_bot.py")
        if not os.path.exists(script_path):
            raise ValueError(f"Cannot find script: {script_path}")

        mode = self.mode_var.get().strip()
        if mode not in {"demo", "live", "backtest"}:
            raise ValueError("Mode must be demo, live or backtest.")

        symbols = [s.strip().upper() for s in re.split(r"[,\s]+", self.symbols_var.get()) if s.strip()]
        if not symbols:
            raise ValueError("Enter at least one symbol.")

        interval = self.interval_var.get().strip()
        if not interval:
            raise ValueError("Interval is required.")

        lookback = self._as_int(self.lookback_var.get(), "Lookback bars", min_value=120)
        poll = self._as_int(self.poll_var.get(), "Poll seconds", min_value=1)
        reoptimize = self._as_int(self.reoptimize_var.get(), "Reoptimize every", min_value=1)
        initial_capital = self._as_float(self.initial_capital_var.get(), "Initial capital", min_value=0.01)
        target_capital = self._as_float(self.target_capital_var.get(), "Target capital", min_value=0.01)
        top_n = self._as_int(self.top_n_var.get(), "Top N", min_value=1)
        min_trades = self._as_int(self.min_trades_var.get(), "Min trades", min_value=0)
        required_win_min = self._as_float(self.required_win_min_var.get(), "Win min", min_value=0, max_value=100)
        required_win_max = self._as_float(self.required_win_max_var.get(), "Win max", min_value=0, max_value=100)
        if required_win_max < required_win_min:
            raise ValueError("Win max must be >= Win min.")
        demo_train_fraction = self._as_float(
            self.demo_train_fraction_var.get(), "Demo train fraction", min_value=0.5, max_value=0.9
        )
        demo_speed_ms = self._as_float(self.demo_speed_ms_var.get(), "Demo speed (ms)", min_value=0)
        max_loops = self._as_int(self.max_loops_var.get(), "Max loops", min_value=0)
        fee_rate = self._as_float(self.fee_rate_var.get(), "Fee rate", min_value=0)
        slippage = self._as_float(self.slippage_var.get(), "Slippage", min_value=0)
        risk_per_trade = self._as_float(self.risk_per_trade_var.get(), "Risk per trade", min_value=0, max_value=1)
        max_position_pct = self._as_float(
            self.max_position_pct_var.get(), "Max position pct", min_value=0, max_value=1
        )
        stop_loss_pct = self._as_float(self.stop_loss_pct_var.get(), "Stop loss pct", min_value=0, max_value=1)
        take_profit_pct = self._as_float(self.take_profit_pct_var.get(), "Take profit pct", min_value=0, max_value=5)
        max_open_positions = self._as_int(self.max_open_positions_var.get(), "Max open positions", min_value=1)

        cmd = [
            sys.executable,
            "-u",
            script_path,
            "--mode",
            mode,
            "--symbols",
            *symbols,
            "--interval",
            interval,
            "--lookback-bars",
            str(lookback),
            "--poll-seconds",
            str(poll),
            "--reoptimize-every",
            str(reoptimize),
            "--initial-capital",
            str(initial_capital),
            "--target-capital",
            str(target_capital),
            "--top-n",
            str(top_n),
            "--min-trades",
            str(min_trades),
            "--required-win-min",
            str(required_win_min),
            "--required-win-max",
            str(required_win_max),
            "--demo-train-fraction",
            str(demo_train_fraction),
            "--demo-speed-ms",
            str(demo_speed_ms),
            "--fee-rate",
            str(fee_rate),
            "--slippage",
            str(slippage),
            "--risk-per-trade",
            str(risk_per_trade),
            "--max-position-pct",
            str(max_position_pct),
            "--stop-loss-pct",
            str(stop_loss_pct),
            "--take-profit-pct",
            str(take_profit_pct),
            "--max-open-positions",
            str(max_open_positions),
            "--max-loops",
            str(max_loops),
        ]
        if not self.stop_on_target_var.get():
            cmd.append("--no-stop-on-target")
        return cmd

    def _as_int(self, raw: str, field_name: str, min_value: int, max_value: int | None = None) -> int:
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be an integer.") from exc
        if value < min_value:
            raise ValueError(f"{field_name} must be >= {min_value}.")
        if max_value is not None and value > max_value:
            raise ValueError(f"{field_name} must be <= {max_value}.")
        return value

    def _as_float(
        self, raw: str, field_name: str, min_value: float, max_value: float | None = None
    ) -> float:
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a number.") from exc
        if value < min_value:
            raise ValueError(f"{field_name} must be >= {min_value}.")
        if max_value is not None and value > max_value:
            raise ValueError(f"{field_name} must be <= {max_value}.")
        return value

    def _append_log(self, line: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, line + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")

    def _parse_log_line(self, line: str) -> None:
        ts = self._extract_ts(line)

        buy = BUY_RE.search(line)
        if buy:
            symbol = buy.group("symbol")
            strategy = buy.group("strategy")
            self.symbol_strategy[symbol] = strategy
            self._insert_trade(
                ts=ts,
                symbol=symbol,
                side="BUY",
                qty=buy.group("qty"),
                price=buy.group("price"),
                pnl="",
                reason="",
                strategy=strategy,
            )
            return

        sell = SELL_RE.search(line)
        if sell:
            symbol = sell.group("symbol")
            strategy = self.symbol_strategy.get(symbol, "")
            self._insert_trade(
                ts=ts,
                symbol=symbol,
                side="SELL",
                qty=sell.group("qty"),
                price=sell.group("price"),
                pnl=sell.group("pnl"),
                reason=sell.group("reason"),
                strategy=strategy,
            )
            return

        loop = LOOP_RE.search(line)
        if loop:
            loop_n = int(loop.group("loop"))
            equity = float(loop.group("equity"))
            self.equity_points.append((loop_n, equity))
            if len(self.equity_points) > 500:
                self.equity_points = self.equity_points[-500:]
            self.status_var.set(
                f"Running | loop={loop_n} | equity={equity:.2f} | positions={loop.group('positions')}"
            )
            self._redraw_chart()

    def _insert_trade(
        self, ts: str, symbol: str, side: str, qty: str, price: str, pnl: str, reason: str, strategy: str
    ) -> None:
        self.trade_tree.insert("", 0, values=(ts, symbol, side, qty, price, pnl, reason, strategy))

    def _extract_ts(self, line: str) -> str:
        if "|" in line:
            return line.split("|", 1)[0].strip()
        return ""

    def _reset_run_views(self) -> None:
        self.equity_points.clear()
        self.symbol_strategy.clear()
        for item in self.trade_tree.get_children():
            self.trade_tree.delete(item)
        self._redraw_chart()

    def _redraw_chart(self) -> None:
        canvas = self.chart
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 40 or height < 40:
            return

        pad_l, pad_r, pad_t, pad_b = 56, 24, 20, 36
        x0, y0 = pad_l, pad_t
        x1, y1 = width - pad_r, height - pad_b
        canvas.create_rectangle(x0, y0, x1, y1, outline="#45525a")

        if not self.equity_points:
            canvas.create_text(width // 2, height // 2, text="No equity data yet", fill="#c6d0d8")
            return

        loops = [pt[0] for pt in self.equity_points]
        values = [pt[1] for pt in self.equity_points]
        min_v = min(values)
        max_v = max(values)
        if abs(max_v - min_v) < 1e-9:
            min_v -= 1.0
            max_v += 1.0

        min_loop = min(loops)
        max_loop = max(loops)
        if max_loop == min_loop:
            max_loop += 1

        def sx(loop_n: int) -> float:
            return x0 + ((loop_n - min_loop) / (max_loop - min_loop)) * (x1 - x0)

        def sy(value: float) -> float:
            return y1 - ((value - min_v) / (max_v - min_v)) * (y1 - y0)

        coords: list[float] = []
        for loop_n, val in self.equity_points:
            coords.extend([sx(loop_n), sy(val)])
        if len(coords) >= 4:
            canvas.create_line(*coords, fill="#4cc2ff", width=2)

        try:
            target = float(self.target_capital_var.get())
            if min_v <= target <= max_v:
                ty = sy(target)
                canvas.create_line(x0, ty, x1, ty, fill="#ff7e6b", dash=(5, 3))
                canvas.create_text(x1 - 4, ty - 9, text=f"target {target:.2f}", fill="#ff7e6b", anchor="e")
        except ValueError:
            pass

        latest = values[-1]
        canvas.create_text(x0, y0 - 8, text=f"max {max_v:.2f}", fill="#9fb2bf", anchor="w")
        canvas.create_text(x0, y1 + 14, text=f"min {min_v:.2f}", fill="#9fb2bf", anchor="w")
        canvas.create_text(x1, y0 - 8, text=f"latest {latest:.2f}", fill="#9fb2bf", anchor="e")

    def _set_running(self, running: bool) -> None:
        self.start_btn.configure(state="disabled" if running else "normal")
        self.stop_btn.configure(state="normal" if running else "disabled")

    def _on_close(self) -> None:
        self.stop_bot()
        self.after(250, self.destroy)


def main() -> None:
    # Keep backward compatibility for old launch command, but route to the ultra simple UI.
    try:
        from adaptive_trading_gui_ultra import main as ultra_main

        ultra_main()
        return
    except Exception:
        pass

    # Fallback: easy UI.
    try:
        from adaptive_trading_gui_easy import main as easy_main

        easy_main()
        return
    except Exception:
        pass

    app = TradingBotGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
