import argparse
import itertools
import json
import logging
import math
import os
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf

try:
    import ccxt  # type: ignore
except Exception:
    ccxt = None

LOG = logging.getLogger("adaptive_bot")
ALIAS = {"1h": "60m"}
PERIOD = {
    "1m": "7d", "2m": "60d", "5m": "60d", "15m": "60d", "30m": "60d",
    "60m": "730d", "90m": "60d", "1d": "10y", "1wk": "max", "1mo": "max",
}
CCXT_TF = {
    "1m": "1m",
    "2m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "60m": "1h",
    "90m": "1h",
    "1h": "1h",
    "1d": "1d",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.getenv("ADAPTIVE_TRADING_RUNTIME_DIR", BASE_DIR)
LOG_DIR = os.getenv("ADAPTIVE_TRADING_LOG_DIR", os.path.join(RUNTIME_DIR, "logs"))
os.makedirs(RUNTIME_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def runtime_file(name: str) -> str:
    return os.path.join(RUNTIME_DIR, name)


def rsi(s, p=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / p, adjust=False, min_periods=p).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / p, adjust=False, min_periods=p).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def macd(s, f=12, sl=26, sg=9):
    fe = s.ewm(span=f, adjust=False).mean()
    se = s.ewm(span=sl, adjust=False).mean()
    m = fe - se
    sig = m.ewm(span=sg, adjust=False).mean()
    return m, sig


def ema(s, p=20):
    return s.ewm(span=int(p), adjust=False).mean()


def bollinger(s, p=20, m=2.0):
    p = int(p)
    m = float(m)
    mid = s.rolling(p).mean()
    sd = s.rolling(p).std(ddof=0)
    up = mid + m * sd
    lo = mid - m * sd
    return mid, up, lo


def stochastic(high, low, close, p=14, smooth=3):
    p = int(p)
    smooth = int(smooth)
    ll = low.rolling(p).min()
    hh = high.rolling(p).max()
    k = 100 * (close - ll) / (hh - ll).replace(0, np.nan)
    d = k.rolling(smooth).mean()
    return k.fillna(50), d.fillna(50)


def cci(df, p=20):
    p = int(p)
    tp = (df.High + df.Low + df.Close) / 3.0
    ma = tp.rolling(p).mean()
    md = (tp - ma).abs().rolling(p).mean()
    out = (tp - ma) / (0.015 * md.replace(0, np.nan))
    return out.fillna(0)


def adx(df, p=14):
    p = int(p)
    high, low, close = df.High, df.Low, df.Close

    up = high.diff()
    down = -low.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / p, adjust=False, min_periods=p).mean()

    plus_di = 100 * plus_dm.ewm(alpha=1 / p, adjust=False, min_periods=p).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / p, adjust=False, min_periods=p).mean() / atr.replace(0, np.nan)

    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0)
    adx_line = dx.ewm(alpha=1 / p, adjust=False, min_periods=p).mean().fillna(0)
    return plus_di.fillna(0), minus_di.fillna(0), adx_line


def sig_sma(df, p):
    f = df.Close.rolling(int(p["fast"])).mean()
    s = df.Close.rolling(int(p["slow"])).mean()
    out = pd.Series(0, index=df.index)
    out[(f > s) & (f.shift(1) <= s.shift(1))] = 1
    out[(f < s) & (f.shift(1) >= s.shift(1))] = -1
    return out


def sig_ema(df, p):
    f = ema(df.Close, int(p["fast"]))
    s = ema(df.Close, int(p["slow"]))
    out = pd.Series(0, index=df.index)
    out[(f > s) & (f.shift(1) <= s.shift(1))] = 1
    out[(f < s) & (f.shift(1) >= s.shift(1))] = -1
    return out


def sig_rsi(df, p):
    x = rsi(df.Close, int(p["period"]))
    out = pd.Series(0, index=df.index)
    out[x <= float(p["buy"])] = 1
    out[x >= float(p["sell"])] = -1
    return out


def sig_macd(df, p):
    m, s = macd(df.Close, int(p["fast"]), int(p["slow"]), int(p["signal"]))
    out = pd.Series(0, index=df.index)
    out[(m > s) & (m.shift(1) <= s.shift(1))] = 1
    out[(m < s) & (m.shift(1) >= s.shift(1))] = -1
    return out


def sig_breakout(df, p):
    w = int(p["window"])
    hi = df.High.rolling(w).max().shift(1)
    lo = df.Low.rolling(w).min().shift(1)
    out = pd.Series(0, index=df.index)
    out[df.Close > hi] = 1
    out[df.Close < lo] = -1
    return out


def sig_bb_reversion(df, p):
    mid, up, lo = bollinger(df.Close, int(p["period"]), float(p["mult"]))
    out = pd.Series(0, index=df.index)
    out[(df.Close > lo) & (df.Close.shift(1) <= lo.shift(1))] = 1
    out[(df.Close < up) & (df.Close.shift(1) >= up.shift(1))] = -1
    out[(df.Close >= mid) & (df.Close.shift(1) < mid.shift(1))] = -1
    return out


def sig_stoch(df, p):
    k, d = stochastic(df.High, df.Low, df.Close, int(p["period"]), int(p["smooth"]))
    buy = float(p["buy"])
    sell = float(p["sell"])
    out = pd.Series(0, index=df.index)
    out[(k > d) & (k.shift(1) <= d.shift(1)) & (k <= buy)] = 1
    out[(k < d) & (k.shift(1) >= d.shift(1)) & (k >= sell)] = -1
    return out


def sig_cci(df, p):
    x = cci(df, int(p["period"]))
    buy = float(p["buy"])
    sell = float(p["sell"])
    out = pd.Series(0, index=df.index)
    out[x <= buy] = 1
    out[x >= sell] = -1
    return out


def sig_adx(df, p):
    plus_di, minus_di, adx_line = adx(df, int(p["period"]))
    min_adx = float(p["min_adx"])
    out = pd.Series(0, index=df.index)
    out[(adx_line >= min_adx) & (plus_di > minus_di) & (plus_di.shift(1) <= minus_di.shift(1))] = 1
    out[(adx_line >= min_adx) & (plus_di < minus_di) & (plus_di.shift(1) >= minus_di.shift(1))] = -1
    return out


def sig_roc(df, p):
    period = int(p["period"])
    threshold = float(p["threshold"])
    roc = df.Close.pct_change(periods=period) * 100.0
    out = pd.Series(0, index=df.index)
    out[(roc > threshold) & (roc.shift(1) <= threshold)] = 1
    out[(roc < -threshold) & (roc.shift(1) >= -threshold)] = -1
    return out


def grid(d):
    k = list(d)
    return [dict(zip(k, v)) for v in itertools.product(*(d[x] for x in k))]


def _catalog_basic():
    return {
        "SMA_CROSS": (sig_sma, [x for x in grid({"fast": [10, 20, 30], "slow": [50, 100, 150]}) if x["fast"] < x["slow"]]),
        "RSI_REVERSION": (sig_rsi, [x for x in grid({"period": [7, 14], "buy": [25, 30], "sell": [65, 70]}) if x["buy"] < x["sell"]]),
        "MACD_CROSS": (sig_macd, [{"fast": 8, "slow": 21, "signal": 5}, {"fast": 12, "slow": 26, "signal": 9}]),
        "BREAKOUT": (sig_breakout, [{"window": 20}, {"window": 55}]),
    }


def _catalog_extended():
    out = dict(_catalog_basic())
    out.update(
        {
            "EMA_CROSS": (sig_ema, [x for x in grid({"fast": [8, 13, 21], "slow": [34, 55, 89]}) if x["fast"] < x["slow"]]),
            "BB_REVERSION": (sig_bb_reversion, [{"period": 20, "mult": 2.0}, {"period": 20, "mult": 2.5}]),
            "STOCH_REV": (sig_stoch, [{"period": 14, "smooth": 3, "buy": 20, "sell": 80}, {"period": 10, "smooth": 3, "buy": 25, "sell": 75}]),
            "CCI_REVERSION": (sig_cci, [{"period": 20, "buy": -120, "sell": 120}, {"period": 14, "buy": -100, "sell": 100}]),
            "ADX_TREND": (sig_adx, [{"period": 14, "min_adx": 20}, {"period": 14, "min_adx": 25}]),
            "ROC_MOMENTUM": (sig_roc, [{"period": 5, "threshold": 0.5}, {"period": 10, "threshold": 1.0}]),
        }
    )
    return out


def _catalog_max():
    out = dict(_catalog_extended())
    out["SMA_CROSS"] = (sig_sma, [x for x in grid({"fast": [5, 8, 10, 13, 20, 30], "slow": [30, 50, 100, 150, 200]}) if x["fast"] < x["slow"]])
    out["EMA_CROSS"] = (sig_ema, [x for x in grid({"fast": [5, 8, 13, 21, 34], "slow": [34, 55, 89, 144]}) if x["fast"] < x["slow"]])
    out["RSI_REVERSION"] = (
        sig_rsi,
        [x for x in grid({"period": [5, 7, 14], "buy": [20, 25, 30], "sell": [65, 70, 75]}) if x["buy"] < x["sell"]],
    )
    out["BB_REVERSION"] = (
        sig_bb_reversion,
        [x for x in grid({"period": [14, 20, 30], "mult": [1.8, 2.0, 2.5]})],
    )
    out["STOCH_REV"] = (
        sig_stoch,
        [x for x in grid({"period": [10, 14, 21], "smooth": [2, 3, 4], "buy": [20, 25], "sell": [75, 80]})],
    )
    out["CCI_REVERSION"] = (
        sig_cci,
        [x for x in grid({"period": [14, 20, 30], "buy": [-150, -120, -100], "sell": [100, 120, 150]}) if x["buy"] < x["sell"]],
    )
    out["ADX_TREND"] = (
        sig_adx,
        [x for x in grid({"period": [10, 14, 20], "min_adx": [18, 20, 25, 30]})],
    )
    out["ROC_MOMENTUM"] = (
        sig_roc,
        [x for x in grid({"period": [3, 5, 8, 10, 14], "threshold": [0.3, 0.5, 0.8, 1.0]})],
    )
    out["BREAKOUT"] = (sig_breakout, [{"window": 10}, {"window": 20}, {"window": 55}, {"window": 100}])
    out["MACD_CROSS"] = (
        sig_macd,
        [{"fast": 6, "slow": 19, "signal": 4}, {"fast": 8, "slow": 21, "signal": 5}, {"fast": 12, "slow": 26, "signal": 9}],
    )
    return out


