"""
Buy-the-dip indicator grid search.

Standalone research script using ONLY OHLCV-derived indicators so the
resulting model can be directly translated to TradingView Pine Script.

Usage:
    python investigations/buy_dip_search.py              # QQQ search + all-ticker validation
    python investigations/buy_dip_search.py --symbol QQQ  # QQQ only
    python investigations/buy_dip_search.py --refresh     # re-download data
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "investigations"
CACHE_DIR = OUT_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

START_DATE = "2017-01-01"

MARKET_PHASES = {
    "2018_drawdown": ("2018-09-20", "2018-12-31"),
    "2020_covid_crash": ("2020-02-19", "2020-04-30"),
    "2022_bear": ("2022-01-03", "2022-12-30"),
    "2024_2026_trend": ("2024-01-01", "2026-12-31"),
    "2025_h2_pullback": ("2025-07-01", "2025-12-31"),
    "2026_april_pullback": ("2026-04-01", "2026-04-30"),
}


# ═══════════════════════════════════════════════════════
# Data loading (reused from zone research)
# ═══════════════════════════════════════════════════════


def fetch_price(symbol: str, refresh: bool = False) -> tuple[pd.DataFrame, str]:
    cache_path = CACHE_DIR / f"{symbol.lower()}_price.parquet"
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path), "yfinance-cache"

    end = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.download(symbol, start=START_DATE, end=end, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if not df.empty:
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        df.columns = [c.lower() for c in df.columns]
        df.to_parquet(cache_path)
        return df, "yfinance"

    # fallback to local parquet
    local_path = DATA_DIR / f"{symbol}.parquet"
    if local_path.exists():
        df = pd.read_parquet(local_path).copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        df.columns = [c.lower() for c in df.columns]
        return df, "local-parquet"

    raise FileNotFoundError(f"Missing price data for {symbol}")


# ═══════════════════════════════════════════════════════
# Indicator computation
# ═══════════════════════════════════════════════════════


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def clamp(series: pd.Series | float, low: float = 0, high: float = 100):
    return np.minimum(high, np.maximum(low, series))


def stochastic(close: pd.Series, high: pd.Series, low: pd.Series, period: int = 14) -> pd.Series:
    """Compute Stochastic %K (fast)."""
    lowest = low.rolling(period).min()
    highest = high.rolling(period).max()
    denom = (highest - lowest).replace(0, np.nan)
    return ((close - lowest) / denom) * 100


def build_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all price-based indicators from OHLCV data."""
    out = df.copy()
    close = out["close"]
    high = out["high"]
    low = out["low"]

    # RSI
    out["rsi14"] = rsi(close, 14)

    # Stochastic %K(14)
    out["stoch14"] = stochastic(close, high, low, 14)

    # Keltner Channel (EMA20 ± 2*ATR20) — replaces Bollinger Bands
    out["ema20"] = close.ewm(span=20, adjust=False).mean()
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    out["atr20"] = tr.rolling(20).mean()
    out["keltner_lower"] = out["ema20"] - 2 * out["atr20"]
    out["keltner_upper"] = out["ema20"] + 2 * out["atr20"]
    # distance below lower band as percentage
    out["keltner_dist"] = (out["keltner_lower"] - close) / out["keltner_lower"] * 100

    # ATR volatility ratio: ATR(14) / SMA(ATR(14), 70)
    atr14 = tr.rolling(14).mean()
    atr70 = atr14.rolling(70).mean()
    out["atr_ratio"] = atr14 / atr70.replace(0, np.nan)

    # EMA trend filter: 21 / 55 / 100 / 200
    out["ema21"] = close.ewm(span=21, adjust=False).mean()
    out["ema55"] = close.ewm(span=55, adjust=False).mean()
    out["ema100"] = close.ewm(span=100, adjust=False).mean()
    out["ema200"] = close.ewm(span=200, adjust=False).mean()

    # SMA 200 (kept for reference)
    out["sma200"] = close.rolling(200).mean()
    out["dist_sma200"] = (close / out["sma200"] - 1) * 100

    # 252-day drawdown (1 year rolling high)
    out["high252"] = close.rolling(252).max()
    out["drawdown252"] = (close / out["high252"] - 1) * 100

    return out.dropna(subset=["sma200", "rsi14", "keltner_lower"])


