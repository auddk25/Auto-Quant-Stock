"""Parameterized technical indicator helpers for project OHLCV data."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd
from ta.momentum import (
    RSIIndicator,
    StochasticOscillator,
)
from ta.trend import ADXIndicator, EMAIndicator, MACD, SMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands

try:
    import pandas_ta_classic as pandas_ta_classic
except ImportError:  # pragma: no cover - dependency is installed in normal project setup.
    pandas_ta_classic = None


OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def validate_ohlcv(df: pd.DataFrame) -> None:
    """Raise when a frame does not contain the project's standard OHLCV columns."""
    missing = [column for column in OHLCV_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required OHLCV columns: {', '.join(missing)}")


def pandas_ta_classic_available() -> bool:
    """Return whether the supplemental indicator backend is importable."""
    return pandas_ta_classic is not None


def _unique_positive_ints(values: Iterable[int], name: str) -> list[int]:
    periods = []
    for value in values:
        period = int(value)
        if period <= 0:
            raise ValueError(f"{name} values must be positive integers")
        if period not in periods:
            periods.append(period)
    return periods


def _format_number(value: float | int) -> str:
    numeric = float(value)
    if numeric.is_integer():
        return str(int(numeric))
    return str(numeric).replace(".", "p")


def _macd_configs(configs: Iterable[Sequence[int]]) -> list[tuple[int, int, int]]:
    parsed = []
    for config in configs:
        if len(config) != 3:
            raise ValueError("macd configs must be (fast, slow, signal)")
        fast, slow, signal = (int(config[0]), int(config[1]), int(config[2]))
        if min(fast, slow, signal) <= 0:
            raise ValueError("macd config values must be positive integers")
        parsed.append((fast, slow, signal))
    return parsed


def _bollinger_configs(configs: Iterable[Sequence[float]]) -> list[tuple[int, float]]:
    parsed = []
    for config in configs:
        if len(config) != 2:
            raise ValueError("bollinger configs must be (period, std_dev)")
        period, std_dev = int(config[0]), float(config[1])
        if period <= 0 or std_dev <= 0:
            raise ValueError("bollinger config values must be positive")
        parsed.append((period, std_dev))
    return parsed


def _stochastic_configs(configs: Iterable[Sequence[int]]) -> list[tuple[int, int]]:
    parsed = []
    for config in configs:
        if len(config) != 2:
            raise ValueError("stochastic configs must be (period, smooth)")
        period, smooth = int(config[0]), int(config[1])
        if period <= 0 or smooth <= 0:
            raise ValueError("stochastic config values must be positive integers")
        parsed.append((period, smooth))
    return parsed


def _pairs(configs: Iterable[Sequence[int]], name: str) -> list[tuple[int, int]]:
    parsed = []
    for config in configs:
        if len(config) != 2:
            raise ValueError(f"{name} configs must be (first, second)")
        first, second = int(config[0]), int(config[1])
        if first <= 0 or second <= 0:
            raise ValueError(f"{name} config values must be positive integers")
        parsed.append((first, second))
    return parsed


def add_sma(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    close = out["Close"]
    for period in _unique_positive_ints(periods, "sma periods"):
        out[f"sma_{period}"] = SMAIndicator(close=close, window=period).sma_indicator()
    return out


def add_ema(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    close = out["Close"]
    for period in _unique_positive_ints(periods, "ema periods"):
        out[f"ema_{period}"] = EMAIndicator(close=close, window=period).ema_indicator()
    return out


def add_rsi(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    close = out["Close"]
    for period in _unique_positive_ints(periods, "rsi periods"):
        out[f"rsi_{period}"] = RSIIndicator(close=close, window=period).rsi()
    return out


def add_macd(df: pd.DataFrame, configs: Iterable[Sequence[int]]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    close = out["Close"]
    for fast, slow, signal in _macd_configs(configs):
        suffix = f"{fast}_{slow}_{signal}"
        macd = MACD(close=close, window_slow=slow, window_fast=fast, window_sign=signal)
        out[f"macd_{suffix}"] = macd.macd()
        out[f"macd_signal_{suffix}"] = macd.macd_signal()
        out[f"macd_diff_{suffix}"] = macd.macd_diff()
    return out


def add_atr(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    high, low, close = out["High"], out["Low"], out["Close"]
    for period in _unique_positive_ints(periods, "atr periods"):
        out[f"atr_{period}"] = AverageTrueRange(
            high=high,
            low=low,
            close=close,
            window=period,
        ).average_true_range()
    return out


def add_adx(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    high, low, close = out["High"], out["Low"], out["Close"]
    for period in _unique_positive_ints(periods, "adx periods"):
        out[f"adx_{period}"] = ADXIndicator(
            high=high,
            low=low,
            close=close,
            window=period,
        ).adx()
    return out


def add_bollinger(df: pd.DataFrame, configs: Iterable[Sequence[float]]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    close = out["Close"]
    for period, std_dev in _bollinger_configs(configs):
        suffix = f"{period}_{_format_number(std_dev)}"
        boll = BollingerBands(close=close, window=period, window_dev=std_dev)
        out[f"bb_mid_{suffix}"] = boll.bollinger_mavg()
        out[f"bb_upper_{suffix}"] = boll.bollinger_hband()
        out[f"bb_lower_{suffix}"] = boll.bollinger_lband()
        out[f"bb_width_{suffix}"] = boll.bollinger_wband()
    return out


def add_stochastic(df: pd.DataFrame, configs: Iterable[Sequence[int]]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    high, low, close = out["High"], out["Low"], out["Close"]
    for period, smooth in _stochastic_configs(configs):
        suffix = f"{period}_{smooth}"
        stoch = StochasticOscillator(
            high=high,
            low=low,
            close=close,
            window=period,
            smooth_window=smooth,
        )
        out[f"stoch_{suffix}"] = stoch.stoch()
        out[f"stoch_signal_{suffix}"] = stoch.stoch_signal()
    return out


def add_volume_features(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    volume = out["Volume"]
    for period in _unique_positive_ints(periods, "volume periods"):
        volume_sma = volume.rolling(period).mean()
        out[f"volume_sma_{period}"] = volume_sma
        out[f"volume_ratio_{period}"] = volume / volume_sma.replace(0, np.nan)
    return out


def add_drawdown(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    close = out["Close"]
    for period in _unique_positive_ints(periods, "drawdown periods"):
        out[f"drawdown_{period}"] = (close / close.rolling(period).max() - 1) * 100
    return out


def add_distance_to_sma(df: pd.DataFrame, periods: Iterable[int]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    close = out["Close"]
    for period in _unique_positive_ints(periods, "distance_to_sma periods"):
        sma_col = f"sma_{period}"
        sma = out[sma_col] if sma_col in out.columns else SMAIndicator(
            close=close,
            window=period,
        ).sma_indicator()
        out[f"dist_sma_{period}"] = (close / sma - 1) * 100
    return out


def add_atr_ratio(df: pd.DataFrame, pairs: Iterable[Sequence[int]]) -> pd.DataFrame:
    validate_ohlcv(df)
    out = df.copy()
    high, low, close = out["High"], out["Low"], out["Close"]
    for short_period, long_period in _pairs(pairs, "atr_ratio"):
        atr_col = f"atr_{short_period}"
        atr = out[atr_col] if atr_col in out.columns else AverageTrueRange(
            high=high,
            low=low,
            close=close,
            window=short_period,
        ).average_true_range()
        atr_avg = atr.rolling(long_period).mean()
        out[f"atr_ratio_{short_period}_{long_period}"] = atr / atr_avg.replace(0, np.nan)
    return out


def build_indicators(df: pd.DataFrame, spec: Mapping[str, Any]) -> pd.DataFrame:
    """Build only the indicator columns requested by the supplied experiment spec."""
    validate_ohlcv(df)
    out = df.copy()
    if "sma" in spec:
        out = add_sma(out, spec["sma"])
    if "ema" in spec:
        out = add_ema(out, spec["ema"])
    if "rsi" in spec:
        out = add_rsi(out, spec["rsi"])
    if "macd" in spec:
        out = add_macd(out, spec["macd"])
    if "atr" in spec:
        out = add_atr(out, spec["atr"])
    if "adx" in spec:
        out = add_adx(out, spec["adx"])
    if "bollinger" in spec:
        out = add_bollinger(out, spec["bollinger"])
    if "stochastic" in spec:
        out = add_stochastic(out, spec["stochastic"])
    if "volume" in spec:
        out = add_volume_features(out, spec["volume"])
    if "drawdown" in spec:
        out = add_drawdown(out, spec["drawdown"])
    if "distance_to_sma" in spec:
        out = add_distance_to_sma(out, spec["distance_to_sma"])
    if "atr_ratio" in spec:
        out = add_atr_ratio(out, spec["atr_ratio"])
    return out