_STRAT_CACHE = {}


def build_strategy_catalog(pack):
    mode = str(pack or "extended").strip().lower()
    if mode not in {"basic", "extended", "max"}:
        mode = "extended"
    if mode in _STRAT_CACHE:
        return _STRAT_CACHE[mode]
    if mode == "basic":
        out = _catalog_basic()
    elif mode == "max":
        out = _catalog_max()
    else:
        out = _catalog_extended()
    _STRAT_CACHE[mode] = out
    return out


VALID_STRATEGIES = set(build_strategy_catalog("max").keys())


def normalize_strategy_filter(raw_strategy):
    if raw_strategy is None:
        return None
    if isinstance(raw_strategy, list):
        chosen = [str(x).upper().strip() for x in raw_strategy if str(x).strip()]
    else:
        text = str(raw_strategy).upper().strip()
        if text in {"", "AUTO", "ALL", "BEST"}:
            return None
        chosen = [x.strip() for x in text.split(",") if x.strip()]
    chosen = [x for x in chosen if x in VALID_STRATEGIES]
    return chosen or None


def _tf_for_exchange(interval):
    clean = ALIAS.get(interval, interval)
    return CCXT_TF.get(clean, "5m")


def _symbol_quote(symbol):
    if "/" in symbol:
        parts = symbol.split("/")
        if len(parts) == 2:
            return parts[1].upper()
    return None


def _init_exchange(cfg, require_auth=False):
    if ccxt is None:
        if require_auth:
            raise RuntimeError("ccxt is not installed. Install it first.")
        return None
    exchange_name = str(cfg.get("exchange", "binance")).lower().strip()
    ex_cls = getattr(ccxt, exchange_name, None)
    if ex_cls is None:
        raise ValueError(f"Unsupported exchange: {exchange_name}")

    params = {"enableRateLimit": True}
    api_key = str(cfg.get("api_key", "") or "").strip()
    api_secret = str(cfg.get("api_secret", "") or "").strip()
    api_password = str(cfg.get("api_password", "") or "").strip()
    if api_key:
        params["apiKey"] = api_key
    if api_secret:
        params["secret"] = api_secret
    if api_password:
        params["password"] = api_password
    if require_auth and (not api_key or not api_secret):
        raise ValueError("Live trading requires API key and API secret.")

    ex = ex_cls(params)
    ex.load_markets()
    return ex


def _load_bars_exchange(exchange, symbol, interval, lookback):
    tf = _tf_for_exchange(interval)
    limit = max(int(lookback), 120)
    rows = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms", utc=True)
    df = df.set_index("Timestamp")
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna()


def load_bars(symbol, interval, lookback, exchange=None):
    if exchange is not None:
        try:
            return _load_bars_exchange(exchange, symbol, interval, lookback)
        except Exception as exc:
            LOG.warning("[%s] exchange data load failed: %s", symbol, exc)
            return pd.DataFrame()
    interval = ALIAS.get(interval, interval)
    raw = yf.download(symbol, period=PERIOD.get(interval, "1y"), interval=interval, progress=False, auto_adjust=False, threads=False)
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0] for c in raw.columns]
    cols = {str(c).lower(): c for c in raw.columns}
    need = ["open", "high", "low", "close", "volume"]
    if any(x not in cols for x in need):
        return pd.DataFrame()
    df = raw[[cols["open"], cols["high"], cols["low"], cols["close"], cols["volume"]]].copy()
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df.dropna().tail(max(lookback, 120))


def ann(interval):
    return {"1m": 252 * 390, "5m": 252 * 78, "15m": 252 * 26, "60m": 252 * 6.5, "1d": 252}.get(interval, 252)


def interval_minutes(interval):
    clean = ALIAS.get(str(interval).strip(), str(interval).strip())
    if clean.endswith("m"):
        return max(1, int(clean[:-1] or 1))
    if clean.endswith("h"):
        return max(1, int(clean[:-1] or 1) * 60)
    if clean.endswith("d"):
        return max(1, int(clean[:-1] or 1) * 1440)
    if clean.endswith("wk"):
        return max(1, int(clean[:-2] or 1) * 10080)
    if clean.endswith("mo"):
        return max(1, int(clean[:-2] or 1) * 43200)
    return 5


def pos_size(cash, price, risk):
    cap_qty = cash * risk["max_position_pct"] / price
    if risk["stop_loss_pct"] > 0:
        risk_qty = cash * risk["risk_per_trade"] / (price * risk["stop_loss_pct"])
    else:
        risk_qty = cap_qty
    q = max(0.0, min(cap_qty, risk_qty))
    return math.floor(q * 10000) / 10000 if risk["allow_fractional"] else math.floor(q)


def _pnl_target_hit(entry_price, mark_price, risk):
    if entry_price <= 0:
        return False
    pnl_pct = (mark_price / entry_price - 1.0) * 100.0
    lo = float(risk.get("pnl_close_min_pct", 0.0) or 0.0)
    hi = float(risk.get("pnl_close_max_pct", 0.0) or 0.0)
    if lo <= 0 and hi <= 0:
        return False
    if hi > 0:
        if lo > 0:
            return (lo <= pnl_pct <= hi) or (pnl_pct > hi)
        return pnl_pct >= hi
    return pnl_pct >= lo


def _has_pnl_target(risk):
    lo = float(risk.get("pnl_close_min_pct", 0.0) or 0.0)
    hi = float(risk.get("pnl_close_max_pct", 0.0) or 0.0)
    return lo > 0 or hi > 0


def _has_fixed_hold(risk):
    return int(risk.get("fixed_hold_bars", 0) or 0) > 0


def _pnl_pct(entry_price, mark_price):
    if entry_price <= 0:
        return 0.0
    return (mark_price / entry_price - 1.0) * 100.0


def backtest(df, sig, risk, cap, interval):
    sig = sig.reindex(df.index).fillna(0)
    cash, q, cost, entry = float(cap), 0.0, 0.0, 0.0
    stop = take = None
    hold_bars = 0
    cooldown_until = -1
    min_hold = int(risk.get("min_hold_bars", 0) or 0)
    cooldown_bars = int(risk.get("cooldown_bars", 0) or 0)
    entry_delay = int(risk.get("entry_delay_bars", 0) or 0)
    fixed_hold = int(risk.get("fixed_hold_bars", 0) or 0)
    fixed_hold_active = fixed_hold > 0
    target_only = _has_pnl_target(risk)
    eq, pnls = [], []
    for idx, (i, row) in enumerate(df.iterrows()):
        c, h, l, s = float(row.Close), float(row.High), float(row.Low), int(sig.loc[i])
        if q > 0:
            hold_bars += 1
            ex = None
            if stop and l <= stop:
                ex = stop * (1 - risk["slippage"])
            elif fixed_hold_active and hold_bars >= fixed_hold:
                ex = c * (1 - risk["slippage"])
            elif take and h >= take and not target_only and not fixed_hold_active:
                ex = take * (1 - risk["slippage"])
            elif hold_bars >= min_hold and _pnl_target_hit(entry, c, risk) and not fixed_hold_active:
                ex = c * (1 - risk["slippage"])
            elif hold_bars >= min_hold and s < 0 and not target_only and not fixed_hold_active:
                ex = c * (1 - risk["slippage"])
            if ex is not None:
                gross = q * ex
                net = gross - gross * risk["fee_rate"]
                cash += net
                pnls.append(net - cost)
                q, cost, entry, stop, take = 0.0, 0.0, 0.0, None, None
                hold_bars = 0
                cooldown_until = idx + cooldown_bars
        if q <= 0 and s > 0 and idx >= cooldown_until and idx >= entry_delay:
            qty = pos_size(cash, c, risk)
            if qty > 0:
                e = c * (1 + risk["slippage"])
                gross = qty * e
                total = gross + gross * risk["fee_rate"]
                if total <= cash:
                    cash -= total
                    q, cost, entry = qty, total, e
                    hold_bars = 0
                    stop = e * (1 - risk["stop_loss_pct"]) if risk["stop_loss_pct"] > 0 else None
                    take = e * (1 + risk["take_profit_pct"]) if risk["take_profit_pct"] > 0 else None
        eq.append(cash + q * c)
    if q > 0:
        c = float(df.Close.iloc[-1]) * (1 - risk["slippage"])
        gross = q * c
        net = gross - gross * risk["fee_rate"]
        cash += net
        pnls.append(net - cost)
        eq[-1] = cash
    ec = pd.Series(eq, index=df.index)
    r = ec.pct_change().fillna(0)
    sh = 0.0 if r.std() == 0 else (r.mean() / r.std()) * np.sqrt(ann(interval))
    dd = ((ec / ec.cummax()) - 1).min() * 100 if len(ec) else 0
    wins = sum(1 for p in pnls if p > 0)
    gp, gl = sum(p for p in pnls if p > 0), abs(sum(p for p in pnls if p < 0))
    pf = gp / gl if gl > 0 else (float("inf") if gp > 0 else 0)
    return {
        "return": (ec.iloc[-1] / cap - 1) * 100 if len(ec) else 0,
        "win": (wins / len(pnls) * 100) if pnls else 0,
        "dd": float(dd),
        "sharpe": float(sh),
        "trades": len(pnls),
        "pf": float(pf),
    }