def score_buy_signals(df: pd.DataFrame, cfg: DipConfig) -> pd.DataFrame:
    """Compute weighted composite buy score from indicators."""
    out = df.copy()

    # Each component scored 0-100, higher = more panic/oversold
    rsi_score = clamp((50 - out["rsi14"]) * 2)

    # Keltner: score by distance from EMA20 in ATR units (more meaningful than band-edge %)
    # 1.7 ATR below EMA = 50 pts, 3.3 ATR = 100
    keltner_atr_dist = (out["ema20"] - out["close"]) / out["atr20"]  # positive = below EMA
    keltner_score = clamp(keltner_atr_dist * 30)

    sma200_score = clamp(-out["dist_sma200"] * 3)  # 1% below SMA → 3 points
    drawdown_score = clamp(-out["drawdown252"] * 2.5)  # 1% drawdown → 2.5 points
    atr_score = clamp((out["atr_ratio"] - 1) * 40)  # 1.5x ATR → 20 points

    # RSI + Stochastic dual confirmation
    rsi_oversold = (50 - out["rsi14"]).clip(lower=0) * 2  # 0-100 when RSI<50
    stoch_oversold = (50 - out["stoch14"]).clip(lower=0) * 2  # 0-100 when Stoch<50
    # Both must be oversold for full score; RSI<30 AND Stoch<20 = max bonus
    dual_raw = (rsi_oversold + stoch_oversold) / 2
    # Extra bonus when both are deeply oversold (RSI<30, Stoch<20)
    deep_bonus = ((out["rsi14"] < 30) & (out["stoch14"] < 20)).astype(float) * 20
    stoch_score = clamp(dual_raw + deep_bonus)

    # EMA trend filter: bearish alignment (21<55<100<200) = oversold signals amplified
    ema_trend = (
        (out["ema21"] < out["ema55"]).astype(float)
        + (out["ema55"] < out["ema100"]).astype(float)
        + (out["ema100"] < out["ema200"]).astype(float)
    ) / 3  # 0=bullish, 1=bearish
    # Additive modifier: -4 pts (bull) to +4 pts (bear) — gentle nudge
    trend_modifier = (ema_trend - 0.5) * 8

    out["rsi_score"] = rsi_score
    out["keltner_score"] = keltner_score
    out["sma200_score"] = sma200_score
    out["drawdown_score"] = drawdown_score
    out["atr_score"] = atr_score
    out["stoch_score"] = stoch_score
    out["ema_trend"] = ema_trend

    raw_score = (
        cfg.w_rsi * rsi_score
        + cfg.w_keltner * keltner_score
        + cfg.w_sma200 * sma200_score
        + cfg.w_drawdown * drawdown_score
        + cfg.w_atr * atr_score
        + cfg.w_stoch * stoch_score
    )
    out["composite_score"] = clamp(raw_score + trend_modifier)

    out["buy_signal"] = out["composite_score"] >= cfg.buy_threshold
    return out


# ═══════════════════════════════════════════════════════
# Config and grid search
# ═══════════════════════════════════════════════════════


@dataclass
class DipConfig:
    name: str
    w_rsi: float
    w_keltner: float
    w_sma200: float
    w_drawdown: float
    w_atr: float
    w_stoch: float
    buy_threshold: float


WEIGHT_SETS = [
    # (rsi, keltner, sma200, drawdown, atr, stoch)
    (0.25, 0.20, 0.15, 0.15, 0.10, 0.15),  # rsi-heavy
    (0.20, 0.15, 0.15, 0.20, 0.15, 0.15),  # drawdown-heavy
    (0.17, 0.17, 0.17, 0.17, 0.16, 0.16),  # equal weight
    (0.20, 0.25, 0.10, 0.15, 0.15, 0.15),  # keltner-heavy
    (0.25, 0.10, 0.20, 0.15, 0.15, 0.15),  # rsi+sma200
    (0.15, 0.15, 0.25, 0.20, 0.10, 0.15),  # sma200+drawdown
    (0.20, 0.15, 0.15, 0.10, 0.25, 0.15),  # atr-heavy
    (0.20, 0.15, 0.15, 0.15, 0.10, 0.25),  # stoch-heavy
    (0.30, 0.25, 0.05, 0.10, 0.10, 0.20),  # oscillator-heavy
    (0.20, 0.20, 0.10, 0.10, 0.20, 0.20),  # balanced-osc
]


