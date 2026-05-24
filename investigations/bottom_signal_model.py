"""Shared data models for Bottom Signal research."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BottomSignalConfig:
    name: str
    drawdown_window: int = 42
    drawdown_threshold: float = -12.0
    rsi_period: int = 7
    stoch_period: int = 9
    stoch_smooth: int = 3
    macd_fast: int = 8
    macd_slow: int = 21
    macd_signal: int = 5
    ma_period: int = 150
    atr_period: int = 10
    volume_window: int = 10
    band_period: int = 20
    band_std: float = 2.0
    watch_threshold: int = 35
    medium_threshold: int = 55
    strong_threshold: int = 75
    entry_threshold: int = 55
    exit_threshold: int = 70
    min_signal_gap: int = 21
    drawdown_weight: float = 0.30
    momentum_weight: float = 0.22
    repair_weight: float = 0.18
    structure_weight: float = 0.15
    volume_weight: float = 0.08
    ma_weight: float = 0.07
    market_symbol_1: str = "QQQ"
    market_symbol_2: str = "SPY"
    market_drawdown_window: int = 126
    market_drawdown_threshold: float = -18.0
    rs_window: int = 63
    rs_drawdown_advantage_threshold: float = 5.0
    rs_repair_advantage_threshold: float = 5.0
    rs_pullback_window: int = 42
    rs_pullback_min_drawdown: float = 5.0
    rs_pullback_max_drawdown: float = 18.0
    mb_entry_offset: int = 0
    experimental_signal_set: str = "rs_antidrawdown_repair"


@dataclass(frozen=True)
class SearchSettings:
    max_configs: int
    cache_indicators: bool
    search_stages: dict[str, Any]
    candidate_parameters: dict[str, list[Any]]
    seed_configs: list[dict[str, Any]]
    thresholds: dict[str, int]
    weights: dict[str, float]
    weight_profiles: list[dict[str, Any]]
    objective_weights: dict[str, float]
    validation: dict[str, Any]