def score(train, test):
    tr, te = train["return"] / 100, test["return"] / 100
    over = max(0.0, tr - te)
    return 0.4 * te + 0.25 * (max(min(test["sharpe"], 5), -5) / 5) + 0.2 * (test["win"] / 100) + 0.15 * tr - 0.3 * abs(test["dd"]) / 100 - 0.2 * over


def _is_win_rate_ok(row, win_min=None, win_max=None):
    win = float(row["test"]["win"])
    if win_min is not None and win < float(win_min):
        return False
    if win_max is not None and win > float(win_max):
        return False
    return True


def _sort_rows(rows, selection_mode):
    mode = str(selection_mode or "score").strip().lower()
    if mode == "winrate":
        rows.sort(
            key=lambda x: (
                float(x["test"]["win"]),
                float(x["test"]["return"]),
                float(x["score"]),
                float(x["test"]["trades"]),
            ),
            reverse=True,
        )
    else:
        rows.sort(key=lambda x: float(x["score"]), reverse=True)


def _success_rows(rows, success_win_min=None, success_return_min=None):
    w = float(success_win_min if success_win_min is not None else 0.0)
    r = float(success_return_min if success_return_min is not None else 0.0)
    out = []
    for x in rows:
        test = x.get("test", {})
        win = float(test.get("win", 0.0) or 0.0)
        ret = float(test.get("return", 0.0) or 0.0)
        trades = int(test.get("trades", 0) or 0)
        if trades <= 0:
            continue
        if win >= w and ret >= r:
            out.append(x)
    return out


def optimize(
    df,
    risk,
    interval,
    min_trades=5,
    top_n=3,
    required_win_min=None,
    required_win_max=None,
    strategy_filter=None,
    strats=None,
    selection_mode="score",
    success_win_min=0.0,
    success_return_min=0.0,
):
    split = max(60, min(int(len(df) * 0.7), len(df) - 30))
    tr, te = df.iloc[:split], df.iloc[split:]
    rows = []
    if strats is None:
        strats = build_strategy_catalog("extended")
    if strategy_filter:
        strat_items = [(name, strats[name]) for name in strategy_filter if name in strats]
    else:
        strat_items = list(strats.items())
    if not strat_items:
        strat_items = list(strats.items())
    if not strat_items:
        raise ValueError("No strategies available for optimization.")

    for name, (fn, params_list) in strat_items:
        for p in params_list:
            tr_m = backtest(tr, fn(tr, p), risk, 1000, interval)
            if tr_m["trades"] < min_trades:
                continue
            te_m = backtest(te, fn(te, p), risk, 1000, interval)
            rows.append({"name": name, "params": p, "train": tr_m, "test": te_m, "score": score(tr_m, te_m)})
    if not rows:
        for name, (fn, params_list) in strat_items:
            for p in params_list:
                tr_m = backtest(tr, fn(tr, p), risk, 1000, interval)
                te_m = backtest(te, fn(te, p), risk, 1000, interval)
                rows.append({"name": name, "params": p, "train": tr_m, "test": te_m, "score": score(tr_m, te_m)})
    if not rows:
        raise ValueError("Optimization produced no candidates.")
    _sort_rows(rows, selection_mode)
    qualified = [x for x in rows if _is_win_rate_ok(x, required_win_min, required_win_max)]
    successful = _success_rows(rows, success_win_min, success_return_min)
    if qualified:
        return (
            qualified[0],
            qualified[: max(1, top_n)],
            True,
            rows[: max(1, top_n)],
            successful[: max(1, top_n)],
        )
    return (
        rows[0],
        rows[: max(1, top_n)],
        False,
        rows[: max(1, top_n)],
        successful[: max(1, top_n)],
    )


def _candidate_sort_key(cand, selection_mode):
    mode = str(selection_mode or "score").strip().lower()
    test = cand.get("test", {}) if isinstance(cand, dict) else {}
    if mode == "winrate":
        return (
            float(test.get("win", 0.0) or 0.0),
            float(test.get("return", 0.0) or 0.0),
            float(cand.get("score", 0.0) or 0.0),
            float(test.get("trades", 0.0) or 0.0),
        )
    return (
        float(cand.get("score", 0.0) or 0.0),
        float(test.get("win", 0.0) or 0.0),
        float(test.get("return", 0.0) or 0.0),
    )


def choose_best_candidate(a, b, selection_mode):
    if a is None:
        return b
    if b is None:
        return a
    return a if _candidate_sort_key(a, selection_mode) >= _candidate_sort_key(b, selection_mode) else b


def _normalize_test_metrics(test):
    t = test if isinstance(test, dict) else {}
    return {
        "return": float(t.get("return", 0.0) or 0.0),
        "win": float(t.get("win", 0.0) or 0.0),
        "dd": float(t.get("dd", 0.0) or 0.0),
        "sharpe": float(t.get("sharpe", 0.0) or 0.0),
        "trades": int(t.get("trades", 0) or 0),
        "pf": float(t.get("pf", 0.0) or 0.0),
    }


def _pack_candidate(cand):
    if not isinstance(cand, dict):
        return {}
    return {
        "name": str(cand.get("name", "")),
        "strategy": str(cand.get("name", "")),
        "params": dict(cand.get("params", {}) or {}),
        "score": float(cand.get("score", 0.0) or 0.0),
        "test": _normalize_test_metrics(cand.get("test", {})),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }


def _normalize_candidate(raw, strats):
    if not isinstance(raw, dict):
        return None
    name = str(raw.get("name") or raw.get("strategy") or "").upper().strip()
    params = raw.get("params", {})
    if name not in strats or not isinstance(params, dict):
        return None
    test = _normalize_test_metrics(raw.get("test", {}))
    return {
        "name": name,
        "params": params,
        "score": float(raw.get("score", 0.0) or 0.0),
        "train": test,
        "test": test,
    }


def _candidate_id(cand):
    if not isinstance(cand, dict):
        return ""
    name = str(cand.get("name", "")).upper()
    params = cand.get("params", {})
    try:
        pkey = json.dumps(params, sort_keys=True)
    except Exception:
        pkey = str(params)
    return f"{name}|{pkey}"


def _merge_top(primary, secondary, top_n):
    out = []
    seen = set()
    for src in (primary or []), (secondary or []):
        for cand in src:
            cid = _candidate_id(cand)
            if cid in seen:
                continue
            out.append(cand)
            seen.add(cid)
            if len(out) >= max(1, int(top_n)):
                return out
    return out


def load_learned_model(path):
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}
    symbols = raw.get("symbols", {})
    if isinstance(symbols, dict):
        return symbols
    return {}


def save_learned_model(path, payload):
    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def candidate_from_learned(learned_symbols, symbol, strats, cfg):
    if not isinstance(learned_symbols, dict):
        return None
    raw = learned_symbols.get(symbol)
    if raw is None and isinstance(symbol, str):
        raw = learned_symbols.get(symbol.upper())
    cand = _normalize_candidate(raw, strats)
    if cand is None:
        return None
    if not cfg.get("learned_ignore_win_range", False):
        row = {"test": cand["test"]}
        if not _is_win_rate_ok(row, cfg.get("required_win_min"), cfg.get("required_win_max")):
            return None
    return cand


def select_strategy_for_symbol(df, symbol, cfg, risk, strats, learned_symbols):
    best, top, matched, global_top, success_top = optimize(
        df,
        risk,
        cfg["interval"],
        cfg["min_trades"],
        cfg["top_n"],
        cfg.get("required_win_min"),
        cfg.get("required_win_max"),
        cfg.get("strategy_filter"),
        strats,
        cfg.get("selection_mode", "score"),
        cfg.get("success_win_min", 0.0),
        cfg.get("success_return_min", 0.0),
    )
    source = "optimized"
    learned = None
    if cfg.get("use_learned_model", True):
        learned = candidate_from_learned(learned_symbols, symbol, strats, cfg)
    if learned is not None:
        if cfg.get("prefer_learned_model", True):
            source = "learned"
            best = learned
            matched = _is_win_rate_ok({"test": best["test"]}, cfg.get("required_win_min"), cfg.get("required_win_max"))
            top = _merge_top([learned], top, cfg.get("top_n", 3))
            if _success_rows([learned], cfg.get("success_win_min", 0.0), cfg.get("success_return_min", 0.0)):
                success_top = _merge_top([learned], success_top, cfg.get("top_n", 3))
        else:
            chosen = choose_best_candidate(best, learned, cfg.get("selection_mode", "score"))
            if chosen is learned:
                source = "learned"
                best = learned
                matched = _is_win_rate_ok({"test": best["test"]}, cfg.get("required_win_min"), cfg.get("required_win_max"))
                top = _merge_top([learned], top, cfg.get("top_n", 3))
                if _success_rows([learned], cfg.get("success_win_min", 0.0), cfg.get("success_return_min", 0.0)):
                    success_top = _merge_top([learned], success_top, cfg.get("top_n", 3))
    return best, top, matched, global_top, success_top, source


def collect_exchange_symbols(exchange, quote_currency="USDT", max_symbols=0):
    quote = str(quote_currency or "").upper().strip()
    markets = getattr(exchange, "markets", {}) or {}
    out = []
    for symbol, market in markets.items():
        try:
            if not isinstance(market, dict):
                continue
            if market.get("active") is False:
                continue
            if market.get("spot") is False:
                continue
            if ":" in str(symbol):
                continue
            if "/" not in str(symbol):
                continue
            q = str(market.get("quote") or "").upper().strip()
            if quote and q != quote:
                continue
            base = str(market.get("base") or "").upper().strip()
            if base.endswith("UP") or base.endswith("DOWN") or base.endswith("BULL") or base.endswith("BEAR"):
                continue
            out.append(str(symbol))
        except Exception:
            continue
    out = sorted(set(out))
    m = int(max_symbols or 0)
    if m > 0:
        out = out[:m]
    return out