def candidate_configs() -> list[DipConfig]:
    configs = []
    seen = set()
    for w_rsi, w_keltner, w_sma200, w_dd, w_atr, w_stoch in WEIGHT_SETS:
        for threshold in [20, 25, 30, 35, 40, 45, 50]:
            key = (w_rsi, w_keltner, w_sma200, w_dd, w_atr, w_stoch, threshold)
            if key in seen:
                continue
            seen.add(key)
            configs.append(
                DipConfig(
                    name=f"r{w_rsi:.2f}_k{w_keltner:.2f}_s{w_sma200:.2f}_d{w_dd:.2f}_a{w_atr:.2f}_st{w_stoch:.2f}_t{threshold}",
                    w_rsi=w_rsi,
                    w_keltner=w_keltner,
                    w_sma200=w_sma200,
                    w_drawdown=w_dd,
                    w_atr=w_atr,
                    w_stoch=w_stoch,
                    buy_threshold=threshold,
                )
            )
    return configs


# ═══════════════════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════════════════


def future_return(close: pd.Series, days: int) -> pd.Series:
    return (close.shift(-days) / close - 1) * 100


def forward_drawdown(close: pd.Series, days: int) -> pd.Series:
    values = []
    arr = close.to_numpy()
    for i, current in enumerate(arr):
        future = arr[i + 1: i + days + 1]
        if len(future) == 0 or current <= 0:
            values.append(np.nan)
        else:
            values.append((np.nanmin(future) / current - 1) * 100)
    return pd.Series(values, index=close.index)


def phase_coverage(df: pd.DataFrame, buy_mask: pd.Series) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for name, (start, end) in MARKET_PHASES.items():
        phase = df.loc[start:end]
        if phase.empty:
            summary[name] = {"available": False}
            continue
        phase_buys = buy_mask.loc[start:end]
        summary[name] = {
            "available": True,
            "start": phase.index.min().date().isoformat(),
            "end": phase.index.max().date().isoformat(),
            "buyDays": int(phase_buys.sum()),
            "phaseDays": len(phase),
            "buyCoveragePct": round(float(phase_buys.mean() * 100), 2),
        }
    return summary


def reference_dca_return(df: pd.DataFrame, buy_mask: pd.Series) -> dict[str, float]:
    """Simulate DCA: invest equal amount on each buy signal day, hold to end."""
    close = df["close"].to_numpy()
    buy_indices = np.where(buy_mask.to_numpy())[0]

    if len(buy_indices) == 0:
        return {"strategyReturnPct": 0, "buyHoldReturnPct": 0, "signalCount": 0}

    # Each buy signal invests $1, compute average cost and final value
    total_cost = 0.0
    total_shares = 0.0
    for idx in buy_indices:
        total_cost += 1.0
        total_shares += 1.0 / close[idx]

    avg_cost_per_share = total_cost / total_shares
    final_price = close[-1]
    strategy_return = (final_price / avg_cost_per_share - 1) * 100

    # Buy-and-hold: invest $1 on first day
    buy_hold_return = (close[-1] / close[0] - 1) * 100

    return {
        "strategyReturnPct": round(strategy_return, 2),
        "buyHoldReturnPct": round(buy_hold_return, 2),
        "excessReturnPct": round(strategy_return - buy_hold_return, 2),
        "signalCount": int(len(buy_indices)),
        "avgCostPerShare": round(avg_cost_per_share, 2),
    }


