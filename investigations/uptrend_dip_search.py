"""
Uptrend dip buy + sell signal grid search.

Two buy strategies (trend pullback / breakout confirmation),
two sell strategies (trend reversal / overbought exit),
with discrete trade simulation and Pine Script generation.

Usage:
    python investigations/uptrend_dip_search.py              # QQQ+SPY search, all validation
    python investigations/uptrend_dip_search.py --symbol QQQ  # QQQ only
    python investigations/uptrend_dip_search.py --refresh     # re-download data
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, fields
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
# Utilities (reused from buy_dip_search.py)
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


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def clamp(series: pd.Series | float, low: float = 0, high: float = 100):
    return np.minimum(high, np.maximum(low, series))


def stochastic(close: pd.Series, high: pd.Series, low: pd.Series, period: int = 14) -> pd.Series:
    lowest = low.rolling(period).min()
    highest = high.rolling(period).max()
    denom = (highest - lowest).replace(0, np.nan)
    return ((close - lowest) / denom) * 100


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


# ═══════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════


@dataclass
class UptrendDipConfig:
    name: str
    buy_strategy: str  # "pullback", "breakout", "both"

    # Buy pullback weights
    w_pb_trend: float
    w_pb_level: float
    w_pb_rsi: float
    w_pb_stoch: float
    w_pb_volume: float

    # Buy breakout weights
    w_bo_range: float
    w_bo_signal: float
    w_bo_volume: float
    w_bo_momentum: float
    w_bo_trend: float

    buy_threshold: float

    # Sell weights
    w_sell_breakdown: float
    w_sell_cross: float
    w_sell_rsi_break: float
    w_sell_overbought: float
    w_sell_keltner_upper: float
    w_sell_profit: float

    sell_threshold: float
    stop_loss_pct: float


# Pullback weight sets: (trend, level, rsi, stoch, volume)
PB_WEIGHT_SETS = [
    (0.30, 0.25, 0.20, 0.15, 0.10),  # trend-heavy
    (0.20, 0.20, 0.25, 0.20, 0.15),  # oscillator-heavy
    (0.20, 0.20, 0.20, 0.20, 0.20),  # equal
    (0.15, 0.30, 0.20, 0.15, 0.20),  # pullback+volume
    (0.25, 0.15, 0.30, 0.20, 0.10),  # rsi-heavy
]

# Breakout weight sets: (range, signal, volume, momentum, trend)
BO_WEIGHT_SETS = [
    (0.15, 0.30, 0.20, 0.20, 0.15),  # signal-heavy
    (0.20, 0.20, 0.25, 0.20, 0.15),  # volume-heavy
    (0.20, 0.20, 0.20, 0.20, 0.20),  # equal
    (0.25, 0.15, 0.20, 0.25, 0.15),  # range+momentum
    (0.10, 0.25, 0.15, 0.20, 0.30),  # trend-heavy
]

# Sell weight sets: (breakdown, cross, rsi_break, overbought, keltner_upper, profit)
SELL_WEIGHT_SETS = [
    (0.30, 0.25, 0.20, 0.10, 0.10, 0.05),  # reversal-heavy
    (0.10, 0.10, 0.10, 0.30, 0.20, 0.20),  # overbought-heavy
    (0.20, 0.15, 0.15, 0.20, 0.15, 0.15),  # balanced
    (0.15, 0.30, 0.15, 0.15, 0.10, 0.15),  # cross-heavy
    (0.20, 0.10, 0.20, 0.15, 0.15, 0.20),  # profit-target
    (0.05, 0.05, 0.05, 0.40, 0.25, 0.20),  # pure overbought
    (0.05, 0.05, 0.05, 0.30, 0.15, 0.40),  # pure profit
    (0.10, 0.05, 0.15, 0.25, 0.25, 0.20),  # overbought+keltner
    (0.25, 0.10, 0.25, 0.15, 0.10, 0.15),  # reversal+rsi
    (0.15, 0.15, 0.10, 0.25, 0.20, 0.15),  # balanced-ob
]


def _default_sell() -> tuple[float, float, float, float, float, float]:
    return SELL_WEIGHT_SETS[2]  # balanced


def _default_sell_threshold() -> float:
    return 35.0


def _default_stop() -> float:
    return 7.0


def candidate_configs_stage1() -> list[UptrendDipConfig]:
    """Stage 1: buy configs only (sell/stop set to defaults)."""
    configs = []
    seen = set()
    default_sell = _default_sell()
    for strategy in ["pullback", "breakout", "both"]:
        weight_sets = PB_WEIGHT_SETS if strategy == "pullback" else (
            BO_WEIGHT_SETS if strategy == "breakout" else PB_WEIGHT_SETS
        )
        for ws in weight_sets:
            for threshold in [25, 30, 35, 40, 45, 50, 55]:
                if strategy == "pullback":
                    key = ("pb", ws, threshold)
                    if key in seen:
                        continue
                    seen.add(key)
                    configs.append(UptrendDipConfig(
                        name=f"pb_t{ws[0]:.2f}_l{ws[1]:.2f}_r{ws[2]:.2f}_s{ws[3]:.2f}_v{ws[4]:.2f}_t{threshold}",
                        buy_strategy="pullback",
                        w_pb_trend=ws[0], w_pb_level=ws[1], w_pb_rsi=ws[2],
                        w_pb_stoch=ws[3], w_pb_volume=ws[4],
                        w_bo_range=0, w_bo_signal=0, w_bo_volume=0,
                        w_bo_momentum=0, w_bo_trend=0,
                        buy_threshold=threshold,
                        w_sell_breakdown=default_sell[0], w_sell_cross=default_sell[1],
                        w_sell_rsi_break=default_sell[2], w_sell_overbought=default_sell[3],
                        w_sell_keltner_upper=default_sell[4], w_sell_profit=default_sell[5],
                        sell_threshold=_default_sell_threshold(),
                        stop_loss_pct=_default_stop(),
                    ))
                elif strategy == "breakout":
                    key = ("bo", ws, threshold)
                    if key in seen:
                        continue
                    seen.add(key)
                    configs.append(UptrendDipConfig(
                        name=f"bo_r{ws[0]:.2f}_s{ws[1]:.2f}_v{ws[2]:.2f}_m{ws[3]:.2f}_t{ws[4]:.2f}_t{threshold}",
                        buy_strategy="breakout",
                        w_pb_trend=0, w_pb_level=0, w_pb_rsi=0,
                        w_pb_stoch=0, w_pb_volume=0,
                        w_bo_range=ws[0], w_bo_signal=ws[1], w_bo_volume=ws[2],
                        w_bo_momentum=ws[3], w_bo_trend=ws[4],
                        buy_threshold=threshold,
                        w_sell_breakdown=default_sell[0], w_sell_cross=default_sell[1],
                        w_sell_rsi_break=default_sell[2], w_sell_overbought=default_sell[3],
                        w_sell_keltner_upper=default_sell[4], w_sell_profit=default_sell[5],
                        sell_threshold=_default_sell_threshold(),
                        stop_loss_pct=_default_stop(),
                    ))
                else:  # both
                    key = ("both", ws, threshold)
                    if key in seen:
                        continue
                    seen.add(key)
                    # Use same weights for both pullback and breakout
                    configs.append(UptrendDipConfig(
                        name=f"both_t{ws[0]:.2f}_l{ws[1]:.2f}_r{ws[2]:.2f}_s{ws[3]:.2f}_v{ws[4]:.2f}_t{threshold}",
                        buy_strategy="both",
                        w_pb_trend=ws[0], w_pb_level=ws[1], w_pb_rsi=ws[2],
                        w_pb_stoch=ws[3], w_pb_volume=ws[4],
                        w_bo_range=ws[0], w_bo_signal=ws[1], w_bo_volume=ws[2],
                        w_bo_momentum=ws[3], w_bo_trend=ws[4],
                        buy_threshold=threshold,
                        w_sell_breakdown=default_sell[0], w_sell_cross=default_sell[1],
                        w_sell_rsi_break=default_sell[2], w_sell_overbought=default_sell[3],
                        w_sell_keltner_upper=default_sell[4], w_sell_profit=default_sell[5],
                        sell_threshold=_default_sell_threshold(),
                        stop_loss_pct=_default_stop(),
                    ))
    return configs


def candidate_configs_stage2(base_cfg: UptrendDipConfig) -> list[UptrendDipConfig]:
    """Stage 2: for a given buy config, search sell configs."""
    configs = []
    for sell_ws in SELL_WEIGHT_SETS:
        for sell_threshold in [15, 20, 25, 30, 35, 40, 45]:
            for stop_loss in [3.0, 5.0, 7.0, 10.0, 15.0]:
                cfg = UptrendDipConfig(
                    name=f"{base_cfg.name}_s{sell_threshold}_sl{stop_loss:.0f}",
                    buy_strategy=base_cfg.buy_strategy,
                    w_pb_trend=base_cfg.w_pb_trend, w_pb_level=base_cfg.w_pb_level,
                    w_pb_rsi=base_cfg.w_pb_rsi, w_pb_stoch=base_cfg.w_pb_stoch,
                    w_pb_volume=base_cfg.w_pb_volume,
                    w_bo_range=base_cfg.w_bo_range, w_bo_signal=base_cfg.w_bo_signal,
                    w_bo_volume=base_cfg.w_bo_volume, w_bo_momentum=base_cfg.w_bo_momentum,
                    w_bo_trend=base_cfg.w_bo_trend,
                    buy_threshold=base_cfg.buy_threshold,
                    w_sell_breakdown=sell_ws[0], w_sell_cross=sell_ws[1],
                    w_sell_rsi_break=sell_ws[2], w_sell_overbought=sell_ws[3],
                    w_sell_keltner_upper=sell_ws[4], w_sell_profit=sell_ws[5],
                    sell_threshold=sell_threshold,
                    stop_loss_pct=stop_loss,
                )
                configs.append(cfg)
    return configs


# ═══════════════════════════════════════════════════════
# Indicator computation
# ═══════════════════════════════════════════════════════


def build_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    close = out["close"]
    high = out["high"]
    low = out["low"]

    # RSI + Stochastic
    out["rsi14"] = rsi(close, 14)
    out["stoch14"] = stochastic(close, high, low, 14)

    # ATR
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    out["atr14"] = tr.rolling(14).mean()
    out["atr20"] = tr.rolling(20).mean()

    # EMA stack
    out["ema20"] = close.ewm(span=20, adjust=False).mean()
    out["ema21"] = close.ewm(span=21, adjust=False).mean()
    out["ema55"] = close.ewm(span=55, adjust=False).mean()
    out["ema100"] = close.ewm(span=100, adjust=False).mean()
    out["sma200"] = close.rolling(200).mean()

    # Keltner channel
    out["keltner_upper"] = out["ema20"] + 2 * out["atr20"]
    out["keltner_lower"] = out["ema20"] - 2 * out["atr20"]

    # Volume ratio
    vol_avg20 = out["volume"].rolling(20).mean()
    out["vol_ratio"] = out["volume"] / vol_avg20.replace(0, np.nan)

    # Trend alignment: count bullish EMA pairs
    out["trend_pairs"] = (
        (out["ema21"] > out["ema55"]).astype(float)
        + (out["ema55"] > out["ema100"]).astype(float)
        + (out["ema100"] > out["sma200"]).astype(float)
    ) / 3.0

    # Pullback level: distance from EMA21 in ATR units (positive = below EMA)
    out["pullback_atr"] = (out["ema21"] - close) / out["atr14"]

    # RSI sweet spot: bell curve around 40 (peak=100 at 40, 0 at 25 and 55)
    out["rsi_sweet"] = clamp(100 - (out["rsi14"] - 40).abs() * (100 / 15), 0, 100)

    # RSI direction (3-bar change)
    out["rsi_delta"] = out["rsi14"] - out["rsi14"].shift(3)

    # Range compression: 10-bar range relative to ATR
    range_10 = high.rolling(10).max() - low.rolling(10).min()
    range_pct = range_10 / close * 100
    atr_pct = out["atr14"] / close * 100
    out["atr_compression"] = clamp((3.0 - range_pct / atr_pct.replace(0, np.nan)) * 33, 0, 100)

    # N-bar high breakout distance in ATR units
    high_20 = high.rolling(20).max()
    out["breakout_dist"] = (close - high_20) / out["atr14"]

    # Keltner upper distance in ATR units
    out["keltner_upper_dist"] = (close - out["keltner_upper"]) / out["atr14"]

    # Death cross detection
    out["ema_cross_down"] = (
        (out["ema21"] < out["ema55"]) & (out["ema21"].shift(1) >= out["ema55"].shift(1))
    )

    return out.dropna(subset=["sma200", "rsi14", "atr14"])


# ═══════════════════════════════════════════════════════
# Buy scoring
# ═══════════════════════════════════════════════════════


def score_buy_pullback(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    trend_score = df["trend_pairs"] * 100
    pullback_score = clamp(df["pullback_atr"].clip(lower=0) * 50, 0, 100)
    rsi_score = df["rsi_sweet"]
    stoch_score = clamp((40 - df["stoch14"]) * 2.5, 0, 100)
    volume_score = clamp((1.0 - df["vol_ratio"]) * 100, 0, 100)

    raw = (
        cfg.w_pb_trend * trend_score
        + cfg.w_pb_level * pullback_score
        + cfg.w_pb_rsi * rsi_score
        + cfg.w_pb_stoch * stoch_score
        + cfg.w_pb_volume * volume_score
    )
    return clamp(raw)


def score_buy_breakout(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    range_score = df["atr_compression"]
    breakout_score = clamp(df["breakout_dist"].clip(lower=0) * 50, 0, 100)
    vol_surge_score = clamp((df["vol_ratio"] - 1.0) * 100, 0, 100)

    rsi_momentum = clamp(df["rsi14"] - 40, 0, 60) * (100 / 60)
    rsi_dir_bonus = clamp(df["rsi_delta"] * 5, 0, 30)
    momentum_score = clamp(rsi_momentum + rsi_dir_bonus)

    above_sma200 = (df["close"] > df["sma200"]).astype(float) * 50
    trend_score = clamp(above_sma200 + df["trend_pairs"] * 50)

    raw = (
        cfg.w_bo_range * range_score
        + cfg.w_bo_signal * breakout_score
        + cfg.w_bo_volume * vol_surge_score
        + cfg.w_bo_momentum * momentum_score
        + cfg.w_bo_trend * trend_score
    )
    return clamp(raw)


# ═══════════════════════════════════════════════════════
# Sell scoring
# ═══════════════════════════════════════════════════════


def score_sell_reversal(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    # Price below EMA21 (first warning) — more sensitive than EMA55
    below_ema21 = clamp((df["ema21"] - df["close"]) / df["atr14"] * 30, 0, 100)
    below_ema55 = clamp((df["ema55"] - df["close"]) / df["atr14"] * 40, 0, 100)
    breakdown_score = np.maximum(below_ema21, below_ema55)

    # EMA21 crossing below EMA55 OR EMA20 below EMA55
    cross_down_21_55 = (
        (df["ema21"] < df["ema55"]) & (df["ema21"].shift(1) >= df["ema55"].shift(1))
    )
    cross_down_20_55 = (
        (df["ema20"] < df["ema55"]) & (df["ema20"].shift(1) >= df["ema55"].shift(1))
    )
    cross_score = (cross_down_21_55 | cross_down_20_55).astype(float) * 100

    # RSI dropping: RSI was above 50 recently, now below 45
    rsi_below_45 = (df["rsi14"] < 45).astype(float)
    rsi_was_above_50 = (df["rsi14"].shift(3) > 50).astype(float)
    rsi_break_raw = clamp((45 - df["rsi14"]) * 2, 0, 100)
    rsi_break_score = rsi_below_45 * rsi_was_above_50 * rsi_break_raw

    # Price making lower lows (3-bar)
    lower_low = (df["close"] < df["close"].shift(1)) & (df["close"].shift(1) < df["close"].shift(2))
    momentum_break = lower_low.astype(float) * clamp((50 - df["rsi14"]) * 2, 0, 50)

    raw = (
        cfg.w_sell_breakdown * breakdown_score
        + cfg.w_sell_cross * cross_score
        + cfg.w_sell_rsi_break * rsi_break_score
        + 0.15 * momentum_break  # fixed bonus for momentum breakdown
    )
    return clamp(raw)


def score_sell_overbought(df: pd.DataFrame, entry_prices: pd.Series) -> pd.Series:
    """Overbought exit score (does not need config weights applied yet)."""
    rsi_overbought = clamp((df["rsi14"] - 45) * 2.0, 0, 100)
    stoch_overbought = clamp((df["stoch14"] - 45) * 2.0, 0, 100)
    overbought_score = (rsi_overbought + stoch_overbought) / 2

    keltner_upper_score = clamp(df["keltner_upper_dist"].clip(lower=0) * 50, 0, 100)

    # Profit score: only when in position
    valid_entry = entry_prices.notna()
    profit_score = pd.Series(0.0, index=df.index)
    if valid_entry.any():
        unrealized = (df["close"] / entry_prices - 1) * 100
        profit_score = clamp(unrealized.clip(lower=0) * (100 / 10), 0, 100)
        profit_score = profit_score.where(valid_entry, 0.0)

    return overbought_score, keltner_upper_score, profit_score


# ═══════════════════════════════════════════════════════
# Trade simulation
# ═══════════════════════════════════════════════════════


def simulate_trades(
    df: pd.DataFrame, cfg: UptrendDipConfig,
    sell_reversal: pd.Series, sell_ob_components: tuple,
) -> list[dict[str, Any]]:
    close = df["close"].values
    buy_arr = df["buy_score"].values
    sell_rev_arr = sell_reversal.values
    n = len(close)

    ob_arr = sell_ob_components[0].values
    kelt_arr = sell_ob_components[1].values

    trades: list[dict[str, Any]] = []
    in_position = False
    entry_price = 0.0
    entry_idx = 0

    for i in range(1, n):
        if not in_position:
            if not np.isnan(buy_arr[i]) and buy_arr[i] >= cfg.buy_threshold:
                in_position = True
                entry_price = close[i]
                entry_idx = i
        else:
            current_return = (close[i] / entry_price - 1) * 100
            stop_hit = current_return <= -cfg.stop_loss_pct

            sell_rev = sell_rev_arr[i] if not np.isnan(sell_rev_arr[i]) else 0
            ob = ob_arr[i] if not np.isnan(ob_arr[i]) else 0
            kelt = kelt_arr[i] if not np.isnan(kelt_arr[i]) else 0
            profit = max(0, min(100, max(0, current_return) * (100 / 15)))

            sell_ob = float(clamp(
                cfg.w_sell_overbought * ob
                + cfg.w_sell_keltner_upper * kelt
                + cfg.w_sell_profit * profit
            ))
            sell_score = max(sell_rev, sell_ob)
            sell_signal = sell_score >= cfg.sell_threshold

            if stop_hit or sell_signal:
                exit_reason = "stop_loss" if stop_hit else "sell_signal"
                trades.append({
                    "entry_date": str(df.index[entry_idx].date()),
                    "entry_price": round(entry_price, 4),
                    "exit_date": str(df.index[i].date()),
                    "exit_price": round(close[i], 4),
                    "return_pct": round(current_return, 2),
                    "holding_days": i - entry_idx,
                    "exit_reason": exit_reason,
                })
                in_position = False

    if in_position:
        current_return = (close[-1] / entry_price - 1) * 100
        trades.append({
            "entry_date": str(df.index[entry_idx].date()),
            "entry_price": round(entry_price, 4),
            "exit_date": str(df.index[-1].date()),
            "exit_price": round(close[-1], 4),
            "return_pct": round(current_return, 2),
            "holding_days": n - 1 - entry_idx,
            "exit_reason": "open",
        })

    return trades


# ═══════════════════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════════════════


def max_drawdown_during_hold(trades: list[dict], df: pd.DataFrame) -> float:
    worst = 0.0
    for t in trades:
        try:
            s = df.index.get_loc(pd.Timestamp(t["entry_date"]))
            e = df.index.get_loc(pd.Timestamp(t["exit_date"]))
        except KeyError:
            continue
        prices = df["close"].iloc[s:e + 1].values
        peak = prices[0]
        for p in prices:
            peak = max(peak, p)
            dd = (p / peak - 1) * 100
            worst = min(worst, dd)
    return round(worst, 2)


def compute_sharpe(trades: list[dict], df: pd.DataFrame, risk_free: float = 0.04) -> float:
    daily_returns: list[float] = []
    for t in trades:
        try:
            s = df.index.get_loc(pd.Timestamp(t["entry_date"]))
            e = df.index.get_loc(pd.Timestamp(t["exit_date"]))
        except KeyError:
            continue
        prices = df["close"].iloc[s:e + 1].values
        for j in range(1, len(prices)):
            daily_returns.append(prices[j] / prices[j - 1] - 1)
    if not daily_returns:
        return 0.0
    mean_r = float(np.mean(daily_returns))
    std_r = float(np.std(daily_returns))
    if std_r == 0:
        return 0.0
    daily_rf = (1 + risk_free) ** (1 / 252) - 1
    return round((mean_r - daily_rf) / std_r * math.sqrt(252), 2)


def evaluate_stage1(df: pd.DataFrame, cfg: UptrendDipConfig) -> dict[str, Any]:
    """Stage 1: buy-only evaluation using forward returns."""
    if cfg.buy_strategy == "pullback":
        buy_score = score_buy_pullback(df, cfg)
    elif cfg.buy_strategy == "breakout":
        buy_score = score_buy_breakout(df, cfg)
    else:
        buy_score = np.maximum(score_buy_pullback(df, cfg), score_buy_breakout(df, cfg))

    buy_mask = buy_score >= cfg.buy_threshold
    buy_count = int(buy_mask.sum())

    if buy_count == 0:
        return {"score": -999, "buyDays": 0, "config": asdict(cfg)}

    fwd_63 = future_return(df["close"], 63)[buy_mask]
    fwd_126 = future_return(df["close"], 126)[buy_mask]
    fwd_252 = future_return(df["close"], 252)[buy_mask]

    win_rate = float((fwd_63 > 0).mean() * 100) if len(fwd_63) > 0 else 0
    avg_63 = float(fwd_63.mean()) if fwd_63.notna().any() else 0
    avg_126 = float(fwd_126.mean()) if fwd_126.notna().any() else 0
    avg_252 = float(fwd_252.mean()) if fwd_252.notna().any() else 0

    signal_penalty = max(0, (5 - buy_count)) * 10
    overtrade_penalty = max(0, (buy_count - 100)) * 0.3

    score = (
        avg_63 * 1.5
        + avg_126 * 0.8
        + avg_252 * 0.3
        + win_rate * 0.3
        - signal_penalty
        - overtrade_penalty
    )

    return {
        "score": round(float(score), 2) if math.isfinite(score) else -999,
        "buyDays": buy_count,
        "config": asdict(cfg),
        "forwardReturns": {
            "avg3mPct": round(avg_63, 2),
            "avg6mPct": round(avg_126, 2),
            "avg12mPct": round(avg_252, 2),
            "winRate3mPct": round(win_rate, 1),
        },
    }


def evaluate_stage2(
    df: pd.DataFrame, cfg: UptrendDipConfig,
) -> dict[str, Any]:
    """Stage 2: full trade simulation evaluation."""
    # Score buy signals
    if cfg.buy_strategy == "pullback":
        buy_score = score_buy_pullback(df, cfg)
    elif cfg.buy_strategy == "breakout":
        buy_score = score_buy_breakout(df, cfg)
    else:
        buy_score = np.maximum(score_buy_pullback(df, cfg), score_buy_breakout(df, cfg))
    df = df.copy()
    df["buy_score"] = buy_score

    # Score sell reversal (no entry price needed)
    sell_reversal = score_sell_reversal(df, cfg)

    # Precompute overbought components (profit computed during sim)
    entry_placeholder = pd.Series(np.nan, index=df.index)
    sell_ob_components = score_sell_overbought(df, entry_placeholder)

    # Simulate
    trades = simulate_trades(df, cfg, sell_reversal, sell_ob_components)

    if not trades:
        return {"score": -999, "tradeCount": 0, "config": asdict(cfg)}

    returns = [t["return_pct"] for t in trades]
    win_trades = [r for r in returns if r > 0]
    loss_trades = [r for r in returns if r <= 0]

    win_rate = len(win_trades) / len(trades) * 100
    avg_return = float(np.mean(returns))
    total_return = sum(returns)
    avg_win = float(np.mean(win_trades)) if win_trades else 0
    avg_loss = float(np.mean(loss_trades)) if loss_trades else 0
    profit_factor = abs(sum(win_trades) / sum(loss_trades)) if loss_trades and sum(loss_trades) != 0 else (
        10.0 if win_trades else 0.0
    )
    max_dd = max_drawdown_during_hold(trades, df)
    sharpe = compute_sharpe(trades, df)
    avg_hold = float(np.mean([t["holding_days"] for t in trades]))
    buy_hold = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100

    # Count stop-loss vs signal exits
    stop_exits = sum(1 for t in trades if t["exit_reason"] == "stop_loss")
    signal_exits = sum(1 for t in trades if t["exit_reason"] == "sell_signal")

    n_trades = len(trades)
    # Strong penalty for too few trades
    if n_trades < 5:
        trade_penalty = (5 - n_trades) * 30
    elif n_trades > 50:
        trade_penalty = (n_trades - 50) * 1.0
    else:
        trade_penalty = 0
    # Penalize noise trades (tiny returns)
    meaningful = [r for r in returns if abs(r) >= 3]
    noise_ratio = 1 - len(meaningful) / n_trades if n_trades > 0 else 0
    noise_penalty = noise_ratio * 30

    score = (
        total_return * 0.05
        + win_rate * 0.3
        + min(profit_factor, 5) * 5
        + sharpe * 10
        - trade_penalty
        - noise_penalty
    )

    return {
        "score": round(float(score), 2) if math.isfinite(score) else -999,
        "tradeCount": len(trades),
        "config": asdict(cfg),
        "metrics": {
            "winRate": round(win_rate, 1),
            "avgReturn": round(avg_return, 2),
            "totalReturn": round(total_return, 2),
            "avgWin": round(avg_win, 2),
            "avgLoss": round(avg_loss, 2),
            "profitFactor": round(min(profit_factor, 10), 2),
            "maxDrawdown": max_dd,
            "sharpe": sharpe,
            "avgHoldingDays": round(avg_hold, 1),
            "buyHoldReturn": round(buy_hold, 2),
            "stopExits": stop_exits,
            "signalExits": signal_exits,
        },
        "trades": trades,
    }


# ═══════════════════════════════════════════════════════
# Multi-symbol ranking
# ═══════════════════════════════════════════════════════


def combined_rank(
    configs: list[UptrendDipConfig],
    metrics_by_symbol: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    ranked = []
    for index, cfg in enumerate(configs):
        by_symbol = {s: m[index] for s, m in metrics_by_symbol.items()}
        scores = [p["score"] for p in by_symbol.values() if p["score"] > -900]
        if not scores:
            continue
        stability_penalty = (max(scores) - min(scores)) * 0.15
        combined = float(np.mean(scores) - stability_penalty)
        ranked.append({
            "config": asdict(cfg),
            "combinedScore": round(combined, 2),
            "symbols": by_symbol,
        })
    ranked.sort(key=lambda x: x["combinedScore"], reverse=True)
    return ranked


# ═══════════════════════════════════════════════════════
# Pine Script generation
# ═══════════════════════════════════════════════════════


def generate_pine_script(cfg: UptrendDipConfig) -> str:
    return f'''//@version=5
indicator("Uptrend Dip Buy+Sell v1", overlay=true, max_labels_count=500)

// ═══════════════════════════════════════════════════════
// Inputs
// ═══════════════════════════════════════════════════════
buy_strategy  = input.string("{cfg.buy_strategy}", "Buy Strategy", options=["pullback","breakout","both"])
buy_threshold = input.float({cfg.buy_threshold:.0f}, "Buy Threshold", minval=10, maxval=90, step=5)
sell_threshold = input.float({cfg.sell_threshold:.0f}, "Sell Threshold", minval=10, maxval=90, step=5)
stop_loss_pct = input.float({cfg.stop_loss_pct:.0f}, "Stop Loss %", minval=1, maxval=20, step=1)

// Pullback weights
w_pb_trend  = input.float({cfg.w_pb_trend:.2f}, "PB Trend",      minval=0, maxval=1, step=0.05)
w_pb_level  = input.float({cfg.w_pb_level:.2f}, "PB Level",      minval=0, maxval=1, step=0.05)
w_pb_rsi    = input.float({cfg.w_pb_rsi:.2f}, "PB RSI",        minval=0, maxval=1, step=0.05)
w_pb_stoch  = input.float({cfg.w_pb_stoch:.2f}, "PB Stoch",      minval=0, maxval=1, step=0.05)
w_pb_volume = input.float({cfg.w_pb_volume:.2f}, "PB Volume",     minval=0, maxval=1, step=0.05)

// Breakout weights
w_bo_range    = input.float({cfg.w_bo_range:.2f}, "BO Range",      minval=0, maxval=1, step=0.05)
w_bo_signal   = input.float({cfg.w_bo_signal:.2f}, "BO Signal",     minval=0, maxval=1, step=0.05)
w_bo_volume   = input.float({cfg.w_bo_volume:.2f}, "BO Volume",     minval=0, maxval=1, step=0.05)
w_bo_momentum = input.float({cfg.w_bo_momentum:.2f}, "BO Momentum",   minval=0, maxval=1, step=0.05)
w_bo_trend    = input.float({cfg.w_bo_trend:.2f}, "BO Trend",      minval=0, maxval=1, step=0.05)

// Sell weights
w_sell_breakdown = input.float({cfg.w_sell_breakdown:.2f}, "Sell Breakdown",    minval=0, maxval=1, step=0.05)
w_sell_cross     = input.float({cfg.w_sell_cross:.2f}, "Sell Cross",        minval=0, maxval=1, step=0.05)
w_sell_rsi_break = input.float({cfg.w_sell_rsi_break:.2f}, "Sell RSI Break",    minval=0, maxval=1, step=0.05)
w_sell_overbought = input.float({cfg.w_sell_overbought:.2f}, "Sell Overbought",   minval=0, maxval=1, step=0.05)
w_sell_kupper    = input.float({cfg.w_sell_keltner_upper:.2f}, "Sell Keltner Upper", minval=0, maxval=1, step=0.05)
w_sell_profit    = input.float({cfg.w_sell_profit:.2f}, "Sell Profit",      minval=0, maxval=1, step=0.05)

// ═══════════════════════════════════════════════════════
// Indicators
// ═══════════════════════════════════════════════════════
atr14 = ta.atr(14)
atr20 = ta.atr(20)

ema20  = ta.ema(close, 20)
ema21  = ta.ema(close, 21)
ema55  = ta.ema(close, 55)
ema100 = ta.ema(close, 100)
sma200 = ta.sma(close, 200)

keltner_upper = ema20 + 2 * atr20

rsi_val   = ta.rsi(close, 14)
stoch_val = ta.stoch(close, high, low, 14)
vol_ratio = volume / ta.sma(volume, 20)

trend_pairs = ((ema21 > ema55 ? 1.0 : 0.0) + (ema55 > ema100 ? 1.0 : 0.0) + (ema100 > sma200 ? 1.0 : 0.0)) / 3.0
pullback_atr = (ema21 - close) / atr14
rsi_sweet = math.max(0, math.min(100, 100 - math.abs(rsi_val - 40) * (100 / 15)))
rsi_delta = rsi_val - ta.rsi(close, 14)[3]

range_10 = ta.highest(high, 10) - ta.lowest(low, 10)
range_pct = range_10 / close * 100
atr_pct = atr14 / close * 100
atr_compression = math.max(0, math.min(100, (3.0 - range_pct / atr_pct) * 33))

high_20 = ta.highest(high, 20)
breakout_dist = (close - high_20) / atr14
keltner_upper_dist = (close - keltner_upper) / atr14

ema_cross_down = ema21 < ema55 and ema21[1] >= ema55[1]

// ═══════════════════════════════════════════════════════
// Buy Scoring
// ═══════════════════════════════════════════════════════
// Pullback
pb_trend  = trend_pairs * 100
pb_level  = math.max(0, math.min(100, math.max(0, pullback_atr) * 50))
pb_rsi    = rsi_sweet
pb_stoch  = math.max(0, math.min(100, (40 - stoch_val) * 2.5))
pb_volume = math.max(0, math.min(100, (1.0 - vol_ratio) * 100))
buy_pullback = math.max(0, math.min(100,
     w_pb_trend * pb_trend + w_pb_level * pb_level + w_pb_rsi * pb_rsi
   + w_pb_stoch * pb_stoch + w_pb_volume * pb_volume))

// Breakout
bo_range    = atr_compression
bo_signal   = math.max(0, math.min(100, math.max(0, breakout_dist) * 50))
bo_volume   = math.max(0, math.min(100, (vol_ratio - 1.0) * 100))
bo_momentum = math.max(0, math.min(100, math.max(0, math.min(60, rsi_val - 40)) * (100/60) + math.max(0, math.min(30, rsi_delta * 5))))
bo_trend    = math.max(0, math.min(100, (close > sma200 ? 50.0 : 0.0) + trend_pairs * 50))
buy_breakout = math.max(0, math.min(100,
     w_bo_range * bo_range + w_bo_signal * bo_signal + w_bo_volume * bo_volume
   + w_bo_momentum * bo_momentum + w_bo_trend * bo_trend))

buy_score = buy_strategy == "pullback" ? buy_pullback : buy_strategy == "breakout" ? buy_breakout : math.max(buy_pullback, buy_breakout)

// ═══════════════════════════════════════════════════════
// Sell Scoring
// ═══════════════════════════════════════════════════════
sell_breakdown = math.max(
     math.max(0, math.min(100, (ema55 - close) / atr14 * 40)),
     math.max(0, math.min(100, (sma200 - close) / atr14 * 30)))
sell_cross = ema_cross_down ? 100.0 : 0.0
sell_rsi_break = (rsi_val < 40 and ta.rsi(close, 14)[5] > 50) ? math.max(0, math.min(100, (40 - rsi_val) * 2.5)) : 0.0
sell_reversal = math.max(0, math.min(100,
     w_sell_breakdown * sell_breakdown + w_sell_cross * sell_cross + w_sell_rsi_break * sell_rsi_break))

// Overbought (simplified — no entry price in Pine)
sell_overbought_rsi = math.max(0, math.min(100, (rsi_val - 45) * 2.0))
sell_overbought_stoch = math.max(0, math.min(100, (stoch_val - 45) * 2.0))
sell_ob = (sell_overbought_rsi + sell_overbought_stoch) / 2
sell_kupper = math.max(0, math.min(100, math.max(0, keltner_upper_dist) * 50))
sell_overbought = math.max(0, math.min(100, w_sell_overbought * sell_ob + w_sell_kupper * sell_kupper))

sell_score = math.max(sell_reversal, sell_overbought)

// ═══════════════════════════════════════════════════════
// Signals & Plotting
// ═══════════════════════════════════════════════════════
buy_signal  = buy_score >= buy_threshold and not na(sma200)
sell_signal = sell_score >= sell_threshold

bgcolor(buy_signal ? color.new(color.green, 80) : na, title="Buy Zone")
bgcolor(sell_signal ? color.new(color.red, 80) : na, title="Sell Zone")

plotshape(buy_signal, title="BUY", style=shape.labelup, location=location.belowbar,
     color=color.green, text="BUY", textcolor=color.white, size=size.small)
plotshape(sell_signal, title="SELL", style=shape.labeldown, location=location.abovebar,
     color=color.red, text="SELL", textcolor=color.white, size=size.small)

// Debug plots (hidden)
plot(buy_score, "Buy Score", color=color.green, display=display.none)
plot(sell_score, "Sell Score", color=color.red, display=display.none)
hline(buy_threshold, "Buy Threshold", color=color.green, linestyle=hline.style_dashed)
hline(sell_threshold, "Sell Threshold", color=color.red, linestyle=hline.style_dashed)
'''


# ═══════════════════════════════════════════════════════
# Report
# ═══════════════════════════════════════════════════════


def write_report(results: dict[str, Any]) -> None:
    lines = [
        "# Uptrend Dip Buy + Sell Signal Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Method",
        "",
        "Two buy strategies (trend pullback / breakout), two sell strategies (reversal / overbought).",
        "Grid-searched weights, thresholds, and stop-loss. Discrete buy-sell cycle simulation.",
        "",
        "Buy A (Pullback): EMA stack trend + RSI sweet spot + Stochastic + volume contraction",
        "Buy B (Breakout): Range compression + N-bar high breakout + volume surge + momentum",
        "Sell A (Reversal): EMA breakdown + death cross + RSI break",
        "Sell B (Overbought): RSI/Stoch overbought + Keltner upper + profit target",
        "",
    ]

    # Stage 1 results
    s1 = results.get("stage1", {})
    if s1:
        lines.extend(["## Stage 1: Buy Config Search", ""])
        for symbol, payload in s1.get("symbols", {}).items():
            best = payload.get("best", {})
            cfg = best.get("config", {})
            fwd = best.get("forwardReturns", {})
            lines.extend([
                f"### {symbol}",
                f"- Best buy: `{cfg.get('name', '?')}` strategy={cfg.get('buy_strategy', '?')}",
                f"- Buy days: {best.get('buyDays', 0)}, 3m: {fwd.get('avg3mPct', 0):.1f}%, "
                f"win: {fwd.get('winRate3mPct', 0):.0f}%",
                "",
            ])

    # Stage 2 results
    s2 = results.get("stage2", {})
    if s2:
        recommended = s2.get("recommendedDefault", {})
        cfg = recommended.get("config", {})
        lines.extend([
            "## Stage 2: Recommended Buy+Sell Config",
            "",
            f"- Config: `{cfg.get('name', '?')}`",
            f"- Strategy: {cfg.get('buy_strategy', '?')}",
            f"- Combined score: {recommended.get('combinedScore', 0):.2f}",
            f"- Buy threshold: {cfg.get('buy_threshold', 0):.0f}",
            f"- Sell threshold: {cfg.get('sell_threshold', 0):.0f}",
            f"- Stop loss: {cfg.get('stop_loss_pct', 0):.0f}%",
            "",
            "Per-symbol results:",
            "",
        ])

        for symbol, metrics in recommended.get("symbols", {}).items():
            m = metrics.get("metrics", {})
            tc = metrics.get("tradeCount", 0)
            if tc == 0:
                lines.extend([f"### {symbol}", "- No trades", ""])
                continue
            lines.extend([
                f"### {symbol}",
                f"- Trades: {tc}",
                f"- Win rate: {m.get('winRate', 0):.1f}%",
                f"- Avg return: {m.get('avgReturn', 0):.2f}%",
                f"- Total return: {m.get('totalReturn', 0):.1f}%",
                f"- Profit factor: {m.get('profitFactor', 0):.2f}",
                f"- Sharpe: {m.get('sharpe', 0):.2f}",
                f"- Max drawdown: {m.get('maxDrawdown', 0):.1f}%",
                f"- Avg hold: {m.get('avgHoldingDays', 0):.0f} days",
                f"- Buy & Hold: {m.get('buyHoldReturn', 0):.1f}%",
                f"- Exits: {m.get('stopExits', 0)} stop / {m.get('signalExits', 0)} signal",
                "",
            ])

        # Trade log for QQQ or first symbol
        for symbol in ["QQQ", "SPY"]:
            sym_data = recommended.get("symbols", {}).get(symbol, {})
            trades = sym_data.get("trades", [])
            if trades:
                lines.extend([f"## Trade Log: {symbol}", ""])
                lines.extend([
                    "| Entry | Exit | Return | Days | Exit |",
                    "|-------|------|--------|------|------|",
                ])
                for t in trades[:30]:  # limit to 30
                    lines.append(
                        f"| {t['entry_date']} | {t['exit_date']} | "
                        f"{t['return_pct']:+.1f}% | {t['holding_days']} | {t['exit_reason']} |"
                    )
                lines.append("")
                break

    # Per-symbol best
    per_sym = results.get("perSymbolBest", {})
    if per_sym:
        lines.extend(["## Per-Symbol Optimal Configs", ""])
        lines.extend([
            "| Symbol | Strategy | Config | Trades | Win% | Avg Ret | Sharpe | PF |",
            "|--------|----------|--------|--------|------|---------|--------|----|",
        ])
        for symbol, best in per_sym.items():
            if "error" in best:
                lines.append(f"| {symbol} | {best['error']} | - | - | - | - | - | - |")
                continue
            cfg_d = best.get("config", {})
            m = best.get("metrics", {})
            lines.append(
                f"| {symbol} | {cfg_d.get('buy_strategy', '?')} | "
                f"`{cfg_d.get('name', '?')[:30]}` | "
                f"{best.get('tradeCount', 0)} | {m.get('winRate', 0):.0f}% | "
                f"{m.get('avgReturn', 0):.1f}% | {m.get('sharpe', 0):.2f} | "
                f"{m.get('profitFactor', 0):.1f} |"
            )
        lines.append("")

    lines.extend([
        "## TradingView Pine Script",
        "",
        "See `uptrend_dip_pine.pine` — ready to paste into TradingView Pine Editor.",
        "",
    ])

    text = "\n".join(lines)
    (OUT_DIR / "uptrend_dip_report.md").write_text(text, encoding="utf-8", newline="\n")


# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════


def run(search_symbols: list[str], validate_symbols: list[str], refresh: bool) -> dict[str, Any]:
    output: dict[str, Any] = {
        "generatedAt": datetime.now().isoformat(),
        "searchSymbols": search_symbols,
        "validateSymbols": validate_symbols,
    }

    # ── Stage 1: Buy config search ──
    stage1_configs = candidate_configs_stage1()
    output["stage1"] = {"configCount": len(stage1_configs)}

    s1_metrics: dict[str, list[dict[str, Any]]] = {}
    s1_metas: dict[str, dict[str, Any]] = {}

    for symbol in search_symbols:
        df, source = fetch_price(symbol, refresh)
        df = build_indicators(df)
        s1_metas[symbol] = {
            "priceSource": source,
            "priceRows": len(df),
            "priceStart": df.index.min().date().isoformat(),
            "priceEnd": df.index.max().date().isoformat(),
        }

        ranked = []
        for cfg in stage1_configs:
            metrics = evaluate_stage1(df, cfg)
            ranked.append(metrics)
        s1_metrics[symbol] = ranked

        ranked_sorted = sorted(ranked, key=lambda x: x["score"], reverse=True)
        output["stage1"].setdefault("symbols", {})[symbol] = {
            "dataMeta": s1_metas[symbol],
            "best": ranked_sorted[0],
            "top5": ranked_sorted[:5],
        }

    s1_combined = combined_rank(stage1_configs, s1_metrics)
    output["stage1"]["combinedTop5"] = s1_combined[:5]

    # ── Stage 2: Sell config search for top-3 buy configs ──
    top3_buy_configs = []
    for entry in s1_combined[:3]:
        cfg_dict = entry["config"]
        top3_buy_configs.append(UptrendDipConfig(**{
            k: cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
        }))

    all_stage2_configs: list[UptrendDipConfig] = []
    for base in top3_buy_configs:
        all_stage2_configs.extend(candidate_configs_stage2(base))

    output["stage2"] = {"configCount": len(all_stage2_configs)}

    s2_metrics: dict[str, list[dict[str, Any]]] = {}

    for symbol in search_symbols:
        df, _ = fetch_price(symbol, refresh)
        df = build_indicators(df)

        ranked = []
        for cfg in all_stage2_configs:
            metrics = evaluate_stage2(df, cfg)
            ranked.append(metrics)
        s2_metrics[symbol] = ranked

        ranked_sorted = sorted(ranked, key=lambda x: x["score"], reverse=True)
        output["stage2"].setdefault("symbols", {})[symbol] = {
            "best": ranked_sorted[0],
            "top5": ranked_sorted[:5],
        }

    s2_combined = combined_rank(all_stage2_configs, s2_metrics)
    output["stage2"]["recommendedDefault"] = s2_combined[0]
    output["stage2"]["combinedTop10"] = s2_combined[:10]

    # ── Validate on all symbols ──
    best_cfg_dict = s2_combined[0]["config"]
    best_cfg = UptrendDipConfig(**{
        k: best_cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
    })

    per_symbol_best: dict[str, dict[str, Any]] = {}
    for symbol in validate_symbols:
        if symbol in output["stage2"].get("symbols", {}):
            per_symbol_best[symbol] = output["stage2"]["symbols"][symbol]["best"]
            continue
        try:
            df, _ = fetch_price(symbol, refresh)
            df = build_indicators(df)
        except FileNotFoundError:
            per_symbol_best[symbol] = {"error": "data not found"}
            continue

        # Evaluate with recommended config
        metrics = evaluate_stage2(df, best_cfg)
        per_symbol_best[symbol] = metrics

        # Also try per-symbol best from stage 1
        s1_ranked = []
        for cfg in stage1_configs:
            m = evaluate_stage1(df, cfg)
            s1_ranked.append(m)
        s1_ranked.sort(key=lambda x: x["score"], reverse=True)
        best_buy = s1_ranked[0]["config"]
        best_buy_cfg = UptrendDipConfig(**{
            k: best_buy[k] for k in [f.name for f in fields(UptrendDipConfig)]
        })
        s2_ranked = []
        for sell_cfg in candidate_configs_stage2(best_buy_cfg):
            m = evaluate_stage2(df, sell_cfg)
            s2_ranked.append(m)
        s2_ranked.sort(key=lambda x: x["score"], reverse=True)
        if s2_ranked and s2_ranked[0]["score"] > per_symbol_best[symbol].get("score", -999):
            per_symbol_best[symbol] = s2_ranked[0]

    output["perSymbolBest"] = per_symbol_best

    # ── Generate Pine Script ──
    pine = generate_pine_script(best_cfg)
    (OUT_DIR / "uptrend_dip_pine.pine").write_text(pine, encoding="utf-8", newline="\n")
    output["pineScript"] = str(OUT_DIR / "uptrend_dip_pine.pine")

    output = json_safe(output)
    (OUT_DIR / "uptrend_dip_results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    write_report(output)

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Uptrend dip buy+sell grid search")
    parser.add_argument(
        "--symbol", choices=["QQQ", "SPY", "all"], default="all",
        help="Symbols to search (default: all = QQQ+SPY search, all 21 validation)",
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

    rec = result["stage2"]["recommendedDefault"]
    cfg = rec["config"]
    print(f"\nRecommended: {cfg['name']}")
    print(f"Strategy: {cfg['buy_strategy']}, combined={rec['combinedScore']:.2f}")
    print(f"Buy thr={cfg['buy_threshold']:.0f}, Sell thr={cfg['sell_threshold']:.0f}, SL={cfg['stop_loss_pct']:.0f}%")

    for symbol, metrics in rec["symbols"].items():
        m = metrics.get("metrics", {})
        tc = metrics.get("tradeCount", 0)
        if tc > 0:
            print(f"  {symbol}: trades={tc} win={m.get('winRate', 0):.0f}% "
                  f"avg={m.get('avgReturn', 0):.1f}% sharpe={m.get('sharpe', 0):.2f} "
                  f"b&h={m.get('buyHoldReturn', 0):.1f}%")
        else:
            print(f"  {symbol}: no trades")


if __name__ == "__main__":
    main()