class Paper:
    def __init__(self, cash, risk):
        self.cash = float(cash)
        self.risk = risk
        self.pos = {}
        self.last = {}
        self.log = []
        self.bar_index = {}
        self.cooldown_until = {}

    def equity(self):
        return self.cash + sum(p["qty"] * self.last.get(s, p["entry"]) for s, p in self.pos.items())

    def on_bar(self, symbol, ts, high, low, close, signal, strategy):
        bar_n = self.bar_index.get(symbol, -1) + 1
        self.bar_index[symbol] = bar_n
        self.last[symbol] = close
        p = self.pos.get(symbol)
        min_hold = int(self.risk.get("min_hold_bars", 0) or 0)
        cooldown_bars = int(self.risk.get("cooldown_bars", 0) or 0)
        entry_delay = int(self.risk.get("entry_delay_bars", 0) or 0)
        fixed_hold = int(self.risk.get("fixed_hold_bars", 0) or 0)
        fixed_hold_active = fixed_hold > 0
        target_only = _has_pnl_target(self.risk)
        cooldown_until = int(self.cooldown_until.get(symbol, -1))
        if p:
            ex, reason = None, None
            held = max(0, bar_n - int(p.get("entry_bar", bar_n)))
            if p["stop"] and low <= p["stop"]:
                ex, reason = p["stop"] * (1 - self.risk["slippage"]), "stop"
            elif fixed_hold_active and held >= fixed_hold:
                ex, reason = close * (1 - self.risk["slippage"]), "time_exit"
            elif p["take"] and high >= p["take"] and not target_only and not fixed_hold_active:
                ex, reason = p["take"] * (1 - self.risk["slippage"]), "take"
            elif held >= min_hold and _pnl_target_hit(float(p["entry"]), close, self.risk) and not fixed_hold_active:
                ex, reason = close * (1 - self.risk["slippage"]), "pnl_target"
            elif held >= min_hold and signal < 0 and not target_only and not fixed_hold_active:
                ex, reason = close * (1 - self.risk["slippage"]), "signal"
            if ex is not None:
                gross = p["qty"] * ex
                fee = gross * self.risk["fee_rate"]
                net = gross - fee
                self.cash += net
                pnl = net - p["cost"]
                pnl_pct = _pnl_pct(float(p["entry"]), ex)
                self.log.append(
                    {
                        "ts": str(ts),
                        "sym": symbol,
                        "side": "SELL",
                        "price": ex,
                        "qty": p["qty"],
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "reason": reason,
                    }
                )
                del self.pos[symbol]
                LOG.info(
                    "SELL %s qty=%.4f price=%.4f reason=%s pnl=%.2f pnl_pct=%.2f%%",
                    symbol,
                    p["qty"],
                    ex,
                    reason,
                    pnl,
                    pnl_pct,
                )
                self.cooldown_until[symbol] = bar_n + cooldown_bars
                cooldown_until = self.cooldown_until[symbol]
                p = None
        if (
            p is None
            and signal > 0
            and bar_n >= entry_delay
            and bar_n >= cooldown_until
            and len(self.pos) < max(1, int(self.risk["max_open_positions"]))
        ):
            qty = pos_size(self.cash, close, self.risk)
            if qty > 0:
                e = close * (1 + self.risk["slippage"])
                gross = qty * e
                fee = gross * self.risk["fee_rate"]
                total = gross + fee
                if total <= self.cash:
                    self.cash -= total
                    self.pos[symbol] = {
                        "qty": qty,
                        "entry": e,
                        "cost": total,
                        "stop": e * (1 - self.risk["stop_loss_pct"]) if self.risk["stop_loss_pct"] > 0 else None,
                        "take": e * (1 + self.risk["take_profit_pct"]) if self.risk["take_profit_pct"] > 0 else None,
                        "entry_bar": bar_n,
                        "strategy": strategy,
                    }
                    self.log.append({"ts": str(ts), "sym": symbol, "side": "BUY", "price": e, "qty": qty})
                    LOG.info("BUY %s qty=%.4f price=%.4f strategy=%s", symbol, qty, e, strategy)


class CcxtLiveBroker:
    def __init__(self, exchange, risk, quote_currency="USDT"):
        self.exchange = exchange
        self.risk = risk
        self.quote_currency = quote_currency.upper()
        self.positions = {}
        self.last = {}
        self.log = []
        self.bar_index = {}
        self.cooldown_until = {}

    def _balance(self):
        return self.exchange.fetch_balance()

    def _quote_free(self):
        bal = self._balance()
        free = bal.get("free", {}) or {}
        return float(free.get(self.quote_currency, 0.0) or 0.0)

    @property
    def cash(self):
        try:
            return self._quote_free()
        except Exception:
            return 0.0

    def _base_free(self, symbol):
        base = symbol.split("/")[0]
        bal = self._balance()
        free = bal.get("free", {}) or {}
        return float(free.get(base, 0.0) or 0.0)

    def _normalize_amount(self, symbol, qty):
        try:
            return float(self.exchange.amount_to_precision(symbol, qty))
        except Exception:
            return float(qty)

    def _close_order(self, symbol, reason, price):
        qty = self._base_free(symbol)
        qty = self._normalize_amount(symbol, qty)
        if qty <= 0:
            return
        order = self.exchange.create_market_sell_order(symbol, qty)
        fill = float(order.get("average") or price)
        pos = self.positions.get(symbol, {})
        entry_cost = float(pos.get("cost", 0.0))
        entry_price = float(pos.get("entry", 0.0))
        gross = qty * fill
        fee = gross * float(self.risk["fee_rate"])
        pnl = gross - fee - entry_cost
        pnl_pct = _pnl_pct(entry_price, fill)
        self.log.append(
            {
                "ts": str(pd.Timestamp.utcnow()),
                "sym": symbol,
                "side": "SELL",
                "price": fill,
                "qty": qty,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "reason": reason,
            }
        )
        LOG.info(
            "SELL %s qty=%.6f price=%.4f reason=%s pnl=%.2f pnl_pct=%.2f%%",
            symbol,
            qty,
            fill,
            reason,
            pnl,
            pnl_pct,
        )
        if symbol in self.positions:
            del self.positions[symbol]

    def on_bar(self, symbol, ts, high, low, close, signal, strategy):
        bar_n = self.bar_index.get(symbol, -1) + 1
        self.bar_index[symbol] = bar_n
        self.last[symbol] = close
        pos = self.positions.get(symbol)
        min_hold = int(self.risk.get("min_hold_bars", 0) or 0)
        cooldown_bars = int(self.risk.get("cooldown_bars", 0) or 0)
        entry_delay = int(self.risk.get("entry_delay_bars", 0) or 0)
        fixed_hold = int(self.risk.get("fixed_hold_bars", 0) or 0)
        fixed_hold_active = fixed_hold > 0
        target_only = _has_pnl_target(self.risk)
        cooldown_until = int(self.cooldown_until.get(symbol, -1))
        if pos:
            held = max(0, bar_n - int(pos.get("entry_bar", bar_n)))
            if pos.get("stop") and low <= pos["stop"]:
                self._close_order(symbol, "stop", close)
                pos = None
            elif pos and fixed_hold_active and held >= fixed_hold:
                self._close_order(symbol, "time_exit", close)
                pos = None
            elif pos and pos.get("take") and high >= pos["take"] and not target_only and not fixed_hold_active:
                self._close_order(symbol, "take", close)
                pos = None
            elif pos and held >= min_hold and _pnl_target_hit(float(pos["entry"]), close, self.risk) and not fixed_hold_active:
                self._close_order(symbol, "pnl_target", close)
                pos = None
            elif pos and held >= min_hold and signal < 0 and not target_only and not fixed_hold_active:
                self._close_order(symbol, "signal", close)
                pos = None
            if pos is None:
                self.cooldown_until[symbol] = bar_n + cooldown_bars
                cooldown_until = self.cooldown_until[symbol]

        if (
            pos is None
            and signal > 0
            and bar_n >= entry_delay
            and bar_n >= cooldown_until
            and len(self.positions) < max(1, int(self.risk["max_open_positions"]))
        ):
            free_quote = self._quote_free()
            qty = pos_size(free_quote, close, self.risk)
            qty = self._normalize_amount(symbol, qty)
            if qty <= 0:
                return
            order = self.exchange.create_market_buy_order(symbol, qty)
            fill = float(order.get("average") or close)
            gross = qty * fill
            fee = gross * float(self.risk["fee_rate"])
            total = gross + fee
            self.positions[symbol] = {
                "qty": qty,
                "entry": fill,
                "cost": total,
                "stop": fill * (1 - self.risk["stop_loss_pct"]) if self.risk["stop_loss_pct"] > 0 else None,
                "take": fill * (1 + self.risk["take_profit_pct"]) if self.risk["take_profit_pct"] > 0 else None,
                "entry_bar": bar_n,
                "strategy": strategy,
            }
            self.log.append({"ts": str(ts), "sym": symbol, "side": "BUY", "price": fill, "qty": qty})
            LOG.info("BUY %s qty=%.6f price=%.4f strategy=%s", symbol, qty, fill, strategy)

    def equity(self):
        bal = self._balance()
        total = bal.get("total", {}) or {}
        eq = 0.0
        for asset, amount in total.items():
            amount = float(amount or 0.0)
            if amount <= 0:
                continue
            if asset.upper() == self.quote_currency:
                eq += amount
                continue
            sym = f"{asset}/{self.quote_currency}"
            if sym in getattr(self.exchange, "markets", {}):
                px = self.last.get(sym)
                if px is None:
                    try:
                        px = float((self.exchange.fetch_ticker(sym) or {}).get("last") or 0.0)
                    except Exception:
                        px = 0.0
                eq += amount * float(px or 0.0)
        return eq