def evaluate(df: pd.DataFrame, cfg: DipConfig) -> dict[str, Any]:
    """Evaluate one config on one symbol."""
    scored = score_buy_signals(df, cfg)
    buy = scored["buy_signal"]
    buy_count = int(buy.sum())

    if buy_count == 0:
        return {
            "score": -999,
            "buyDays": 0,
            "config": asdict(cfg),
        }

    # Forward returns after buy signals
    fwd_63 = future_return(scored["close"], 63)[buy]
    fwd_126 = future_return(scored["close"], 126)[buy]
    fwd_252 = future_return(scored["close"], 252)[buy]

    # Win rate (positive 63-day return)
    win_rate_63 = float((fwd_63 > 0).mean() * 100) if len(fwd_63) > 0 else 0

    # Average forward return
    avg_fwd_63 = float(fwd_63.mean()) if len(fwd_63) > 0 and fwd_63.notna().any() else 0
    avg_fwd_126 = float(fwd_126.mean()) if len(fwd_126) > 0 and fwd_126.notna().any() else 0
    avg_fwd_252 = float(fwd_252.mean()) if len(fwd_252) > 0 and fwd_252.notna().any() else 0

    # Phase coverage
    phases = phase_coverage(scored, buy)

    # Reference DCA return
    ref = reference_dca_return(scored, buy)

    # Composite score:
    # - Higher forward returns = better
    # - Higher win rate = better
    # - Penalize too few (< 5) or too many (> 80) signals
    # - Bonus for covering crash phases
    signal_penalty = 0
    if buy_count < 8:
        signal_penalty = (8 - buy_count) * 5
    elif buy_count > 120:
        signal_penalty = (buy_count - 120) * 0.3

    phase_bonus = 0
    for crash_phase in ["2020_covid_crash", "2022_bear"]:
        p = phases.get(crash_phase, {})
        if p.get("available") and p.get("buyDays", 0) >= 2:
            phase_bonus += 10
        elif p.get("available") and p.get("buyDays", 0) >= 1:
            phase_bonus += 5

    for pullback_phase in ["2025_h2_pullback", "2026_april_pullback"]:
        p = phases.get(pullback_phase, {})
        if p.get("available") and p.get("buyDays", 0) >= 1:
            phase_bonus += 5

    score = (
        avg_fwd_63 * 1.0
        + avg_fwd_126 * 0.6
        + avg_fwd_252 * 0.3
        + win_rate_63 * 0.3
        + min(ref["excessReturnPct"], 50) * 0.2
        + phase_bonus
        - signal_penalty
    )

    return {
        "score": round(float(score), 2) if math.isfinite(score) else -999,
        "buyDays": buy_count,
        "config": asdict(cfg),
        "forwardReturns": {
            "avg3mPct": round(avg_fwd_63, 2),
            "avg6mPct": round(avg_fwd_126, 2),
            "avg12mPct": round(avg_fwd_252, 2),
            "winRate3mPct": round(win_rate_63, 1),
        },
        "phaseCoverage": phases,
        "reference": ref,
        "scoreComponents": {
            "fwdReturn": round(avg_fwd_63 * 1.0 + avg_fwd_126 * 0.6 + avg_fwd_252 * 0.3, 2),
            "winRate": round(win_rate_63 * 0.3, 2),
            "phaseBonus": phase_bonus,
            "signalPenalty": signal_penalty,
        },
        "latest": {
            "date": scored.index[-1].date().isoformat(),
            "close": round(float(scored["close"].iloc[-1]), 2),
            "compositeScore": round(float(scored["composite_score"].iloc[-1]), 2),
            "buySignal": bool(buy.iloc[-1]),
            "rsi": round(float(scored["rsi14"].iloc[-1]), 2),
            "distSma200": round(float(scored["dist_sma200"].iloc[-1]), 2),
            "drawdown252": round(float(scored["drawdown252"].iloc[-1]), 2),
        },
    }


# ═══════════════════════════════════════════════════════
# Multi-symbol ranking
# ═══════════════════════════════════════════════════════


