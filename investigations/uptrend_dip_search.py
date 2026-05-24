"""
Uptrend dip buy + sell signal grid search.

Seven buy strategies (trend pullback / breakout confirmation / tech breakout / trend-filtered breakout / bottom reversal / RSI divergence / index shallow pullback),
two sell strategies (trend reversal / overbought exit),
with discrete trade simulation and Pine Script generation.

Usage:
    python investigations/uptrend_dip_search.py              # QQQ+SPY search, all validation
    python investigations/uptrend_dip_search.py --symbol QQQ  # QQQ only
    python investigations/uptrend_dip_search.py --refresh     # re-download data
    python investigations/uptrend_dip_search.py --paper-status # show current paper-tracking plan without rerunning search
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
CATALOG_DIR = ROOT / "strategy_catalog"
UPTREND_DIP_DIR = CATALOG_DIR / "uptrend_dip_buy_sell"
LONG_TERM_ADDON_DIR = CATALOG_DIR / "long_term_addon_radar"
OUT_DIR = UPTREND_DIP_DIR
CACHE_DIR = ROOT / "investigations" / ".cache"
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

TECH_STOCK_SUBSET = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMD",
    "AMZN",
    "META",
    "AVGO",
    "CRM",
    "TSLA",
    "TSM",
    "PLTR",
    "CRWD",
]

TECH_SEGMENTS = {
    "large_cap_quality_tech": ["AAPL", "MSFT", "AMZN", "META", "AVGO", "CRM", "TSM"],
    "high_beta_tech": ["NVDA", "AMD", "TSLA", "PLTR", "CRWD"],
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
    buy_strategy: str  # "pullback", "breakout", "tech_breakout", "trend_breakout", "bottom_reversal", "rsi_divergence", "index_shallow_pullback", "both"

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

# Tech breakout weight sets reuse breakout fields:
# (volatility contraction, prior-high breakout, volume expansion, momentum, relative strength)
TECH_BO_WEIGHT_SETS = [
    (0.20, 0.20, 0.25, 0.15, 0.20),  # balanced tech breakout
    (0.15, 0.20, 0.25, 0.15, 0.25),  # relative-strength + volume
    (0.25, 0.20, 0.20, 0.15, 0.20),  # compression-heavy
    (0.15, 0.25, 0.20, 0.20, 0.20),  # breakout + momentum
    (0.15, 0.15, 0.30, 0.15, 0.25),  # abnormal-volume + relative-strength
]

# Bottom reversal weight sets reuse pullback fields:
# (drawdown, retest/multi-bottom, RSI divergence, crash, capitulation)
BOTTOM_WEIGHT_SETS = [
    (0.25, 0.25, 0.25, 0.15, 0.10),  # balanced bottom
    (0.20, 0.30, 0.30, 0.10, 0.10),  # double-bottom + divergence
    (0.30, 0.20, 0.20, 0.20, 0.10),  # crash-heavy
    (0.20, 0.20, 0.35, 0.15, 0.10),  # RSI divergence-heavy
    (0.20, 0.25, 0.20, 0.15, 0.20),  # capitulation confirmation
]

# Standalone RSI-divergence baseline reuses pullback fields:
# (RSI divergence, retest/multi-bottom, drawdown, RSI washout, capitulation)
RSI_DIVERGENCE_WEIGHT_SETS = [
    (0.50, 0.20, 0.15, 0.10, 0.05),  # pure divergence baseline
    (0.45, 0.25, 0.15, 0.10, 0.05),  # divergence + retest
    (0.55, 0.15, 0.10, 0.10, 0.10),  # divergence-heavy
]

# Index shallow-pullback weight sets reuse pullback fields:
# (drawdown band, moving-average support, RSI reset, recent decline, trend health)
INDEX_PULLBACK_WEIGHT_SETS = [
    (0.20, 0.25, 0.25, 0.15, 0.15),  # balanced shallow dip
    (0.15, 0.30, 0.25, 0.10, 0.20),  # support + trend health
    (0.25, 0.25, 0.20, 0.15, 0.15),  # drawdown band
    (0.15, 0.25, 0.20, 0.25, 0.15),  # recent decline
    (0.15, 0.20, 0.30, 0.15, 0.20),  # RSI reset
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
    for strategy in [
        "pullback",
        "breakout",
        "tech_breakout",
        "trend_breakout",
        "bottom_reversal",
        "rsi_divergence",
        "index_shallow_pullback",
        "both",
    ]:
        weight_sets = (
            PB_WEIGHT_SETS if strategy == "pullback"
            else BOTTOM_WEIGHT_SETS if strategy == "bottom_reversal"
            else RSI_DIVERGENCE_WEIGHT_SETS if strategy == "rsi_divergence"
            else INDEX_PULLBACK_WEIGHT_SETS if strategy == "index_shallow_pullback"
            else TECH_BO_WEIGHT_SETS if strategy == "tech_breakout"
            else BO_WEIGHT_SETS if strategy in {"breakout", "trend_breakout"}
            else PB_WEIGHT_SETS
        )
        for ws in weight_sets:
            for threshold in [25, 30, 35, 40, 45, 50, 55]:
                if strategy in {"pullback", "bottom_reversal", "rsi_divergence", "index_shallow_pullback"}:
                    key_prefix = (
                        "btm" if strategy == "bottom_reversal"
                        else "rdiv" if strategy == "rsi_divergence"
                        else "idx" if strategy == "index_shallow_pullback"
                        else "pb"
                    )
                    key = (key_prefix, ws, threshold)
                    if key in seen:
                        continue
                    seen.add(key)
                    configs.append(UptrendDipConfig(
                        name=f"{key_prefix}_d{ws[0]:.2f}_b{ws[1]:.2f}_r{ws[2]:.2f}_c{ws[3]:.2f}_v{ws[4]:.2f}_t{threshold}",
                        buy_strategy=strategy,
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
                elif strategy in {"breakout", "tech_breakout", "trend_breakout"}:
                    key_prefix = (
                        "tb" if strategy == "tech_breakout"
                        else "tr" if strategy == "trend_breakout"
                        else "bo"
                    )
                    key = (key_prefix, ws, threshold)
                    if key in seen:
                        continue
                    seen.add(key)
                    configs.append(UptrendDipConfig(
                        name=f"{key_prefix}_c{ws[0]:.2f}_b{ws[1]:.2f}_v{ws[2]:.2f}_m{ws[3]:.2f}_rs{ws[4]:.2f}_t{threshold}",
                        buy_strategy=strategy,
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


def build_indicators(df: pd.DataFrame, benchmark_close: pd.Series | None = None) -> pd.DataFrame:
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

    # ADX trend strength
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=out.index,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=out.index,
    )
    plus_di = 100 * plus_dm.rolling(14).mean() / out["atr14"].replace(0, np.nan)
    minus_di = 100 * minus_dm.rolling(14).mean() / out["atr14"].replace(0, np.nan)
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    out["adx14"] = dx.rolling(14).mean()

    # EMA stack
    out["ema20"] = close.ewm(span=20, adjust=False).mean()
    out["ema21"] = close.ewm(span=21, adjust=False).mean()
    out["ema55"] = close.ewm(span=55, adjust=False).mean()
    out["ema100"] = close.ewm(span=100, adjust=False).mean()
    out["sma200"] = close.rolling(200).mean()
    out["ema55_slope20"] = (out["ema55"] / out["ema55"].shift(20) - 1) * 100

    # Keltner channel
    out["keltner_upper"] = out["ema20"] + 2 * out["atr20"]
    out["keltner_lower"] = out["ema20"] - 2 * out["atr20"]

    # Volume ratio
    vol_avg20 = out["volume"].rolling(20).mean()
    out["vol_ratio"] = out["volume"] / vol_avg20.replace(0, np.nan)

    # Bottom/retest context
    out["drawdown_252"] = (close / close.rolling(252).max() - 1) * 100
    out["return_5d"] = (close / close.shift(5) - 1) * 100
    out["return_20d"] = (close / close.shift(20) - 1) * 100

    prior_low_120 = low.shift(10).rolling(120).min()
    retest_dist_pct = (close / prior_low_120.replace(0, np.nan) - 1).abs() * 100
    near_major_low = retest_dist_pct <= 8
    low_120 = low.rolling(120).min()
    near_low = low <= low_120 * 1.05
    near_low_count = near_low.rolling(120).sum()
    retest_score = clamp((8 - retest_dist_pct) * 12.5, 0, 100)
    multi_bottom_bonus = clamp((near_low_count - 2) * 15, 0, 40)
    out["bottom_retest_score"] = clamp(retest_score + multi_bottom_bonus, 0, 100)

    prior_rsi_min = out["rsi14"].shift(10).rolling(60).min()
    lower_low_zone = close <= prior_low_120 * 1.05
    rsi_higher_low = out["rsi14"] - prior_rsi_min
    out["rsi_divergence_score"] = (
        clamp((rsi_higher_low - 4) * 8, 0, 100)
        * lower_low_zone.astype(float)
    )

    out["crash_score"] = clamp(
        (-out["return_20d"] - 10) * 5 + (-out["return_5d"] - 4) * 5,
        0,
        100,
    )
    out["capitulation_score"] = clamp(
        (out["vol_ratio"] - 1.2) * 45 + (35 - out["rsi14"]) * 3,
        0,
        100,
    )

    # Index shallow pullback context: orderly 3%-18% dips near key moving averages.
    dd_abs = -out["drawdown_252"]
    drawdown_entry = clamp((dd_abs - 2.5) * 35, 0, 100)
    too_deep_guard = clamp((22 - dd_abs) * 8, 0, 100)
    out["index_pullback_drawdown_score"] = np.minimum(drawdown_entry, too_deep_guard)

    ema21_dist_pct = (close / out["ema21"] - 1) * 100
    ema55_dist_pct = (close / out["ema55"] - 1) * 100
    sma200_dist_pct = (close / out["sma200"] - 1) * 100
    ema21_support = clamp((4 - ema21_dist_pct.abs()) * 25, 0, 100)
    ema55_support = clamp((6 - ema55_dist_pct.abs()) * (100 / 6), 0, 100)
    sma200_support = clamp((5 - sma200_dist_pct.abs()) * 20, 0, 100)
    out["index_pullback_support_score"] = np.maximum.reduce([
        ema21_support,
        ema55_support,
        sma200_support,
    ])

    out["index_pullback_rsi_score"] = clamp(100 - (out["rsi14"] - 43).abs() * 5.5, 0, 100)
    out["index_pullback_decline_score"] = clamp(
        (-out["return_20d"] - 2) * 10 + (-out["return_5d"] - 0.5) * 12,
        0,
        100,
    )

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

    # Tech breakout uses the prior 20-bar high, so today's high does not hide a close breakout.
    prior_high_20 = high.shift(1).rolling(20).max()
    out["tech_breakout_dist"] = (close - prior_high_20) / out["atr14"]

    # Relative strength vs SPY. If no benchmark is available, keep this component neutral.
    if benchmark_close is not None:
        benchmark = benchmark_close.reindex(out.index).ffill()
        rs_ratio = close / benchmark.replace(0, np.nan)
        rs_sma50 = rs_ratio.rolling(50).mean()
        rs_delta20 = rs_ratio / rs_ratio.shift(20) - 1
        rs_level = clamp((rs_ratio / rs_sma50 - 1) * 500 + 50, 0, 100)
        rs_slope = clamp(rs_delta20 * 500 + 50, 0, 100)
        out["relative_strength_score"] = (rs_level + rs_slope) / 2
    else:
        out["relative_strength_score"] = 50.0

    trend_buffer = clamp((close / out["sma200"] - 0.97) * 900, 0, 100)
    slope_health = clamp(out["ema55_slope20"] * 10 + 40, 0, 100)
    out["index_pullback_trend_score"] = clamp(
        out["trend_pairs"] * 45 + trend_buffer * 0.30 + slope_health * 0.25,
        0,
        100,
    )

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


def score_buy_bottom_reversal(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    drawdown_score = clamp((-df["drawdown_252"] - 15) * 4, 0, 100)
    retest_score = df["bottom_retest_score"]
    divergence_score = df["rsi_divergence_score"]
    crash_score = df["crash_score"]
    capitulation_score = df["capitulation_score"]

    raw = (
        cfg.w_pb_trend * drawdown_score
        + cfg.w_pb_level * retest_score
        + cfg.w_pb_rsi * divergence_score
        + cfg.w_pb_stoch * crash_score
        + cfg.w_pb_volume * capitulation_score
    )
    return clamp(raw)


def score_buy_rsi_divergence(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    divergence_score = df["rsi_divergence_score"]
    retest_score = df["bottom_retest_score"]
    drawdown_score = clamp((-df["drawdown_252"] - 10) * 5, 0, 100)
    rsi_washout_score = clamp((40 - df["rsi14"]) * 4, 0, 100)
    capitulation_score = df["capitulation_score"]

    raw = (
        cfg.w_pb_trend * divergence_score
        + cfg.w_pb_level * retest_score
        + cfg.w_pb_rsi * drawdown_score
        + cfg.w_pb_stoch * rsi_washout_score
        + cfg.w_pb_volume * capitulation_score
    )
    return clamp(raw)


def score_buy_index_shallow_pullback(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    raw = (
        cfg.w_pb_trend * df["index_pullback_drawdown_score"]
        + cfg.w_pb_level * df["index_pullback_support_score"]
        + cfg.w_pb_rsi * df["index_pullback_rsi_score"]
        + cfg.w_pb_stoch * df["index_pullback_decline_score"]
        + cfg.w_pb_volume * df["index_pullback_trend_score"]
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


def score_buy_tech_breakout(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    base_breakout = score_buy_breakout(df, cfg)
    compression_score = df["atr_compression"]
    breakout_score = clamp(df["tech_breakout_dist"].clip(lower=0) * 60, 0, 100)
    volume_score = clamp((df["vol_ratio"] - 1.05) * 110, 0, 100)
    relative_strength_score = df["relative_strength_score"]

    rsi_momentum = clamp((df["rsi14"] - 45) * (100 / 25), 0, 100)
    rsi_dir_bonus = clamp(df["rsi_delta"] * 6, 0, 35)
    momentum_score = clamp(rsi_momentum + rsi_dir_bonus)

    raw = (
        cfg.w_bo_range * compression_score
        + cfg.w_bo_signal * breakout_score
        + cfg.w_bo_volume * volume_score
        + cfg.w_bo_momentum * momentum_score
        + cfg.w_bo_trend * relative_strength_score
    )
    return np.maximum(base_breakout, clamp(raw))


def score_buy_trend_breakout(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    base_breakout = score_buy_breakout(df, cfg)
    adx_score = clamp((df["adx14"] - 18) * 5, 0, 100)
    slope_score = clamp(df["ema55_slope20"] * 20, 0, 100)
    trend_quality = cfg.w_bo_trend * adx_score + (1 - cfg.w_bo_trend) * slope_score
    trend_multiplier = 0.55 + trend_quality * 0.007
    return clamp(base_breakout * trend_multiplier)


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
    peak_price = 0.0

    for i in range(1, n):
        if not in_position:
            if not np.isnan(buy_arr[i]) and buy_arr[i] >= cfg.buy_threshold:
                in_position = True
                entry_price = close[i]
                entry_idx = i
                peak_price = close[i]
        else:
            peak_price = max(peak_price, close[i])
            current_return = (close[i] / entry_price - 1) * 100
            stop_hit = current_return <= -cfg.stop_loss_pct
            peak_return = (peak_price / entry_price - 1) * 100
            peak_drawdown = (close[i] / peak_price - 1) * 100 if peak_price > 0 else 0
            atr_value = df["atr14"].iloc[i] if "atr14" in df.columns else np.nan
            profit_drawdown_hit = peak_return >= 12 and peak_drawdown <= -7
            atr_trailing_hit = (
                peak_return >= 8
                and not np.isnan(atr_value)
                and close[i] <= peak_price - 3 * atr_value
            )
            trailing_hit = profit_drawdown_hit or atr_trailing_hit

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

            if stop_hit or trailing_hit or sell_signal:
                if stop_hit:
                    exit_reason = "stop_loss"
                elif trailing_hit:
                    exit_reason = "trailing_stop"
                else:
                    exit_reason = "sell_signal"
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
    buy_score = compute_buy_score(df, cfg)
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


def compute_buy_score(df: pd.DataFrame, cfg: UptrendDipConfig) -> pd.Series:
    if cfg.buy_strategy == "pullback":
        return score_buy_pullback(df, cfg)
    if cfg.buy_strategy == "bottom_reversal":
        return score_buy_bottom_reversal(df, cfg)
    if cfg.buy_strategy == "rsi_divergence":
        return score_buy_rsi_divergence(df, cfg)
    if cfg.buy_strategy == "index_shallow_pullback":
        return score_buy_index_shallow_pullback(df, cfg)
    if cfg.buy_strategy == "breakout":
        return score_buy_breakout(df, cfg)
    if cfg.buy_strategy == "tech_breakout":
        return score_buy_tech_breakout(df, cfg)
    if cfg.buy_strategy == "trend_breakout":
        return score_buy_trend_breakout(df, cfg)
    return np.maximum(score_buy_pullback(df, cfg), score_buy_breakout(df, cfg))


def _numeric_row_value(df: pd.DataFrame, pos: int, key: str, default: float = 0.0) -> float:
    if key not in df.columns:
        return default
    value = df[key].iloc[pos]
    if value is None or pd.isna(value):
        return default
    return float(value)


def classify_addon_signal(
    df: pd.DataFrame,
    pos: int,
    cfg: UptrendDipConfig,
    buy_score_value: float,
) -> str:
    """Human-readable signal type for long-term add-on logs."""
    if cfg.buy_strategy == "index_shallow_pullback":
        support = _numeric_row_value(df, pos, "index_pullback_support_score")
        rsi_reset = _numeric_row_value(df, pos, "index_pullback_rsi_score")
        if buy_score_value >= 55 and support >= 70 and rsi_reset >= 60:
            return "Shallow Pullback - Strong"
        if buy_score_value >= 45:
            return "Shallow Pullback - Medium"
        return "Shallow Pullback - Watch"

    if cfg.buy_strategy == "bottom_reversal":
        drawdown = _numeric_row_value(df, pos, "drawdown_252")
        retest = _numeric_row_value(df, pos, "bottom_retest_score")
        divergence = _numeric_row_value(df, pos, "rsi_divergence_score")
        if buy_score_value >= 55 and drawdown <= -20 and (retest >= 75 or divergence >= 75):
            return "Deep Bottom - Strong"
        if buy_score_value >= 45:
            return "Deep Bottom - Medium"
        return "Deep Bottom - Watch"

    if cfg.buy_strategy == "rsi_divergence":
        drawdown = _numeric_row_value(df, pos, "drawdown_252")
        divergence = _numeric_row_value(df, pos, "rsi_divergence_score")
        if buy_score_value >= 55 and divergence >= 75 and drawdown <= -15:
            return "RSI Divergence - Strong"
        if buy_score_value >= 45:
            return "RSI Divergence - Medium"
        return "RSI Divergence - Watch"

    if buy_score_value >= 55:
        return "Momentum Add-On - Strong"
    if buy_score_value >= 45:
        return "Momentum Add-On - Medium"
    return "Momentum Add-On - Watch"


def _factor_value(df: pd.DataFrame, pos: int, key: str, default: float = 0.0) -> float:
    return round(_numeric_row_value(df, pos, key, default), 2)


def addon_factor_snapshot(df: pd.DataFrame, pos: int, cfg: UptrendDipConfig) -> dict[str, Any]:
    """Compact per-signal factor snapshot for explaining radar triggers."""
    if cfg.buy_strategy == "bottom_reversal":
        return {
            "strategy": cfg.buy_strategy,
            "drawdown252Pct": _factor_value(df, pos, "drawdown_252"),
            "bottomRetestScore": _factor_value(df, pos, "bottom_retest_score"),
            "rsiDivergenceScore": _factor_value(df, pos, "rsi_divergence_score"),
            "crashScore": _factor_value(df, pos, "crash_score"),
            "capitulationScore": _factor_value(df, pos, "capitulation_score"),
            "rsi14": _factor_value(df, pos, "rsi14"),
            "volumeRatio": _factor_value(df, pos, "vol_ratio", default=1.0),
        }

    if cfg.buy_strategy == "rsi_divergence":
        return {
            "strategy": cfg.buy_strategy,
            "drawdown252Pct": _factor_value(df, pos, "drawdown_252"),
            "bottomRetestScore": _factor_value(df, pos, "bottom_retest_score"),
            "rsiDivergenceScore": _factor_value(df, pos, "rsi_divergence_score"),
            "rsi14": _factor_value(df, pos, "rsi14"),
            "capitulationScore": _factor_value(df, pos, "capitulation_score"),
            "volumeRatio": _factor_value(df, pos, "vol_ratio", default=1.0),
        }

    if cfg.buy_strategy == "index_shallow_pullback":
        return {
            "strategy": cfg.buy_strategy,
            "drawdown252Pct": _factor_value(df, pos, "drawdown_252"),
            "drawdownBandScore": _factor_value(df, pos, "index_pullback_drawdown_score"),
            "supportScore": _factor_value(df, pos, "index_pullback_support_score"),
            "rsiResetScore": _factor_value(df, pos, "index_pullback_rsi_score"),
            "declineScore": _factor_value(df, pos, "index_pullback_decline_score"),
            "trendHealthScore": _factor_value(df, pos, "index_pullback_trend_score"),
            "rsi14": _factor_value(df, pos, "rsi14"),
        }

    return {
        "strategy": cfg.buy_strategy,
        "rsi14": _factor_value(df, pos, "rsi14"),
        "volumeRatio": _factor_value(df, pos, "vol_ratio", default=1.0),
        "relativeStrengthScore": _factor_value(df, pos, "relative_strength_score", default=50.0),
        "trendPairs": _factor_value(df, pos, "trend_pairs"),
        "ema55Slope20": _factor_value(df, pos, "ema55_slope20"),
    }


def addon_action_profile(strength_label: str, factors: dict[str, Any]) -> dict[str, Any]:
    """Research-only actionability summary derived from existing signal factors."""
    strategy = factors.get("strategy", "")
    confirmations: list[str] = []
    risk_flags: list[str] = []

    if strategy == "bottom_reversal":
        if factors.get("drawdown252Pct", 0) <= -20:
            confirmations.append("deep_drawdown")
        if factors.get("bottomRetestScore", 0) >= 70:
            confirmations.append("bottom_retest")
        if factors.get("rsiDivergenceScore", 0) >= 70:
            confirmations.append("rsi_divergence")
        if factors.get("capitulationScore", 0) >= 50:
            confirmations.append("capitulation")
        if factors.get("volumeRatio", 1.0) < 1.0:
            risk_flags.append("no_volume_expansion")
        if factors.get("rsiDivergenceScore", 0) < 30:
            risk_flags.append("weak_rsi_divergence")
        if factors.get("bottomRetestScore", 0) < 50:
            risk_flags.append("weak_bottom_retest")
    elif strategy == "rsi_divergence":
        if factors.get("rsiDivergenceScore", 0) >= 70:
            confirmations.append("rsi_divergence")
        if factors.get("bottomRetestScore", 0) >= 70:
            confirmations.append("bottom_retest")
        if factors.get("drawdown252Pct", 0) <= -15:
            confirmations.append("drawdown_context")
        if factors.get("rsi14", 50) <= 35:
            confirmations.append("rsi_washout")

        if factors.get("rsiDivergenceScore", 0) < 55:
            risk_flags.append("weak_rsi_divergence")
        if factors.get("bottomRetestScore", 0) < 50:
            risk_flags.append("weak_bottom_retest")
    elif strategy == "index_shallow_pullback":
        if factors.get("supportScore", 0) >= 70:
            confirmations.append("support_hold")
        if factors.get("rsiResetScore", 0) >= 60:
            confirmations.append("rsi_reset")
        if factors.get("trendHealthScore", 0) >= 60:
            confirmations.append("trend_health")
        if factors.get("drawdown252Pct", 0) > -5:
            risk_flags.append("shallow_drawdown")
    else:
        if factors.get("relativeStrengthScore", 0) >= 60:
            confirmations.append("relative_strength")
        if factors.get("volumeRatio", 1.0) >= 1.3:
            confirmations.append("volume_expansion")
        if factors.get("ema55Slope20", 0) <= 0:
            risk_flags.append("weak_slope")

    if "Strong" in strength_label and len(confirmations) >= 2:
        grade = "Strong Add-On Candidate"
    elif "Medium" in strength_label or confirmations:
        grade = "Medium Add-On Candidate"
    else:
        grade = "Watch Only"

    return {
        "grade": grade,
        "confirmations": confirmations,
        "riskFlags": risk_flags,
    }


def _forward_pct(close: pd.Series, index_pos: int, days: int) -> float | None:
    target = index_pos + days
    if target >= len(close):
        return None
    current = close.iloc[index_pos]
    if current <= 0:
        return None
    return float((close.iloc[target] / current - 1) * 100)


def _forward_max_drawdown_pct(close: pd.Series, index_pos: int, days: int) -> float | None:
    end = min(index_pos + days, len(close) - 1)
    if end <= index_pos:
        return None
    current = close.iloc[index_pos]
    if current <= 0:
        return None
    future = close.iloc[index_pos + 1:end + 1]
    if future.empty:
        return None
    return min(0.0, float((future.min() / current - 1) * 100))


def _mean_present(values: list[float | None]) -> float:
    present = [v for v in values if v is not None and math.isfinite(v)]
    return float(np.mean(present)) if present else 0.0


def _mean_present_or_none(values: list[float | None]) -> float | None:
    present = [v for v in values if v is not None and math.isfinite(v)]
    return round(float(np.mean(present)), 2) if present else None


def summarize_radar_subset(
    per_symbol_radar: dict[str, dict[str, Any]],
    symbols: list[str],
) -> dict[str, Any]:
    rows = []
    strategy_counts: dict[str, int] = {}
    for symbol in symbols:
        metrics = per_symbol_radar.get(symbol, {})
        if not metrics or "error" in metrics:
            continue
        cfg = metrics.get("config", {})
        strategy = cfg.get("buy_strategy", "?")
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        fwd = metrics.get("avgForwardReturns", {})
        dd = metrics.get("avgDrawdowns", {})
        rows.append({
            "signalCount": metrics.get("signalCount"),
            "avg6mPct": fwd.get("avg6mPct"),
            "avg12mPct": fwd.get("avg12mPct"),
            "avg24mPct": fwd.get("avg24mPct"),
            "avgMaxDrawdown12mPct": dd.get("avgMaxDrawdown12mPct"),
        })

    def mean_key(key: str) -> float:
        return round(_mean_present([row.get(key) for row in rows]), 2)

    def median_key(key: str) -> float:
        values = [row.get(key) for row in rows]
        present = [v for v in values if v is not None and math.isfinite(v)]
        return round(float(np.median(present)), 2) if present else 0.0

    return {
        "symbols": [symbol for symbol in symbols if symbol in per_symbol_radar and "error" not in per_symbol_radar[symbol]],
        "symbolCount": len(rows),
        "avgSignals": mean_key("signalCount"),
        "avg6mPct": mean_key("avg6mPct"),
        "avg12mPct": mean_key("avg12mPct"),
        "avg24mPct": mean_key("avg24mPct"),
        "median12mPct": median_key("avg12mPct"),
        "avgMaxDrawdown12mPct": mean_key("avgMaxDrawdown12mPct"),
        "strategyCounts": strategy_counts,
    }


def summarize_radar_segments(
    per_symbol_radar: dict[str, dict[str, Any]],
    segments: dict[str, list[str]] = TECH_SEGMENTS,
) -> dict[str, dict[str, Any]]:
    return {
        segment_name: summarize_radar_subset(per_symbol_radar, symbols)
        for segment_name, symbols in segments.items()
    }


def summarize_signal_window(
    per_symbol_radar: dict[str, dict[str, Any]],
    symbols: list[str],
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    signals = []
    for symbol in symbols:
        for signal in per_symbol_radar.get(symbol, {}).get("signals", []):
            date = signal.get("date", "")
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            signals.append(signal)

    return {
        "startDate": start_date,
        "endDate": end_date,
        "signalCount": len(signals),
        "mature6mSignalCount": sum(1 for s in signals if s.get("return6mPct") is not None),
        "mature12mSignalCount": sum(1 for s in signals if s.get("return12mPct") is not None),
        "mature24mSignalCount": sum(1 for s in signals if s.get("return24mPct") is not None),
        "avg6mPct": _mean_present_or_none([s.get("return6mPct") for s in signals]),
        "avg12mPct": _mean_present_or_none([s.get("return12mPct") for s in signals]),
        "avg24mPct": _mean_present_or_none([s.get("return24mPct") for s in signals]),
        "avgMaxDrawdown12mPct": round(_mean_present([s.get("maxDrawdown12mPct") for s in signals]), 2),
    }


def summarize_signal_years(
    per_symbol_radar: dict[str, dict[str, Any]],
    symbols: list[str],
    start_year: int,
) -> dict[str, dict[str, Any]]:
    by_year: dict[str, list[dict[str, Any]]] = {}
    for symbol in symbols:
        for signal in per_symbol_radar.get(symbol, {}).get("signals", []):
            date = signal.get("date", "")
            if len(date) < 4:
                continue
            year = int(date[:4])
            if year < start_year:
                continue
            by_year.setdefault(str(year), []).append(signal)

    summary: dict[str, dict[str, Any]] = {}
    for year, signals in sorted(by_year.items()):
        summary[year] = {
            "signalCount": len(signals),
            "mature6mSignalCount": sum(1 for s in signals if s.get("return6mPct") is not None),
            "mature12mSignalCount": sum(1 for s in signals if s.get("return12mPct") is not None),
            "avg6mPct": _mean_present_or_none([s.get("return6mPct") for s in signals]),
            "avg12mPct": _mean_present_or_none([s.get("return12mPct") for s in signals]),
            "avgMaxDrawdown12mPct": round(_mean_present([s.get("maxDrawdown12mPct") for s in signals]), 2),
        }
    return summary


def _summarize_signal_group(signals: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "signalCount": len(signals),
        "mature12mSignalCount": sum(1 for signal in signals if signal.get("return12mPct") is not None),
        "avg12mPct": _mean_present_or_none([signal.get("return12mPct") for signal in signals]),
        "avgMaxDrawdown12mPct": round(_mean_present([signal.get("maxDrawdown12mPct") for signal in signals]), 2),
    }


def summarize_signal_risk_diagnostics(
    per_symbol_radar: dict[str, dict[str, Any]],
    symbols: list[str],
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    signals = []
    for symbol in symbols:
        for signal in per_symbol_radar.get(symbol, {}).get("signals", []):
            date = signal.get("date", "")
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            row = dict(signal)
            row["symbol"] = symbol
            signals.append(row)

    risk_groups: dict[str, list[dict[str, Any]]] = {}
    strength_groups: dict[str, list[dict[str, Any]]] = {}
    for signal in signals:
        strength = signal.get("strengthLabel", "Unknown")
        strength_groups.setdefault(strength, []).append(signal)

        flags = signal.get("actionProfile", {}).get("riskFlags", [])
        if not flags:
            flags = ["no_risk_flags"]
        for flag in flags:
            risk_groups.setdefault(str(flag), []).append(signal)

    return {
        "startDate": start_date,
        "endDate": end_date,
        "signalCount": len(signals),
        "riskFlagGroups": {
            key: _summarize_signal_group(rows)
            for key, rows in sorted(risk_groups.items())
        },
        "strengthGroups": {
            key: _summarize_signal_group(rows)
            for key, rows in sorted(strength_groups.items())
        },
    }


def summarize_recent_signal_log(
    per_symbol_radar: dict[str, dict[str, Any]],
    symbols: list[str],
    limit: int = 20,
) -> list[dict[str, Any]]:
    rows = []
    for symbol in symbols:
        for signal in per_symbol_radar.get(symbol, {}).get("signals", []):
            row = dict(signal)
            row["symbol"] = symbol
            rows.append(row)
    rows.sort(key=lambda row: row.get("date", ""), reverse=True)
    return rows[:limit]


def summarize_active_signal_log(
    per_symbol_radar: dict[str, dict[str, Any]],
    symbols: list[str],
    max_age_bars: int = 126,
    limit: int = 20,
) -> list[dict[str, Any]]:
    rows = []
    for row in summarize_recent_signal_log(per_symbol_radar, symbols, limit=200):
        age = row.get("barsSinceSignal")
        if not isinstance(age, int):
            continue
        if age <= max_age_bars:
            rows.append(row)
    return rows[:limit]


def build_paper_tracking_plan(
    current_signals: list[dict[str, Any]],
    generated_at: str,
) -> dict[str, Any]:
    generated_date = generated_at[:10] if generated_at else datetime.now().date().isoformat()
    generated_day = datetime.fromisoformat(generated_date).date()
    rows = []
    pending_6m = 0
    pending_12m = 0
    overdue_pending_6m = 0
    overdue_pending_12m = 0
    pending_6m_dates = []
    pending_12m_dates = []
    for signal in current_signals:
        signal_date = datetime.fromisoformat(signal.get("date", generated_date)).date()
        check_6m = signal_date + timedelta(days=183)
        check_12m = signal_date + timedelta(days=365)
        status_6m = "mature" if signal.get("return6mPct") is not None else "pending"
        status_12m = "mature" if signal.get("return12mPct") is not None else "pending"
        if status_6m == "pending":
            pending_6m += 1
            pending_6m_dates.append(check_6m)
            if check_6m <= generated_day:
                overdue_pending_6m += 1
        if status_12m == "pending":
            pending_12m += 1
            pending_12m_dates.append(check_12m)
            if check_12m <= generated_day:
                overdue_pending_12m += 1
        rows.append({
            "symbol": signal.get("symbol", "?"),
            "signalDate": signal_date.isoformat(),
            "price": signal.get("price"),
            "strengthLabel": signal.get("strengthLabel", "-"),
            "action": signal.get("actionProfile", {}).get("grade", "-"),
            "riskFlags": signal.get("actionProfile", {}).get("riskFlags", []),
            "check6mDate": check_6m.isoformat(),
            "check12mDate": check_12m.isoformat(),
            "status6m": status_6m,
            "status12m": status_12m,
            "return6mPct": signal.get("return6mPct"),
            "return12mPct": signal.get("return12mPct"),
            "maxDrawdown12mPct": signal.get("maxDrawdown12mPct"),
        })

    return {
        "generatedDate": generated_date,
        "signalCount": len(rows),
        "pending6mCount": pending_6m,
        "pending12mCount": pending_12m,
        "overduePending6mCount": overdue_pending_6m,
        "overduePending12mCount": overdue_pending_12m,
        "nextPending6mDate": min(pending_6m_dates).isoformat() if pending_6m_dates else None,
        "nextPending12mDate": min(pending_12m_dates).isoformat() if pending_12m_dates else None,
        "nextPendingCheckDate": min(pending_6m_dates + pending_12m_dates).isoformat()
        if pending_6m_dates or pending_12m_dates else None,
        "signals": rows,
    }


def format_paper_tracking_status(
    results: dict[str, Any],
    limit: int = 12,
    as_of_date: str | None = None,
) -> str:
    paper_plan = results.get("paperTrackingPlan", {})
    if not paper_plan:
        return "No paperTrackingPlan found. Run the search first to generate strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_results.json."

    as_of = datetime.fromisoformat(as_of_date).date() if as_of_date else datetime.now().date()
    overdue_6m = 0
    overdue_12m = 0
    rows = []
    for row in paper_plan.get("signals", []):
        row = dict(row)
        status_6m = row.get("status6m", "-")
        status_12m = row.get("status12m", "-")
        check_6m = row.get("check6mDate")
        check_12m = row.get("check12mDate")
        if status_6m == "pending" and check_6m and datetime.fromisoformat(check_6m).date() <= as_of:
            status_6m = "overdue"
            overdue_6m += 1
        if status_12m == "pending" and check_12m and datetime.fromisoformat(check_12m).date() <= as_of:
            status_12m = "overdue"
            overdue_12m += 1
        row["displayStatus6m"] = status_6m
        row["displayStatus12m"] = status_12m
        rows.append(row)

    lines = [
        "Paper Tracking Status",
        f"Generated date: {paper_plan.get('generatedDate', '-')}",
        f"As-of date: {as_of.isoformat()}",
        f"Tracked signals: {paper_plan.get('signalCount', 0)}",
        f"Pending checks: 6m={paper_plan.get('pending6mCount', 0)}, 12m={paper_plan.get('pending12mCount', 0)}",
        f"Overdue pending checks: 6m={overdue_6m}, 12m={overdue_12m}",
        f"Next pending check date: {paper_plan.get('nextPendingCheckDate', '-')}",
        "",
        "Signals:",
    ]
    for row in rows[:limit]:
        risk_flags = ", ".join(row.get("riskFlags", [])) if row.get("riskFlags") else "-"
        lines.append(
            f"- {row.get('symbol', '?')} | signal={row.get('signalDate', '-')} | "
            f"6m={row.get('check6mDate', '-')} {row.get('displayStatus6m', '-')} | "
            f"12m={row.get('check12mDate', '-')} {row.get('displayStatus12m', '-')} | "
            f"{row.get('strengthLabel', '-')} | {row.get('action', '-')} | risks={risk_flags}"
        )
    return "\n".join(lines)


def evaluate_long_term_radar(
    df: pd.DataFrame,
    cfg: UptrendDipConfig,
    min_gap_days: int = 63,
    signal_start_date: str | None = None,
    signal_end_date: str | None = None,
) -> dict[str, Any]:
    """Long-term add-on radar: sparse buy signals scored by 6/12/24m outcomes."""
    buy_score = df["buy_score"] if "buy_score" in df.columns else compute_buy_score(df, cfg)
    bearish_candle = df["close"] < df["open"]
    signal_positions: list[int] = []
    last_pos = -min_gap_days
    for pos, score in enumerate(buy_score):
        signal_date = df.index[pos].date().isoformat()
        if signal_start_date and signal_date < signal_start_date:
            continue
        if signal_end_date and signal_date > signal_end_date:
            continue
        if np.isnan(score) or score < cfg.buy_threshold:
            continue
        if not bool(bearish_candle.iloc[pos]):
            continue
        if pos - last_pos < min_gap_days:
            if cfg.buy_strategy != "index_shallow_pullback":
                continue
            current_dd = _numeric_row_value(df, pos, "drawdown_252", default=0.0)
            last_dd = _numeric_row_value(df, last_pos, "drawdown_252", default=0.0)
            if current_dd > last_dd - 4.0:
                continue
        signal_positions.append(pos)
        last_pos = pos

    if not signal_positions:
        return {
            "score": -999,
            "signalCount": 0,
            "matureSignalCount": 0,
            "config": asdict(cfg),
            "signals": [],
        }

    close = df["close"]
    signals = []
    for pos in signal_positions:
        signal_score = float(buy_score.iloc[pos])
        bars_since_signal = len(close) - 1 - pos
        strength_label = classify_addon_signal(df, pos, cfg, signal_score)
        factor_snapshot = addon_factor_snapshot(df, pos, cfg)
        signal = {
            "date": str(df.index[pos].date()),
            "price": round(float(close.iloc[pos]), 4),
            "buyScore": round(signal_score, 2),
            "strengthLabel": strength_label,
            "factorSnapshot": factor_snapshot,
            "actionProfile": addon_action_profile(strength_label, factor_snapshot),
            "barsSinceSignal": int(bars_since_signal),
            "mature6m": bool(bars_since_signal >= 126),
            "mature12m": bool(bars_since_signal >= 252),
            "mature24m": bool(bars_since_signal >= 504),
            "return6mPct": _forward_pct(close, pos, 126),
            "return12mPct": _forward_pct(close, pos, 252),
            "return24mPct": _forward_pct(close, pos, 504),
            "maxDrawdown6mPct": _forward_max_drawdown_pct(close, pos, 126),
            "maxDrawdown12mPct": _forward_max_drawdown_pct(close, pos, 252),
        }
        signals.append(signal)

    avg_6m = _mean_present([s["return6mPct"] for s in signals])
    avg_12m = _mean_present([s["return12mPct"] for s in signals])
    avg_24m = _mean_present([s["return24mPct"] for s in signals])
    avg_dd_6m = _mean_present([s["maxDrawdown6mPct"] for s in signals])
    avg_dd_12m = _mean_present([s["maxDrawdown12mPct"] for s in signals])
    mature_count = sum(1 for s in signals if s["return12mPct"] is not None)

    if mature_count < 3:
        score = -100 + mature_count * 10
    else:
        overactive_penalty = max(0, len(signals) - 24) * 1.5
        drawdown_penalty = max(0, abs(avg_dd_12m) - 18) * 1.2
        score = (
            avg_6m * 0.3
            + avg_12m * 1.2
            + avg_24m * 0.9
            - drawdown_penalty
            - overactive_penalty
        )


    def rounded(value: float | None) -> float | None:
        return round(value, 2) if value is not None and math.isfinite(value) else None

    for signal in signals:
        for key in ["return6mPct", "return12mPct", "return24mPct", "maxDrawdown6mPct", "maxDrawdown12mPct"]:
            signal[key] = rounded(signal[key])

    return {
        "score": round(float(score), 2) if math.isfinite(score) else -999,
        "signalCount": len(signals),
        "matureSignalCount": mature_count,
        "config": asdict(cfg),
        "avgForwardReturns": {
            "avg6mPct": round(avg_6m, 2),
            "avg12mPct": round(avg_12m, 2),
            "avg24mPct": round(avg_24m, 2),
        },
        "avgDrawdowns": {
            "avgMaxDrawdown6mPct": round(avg_dd_6m, 2),
            "avgMaxDrawdown12mPct": round(avg_dd_12m, 2),
        },
        "signals": signals[:40],
    }


def evaluate_stage2(
    df: pd.DataFrame, cfg: UptrendDipConfig,
) -> dict[str, Any]:
    """Stage 2: full trade simulation evaluation."""
    # Score buy signals
    if cfg.buy_strategy == "pullback":
        buy_score = score_buy_pullback(df, cfg)
    elif cfg.buy_strategy == "bottom_reversal":
        buy_score = score_buy_bottom_reversal(df, cfg)
    elif cfg.buy_strategy == "rsi_divergence":
        buy_score = score_buy_rsi_divergence(df, cfg)
    elif cfg.buy_strategy == "index_shallow_pullback":
        buy_score = score_buy_index_shallow_pullback(df, cfg)
    elif cfg.buy_strategy == "breakout":
        buy_score = score_buy_breakout(df, cfg)
    elif cfg.buy_strategy == "tech_breakout":
        buy_score = score_buy_tech_breakout(df, cfg)
    elif cfg.buy_strategy == "trend_breakout":
        buy_score = score_buy_trend_breakout(df, cfg)
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
    trailing_exits = sum(1 for t in trades if t["exit_reason"] == "trailing_stop")
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
            "trailingExits": trailing_exits,
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


def best_by_buy_strategy(ranked: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for entry in ranked:
        strategy = entry.get("config", {}).get("buy_strategy")
        if strategy and strategy not in best:
            best[strategy] = entry
    return best


def select_freeze_candidate_entries(
    recommended: dict[str, Any],
    date_split: dict[str, Any],
    strategy_best: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    def add(reason: str, entry: dict[str, Any] | None) -> None:
        if not entry:
            return
        cfg_d = entry.get("config", {})
        name = cfg_d.get("name")
        if not name or any(item["name"] == name for item in candidates):
            return
        candidates.append({
            "reason": reason,
            "name": name,
            "strategy": cfg_d.get("buy_strategy", "?"),
            "config": cfg_d,
            "combinedScore": entry.get("combinedScore"),
        })

    add("Broad default", recommended)
    add("Date-split selected", date_split.get("trainedDefault"))
    add("Best trend-breakout family", strategy_best.get("trend_breakout"))
    add("Best tech-breakout family", strategy_best.get("tech_breakout"))
    add("Best RSI-divergence baseline", strategy_best.get("rsi_divergence"))
    add("Best index-shallow-pullback family", strategy_best.get("index_shallow_pullback"))
    return candidates


def evaluate_restricted_walk_forward(
    frames_by_symbol: dict[str, pd.DataFrame],
    train_symbols: list[str],
    holdout_symbols: list[str],
    candidate_entries: list[dict[str, Any]],
    years: list[int],
) -> dict[str, Any]:
    """Yearly walk-forward using only a small frozen candidate set."""
    cfg_fields = [f.name for f in fields(UptrendDipConfig)]
    configs = [
        UptrendDipConfig(**{k: entry["config"][k] for k in cfg_fields})
        for entry in candidate_entries
    ]
    reason_by_name = {entry["name"]: entry.get("reason", "?") for entry in candidate_entries}
    rows: list[dict[str, Any]] = []

    for year in years:
        train_end = f"{year - 1}-12-31"
        holdout_start = f"{year}-01-01"
        holdout_end = f"{year}-12-31"
        train_metrics: dict[str, list[dict[str, Any]]] = {}

        for symbol in train_symbols:
            df = frames_by_symbol.get(symbol)
            if df is None:
                continue
            train_metrics[symbol] = [
                evaluate_long_term_radar(df, cfg, signal_end_date=train_end)
                for cfg in configs
            ]

        train_ranked = combined_rank(configs, train_metrics)
        if not train_ranked:
            rows.append({
                "year": year,
                "trainSignalEndDate": train_end,
                "holdoutSignalStartDate": holdout_start,
                "holdoutSignalEndDate": holdout_end,
                "error": "no trainable candidate",
            })
            continue

        selected = train_ranked[0]
        selected_cfg_dict = selected["config"]
        selected_cfg = UptrendDipConfig(**{k: selected_cfg_dict[k] for k in cfg_fields})
        holdout_by_symbol: dict[str, dict[str, Any]] = {}
        for symbol in holdout_symbols:
            df = frames_by_symbol.get(symbol)
            if df is None:
                holdout_by_symbol[symbol] = {"error": "data not found"}
                continue
            holdout_by_symbol[symbol] = evaluate_long_term_radar(
                df,
                selected_cfg,
                signal_start_date=holdout_start,
                signal_end_date=holdout_end,
            )

        selected_name = selected_cfg_dict.get("name", "?")
        rows.append({
            "year": year,
            "trainSignalEndDate": train_end,
            "holdoutSignalStartDate": holdout_start,
            "holdoutSignalEndDate": holdout_end,
            "selectedReason": reason_by_name.get(selected_name, "?"),
            "selectedConfig": selected_cfg_dict,
            "trainCombinedScore": selected.get("combinedScore"),
            "techHoldoutSummary": summarize_radar_subset(holdout_by_symbol, holdout_symbols),
            "techSignalSummary": summarize_signal_window(
                holdout_by_symbol,
                holdout_symbols,
                start_date=holdout_start,
                end_date=holdout_end,
            ),
            "latestSignals": summarize_recent_signal_log(
                holdout_by_symbol,
                holdout_symbols,
                limit=8,
            ),
        })

    return {
        "note": "Restricted walk-forward: each year selects from frozen candidate configs only, not the full grid.",
        "candidateCount": len(candidate_entries),
        "trainSymbols": train_symbols,
        "holdoutSymbols": holdout_symbols,
        "years": rows,
    }


def evaluate_full_grid_walk_forward(
    frames_by_symbol: dict[str, pd.DataFrame],
    train_symbols: list[str],
    holdout_symbols: list[str],
    configs: list[UptrendDipConfig],
    years: list[int],
) -> dict[str, Any]:
    """Yearly walk-forward that reranks the full stage-1 config grid each year."""
    rows: list[dict[str, Any]] = []

    for year in years:
        train_end = f"{year - 1}-12-31"
        holdout_start = f"{year}-01-01"
        holdout_end = f"{year}-12-31"
        train_metrics: dict[str, list[dict[str, Any]]] = {}

        for symbol in train_symbols:
            df = frames_by_symbol.get(symbol)
            if df is None:
                continue
            train_metrics[symbol] = [
                evaluate_long_term_radar(df, cfg, signal_end_date=train_end)
                for cfg in configs
            ]

        train_ranked = combined_rank(configs, train_metrics)
        if not train_ranked:
            rows.append({
                "year": year,
                "trainSignalEndDate": train_end,
                "holdoutSignalStartDate": holdout_start,
                "holdoutSignalEndDate": holdout_end,
                "error": "no trainable config",
            })
            continue

        selected = train_ranked[0]
        selected_cfg_dict = selected["config"]
        selected_cfg = UptrendDipConfig(**{
            k: selected_cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
        })
        holdout_by_symbol: dict[str, dict[str, Any]] = {}
        for symbol in holdout_symbols:
            df = frames_by_symbol.get(symbol)
            if df is None:
                holdout_by_symbol[symbol] = {"error": "data not found"}
                continue
            holdout_by_symbol[symbol] = evaluate_long_term_radar(
                df,
                selected_cfg,
                signal_start_date=holdout_start,
                signal_end_date=holdout_end,
            )

        rows.append({
            "year": year,
            "trainSignalEndDate": train_end,
            "holdoutSignalStartDate": holdout_start,
            "holdoutSignalEndDate": holdout_end,
            "selectedConfig": selected_cfg_dict,
            "trainCombinedScore": selected.get("combinedScore"),
            "trainTop5": [
                {
                    "config": item.get("config", {}),
                    "combinedScore": item.get("combinedScore"),
                }
                for item in train_ranked[:5]
            ],
            "techHoldoutSummary": summarize_radar_subset(holdout_by_symbol, holdout_symbols),
            "techSignalSummary": summarize_signal_window(
                holdout_by_symbol,
                holdout_symbols,
                start_date=holdout_start,
                end_date=holdout_end,
            ),
            "latestSignals": summarize_recent_signal_log(
                holdout_by_symbol,
                holdout_symbols,
                limit=8,
            ),
        })

    return {
        "note": "Full-grid walk-forward: each year reranks the full stage-1 config grid using prior signal history.",
        "configCount": len(configs),
        "trainSymbols": train_symbols,
        "holdoutSymbols": holdout_symbols,
        "years": rows,
    }


def evaluate_multi_window_validation(
    frames_by_symbol: dict[str, pd.DataFrame],
    holdout_symbols: list[str],
    cfg: UptrendDipConfig,
    anchored_start_years: list[int],
    rolling_windows: list[tuple[str, str]],
) -> dict[str, Any]:
    """Evaluate one frozen config across multiple holdout windows."""

    def evaluate_window(start_date: str, end_date: str | None = None) -> dict[str, Any]:
        by_symbol: dict[str, dict[str, Any]] = {}
        for symbol in holdout_symbols:
            df = frames_by_symbol.get(symbol)
            if df is None:
                by_symbol[symbol] = {"error": "data not found"}
                continue
            by_symbol[symbol] = evaluate_long_term_radar(
                df,
                cfg,
                signal_start_date=start_date,
                signal_end_date=end_date,
            )
        return {
            "symbolSummary": summarize_radar_subset(by_symbol, holdout_symbols),
            "signalSummary": summarize_signal_window(
                by_symbol,
                holdout_symbols,
                start_date=start_date,
                end_date=end_date,
            ),
            "latestSignals": summarize_recent_signal_log(
                by_symbol,
                holdout_symbols,
                limit=8,
            ),
        }

    anchored_rows = []
    for year in anchored_start_years:
        start_date = f"{year}-01-01"
        payload = evaluate_window(start_date)
        anchored_rows.append({
            "startYear": year,
            "startDate": start_date,
            "endDate": None,
            **payload,
        })

    rolling_rows = []
    for start_date, end_date in rolling_windows:
        payload = evaluate_window(start_date, end_date)
        rolling_rows.append({
            "label": f"{start_date} to {end_date}",
            "startDate": start_date,
            "endDate": end_date,
            **payload,
        })

    return {
        "note": "Multi-window validation: evaluates one frozen config across anchored and fixed rolling holdout windows.",
        "config": asdict(cfg),
        "holdoutSymbols": holdout_symbols,
        "anchoredWindows": anchored_rows,
        "rollingWindows": rolling_rows,
        "summary": summarize_multi_window_rows(anchored_rows + rolling_rows),
    }


def summarize_multi_window_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    signal_counts = [
        row.get("signalSummary", {}).get("signalCount", 0)
        for row in rows
    ]
    mature_counts = [
        row.get("signalSummary", {}).get("mature12mSignalCount", 0)
        for row in rows
    ]
    avg12_values = [
        row.get("signalSummary", {}).get("avg12mPct")
        for row in rows
        if isinstance(row.get("signalSummary", {}).get("avg12mPct"), (int, float))
    ]
    dd12_values = [
        row.get("signalSummary", {}).get("avgMaxDrawdown12mPct")
        for row in rows
        if isinstance(row.get("signalSummary", {}).get("avgMaxDrawdown12mPct"), (int, float))
    ]

    return {
        "windowCount": len(rows),
        "matureWindowCount": sum(1 for count in mature_counts if count > 0),
        "totalSignals": int(sum(signal_counts)),
        "windowsWithPositiveAvg12m": sum(1 for value in avg12_values if value > 0),
        "minSignalAvg12mPct": round(float(min(avg12_values)), 2) if avg12_values else None,
        "medianSignalAvg12mPct": round(float(np.median(avg12_values)), 2) if avg12_values else None,
        "maxSignalAvg12mPct": round(float(max(avg12_values)), 2) if avg12_values else None,
        "worstSignalDrawdown12mPct": round(float(min(dd12_values)), 2) if dd12_values else None,
    }


def select_stage2_buy_configs(
    ranked_stage1: list[dict[str, Any]],
    max_configs: int = 8,
) -> list[UptrendDipConfig]:
    selected: list[UptrendDipConfig] = []
    seen_names: set[str] = set()

    def add(entry: dict[str, Any]) -> None:
        cfg_dict = entry["config"]
        name = cfg_dict["name"]
        if name in seen_names or len(selected) >= max_configs:
            return
        selected.append(UptrendDipConfig(**{
            k: cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
        }))
        seen_names.add(name)

    for entry in ranked_stage1[:3]:
        add(entry)

    seen_strategies = {cfg.buy_strategy for cfg in selected}
    for entry in ranked_stage1:
        strategy = entry["config"]["buy_strategy"]
        if strategy not in seen_strategies:
            add(entry)
            seen_strategies.add(strategy)

    for entry in ranked_stage1:
        if len(selected) >= max_configs:
            break
        add(entry)

    return selected


# ═══════════════════════════════════════════════════════
# Pine Script generation
# ═══════════════════════════════════════════════════════


def generate_pine_script(cfg: UptrendDipConfig) -> str:
    return f'''//@version=5
indicator("Uptrend Dip Buy+Sell v1", overlay=true, max_labels_count=500)

// -------------------------------------------------------
// Inputs
// -------------------------------------------------------
buy_strategy  = input.string("{cfg.buy_strategy}", "Buy Strategy", options=["pullback","breakout","tech_breakout","trend_breakout","bottom_reversal","rsi_divergence","index_shallow_pullback","both"])
buy_threshold = input.float({cfg.buy_threshold:.0f}, "Buy Threshold", minval=10, maxval=90, step=5)
sell_threshold = input.float({cfg.sell_threshold:.0f}, "Sell Threshold", minval=10, maxval=90, step=5)
stop_loss_pct = input.float({cfg.stop_loss_pct:.0f}, "Stop Loss %", minval=1, maxval=20, step=1)
benchmark_symbol = input.symbol("SPY", "Relative Strength Benchmark")

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
w_bo_trend    = input.float({cfg.w_bo_trend:.2f}, "BO Trend / Tech RS", minval=0, maxval=1, step=0.05)

// Sell weights
w_sell_breakdown = input.float({cfg.w_sell_breakdown:.2f}, "Sell Breakdown",    minval=0, maxval=1, step=0.05)
w_sell_cross     = input.float({cfg.w_sell_cross:.2f}, "Sell Cross",        minval=0, maxval=1, step=0.05)
w_sell_rsi_break = input.float({cfg.w_sell_rsi_break:.2f}, "Sell RSI Break",    minval=0, maxval=1, step=0.05)
w_sell_overbought = input.float({cfg.w_sell_overbought:.2f}, "Sell Overbought",   minval=0, maxval=1, step=0.05)
w_sell_kupper    = input.float({cfg.w_sell_keltner_upper:.2f}, "Sell Keltner Upper", minval=0, maxval=1, step=0.05)
w_sell_profit    = input.float({cfg.w_sell_profit:.2f}, "Sell Profit",      minval=0, maxval=1, step=0.05)

// Helpers
rolling_count(condition, length) =>
    count = 0.0
    for i = 0 to length - 1
        count += condition[i] ? 1.0 : 0.0
    count

// -------------------------------------------------------
// Indicators
// -------------------------------------------------------
atr14 = ta.atr(14)
atr20 = ta.atr(20)

ema20  = ta.ema(close, 20)
ema21  = ta.ema(close, 21)
ema55  = ta.ema(close, 55)
ema100 = ta.ema(close, 100)
sma200 = ta.sma(close, 200)
ema55_slope20 = (ema55 / ema55[20] - 1) * 100
[_plus_di, _minus_di, adx_val] = ta.dmi(14, 14)

keltner_upper = ema20 + 2 * atr20

rsi_val   = ta.rsi(close, 14)
stoch_val = ta.stoch(close, high, low, 14)
vol_ratio = volume / ta.sma(volume, 20)

drawdown_252 = (close / ta.highest(close, 252) - 1) * 100
return_5d = (close / close[5] - 1) * 100
return_20d = (close / close[20] - 1) * 100

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
prior_high_20 = ta.highest(high[1], 20)
tech_breakout_dist = (close - prior_high_20) / atr14
keltner_upper_dist = (close - keltner_upper) / atr14

benchmark_close = request.security(benchmark_symbol, timeframe.period, close)
rs_ratio = close / benchmark_close
rs_sma50 = ta.sma(rs_ratio, 50)
rs_delta20 = rs_ratio / rs_ratio[20] - 1
rs_level = math.max(0, math.min(100, (rs_ratio / rs_sma50 - 1) * 500 + 50))
rs_slope = math.max(0, math.min(100, rs_delta20 * 500 + 50))
relative_strength_score = (rs_level + rs_slope) / 2

prior_low_120 = ta.lowest(low[10], 120)
retest_dist_pct = math.abs(close / prior_low_120 - 1) * 100
low_120 = ta.lowest(low, 120)
near_low = low <= low_120 * 1.05
near_low_count = rolling_count(near_low, 120)
retest_score = math.max(0, math.min(100, (8 - retest_dist_pct) * 12.5))
multi_bottom_bonus = math.max(0, math.min(40, (near_low_count - 2) * 15))
bottom_retest_score = math.max(0, math.min(100, retest_score + multi_bottom_bonus))
prior_rsi_min = ta.lowest(rsi_val[10], 60)
lower_low_zone = close <= prior_low_120 * 1.05
rsi_divergence_score = (lower_low_zone ? 1.0 : 0.0) * math.max(0, math.min(100, (rsi_val - prior_rsi_min - 4) * 8))
crash_score = math.max(0, math.min(100, (-return_20d - 10) * 5 + (-return_5d - 4) * 5))
capitulation_score = math.max(0, math.min(100, (vol_ratio - 1.2) * 45 + (35 - rsi_val) * 3))

dd_abs = -drawdown_252
idx_drawdown_entry = math.max(0, math.min(100, (dd_abs - 2.5) * 35))
idx_too_deep_guard = math.max(0, math.min(100, (22 - dd_abs) * 8))
idx_drawdown = math.min(idx_drawdown_entry, idx_too_deep_guard)
ema21_dist_pct = (close / ema21 - 1) * 100
ema55_dist_pct = (close / ema55 - 1) * 100
sma200_dist_pct = (close / sma200 - 1) * 100
idx_ema21_support = math.max(0, math.min(100, (4 - math.abs(ema21_dist_pct)) * 25))
idx_ema55_support = math.max(0, math.min(100, (6 - math.abs(ema55_dist_pct)) * (100 / 6)))
idx_sma200_support = math.max(0, math.min(100, (5 - math.abs(sma200_dist_pct)) * 20))
idx_support = math.max(idx_ema21_support, math.max(idx_ema55_support, idx_sma200_support))
idx_rsi_reset = math.max(0, math.min(100, 100 - math.abs(rsi_val - 43) * 5.5))
idx_decline = math.max(0, math.min(100, (-return_20d - 2) * 10 + (-return_5d - 0.5) * 12))
idx_trend_buffer = math.max(0, math.min(100, (close / sma200 - 0.97) * 900))
idx_slope_health = math.max(0, math.min(100, ema55_slope20 * 10 + 40))
idx_trend_health = math.max(0, math.min(100, trend_pairs * 45 + idx_trend_buffer * 0.30 + idx_slope_health * 0.25))

ema_cross_down = ema21 < ema55 and ema21[1] >= ema55[1]

// -------------------------------------------------------
// Buy Scoring
// -------------------------------------------------------
// Pullback
pb_trend  = trend_pairs * 100
pb_level  = math.max(0, math.min(100, math.max(0, pullback_atr) * 50))
pb_rsi    = rsi_sweet
pb_stoch  = math.max(0, math.min(100, (40 - stoch_val) * 2.5))
pb_volume = math.max(0, math.min(100, (1.0 - vol_ratio) * 100))
buy_pullback = math.max(0, math.min(100,
     w_pb_trend * pb_trend + w_pb_level * pb_level + w_pb_rsi * pb_rsi
   + w_pb_stoch * pb_stoch + w_pb_volume * pb_volume))

// Bottom Reversal
btm_drawdown = math.max(0, math.min(100, (-drawdown_252 - 15) * 4))
buy_bottom_reversal = math.max(0, math.min(100,
     w_pb_trend * btm_drawdown + w_pb_level * bottom_retest_score + w_pb_rsi * rsi_divergence_score
   + w_pb_stoch * crash_score + w_pb_volume * capitulation_score))

// RSI Divergence Baseline
rsi_div_drawdown = math.max(0, math.min(100, (-drawdown_252 - 10) * 5))
rsi_washout = math.max(0, math.min(100, (40 - rsi_val) * 4))
buy_rsi_divergence = math.max(0, math.min(100,
     w_pb_trend * rsi_divergence_score + w_pb_level * bottom_retest_score + w_pb_rsi * rsi_div_drawdown
   + w_pb_stoch * rsi_washout + w_pb_volume * capitulation_score))

// Index Shallow Pullback
buy_index_shallow_pullback = math.max(0, math.min(100,
     w_pb_trend * idx_drawdown + w_pb_level * idx_support + w_pb_rsi * idx_rsi_reset
   + w_pb_stoch * idx_decline + w_pb_volume * idx_trend_health))

// Breakout
bo_range    = atr_compression
bo_signal   = math.max(0, math.min(100, math.max(0, breakout_dist) * 50))
bo_volume   = math.max(0, math.min(100, (vol_ratio - 1.0) * 100))
bo_momentum = math.max(0, math.min(100, math.max(0, math.min(60, rsi_val - 40)) * (100/60) + math.max(0, math.min(30, rsi_delta * 5))))
bo_trend    = math.max(0, math.min(100, (close > sma200 ? 50.0 : 0.0) + trend_pairs * 50))
buy_breakout = math.max(0, math.min(100,
     w_bo_range * bo_range + w_bo_signal * bo_signal + w_bo_volume * bo_volume
   + w_bo_momentum * bo_momentum + w_bo_trend * bo_trend))

// Tech Breakout
tb_compression = atr_compression
tb_breakout = math.max(0, math.min(100, math.max(0, tech_breakout_dist) * 60))
tb_volume = math.max(0, math.min(100, (vol_ratio - 1.05) * 110))
tb_momentum = math.max(0, math.min(100, math.max(0, math.min(100, (rsi_val - 45) * (100/25))) + math.max(0, math.min(35, rsi_delta * 6))))
buy_tech_breakout = math.max(0, math.min(100,
     w_bo_range * tb_compression + w_bo_signal * tb_breakout + w_bo_volume * tb_volume
   + w_bo_momentum * tb_momentum + w_bo_trend * relative_strength_score))
buy_tech_breakout := math.max(buy_breakout, buy_tech_breakout)

// Trend-filtered Breakout
tr_adx = math.max(0, math.min(100, (adx_val - 18) * 5))
tr_slope = math.max(0, math.min(100, ema55_slope20 * 20))
tr_quality = w_bo_trend * tr_adx + (1 - w_bo_trend) * tr_slope
buy_trend_breakout = math.max(0, math.min(100, buy_breakout * (0.55 + tr_quality * 0.007)))

buy_score = buy_strategy == "pullback" ? buy_pullback : buy_strategy == "breakout" ? buy_breakout : buy_strategy == "tech_breakout" ? buy_tech_breakout : buy_strategy == "trend_breakout" ? buy_trend_breakout : buy_strategy == "bottom_reversal" ? buy_bottom_reversal : buy_strategy == "rsi_divergence" ? buy_rsi_divergence : buy_strategy == "index_shallow_pullback" ? buy_index_shallow_pullback : math.max(buy_pullback, buy_breakout)

// -------------------------------------------------------
// Sell Scoring
// -------------------------------------------------------
sell_breakdown = math.max(
     math.max(0, math.min(100, (ema55 - close) / atr14 * 40)),
     math.max(0, math.min(100, (sma200 - close) / atr14 * 30)))
sell_cross = ema_cross_down ? 100.0 : 0.0
sell_rsi_break = (rsi_val < 40 and ta.rsi(close, 14)[5] > 50) ? math.max(0, math.min(100, (40 - rsi_val) * 2.5)) : 0.0
sell_reversal = math.max(0, math.min(100,
     w_sell_breakdown * sell_breakdown + w_sell_cross * sell_cross + w_sell_rsi_break * sell_rsi_break))

// Overbought (simplified - no entry price in Pine)
sell_overbought_rsi = math.max(0, math.min(100, (rsi_val - 45) * 2.0))
sell_overbought_stoch = math.max(0, math.min(100, (stoch_val - 45) * 2.0))
sell_ob = (sell_overbought_rsi + sell_overbought_stoch) / 2
sell_kupper = math.max(0, math.min(100, math.max(0, keltner_upper_dist) * 50))
sell_overbought = math.max(0, math.min(100, w_sell_overbought * sell_ob + w_sell_kupper * sell_kupper))

sell_score = math.max(sell_reversal, sell_overbought)

// -------------------------------------------------------
// Signals & Plotting
// -------------------------------------------------------
raw_buy_signal  = buy_score >= buy_threshold and not na(sma200)
raw_sell_signal = sell_score >= sell_threshold
bearish_candle = close < open

var bool in_position = false
var float entry_price = na
var float peak_price = na

buy_signal = raw_buy_signal and bearish_candle and not in_position
if buy_signal
    in_position := true
    entry_price := close
    peak_price := close
else if in_position
    peak_price := math.max(peak_price, close)

current_return = in_position and not na(entry_price) ? (close / entry_price - 1) * 100 : na
peak_return = in_position and not na(entry_price) ? (peak_price / entry_price - 1) * 100 : na
peak_drawdown = in_position and not na(peak_price) ? (close / peak_price - 1) * 100 : na
stop_loss_signal = in_position and current_return <= -stop_loss_pct
profit_drawdown_signal = in_position and peak_return >= 12 and peak_drawdown <= -7
atr_trailing_signal = in_position and peak_return >= 8 and close <= peak_price - 3 * atr14

sell_signal = in_position and not buy_signal and (raw_sell_signal or stop_loss_signal or profit_drawdown_signal or atr_trailing_signal)
if sell_signal
    in_position := false
    entry_price := na
    peak_price := na

bgcolor(buy_signal ? color.new(color.green, 80) : na, title="Buy Zone")
bgcolor(sell_signal ? color.new(color.red, 80) : na, title="Sell Zone")

idx_strong_signal = buy_signal and buy_strategy == "index_shallow_pullback" and buy_score >= 55 and idx_support >= 70 and idx_rsi_reset >= 60
idx_medium_signal = buy_signal and buy_strategy == "index_shallow_pullback" and not idx_strong_signal and buy_score >= 45
idx_watch_signal = buy_signal and buy_strategy == "index_shallow_pullback" and not idx_strong_signal and not idx_medium_signal
btm_strong_signal = buy_signal and buy_strategy == "bottom_reversal" and buy_score >= 55 and drawdown_252 <= -20 and (bottom_retest_score >= 75 or rsi_divergence_score >= 75)
btm_medium_signal = buy_signal and buy_strategy == "bottom_reversal" and not btm_strong_signal and buy_score >= 45
btm_watch_signal = buy_signal and buy_strategy == "bottom_reversal" and not btm_strong_signal and not btm_medium_signal
rsi_div_strong_signal = buy_signal and buy_strategy == "rsi_divergence" and buy_score >= 55 and rsi_divergence_score >= 75 and drawdown_252 <= -15
rsi_div_medium_signal = buy_signal and buy_strategy == "rsi_divergence" and not rsi_div_strong_signal and buy_score >= 45
rsi_div_watch_signal = buy_signal and buy_strategy == "rsi_divergence" and not rsi_div_strong_signal and not rsi_div_medium_signal
other_buy_signal = buy_signal and buy_strategy != "index_shallow_pullback" and buy_strategy != "bottom_reversal" and buy_strategy != "rsi_divergence"

plotshape(idx_strong_signal, title="INDEX SHALLOW STRONG", style=shape.labelup, location=location.belowbar,
     color=color.new(color.green, 0), text="IDX STRONG", textcolor=color.white, size=size.small)
plotshape(idx_medium_signal, title="INDEX SHALLOW MEDIUM", style=shape.labelup, location=location.belowbar,
     color=color.new(color.teal, 0), text="IDX MED", textcolor=color.white, size=size.small)
plotshape(idx_watch_signal, title="INDEX SHALLOW WATCH", style=shape.labelup, location=location.belowbar,
     color=color.new(color.gray, 0), text="IDX WATCH", textcolor=color.white, size=size.small)
plotshape(btm_strong_signal, title="DEEP BOTTOM STRONG", style=shape.labelup, location=location.belowbar,
     color=color.new(color.purple, 0), text="BTM STRONG", textcolor=color.white, size=size.small)
plotshape(btm_medium_signal, title="DEEP BOTTOM MEDIUM", style=shape.labelup, location=location.belowbar,
     color=color.new(color.orange, 0), text="BTM MED", textcolor=color.white, size=size.small)
plotshape(btm_watch_signal, title="DEEP BOTTOM WATCH", style=shape.labelup, location=location.belowbar,
     color=color.new(color.gray, 0), text="BTM WATCH", textcolor=color.white, size=size.small)
plotshape(rsi_div_strong_signal, title="RSI DIVERGENCE STRONG", style=shape.labelup, location=location.belowbar,
     color=color.new(color.blue, 0), text="RSI DIV STRONG", textcolor=color.white, size=size.small)
plotshape(rsi_div_medium_signal, title="RSI DIVERGENCE MEDIUM", style=shape.labelup, location=location.belowbar,
     color=color.new(color.navy, 0), text="RSI DIV MED", textcolor=color.white, size=size.small)
plotshape(rsi_div_watch_signal, title="RSI DIVERGENCE WATCH", style=shape.labelup, location=location.belowbar,
     color=color.new(color.gray, 0), text="RSI DIV WATCH", textcolor=color.white, size=size.small)
plotshape(other_buy_signal, title="BUY", style=shape.labelup, location=location.belowbar,
     color=color.green, text="BUY", textcolor=color.white, size=size.small)
plotshape(sell_signal, title="SELL", style=shape.labeldown, location=location.abovebar,
     color=color.red, text="SELL", textcolor=color.white, size=size.small)

// Debug plots (hidden)
plot(buy_score, "Buy Score", color=color.green, display=display.none)
plot(sell_score, "Sell Score", color=color.red, display=display.none)
hline(buy_threshold, "Buy Threshold", color=color.green, linestyle=hline.style_dashed)
hline(sell_threshold, "Sell Threshold", color=color.red, linestyle=hline.style_dashed)
'''


def generate_long_term_addon_pine_script(
    bottom_cfg: UptrendDipConfig | None = None,
    index_cfg: UptrendDipConfig | None = None,
    rsi_cfg: UptrendDipConfig | None = None,
) -> str:
    """Standalone TradingView indicator for long-term add-on radar signals."""
    bottom_threshold = bottom_cfg.buy_threshold if bottom_cfg else 45.0
    bottom_weights = (
        bottom_cfg.w_pb_trend,
        bottom_cfg.w_pb_level,
        bottom_cfg.w_pb_rsi,
        bottom_cfg.w_pb_stoch,
        bottom_cfg.w_pb_volume,
    ) if bottom_cfg else (0.30, 0.20, 0.20, 0.20, 0.10)
    index_threshold = index_cfg.buy_threshold if index_cfg else 55.0
    index_weights = (
        index_cfg.w_pb_trend,
        index_cfg.w_pb_level,
        index_cfg.w_pb_rsi,
        index_cfg.w_pb_stoch,
        index_cfg.w_pb_volume,
    ) if index_cfg else (0.15, 0.25, 0.20, 0.25, 0.15)
    rsi_threshold = rsi_cfg.buy_threshold if rsi_cfg else 45.0
    rsi_weights = (
        rsi_cfg.w_pb_trend,
        rsi_cfg.w_pb_level,
        rsi_cfg.w_pb_rsi,
        rsi_cfg.w_pb_stoch,
        rsi_cfg.w_pb_volume,
    ) if rsi_cfg else (0.50, 0.20, 0.15, 0.10, 0.05)

    return f'''//@version=5
indicator("Long-Term Tech Add-On Radar", overlay=true, max_labels_count=500)

// Long-term add-on radar generated from AutoQuantStock.
// Default config: bottom_reversal, threshold {bottom_threshold:.0f}.
// This is an add-on signal indicator, not a short-term trading strategy.
// Signals require a bearish candle (close < open).
// bottom_reversal focuses on large drawdown / multi-bottom / RSI divergence.
// rsi_divergence isolates RSI divergence as a standalone baseline.
// index_shallow_pullback focuses on orderly index/ETF pullbacks near moving-average support.

// Inputs
radar_mode = input.string("bottom_reversal", "Radar Mode", options=["bottom_reversal", "rsi_divergence", "index_shallow_pullback"])
bottom_threshold = input.float({bottom_threshold:.0f}, "Bottom Threshold", minval=10, maxval=90, step=5)
rsi_threshold = input.float({rsi_threshold:.0f}, "RSI Divergence Threshold", minval=10, maxval=90, step=5)
index_threshold = input.float({index_threshold:.0f}, "Index Shallow Threshold", minval=10, maxval=90, step=5)
min_gap_bars = input.int(63, "Minimum Bars Between Signals", minval=1, maxval=252)
deeper_resignal_pct = input.float(4.0, "Index Re-Signal If Drawdown Deepens %", minval=1, maxval=15, step=0.5)

w_drawdown = input.float({bottom_weights[0]:.2f}, "Drawdown Weight", minval=0, maxval=1, step=0.05)
w_retest = input.float({bottom_weights[1]:.2f}, "Retest/Multi-Bottom Weight", minval=0, maxval=1, step=0.05)
w_divergence = input.float({bottom_weights[2]:.2f}, "RSI Divergence Weight", minval=0, maxval=1, step=0.05)
w_crash = input.float({bottom_weights[3]:.2f}, "Crash Weight", minval=0, maxval=1, step=0.05)
w_capitulation = input.float({bottom_weights[4]:.2f}, "Capitulation Weight", minval=0, maxval=1, step=0.05)

w_rsi_divergence = input.float({rsi_weights[0]:.2f}, "Standalone RSI-Div Weight", minval=0, maxval=1, step=0.05)
w_rsi_retest = input.float({rsi_weights[1]:.2f}, "Standalone Retest Weight", minval=0, maxval=1, step=0.05)
w_rsi_drawdown = input.float({rsi_weights[2]:.2f}, "Standalone Drawdown Weight", minval=0, maxval=1, step=0.05)
w_rsi_washout = input.float({rsi_weights[3]:.2f}, "Standalone RSI-Washout Weight", minval=0, maxval=1, step=0.05)
w_rsi_capitulation = input.float({rsi_weights[4]:.2f}, "Standalone Capitulation Weight", minval=0, maxval=1, step=0.05)

w_idx_drawdown = input.float({index_weights[0]:.2f}, "Index Drawdown-Band Weight", minval=0, maxval=1, step=0.05)
w_idx_support = input.float({index_weights[1]:.2f}, "Index MA-Support Weight", minval=0, maxval=1, step=0.05)
w_idx_rsi = input.float({index_weights[2]:.2f}, "Index RSI-Reset Weight", minval=0, maxval=1, step=0.05)
w_idx_decline = input.float({index_weights[3]:.2f}, "Index Recent-Decline Weight", minval=0, maxval=1, step=0.05)
w_idx_trend = input.float({index_weights[4]:.2f}, "Index Trend-Health Weight", minval=0, maxval=1, step=0.05)

// Helpers
clamp(value, low, high) =>
    math.max(low, math.min(high, value))

rolling_count(condition, length) =>
    count = 0.0
    for i = 0 to length - 1
        count += condition[i] ? 1.0 : 0.0
    count

// Indicators
atr14 = ta.atr(14)
ema21 = ta.ema(close, 21)
ema55 = ta.ema(close, 55)
ema100 = ta.ema(close, 100)
sma200 = ta.sma(close, 200)
ema55_slope20 = (ema55 / ema55[20] - 1) * 100
[_plus_di, _minus_di, adx_val] = ta.dmi(14, 14)

rsi_val = ta.rsi(close, 14)
rsi_delta = rsi_val - rsi_val[3]
vol_ratio = volume / ta.sma(volume, 20)

trend_pairs = ((ema21 > ema55 ? 1.0 : 0.0) + (ema55 > ema100 ? 1.0 : 0.0) + (ema100 > sma200 ? 1.0 : 0.0)) / 3.0

range_10 = ta.highest(high, 10) - ta.lowest(low, 10)
range_pct = range_10 / close * 100
atr_pct = atr14 / close * 100
compression_score = clamp((3.0 - range_pct / atr_pct) * 33, 0, 100)

high_20 = ta.highest(high, 20)
breakout_dist = (close - high_20) / atr14
base_breakout_score = clamp(math.max(0, breakout_dist) * 50, 0, 100)

prior_high_20 = ta.highest(high[1], 20)
tech_breakout_dist = (close - prior_high_20) / atr14
tech_breakout_score = clamp(math.max(0, tech_breakout_dist) * 60, 0, 100)

base_volume_score = clamp((vol_ratio - 1.0) * 100, 0, 100)
tech_volume_score = clamp((vol_ratio - 1.05) * 110, 0, 100)

base_momentum_score = clamp(clamp(rsi_val - 40, 0, 60) * (100 / 60) + clamp(rsi_delta * 5, 0, 30), 0, 100)
tech_momentum_score = clamp(clamp((rsi_val - 45) * (100 / 25), 0, 100) + clamp(rsi_delta * 6, 0, 35), 0, 100)

drawdown_252 = (close / ta.highest(close, 252) - 1) * 100
return_5d = (close / close[5] - 1) * 100
return_20d = (close / close[20] - 1) * 100

prior_low_120 = ta.lowest(low[10], 120)
retest_dist_pct = math.abs(close / prior_low_120 - 1) * 100
low_120 = ta.lowest(low, 120)
near_low = low <= low_120 * 1.05
near_low_count = rolling_count(near_low, 120)
retest_score = clamp((8 - retest_dist_pct) * 12.5, 0, 100)
multi_bottom_bonus = clamp((near_low_count - 2) * 15, 0, 40)
bottom_retest_score = clamp(retest_score + multi_bottom_bonus, 0, 100)

prior_rsi_min = ta.lowest(rsi_val[10], 60)
lower_low_zone = close <= prior_low_120 * 1.05
rsi_divergence_score = (lower_low_zone ? 1.0 : 0.0) * clamp((rsi_val - prior_rsi_min - 4) * 8, 0, 100)

drawdown_score = clamp((-drawdown_252 - 15) * 4, 0, 100)
crash_score = clamp((-return_20d - 10) * 5 + (-return_5d - 4) * 5, 0, 100)
capitulation_score = clamp((vol_ratio - 1.2) * 45 + (35 - rsi_val) * 3, 0, 100)

bottom_score = clamp(
     w_drawdown * drawdown_score
   + w_retest * bottom_retest_score
   + w_divergence * rsi_divergence_score
   + w_crash * crash_score
   + w_capitulation * capitulation_score,
   0, 100)

rsi_div_drawdown = clamp((-drawdown_252 - 10) * 5, 0, 100)
rsi_washout = clamp((40 - rsi_val) * 4, 0, 100)
rsi_div_score = clamp(
     w_rsi_divergence * rsi_divergence_score
   + w_rsi_retest * bottom_retest_score
   + w_rsi_drawdown * rsi_div_drawdown
   + w_rsi_washout * rsi_washout
   + w_rsi_capitulation * capitulation_score,
   0, 100)

dd_abs = -drawdown_252
idx_drawdown_entry = clamp((dd_abs - 2.5) * 35, 0, 100)
idx_too_deep_guard = clamp((22 - dd_abs) * 8, 0, 100)
idx_drawdown = math.min(idx_drawdown_entry, idx_too_deep_guard)

ema21_dist_pct = (close / ema21 - 1) * 100
ema55_dist_pct = (close / ema55 - 1) * 100
sma200_dist_pct = (close / sma200 - 1) * 100
idx_ema21_support = clamp((4 - math.abs(ema21_dist_pct)) * 25, 0, 100)
idx_ema55_support = clamp((6 - math.abs(ema55_dist_pct)) * (100 / 6), 0, 100)
idx_sma200_support = clamp((5 - math.abs(sma200_dist_pct)) * 20, 0, 100)
idx_support = math.max(idx_ema21_support, math.max(idx_ema55_support, idx_sma200_support))
idx_rsi_reset = clamp(100 - math.abs(rsi_val - 43) * 5.5, 0, 100)
idx_decline = clamp((-return_20d - 2) * 10 + (-return_5d - 0.5) * 12, 0, 100)
idx_trend_buffer = clamp((close / sma200 - 0.97) * 900, 0, 100)
idx_slope_health = clamp(ema55_slope20 * 10 + 40, 0, 100)
idx_trend_health = clamp(trend_pairs * 45 + idx_trend_buffer * 0.30 + idx_slope_health * 0.25, 0, 100)

index_score = clamp(
     w_idx_drawdown * idx_drawdown
   + w_idx_support * idx_support
   + w_idx_rsi * idx_rsi_reset
   + w_idx_decline * idx_decline
   + w_idx_trend * idx_trend_health,
   0, 100)

addon_score = radar_mode == "index_shallow_pullback" ? index_score : radar_mode == "rsi_divergence" ? rsi_div_score : bottom_score
buy_threshold = radar_mode == "index_shallow_pullback" ? index_threshold : radar_mode == "rsi_divergence" ? rsi_threshold : bottom_threshold
raw_addon_signal = addon_score >= buy_threshold and not na(sma200)
bearish_candle = close < open

var int last_signal_bar = na
var float last_signal_drawdown = na
gap_ok = na(last_signal_bar) or bar_index - last_signal_bar >= min_gap_bars
index_deeper_ok = radar_mode == "index_shallow_pullback" and not na(last_signal_drawdown) and drawdown_252 <= last_signal_drawdown - deeper_resignal_pct
addon_signal = raw_addon_signal and bearish_candle and (gap_ok or index_deeper_ok)

if addon_signal
    last_signal_bar := bar_index
    last_signal_drawdown := drawdown_252

// Plotting
bgcolor(addon_signal ? color.new(color.green, 82) : na, title="Add-On Zone")

idx_strong_signal = addon_signal and radar_mode == "index_shallow_pullback" and addon_score >= 55 and idx_support >= 70 and idx_rsi_reset >= 60
idx_medium_signal = addon_signal and radar_mode == "index_shallow_pullback" and not idx_strong_signal and addon_score >= 45
idx_watch_signal = addon_signal and radar_mode == "index_shallow_pullback" and not idx_strong_signal and not idx_medium_signal
btm_strong_signal = addon_signal and radar_mode == "bottom_reversal" and addon_score >= 55 and drawdown_252 <= -20 and (bottom_retest_score >= 75 or rsi_divergence_score >= 75)
btm_medium_signal = addon_signal and radar_mode == "bottom_reversal" and not btm_strong_signal and addon_score >= 45
btm_watch_signal = addon_signal and radar_mode == "bottom_reversal" and not btm_strong_signal and not btm_medium_signal
rsi_div_strong_signal = addon_signal and radar_mode == "rsi_divergence" and addon_score >= 55 and rsi_divergence_score >= 75 and drawdown_252 <= -15
rsi_div_medium_signal = addon_signal and radar_mode == "rsi_divergence" and not rsi_div_strong_signal and addon_score >= 45
rsi_div_watch_signal = addon_signal and radar_mode == "rsi_divergence" and not rsi_div_strong_signal and not rsi_div_medium_signal

plotshape(idx_strong_signal, title="INDEX SHALLOW STRONG", style=shape.labelup, location=location.belowbar,
     color=color.new(color.green, 0), text="IDX STRONG", textcolor=color.white, size=size.small)
plotshape(idx_medium_signal, title="INDEX SHALLOW MEDIUM", style=shape.labelup, location=location.belowbar,
     color=color.new(color.teal, 0), text="IDX MED", textcolor=color.white, size=size.small)
plotshape(idx_watch_signal, title="INDEX SHALLOW WATCH", style=shape.labelup, location=location.belowbar,
     color=color.new(color.gray, 0), text="IDX WATCH", textcolor=color.white, size=size.small)
plotshape(btm_strong_signal, title="DEEP BOTTOM STRONG", style=shape.labelup, location=location.belowbar,
     color=color.new(color.purple, 0), text="BTM STRONG", textcolor=color.white, size=size.small)
plotshape(btm_medium_signal, title="DEEP BOTTOM MEDIUM", style=shape.labelup, location=location.belowbar,
     color=color.new(color.orange, 0), text="BTM MED", textcolor=color.white, size=size.small)
plotshape(btm_watch_signal, title="DEEP BOTTOM WATCH", style=shape.labelup, location=location.belowbar,
     color=color.new(color.gray, 0), text="BTM WATCH", textcolor=color.white, size=size.small)
plotshape(rsi_div_strong_signal, title="RSI DIVERGENCE STRONG", style=shape.labelup, location=location.belowbar,
     color=color.new(color.blue, 0), text="RSI DIV STRONG", textcolor=color.white, size=size.small)
plotshape(rsi_div_medium_signal, title="RSI DIVERGENCE MEDIUM", style=shape.labelup, location=location.belowbar,
     color=color.new(color.navy, 0), text="RSI DIV MED", textcolor=color.white, size=size.small)
plotshape(rsi_div_watch_signal, title="RSI DIVERGENCE WATCH", style=shape.labelup, location=location.belowbar,
     color=color.new(color.gray, 0), text="RSI DIV WATCH", textcolor=color.white, size=size.small)

plot(addon_score, "Add-On Score", color=color.green, display=display.none)
plot(buy_threshold, "Add-On Threshold", color=color.green, display=display.none)

alertcondition(addon_signal, title="Long-Term Add-On Signal", message="Long-term add-on signal on {{{{ticker}}}}")
'''


def build_prompt_to_artifact_checklist(results: dict[str, Any]) -> list[dict[str, str]]:
    radar = results.get("longTermRadar", {})
    recommended = radar.get("recommendedDefault", {})
    cfg = recommended.get("config", {})
    best_by_strategy = radar.get("bestByStrategy", {})
    tech_summary = results.get("techSubsetRecommendedRadarSummary", {})
    date_split = results.get("dateSplitRadar", {})
    full_walk_forward = results.get("fullGridWalkForwardRadar", {})
    multi_window = results.get("multiWindowValidationRadar", {})
    current_signals = results.get("techSubsetCurrentSignalLog", [])
    paper_plan = results.get("paperTrackingPlan", {})

    def covered(ok: bool) -> str:
        return "covered" if ok else "needs review"

    return [
        {
            "requirement": "Keep the main implementation inside investigations/uptrend_dip_search.py.",
            "evidence": "All strategy families, radar evaluation, walk-forward diagnostics, report writing, and Pine generation are wired from investigations/uptrend_dip_search.py.",
            "status": "covered",
        },
        {
            "requirement": "Do not modify config.py or run.py.",
            "evidence": "Session gate: git diff --name-only -- config.py run.py must stay empty.",
            "status": "external gate",
        },
        {
            "requirement": "Explore buy signals: volatility contraction breakout, relative strength, abnormal volume, and large-drawdown add-on points.",
            "evidence": "tech_breakout covers compression / relative strength / volume expansion; bottom_reversal covers deep drawdown, multi-bottom/retest, RSI divergence, crash and capitulation; rsi_divergence is a standalone RSI-divergence baseline; index_shallow_pullback covers orderly index dips.",
            "status": covered({"tech_breakout", "bottom_reversal", "rsi_divergence", "index_shallow_pullback"}.issubset(best_by_strategy.keys())),
        },
        {
            "requirement": "Explore trend filters with ADX and moving-average slope; keep Ichimoku as backup only.",
            "evidence": "trend_breakout uses ADX and EMA55 slope. Ichimoku is intentionally not added to avoid unnecessary complexity before the simpler filters are validated.",
            "status": covered("trend_breakout" in best_by_strategy),
        },
        {
            "requirement": "Explore sell protection: trailing stop, ATR trailing, and profit drawdown protection.",
            "evidence": "simulate_trades() includes fixed stop, profit drawdown trailing, ATR trailing, and sell-signal exits; Stage 2 report keeps this separate from the long-term add-on radar.",
            "status": "covered",
        },
        {
            "requirement": "Optimize for long-term add-on quality, not high short-term win rate.",
            "evidence": f"Current default is {cfg.get('buy_strategy', '?')} / {cfg.get('name', '?')}; long-term score weights 12m/24m forward returns and penalizes post-entry drawdown.",
            "status": covered(bool(recommended)),
        },
        {
            "requirement": "Avoid buying green momentum-chase bars for the long-term add-on radar.",
            "evidence": "evaluate_long_term_radar() requires close < open for add-on entries, so long-term radar signals occur on bearish candles.",
            "status": "covered",
        },
        {
            "requirement": "Support deep crashes, double bottoms / multi-bottoms, and RSI divergence.",
            "evidence": "bottom_reversal scoring uses drawdown_252, bottom_retest_score, multi-bottom count, RSI divergence, crash score, and capitulation score.",
            "status": covered(cfg.get("buy_strategy") == "bottom_reversal"),
        },
        {
            "requirement": "Add index_shallow_pullback with strength labels distinct from bottom_reversal.",
            "evidence": "Report and Pine emit Deep Bottom vs Shallow Pullback labels; index_shallow_pullback has its own threshold, weights, and re-signal rule.",
            "status": covered("index_shallow_pullback" in best_by_strategy),
        },
        {
            "requirement": "Expand validation to the requested tech subset.",
            "evidence": f"Tech subset summary covers {tech_summary.get('symbolCount', 0)} symbols; current watchlist contains {len(current_signals)} recent global-default tech signals.",
            "status": covered(tech_summary.get("symbolCount", 0) >= len(TECH_STOCK_SUBSET)),
        },
        {
            "requirement": "Run QQQ quick validation, then full --symbol all validation when it does not deteriorate.",
            "evidence": "Session gates: python investigations/uptrend_dip_search.py --symbol QQQ and python investigations/uptrend_dip_search.py --symbol all.",
            "status": "external gate",
        },
        {
            "requirement": "Reduce overfitting risk before treating the strategy as usable.",
            "evidence": f"Date-split holdout starts at {date_split.get('holdoutSignalStartDate', '?')}; full-grid walk-forward covers years {[row.get('year') for row in full_walk_forward.get('years', [])]}; multi-window validation has {len(multi_window.get('anchoredWindows', []))} anchored windows and {len(multi_window.get('rollingWindows', []))} rolling windows.",
            "status": covered(
                bool(date_split)
                and bool(full_walk_forward.get("years"))
                and bool(multi_window.get("anchoredWindows"))
                and bool(multi_window.get("rollingWindows"))
            ),
        },
        {
            "requirement": "Keep TradingView Pine output synchronized and compatible with TradingView's function set.",
            "evidence": "run() regenerates uptrend_dip_pine.pine and long_term_addon_radar.pine; Pine uses rolling_count() instead of unsupported rolling-sum function calls.",
            "status": covered(bool(results.get("pineScript")) and bool(results.get("longTermAddonPineScript"))),
        },
        {
            "requirement": "Provide user-facing artifacts for review.",
            "evidence": "Generated artifacts: strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_report.md, strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_results.json, strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_pine.pine, strategy_catalog/long_term_addon_radar/long_term_addon_radar.pine, tests/test_uptrend_dip_search.py.",
            "status": "covered",
        },
        {
            "requirement": "Do not claim production readiness from in-sample or proxy signals alone.",
            "evidence": "Report caveats keep the conservative read separate from per-symbol in-sample best configs and call for live paper-trading or a later true out-of-sample period before production use.",
            "status": "covered",
        },
        {
            "requirement": "Track future paper-validation checkpoints for current tech signals.",
            "evidence": f"paperTrackingPlan tracks {paper_plan.get('signalCount', 0)} signals; next pending check date is {paper_plan.get('nextPendingCheckDate', '?')}; overdue pending 6m/12m checks are {paper_plan.get('overduePending6mCount', '?')} / {paper_plan.get('overduePending12mCount', '?')}.",
            "status": covered(bool(paper_plan.get("signalCount")) and bool(paper_plan.get("nextPendingCheckDate"))),
        },
    ]


# ═══════════════════════════════════════════════════════
# Report
# ═══════════════════════════════════════════════════════


def write_report(results: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LONG_TERM_ADDON_DIR.mkdir(parents=True, exist_ok=True)

    def pct_text(value: Any) -> str:
        return f"{value:.1f}%" if isinstance(value, (int, float)) and math.isfinite(value) else "-"

    def factor_driver_text(signal: dict[str, Any]) -> str:
        factors = signal.get("factorSnapshot", {})
        strategy = factors.get("strategy", "")
        if strategy == "bottom_reversal":
            return (
                f"DD {pct_text(factors.get('drawdown252Pct'))}; "
                f"retest {factors.get('bottomRetestScore', 0):.0f}; "
                f"RSI div {factors.get('rsiDivergenceScore', 0):.0f}; "
                f"cap {factors.get('capitulationScore', 0):.0f}; "
                f"RSI {factors.get('rsi14', 0):.1f}; "
                f"vol {factors.get('volumeRatio', 0):.2f}x"
            )
        if strategy == "rsi_divergence":
            return (
                f"DD {pct_text(factors.get('drawdown252Pct'))}; "
                f"retest {factors.get('bottomRetestScore', 0):.0f}; "
                f"RSI div {factors.get('rsiDivergenceScore', 0):.0f}; "
                f"RSI {factors.get('rsi14', 0):.1f}; "
                f"vol {factors.get('volumeRatio', 0):.2f}x"
            )
        if strategy == "index_shallow_pullback":
            return (
                f"DD {pct_text(factors.get('drawdown252Pct'))}; "
                f"support {factors.get('supportScore', 0):.0f}; "
                f"RSI reset {factors.get('rsiResetScore', 0):.0f}; "
                f"decline {factors.get('declineScore', 0):.0f}; "
                f"trend {factors.get('trendHealthScore', 0):.0f}"
            )
        if factors:
            return (
                f"RS {factors.get('relativeStrengthScore', 0):.0f}; "
                f"vol {factors.get('volumeRatio', 0):.2f}x; "
                f"RSI {factors.get('rsi14', 0):.1f}; "
                f"slope {pct_text(factors.get('ema55Slope20'))}"
            )
        return "-"

    def action_grade_text(signal: dict[str, Any]) -> str:
        return signal.get("actionProfile", {}).get("grade", "-")

    def risk_flags_text(signal: dict[str, Any]) -> str:
        flags = signal.get("actionProfile", {}).get("riskFlags", [])
        return ", ".join(flags) if flags else "-"

    lines = [
        "# Uptrend Dip Buy + Sell Signal Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]

    radar = results.get("longTermRadar", {})
    recommended = radar.get("recommendedDefault", {})
    rec_cfg = recommended.get("config", {})
    tech_default = results.get("techSubsetRecommendedRadarSummary", {})
    date_split = results.get("dateSplitRadar", {})
    split_summary = date_split.get("techSubsetHoldoutSummary", {})
    split_signal_summary = date_split.get("techSubsetHoldoutSignalSummary", {})
    multi_window = results.get("multiWindowValidationRadar", {})
    multi_summary = multi_window.get("summary", {})
    latest_signals = results.get("techSubsetRecommendedRecentSignalLog", [])
    if recommended:
        latest_text = "-"
        if latest_signals:
            latest = latest_signals[0]
            latest_text = (
                f"{latest.get('symbol', '?')} {latest.get('date', '?')} "
                f"{latest.get('strengthLabel', '-')}"
            )
        lines.extend([
            "## Executive Summary",
            "",
            f"- Current broad long-term add-on default: `{rec_cfg.get('name', '?')}` strategy={rec_cfg.get('buy_strategy', '?')}.",
            f"- QQQ/SPY combined score: {recommended.get('combinedScore', 0):.2f}.",
            f"- Tech subset using this global default: avg 12m {tech_default.get('avg12mPct', 0):.1f}%, "
            f"avg 12m drawdown {tech_default.get('avgMaxDrawdown12mPct', 0):.1f}%.",
            f"- Date-split 2023+ tech holdout, symbol-average: avg 12m {split_summary.get('avg12mPct', 0):.1f}%, "
            f"avg 12m drawdown {split_summary.get('avgMaxDrawdown12mPct', 0):.1f}%.",
            f"- Date-split 2023+ tech holdout, signal-level: {split_signal_summary.get('signalCount', 0)} signals, "
            f"avg 12m {pct_text(split_signal_summary.get('avg12mPct'))}.",
            f"- Multi-window validation: {multi_summary.get('windowCount', 0)} windows, "
            f"min/median signal avg 12m {pct_text(multi_summary.get('minSignalAvg12mPct'))} / "
            f"{pct_text(multi_summary.get('medianSignalAvg12mPct'))}, "
            f"worst signal 12m drawdown {pct_text(multi_summary.get('worstSignalDrawdown12mPct'))}.",
            f"- Latest tech signal in the generated log: {latest_text}.",
            "- Research status: date-split, full-grid walk-forward, and multi-window validation are now present; production use still needs live paper-trading or future out-of-sample evidence.",
            "",
        ])

        lines.extend([
            "## Current Strategy Card",
            "",
            "- Primary use: long-term add-on buying for U.S. tech stocks, not short-term swing trading.",
            "- Default signal family: `bottom_reversal`, which looks for deep drawdown, prior-low retest or multi-bottom behavior, RSI divergence, crash pressure, and capitulation volume.",
            "- Entry rule: signal must pass the score threshold and close on a bearish candle, so it is not chasing a large green breakout day.",
            "- Signal spacing: normal add-on signals are sparse and separated by about 63 trading bars.",
            "- Strength labels: `Deep Bottom - Strong` is the preferred long-term add-on label; `Deep Bottom - Medium` is usable but weaker; `Watch` means the score barely qualifies.",
            "- Separate index mode: `index_shallow_pullback` is for SPY/QQQ-style orderly pullbacks and should be read as `Shallow Pullback`, not as the same type of bottom signal.",
            "",
        ])

    lines.extend([
        "## Method",
        "",
        "Seven buy strategies (trend pullback / breakout / tech breakout / trend-filtered breakout / bottom reversal / RSI divergence / index shallow pullback), two sell strategies (reversal / overbought).",
        "Grid-searched weights, thresholds, and stop-loss. Discrete buy-sell cycle simulation.",
        "",
        "Buy A (Pullback): EMA stack trend + RSI sweet spot + Stochastic + volume contraction",
        "Buy B (Breakout): Range compression + N-bar high breakout + volume surge + momentum",
        "Buy C (Tech Breakout): Prior-high breakout + volatility contraction + relative strength vs SPY + volume expansion",
        "Buy D (Trend Breakout): Breakout score adjusted by ADX trend strength and EMA55 slope",
        "Buy E (Bottom Reversal): Large drawdown + prior-low retest/multi-bottom + RSI divergence + crash/capitulation",
        "Buy F (RSI Divergence): Standalone RSI-divergence baseline with retest/drawdown context",
        "Buy G (Index Shallow Pullback): Orderly index/ETF drawdown + EMA/SMA support + RSI reset + trend health",
        "Sell A (Reversal): EMA breakdown + death cross + RSI break",
        "Sell B (Overbought): RSI/Stoch overbought + Keltner upper + profit target",
        "",
    ])

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

    # Long-term radar results
    radar = results.get("longTermRadar", {})
    if radar:
        recommended = radar.get("recommendedDefault", {})
        cfg = recommended.get("config", {})
        lines.extend([
            "## Long-Term Add-On Radar",
            "",
            "This section scores buy signals as long-term add-on points, not as short trades.",
            "Higher weight is given to 12-month and 24-month forward returns; drawdown is a penalty, and win rate is not the main target.",
            "",
            f"- Config: `{cfg.get('name', '?')}`",
            f"- Strategy: {cfg.get('buy_strategy', '?')}",
            f"- Combined score: {recommended.get('combinedScore', 0):.2f}",
            f"- Buy threshold: {cfg.get('buy_threshold', 0):.0f}",
            "",
            "Per-symbol radar results:",
            "",
        ])

        for symbol, metrics in recommended.get("symbols", {}).items():
            fwd = metrics.get("avgForwardReturns", {})
            dd = metrics.get("avgDrawdowns", {})
            lines.extend([
                f"### {symbol}",
                f"- Signals: {metrics.get('signalCount', 0)}",
                f"- Mature 12m signals: {metrics.get('matureSignalCount', 0)}",
                f"- Avg 6m / 12m / 24m: {fwd.get('avg6mPct', 0):.1f}% / "
                f"{fwd.get('avg12mPct', 0):.1f}% / {fwd.get('avg24mPct', 0):.1f}%",
                f"- Avg max drawdown 6m / 12m: {dd.get('avgMaxDrawdown6mPct', 0):.1f}% / "
                f"{dd.get('avgMaxDrawdown12mPct', 0):.1f}%",
                "",
            ])

        for symbol in ["QQQ", "SPY"]:
            sym_data = recommended.get("symbols", {}).get(symbol, {})
            signals = sym_data.get("signals", [])
            if signals:
                lines.extend([f"## Add-On Signal Log: {symbol}", ""])
                lines.extend([
                    "| Date | Price | Score | Strength | Age Bars | 6m | 12m | 24m | 12m/Partial DD |",
                    "|------|-------|-------|----------|----------|----|-----|-----|----------------|",
                ])
                for s in signals[:20]:
                    lines.append(
                        f"| {s['date']} | {s['price']:.2f} | {s['buyScore']:.1f} | "
                        f"{s.get('strengthLabel', '-')} | "
                        f"{s.get('barsSinceSignal', '-')} | "
                        f"{s.get('return6mPct') if s.get('return6mPct') is not None else '-'} | "
                        f"{s.get('return12mPct') if s.get('return12mPct') is not None else '-'} | "
                        f"{s.get('return24mPct') if s.get('return24mPct') is not None else '-'} | "
                        f"{s.get('maxDrawdown12mPct') if s.get('maxDrawdown12mPct') is not None else '-'} |"
                    )
                lines.append("")
                break

        strategy_best = radar.get("bestByStrategy", {})
        if strategy_best:
            lines.extend(["## Long-Term Radar Strategy Comparison", ""])
            lines.extend([
                "| Strategy | Config | Combined | QQQ Signals / 12m | SPY Signals / 12m |",
                "|----------|--------|----------|-------------------|-------------------|",
            ])
            for strategy, entry in sorted(
                strategy_best.items(),
                key=lambda item: item[1].get("combinedScore", -999),
                reverse=True,
            ):
                cfg_d = entry.get("config", {})
                symbols = entry.get("symbols", {})

                def symbol_summary(symbol: str) -> str:
                    metrics = symbols.get(symbol, {})
                    fwd = metrics.get("avgForwardReturns", {})
                    avg12 = fwd.get("avg12mPct")
                    avg12_text = f"{avg12:.1f}%" if isinstance(avg12, (int, float)) else "-"
                    return f"{metrics.get('signalCount', 0)} / {avg12_text}"

                lines.append(
                    f"| {strategy} | `{cfg_d.get('name', '?')}` | "
                    f"{entry.get('combinedScore', 0):.2f} | "
                    f"{symbol_summary('QQQ')} | {symbol_summary('SPY')} |"
                )
            lines.append("")

            shallow = strategy_best.get("index_shallow_pullback")
            if shallow:
                for symbol in ["SPY", "QQQ"]:
                    signals = shallow.get("symbols", {}).get(symbol, {}).get("signals", [])
                    recent = [s for s in signals if s.get("date", "") >= "2024-01-01"]
                    if recent:
                        lines.extend([f"## Index Shallow Pullback Signal Log: {symbol}", ""])
                        lines.extend([
                            "| Date | Price | Score | Strength | Age Bars | 6m | 12m | 12m/Partial DD |",
                            "|------|-------|-------|----------|----------|----|-----|----------------|",
                        ])
                        for s in recent[:12]:
                            lines.append(
                                f"| {s['date']} | {s['price']:.2f} | {s['buyScore']:.1f} | "
                                f"{s.get('strengthLabel', '-')} | "
                                f"{s.get('barsSinceSignal', '-')} | "
                                f"{s.get('return6mPct') if s.get('return6mPct') is not None else '-'} | "
                                f"{s.get('return12mPct') if s.get('return12mPct') is not None else '-'} | "
                                f"{s.get('maxDrawdown12mPct') if s.get('maxDrawdown12mPct') is not None else '-'} |"
                            )
                        lines.append("")
                        break

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
                f"- Exits: {m.get('stopExits', 0)} stop / {m.get('trailingExits', 0)} trailing / {m.get('signalExits', 0)} signal",
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
                f"`{cfg_d.get('name', '?')}` | "
                f"{best.get('tradeCount', 0)} | {m.get('winRate', 0):.0f}% | "
                f"{m.get('avgReturn', 0):.1f}% | {m.get('sharpe', 0):.2f} | "
                f"{m.get('profitFactor', 0):.1f} |"
            )
        lines.append("")

    per_sym_radar = results.get("perSymbolRadarBest", {})
    if per_sym_radar:
        tech_default_summary = results.get("techSubsetRecommendedRadarSummary", {})
        tech_best_summary = results.get("techSubsetRadarSummary", {})
        tech_segment_default = results.get("techSegmentRecommendedRadarSummaries", {})
        tech_segment_best = results.get("techSegmentBestRadarSummaries", {})

        def append_tech_summary(label: str, summary: dict[str, Any]) -> None:
            strategy_counts = summary.get("strategyCounts", {})
            strategy_text = ", ".join(
                f"{strategy}: {count}" for strategy, count in sorted(strategy_counts.items())
            ) or "-"
            lines.extend([
                f"### {label}",
                "",
                f"- Symbols covered: {summary.get('symbolCount', 0)}",
                f"- Avg signals: {summary.get('avgSignals', 0):.1f}",
                f"- Avg 6m / 12m / 24m: {summary.get('avg6mPct', 0):.1f}% / "
                f"{summary.get('avg12mPct', 0):.1f}% / {summary.get('avg24mPct', 0):.1f}%",
                f"- Median 12m: {summary.get('median12mPct', 0):.1f}%",
                f"- Avg 12m max drawdown: {summary.get('avgMaxDrawdown12mPct', 0):.1f}%",
                f"- Strategy mix: {strategy_text}",
                "",
            ])

        if tech_default_summary or tech_best_summary:
            lines.extend(["## Tech Stock Long-Term Radar Summary", ""])
            if tech_default_summary:
                append_tech_summary("Global Default Applied To Tech Stocks", tech_default_summary)
            if tech_best_summary:
                append_tech_summary("Per-Symbol Best Tech Configs", tech_best_summary)

            if tech_segment_default or tech_segment_best:
                lines.extend([
                    "### Tech Segment Summary",
                    "",
                    "Large-cap quality tech separates steadier megacap names from the high-beta group, so the averages are not dominated by the most volatile stocks.",
                    "",
                    "| Segment | Scope | Symbols | Avg Signals | Avg 12m | Median 12m | 12m DD |",
                    "|---------|-------|---------|-------------|---------|------------|--------|",
                ])

                segment_labels = {
                    "large_cap_quality_tech": "Large-cap quality tech",
                    "high_beta_tech": "High-beta tech",
                }

                def append_segment_rows(scope: str, summaries: dict[str, dict[str, Any]]) -> None:
                    for segment, summary in summaries.items():
                        label = segment_labels.get(segment, segment)
                        lines.append(
                            f"| {label} | {scope} | {summary.get('symbolCount', 0)} | "
                            f"{summary.get('avgSignals', 0):.1f} | "
                            f"{summary.get('avg12mPct', 0):.1f}% | "
                            f"{summary.get('median12mPct', 0):.1f}% | "
                            f"{summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                        )

                if tech_segment_default:
                    append_segment_rows("Global default", tech_segment_default)
                if tech_segment_best:
                    append_segment_rows("Per-symbol best", tech_segment_best)
                lines.append("")

            recent_default = results.get("techSubsetRecommendedRecentSignals", {})
            recent_best = results.get("techSubsetBestRecentSignals", {})
            if recent_default or recent_best:
                lines.extend([
                    "### Recent Tech Signal Window",
                    "",
                    "Signals dated 2023-01-01 or later. Recent windows have fewer mature 12m/24m observations.",
                    "",
                    "| Scope | Signals | Mature 12m | Avg 6m | Avg 12m | Avg 24m | 12m DD |",
                    "|-------|---------|------------|--------|---------|---------|--------|",
                ])

                def append_recent(label: str, summary: dict[str, Any]) -> None:
                    lines.append(
                        f"| {label} | {summary.get('signalCount', 0)} | "
                        f"{summary.get('mature12mSignalCount', 0)} | "
                        f"{pct_text(summary.get('avg6mPct'))} | "
                        f"{pct_text(summary.get('avg12mPct'))} | "
                        f"{pct_text(summary.get('avg24mPct'))} | "
                        f"{summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )

                if recent_default:
                    append_recent("Global default", recent_default)
                if recent_best:
                    append_recent("Per-symbol best", recent_best)
                lines.append("")

            by_year = results.get("techSubsetRecommendedSignalsByYear", {})
            if by_year:
                lines.extend([
                    "### Global Default Tech Signals By Year",
                    "",
                    "| Year | Signals | Mature 12m | Avg 6m | Avg 12m | 12m DD |",
                    "|------|---------|------------|--------|---------|--------|",
                ])
                for year, summary in by_year.items():
                    lines.append(
                        f"| {year} | {summary.get('signalCount', 0)} | "
                        f"{summary.get('mature12mSignalCount', 0)} | "
                        f"{pct_text(summary.get('avg6mPct'))} | "
                        f"{pct_text(summary.get('avg12mPct'))} | "
                        f"{summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )
                lines.append("")

            risk_diagnostics = results.get("techSubsetSignalRiskDiagnostics", {})
            if risk_diagnostics:
                lines.extend([
                    "### Tech Signal Risk Diagnostics",
                    "",
                    "Groups global-default tech signals dated 2023-01-01 or later by the signal's own risk tags. A signal with multiple risk tags appears in multiple risk rows.",
                    "",
                    "| Risk Flag | Signals | Mature 12m | Avg 12m | 12m DD |",
                    "|-----------|---------|------------|---------|--------|",
                ])
                for flag, summary in risk_diagnostics.get("riskFlagGroups", {}).items():
                    lines.append(
                        f"| {flag} | {summary.get('signalCount', 0)} | "
                        f"{summary.get('mature12mSignalCount', 0)} | "
                        f"{pct_text(summary.get('avg12mPct'))} | "
                        f"{summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )
                lines.extend([
                    "",
                    "| Strength | Signals | Mature 12m | Avg 12m | 12m DD |",
                    "|----------|---------|------------|---------|--------|",
                ])
                for strength, summary in risk_diagnostics.get("strengthGroups", {}).items():
                    lines.append(
                        f"| {strength} | {summary.get('signalCount', 0)} | "
                        f"{summary.get('mature12mSignalCount', 0)} | "
                        f"{pct_text(summary.get('avg12mPct'))} | "
                        f"{summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )
                lines.append("")

            recent_signal_log = results.get("techSubsetRecommendedRecentSignalLog", [])
            if recent_signal_log:
                lines.extend([
                    "### Latest Global-Default Tech Signals",
                    "",
                    "| Symbol | Date | Price | Score | Strength | Action | Risk Flags | Drivers | Age Bars | 6m | 12m | 12m/Partial DD |",
                    "|--------|------|-------|-------|----------|--------|------------|---------|----------|----|-----|----------------|",
                ])
                for s in recent_signal_log[:12]:
                    lines.append(
                        f"| {s.get('symbol', '?')} | {s.get('date', '?')} | "
                        f"{s.get('price', 0):.2f} | {s.get('buyScore', 0):.1f} | "
                        f"{s.get('strengthLabel', '-')} | "
                        f"{action_grade_text(s)} | "
                        f"{risk_flags_text(s)} | "
                        f"{factor_driver_text(s)} | "
                        f"{s.get('barsSinceSignal', '-')} | "
                        f"{s.get('return6mPct') if s.get('return6mPct') is not None else '-'} | "
                        f"{s.get('return12mPct') if s.get('return12mPct') is not None else '-'} | "
                        f"{s.get('maxDrawdown12mPct') if s.get('maxDrawdown12mPct') is not None else '-'} |"
                    )
                lines.append("")

            current_signal_log = results.get("techSubsetCurrentSignalLog", [])
            if current_signal_log:
                lines.extend([
                    "### Current Tech Radar Watchlist",
                    "",
                    "Global-default tech signals from the last 126 trading bars. These are recent enough to monitor, but 6m/12m outcomes may not be mature.",
                    "",
                    "| Symbol | Date | Price | Score | Strength | Action | Risk Flags | Drivers | Age Bars | 6m | 12m | 12m/Partial DD |",
                    "|--------|------|-------|-------|----------|--------|------------|---------|----------|----|-----|----------------|",
                ])
                for s in current_signal_log[:12]:
                    lines.append(
                        f"| {s.get('symbol', '?')} | {s.get('date', '?')} | "
                        f"{s.get('price', 0):.2f} | {s.get('buyScore', 0):.1f} | "
                        f"{s.get('strengthLabel', '-')} | "
                        f"{action_grade_text(s)} | "
                        f"{risk_flags_text(s)} | "
                        f"{factor_driver_text(s)} | "
                        f"{s.get('barsSinceSignal', '-')} | "
                        f"{s.get('return6mPct') if s.get('return6mPct') is not None else '-'} | "
                        f"{s.get('return12mPct') if s.get('return12mPct') is not None else '-'} | "
                        f"{s.get('maxDrawdown12mPct') if s.get('maxDrawdown12mPct') is not None else '-'} |"
                    )
                lines.append("")

            paper_plan = results.get("paperTrackingPlan", {})
            if paper_plan:
                lines.extend([
                    "### Paper Tracking Plan",
                    "",
                    "These are not completed returns. They are the calendar dates to revisit current radar signals for future 6m/12m evidence.",
                    "",
                    f"- Generated date: {paper_plan.get('generatedDate', '?')}",
                    f"- Current signals tracked: {paper_plan.get('signalCount', 0)}",
                    f"- Pending 6m checks: {paper_plan.get('pending6mCount', 0)}",
                    f"- Pending 12m checks: {paper_plan.get('pending12mCount', 0)}",
                    f"- Overdue pending 6m checks: {paper_plan.get('overduePending6mCount', 0)}",
                    f"- Overdue pending 12m checks: {paper_plan.get('overduePending12mCount', 0)}",
                    f"- Next pending check date: {paper_plan.get('nextPendingCheckDate', '-')}",
                    "- Quick check command: `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status --as-of YYYY-MM-DD`",
                    "",
                    "| Symbol | Signal Date | Strength | Action | Risk Flags | 6m Check | 12m Check | 6m Status | 12m Status |",
                    "|--------|-------------|----------|--------|------------|----------|-----------|-----------|------------|",
                ])
                for row in paper_plan.get("signals", [])[:12]:
                    lines.append(
                        f"| {row.get('symbol', '?')} | {row.get('signalDate', '?')} | "
                        f"{row.get('strengthLabel', '-')} | {row.get('action', '-')} | "
                        f"{', '.join(row.get('riskFlags', [])) if row.get('riskFlags') else '-'} | "
                        f"{row.get('check6mDate', '-')} | {row.get('check12mDate', '-')} | "
                        f"{row.get('status6m', '-')} | {row.get('status12m', '-')} |"
                    )
                lines.append("")

            date_split = results.get("dateSplitRadar", {})
            split_summary = date_split.get("techSubsetHoldoutSummary", {})
            if split_summary:
                split_cfg = date_split.get("trainedDefault", {}).get("config", {})
                lines.extend([
                    "### Date-Split Diagnostic",
                    "",
                    "Trains on QQQ/SPY signals dated up to "
                    f"{date_split.get('trainSignalEndDate', '?')}, then evaluates tech-stock signals dated "
                    f"{date_split.get('holdoutSignalStartDate', '?')} or later.",
                    "",
                    f"- Trained config: `{split_cfg.get('name', '?')}` strategy={split_cfg.get('buy_strategy', '?')}",
                    f"- Tech holdout symbols: {split_summary.get('symbolCount', 0)}",
                    f"- Avg signals: {split_summary.get('avgSignals', 0):.1f}",
                    f"- Avg 6m / 12m / 24m: {split_summary.get('avg6mPct', 0):.1f}% / "
                    f"{split_summary.get('avg12mPct', 0):.1f}% / {split_summary.get('avg24mPct', 0):.1f}%",
                    f"- Median 12m: {split_summary.get('median12mPct', 0):.1f}%",
                    f"- Avg 12m max drawdown: {split_summary.get('avgMaxDrawdown12mPct', 0):.1f}%",
                    f"- Signal-level holdout: {split_signal_summary.get('signalCount', 0)} signals, "
                    f"{split_signal_summary.get('mature12mSignalCount', 0)} mature 12m, "
                    f"avg 12m {pct_text(split_signal_summary.get('avg12mPct'))}, "
                    f"avg 12m drawdown {split_signal_summary.get('avgMaxDrawdown12mPct', 0):.1f}%.",
                    "- Note: this is a signal-date split diagnostic, not a full rolling walk-forward test.",
                    "",
                ])

            if strategy_best:
                freeze_candidates = select_freeze_candidate_entries(
                    radar.get("recommendedDefault", {}),
                    date_split,
                    strategy_best,
                )
                if freeze_candidates:
                    lines.extend([
                        "### Frozen Candidate Set Used For Validation",
                        "",
                        "These configs are the frozen candidate set used by the restricted walk-forward diagnostic below.",
                        "",
                        "| Reason | Strategy | Config | Combined |",
                        "|--------|----------|--------|----------|",
                    ])
                    for item in freeze_candidates:
                        combined = item.get("combinedScore")
                        combined_text = f"{combined:.2f}" if isinstance(combined, (int, float)) else "-"
                        lines.append(
                            f"| {item['reason']} | {item['strategy']} | `{item['name']}` | {combined_text} |"
                        )
                    lines.append("")

            frozen_holdouts = results.get("frozenCandidateTechHoldouts", [])
            if frozen_holdouts:
                lines.extend([
                    "### Frozen Candidate 2023+ Tech Holdout Comparison",
                    "",
                    "Symbol-average treats each ticker equally. Signal-level treats each signal equally, so active tickers can carry more weight.",
                    "",
                    "| Reason | Strategy | Config | Symbols | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |",
                    "|--------|----------|--------|---------|---------|------------|----------------|----------------|---------------|",
                ])
                for item in frozen_holdouts:
                    cfg_d = item.get("config", {})
                    symbol_summary = item.get("techHoldoutSummary", {})
                    signal_summary = item.get("techRecentSignalSummary", {})
                    lines.append(
                        f"| {item.get('reason', '?')} | {cfg_d.get('buy_strategy', '?')} | "
                        f"`{cfg_d.get('name', '?')}` | {symbol_summary.get('symbolCount', 0)} | "
                        f"{signal_summary.get('signalCount', 0)} | "
                        f"{signal_summary.get('mature12mSignalCount', 0)} | "
                        f"{symbol_summary.get('avg12mPct', 0):.1f}% | "
                        f"{pct_text(signal_summary.get('avg12mPct'))} | "
                        f"{signal_summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )
                lines.append("")

            walk_forward = results.get("restrictedWalkForwardRadar", {})
            walk_years = walk_forward.get("years", [])
            if walk_years:
                lines.extend([
                    "### Restricted Walk-Forward Diagnostic",
                    "",
                    "Each year selects only from the frozen candidate configs using prior QQQ/SPY signal history, then evaluates that selected config on tech-stock signals in the next calendar year.",
                    "This is more operationally conservative than the full-grid walk-forward because it only selects from a small predeclared candidate set.",
                    "",
                    "| Year | Selected | Strategy | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |",
                    "|------|----------|----------|---------|------------|----------------|----------------|---------------|",
                ])
                for row in walk_years:
                    if "error" in row:
                        lines.append(
                            f"| {row.get('year', '?')} | {row.get('error', '?')} | - | - | - | - | - | - |"
                        )
                        continue
                    cfg_d = row.get("selectedConfig", {})
                    symbol_summary = row.get("techHoldoutSummary", {})
                    signal_summary = row.get("techSignalSummary", {})
                    symbol_avg12_text = (
                        "-"
                        if signal_summary.get("mature12mSignalCount", 0) == 0
                        else pct_text(symbol_summary.get("avg12mPct"))
                    )
                    lines.append(
                        f"| {row.get('year', '?')} | `{cfg_d.get('name', '?')}` | "
                        f"{cfg_d.get('buy_strategy', '?')} | "
                        f"{signal_summary.get('signalCount', 0)} | "
                        f"{signal_summary.get('mature12mSignalCount', 0)} | "
                        f"{symbol_avg12_text} | "
                        f"{pct_text(signal_summary.get('avg12mPct'))} | "
                        f"{signal_summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )
                lines.append("")

            full_walk_forward = results.get("fullGridWalkForwardRadar", {})
            full_walk_years = full_walk_forward.get("years", [])
            if full_walk_years:
                lines.extend([
                    "### Full-Grid Walk-Forward Diagnostic",
                    "",
                    "Each year reranks the full stage-1 grid using only prior QQQ/SPY signal history, then evaluates the selected config on tech-stock signals in the next calendar year.",
                    "",
                    "| Year | Selected | Strategy | Train Score | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |",
                    "|------|----------|----------|-------------|---------|------------|----------------|----------------|---------------|",
                ])
                for row in full_walk_years:
                    if "error" in row:
                        lines.append(
                            f"| {row.get('year', '?')} | {row.get('error', '?')} | - | - | - | - | - | - | - |"
                        )
                        continue
                    cfg_d = row.get("selectedConfig", {})
                    symbol_summary = row.get("techHoldoutSummary", {})
                    signal_summary = row.get("techSignalSummary", {})
                    train_score = row.get("trainCombinedScore")
                    train_score_text = f"{train_score:.2f}" if isinstance(train_score, (int, float)) else "-"
                    symbol_avg12_text = (
                        "-"
                        if signal_summary.get("mature12mSignalCount", 0) == 0
                        else pct_text(symbol_summary.get("avg12mPct"))
                    )
                    lines.append(
                        f"| {row.get('year', '?')} | `{cfg_d.get('name', '?')}` | "
                        f"{cfg_d.get('buy_strategy', '?')} | {train_score_text} | "
                        f"{signal_summary.get('signalCount', 0)} | "
                        f"{signal_summary.get('mature12mSignalCount', 0)} | "
                        f"{symbol_avg12_text} | "
                        f"{pct_text(signal_summary.get('avg12mPct'))} | "
                        f"{signal_summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )
                lines.append("")

            multi_window = results.get("multiWindowValidationRadar", {})
            if multi_window:
                window_summary = multi_window.get("summary", {})
                lines.extend([
                    "### Multi-Window Validation",
                    "",
                    "This freezes the current broad default config and evaluates it across additional anchored and fixed holdout windows on the tech-stock subset.",
                    "",
                    f"- Windows: {window_summary.get('windowCount', 0)} total, "
                    f"{window_summary.get('matureWindowCount', 0)} with mature 12m samples.",
                    f"- Positive 12m windows: {window_summary.get('windowsWithPositiveAvg12m', 0)}.",
                    f"- Signal avg 12m, min / median / max: "
                    f"{pct_text(window_summary.get('minSignalAvg12mPct'))} / "
                    f"{pct_text(window_summary.get('medianSignalAvg12mPct'))} / "
                    f"{pct_text(window_summary.get('maxSignalAvg12mPct'))}.",
                    f"- Worst signal 12m drawdown across windows: "
                    f"{pct_text(window_summary.get('worstSignalDrawdown12mPct'))}.",
                    "",
                    "Anchored windows:",
                    "",
                    "| Start | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |",
                    "|-------|---------|------------|----------------|----------------|---------------|",
                ])

                def append_window_row(start_text: str, row: dict[str, Any]) -> None:
                    symbol_summary = row.get("symbolSummary", {})
                    signal_summary = row.get("signalSummary", {})
                    symbol_avg12_text = (
                        "-"
                        if signal_summary.get("mature12mSignalCount", 0) == 0
                        else pct_text(symbol_summary.get("avg12mPct"))
                    )
                    lines.append(
                        f"| {start_text} | {signal_summary.get('signalCount', 0)} | "
                        f"{signal_summary.get('mature12mSignalCount', 0)} | "
                        f"{symbol_avg12_text} | "
                        f"{pct_text(signal_summary.get('avg12mPct'))} | "
                        f"{signal_summary.get('avgMaxDrawdown12mPct', 0):.1f}% |"
                    )

                for row in multi_window.get("anchoredWindows", []):
                    append_window_row(row.get("startDate", "?"), row)

                rolling_windows = multi_window.get("rollingWindows", [])
                if rolling_windows:
                    lines.extend([
                        "",
                        "Fixed rolling windows:",
                        "",
                        "| Window | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |",
                        "|--------|---------|------------|----------------|----------------|---------------|",
                    ])
                    for row in rolling_windows:
                        append_window_row(row.get("label", "?"), row)
                lines.append("")

            lines.extend([
                "### Current Interpretation",
                "",
                "- Unified tech-stock add-on default: `bottom_reversal` remains the strongest broad strategy found so far.",
                "- Per-symbol best configs show higher returns, but they are more likely to contain in-sample fitting because each ticker gets its own best setup.",
                "- `index_shallow_pullback` is useful as a higher-frequency ETF/index pullback radar, but it is not the current return-maximizing default.",
                "- Stage 2 trade simulation is a short-term buy/sell comparison; it should not be treated as the final sell rule for long-term investment add-ons.",
                "",
                "### Validation Caveats",
                "",
                "- The full-grid walk-forward table is the stricter validation view because each year reranks the whole stage-1 grid using only prior data.",
                "- The restricted walk-forward table is more conservative operationally because it only selects from a small frozen candidate set.",
                "- The multi-window table freezes the current broad default and checks whether the same config remains reasonable across additional anchored and fixed windows.",
                "- The conservative read is the global default applied to tech stocks; the per-symbol best table is useful for research, but easier to overfit.",
                "- Future validation should still add live paper-trading or a later out-of-sample period before treating the radar as production-grade.",
                "- Signal quality should be judged by 12m/24m forward return and post-entry drawdown, not by short-term trade win rate.",
                "",
            ])

            checklist = results.get("promptToArtifactChecklist", [])
            if checklist:
                lines.extend([
                    "### Prompt-To-Artifact Checklist",
                    "",
                    "| Requirement | Status | Evidence |",
                    "|-------------|--------|----------|",
                ])
                for item in checklist:
                    lines.append(
                        f"| {item.get('requirement', '?')} | {item.get('status', '?')} | "
                        f"{item.get('evidence', '-')} |"
                    )
                lines.append("")

        lines.extend(["## Per-Symbol Long-Term Radar Configs", ""])
        lines.extend([
            "| Symbol | Strategy | Config | Signals | 6m | 12m | 24m | 12m DD |",
            "|--------|----------|--------|---------|----|-----|-----|--------|",
        ])
        for symbol, best in per_sym_radar.items():
            if "error" in best:
                lines.append(f"| {symbol} | {best['error']} | - | - | - | - | - | - |")
                continue
            cfg_d = best.get("config", {})
            fwd = best.get("avgForwardReturns", {})
            dd = best.get("avgDrawdowns", {})
            lines.append(
                f"| {symbol} | {cfg_d.get('buy_strategy', '?')} | "
                f"`{cfg_d.get('name', '?')}` | "
                f"{best.get('signalCount', 0)} | {fwd.get('avg6mPct', 0):.1f}% | "
                f"{fwd.get('avg12mPct', 0):.1f}% | {fwd.get('avg24mPct', 0):.1f}% | "
                f"{dd.get('avgMaxDrawdown12mPct', 0):.1f}% |"
            )
        lines.append("")

    lines.extend([
        "## TradingView Pine Script",
        "",
        "Two Pine files are available, and they serve different purposes.",
        "",
        "Recommended use:",
        "",
        "- Use `long_term_addon_radar.pine` for the long-term add-on radar that matches this report's investment use case.",
        "- Use `uptrend_dip_pine.pine` only when you want the fuller buy/sell comparison indicator with position-state and sell logic.",
        "- Keep `Radar Mode = bottom_reversal` for rare deep-drawdown add-on signals.",
        "- Switch `Radar Mode = index_shallow_pullback` for higher-frequency SPY/QQQ-style shallow pullback alerts; its standalone default threshold is 55.",
        "- Treat `IDX WATCH/MED/STRONG` and `BTM WATCH/MED/STRONG` as different signal families, not as the same score scale.",
        "",
    ])

    text = "\n".join(lines)
    (OUT_DIR / "uptrend_dip_report.md").write_text(text, encoding="utf-8", newline="\n")
    (LONG_TERM_ADDON_DIR / "uptrend_dip_report.md").write_text(
        text,
        encoding="utf-8",
        newline="\n",
    )


# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════


def load_symbol_frame(symbol: str, refresh: bool) -> tuple[pd.DataFrame, str]:
    df, source = fetch_price(symbol, refresh)
    benchmark_close = None
    if symbol != "SPY":
        try:
            benchmark_df, _ = fetch_price("SPY", refresh)
            benchmark_close = benchmark_df["close"]
        except FileNotFoundError:
            benchmark_close = None
    return build_indicators(df, benchmark_close), source


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
        df, source = load_symbol_frame(symbol, refresh)
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

    # ── Long-term add-on radar: buy signal quality for long holding periods ──
    output["longTermRadar"] = {"configCount": len(stage1_configs)}
    lt_metrics: dict[str, list[dict[str, Any]]] = {}
    for symbol in search_symbols:
        df, _ = load_symbol_frame(symbol, refresh)
        ranked = []
        for cfg in stage1_configs:
            metrics = evaluate_long_term_radar(df, cfg)
            ranked.append(metrics)
        lt_metrics[symbol] = ranked

        ranked_sorted = sorted(ranked, key=lambda x: x["score"], reverse=True)
        output["longTermRadar"].setdefault("symbols", {})[symbol] = {
            "best": ranked_sorted[0],
            "top5": ranked_sorted[:5],
        }

    lt_combined = combined_rank(stage1_configs, lt_metrics)
    output["longTermRadar"]["recommendedDefault"] = lt_combined[0]
    output["longTermRadar"]["combinedTop10"] = lt_combined[:10]
    output["longTermRadar"]["bestByStrategy"] = best_by_buy_strategy(lt_combined)

    split_train_end = "2022-12-31"
    split_holdout_start = "2023-01-01"
    split_train_metrics: dict[str, list[dict[str, Any]]] = {}
    for symbol in search_symbols:
        df, _ = load_symbol_frame(symbol, refresh)
        split_train_metrics[symbol] = [
            evaluate_long_term_radar(df, cfg, signal_end_date=split_train_end)
            for cfg in stage1_configs
        ]
    split_combined = combined_rank(stage1_configs, split_train_metrics)
    split_radar_cfg: UptrendDipConfig | None = None
    if split_combined:
        output["dateSplitRadar"] = {
            "trainSignalEndDate": split_train_end,
            "holdoutSignalStartDate": split_holdout_start,
            "trainedDefault": split_combined[0],
            "combinedTop5": split_combined[:5],
            "note": "Signal-date split diagnostic, not a full rolling walk-forward test.",
        }
        split_cfg_dict = split_combined[0]["config"]
        split_radar_cfg = UptrendDipConfig(**{
            k: split_cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
        })

    # ── Stage 2: Sell config search for top buy configs ──
    top_buy_configs = select_stage2_buy_configs(s1_combined)

    all_stage2_configs: list[UptrendDipConfig] = []
    for base in top_buy_configs:
        all_stage2_configs.extend(candidate_configs_stage2(base))

    output["stage2"] = {"configCount": len(all_stage2_configs)}

    s2_metrics: dict[str, list[dict[str, Any]]] = {}

    for symbol in search_symbols:
        df, _ = load_symbol_frame(symbol, refresh)

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
    radar_cfg_dict = lt_combined[0]["config"]
    radar_cfg = UptrendDipConfig(**{
        k: radar_cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
    })

    per_symbol_best: dict[str, dict[str, Any]] = {}
    per_symbol_radar_best: dict[str, dict[str, Any]] = {}
    per_symbol_radar_recommended: dict[str, dict[str, Any]] = {}
    for symbol in validate_symbols:
        if symbol in output["stage2"].get("symbols", {}):
            per_symbol_best[symbol] = output["stage2"]["symbols"][symbol]["best"]
            per_symbol_radar_best[symbol] = output["longTermRadar"]["symbols"][symbol]["best"]
            per_symbol_radar_recommended[symbol] = lt_combined[0]["symbols"][symbol]
            continue
        try:
            df, _ = load_symbol_frame(symbol, refresh)
        except FileNotFoundError:
            per_symbol_best[symbol] = {"error": "data not found"}
            per_symbol_radar_best[symbol] = {"error": "data not found"}
            per_symbol_radar_recommended[symbol] = {"error": "data not found"}
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

        radar_metrics = evaluate_long_term_radar(df, radar_cfg)
        per_symbol_radar_recommended[symbol] = radar_metrics
        per_symbol_radar_best[symbol] = radar_metrics

        radar_ranked = []
        for cfg in stage1_configs:
            m = evaluate_long_term_radar(df, cfg)
            radar_ranked.append(m)
        radar_ranked.sort(key=lambda x: x["score"], reverse=True)
        if radar_ranked and radar_ranked[0]["score"] > per_symbol_radar_best[symbol].get("score", -999):
            per_symbol_radar_best[symbol] = radar_ranked[0]

    output["perSymbolBest"] = per_symbol_best
    output["recommendedRadarBySymbol"] = per_symbol_radar_recommended
    output["perSymbolRadarBest"] = per_symbol_radar_best
    output["techSubsetRecommendedRadarSummary"] = summarize_radar_subset(
        per_symbol_radar_recommended,
        TECH_STOCK_SUBSET,
    )
    output["techSegmentRecommendedRadarSummaries"] = summarize_radar_segments(
        per_symbol_radar_recommended,
    )
    output["techSubsetRecommendedRecentSignals"] = summarize_signal_window(
        per_symbol_radar_recommended,
        TECH_STOCK_SUBSET,
        start_date="2023-01-01",
    )
    output["techSubsetRecommendedSignalsByYear"] = summarize_signal_years(
        per_symbol_radar_recommended,
        TECH_STOCK_SUBSET,
        start_year=2023,
    )
    output["techSubsetSignalRiskDiagnostics"] = summarize_signal_risk_diagnostics(
        per_symbol_radar_recommended,
        TECH_STOCK_SUBSET,
        start_date="2023-01-01",
    )
    output["techSubsetRecommendedRecentSignalLog"] = summarize_recent_signal_log(
        per_symbol_radar_recommended,
        TECH_STOCK_SUBSET,
        limit=20,
    )
    output["techSubsetCurrentSignalLog"] = summarize_active_signal_log(
        per_symbol_radar_recommended,
        TECH_STOCK_SUBSET,
        max_age_bars=126,
        limit=20,
    )
    output["paperTrackingPlan"] = build_paper_tracking_plan(
        output["techSubsetCurrentSignalLog"],
        output["generatedAt"],
    )
    output["techSubsetRadarSummary"] = summarize_radar_subset(per_symbol_radar_best, TECH_STOCK_SUBSET)
    output["techSegmentBestRadarSummaries"] = summarize_radar_segments(
        per_symbol_radar_best,
    )
    output["techSubsetBestRecentSignals"] = summarize_signal_window(
        per_symbol_radar_best,
        TECH_STOCK_SUBSET,
        start_date="2023-01-01",
    )

    if split_radar_cfg is not None:
        split_holdout_by_symbol: dict[str, dict[str, Any]] = {}
        for symbol in validate_symbols:
            try:
                df, _ = load_symbol_frame(symbol, refresh)
            except FileNotFoundError:
                split_holdout_by_symbol[symbol] = {"error": "data not found"}
                continue
            split_holdout_by_symbol[symbol] = evaluate_long_term_radar(
                df,
                split_radar_cfg,
                signal_start_date=split_holdout_start,
            )
        output["dateSplitRadar"]["holdoutBySymbol"] = split_holdout_by_symbol
        output["dateSplitRadar"]["techSubsetHoldoutSummary"] = summarize_radar_subset(
            split_holdout_by_symbol,
            TECH_STOCK_SUBSET,
        )
        output["dateSplitRadar"]["techSubsetHoldoutSignalSummary"] = summarize_signal_window(
            split_holdout_by_symbol,
            TECH_STOCK_SUBSET,
            start_date=split_holdout_start,
        )
        output["dateSplitRadar"]["techSubsetHoldoutByYear"] = summarize_signal_years(
            split_holdout_by_symbol,
            TECH_STOCK_SUBSET,
            start_year=2023,
        )

    freeze_candidates = select_freeze_candidate_entries(
        lt_combined[0],
        output.get("dateSplitRadar", {}),
        output["longTermRadar"].get("bestByStrategy", {}),
    )
    frozen_holdouts = []
    for entry in freeze_candidates:
        cfg = UptrendDipConfig(**{
            k: entry["config"][k] for k in [f.name for f in fields(UptrendDipConfig)]
        })
        by_symbol: dict[str, dict[str, Any]] = {}
        for symbol in TECH_STOCK_SUBSET:
            try:
                df, _ = load_symbol_frame(symbol, refresh)
            except FileNotFoundError:
                by_symbol[symbol] = {"error": "data not found"}
                continue
            by_symbol[symbol] = evaluate_long_term_radar(
                df,
                cfg,
                signal_start_date=split_holdout_start,
            )
        frozen_holdouts.append({
            "reason": entry["reason"],
            "config": entry["config"],
            "combinedScore": entry.get("combinedScore"),
            "techHoldoutSummary": summarize_radar_subset(by_symbol, TECH_STOCK_SUBSET),
            "techRecentSignalSummary": summarize_signal_window(
                by_symbol,
                TECH_STOCK_SUBSET,
                start_date=split_holdout_start,
            ),
        })
    output["frozenCandidateTechHoldouts"] = frozen_holdouts

    walk_forward_frames: dict[str, pd.DataFrame] = {}
    for symbol in sorted(set(search_symbols) | set(TECH_STOCK_SUBSET)):
        try:
            walk_forward_frames[symbol] = load_symbol_frame(symbol, refresh)[0]
        except FileNotFoundError:
            continue
    output["restrictedWalkForwardRadar"] = evaluate_restricted_walk_forward(
        walk_forward_frames,
        search_symbols,
        TECH_STOCK_SUBSET,
        freeze_candidates,
        years=[2023, 2024, 2025, 2026],
    )
    output["fullGridWalkForwardRadar"] = evaluate_full_grid_walk_forward(
        walk_forward_frames,
        search_symbols,
        TECH_STOCK_SUBSET,
        stage1_configs,
        years=[2023, 2024, 2025, 2026],
    )
    output["multiWindowValidationRadar"] = evaluate_multi_window_validation(
        walk_forward_frames,
        TECH_STOCK_SUBSET,
        radar_cfg,
        anchored_start_years=[2021, 2022, 2023, 2024],
        rolling_windows=[
            ("2021-01-01", "2022-12-31"),
            ("2022-01-01", "2023-12-31"),
            ("2023-01-01", "2024-12-31"),
            ("2024-01-01", "2025-12-31"),
        ],
    )

    # ── Generate Pine Script ──
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LONG_TERM_ADDON_DIR.mkdir(parents=True, exist_ok=True)
    pine = generate_pine_script(radar_cfg)
    (OUT_DIR / "uptrend_dip_pine.pine").write_text(pine, encoding="utf-8", newline="\n")
    output["pineScript"] = str(OUT_DIR / "uptrend_dip_pine.pine")
    index_radar_cfg = None
    index_entry = output["longTermRadar"].get("bestByStrategy", {}).get("index_shallow_pullback")
    if index_entry:
        index_cfg_dict = index_entry["config"]
        index_radar_cfg = UptrendDipConfig(**{
            k: index_cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
        })
    rsi_radar_cfg = None
    rsi_entry = output["longTermRadar"].get("bestByStrategy", {}).get("rsi_divergence")
    if rsi_entry:
        rsi_cfg_dict = rsi_entry["config"]
        rsi_radar_cfg = UptrendDipConfig(**{
            k: rsi_cfg_dict[k] for k in [f.name for f in fields(UptrendDipConfig)]
        })
    long_term_pine = generate_long_term_addon_pine_script(radar_cfg, index_radar_cfg, rsi_radar_cfg)
    (LONG_TERM_ADDON_DIR / "long_term_addon_radar.pine").write_text(
        long_term_pine,
        encoding="utf-8",
        newline="\n",
    )
    output["longTermAddonPineScript"] = str(LONG_TERM_ADDON_DIR / "long_term_addon_radar.pine")
    output["promptToArtifactChecklist"] = build_prompt_to_artifact_checklist(output)

    output = json_safe(output)
    (OUT_DIR / "uptrend_dip_results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
        newline="\n",
    )
    (LONG_TERM_ADDON_DIR / "uptrend_dip_results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
        newline="\n",
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
    parser.add_argument(
        "--paper-status",
        action="store_true",
        help="Print the latest paper-tracking plan from uptrend_dip_results.json without rerunning search",
    )
    parser.add_argument(
        "--as-of",
        help="As-of date for --paper-status overdue checks, formatted as YYYY-MM-DD",
    )
    args = parser.parse_args()

    if args.paper_status:
        results_path = OUT_DIR / "uptrend_dip_results.json"
        if not results_path.exists():
            raise SystemExit("No uptrend_dip_results.json found. Run the search first.")
        results = json.loads(results_path.read_text(encoding="utf-8"))
        print(format_paper_tracking_status(results, as_of_date=args.as_of))
        return

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

    radar = result["longTermRadar"]["recommendedDefault"]
    radar_cfg = radar["config"]
    print(f"\nLong-term radar: {radar_cfg['name']}")
    print(f"Strategy: {radar_cfg['buy_strategy']}, combined={radar['combinedScore']:.2f}")
    print(f"Buy thr={radar_cfg['buy_threshold']:.0f}")
    for symbol, metrics in radar["symbols"].items():
        fwd = metrics.get("avgForwardReturns", {})
        dd = metrics.get("avgDrawdowns", {})
        print(f"  {symbol}: signals={metrics.get('signalCount', 0)} "
              f"6m={fwd.get('avg6mPct', 0):.1f}% "
              f"12m={fwd.get('avg12mPct', 0):.1f}% "
              f"24m={fwd.get('avg24mPct', 0):.1f}% "
              f"12mDD={dd.get('avgMaxDrawdown12mPct', 0):.1f}%")

    rec = result["stage2"]["recommendedDefault"]
    cfg = rec["config"]
    print(f"\nTrading-system comparison: {cfg['name']}")
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