def run_train(cfg, risk):
    LOG.warning(
        "TRAIN mode: scanning historical data to build a learned strategy map for crypto symbols."
    )
    try:
        exchange = _init_exchange(cfg, require_auth=False)
    except Exception as exc:
        LOG.error("Cannot initialize exchange for training: %s", exc)
        return
    if exchange is None:
        LOG.error("Exchange is required for training mode.")
        return

    strats = build_strategy_catalog(cfg.get("strategy_pack", "extended"))
    model_path = cfg.get("learned_model_path", "learned_crypto_model.json")
    learned_symbols = load_learned_model(model_path)
    model = {
        "meta": {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "exchange": cfg.get("exchange", ""),
            "interval": cfg.get("interval", ""),
            "strategy_pack": cfg.get("strategy_pack", ""),
            "selection_mode": cfg.get("selection_mode", ""),
            "quote_currency": cfg.get("quote_currency", ""),
            "train_all_symbols": bool(cfg.get("train_all_symbols", False)),
            "symbols_total": 0,
            "symbols_trained": 0,
            "symbols_skipped": 0,
            "symbols_failed": 0,
        },
        "symbols": dict(learned_symbols),
    }

    if cfg.get("train_all_symbols", False):
        symbols = collect_exchange_symbols(
            exchange,
            quote_currency=cfg.get("quote_currency", "USDT"),
            max_symbols=cfg.get("train_max_symbols", 0),
        )
    else:
        symbols = [s for s in cfg.get("symbols", []) if "/" in str(s)]
    if not symbols:
        LOG.error("No symbols selected for training.")
        return

    save_every = max(1, int(cfg.get("train_save_every", 25) or 25))
    min_bars = max(80, int(cfg.get("train_min_bars", 160) or 160))
    train_cfg = dict(cfg)
    train_cfg["use_learned_model"] = False
    train_cfg["prefer_learned_model"] = False
    total = len(symbols)
    trained = skipped = failed = 0
    LOG.info(
        "Training started: symbols=%d pack=%s selection=%s model=%s",
        total,
        cfg.get("strategy_pack", "extended"),
        cfg.get("selection_mode", "score"),
        model_path,
    )
    for idx, sym in enumerate(symbols, 1):
        try:
            df = load_bars(sym, cfg["interval"], cfg["lookback_bars"], exchange=exchange)
            if len(df) < min_bars:
                skipped += 1
                LOG.warning("[%d/%d] %s skip: not enough bars (%d)", idx, total, sym, len(df))
                continue

            best, top, matched, _, success_top, source = select_strategy_for_symbol(
                df,
                sym,
                train_cfg,
                risk,
                strats,
                model["symbols"],
            )
            if not matched and cfg.get("success_fallback_enabled", True) and success_top:
                best = success_top[0]
                source = "success_fallback"

            model["symbols"][sym] = _pack_candidate(best)
            model["symbols"][sym]["source"] = source
            model["symbols"][sym]["matched_target"] = bool(matched)
            trained += 1
            LOG.info(
                "[%d/%d] TRAINED %s -> %s win=%.2f%% ret=%.2f%% source=%s",
                idx,
                total,
                sym,
                best["name"],
                best["test"]["win"],
                best["test"]["return"],
                source,
            )
            for i, x in enumerate(top[: max(1, int(cfg.get("top_n", 3)))], 1):
                LOG.info(
                    "[%s] TOP%d %s params=%s test_win=%.2f%% test_ret=%.2f%%",
                    sym,
                    i,
                    x["name"],
                    json.dumps(x["params"]),
                    x["test"]["win"],
                    x["test"]["return"],
                )
        except Exception as exc:
            failed += 1
            LOG.warning("[%d/%d] %s train error: %s", idx, total, sym, exc)
        if idx % save_every == 0:
            model["meta"]["updated_at"] = datetime.now(timezone.utc).isoformat()
            model["meta"]["symbols_total"] = total
            model["meta"]["symbols_trained"] = trained
            model["meta"]["symbols_skipped"] = skipped
            model["meta"]["symbols_failed"] = failed
            save_learned_model(model_path, model)
            LOG.info("Intermediate model saved: %s", model_path)

    model["meta"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    model["meta"]["symbols_total"] = total
    model["meta"]["symbols_trained"] = trained
    model["meta"]["symbols_skipped"] = skipped
    model["meta"]["symbols_failed"] = failed
    save_learned_model(model_path, model)
    LOG.warning(
        "Training completed: total=%d trained=%d skipped=%d failed=%d | model=%s",
        total,
        trained,
        skipped,
        failed,
        model_path,
    )


def run_backtest(cfg, risk):
    LOG.warning("Backtest is historical simulation only, not a future guarantee.")
    strats = build_strategy_catalog(cfg.get("strategy_pack", "extended"))
    learned_symbols = load_learned_model(cfg.get("learned_model_path")) if cfg.get("use_learned_model", True) else {}
    LOG.info(
        "Strategy pool: pack=%s count=%d selection=%s",
        cfg.get("strategy_pack", "extended"),
        len(strats),
        cfg.get("selection_mode", "score"),
    )
    if learned_symbols:
        LOG.info("Learned model loaded: %s (%d symbols)", cfg.get("learned_model_path"), len(learned_symbols))
    exchange = None
    need_exchange = bool(cfg.get("exchange")) and any("/" in s for s in cfg["symbols"])
    if need_exchange:
        try:
            exchange = _init_exchange(cfg, require_auth=False)
        except Exception as exc:
            LOG.warning("Exchange init failed in backtest, fallback to yfinance: %s", exc)
            exchange = None
    for s in cfg["symbols"]:
        use_ex = exchange if "/" in s else None
        df = load_bars(s, cfg["interval"], cfg["lookback_bars"], exchange=use_ex)
        if len(df) < 120:
            LOG.warning("Skip %s, not enough data", s)
            continue
        best, top, matched, global_top, success_top, source = select_strategy_for_symbol(
            df,
            s,
            cfg,
            risk,
            strats,
            learned_symbols,
        )
        if source == "learned":
            LOG.info("[%s] Using learned strategy: %s params=%s", s, best["name"], json.dumps(best["params"]))
        if cfg.get("success_scan_enabled", True) and success_top:
            for i, x in enumerate(success_top, 1):
                LOG.info(
                    "[%s] SUCCESS%d %s params=%s test_win=%.2f%% test_ret=%.2f%%",
                    s,
                    i,
                    x["name"],
                    json.dumps(x["params"]),
                    x["test"]["win"],
                    x["test"]["return"],
                )
        if not matched:
            if cfg.get("success_fallback_enabled", True) and success_top:
                best = success_top[0]
                top = success_top[: max(1, cfg.get("top_n", 3))]
                LOG.warning(
                    "[%s] No strategy in target range %.2f-%.2f%%. Using SUCCESS fallback: %s",
                    s,
                    cfg.get("required_win_min", 0.0),
                    cfg.get("required_win_max", 100.0),
                    best["name"],
                )
            else:
                LOG.warning(
                    "[%s] No strategy in target win-rate range %.2f-%.2f%%. Showing best available candidate.",
                    s,
                    cfg.get("required_win_min", 0.0),
                    cfg.get("required_win_max", 100.0),
                )
                top = global_top
        fn = strats[best["name"]][0]
        full = backtest(df, fn(df, best["params"]), risk, cfg["initial_capital"], cfg["interval"])
        LOG.info("[%s] BEST=%s params=%s score=%.4f | return=%.2f%% win=%.2f%% dd=%.2f%% sharpe=%.2f trades=%d", s, best["name"], json.dumps(best["params"]), best["score"], full["return"], full["win"], full["dd"], full["sharpe"], full["trades"])
        for i, x in enumerate(top, 1):
            LOG.info("[%s] TOP%d %s params=%s score=%.4f test_ret=%.2f%% test_win=%.2f%%", s, i, x["name"], json.dumps(x["params"]), x["score"], x["test"]["return"], x["test"]["win"])


def run_live(cfg, risk):
    strats = build_strategy_catalog(cfg.get("strategy_pack", "extended"))
    learned_symbols = load_learned_model(cfg.get("learned_model_path")) if cfg.get("use_learned_model", True) else {}
    LOG.info(
        "Strategy pool: pack=%s count=%d selection=%s",
        cfg.get("strategy_pack", "extended"),
        len(strats),
        cfg.get("selection_mode", "score"),
    )
    if learned_symbols:
        LOG.info("Learned model loaded: %s (%d symbols)", cfg.get("learned_model_path"), len(learned_symbols))
    if cfg.get("broker_mode") == "live":
        LOG.warning("LIVE broker mode: real orders can be sent. Profit is not guaranteed.")
        try:
            exchange = _init_exchange(cfg, require_auth=True)
        except Exception as exc:
            LOG.error("Cannot start live broker mode: %s", exc)
            return
        quote_currency = str(cfg.get("quote_currency", "USDT")).upper()
        broker = CcxtLiveBroker(exchange, risk, quote_currency=quote_currency)
    else:
        LOG.warning("Live mode in PAPER broker mode. Profit is not guaranteed.")
        exchange = None
        if any("/" in s for s in cfg["symbols"]):
            try:
                exchange = _init_exchange(cfg, require_auth=False)
            except Exception as exc:
                LOG.warning("Exchange init failed for market data in paper mode: %s", exc)
                exchange = None
        broker = Paper(cfg["initial_capital"], risk)
    best, loops = {}, 0
    while True:
        loops += 1
        for s in cfg["symbols"]:
            try:
                use_ex = exchange if (exchange is not None and "/" in s) else None
                df = load_bars(s, cfg["interval"], cfg["lookback_bars"], exchange=use_ex)
                if len(df) < 120:
                    continue
                if s not in best or best[s] is None or loops % max(1, cfg["reoptimize_every"]) == 0:
                    candidate, top_live, matched, _, success_live, source = select_strategy_for_symbol(
                        df,
                        s,
                        cfg,
                        risk,
                        strats,
                        learned_symbols,
                    )
                    if cfg.get("success_scan_enabled", True) and success_live:
                        for i, x in enumerate(success_live, 1):
                            LOG.info(
                                "[%s] SUCCESS%d %s params=%s test_win=%.2f%% test_ret=%.2f%%",
                                s,
                                i,
                                x["name"],
                                json.dumps(x["params"]),
                                x["test"]["win"],
                                x["test"]["return"],
                            )
                    if source == "learned":
                        LOG.info("[%s] Using learned strategy: %s params=%s", s, candidate["name"], json.dumps(candidate["params"]))
                    if matched:
                        best[s] = candidate
                        LOG.info(
                            "[%s] strategy=%s params=%s score=%.4f test_win=%.2f%%",
                            s,
                            best[s]["name"],
                            json.dumps(best[s]["params"]),
                            best[s]["score"],
                            best[s]["test"]["win"],
                        )
                        for i, x in enumerate(top_live, 1):
                            LOG.info(
                                "[%s] TOP%d %s params=%s test_win=%.2f%% test_ret=%.2f%%",
                                s,
                                i,
                                x["name"],
                                json.dumps(x["params"]),
                                x["test"]["win"],
                                x["test"]["return"],
                            )
                    else:
                        if cfg.get("success_fallback_enabled", True) and success_live:
                            best[s] = success_live[0]
                            LOG.warning(
                                "[%s] No strategy in %.2f-%.2f%%. SUCCESS fallback=%s win=%.2f%% ret=%.2f%%",
                                s,
                                cfg.get("required_win_min", 0.0),
                                cfg.get("required_win_max", 100.0),
                                best[s]["name"],
                                best[s]["test"]["win"],
                                best[s]["test"]["return"],
                            )
                        else:
                            best[s] = None
                            LOG.warning(
                                "[%s] No strategy matched win-rate %.2f-%.2f%%. Trading paused for this symbol.",
                                s,
                                cfg.get("required_win_min", 0.0),
                                cfg.get("required_win_max", 100.0),
                            )
                if best.get(s) is None:
                    continue
                fn = strats[best[s]["name"]][0]
                sig = fn(df, best[s]["params"])
                b = df.iloc[-1]
                broker.on_bar(s, df.index[-1], float(b.High), float(b.Low), float(b.Close), int(sig.iloc[-1]), best[s]["name"])
                LOG.info("[%s] close=%.4f signal=%d strategy=%s", s, float(b.Close), int(sig.iloc[-1]), best[s]["name"])
            except Exception as exc:
                LOG.warning("[%s] loop error: %s", s, exc)
        eq = broker.equity()
        pos_obj = getattr(broker, "pos", None)
        if pos_obj is None:
            pos_obj = getattr(broker, "positions", {})
        cash = float(getattr(broker, "cash", 0.0) or 0.0)
        LOG.info(
            "loop=%d equity=%.2f target=%.2f cash=%.2f positions=%d",
            loops,
            eq,
            cfg["target_capital"],
            cash,
            len(pos_obj),
        )
        if cfg["stop_on_target"] and eq >= cfg["target_capital"]:
            LOG.warning("Target reached: %.2f >= %.2f. Stop.", eq, cfg["target_capital"])
            break
        if cfg["max_loops"] > 0 and loops >= cfg["max_loops"]:
            LOG.info("Max loops reached: %d", cfg["max_loops"])
            break
        time.sleep(max(1, cfg["poll_seconds"]))


def run_demo(cfg, risk):
    LOG.warning(
        "Demo mode runs accelerated paper simulation on historical bars. This is for strategy testing only."
    )
    strats = build_strategy_catalog(cfg.get("strategy_pack", "extended"))
    learned_symbols = load_learned_model(cfg.get("learned_model_path")) if cfg.get("use_learned_model", True) else {}
    LOG.info(
        "Strategy pool: pack=%s count=%d selection=%s",
        cfg.get("strategy_pack", "extended"),
        len(strats),
        cfg.get("selection_mode", "score"),
    )
    if learned_symbols:
        LOG.info("Learned model loaded: %s (%d symbols)", cfg.get("learned_model_path"), len(learned_symbols))
    broker = Paper(cfg["initial_capital"], risk)
    prepared = {}
    exchange = None
    need_exchange = bool(cfg.get("exchange")) and any("/" in s for s in cfg["symbols"])
    if need_exchange:
        try:
            exchange = _init_exchange(cfg, require_auth=False)
        except Exception as exc:
            LOG.warning("Exchange init failed in demo, fallback to yfinance: %s", exc)
            exchange = None

    for s in cfg["symbols"]:
        use_ex = exchange if "/" in s else None
        df = load_bars(s, cfg["interval"], cfg["lookback_bars"], exchange=use_ex)
        if len(df) < 140:
            LOG.warning("[%s] Skip: not enough bars for demo.", s)
            continue

        best, top, matched, _, success_top, source = select_strategy_for_symbol(
            df,
            s,
            cfg,
            risk,
            strats,
            learned_symbols,
        )
        if source == "learned":
            LOG.info("[%s] Using learned strategy: %s params=%s", s, best["name"], json.dumps(best["params"]))
        if cfg.get("success_scan_enabled", True) and success_top:
            for i, x in enumerate(success_top, 1):
                LOG.info(
                    "[%s] SUCCESS%d %s params=%s test_win=%.2f%% test_ret=%.2f%%",
                    s,
                    i,
                    x["name"],
                    json.dumps(x["params"]),
                    x["test"]["win"],
                    x["test"]["return"],
                )
        if not matched:
            if cfg.get("success_fallback_enabled", True) and success_top:
                best = success_top[0]
                top = success_top[: max(1, cfg.get("top_n", 3))]
                LOG.warning(
                    "[%s] No strategy in %.2f-%.2f%%. Using SUCCESS fallback=%s",
                    s,
                    cfg.get("required_win_min", 0.0),
                    cfg.get("required_win_max", 100.0),
                    best["name"],
                )
            else:
                LOG.warning(
                    "[%s] No strategy matched win-rate %.2f-%.2f%%. Symbol excluded from demo.",
                    s,
                    cfg.get("required_win_min", 0.0),
                    cfg.get("required_win_max", 100.0),
                )
                continue

        split = max(60, min(int(len(df) * cfg["demo_train_fraction"]), len(df) - 30))
        train, demo = df.iloc[:split], df.iloc[split:]
        fn = strats[best["name"]][0]
        tr = backtest(train, fn(train, best["params"]), risk, 1000, cfg["interval"])
        te = backtest(demo, fn(demo, best["params"]), risk, 1000, cfg["interval"])
        sig = fn(demo, best["params"])
        prepared[s] = {"bars": demo, "signals": sig, "best": best}

        LOG.info(
            "[%s] DEMO strategy=%s params=%s | train_win=%.2f%% test_win=%.2f%% score=%.4f",
            s,
            best["name"],
            json.dumps(best["params"]),
            tr["win"],
            te["win"],
            best["score"],
        )
        for i, x in enumerate(top, 1):
            LOG.info(
                "[%s] TOP%d %s params=%s test_win=%.2f%% test_ret=%.2f%%",
                s,
                i,
                x["name"],
                json.dumps(x["params"]),
                x["test"]["win"],
                x["test"]["return"],
            )

    if not prepared:
        LOG.error("Demo stopped: no symbols have a strategy in the requested win-rate range.")
        return

    max_steps = max(len(v["bars"]) for v in prepared.values())
    demo_sleep = max(0.0, float(cfg.get("demo_speed_ms", 80)) / 1000.0)

    for step in range(max_steps):
        loop = step + 1
        for s, payload in prepared.items():
            bars = payload["bars"]
            if step >= len(bars):
                continue
            row = bars.iloc[step]
            ts = bars.index[step]
            signal = int(payload["signals"].iloc[step])
            broker.on_bar(
                s,
                ts,
                float(row.High),
                float(row.Low),
                float(row.Close),
                signal,
                payload["best"]["name"],
            )
            LOG.info(
                "[%s] close=%.4f signal=%d strategy=%s",
                s,
                float(row.Close),
                signal,
                payload["best"]["name"],
            )

        eq = broker.equity()
        LOG.info(
            "loop=%d equity=%.2f target=%.2f cash=%.2f positions=%d",
            loop,
            eq,
            cfg["target_capital"],
            broker.cash,
            len(broker.pos),
        )
        if cfg["stop_on_target"] and eq >= cfg["target_capital"]:
            LOG.warning("Target reached in demo: %.2f >= %.2f. Stop.", eq, cfg["target_capital"])
            break
        if cfg["max_loops"] > 0 and loop >= cfg["max_loops"]:
            LOG.info("Max loops reached: %d", cfg["max_loops"])
            break
        if demo_sleep > 0:
            time.sleep(demo_sleep)

    LOG.info(
        "Demo finished | equity=%.2f cash=%.2f open_positions=%d",
        broker.equity(),
        broker.cash,
        len(broker.pos),
    )


def apply_simple_mode(cfg, risk):
    if not bool(cfg.get("simple_mode", False)):
        return
    cfg["strategy"] = "AUTO"
    cfg["strategy_pack"] = "max"
    cfg["selection_mode"] = "winrate"
    cfg["use_learned_model"] = True
    cfg["prefer_learned_model"] = True
    cfg["required_win_min"] = 0.0
    cfg["required_win_max"] = 100.0
    cfg["success_scan_enabled"] = True
    cfg["success_fallback_enabled"] = True
    cfg["success_win_min"] = float(cfg.get("success_win_min", 50.0) or 50.0)
    cfg["success_return_min"] = float(cfg.get("success_return_min", 0.0) or 0.0)
    cfg["top_n"] = max(5, int(cfg.get("top_n", 5)))
    cfg["min_trades"] = max(2, int(cfg.get("min_trades", 5)))
    if str(cfg.get("trade_frequency", "")).strip() == "":
        cfg["trade_frequency"] = "frequent"

    # In simple mode we focus on strategy win-rate and time-based exits.
    risk["pnl_close_min_pct"] = 0.0
    risk["pnl_close_max_pct"] = 0.0
    risk["take_profit_pct"] = 0.0
    LOG.info("Simple mode active: broad search, rank by win-rate, time-hold exits enabled.")


def apply_trade_frequency_profile(cfg, risk):
    mode = str(cfg.get("trade_frequency", "normal") or "normal").strip().lower()
    if mode not in {"calm", "normal", "frequent", "very_frequent"}:
        mode = "normal"
    cfg["trade_frequency"] = mode

    if mode == "calm":
        cfg["poll_seconds"] = max(20, int(cfg.get("poll_seconds", 30)))
        cfg["reoptimize_every"] = max(8, int(cfg.get("reoptimize_every", 10)))
        risk["min_hold_bars"] = max(3, int(risk.get("min_hold_bars", 3)))
        risk["cooldown_bars"] = max(2, int(risk.get("cooldown_bars", 2)))
        risk["entry_delay_bars"] = max(3, int(risk.get("entry_delay_bars", 5)))
    elif mode == "frequent":
        cfg["poll_seconds"] = max(2, min(int(cfg.get("poll_seconds", 30)), 8))
        cfg["reoptimize_every"] = max(1, min(int(cfg.get("reoptimize_every", 10)), 4))
        risk["min_hold_bars"] = max(1, min(int(risk.get("min_hold_bars", 3)), 2))
        risk["cooldown_bars"] = max(0, min(int(risk.get("cooldown_bars", 2)), 1))
        risk["entry_delay_bars"] = max(0, min(int(risk.get("entry_delay_bars", 5)), 1))
    elif mode == "very_frequent":
        cfg["poll_seconds"] = max(1, min(int(cfg.get("poll_seconds", 30)), 5))
        cfg["reoptimize_every"] = max(1, min(int(cfg.get("reoptimize_every", 10)), 2))
        risk["min_hold_bars"] = max(1, min(int(risk.get("min_hold_bars", 3)), 1))
        risk["cooldown_bars"] = 0
        risk["entry_delay_bars"] = 0

    LOG.info(
        "Trade frequency profile: %s | poll=%ss reoptimize_every=%d hold=%d cooldown=%d delay=%d",
        cfg["trade_frequency"],
        cfg["poll_seconds"],
        cfg["reoptimize_every"],
        int(risk.get("min_hold_bars", 0)),
        int(risk.get("cooldown_bars", 0)),
        int(risk.get("entry_delay_bars", 0)),
    )


def apply_fixed_hold_profile(cfg, risk):
    hold_minutes = int(cfg.get("hold_minutes", 0) or 0)
    if hold_minutes <= 0:
        risk["fixed_hold_bars"] = 0
        return
    tf_minutes = interval_minutes(cfg.get("interval", "5m"))
    bars = max(1, int(math.ceil(float(hold_minutes) / float(tf_minutes))))
    risk["fixed_hold_bars"] = bars
    LOG.info(
        "Fixed hold active: %d minutes -> %d bar(s) at interval %s",
        hold_minutes,
        bars,
        cfg.get("interval", "5m"),
    )


def read_cfg(path):
    cfg = {
        "mode": "demo",
        "symbols": ["AAPL", "MSFT", "NVDA"],
        "interval": "5m",
        "lookback_bars": 600,
        "poll_seconds": 30,
        "reoptimize_every": 10,
        "initial_capital": 10.0,
        "target_capital": 100.0,
        "broker_mode": "paper",
        "exchange": "binance",
        "api_key": "",
        "api_secret": "",
        "api_password": "",
        "quote_currency": "USDT",
        "stop_on_target": True,
        "top_n": 5,
        "min_trades": 5,
        "strategy": "AUTO",
        "strategy_pack": "max",
        "selection_mode": "winrate",
        "trade_frequency": "frequent",
        "simple_mode": False,
        "hold_minutes": 0,
        "learned_model_path": runtime_file("learned_crypto_model.json"),
        "use_learned_model": True,
        "prefer_learned_model": True,
        "learned_ignore_win_range": False,
        "train_all_symbols": True,
        "train_max_symbols": 0,
        "train_save_every": 25,
        "train_min_bars": 160,
        "success_scan_enabled": True,
        "success_fallback_enabled": True,
        "success_win_min": 55.0,
        "success_return_min": 0.0,
        "required_win_min": 70.0,
        "required_win_max": 75.0,
        "demo_train_fraction": 0.7,
        "demo_speed_ms": 80,
        "max_loops": 0,
    }
    risk = {
        "fee_rate": 0.0005,
        "slippage": 0.0002,
        "risk_per_trade": 0.01,
        "max_position_pct": 0.25,
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.04,
        "pnl_close_min_pct": 20.0,
        "pnl_close_max_pct": 30.0,
        "min_hold_bars": 3,
        "cooldown_bars": 2,
        "entry_delay_bars": 5,
        "fixed_hold_bars": 0,
        "allow_fractional": True,
        "max_open_positions": 3,
    }
    if path:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cfg.update({k: raw[k] for k in cfg if k in raw})
        if "risk" in raw and isinstance(raw["risk"], dict):
            risk.update(raw["risk"])
    cfg["interval"] = ALIAS.get(cfg["interval"], cfg["interval"])
    return cfg, risk


def save_example(path):
    cfg, risk = read_cfg(None)
    payload = dict(cfg)
    payload["risk"] = risk
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    LOG.info("Example config saved: %s", path)


def main():
    log_handlers = [logging.StreamHandler()]
    log_file = os.path.join(LOG_DIR, "adaptive_trading_runtime.log")
    try:
        log_handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    except Exception:
        pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=log_handlers,
    )
    LOG.info("Runtime isolation active: runtime_dir=%s log_dir=%s", RUNTIME_DIR, LOG_DIR)
    p = argparse.ArgumentParser(description="Adaptive trading bot: real-time scan + auto strategy selection + paper trading")
    p.add_argument("--config", type=str, default=None)
    p.add_argument("--init-config", type=str, default=None)
    p.add_argument("--mode", choices=["demo", "backtest", "live", "train"], default=None)
    p.add_argument("--symbols", nargs="+", default=None)
    p.add_argument("--interval", type=str, default=None)
    p.add_argument("--lookback-bars", type=int, default=None)
    p.add_argument("--poll-seconds", type=int, default=None)
    p.add_argument("--reoptimize-every", type=int, default=None)
    p.add_argument("--initial-capital", type=float, default=None)
    p.add_argument("--target-capital", type=float, default=None)
    p.add_argument("--broker-mode", choices=["paper", "live"], default=None)
    p.add_argument("--exchange", type=str, default=None)
    p.add_argument("--api-key", type=str, default=None)
    p.add_argument("--api-secret", type=str, default=None)
    p.add_argument("--api-password", type=str, default=None)
    p.add_argument("--quote-currency", type=str, default=None)
    p.add_argument("--top-n", type=int, default=None)
    p.add_argument("--min-trades", type=int, default=None)
    p.add_argument("--strategy", type=str, default=None, help="AUTO or one/many strategy names")
    p.add_argument("--strategy-pack", choices=["basic", "extended", "max"], default=None)
    p.add_argument("--selection-mode", choices=["score", "winrate"], default=None)
    p.add_argument("--trade-frequency", choices=["calm", "normal", "frequent", "very_frequent"], default=None)
    p.add_argument("--simple-mode", action="store_true")
    p.add_argument("--hold-minutes", type=int, choices=[0, 5, 15, 30, 60], default=None)
    p.add_argument("--learned-model-path", type=str, default=None)
    p.add_argument("--no-use-learned-model", action="store_true")
    p.add_argument("--no-prefer-learned-model", action="store_true")
    p.add_argument("--learned-ignore-win-range", action="store_true")
    p.add_argument("--train-all-symbols", action="store_true")
    p.add_argument("--train-max-symbols", type=int, default=None)
    p.add_argument("--train-save-every", type=int, default=None)
    p.add_argument("--train-min-bars", type=int, default=None)
    p.add_argument("--success-win-min", type=float, default=None)
    p.add_argument("--success-return-min", type=float, default=None)
    p.add_argument("--no-success-scan", action="store_true")
    p.add_argument("--no-success-fallback", action="store_true")
    p.add_argument("--required-win-min", type=float, default=None)
    p.add_argument("--required-win-max", type=float, default=None)
    p.add_argument("--demo-train-fraction", type=float, default=None)
    p.add_argument("--demo-speed-ms", type=float, default=None)
    p.add_argument("--fee-rate", type=float, default=None)
    p.add_argument("--slippage", type=float, default=None)
    p.add_argument("--risk-per-trade", type=float, default=None)
    p.add_argument("--max-position-pct", type=float, default=None)
    p.add_argument("--stop-loss-pct", type=float, default=None)
    p.add_argument("--take-profit-pct", type=float, default=None)
    p.add_argument("--pnl-close-min-pct", type=float, default=None)
    p.add_argument("--pnl-close-max-pct", type=float, default=None)
    p.add_argument("--min-hold-bars", type=int, default=None)
    p.add_argument("--cooldown-bars", type=int, default=None)
    p.add_argument("--entry-delay-bars", type=int, default=None)
    p.add_argument("--max-open-positions", type=int, default=None)
    p.add_argument("--max-loops", type=int, default=None)
    p.add_argument("--no-stop-on-target", action="store_true")
    a = p.parse_args()

    if a.init_config:
        save_example(a.init_config)
        return

    cfg, risk = read_cfg(a.config)
    if a.mode: cfg["mode"] = a.mode
    if a.symbols: cfg["symbols"] = [x.upper() for x in a.symbols]
    if a.interval: cfg["interval"] = ALIAS.get(a.interval, a.interval)
    if a.lookback_bars is not None: cfg["lookback_bars"] = a.lookback_bars
    if a.poll_seconds is not None: cfg["poll_seconds"] = a.poll_seconds
    if a.reoptimize_every is not None: cfg["reoptimize_every"] = a.reoptimize_every
    if a.initial_capital is not None: cfg["initial_capital"] = a.initial_capital
    if a.target_capital is not None: cfg["target_capital"] = a.target_capital
    if a.broker_mode is not None: cfg["broker_mode"] = a.broker_mode
    if a.exchange is not None: cfg["exchange"] = a.exchange.lower().strip()
    if a.api_key is not None: cfg["api_key"] = a.api_key
    if a.api_secret is not None: cfg["api_secret"] = a.api_secret
    if a.api_password is not None: cfg["api_password"] = a.api_password
    if a.quote_currency is not None: cfg["quote_currency"] = a.quote_currency.upper().strip()
    if a.top_n is not None: cfg["top_n"] = a.top_n
    if a.min_trades is not None: cfg["min_trades"] = a.min_trades
    if a.strategy is not None: cfg["strategy"] = a.strategy
    if a.strategy_pack is not None: cfg["strategy_pack"] = a.strategy_pack
    if a.selection_mode is not None: cfg["selection_mode"] = a.selection_mode
    if a.trade_frequency is not None: cfg["trade_frequency"] = a.trade_frequency
    if a.simple_mode: cfg["simple_mode"] = True
    if a.hold_minutes is not None: cfg["hold_minutes"] = int(a.hold_minutes)
    if a.learned_model_path is not None: cfg["learned_model_path"] = a.learned_model_path
    if a.no_use_learned_model: cfg["use_learned_model"] = False
    if a.no_prefer_learned_model: cfg["prefer_learned_model"] = False
    if a.learned_ignore_win_range: cfg["learned_ignore_win_range"] = True
    if a.train_all_symbols: cfg["train_all_symbols"] = True
    if a.train_max_symbols is not None: cfg["train_max_symbols"] = a.train_max_symbols
    if a.train_save_every is not None: cfg["train_save_every"] = a.train_save_every
    if a.train_min_bars is not None: cfg["train_min_bars"] = a.train_min_bars
    if a.success_win_min is not None: cfg["success_win_min"] = a.success_win_min
    if a.success_return_min is not None: cfg["success_return_min"] = a.success_return_min
    if a.no_success_scan: cfg["success_scan_enabled"] = False
    if a.no_success_fallback: cfg["success_fallback_enabled"] = False
    if a.required_win_min is not None: cfg["required_win_min"] = a.required_win_min
    if a.required_win_max is not None: cfg["required_win_max"] = a.required_win_max
    if a.demo_train_fraction is not None: cfg["demo_train_fraction"] = a.demo_train_fraction
    if a.demo_speed_ms is not None: cfg["demo_speed_ms"] = a.demo_speed_ms
    if a.fee_rate is not None: risk["fee_rate"] = a.fee_rate
    if a.slippage is not None: risk["slippage"] = a.slippage
    if a.risk_per_trade is not None: risk["risk_per_trade"] = a.risk_per_trade
    if a.max_position_pct is not None: risk["max_position_pct"] = a.max_position_pct
    if a.stop_loss_pct is not None: risk["stop_loss_pct"] = a.stop_loss_pct
    if a.take_profit_pct is not None: risk["take_profit_pct"] = a.take_profit_pct
    if a.pnl_close_min_pct is not None: risk["pnl_close_min_pct"] = a.pnl_close_min_pct
    if a.pnl_close_max_pct is not None: risk["pnl_close_max_pct"] = a.pnl_close_max_pct
    if a.min_hold_bars is not None: risk["min_hold_bars"] = a.min_hold_bars
    if a.cooldown_bars is not None: risk["cooldown_bars"] = a.cooldown_bars
    if a.entry_delay_bars is not None: risk["entry_delay_bars"] = a.entry_delay_bars
    if a.max_open_positions is not None: risk["max_open_positions"] = a.max_open_positions
    if a.max_loops is not None: cfg["max_loops"] = a.max_loops
    if a.no_stop_on_target: cfg["stop_on_target"] = False

    apply_simple_mode(cfg, risk)

    if cfg["required_win_max"] < cfg["required_win_min"]:
        raise ValueError("required_win_max must be >= required_win_min")
    cfg["hold_minutes"] = int(cfg.get("hold_minutes", 0) or 0)
    if cfg["hold_minutes"] not in {0, 5, 15, 30, 60}:
        raise ValueError("hold_minutes must be one of: 0, 5, 15, 30, 60")
    cfg["strategy_pack"] = str(cfg.get("strategy_pack", "extended") or "extended").strip().lower()
    if cfg["strategy_pack"] not in {"basic", "extended", "max"}:
        cfg["strategy_pack"] = "extended"
    cfg["selection_mode"] = str(cfg.get("selection_mode", "score") or "score").strip().lower()
    if cfg["selection_mode"] not in {"score", "winrate"}:
        cfg["selection_mode"] = "score"
    cfg["learned_model_path"] = str(
        cfg.get("learned_model_path", runtime_file("learned_crypto_model.json")) or runtime_file("learned_crypto_model.json")
    ).strip()
    if not os.path.isabs(cfg["learned_model_path"]):
        cfg["learned_model_path"] = runtime_file(cfg["learned_model_path"])
    cfg["use_learned_model"] = bool(cfg.get("use_learned_model", True))
    cfg["prefer_learned_model"] = bool(cfg.get("prefer_learned_model", True))
    cfg["learned_ignore_win_range"] = bool(cfg.get("learned_ignore_win_range", False))
    cfg["train_all_symbols"] = bool(cfg.get("train_all_symbols", False))
    cfg["train_max_symbols"] = max(0, int(cfg.get("train_max_symbols", 0) or 0))
    cfg["train_save_every"] = max(1, int(cfg.get("train_save_every", 25) or 25))
    cfg["train_min_bars"] = max(80, int(cfg.get("train_min_bars", 160) or 160))
    cfg["success_scan_enabled"] = bool(cfg.get("success_scan_enabled", True))
    cfg["success_fallback_enabled"] = bool(cfg.get("success_fallback_enabled", True))
    cfg["success_win_min"] = float(cfg.get("success_win_min", 55.0) or 55.0)
    cfg["success_return_min"] = float(cfg.get("success_return_min", 0.0) or 0.0)
    if cfg["success_win_min"] < 0:
        cfg["success_win_min"] = 0.0
    if cfg["success_win_min"] > 100:
        cfg["success_win_min"] = 100.0
    risk["pnl_close_min_pct"] = max(0.0, float(risk.get("pnl_close_min_pct", 0.0) or 0.0))
    risk["pnl_close_max_pct"] = max(0.0, float(risk.get("pnl_close_max_pct", 0.0) or 0.0))
    if risk["pnl_close_max_pct"] > 0 and risk["pnl_close_max_pct"] < risk["pnl_close_min_pct"]:
        raise ValueError("pnl_close_max_pct must be >= pnl_close_min_pct")
    risk["min_hold_bars"] = max(0, int(risk.get("min_hold_bars", 0) or 0))
    risk["cooldown_bars"] = max(0, int(risk.get("cooldown_bars", 0) or 0))
    risk["entry_delay_bars"] = max(0, int(risk.get("entry_delay_bars", 0) or 0))
    apply_trade_frequency_profile(cfg, risk)
    apply_fixed_hold_profile(cfg, risk)
    cfg["demo_train_fraction"] = min(max(cfg["demo_train_fraction"], 0.5), 0.9)
    cfg["strategy_filter"] = normalize_strategy_filter(cfg.get("strategy", "AUTO"))
    if cfg["strategy_filter"]:
        LOG.info("Strategy filter active: %s", ",".join(cfg["strategy_filter"]))
    LOG.info(
        "Strategy selection mode: %s | pack: %s | requested_win_range: %.2f-%.2f%%",
        cfg["selection_mode"],
        cfg["strategy_pack"],
        cfg["required_win_min"],
        cfg["required_win_max"],
    )
    LOG.info(
        "Success scan: enabled=%s fallback=%s min_win=%.2f%% min_ret=%.2f%%",
        cfg["success_scan_enabled"],
        cfg["success_fallback_enabled"],
        cfg["success_win_min"],
        cfg["success_return_min"],
    )
    LOG.info(
        "Learned model: use=%s prefer=%s ignore_win_range=%s path=%s",
        cfg["use_learned_model"],
        cfg["prefer_learned_model"],
        cfg["learned_ignore_win_range"],
        cfg["learned_model_path"],
    )
    if cfg["mode"] == "train":
        LOG.info(
            "Train settings: all_symbols=%s max_symbols=%d min_bars=%d save_every=%d",
            cfg["train_all_symbols"],
            cfg["train_max_symbols"],
            cfg["train_min_bars"],
            cfg["train_save_every"],
        )
    if _has_fixed_hold(risk):
        LOG.info("Time-hold mode: every trade is closed after %d bar(s).", int(risk.get("fixed_hold_bars", 0) or 0))
    if risk["pnl_close_min_pct"] > 0 or risk["pnl_close_max_pct"] > 0:
        LOG.info(
            "Trade close target active: pnl %.2f%%..%.2f%% | min_hold=%d bars | cooldown=%d bars | entry_delay=%d bars | signal exits disabled",
            risk["pnl_close_min_pct"],
            risk["pnl_close_max_pct"],
            risk["min_hold_bars"],
            risk["cooldown_bars"],
            risk["entry_delay_bars"],
        )

    if cfg["mode"] == "backtest":
        run_backtest(cfg, risk)
    elif cfg["mode"] == "live":
        run_live(cfg, risk)
    elif cfg["mode"] == "train":
        run_train(cfg, risk)
    else:
        run_demo(cfg, risk)


if __name__ == "__main__":
    main()