def combined_rank(
    configs: list[DipConfig],
    metrics_by_symbol: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    ranked = []
    for index, cfg in enumerate(configs):
        by_symbol = {s: m[index] for s, m in metrics_by_symbol.items()}
        scores = [p["score"] for p in by_symbol.values() if p["score"] > -900]
        if not scores:
            continue
        buy_days = [p["buyDays"] for p in by_symbol.values() if p["score"] > -900]
        stability_penalty = (
            (max(scores) - min(scores)) * 0.15
            + abs(max(buy_days) - min(buy_days)) * 0.05
        )
        combined = float(np.mean(scores) - stability_penalty)
        ranked.append({
            "config": asdict(cfg),
            "combinedScore": round(combined, 2),
            "symbols": by_symbol,
        })
    ranked.sort(key=lambda x: x["combinedScore"], reverse=True)
    return ranked


# ═══════════════════════════════════════════════════════
# Output
# ═══════════════════════════════════════════════════════


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    return value


def generate_pine_script(cfg: DipConfig) -> str:
    """Generate TradingView Pine Script v5 from optimized config."""
    return f'''//@version=5
indicator("Buy-the-Dip DCA Signal v2", overlay=true, max_labels_count=500)

// ═══════════════════════════════════════════════════════
// Inputs (optimized by grid search on QQQ)
// ═══════════════════════════════════════════════════════
w_rsi      = input.float({cfg.w_rsi:.2f}, "RSI Weight",        minval=0, maxval=1, step=0.05)
w_keltner  = input.float({cfg.w_keltner:.2f}, "Keltner Weight",    minval=0, maxval=1, step=0.05)
w_sma200   = input.float({cfg.w_sma200:.2f}, "SMA200 Weight",     minval=0, maxval=1, step=0.05)
w_drawdown = input.float({cfg.w_drawdown:.2f}, "Drawdown Weight",   minval=0, maxval=1, step=0.05)
w_atr      = input.float({cfg.w_atr:.2f}, "ATR Vol Weight",     minval=0, maxval=1, step=0.05)
w_stoch    = input.float({cfg.w_stoch:.2f}, "Stochastic Weight",  minval=0, maxval=1, step=0.05)
threshold  = input.float({cfg.buy_threshold:.0f}, "Buy Threshold",     minval=10, maxval=90, step=5)

// ═══════════════════════════════════════════════════════
// Indicators
// ═══════════════════════════════════════════════════════
rsi_val    = ta.rsi(close, 14)
stoch_val  = ta.stoch(close, high, low, 14)

// Keltner Channel (EMA20 ± 2*ATR20)
ema20_val  = ta.ema(close, 20)
atr20_val  = ta.atr(20)
kelt_lower = ema20_val - 2 * atr20_val
kelt_atr_dist = (ema20_val - close) / atr20_val

// ATR volatility ratio: ATR(14) / SMA(ATR(14), 70)
atr14_val  = ta.atr(14)
atr70_avg  = ta.sma(atr14_val, 70)
atr_ratio  = atr14_val / atr70_avg

// SMA 200 distance
sma200      = ta.sma(close, 200)
dist_sma200 = (close / sma200 - 1) * 100

// 252-day drawdown
high252     = ta.highest(close, 252)
drawdown252 = (close / high252 - 1) * 100

// EMA trend filter: 21 / 55 / 100 / 200
ema21  = ta.ema(close, 21)
ema55  = ta.ema(close, 55)
ema100 = ta.ema(close, 100)
ema200 = ta.ema(close, 200)

// ═══════════════════════════════════════════════════════
// Scoring (0-100 each)
// ═══════════════════════════════════════════════════════
rsi_score      = math.max(0, math.min(100, (50 - rsi_val) * 2))
keltner_score  = math.max(0, math.min(100, kelt_atr_dist * 30))
sma200_score   = math.max(0, math.min(100, -dist_sma200 * 3))
drawdown_score = math.max(0, math.min(100, -drawdown252 * 2.5))
atr_score      = math.max(0, math.min(100, (atr_ratio - 1) * 40))

// RSI + Stochastic dual confirmation
rsi_raw   = math.max(0, (50 - rsi_val) * 2)
stoch_raw = math.max(0, (50 - stoch_val) * 2)
deep_bonus = (rsi_val < 30 and stoch_val < 20) ? 20.0 : 0.0
stoch_score  = math.max(0, math.min(100, (rsi_raw + stoch_raw) / 2 + deep_bonus))

// EMA trend filter: additive modifier (-6 bull to +6 bear)
ema_trend = ((ema21 < ema55 ? 1.0 : 0.0) + (ema55 < ema100 ? 1.0 : 0.0) + (ema100 < ema200 ? 1.0 : 0.0)) / 3.0
trend_mod = (ema_trend - 0.5) * 8

raw_score = w_rsi * rsi_score + w_keltner * keltner_score + w_sma200 * sma200_score
          + w_drawdown * drawdown_score + w_atr * atr_score + w_stoch * stoch_score
composite = math.max(0, math.min(100, raw_score + trend_mod))

// ═══════════════════════════════════════════════════════
// Signal
// ═══════════════════════════════════════════════════════
buy_signal = composite >= threshold and not na(sma200)

// Background: panic intensity gradient
bgcolor(buy_signal ? color.new(color.green, 70) : na, title="Buy Zone")

// Buy label
plotshape(buy_signal, title="DCA Buy", style=shape.labelup,
     location=location.belowbar, color=color.green, text="BUY",
     textcolor=color.white, size=size.small)

// Score plot
plot(composite, title="Panic Score", color=color.new(color.orange, 0),
     linewidth=1, display=display.none)
hline(threshold, "Threshold", color=color.red, linestyle=hline.style_dashed)

// Debug: component scores (hidden by default)
plot(rsi_score,      "RSI Score",      color=color.blue,   display=display.none)
plot(keltner_score,  "Keltner Score",  color=color.purple, display=display.none)
plot(sma200_score,   "SMA200 Score",   color=color.gray,   display=display.none)
plot(drawdown_score, "Drawdown Score", color=color.red,    display=display.none)
plot(atr_score,      "ATR Score",      color=color.teal,   display=display.none)
plot(stoch_score,    "Stoch Score",    color=color.orange, display=display.none)
'''


def write_report(results: dict[str, Any]) -> None:
    lines = [
        "# Buy-the-Dip Indicator Search Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Method",
        "",
        "Pure OHLCV-based indicators, grid-searched weights and thresholds.",
        "No external data (VIX, CAPE, CNN F&G) — only price and volume.",
        "",
        "Indicators:",
        "- RSI(14) oversold score",
        "- Keltner Channel (EMA20 ± 2×ATR20) lower breakout score",
        "- Price below SMA(200) score",
        "- 252-day drawdown score",
        "- ATR volatility ratio: ATR(14)/SMA(ATR(14),70) panic spike",
        "- RSI + Stochastic(14) dual confirmation score",
        "- EMA 21/55/100/200 trend filter (bear bonus, bull penalty)",
        "",
        "Evaluation: forward returns (3/6/12m) after buy signals, win rate,",
        "DCA return vs buy-and-hold, crash phase coverage.",
        "",
    ]

    for symbol, payload in results["symbols"].items():
        meta = payload["dataMeta"]
        lines.extend([
            f"## {symbol}",
            "",
            f"- Data: {meta['priceSource']} ({meta['priceStart']} to {meta['priceEnd']})",
            f"- Rows: {meta['priceRows']}",
            "",
        ])

        best = payload["best"]
        fwd = best["forwardReturns"]
        ref = best["reference"]
        cfg = best["config"]
        lines.extend([
            "### Best single-symbol config",
            "",
            f"- Config: `{cfg['name']}`",
            f"- Score: {best['score']:.2f}",
            f"- Buy days: {best['buyDays']}",
            f"- Avg 3m return: {fwd['avg3mPct']:.2f}%",
            f"- Avg 6m return: {fwd['avg6mPct']:.2f}%",
            f"- Avg 12m return: {fwd['avg12mPct']:.2f}%",
            f"- Win rate (3m): {fwd['winRate3mPct']:.1f}%",
            f"- DCA return: {ref['strategyReturnPct']:.2f}%",
            f"- Buy & Hold: {ref['buyHoldReturnPct']:.2f}%",
            f"- Excess: {ref['excessReturnPct']:.2f}%",
            "",
            "Phase coverage:",
            "",
        ])
        for phase, p in best["phaseCoverage"].items():
            if not p.get("available"):
                lines.append(f"- {phase}: unavailable")
            else:
                lines.append(
                    f"- {phase}: {p['buyDays']} buy days / {p['phaseDays']} total "
                    f"({p['buyCoveragePct']:.1f}%)"
                )
        lines.append("")

    recommended = results["recommendedDefault"]
    cfg = recommended["config"]
    lines.extend([
        "## Recommended joint config",
        "",
        f"- Config: `{cfg['name']}`",
        f"- Combined score: {recommended['combinedScore']:.2f}",
        f"- Weights: RSI={cfg['w_rsi']:.2f}, Keltner={cfg['w_keltner']:.2f}, "
        f"SMA200={cfg['w_sma200']:.2f}, DD={cfg['w_drawdown']:.2f}, "
        f"ATR={cfg['w_atr']:.2f}, Stoch={cfg['w_stoch']:.2f}",
        f"- Buy threshold: {cfg['buy_threshold']:.0f}",
        "",
        "Per-symbol results:",
        "",
    ])
    for symbol, metrics in recommended["symbols"].items():
        ref = metrics.get("reference", {})
        fwd = metrics.get("forwardReturns", {})
        lines.extend([
            f"### {symbol}",
            "",
            f"- Buy days: {metrics['buyDays']}",
            f"- Avg 3m return: {fwd.get('avg3mPct', 0):.2f}%",
            f"- Win rate (3m): {fwd.get('winRate3mPct', 0):.1f}%",
            f"- DCA return: {ref.get('strategyReturnPct', 0):.2f}%",
            f"- Buy & Hold: {ref.get('buyHoldReturnPct', 0):.2f}%",
            f"- Excess: {ref.get('excessReturnPct', 0):.2f}%",
            "",
        ])

    # Per-symbol best configs
    per_symbol = results.get("perSymbolBest", {})
    if per_symbol:
        lines.extend(["## Per-symbol optimal configs", ""])
        lines.extend([
            "| Symbol | Config | Threshold | Buy Days | 3m Return | Win Rate | DCA % | Excess % |",
            "|--------|--------|-----------|----------|-----------|----------|-------|----------|",
        ])
        for symbol, best in per_symbol.items():
            if "error" in best:
                lines.append(f"| {symbol} | {best['error']} | - | - | - | - | - | - |")
                continue
            cfg = best["config"]
            fwd = best.get("forwardReturns", {})
            ref = best.get("reference", {})
            lines.append(
                f"| {symbol} | `{cfg['name']}` | {cfg['buy_threshold']:.0f} | "
                f"{best['buyDays']} | {fwd.get('avg3mPct', 0):.1f}% | "
                f"{fwd.get('winRate3mPct', 0):.0f}% | "
                f"{ref.get('strategyReturnPct', 0):.1f}% | "
                f"{ref.get('excessReturnPct', 0):.1f}% |"
            )
        lines.append("")

    lines.extend([
        "## TradingView Pine Script",
        "",
        "See `buy_dip_pine.pine` — ready to paste into TradingView Pine Editor.",
        "All weights and threshold are configurable via TradingView input panel.",
        "",
    ])

    text = "\n".join(lines)
    (OUT_DIR / "buy_dip_report.md").write_text(text, encoding="utf-8", newline="\n")


# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════


def run(search_symbols: list[str], validate_symbols: list[str], refresh: bool) -> dict[str, Any]:
    output: dict[str, Any] = {
        "generatedAt": datetime.now().isoformat(),
        "searchSymbols": search_symbols,
        "validateSymbols": validate_symbols,
    }

    configs = candidate_configs()
    output["searchSpace"] = {"configCount": len(configs)}

    # Phase 1: grid search on search symbols
    metrics_by_symbol: dict[str, list[dict[str, Any]]] = {}
    metas: dict[str, dict[str, Any]] = {}

    for symbol in search_symbols:
        df, source = fetch_price(symbol, refresh)
        df = build_indicators(df)
        metas[symbol] = {
            "priceSource": source,
            "priceRows": len(df),
            "priceStart": df.index.min().date().isoformat(),
            "priceEnd": df.index.max().date().isoformat(),
        }

        ranked = []
        for cfg in configs:
            metrics = evaluate(df, cfg)
            ranked.append(metrics)
        metrics_by_symbol[symbol] = ranked

        ranked_sorted = sorted(ranked, key=lambda x: x["score"], reverse=True)
        output.setdefault("symbols", {})[symbol] = {
            "dataMeta": metas[symbol],
            "best": ranked_sorted[0],
            "top5": ranked_sorted[:5],
        }

    # Combined ranking across search symbols
    combined = combined_rank(configs, metrics_by_symbol)
    output["recommendedDefault"] = combined[0]
    output["combinedTop10"] = combined[:10]

    # Phase 2: per-symbol search on all validation symbols
    per_symbol_best: dict[str, dict[str, Any]] = {}
    for symbol in validate_symbols:
        if symbol in output.get("symbols", {}):
            per_symbol_best[symbol] = output["symbols"][symbol]["best"]
            continue
        try:
            df, source = fetch_price(symbol, refresh)
            df = build_indicators(df)
        except FileNotFoundError:
            per_symbol_best[symbol] = {"error": "data not found"}
            continue

        ranked = []
        for cfg in configs:
            metrics = evaluate(df, cfg)
            ranked.append(metrics)
        ranked.sort(key=lambda x: x["score"], reverse=True)
        per_symbol_best[symbol] = ranked[0]

    output["perSymbolBest"] = per_symbol_best

    # Phase 3: validate recommended config on all symbols
    best_cfg_name = combined[0]["config"]["name"]
    best_cfg = next(c for c in configs if c.name == best_cfg_name)

    validation_results = {}
    for symbol in validate_symbols:
        try:
            df, source = fetch_price(symbol, refresh)
            df = build_indicators(df)
        except FileNotFoundError:
            validation_results[symbol] = {"error": "data not found"}
            continue

        metrics = evaluate(df, best_cfg)
        validation_results[symbol] = metrics

    output["validation"] = validation_results

    # Phase 3: generate Pine Script
    pine = generate_pine_script(best_cfg)
    (OUT_DIR / "buy_dip_pine.pine").write_text(pine, encoding="utf-8", newline="\n")
    output["pineScript"] = str(OUT_DIR / "buy_dip_pine.pine")

    output = json_safe(output)
    (OUT_DIR / "buy_dip_results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    write_report(output)

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Buy-the-dip indicator grid search")
    parser.add_argument(
        "--symbol", choices=["QQQ", "SPY", "all"], default="all",
        help="Symbols to search (default: all = QQQ + SPY for search, all 21 for validation)",
    )
    parser.add_argument("--refresh", action="store_true", help="Refresh data caches")
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT))
    from config import ALL_TICKERS, DEV_TICKERS

    if args.symbol == "all":
        search = ["QQQ", "SPY"]
        validate = ALL_TICKERS
    elif args.symbol == "QQQ":
        search = ["QQQ"]
        validate = DEV_TICKERS
    else:
        search = ["SPY"]
        validate = DEV_TICKERS

    result = run(search, validate, args.refresh)
    recommended = result["recommendedDefault"]
    cfg = recommended["config"]
    print(
        f"Recommended: {cfg['name']} combined={recommended['combinedScore']:.2f} "
        f"threshold={cfg['buy_threshold']:.0f}"
    )
    print(f"Weights: RSI={cfg['w_rsi']:.2f} Keltner={cfg['w_keltner']:.2f} "
          f"SMA200={cfg['w_sma200']:.2f} DD={cfg['w_drawdown']:.2f} "
          f"ATR={cfg['w_atr']:.2f} Stoch={cfg['w_stoch']:.2f}")

    for symbol, metrics in recommended["symbols"].items():
        ref = metrics.get("reference", {})
        print(f"  {symbol}: buys={metrics['buyDays']} "
              f"dca={ref.get('strategyReturnPct', 0):.1f}% "
              f"b&h={ref.get('buyHoldReturnPct', 0):.1f}% "
              f"excess={ref.get('excessReturnPct', 0):.1f}%")

    # Validation summary
    val = result.get("validation", {})
    if val:
        print(f"\nValidation ({len(val)} tickers):")
        for symbol, metrics in val.items():
            if "error" in metrics:
                print(f"  {symbol}: {metrics['error']}")
            else:
                ref = metrics.get("reference", {})
                print(f"  {symbol}: buys={metrics['buyDays']} "
                      f"dca={ref.get('strategyReturnPct', 0):.1f}% "
                      f"excess={ref.get('excessReturnPct', 0):.1f}%")


if __name__ == "__main__":
    main()
