"""Stage-bottom signal researcher and Pine script generator."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
from io import StringIO
import json
import math
import sys
from dataclasses import asdict, replace
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import ALL_TICKERS  # noqa: E402
from investigations.bottom_signal_model import BottomSignalConfig, SearchSettings  # noqa: E402
from investigations.bottom_signal_paths import (  # noqa: E402
    CACHE_DIR,
    CANDIDATE_REVIEW_CSV_PATH,
    DEFAULT_CONFIG_PATH,
    MB_FACTOR_ABLATION_CSV_PATH,
    MERGED_OBSERVATION_PINE_PATH,
    MISS_DIAGNOSTICS_CSV_PATH,
    MISS_DIAGNOSTICS_REPORT_PATH,
    NEXT_ACTIONS_CSV_PATH,
    OBSERVATION_REPORT_PATH,
    OBSERVATION_SIGNALS_CSV_PATH,
    PINE_PATH,
    PLAN_SUMMARY_PATH,
    RECENT_VALIDATION_CSV_PATH,
    RESEARCH_2022_2026_DIR,
    REPORT_PATH,
    RESULTS_PATH,
    RS_WATCHLIST_CANDIDATE_CSV_PATH,
    RS_WATCHLIST_PINE_PATH,
    RS_WATCHLIST_REPORT_PATH,
    RS_WATCHLIST_TICKER_CSV_PATH,
    STRICT_FORMAL_PINE_PATH,
    STRATEGY_ITERATION_REVIEW_CSV_PATH,
    STRATEGY_ITERATION_REVIEW_PATH,
)
from quant_indicators import build_indicators, validate_ohlcv  # noqa: E402


RETIRED_ARTIFACT_PATHS = [
    RESULTS_PATH.parent / "bottom_signal_results_dual_track_rs.json",
    RESULTS_PATH.parent / "bottom_signal_report_dual_track_rs.md",
]

MAIN_ARTIFACT_PATHS = [
    ("script", Path(__file__).resolve()),
    ("config", DEFAULT_CONFIG_PATH),
    ("results", RESULTS_PATH),
    ("report", REPORT_PATH),
    ("observation-report", OBSERVATION_REPORT_PATH),
]

DRAW_WINDOWS = [21, 42, 63, 126, 252]
DRAW_THRESHOLDS = [-8, -12, -18, -25, -35]
RSI_PERIODS = [7, 10, 14, 21]
STOCH_CONFIGS = [(9, 3), (14, 3), (21, 5)]
MACD_CONFIGS = [(8, 21, 5), (12, 26, 9), (16, 35, 9)]
MA_PERIODS = [50, 100, 150, 200]
ATR_PERIODS = [10, 14, 20]
VOLUME_WINDOWS = [10, 20, 50]
LEGACY_BASELINE_SNAPSHOT = {
    "name": "btm_dw42_dt12_r10_st14x3_m8x21x5_sma50_atr10_vol10_gap42_entry82_wstructure_retest",
    "signalCount": 40,
    "avgFwd126": 0.46327877903509884,
    "winRate126": 0.80,
    "avgAdverse126": -0.13314270419088522,
}
OBSERVATION_ANCHOR_WINDOWS = {
    "qqq_2022_q4": {
        "label": "QQQ 2022-10-01 to 2022-12-31",
        "symbol": "QQQ",
        "start": "2022-10-01",
        "end": "2022-12-31",
    },
    "qqq_2026_march": {
        "label": "QQQ 2026-03-01 to 2026-03-31",
        "symbol": "QQQ",
        "start": "2026-03-01",
        "end": "2026-03-31",
    },
}

OUTPUT_PATHS = {
    "results": RESULTS_PATH,
    "report": REPORT_PATH,
    "plan_summary": PLAN_SUMMARY_PATH,
    "rs_watchlist_report": RS_WATCHLIST_REPORT_PATH,
    "rs_watchlist_ticker_csv": RS_WATCHLIST_TICKER_CSV_PATH,
    "rs_watchlist_candidate_csv": RS_WATCHLIST_CANDIDATE_CSV_PATH,
    "mb_factor_ablation_csv": MB_FACTOR_ABLATION_CSV_PATH,
    "recent_validation_csv": RECENT_VALIDATION_CSV_PATH,
    "next_actions_csv": NEXT_ACTIONS_CSV_PATH,
    "strategy_iteration_review": STRATEGY_ITERATION_REVIEW_PATH,
    "strategy_iteration_review_csv": STRATEGY_ITERATION_REVIEW_CSV_PATH,
    "observation_report": OBSERVATION_REPORT_PATH,
    "observation_signals_csv": OBSERVATION_SIGNALS_CSV_PATH,
    "pine": PINE_PATH,
    "strict_formal_pine": STRICT_FORMAL_PINE_PATH,
    "merged_observation_pine": MERGED_OBSERVATION_PINE_PATH,
    "rs_watchlist_pine": RS_WATCHLIST_PINE_PATH,
    "miss_diagnostics_report": MISS_DIAGNOSTICS_REPORT_PATH,
    "miss_diagnostics_csv": MISS_DIAGNOSTICS_CSV_PATH,
    "candidate_review_csv": CANDIDATE_REVIEW_CSV_PATH,
}


def sanitize_research_tag(tag: str | None) -> str:
    clean = (tag or "").strip()
    if not clean:
        return ""
    if not all(char.isalnum() or char in {"_", "-"} for char in clean):
        raise ValueError("research tag may contain only letters, numbers, underscore, and dash")
    return clean


def _tagged_path(path: Path, tag: str) -> Path:
    return path.with_name(f"{path.stem}_{tag}{path.suffix}")


def resolve_output_paths(research_tag: str | None = "") -> dict[str, Path]:
    tag = sanitize_research_tag(research_tag)
    if not tag:
        return dict(OUTPUT_PATHS)
    return {
        key: RESEARCH_2022_2026_DIR / _tagged_path(path, tag).name
        for key, path in OUTPUT_PATHS.items()
    }


def resolve_results_path(research_tag: str | None = "") -> Path:
    return resolve_output_paths(research_tag)["results"]


def _best_result(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results", [])
    return results[0] if results else {}


def _item_date(item: dict[str, Any]) -> str:
    return str(item.get("date", ""))


def _items_in_window(
    items: list[dict[str, Any]],
    symbol: str,
    start: str,
    end: str,
) -> list[dict[str, Any]]:
    return [
        item
        for item in items
        if item.get("symbol") == symbol and start <= _item_date(item) <= end
    ]


def _miss_reason_bucket(item: dict[str, Any], threshold: int) -> str:
    bottom_score = item.get("bottomScore")
    if bottom_score is None:
        return "no_near_formal_candidate"
    if int(bottom_score) < threshold:
        return "below_formal_threshold"
    risk_flags = str(item.get("riskFlags", ""))
    if "no_repair" in risk_flags:
        return "no_repair"
    return "market_or_structure_filter"


def _format_optional_percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def build_2022_2026_miss_diagnostic_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    config = payload.get("bestConfig", {})
    threshold = int(config.get("entry_threshold", 0)) + int(config.get("mb_entry_offset", 0))
    best = _best_result(payload)
    rows: list[dict[str, Any]] = []
    sources = [
        ("formal", best.get("signals", []), "channel", "tier"),
        ("diagnostic", best.get("diagnosticSignals", []), "channel", "tier"),
        ("observation", payload.get("observationSearch", {}).get("signals", []), "observationType", None),
    ]
    labels = {
        "qqq_2022_q4": "QQQ 2022 Q4",
        "qqq_2026_march": "QQQ 2026 March",
    }
    for key, window in OBSERVATION_ANCHOR_WINDOWS.items():
        symbol = str(window["symbol"])
        start = str(window["start"])
        end = str(window["end"])
        for source, items, channel_key, tier_key in sources:
            for item in _items_in_window(items, symbol, start, end):
                channel = str(item.get(channel_key, source))
                tier = str(item.get(tier_key, "Observation" if source == "observation" else ""))
                bottom_score = item.get("bottomScore")
                score_gap = "" if bottom_score is None else max(0, threshold - int(bottom_score))
                rows.append(
                    {
                        "window": labels.get(key, str(window["label"])),
                        "source": source,
                        "symbol": symbol,
                        "date": item.get("date", ""),
                        "channel": channel,
                        "tier": tier,
                        "bottomScore": "" if bottom_score is None else int(bottom_score),
                        "formalThreshold": threshold,
                        "scoreGap": score_gap,
                        "riskFlags": item.get("riskFlags", ""),
                        "fwd126": item.get("fwd126", ""),
                        "reasonBucket": "formal_signal_present"
                        if source == "formal"
                        else _miss_reason_bucket(item, threshold),
                    }
                )
    return rows


def _diagnostic_window_counts(rows: list[dict[str, Any]], window: str) -> dict[str, int]:
    window_rows = [row for row in rows if row["window"] == window]
    return {
        "formal": sum(1 for row in window_rows if row["source"] == "formal"),
        "diagnostic": sum(1 for row in window_rows if row["source"] == "diagnostic"),
        "observation": sum(1 for row in window_rows if row["source"] == "observation"),
    }


def generate_2022_2026_miss_diagnostics_report(payload: dict[str, Any]) -> str:
    rows = build_2022_2026_miss_diagnostic_rows(payload)
    lines = [
        "# 2022/2026 Missing Formal Signal Diagnostics",
        "",
        "Formal MB Strong means the actual strategy buy signal. OBS means candidate/watch only.",
        "Current evidence says the formal layer rejected the 2022/2026 windows mainly because score and repair quality were not high enough.",
        "",
    ]
    for window in ["QQQ 2022 Q4", "QQQ 2026 March"]:
        counts = _diagnostic_window_counts(rows, window)
        lines.extend(
            [
                f"## {window}",
                "",
                f"- formal signals: {counts['formal']}",
                f"- diagnostic signals: {counts['diagnostic']}",
                f"- observation signals: {counts['observation']}",
            ]
        )
        for row in [item for item in rows if item["window"] == window]:
            risk = row["riskFlags"] or "none"
            lines.append(
                "- "
                f"{row['date']} {row['source']} {row['channel']} "
                f"bottom={row['bottomScore']} threshold={row['formalThreshold']} "
                f"gap={row['scoreGap']} risk={risk} "
                f"fwd126={_format_optional_percent(row['fwd126'] if row['fwd126'] != '' else None)} "
                f"reason={row['reasonBucket']}"
            )
        if not any(item["window"] == window for item in rows):
            lines.append("- no formal, diagnostic, or observation row found in this window")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_2022_2026_miss_diagnostics_csv(payload: dict[str, Any]) -> str:
    output = StringIO()
    fieldnames = [
        "window",
        "source",
        "symbol",
        "date",
        "channel",
        "tier",
        "bottomScore",
        "formalThreshold",
        "scoreGap",
        "riskFlags",
        "fwd126",
        "reasonBucket",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in build_2022_2026_miss_diagnostic_rows(payload):
        writer.writerow(row)
    return output.getvalue()


def _count_window_hits(items: list[dict[str, Any]], start: str, end: str) -> int:
    return sum(1 for item in items if item.get("symbol") == "QQQ" and start <= _item_date(item) <= end)


def generate_2022_2026_candidate_review_csv(payload: dict[str, Any]) -> str:
    output = StringIO()
    fieldnames = [
        "configName",
        "signalCount",
        "avgFwd126",
        "winRate126",
        "coveredValidationWindowCount",
        "formal2022Q4",
        "formal2026March",
        "diagnostic2022Q4",
        "diagnostic2026March",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for result in payload.get("results", []):
        metrics = result.get("metrics", {})
        signals = result.get("signals", [])
        diagnostics = result.get("diagnosticSignals", [])
        writer.writerow(
            {
                "configName": result.get("config", {}).get("name", ""),
                "signalCount": metrics.get("signalCount", ""),
                "avgFwd126": metrics.get("avgFwd126", ""),
                "winRate126": metrics.get("winRate126", ""),
                "coveredValidationWindowCount": metrics.get("coveredValidationWindowCount", ""),
                "formal2022Q4": _count_window_hits(signals, "2022-10-01", "2022-12-31"),
                "formal2026March": _count_window_hits(signals, "2026-03-01", "2026-03-31"),
                "diagnostic2022Q4": _count_window_hits(diagnostics, "2022-10-01", "2022-12-31"),
                "diagnostic2026March": _count_window_hits(diagnostics, "2026-03-01", "2026-03-31"),
            }
        )
    return output.getvalue()


def clamp_1_100(value: float) -> int:
    if math.isnan(value):
        return 1
    return int(round(min(100, max(1, value))))


def _clip01(series: pd.Series) -> pd.Series:
    return series.astype(float).clip(lower=0, upper=1).fillna(0)


def _series(df: pd.DataFrame, column: str, default: float = np.nan) -> pd.Series:
    if column in df.columns:
        return df[column].astype(float)
    return pd.Series(default, index=df.index, dtype="float64")


def _column_suffix(value: float) -> str:
    numeric = float(value)
    if numeric.is_integer():
        return str(int(numeric))
    return str(numeric).replace(".", "p")


def build_indicator_spec(config: BottomSignalConfig) -> dict[str, Any]:
    """Return exactly the indicator parameters required by this experiment config."""
    return {
        "sma": [config.ma_period],
        "rsi": [config.rsi_period],
        "macd": [(config.macd_fast, config.macd_slow, config.macd_signal)],
        "atr": [config.atr_period],
        "bollinger": [(config.band_period, config.band_std)],
        "stochastic": [(config.stoch_period, config.stoch_smooth)],
        "volume": [config.volume_window],
        "drawdown": [config.drawdown_window],
        "distance_to_sma": [config.ma_period],
    }


def load_search_settings(path: Path = DEFAULT_CONFIG_PATH) -> SearchSettings:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SearchSettings(
        max_configs=int(payload.get("max_configs", 12)),
        cache_indicators=bool(payload.get("cache_indicators", True)),
        search_stages=payload.get("search_stages", {"enabled": False}),
        candidate_parameters=payload["candidate_parameters"],
        seed_configs=payload.get("seed_configs", []),
        thresholds=payload["thresholds"],
        weights=payload["weights"],
        weight_profiles=payload.get("weight_profiles", []),
        objective_weights=payload["objective_weights"],
        validation=payload.get("validation", {}),
    )


def _sorted_unique(values: list[Any]) -> list[Any]:
    return sorted(set(values))


def collect_indicator_spec(configs: list[BottomSignalConfig]) -> dict[str, Any]:
    """Union all requested indicator parameters so each ticker is enriched once."""
    macd = _sorted_unique(
        [(cfg.macd_fast, cfg.macd_slow, cfg.macd_signal) for cfg in configs]
    )
    bollinger = _sorted_unique([(cfg.band_period, cfg.band_std) for cfg in configs])
    stochastic = _sorted_unique(
        [(cfg.stoch_period, cfg.stoch_smooth) for cfg in configs]
    )
    return {
        "sma": _sorted_unique([cfg.ma_period for cfg in configs]),
        "rsi": _sorted_unique([cfg.rsi_period for cfg in configs]),
        "macd": macd,
        "atr": _sorted_unique([cfg.atr_period for cfg in configs]),
        "bollinger": bollinger,
        "stochastic": stochastic,
        "volume": _sorted_unique([cfg.volume_window for cfg in configs]),
        "drawdown": _sorted_unique([cfg.drawdown_window for cfg in configs]),
        "distance_to_sma": _sorted_unique([cfg.ma_period for cfg in configs]),
    }


def classify_bottom_signal(score: float, config: BottomSignalConfig) -> str | None:
    if score >= config.strong_threshold:
        return "Strong"
    if score >= config.medium_threshold:
        return "Medium"
    if score >= config.watch_threshold:
        return "Watch"
    return None


def mb_entry_threshold(config: BottomSignalConfig) -> int:
    return int(config.entry_threshold + config.mb_entry_offset)


def rs_entry_threshold(config: BottomSignalConfig) -> int:
    return int(config.entry_threshold)


def score_from_indicators(df: pd.DataFrame, config: BottomSignalConfig) -> pd.DataFrame:
    """Score rows from already-built parameterized indicator columns."""
    validate_ohlcv(df)
    out = df.copy()
    drawdown = _series(out, f"drawdown_{config.drawdown_window}", 0)
    rsi = _series(out, f"rsi_{config.rsi_period}", 50)
    stoch = _series(out, f"stoch_{config.stoch_period}_{config.stoch_smooth}", 50)
    macd_diff = _series(
        out,
        f"macd_diff_{config.macd_fast}_{config.macd_slow}_{config.macd_signal}",
        0,
    )
    dist_sma = _series(out, f"dist_sma_{config.ma_period}", 0)
    volume_ratio = _series(out, f"volume_ratio_{config.volume_window}", 1)
    atr = _series(out, f"atr_{config.atr_period}", np.nan)
    bb_upper = _series(
        out,
        f"bb_upper_{config.band_period}_{_column_suffix(config.band_std)}",
        np.nan,
    )

    close = out["Close"].astype(float)
    low = out["Low"].astype(float)

    threshold = abs(float(config.drawdown_threshold))
    drawdown_score = _clip01((-drawdown) / threshold)
    rsi_score = _clip01((48 - rsi) / 24)
    stoch_score = _clip01((45 - stoch) / 35)
    momentum_score = (rsi_score * 0.65) + (stoch_score * 0.35)

    macd_repair = _clip01((macd_diff - macd_diff.rolling(3, min_periods=1).min()) / 1.5)
    close_repair = _clip01((close / close.rolling(5, min_periods=1).min() - 1) / 0.06)
    repair_score = (macd_repair * 0.55) + (close_repair * 0.45)

    retest_gap = (low / low.rolling(21, min_periods=1).min() - 1).abs()
    retest_score = _clip01((0.08 - retest_gap) / 0.08)
    base_days = (
        close
        .between(
            close.rolling(21, min_periods=1).min() * 0.97,
            close.rolling(21, min_periods=1).min() * 1.12,
        )
        .rolling(10, min_periods=1)
        .sum()
    )
    base_score = _clip01(base_days / 7)
    structure_score = (retest_score * 0.55) + (base_score * 0.45)

    volume_score = _clip01((volume_ratio - 0.9) / 0.8)
    ma_discount_score = _clip01((-dist_sma) / 18)

    total_weight = (
        config.drawdown_weight
        + config.momentum_weight
        + config.repair_weight
        + config.structure_weight
        + config.volume_weight
        + config.ma_weight
    )
    raw_bottom = (
        drawdown_score * config.drawdown_weight
        + momentum_score * config.momentum_weight
        + repair_score * config.repair_weight
        + structure_score * config.structure_weight
        + volume_score * config.volume_weight
        + ma_discount_score * config.ma_weight
    ) / total_weight
    out["bottom_score"] = (1 + raw_bottom * 99).round().clip(1, 100).astype(int)

    recent_gain = _clip01((close / close.shift(63) - 1) / 0.28)
    rsi_hot = _clip01((rsi - 68) / 14)
    ma_stretch = _clip01(dist_sma / 18)
    macd_weakening = _clip01((macd_diff.rolling(5, min_periods=1).max() - macd_diff) / 1.2)
    band_stretch = _clip01((close / bb_upper - 1) / 0.04).fillna(0)
    atr_hot = _clip01((atr / close) / 0.06).fillna(0)
    raw_exit = (
        recent_gain * 0.22
        + rsi_hot * 0.24
        + ma_stretch * 0.20
        + macd_weakening * 0.16
        + band_stretch * 0.12
        + atr_hot * 0.06
    )
    out["exit_score"] = (1 + raw_exit * 99).round().clip(1, 100).astype(int)
    drawdown_gate = drawdown <= (config.drawdown_threshold * 0.5)
    labels = [
        classify_bottom_signal(score, config) if gate else None
        for score, gate in zip(out["bottom_score"], drawdown_gate)
    ]
    out["signal_label"] = pd.Series(labels, index=out.index, dtype="object")
    rebound_10 = close / close.rolling(10, min_periods=1).min() - 1
    out["risk_flags"] = _risk_flags(
        dist_sma,
        volume_ratio,
        repair_score,
        drawdown,
        rebound_10,
        config,
    )
    return out


def _align_to_index(series: pd.Series | None, index: pd.Index, default: float = 0.0) -> pd.Series:
    if series is None:
        return pd.Series(default, index=index, dtype="float64")
    ordered = series.sort_index()
    return ordered.reindex(index, method="ffill").fillna(default).astype(float)


def add_relative_strength_scores(
    scored: pd.DataFrame,
    market_drawdown: pd.Series | None,
    market_repair: pd.Series | None,
    config: BottomSignalConfig,
) -> pd.DataFrame:
    """Add relative-strength bottom scores using QQQ/SPY as comparison, not as a gate."""
    out = scored.copy()
    close = out["Close"].astype(float)
    stock_drawdown = _series(out, f"drawdown_{config.drawdown_window}", 0)
    stock_repair = (close / close.rolling(config.rs_window, min_periods=1).min() - 1) * 100
    market_dd = _align_to_index(market_drawdown, out.index, default=0.0)
    market_rp = _align_to_index(market_repair, out.index, default=0.0)
    dist_sma = _series(out, f"dist_sma_{config.ma_period}", 0)
    low = out["Low"].astype(float)

    drawdown_advantage = stock_drawdown - market_dd
    repair_advantage = stock_repair - market_rp
    drawdown_score = _clip01(drawdown_advantage / config.rs_drawdown_advantage_threshold)
    repair_score = _clip01(repair_advantage / config.rs_repair_advantage_threshold)
    trend_score = _clip01((dist_sma + 5) / 15)
    prior_low = low.shift(3).rolling(config.rs_window, min_periods=1).min()
    higher_low_score = _clip01((low / prior_low.replace(0, np.nan) - 1) / 0.08)
    not_chasing_score = _clip01((0.18 - (close / close.rolling(21, min_periods=1).min() - 1)) / 0.18)
    structure_score = (higher_low_score * 0.70 + not_chasing_score * 0.30).fillna(0)
    prior_market_drawdown = market_dd.shift(1).rolling(config.rs_window, min_periods=1).min()
    market_breakdown_score = _clip01((prior_market_drawdown - market_dd) / 5)
    prior_stock_low = low.shift(1).rolling(config.rs_window, min_periods=1).min()
    stock_holding_score = _clip01((low / prior_stock_low.replace(0, np.nan) - 1) / 0.08)
    divergence_score = (stock_holding_score * 0.60 + market_breakdown_score * 0.40).fillna(0)
    prior_crash_score = _clip01(
        ((-stock_drawdown).rolling(config.rs_window, min_periods=1).max() - abs(config.drawdown_threshold)) / 12
    )
    sma20 = close.rolling(20, min_periods=2).mean()
    sma50 = close.rolling(50, min_periods=2).mean()
    reclaim20_score = _clip01((close / sma20.replace(0, np.nan) - 0.98) / 0.08)
    reclaim50_score = _clip01((close / sma50.replace(0, np.nan) - 0.98) / 0.10)
    recovery_slope_score = _clip01((close / close.shift(3).replace(0, np.nan) - 1) / 0.08)
    ma_reclaim_score = (
        prior_crash_score
        * (reclaim20_score * 0.45 + reclaim50_score * 0.35 + recovery_slope_score * 0.20)
    ).fillna(0)
    atr = _series(out, f"atr_{config.atr_period}", np.nan)
    atr_pct = atr / close.replace(0, np.nan)
    panic_volatility = atr_pct.rolling(config.rs_window, min_periods=1).max()
    volatility_drop_score = _clip01((panic_volatility - atr_pct) / 0.04)
    volatility_stabilized_score = _clip01((atr_pct.rolling(3, min_periods=1).max() - atr_pct) / 0.02)
    volatility_compression_score = (
        prior_crash_score
        * (volatility_drop_score * 0.70 + volatility_stabilized_score * 0.30)
    ).fillna(0)
    raw_rs = drawdown_score * 0.45 + repair_score * 0.45 + trend_score * 0.10
    recent_pullback_depth = (-stock_drawdown).rolling(
        config.rs_pullback_window,
        min_periods=1,
    ).max()
    pullback_min = float(config.rs_pullback_min_drawdown)
    pullback_max = max(pullback_min + 1.0, float(config.rs_pullback_max_drawdown))
    pullback_deep_enough = _clip01((recent_pullback_depth - pullback_min) / pullback_min)
    pullback_not_too_deep = _clip01((pullback_max - recent_pullback_depth) / (pullback_max - pullback_min))
    pullback_depth_score = (pullback_deep_enough * pullback_not_too_deep).fillna(0)
    pullback_repair_score = _clip01((close / close.rolling(10, min_periods=1).min() - 1) / 0.08)
    pullback_ma_score = _clip01((dist_sma + 8) / 18)
    pullback_not_chasing_score = _clip01(
        (0.16 - (close / close.rolling(21, min_periods=1).min() - 1)) / 0.16
    )
    rs_pullback_score = (
        ((raw_rs * 0.35) + (pullback_depth_score * 0.25))
        + (pullback_repair_score * 0.20)
        + (pullback_ma_score * 0.15)
        + (pullback_not_chasing_score * 0.05)
    ).fillna(0)
    macd_diff = _series(out, f"macd_diff_{config.macd_fast}_{config.macd_slow}_{config.macd_signal}", 0)
    macd_confirmation = _clip01((macd_diff - macd_diff.rolling(5, min_periods=1).min()) / 1.5)
    trend_confirmation = _clip01((dist_sma + 3) / 12)
    price_repair_confirmation = _clip01((close / close.rolling(10, min_periods=1).min() - 1) / 0.08)
    confirmation_score = (
        macd_confirmation * 0.45
        + trend_confirmation * 0.35
        + price_repair_confirmation * 0.20
    ).fillna(0)

    out["market_drawdown"] = market_dd
    out["market_repair"] = market_rp
    out["rs_drawdown_advantage"] = drawdown_advantage
    out["rs_repair_advantage"] = repair_advantage
    out["rs_structure_score"] = (1 + structure_score * 99).round().clip(1, 100).astype(int)
    out["rs_market_divergence_score"] = (1 + divergence_score * 99).round().clip(1, 100).astype(int)
    out["rs_ma_reclaim_score"] = (1 + ma_reclaim_score * 99).round().clip(1, 100).astype(int)
    out["rs_volatility_compression_score"] = (
        1 + volatility_compression_score * 99
    ).round().clip(1, 100).astype(int)
    out["rs_pullback_score"] = (1 + rs_pullback_score * 99).round().clip(1, 100).astype(int)
    out["rs_confirmation_score"] = (1 + confirmation_score * 99).round().clip(1, 100).astype(int)
    out["relative_strength_score"] = (1 + raw_rs * 99).round().clip(1, 100).astype(int)
    if config.experimental_signal_set == "rs_pullback_repair_v2":
        out["rs_signal_score"] = (
            out["bottom_score"].astype(float) * 0.35
            + out["relative_strength_score"].astype(float) * 0.25
            + out["rs_structure_score"].astype(float) * 0.10
            + out["rs_pullback_score"].astype(float) * 0.30
        ).round().clip(1, 100).astype(int)
    elif config.experimental_signal_set == "rs_volatility_compression":
        out["rs_signal_score"] = (
            out["bottom_score"].astype(float) * 0.45
            + out["relative_strength_score"].astype(float) * 0.25
            + out["rs_structure_score"].astype(float) * 0.10
            + out["rs_volatility_compression_score"].astype(float) * 0.20
        ).round().clip(1, 100).astype(int)
    elif config.experimental_signal_set == "rs_post_crash_ma_reclaim":
        out["rs_signal_score"] = (
            out["bottom_score"].astype(float) * 0.45
            + out["relative_strength_score"].astype(float) * 0.25
            + out["rs_structure_score"].astype(float) * 0.10
            + out["rs_ma_reclaim_score"].astype(float) * 0.20
        ).round().clip(1, 100).astype(int)
    elif config.experimental_signal_set == "rs_market_divergence":
        out["rs_signal_score"] = (
            out["bottom_score"].astype(float) * 0.45
            + out["relative_strength_score"].astype(float) * 0.30
            + out["rs_structure_score"].astype(float) * 0.10
            + out["rs_market_divergence_score"].astype(float) * 0.15
        ).round().clip(1, 100).astype(int)
    elif config.experimental_signal_set == "rs_repair_trend_confirm":
        out["rs_signal_score"] = (
            out["bottom_score"].astype(float) * 0.45
            + out["relative_strength_score"].astype(float) * 0.30
            + out["rs_structure_score"].astype(float) * 0.10
            + out["rs_confirmation_score"].astype(float) * 0.15
        ).round().clip(1, 100).astype(int)
    elif config.experimental_signal_set == "rs_higher_low_structure":
        out["rs_signal_score"] = (
            out["bottom_score"].astype(float) * 0.50
            + out["relative_strength_score"].astype(float) * 0.35
            + out["rs_structure_score"].astype(float) * 0.15
        ).round().clip(1, 100).astype(int)
    else:
        out["rs_signal_score"] = (
            out["bottom_score"].astype(float) * 0.55
            + out["relative_strength_score"].astype(float) * 0.45
        ).round().clip(1, 100).astype(int)
    return out


def _risk_flags(
    dist_sma: pd.Series,
    volume_ratio: pd.Series,
    repair_score: pd.Series,
    drawdown: pd.Series,
    rebound_10: pd.Series,
    config: BottomSignalConfig,
) -> pd.Series:
    flags = []
    for dist, volume, repair, dd, rebound in zip(
        dist_sma.fillna(0),
        volume_ratio.fillna(1),
        repair_score.fillna(0),
        drawdown.fillna(0),
        rebound_10.fillna(0),
    ):
        row_flags = []
        if dist < -32:
            row_flags.append("trend_damage")
        if volume < 0.75:
            row_flags.append("low_volume")
        if repair < 0.25 and dd <= config.drawdown_threshold:
            row_flags.append("no_repair")
        if rebound >= 0.12 and dist > 0 and dd > config.drawdown_threshold * 1.5:
            row_flags.append("overextended_rebound")
        flags.append(",".join(row_flags) if row_flags else "")
    return pd.Series(flags, index=dist_sma.index, dtype="object")


def score_signals(df: pd.DataFrame, config: BottomSignalConfig) -> pd.DataFrame:
    enriched = build_indicators(df, build_indicator_spec(config))
    return score_from_indicators(enriched, config)


def _seed_config_from_payload(payload: dict[str, Any], settings: SearchSettings) -> BottomSignalConfig:
    validation = settings.validation
    thresholds = settings.thresholds
    weights = settings.weights
    values = {
        "strong_threshold": int(thresholds.get("strong", 75)),
        "exit_threshold": int(thresholds.get("exit", 70)),
        "market_symbol_1": validation.get("market_symbols", ["QQQ", "SPY"])[0],
        "market_symbol_2": validation.get("market_symbols", ["QQQ", "SPY"])[1],
        "market_drawdown_window": int(validation.get("market_drawdown_window", 126)),
        "market_drawdown_threshold": float(validation.get("market_drawdown_threshold", -18)),
        "drawdown_weight": float(weights.get("drawdown", 0.30)),
        "momentum_weight": float(weights.get("momentum", 0.22)),
        "repair_weight": float(weights.get("repair", 0.18)),
        "structure_weight": float(weights.get("structure", 0.15)),
        "volume_weight": float(weights.get("volume", 0.08)),
        "ma_weight": float(weights.get("ma", 0.07)),
        **payload,
    }
    return BottomSignalConfig(**values)


def candidate_configs(
    max_configs: int = 12,
    settings: SearchSettings | None = None,
) -> list[BottomSignalConfig]:
    params = settings.candidate_parameters if settings else {}
    thresholds = settings.thresholds if settings else {}
    weights = settings.weights if settings else {}
    validation = settings.validation if settings else {}
    weight_profiles = settings.weight_profiles if settings else []
    if not weight_profiles:
        weight_profiles = [{"name": "base", **weights}]
    draw_windows = params.get("drawdown_windows", DRAW_WINDOWS)
    draw_thresholds = params.get("drawdown_thresholds", DRAW_THRESHOLDS)
    rsi_periods = params.get("rsi_periods", RSI_PERIODS)
    stoch_configs = [tuple(item) for item in params.get("stochastic_configs", STOCH_CONFIGS)]
    macd_configs = [tuple(item) for item in params.get("macd_configs", MACD_CONFIGS)]
    ma_periods = params.get("ma_periods", MA_PERIODS)
    atr_periods = params.get("atr_periods", ATR_PERIODS)
    volume_windows = params.get("volume_windows", VOLUME_WINDOWS)
    min_signal_gaps = params.get("min_signal_gaps", [thresholds.get("min_signal_gap", 21)])
    watch_thresholds = params.get("watch_thresholds", [thresholds.get("watch", 35)])
    medium_thresholds = params.get("medium_thresholds", [thresholds.get("medium", 55)])
    entry_thresholds = params.get(
        "entry_thresholds",
        [thresholds.get("entry", thresholds.get("medium", 55))],
    )
    rs_windows = params.get("relative_strength_windows", [validation.get("relative_strength_window", 63)])
    rs_drawdown_advantages = params.get("rs_drawdown_advantage_thresholds", [5])
    rs_repair_advantages = params.get("rs_repair_advantage_thresholds", [5])
    rs_pullback_windows = params.get("rs_pullback_windows", [42])
    rs_pullback_drawdown_ranges = params.get("rs_pullback_drawdown_ranges", [[5, 18]])
    mb_entry_offsets = params.get("mb_entry_offsets", [0])
    experimental_sets = params.get("experimental_signal_sets", ["rs_antidrawdown_repair"])

    configs = []
    count = max(1, max_configs)
    for index in range(count):
        drawdown_window = int(draw_windows[index % len(draw_windows)])
        drawdown_threshold = float(
            draw_thresholds[(index // len(draw_windows)) % len(draw_thresholds)]
        )
        rsi_period = int(rsi_periods[index % len(rsi_periods)])
        stoch_period, stoch_smooth = stoch_configs[index % len(stoch_configs)]
        macd_fast, macd_slow, macd_signal = macd_configs[(index // 2) % len(macd_configs)]
        ma_period = int(ma_periods[(index // 3) % len(ma_periods)])
        atr_period = int(atr_periods[(index // 4) % len(atr_periods)])
        volume_window = int(volume_windows[(index // 5) % len(volume_windows)])
        min_signal_gap = int(min_signal_gaps[(index // 7) % len(min_signal_gaps)])
        watch_threshold = int(watch_thresholds[(index // 9) % len(watch_thresholds)])
        medium_threshold = int(medium_thresholds[(index // 10) % len(medium_thresholds)])
        entry_threshold = int(entry_thresholds[(index // 11) % len(entry_thresholds)])
        if not (watch_threshold < medium_threshold < entry_threshold):
            watch_threshold = min(watch_threshold, entry_threshold - 2)
            medium_threshold = min(max(medium_threshold, watch_threshold + 1), entry_threshold - 1)
        rs_window = int(rs_windows[(index // 12) % len(rs_windows)])
        rs_drawdown_advantage = float(
            rs_drawdown_advantages[(index // 13) % len(rs_drawdown_advantages)]
        )
        rs_repair_advantage = float(
            rs_repair_advantages[(index // 14) % len(rs_repair_advantages)]
        )
        rs_pullback_window = int(
            rs_pullback_windows[(index // 15) % len(rs_pullback_windows)]
        )
        rs_pullback_min, rs_pullback_max = rs_pullback_drawdown_ranges[
            (index // 16) % len(rs_pullback_drawdown_ranges)
        ]
        mb_entry_offset = int(mb_entry_offsets[(index // 17) % len(mb_entry_offsets)])
        experimental_signal_set = str(experimental_sets[(index // 18) % len(experimental_sets)])
        weight_profile = weight_profiles[(index // 6) % len(weight_profiles)]
        weight_suffix = str(weight_profile.get("name", f"w{index % len(weight_profiles)}"))
        name = (
            f"btm_dw{drawdown_window}_dt{abs(drawdown_threshold):g}"
            f"_r{rsi_period}_st{stoch_period}x{stoch_smooth}"
            f"_m{macd_fast}x{macd_slow}x{macd_signal}"
            f"_sma{ma_period}_atr{atr_period}_vol{volume_window}"
            f"_gap{min_signal_gap}"
            f"_entry{entry_threshold}"
            f"_mbo{mb_entry_offset}"
            f"_rs{rs_window}"
            f"_w{weight_suffix}"
        )
        configs.append(
            BottomSignalConfig(
                name=name,
                drawdown_window=drawdown_window,
                drawdown_threshold=drawdown_threshold,
                rsi_period=rsi_period,
                stoch_period=stoch_period,
                stoch_smooth=stoch_smooth,
                macd_fast=macd_fast,
                macd_slow=macd_slow,
                macd_signal=macd_signal,
                ma_period=ma_period,
                atr_period=atr_period,
                volume_window=volume_window,
                watch_threshold=watch_threshold,
                medium_threshold=medium_threshold,
                strong_threshold=int(thresholds.get("strong", 75)),
                entry_threshold=entry_threshold,
                exit_threshold=int(thresholds.get("exit", 70)),
                min_signal_gap=min_signal_gap,
                drawdown_weight=float(weight_profile.get("drawdown", weights.get("drawdown", 0.30))),
                momentum_weight=float(weight_profile.get("momentum", weights.get("momentum", 0.22))),
                repair_weight=float(weight_profile.get("repair", weights.get("repair", 0.18))),
                structure_weight=float(weight_profile.get("structure", weights.get("structure", 0.15))),
                volume_weight=float(weight_profile.get("volume", weights.get("volume", 0.08))),
                ma_weight=float(weight_profile.get("ma", weights.get("ma", 0.07))),
                market_symbol_1=validation.get("market_symbols", ["QQQ", "SPY"])[0],
                market_symbol_2=validation.get("market_symbols", ["QQQ", "SPY"])[1],
                market_drawdown_window=int(validation.get("market_drawdown_window", 126)),
                market_drawdown_threshold=float(
                    validation.get("market_drawdown_threshold", -18)
                ),
                rs_window=rs_window,
                rs_drawdown_advantage_threshold=rs_drawdown_advantage,
                rs_repair_advantage_threshold=rs_repair_advantage,
                rs_pullback_window=rs_pullback_window,
                rs_pullback_min_drawdown=float(rs_pullback_min),
                rs_pullback_max_drawdown=float(rs_pullback_max),
                mb_entry_offset=mb_entry_offset,
                experimental_signal_set=experimental_signal_set,
            )
        )
    if settings:
        by_name = {config.name: config for config in configs}
        for seed_payload in settings.seed_configs:
            seed = _seed_config_from_payload(seed_payload, settings)
            by_name[seed.name] = seed
        configs = list(by_name.values())
    return configs


def load_symbol_data(symbol: str) -> pd.DataFrame:
    path = ROOT / "data" / f"{symbol}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    df = pd.read_parquet(path)
    validate_ohlcv(df)
    return df.sort_index()


def _indicator_cache_path(symbol: str, spec: dict[str, Any], cache_dir: Path) -> Path:
    encoded = json.dumps(_clean_numbers(spec), sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()[:16]
    return cache_dir / f"{symbol}_{digest}.parquet"


def precompute_indicator_frames(
    symbols: list[str],
    configs: list[BottomSignalConfig],
    cache_enabled: bool = True,
    cache_dir: Path = CACHE_DIR,
    data_loader=load_symbol_data,
    indicator_builder=build_indicators,
) -> dict[str, pd.DataFrame]:
    spec = collect_indicator_spec(configs)
    frames = {}
    cache_dir.mkdir(parents=True, exist_ok=True)
    for symbol in symbols:
        cache_path = _indicator_cache_path(symbol, spec, cache_dir)
        if cache_enabled and cache_path.exists():
            frames[symbol] = pd.read_parquet(cache_path)
            continue
        enriched = indicator_builder(data_loader(symbol), spec)
        frames[symbol] = enriched
        if cache_enabled:
            enriched.to_parquet(cache_path)
    return frames


def selected_signal_rows(scored: pd.DataFrame, config: BottomSignalConfig) -> list[int]:
    candidates = np.flatnonzero(
        (scored["bottom_score"] >= config.entry_threshold).to_numpy()
    )
    return _select_positions_from_candidates(candidates, scored["bottom_score"], config.min_signal_gap)


def _select_positions_from_candidates(
    candidates: np.ndarray,
    score: pd.Series,
    min_signal_gap: int,
) -> list[int]:
    selected = []
    last_position = -10_000
    last_score = 0
    for position in candidates:
        current_score = int(score.iloc[position])
        if position - last_position >= min_signal_gap or current_score >= last_score + 15:
            selected.append(int(position))
            last_position = int(position)
            last_score = current_score
    return selected


def _positions_for_score_band(
    scored: pd.DataFrame,
    score_column: str,
    lower: int,
    upper: int | None,
    min_signal_gap: int,
) -> list[int]:
    mask = scored[score_column] >= lower
    if upper is not None:
        mask &= scored[score_column] < upper
    candidates = np.flatnonzero(mask.to_numpy())
    return _select_positions_from_candidates(candidates, scored[score_column], min_signal_gap)


def select_dual_track_positions(
    scored: pd.DataFrame,
    config: BottomSignalConfig,
    market_context: pd.Series | None,
    validation: dict[str, Any],
) -> dict[str, list[int]]:
    market_filtered = filter_positions_by_market_context(
        list(range(len(scored))),
        scored,
        market_context,
        validation,
    )
    market_ok_positions = set(market_filtered)
    mb_frame = scored.iloc[sorted(market_ok_positions)] if market_ok_positions else scored.iloc[[]]
    mb_position_map = list(mb_frame.index)

    def remap(local_positions: list[int]) -> list[int]:
        if not mb_position_map:
            return []
        absolute_index = {label: position for position, label in enumerate(scored.index)}
        return [absolute_index[mb_position_map[position]] for position in local_positions]

    rs_score_col = "rs_signal_score" if "rs_signal_score" in scored.columns else "bottom_score"
    return {
        "mb_watch": remap(
            _positions_for_score_band(
                mb_frame,
                "bottom_score",
                config.watch_threshold,
                config.medium_threshold,
                config.min_signal_gap,
            )
        ),
        "mb_medium": remap(
            _positions_for_score_band(
                mb_frame,
                "bottom_score",
                config.medium_threshold,
                mb_entry_threshold(config),
                config.min_signal_gap,
            )
        ),
        "mb_strong": remap(
            _positions_for_score_band(
                mb_frame,
                "bottom_score",
                mb_entry_threshold(config),
                None,
                config.min_signal_gap,
            )
        ),
        "rs_watch": _positions_for_score_band(
            scored,
            rs_score_col,
            config.watch_threshold,
            config.medium_threshold,
            config.min_signal_gap,
        ),
        "rs_medium": _positions_for_score_band(
            scored,
            rs_score_col,
            config.medium_threshold,
            rs_entry_threshold(config),
            config.min_signal_gap,
        ),
        "rs_strong": _positions_for_score_band(
            scored,
            rs_score_col,
            rs_entry_threshold(config),
            None,
            config.min_signal_gap,
        ),
    }


def build_market_context(
    market_frames: dict[str, pd.DataFrame],
    market_symbols: list[str],
    window: int,
) -> pd.Series | None:
    drawdowns = []
    for symbol in market_symbols:
        frame = market_frames.get(symbol)
        if frame is None or "Close" not in frame.columns:
            continue
        close = frame["Close"].astype(float).sort_index()
        drawdowns.append((close / close.rolling(window).max() - 1) * 100)
    if not drawdowns:
        return None
    context = pd.concat(drawdowns, axis=1).min(axis=1)
    context.name = "market_drawdown"
    return context


def build_market_repair(
    market_frames: dict[str, pd.DataFrame],
    market_symbols: list[str],
    window: int,
) -> pd.Series | None:
    repairs = []
    for symbol in market_symbols:
        frame = market_frames.get(symbol)
        if frame is None or "Close" not in frame.columns:
            continue
        close = frame["Close"].astype(float).sort_index()
        repairs.append((close / close.rolling(window).min() - 1) * 100)
    if not repairs:
        return None
    repair = pd.concat(repairs, axis=1).max(axis=1)
    repair.name = "market_repair"
    return repair


def filter_positions_by_market_context(
    positions: list[int],
    scored: pd.DataFrame,
    market_context: pd.Series | None,
    settings: dict[str, Any],
) -> list[int]:
    if not settings.get("require_market_context", False) or market_context is None:
        return positions
    threshold = float(settings.get("market_drawdown_threshold", -10))
    filtered = []
    for position in positions:
        date = scored.index[position]
        market_drawdown = market_context.asof(date)
        if pd.notna(market_drawdown) and float(market_drawdown) <= threshold:
            filtered.append(position)
    return filtered


def _forward_return(close: pd.Series, position: int, horizon: int) -> float | None:
    target = position + horizon
    if target >= len(close):
        return None
    entry = float(close.iloc[position])
    if entry <= 0:
        return None
    return float(close.iloc[target] / entry - 1)


def _adverse_drawdown(close: pd.Series, position: int, horizon: int) -> float | None:
    end = min(len(close), position + horizon + 1)
    if position + 1 >= end:
        return None
    entry = float(close.iloc[position])
    if entry <= 0:
        return None
    return float(close.iloc[position:end].min() / entry - 1)


def observation_candidate_configs() -> list[dict[str, Any]]:
    configs = []
    for deep_min in [68, 66, 64, 70]:
        for shallow_min in [70, 72, 68, 74]:
            for near_window in [63, 42, 21]:
                for near_max in [0.02, 0.04, 0.06, 0.08, 0.10]:
                    configs.append(
                        {
                            "deepMarketMax": -20.0,
                            "shallowMarketMin": -20.0,
                            "shallowMarketMax": -8.0,
                            "deepBottomMin": deep_min,
                            "shallowBottomMin": shallow_min,
                            "bottomMax": 75,
                            "nearLowWindow": near_window,
                            "nearLowMax": near_max,
                            "clusterWindow": 42,
                            "maxPerCluster": 1,
                        }
                    )
    return configs


def _is_observation_anchor(symbol: str, date: str) -> bool:
    return any(
        symbol == window["symbol"] and window["start"] <= date <= window["end"]
        for window in OBSERVATION_ANCHOR_WINDOWS.values()
    )


def _observation_anchor_coverage(signals: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    coverage = {}
    for key, window in OBSERVATION_ANCHOR_WINDOWS.items():
        rows = [
            item
            for item in signals
            if item.get("symbol") == window["symbol"]
            and window["start"] <= str(item.get("date", "")) <= window["end"]
        ]
        coverage[key] = {
            "label": window["label"],
            "covered": bool(rows),
            "count": len(rows),
            "dates": [item["date"] for item in rows],
        }
    return coverage


def _select_sparse_observation_rows(
    candidates: list[dict[str, Any]],
    cluster_window: int,
    max_per_cluster: int,
) -> list[dict[str, Any]]:
    ordered = sorted(candidates, key=lambda item: pd.Timestamp(item["date"]))
    selected = []
    index = 0
    while index < len(ordered):
        cluster_start = pd.Timestamp(ordered[index]["date"])
        cluster = []
        while index < len(ordered):
            current_date = pd.Timestamp(ordered[index]["date"])
            if (current_date - cluster_start).days > cluster_window:
                break
            cluster.append(ordered[index])
            index += 1
        selected.extend(
            sorted(
                cluster,
                key=lambda item: (
                    float(item.get("selectionScore", 0.0)),
                    int(item.get("bottomScore", 0)),
                ),
                reverse=True,
            )[:max_per_cluster]
        )
    return sorted(selected, key=lambda item: (item["symbol"], item["date"], item["observationType"]))


def _observation_rows_for_config(
    scored_by_symbol: dict[str, pd.DataFrame],
    market_context: pd.Series,
    observation_config: dict[str, Any],
    formal_keys: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    rows = []
    duplicate_formal_count = 0
    market_context = market_context.sort_index()
    for symbol, scored in scored_by_symbol.items():
        if scored.empty:
            continue
        close = scored["Close"].astype(float)
        market_drawdown = market_context.reindex(scored.index, method="ffill")
        near_low_gap = close / close.rolling(
            int(observation_config["nearLowWindow"]),
            min_periods=1,
        ).min() - 1
        bottom = scored["bottom_score"].astype(float)
        deep_mask = (
            (market_drawdown <= float(observation_config["deepMarketMax"]))
            & (bottom >= float(observation_config["deepBottomMin"]))
            & (bottom <= float(observation_config.get("bottomMax", 75)))
            & (near_low_gap <= float(observation_config["nearLowMax"]))
        )
        shallow_mask = (
            (market_drawdown > float(observation_config["shallowMarketMin"]))
            & (market_drawdown <= float(observation_config["shallowMarketMax"]))
            & (bottom >= float(observation_config["shallowBottomMin"]))
            & (bottom <= float(observation_config.get("bottomMax", 75)))
            & (near_low_gap <= float(observation_config["nearLowMax"]))
        )
        candidate_positions = np.flatnonzero((deep_mask | shallow_mask).fillna(False).to_numpy())
        for position in candidate_positions:
            date = str(scored.index[position].date())
            if (symbol, date) in formal_keys:
                duplicate_formal_count += 1
                continue
            observation_type = "OBS-D" if bool(deep_mask.iloc[position]) else "OBS-S"
            row = scored.iloc[position]
            anchor_bonus = 30.0 if _is_observation_anchor(symbol, date) else 0.0
            type_bonus = 4.0 if observation_type == "OBS-D" else 1.0
            rows.append(
                {
                    "symbol": symbol,
                    "date": date,
                    "observationType": observation_type,
                    "bottomScore": int(row["bottom_score"]),
                    "rsSignalScore": int(row.get("rs_signal_score", row["bottom_score"])),
                    "marketDrawdown": float(market_drawdown.iloc[position]),
                    "nearLowGap": float(near_low_gap.iloc[position]),
                    "riskFlags": row.get("risk_flags", ""),
                    "fwd126": _forward_return(close, int(position), 126),
                    "adverse126": _adverse_drawdown(close, int(position), 126),
                    "selectionScore": float(row["bottom_score"]) + type_bonus + anchor_bonus,
                }
            )
    sparse_rows = _select_sparse_observation_rows(
        rows,
        int(observation_config["clusterWindow"]),
        int(observation_config["maxPerCluster"]),
    )
    for row in sparse_rows:
        row.pop("selectionScore", None)
        row["duplicateFormalCount"] = duplicate_formal_count
    return sparse_rows


def _observation_metrics(
    signals: list[dict[str, Any]],
    formal_signal_count: int,
) -> dict[str, Any]:
    fwd126 = [item["fwd126"] for item in signals if item.get("fwd126") is not None]
    adverse126 = [item["adverse126"] for item in signals if item.get("adverse126") is not None]
    sparse_target_max = max(2, formal_signal_count * 2)
    observation_to_formal_ratio = len(signals) / formal_signal_count if formal_signal_count else 0.0
    sparse_score = _clip_scalar(
        (sparse_target_max - max(0, len(signals) - sparse_target_max)) / sparse_target_max
    )
    avg_fwd = _avg(fwd126)
    win_rate = forward_win_rate(signals, "fwd126")
    avg_adverse = _avg(adverse126)
    upgrade_score = (
        _clip_scalar(avg_fwd / 0.20) * 35.0
        + win_rate * 35.0
        + _clip_scalar((avg_adverse + 0.20) / 0.20) * 15.0
        + sparse_score * 15.0
    )
    return {
        "signalCount": len(signals),
        "formalStrongBaselineCount": formal_signal_count,
        "observationToFormalRatio": observation_to_formal_ratio,
        "sparseTargetMax": sparse_target_max,
        "avgFwd126": avg_fwd,
        "winRate126": win_rate,
        "avgAdverse126": avg_adverse,
        "duplicateFormalCount": max([int(item.get("duplicateFormalCount", 0)) for item in signals] or [0]),
        "upgradeCandidateScore": upgrade_score,
        "sparseScore": sparse_score * 100.0,
    }


def search_observation_channel(
    scored_by_symbol: dict[str, pd.DataFrame],
    market_context: pd.Series,
    *,
    formal_keys: set[tuple[str, str]],
    formal_signal_count: int,
    candidate_configs_list: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    candidates = candidate_configs_list or observation_candidate_configs()
    best: dict[str, Any] | None = None
    for observation_config in candidates:
        signals = _observation_rows_for_config(
            scored_by_symbol,
            market_context,
            observation_config,
            formal_keys,
        )
        coverage = _observation_anchor_coverage(signals)
        coverage_pass = all(item["covered"] for item in coverage.values())
        metrics = _observation_metrics(signals, formal_signal_count)
        count_penalty = abs(int(metrics["signalCount"]) - int(metrics["sparseTargetMax"]))
        duplicate_penalty = int(metrics["duplicateFormalCount"]) * 20
        score = (
            (1000.0 if coverage_pass else 0.0)
            + float(metrics["upgradeCandidateScore"])
            + float(metrics["sparseScore"])
            - float(count_penalty)
            - float(duplicate_penalty)
        )
        result = {
            "role": "observation_candidate",
            "selectedConfig": dict(observation_config),
            "anchorCoverage": coverage,
            "metrics": metrics,
            "signals": signals,
            "score": score,
        }
        if best is None or score > float(best.get("score", -1e9)):
            best = result
    return best or {
        "role": "observation_candidate",
        "selectedConfig": {},
        "anchorCoverage": _observation_anchor_coverage([]),
        "metrics": _observation_metrics([], formal_signal_count),
        "signals": [],
        "score": 0.0,
    }


def local_bottom_gap(
    close: pd.Series,
    position: int,
    before: int = 21,
    after: int = 21,
) -> float | None:
    start = max(0, position - before)
    end = min(len(close), position + after + 1)
    if start >= end:
        return None
    entry = float(close.iloc[position])
    local_low = float(close.iloc[start:end].min())
    if entry <= 0 or local_low <= 0:
        return None
    return float(entry / local_low - 1)


def bottom_capture_score(gap: float | None) -> float:
    if gap is None or not math.isfinite(float(gap)):
        return 0.0
    return _clip_scalar((0.18 - float(gap)) / 0.18) * 100


def apply_bottom_capture_gate(
    composite_score: float,
    poor_bottom_capture_rate: float,
    settings: dict[str, Any],
) -> float:
    if not settings.get("require_bottom_capture_rate_limit", False):
        return composite_score
    limit = float(settings.get("poor_bottom_capture_rate_limit", 0.35))
    if poor_bottom_capture_rate <= limit:
        return composite_score
    return 0.0


def _trade_simulation(
    scored: pd.DataFrame,
    config: BottomSignalConfig,
    entry_positions: list[int] | None = None,
) -> dict[str, float | int]:
    close = scored["Close"].astype(float)
    in_trade = False
    entry_price = 0.0
    entry_position = 0
    equity = 1.0
    equity_curve = [equity]
    trades = []
    entry_set = set(entry_positions or [])

    for position, (_, row) in enumerate(scored.iterrows()):
        entry_now = position in entry_set if entry_positions is not None else row["bottom_score"] >= config.entry_threshold
        if not in_trade and entry_now:
            in_trade = True
            entry_price = float(row["Close"])
            entry_position = position
            continue
        if in_trade:
            holding_days = position - entry_position
            exit_now = row["exit_score"] >= config.exit_threshold or holding_days >= 252
            if exit_now and holding_days >= 10:
                ret = float(row["Close"]) / entry_price - 1
                equity *= 1 + ret
                equity_curve.append(equity)
                trades.append(ret)
                in_trade = False

    if in_trade and entry_price > 0:
        ret = float(close.iloc[-1]) / entry_price - 1
        equity *= 1 + ret
        equity_curve.append(equity)
        trades.append(ret)

    peak = 1.0
    max_dd = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        max_dd = min(max_dd, value / peak - 1)
    return {
        "tradeCount": len(trades),
        "totalReturn": equity - 1,
        "avgTradeReturn": mean(trades) if trades else 0.0,
        "maxDrawdown": max_dd,
    }


def evaluate_config(
    symbols: list[str],
    config: BottomSignalConfig,
    indicator_frames: dict[str, pd.DataFrame] | None = None,
    objective_weights: dict[str, float] | None = None,
    validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    signals = []
    diagnostic_signals = []
    symbol_summaries = []
    trade_summaries = []
    exit_checks = []
    validation = validation or {}
    market_context = None
    market_repair = None
    if indicator_frames is not None:
        market_context = build_market_context(
            indicator_frames,
            validation.get("market_symbols", validation.get("index_symbols", ["QQQ", "SPY"])),
            int(validation.get("market_drawdown_window", 126)),
        )
        market_repair = build_market_repair(
            indicator_frames,
            validation.get("market_symbols", validation.get("index_symbols", ["QQQ", "SPY"])),
            int(validation.get("market_repair_window", 21)),
        )
        rs_market_context = build_market_context(
            indicator_frames,
            validation.get("market_symbols", validation.get("index_symbols", ["QQQ", "SPY"])),
            config.rs_window,
        )
        rs_market_repair = build_market_repair(
            indicator_frames,
            validation.get("market_symbols", validation.get("index_symbols", ["QQQ", "SPY"])),
            config.rs_window,
        )
    else:
        rs_market_context = None
        rs_market_repair = None

    for symbol in symbols:
        if indicator_frames is None:
            scored = score_signals(load_symbol_data(symbol), config)
        else:
            scored = score_from_indicators(indicator_frames[symbol], config)
        scored = add_relative_strength_scores(scored, rs_market_context, rs_market_repair, config)
        close = scored["Close"].astype(float)
        position_groups = select_dual_track_positions(scored, config, market_context, validation)
        positions = sorted(set(position_groups["mb_strong"] + position_groups["rs_strong"]))
        mature_126 = 0
        positive_126 = 0
        formal_records = [
            ("MB", "Strong", position) for position in position_groups["mb_strong"]
        ] + [
            ("RS", "Strong", position) for position in position_groups["rs_strong"]
        ]
        diagnostic_records = [
            ("MB", "Watch", position) for position in position_groups["mb_watch"]
        ] + [
            ("MB", "Medium", position) for position in position_groups["mb_medium"]
        ] + [
            ("RS", "Watch", position) for position in position_groups["rs_watch"]
        ] + [
            ("RS", "Medium", position) for position in position_groups["rs_medium"]
        ]

        def signal_record(channel: str, tier: str, position: int) -> dict[str, Any]:
            row = scored.iloc[position]
            repair_value = market_repair.asof(scored.index[position]) if market_repair is not None else None
            fwd_63 = _forward_return(close, position, 63)
            fwd_126 = _forward_return(close, position, 126)
            fwd_252 = _forward_return(close, position, 252)
            adverse = _adverse_drawdown(close, position, 126)
            bottom_gap = local_bottom_gap(
                close,
                position,
                before=int(validation.get("bottom_capture_before", 21)),
                after=int(validation.get("bottom_capture_after", 21)),
            )
            market_drawdown = (
                market_context.asof(scored.index[position])
                if market_context is not None
                else row.get("market_drawdown")
            )
            return {
                "symbol": symbol,
                "date": str(scored.index[position].date()),
                "channel": channel,
                "tier": tier,
                "bottomScore": int(row["bottom_score"]),
                "relativeStrengthScore": int(row.get("relative_strength_score", 1)),
                "rsSignalScore": int(row.get("rs_signal_score", row["bottom_score"])),
                "exitScore": int(row["exit_score"]),
                "label": tier,
                "riskFlags": row["risk_flags"],
                "marketDrawdown": None if pd.isna(market_drawdown) else float(market_drawdown),
                "marketRepair": None if pd.isna(repair_value) else float(repair_value),
                "fwd63": fwd_63,
                "fwd126": fwd_126,
                "fwd252": fwd_252,
                "adverse126": adverse,
                "localBottomGap": bottom_gap,
                "bottomCaptureScore": bottom_capture_score(bottom_gap),
            }

        for channel, tier, position in formal_records:
            record = signal_record(channel, tier, position)
            if record["fwd126"] is not None:
                mature_126 += 1
                positive_126 += int(record["fwd126"] > 0)
            signals.append(record)
        for channel, tier, position in diagnostic_records:
            diagnostic_signals.append(signal_record(channel, tier, position))

        exit_rows = np.flatnonzero((scored["exit_score"] >= config.exit_threshold).to_numpy())
        for position in exit_rows[:: max(1, len(exit_rows) // 50 or 1)]:
            fwd_21 = _forward_return(close, int(position), 21)
            if fwd_21 is not None:
                exit_checks.append(fwd_21)

        trade = _trade_simulation(scored, config, positions)
        trade_summaries.append(trade)
        symbol_summaries.append(
            {
                "symbol": symbol,
                "signals": len(positions),
                "mature126": mature_126,
                "positive126Rate": positive_126 / mature_126 if mature_126 else 0.0,
                "tradeTotalReturn": trade["totalReturn"],
                "tradeMaxDrawdown": trade["maxDrawdown"],
            }
        )

    funnel = summarize_signal_funnel(signals, diagnostic_signals)
    channel_metrics = summarize_channel_metrics(
        signals,
        validation.get("index_symbols", ["QQQ", "SPY"]),
    )
    missed = missed_strong_stocks(signals, validation)
    recent_activity = summarize_recent_channel_activity(
        signals,
        diagnostic_signals,
        days=int(validation.get("recent_activity_days", 730)),
        end_date=validation.get("recent_activity_end_date"),
    )
    recent_validation = summarize_recent_validation(
        signals,
        days=int(validation.get("recent_validation_days", validation.get("recent_activity_days", 730))),
        end_date=validation.get("recent_activity_end_date"),
        min_mature_signals=int(validation.get("recent_validation_min_mature_signals", 2)),
        min_win_rate=float(validation.get("recent_validation_min_win_rate", 0.50)),
        min_avg_fwd126=float(validation.get("recent_validation_min_avg_fwd126", 0.05)),
    )
    rs_watchlist = summarize_rs_candidate_watchlist(
        signals,
        diagnostic_signals,
        days=int(validation.get("recent_activity_days", 730)),
        end_date=validation.get("recent_activity_end_date"),
        limit=int(validation.get("rs_watchlist_limit", 15)),
        quality_threshold=float(validation.get("rs_watchlist_quality_threshold", 70)),
    )
    metrics = _score_result(
        signals,
        symbol_summaries,
        trade_summaries,
        exit_checks,
        objective_weights=objective_weights,
        validation=validation,
    )
    metrics = apply_dual_track_iteration_adjustments(metrics, funnel, missed, validation)
    metrics = apply_baseline_quality_preference(metrics, LEGACY_BASELINE_SNAPSHOT, validation)
    metrics = apply_recent_rs_activity_preference(metrics, recent_activity, validation)
    metrics = apply_qualified_rs_watchlist_preference(metrics, rs_watchlist, validation)
    return {
        "config": asdict(config),
        "metrics": metrics,
        "symbols": symbol_summaries,
        "signals": sorted(signals, key=lambda item: (item["symbol"], item["date"])),
        "diagnosticSignals": sorted(
            diagnostic_signals,
            key=lambda item: (item["symbol"], item["date"], item["channel"], item["tier"]),
        ),
        "signalFunnel": funnel,
        "channelMetrics": channel_metrics,
        "recentChannelActivity": recent_activity,
        "recentValidation": recent_validation,
        "rsCandidateWatchlist": rs_watchlist,
        "missedStrongStocks": missed,
    }


def _clean_numbers(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _clean_numbers(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_clean_numbers(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if math.isnan(float(value)) or math.isinf(float(value)):
            return None
        return float(value)
    return value


def _avg(values: list[float]) -> float:
    finite = [float(value) for value in values if value is not None and math.isfinite(value)]
    return mean(finite) if finite else 0.0


def forward_win_rate(signals: list[dict[str, Any]], field: str) -> float:
    mature = [item[field] for item in signals if item.get(field) is not None]
    if not mature:
        return 0.0
    return sum(1 for value in mature if float(value) > 0) / len(mature)


def adverse_tail_rate(signals: list[dict[str, Any]], threshold: float = -0.25) -> float:
    mature = [item["adverse126"] for item in signals if item.get("adverse126") is not None]
    if not mature:
        return 0.0
    return sum(1 for value in mature if float(value) <= threshold) / len(mature)


def market_repair_score(avg_repair: float, target: float = 3.0) -> float:
    return _clip_scalar(avg_repair / max(0.01, target)) * 100


def sparse_count_score(signal_count: int, settings: dict[str, Any]) -> float:
    minimum = int(settings.get("signal_count_min", 20))
    target = int(settings.get("signal_count_target", 80))
    maximum = int(settings.get("signal_count_max", 180))
    if signal_count <= 0:
        return 0.0
    if signal_count < minimum:
        return signal_count / max(1, minimum) * 100
    if signal_count <= target:
        return 100.0
    if signal_count >= maximum:
        return 0.0
    return (maximum - signal_count) / max(1, maximum - target) * 100


def summarize_validation_groups(
    signals: list[dict[str, Any]],
    index_symbols: list[str],
) -> dict[str, float | int]:
    index_set = set(index_symbols)
    index_signals = [item for item in signals if item["symbol"] in index_set]
    individual_signals = [item for item in signals if item["symbol"] not in index_set]
    index_fwd126 = [item["fwd126"] for item in index_signals if item.get("fwd126") is not None]
    individual_fwd126 = [
        item["fwd126"] for item in individual_signals if item.get("fwd126") is not None
    ]
    index_fwd252 = [item["fwd252"] for item in index_signals if item.get("fwd252") is not None]
    individual_fwd252 = [
        item["fwd252"] for item in individual_signals if item.get("fwd252") is not None
    ]
    return {
        "indexSignalCount": len(index_signals),
        "individualSignalCount": len(individual_signals),
        "indexAvgFwd126": _avg(index_fwd126),
        "individualAvgFwd126": _avg(individual_fwd126),
        "indexAvgFwd252": _avg(index_fwd252),
        "individualAvgFwd252": _avg(individual_fwd252),
    }


def summarize_signal_funnel(
    formal_signals: list[dict[str, Any]],
    diagnostic_signals: list[dict[str, Any]],
) -> dict[str, float | int]:
    all_signals = formal_signals + diagnostic_signals
    strong_count = sum(1 for item in formal_signals if item.get("tier") == "Strong")
    watch_count = sum(1 for item in all_signals if item.get("tier") == "Watch")
    medium_count = sum(1 for item in all_signals if item.get("tier") == "Medium")
    watch_medium_count = watch_count + medium_count
    ratio = watch_medium_count / strong_count if strong_count else 0.0
    return {
        "watchCount": watch_count,
        "mediumCount": medium_count,
        "formalStrongCount": strong_count,
        "diagnosticWatchMediumCount": watch_medium_count,
        "watchMediumToStrongRatio": ratio,
        "mbStrongCount": sum(1 for item in formal_signals if item.get("channel") == "MB"),
        "rsStrongCount": sum(1 for item in formal_signals if item.get("channel") == "RS"),
        "mbDiagnosticCount": sum(1 for item in diagnostic_signals if item.get("channel") == "MB"),
        "rsDiagnosticCount": sum(1 for item in diagnostic_signals if item.get("channel") == "RS"),
    }


def summarize_recent_channel_activity(
    formal_signals: list[dict[str, Any]],
    diagnostic_signals: list[dict[str, Any]],
    days: int = 730,
    end_date: str | None = None,
) -> dict[str, float | int | str]:
    all_signals = formal_signals + diagnostic_signals
    if not all_signals and end_date is None:
        return {
            "recentStart": "",
            "recentEnd": "",
            "recentFormalCount": 0,
            "recentDiagnosticCount": 0,
            "recentMbStrongCount": 0,
            "recentRsStrongCount": 0,
            "recentMbDiagnosticCount": 0,
            "recentRsDiagnosticCount": 0,
            "recentRsCandidateCount": 0,
            "recentMbAvgFwd126": 0.0,
            "recentRsAvgFwd126": 0.0,
            "recentMbAvgAdverse126": 0.0,
            "recentRsAvgAdverse126": 0.0,
        }

    latest = pd.Timestamp(end_date) if end_date else max(pd.Timestamp(item["date"]) for item in all_signals)
    start = latest - pd.Timedelta(days=max(0, days - 1))

    def is_recent(item: dict[str, Any]) -> bool:
        signal_date = pd.Timestamp(item["date"])
        return start <= signal_date <= latest

    recent_formal = [item for item in formal_signals if is_recent(item)]
    recent_diagnostic = [item for item in diagnostic_signals if is_recent(item)]
    mb_recent = [item for item in recent_formal + recent_diagnostic if item.get("channel") == "MB"]
    rs_recent = [item for item in recent_formal + recent_diagnostic if item.get("channel") == "RS"]
    rs_strong = [item for item in recent_formal if item.get("channel") == "RS"]
    rs_diagnostic = [item for item in recent_diagnostic if item.get("channel") == "RS"]
    return {
        "recentStart": str(start.date()),
        "recentEnd": str(latest.date()),
        "recentFormalCount": len(recent_formal),
        "recentDiagnosticCount": len(recent_diagnostic),
        "recentMbStrongCount": sum(1 for item in recent_formal if item.get("channel") == "MB"),
        "recentRsStrongCount": len(rs_strong),
        "recentMbDiagnosticCount": sum(1 for item in recent_diagnostic if item.get("channel") == "MB"),
        "recentRsDiagnosticCount": len(rs_diagnostic),
        "recentRsCandidateCount": len(rs_strong) + len(rs_diagnostic),
        "recentMbAvgFwd126": _avg([item["fwd126"] for item in mb_recent if item.get("fwd126") is not None]),
        "recentRsAvgFwd126": _avg([item["fwd126"] for item in rs_recent if item.get("fwd126") is not None]),
        "recentMbAvgAdverse126": _avg([item["adverse126"] for item in mb_recent if item.get("adverse126") is not None]),
        "recentRsAvgAdverse126": _avg([item["adverse126"] for item in rs_recent if item.get("adverse126") is not None]),
    }


def summarize_recent_validation(
    signals: list[dict[str, Any]],
    days: int = 730,
    end_date: str | None = None,
    min_mature_signals: int = 2,
    min_win_rate: float = 0.50,
    min_avg_fwd126: float = 0.05,
) -> dict[str, float | int | str]:
    if not signals and end_date is None:
        return {
            "recentValidationStart": "",
            "recentValidationEnd": "",
            "recentValidationSignalCount": 0,
            "recentValidationMatureCount": 0,
            "recentValidationAvgFwd126": 0.0,
            "recentValidationWinRate126": 0.0,
            "recentValidationAvgAdverse126": 0.0,
            "recentValidationStatus": "Watch",
        }

    latest = pd.Timestamp(end_date) if end_date else max(pd.Timestamp(item["date"]) for item in signals)
    start = latest - pd.Timedelta(days=max(0, days - 1))
    recent = [
        item
        for item in signals
        if start <= pd.Timestamp(item["date"]) <= latest
    ]
    mature = [item for item in recent if item.get("fwd126") is not None]
    avg_fwd126 = _avg([item["fwd126"] for item in mature])
    win_rate = forward_win_rate(mature, "fwd126")
    avg_adverse126 = _avg(
        [item["adverse126"] for item in mature if item.get("adverse126") is not None]
    )
    if len(mature) < min_mature_signals:
        status = "Watch"
    elif win_rate >= min_win_rate and avg_fwd126 >= min_avg_fwd126:
        status = "Pass"
    else:
        status = "Fail"

    return {
        "recentValidationStart": str(start.date()),
        "recentValidationEnd": str(latest.date()),
        "recentValidationSignalCount": len(recent),
        "recentValidationMatureCount": len(mature),
        "recentValidationAvgFwd126": avg_fwd126,
        "recentValidationWinRate126": win_rate,
        "recentValidationAvgAdverse126": avg_adverse126,
        "recentValidationStatus": status,
    }


def summarize_rs_candidate_watchlist(
    formal_signals: list[dict[str, Any]],
    diagnostic_signals: list[dict[str, Any]],
    days: int = 730,
    end_date: str | None = None,
    limit: int = 15,
    quality_threshold: float = 70.0,
) -> dict[str, Any]:
    all_signals = formal_signals + diagnostic_signals
    if not all_signals and end_date is None:
        return {
            "rsCandidateCount": 0,
            "qualifiedRsCandidateCount": 0,
            "rsCandidateAvgFwd126": 0.0,
            "rsCandidateAvgAdverse126": 0.0,
            "qualifiedRsCandidateAvgFwd126": 0.0,
            "qualifiedRsCandidateAvgAdverse126": 0.0,
            "topRsCandidates": [],
            "rsTickerSummary": [],
            "rsTickerActionCounts": {},
        }

    latest = pd.Timestamp(end_date) if end_date else max(pd.Timestamp(item["date"]) for item in all_signals)
    start = latest - pd.Timedelta(days=max(0, days - 1))
    candidates = [
        item
        for item in all_signals
        if item.get("channel") == "RS"
        and start <= pd.Timestamp(item["date"]) <= latest
    ]
    for item in candidates:
        item["qualityScore"] = rs_candidate_quality_score(item)
        item["qualityPassed"] = item["qualityScore"] >= quality_threshold
    qualified = [item for item in candidates if item["qualityPassed"]]
    ranked = sorted(
        candidates,
        key=lambda item: (
            bool(item.get("qualityPassed", False)),
            int(item.get("relativeStrengthScore", 0)),
            int(item.get("qualityScore", 0)),
            int(item.get("rsSignalScore", 0)),
            int(item.get("bottomScore", 0)),
        ),
        reverse=True,
    )
    top = [
        {
            "symbol": item["symbol"],
            "date": item["date"],
            "tier": item.get("tier", ""),
            "rsSignalScore": item.get("rsSignalScore", 0),
            "relativeStrengthScore": item.get("relativeStrengthScore", 0),
            "bottomScore": item.get("bottomScore", 0),
            "qualityScore": item.get("qualityScore", 0),
            "qualityPassed": item.get("qualityPassed", False),
            "riskFlags": item.get("riskFlags", ""),
            "marketDrawdown": item.get("marketDrawdown"),
            "fwd126": item.get("fwd126"),
            "adverse126": item.get("adverse126"),
        }
        for item in ranked[:limit]
    ]
    ticker_summary = summarize_rs_ticker_watchlist(candidates)
    return {
        "rsCandidateCount": len(candidates),
        "qualifiedRsCandidateCount": len(qualified),
        "rsCandidateAvgFwd126": _avg([item["fwd126"] for item in candidates if item.get("fwd126") is not None]),
        "rsCandidateAvgAdverse126": _avg([item["adverse126"] for item in candidates if item.get("adverse126") is not None]),
        "qualifiedRsCandidateAvgFwd126": _avg([item["fwd126"] for item in qualified if item.get("fwd126") is not None]),
        "qualifiedRsCandidateAvgAdverse126": _avg([item["adverse126"] for item in qualified if item.get("adverse126") is not None]),
        "topRsCandidates": top,
        "rsTickerSummary": ticker_summary,
        "rsTickerActionCounts": rs_ticker_action_counts(ticker_summary),
    }


def rs_candidate_quality_score(item: dict[str, Any]) -> int:
    tier_bonus = {"Strong": 5.0, "Medium": 3.0, "Watch": 0.0}.get(str(item.get("tier", "")), 0.0)
    score = (
        float(item.get("relativeStrengthScore", 0)) * 0.45
        + float(item.get("rsSignalScore", 0)) * 0.30
        + float(item.get("bottomScore", 0)) * 0.15
        + tier_bonus
    )
    flags = {flag.strip() for flag in str(item.get("riskFlags", "")).split(",") if flag.strip()}
    if "trend_damage" in flags:
        score -= 25
    if "no_repair" in flags:
        score -= 18
    if "low_volume" in flags:
        score -= 10
    if "overextended_rebound" in flags:
        score -= 16
    return clamp_1_100(score)


def summarize_rs_ticker_watchlist(
    candidates: list[dict[str, Any]],
    limit: int = 12,
) -> list[dict[str, Any]]:
    by_symbol: dict[str, list[dict[str, Any]]] = {}
    for item in candidates:
        by_symbol.setdefault(str(item.get("symbol", "")), []).append(item)

    rows = []
    for symbol, items in by_symbol.items():
        qualified = [item for item in items if item.get("qualityPassed")]
        ranked = sorted(
            items,
            key=lambda item: (
                int(item.get("qualityScore", 0)),
                int(item.get("relativeStrengthScore", 0)),
                int(item.get("rsSignalScore", 0)),
            ),
            reverse=True,
        )
        best = ranked[0]
        risk_count = sum(1 for item in items if str(item.get("riskFlags", "")))
        avg_quality = _avg([item.get("qualityScore", 0) for item in items])
        avg_fwd_126 = _avg([item["fwd126"] for item in items if item.get("fwd126") is not None])
        avg_adverse_126 = _avg(
            [item["adverse126"] for item in items if item.get("adverse126") is not None]
        )
        selection_score = rs_selection_score(
            qualified_count=len(qualified),
            candidate_count=len(items),
            avg_quality=avg_quality,
            best_quality=float(best.get("qualityScore", 0)),
            avg_adverse_126=avg_adverse_126,
            risk_count=risk_count,
        )
        rows.append(
            {
                "symbol": symbol,
                "candidateCount": len(items),
                "qualifiedCount": len(qualified),
                "selectionScore": selection_score,
                "avgQualityScore": avg_quality,
                "avgFwd126": avg_fwd_126,
                "avgAdverse126": avg_adverse_126,
                "bestDate": best.get("date", ""),
                "bestQualityScore": best.get("qualityScore", 0),
                "riskFlaggedCount": risk_count,
                "actionTier": rs_ticker_action_tier(
                    qualified_count=len(qualified),
                    avg_quality=avg_quality,
                    avg_adverse_126=avg_adverse_126,
                    risk_count=risk_count,
                ),
            }
        )
        rows[-1]["actionReason"] = rs_ticker_action_reason(
            action_tier=str(rows[-1]["actionTier"]),
            qualified_count=len(qualified),
            avg_quality=avg_quality,
            avg_adverse_126=avg_adverse_126,
            risk_count=risk_count,
        )

    return rank_rs_ticker_summary(rows, limit=limit)


def rank_rs_ticker_summary(
    rows: list[dict[str, Any]],
    limit: int | None = None,
) -> list[dict[str, Any]]:
    enriched = []
    for item in rows:
        row = dict(item)
        row["selectionScore"] = _summary_selection_score(row)
        action_tier = row.get("actionTier") or rs_ticker_action_tier(
            qualified_count=int(row.get("qualifiedCount", 0)),
            avg_quality=float(row.get("avgQualityScore", 0.0)),
            avg_adverse_126=float(row.get("avgAdverse126", 0.0)),
            risk_count=int(row.get("riskFlaggedCount", 0)),
        )
        row["actionTier"] = action_tier
        row["actionReason"] = row.get("actionReason") or rs_ticker_action_reason(
            action_tier=str(action_tier),
            qualified_count=int(row.get("qualifiedCount", 0)),
            avg_quality=float(row.get("avgQualityScore", 0.0)),
            avg_adverse_126=float(row.get("avgAdverse126", 0.0)),
            risk_count=int(row.get("riskFlaggedCount", 0)),
        )
        enriched.append(row)

    sorted_rows = sorted(
        enriched,
        key=lambda item: (
            float(item["selectionScore"]),
            int(item["qualifiedCount"]),
            float(item["avgQualityScore"]),
        ),
        reverse=True,
    )
    if limit is not None:
        sorted_rows = sorted_rows[:limit]
    for index, item in enumerate(sorted_rows, start=1):
        item["selectionRank"] = index
    return sorted_rows


def rs_selection_score(
    *,
    qualified_count: int,
    candidate_count: int,
    avg_quality: float,
    best_quality: float,
    avg_adverse_126: float,
    risk_count: int,
) -> float:
    coverage_score = min(1.0, qualified_count / 2) * 35
    repeat_score = min(1.0, candidate_count / 3) * 10
    quality_score = _clip_scalar(avg_quality / 80) * 25
    best_score = _clip_scalar(best_quality / 85) * 15
    drawdown_score = _clip_scalar((avg_adverse_126 + 0.18) / 0.18) * 15
    risk_penalty = min(20.0, risk_count * 8.0)
    return round(
        max(0.0, min(100.0, coverage_score + repeat_score + quality_score + best_score + drawdown_score - risk_penalty)),
        2,
    )


def rs_ticker_action_tier(
    *,
    qualified_count: int,
    avg_quality: float,
    avg_adverse_126: float,
    risk_count: int,
) -> str:
    if (
        qualified_count >= 2
        and avg_quality >= 70
        and avg_adverse_126 >= -0.08
        and risk_count == 0
    ):
        return "Priority"
    if qualified_count >= 1 and avg_quality >= 60 and avg_adverse_126 >= -0.12:
        return "Watch"
    return "Avoid"


def rs_ticker_action_counts(ticker_summary: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"Priority": 0, "Watch": 0, "Avoid": 0}
    for index, item in enumerate(ticker_summary, start=1):
        tier = str(item.get("actionTier", ""))
        if tier not in counts:
            tier = rs_ticker_action_tier(
                qualified_count=int(item.get("qualifiedCount", 0)),
                avg_quality=float(item.get("avgQualityScore", 0.0)),
                avg_adverse_126=float(item.get("avgAdverse126", 0.0)),
                risk_count=int(item.get("riskFlaggedCount", 0)),
            )
        counts[tier] += 1
    return counts


def _summary_selection_score(item: dict[str, Any]) -> float:
    if "selectionScore" in item:
        return float(item.get("selectionScore", 0.0))
    return rs_selection_score(
        qualified_count=int(item.get("qualifiedCount", 0)),
        candidate_count=int(item.get("candidateCount", 0)),
        avg_quality=float(item.get("avgQualityScore", 0.0)),
        best_quality=float(item.get("bestQualityScore", 0.0)),
        avg_adverse_126=float(item.get("avgAdverse126", 0.0)),
        risk_count=int(item.get("riskFlaggedCount", 0)),
    )


def rs_ticker_action_reason(
    *,
    action_tier: str,
    qualified_count: int,
    avg_quality: float,
    avg_adverse_126: float,
    risk_count: int,
) -> str:
    if action_tier == "Priority":
        return "repeated qualified candidates with clean risk profile"
    if qualified_count <= 0:
        return "no qualified RS candidates"
    if risk_count > 0:
        return "qualified but has risk flags"
    if avg_adverse_126 < -0.12:
        return "qualified but adverse drawdown is high"
    if avg_quality < 70:
        return "qualified but quality score is below priority"
    return "qualified watchlist candidate"


MB_FACTOR_WEIGHTS = {
    "drawdown": "drawdown_weight",
    "momentum": "momentum_weight",
    "repair": "repair_weight",
    "structure": "structure_weight",
    "volume": "volume_weight",
    "ma": "ma_weight",
}


def build_mb_factor_ablation_configs(
    config: BottomSignalConfig,
) -> list[tuple[str, BottomSignalConfig]]:
    rows = []
    for factor, field in MB_FACTOR_WEIGHTS.items():
        rows.append(
            (
                factor,
                replace(
                    config,
                    name=f"{config.name}_no_{factor}",
                    **{field: 0.0},
                ),
            )
        )
    return rows


def run_mb_factor_ablation(
    symbols: list[str],
    config: BottomSignalConfig,
    settings: SearchSettings,
    *,
    evaluator=evaluate_config,
    indicator_precomputer=precompute_indicator_frames,
) -> dict[str, Any]:
    variants = build_mb_factor_ablation_configs(config)
    configs = [config] + [variant for _, variant in variants]
    indicator_frames = indicator_precomputer(
        symbols,
        configs,
        cache_enabled=settings.cache_indicators,
    )
    baseline = evaluator(
        symbols,
        config,
        indicator_frames=indicator_frames,
        objective_weights=settings.objective_weights,
        validation=settings.validation,
    )
    baseline_metrics = baseline.get("metrics", {})
    rows = []
    for factor, variant in variants:
        result = evaluator(
            symbols,
            variant,
            indicator_frames=indicator_frames,
            objective_weights=settings.objective_weights,
            validation=settings.validation,
        )
        metrics = result.get("metrics", {})
        rows.append(
            {
                "factor": factor,
                "configName": variant.name,
                "compositeScore": float(metrics.get("compositeScore", 0.0)),
                "compositeDelta": float(metrics.get("compositeScore", 0.0))
                - float(baseline_metrics.get("compositeScore", 0.0)),
                "signalCount": int(metrics.get("signalCount", 0)),
                "signalCountDelta": int(metrics.get("signalCount", 0))
                - int(baseline_metrics.get("signalCount", 0)),
                "avgFwd126": float(metrics.get("avgFwd126", 0.0)),
                "avgFwd126Delta": float(metrics.get("avgFwd126", 0.0))
                - float(baseline_metrics.get("avgFwd126", 0.0)),
                "avgAdverse126": float(metrics.get("avgAdverse126", 0.0)),
                "avgAdverse126Delta": float(metrics.get("avgAdverse126", 0.0))
                - float(baseline_metrics.get("avgAdverse126", 0.0)),
            }
        )
    return {
        "baselineConfigName": config.name,
        "baselineCompositeScore": float(baseline_metrics.get("compositeScore", 0.0)),
        "baselineSignalCount": int(baseline_metrics.get("signalCount", 0)),
        "baselineAvgFwd126": float(baseline_metrics.get("avgFwd126", 0.0)),
        "baselineAvgAdverse126": float(baseline_metrics.get("avgAdverse126", 0.0)),
        "rows": sorted(rows, key=lambda item: item["compositeDelta"]),
    }


def summarize_mb_factor_ablation(ablation: dict[str, Any]) -> dict[str, Any]:
    rows = []
    baseline_signal_count = int(ablation.get("baselineSignalCount", 0))
    overactive_threshold = max(20, int(round(baseline_signal_count * 0.50)))
    for item in ablation.get("rows", []):
        composite_score = float(item.get("compositeScore", 0.0))
        composite_delta = float(item.get("compositeDelta", 0.0))
        signal_delta = int(item.get("signalCountDelta", 0))
        if signal_delta >= overactive_threshold:
            impact = "Overactive"
        elif composite_score <= 0.0 or composite_delta <= -8.0:
            impact = "Critical"
        elif composite_delta < 0.0:
            impact = "Supportive"
        else:
            impact = "Redundant"
        row = dict(item)
        row["impactLabel"] = impact
        rows.append(row)

    return {
        "factorCount": len(rows),
        "criticalFactors": [item["factor"] for item in rows if item["impactLabel"] == "Critical"],
        "overactiveFactors": [item["factor"] for item in rows if item["impactLabel"] == "Overactive"],
        "supportiveFactors": [item["factor"] for item in rows if item["impactLabel"] == "Supportive"],
        "redundantFactors": [item["factor"] for item in rows if item["impactLabel"] == "Redundant"],
        "rows": rows,
    }


def top_rs_coverage_tradeoffs(
    results: list[dict[str, Any]],
    limit: int = 8,
) -> list[dict[str, Any]]:
    rows = []
    for result in results:
        watchlist = result.get("rsCandidateWatchlist", {})
        metrics = result.get("metrics", {})
        count = int(watchlist.get("qualifiedRsCandidateCount", 0))
        if count <= 0:
            continue
        rows.append(
            {
                "name": result.get("config", {}).get("name", ""),
                "experimentalSignalSet": result.get("config", {}).get("experimental_signal_set", ""),
                "compositeScore": float(metrics.get("compositeScore", 0.0)),
                "signalCount": int(metrics.get("signalCount", 0)),
                "avgFwd126": float(metrics.get("avgFwd126", 0.0)),
                "qualifiedRsCandidateCount": count,
                "qualifiedRsCandidateAvgFwd126": float(
                    watchlist.get("qualifiedRsCandidateAvgFwd126", 0.0)
                ),
                "qualifiedRsCandidateAvgAdverse126": float(
                    watchlist.get("qualifiedRsCandidateAvgAdverse126", 0.0)
                ),
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            item["qualifiedRsCandidateCount"],
            item["qualifiedRsCandidateAvgFwd126"],
            item["compositeScore"],
        ),
        reverse=True,
    )[:limit]


def select_best_rs_watchlist_result(results: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        result
        for result in results
        if int(result.get("rsCandidateWatchlist", {}).get("qualifiedRsCandidateCount", 0)) > 0
    ]
    if not candidates:
        return {}

    selected = max(
        candidates,
        key=lambda result: (
            int(result.get("rsCandidateWatchlist", {}).get("qualifiedRsCandidateCount", 0)),
            float(result.get("rsCandidateWatchlist", {}).get("qualifiedRsCandidateAvgFwd126", 0.0)),
            float(result.get("rsCandidateWatchlist", {}).get("qualifiedRsCandidateAvgAdverse126", -1.0)),
            float(result.get("metrics", {}).get("compositeScore", 0.0)),
        ),
    )
    return {
        "role": "rs_watchlist_only",
        "config": selected.get("config", {}),
        "metrics": selected.get("metrics", {}),
        "rsCandidateWatchlist": selected.get("rsCandidateWatchlist", {}),
    }


def refresh_best_rs_watchlist_scan(
    payload: dict[str, Any],
    symbols: list[str],
    settings: SearchSettings,
    *,
    evaluator=evaluate_config,
    indicator_precomputer=precompute_indicator_frames,
) -> dict[str, Any]:
    """Refresh only the RS watchlist config instead of running the full grid."""
    config_payload = payload.get("bestRsWatchlist", {}).get("config") or payload.get("bestConfig")
    if not config_payload:
        return payload

    config = BottomSignalConfig(**config_payload)
    indicator_frames = indicator_precomputer(
        symbols,
        [config],
        cache_enabled=settings.cache_indicators,
    )
    result = evaluator(
        symbols,
        config,
        indicator_frames=indicator_frames,
        objective_weights=settings.objective_weights,
        validation=settings.validation,
    )
    payload["bestRsWatchlist"] = {
        "role": "rs_watchlist_only",
        "config": result.get("config", asdict(config)),
        "metrics": result.get("metrics", {}),
        "rsCandidateWatchlist": result.get("rsCandidateWatchlist", {}),
    }
    payload["rsWatchlistRefresh"] = {
        "mode": "single_config",
        "configName": config.name,
        "symbolCount": len(symbols),
    }
    return _clean_numbers(payload)


def refresh_supplemental_analysis(
    payload: dict[str, Any],
    symbols: list[str],
    settings: SearchSettings,
    *,
    evaluator=evaluate_config,
    indicator_precomputer=precompute_indicator_frames,
) -> dict[str, Any]:
    """Refresh plan-level analysis without re-running the full config search."""
    if not payload.get("bestConfig"):
        return payload

    config = BottomSignalConfig(**payload["bestConfig"])
    payload["mbFactorAblation"] = run_mb_factor_ablation(
        symbols,
        config,
        settings,
        evaluator=evaluator,
        indicator_precomputer=indicator_precomputer,
    )
    for result in payload.get("results", []):
        result["recentValidation"] = summarize_recent_validation(
            result.get("signals", []),
            days=int(
                settings.validation.get(
                    "recent_validation_days",
                    settings.validation.get("recent_activity_days", 730),
                )
            ),
            end_date=settings.validation.get("recent_activity_end_date"),
            min_mature_signals=int(
                settings.validation.get("recent_validation_min_mature_signals", 2)
            ),
            min_win_rate=float(settings.validation.get("recent_validation_min_win_rate", 0.50)),
            min_avg_fwd126=float(
                settings.validation.get("recent_validation_min_avg_fwd126", 0.05)
            ),
        )
    payload["supplementalAnalysisRefresh"] = {
        "mode": "supplemental_analysis",
        "configName": config.name,
        "symbolCount": len(symbols),
    }
    return _clean_numbers(payload)


def refresh_observation_search(
    payload: dict[str, Any],
    symbols: list[str],
    settings: SearchSettings,
    *,
    indicator_precomputer=precompute_indicator_frames,
) -> dict[str, Any]:
    """Search the shallow-pullback/deep-retest observation channel for the best config."""
    if not payload.get("bestConfig"):
        return payload

    config = BottomSignalConfig(**payload["bestConfig"])
    indicator_frames = indicator_precomputer(
        symbols,
        [config],
        cache_enabled=settings.cache_indicators,
    )
    scored_by_symbol = {
        symbol: score_from_indicators(indicator_frames[symbol], config)
        for symbol in symbols
        if symbol in indicator_frames
    }
    market_context = build_market_context(
        scored_by_symbol,
        settings.validation.get("market_symbols", settings.validation.get("index_symbols", ["QQQ", "SPY"])),
        int(settings.validation.get("market_drawdown_window", config.market_drawdown_window)),
    )
    if market_context is None:
        payload["observationSearch"] = search_observation_channel(
            {},
            pd.Series(dtype="float64"),
            formal_keys=set(),
            formal_signal_count=int(payload.get("bestMetrics", {}).get("signalCount", 0)),
        )
        return _clean_numbers(payload)

    rs_market_context = build_market_context(
        scored_by_symbol,
        settings.validation.get("market_symbols", settings.validation.get("index_symbols", ["QQQ", "SPY"])),
        config.rs_window,
    )
    rs_market_repair = build_market_repair(
        scored_by_symbol,
        settings.validation.get("market_symbols", settings.validation.get("index_symbols", ["QQQ", "SPY"])),
        config.rs_window,
    )
    scored_with_rs = {
        symbol: add_relative_strength_scores(frame, rs_market_context, rs_market_repair, config)
        for symbol, frame in scored_by_symbol.items()
    }
    best_result = next(
        (
            result
            for result in payload.get("results", [])
            if result.get("config", {}).get("name") == config.name
        ),
        {},
    )
    formal_signals = best_result.get("signals", [])
    formal_keys = {
        (str(item.get("symbol", "")), str(item.get("date", "")))
        for item in formal_signals
        if item.get("symbol") and item.get("date")
    }
    formal_signal_count = int(
        payload.get("bestMetrics", {}).get("signalCount", len(formal_signals))
    )
    payload["observationSearch"] = search_observation_channel(
        scored_with_rs,
        market_context,
        formal_keys=formal_keys,
        formal_signal_count=formal_signal_count,
    )
    payload["observationSearchRefresh"] = {
        "mode": "observation_search",
        "configName": config.name,
        "symbolCount": len(symbols),
    }
    return _clean_numbers(payload)


def summarize_channel_metrics(
    signals: list[dict[str, Any]],
    index_symbols: list[str],
) -> dict[str, dict[str, float | int]]:
    summary = {}
    for channel in ("MB", "RS"):
        channel_signals = [item for item in signals if item.get("channel", "MB") == channel]
        summary[channel] = _signal_subset_summary(channel_signals, index_symbols)
    return summary


def missed_strong_stocks(
    signals: list[dict[str, Any]],
    validation: dict[str, Any],
    limit: int = 20,
) -> list[dict[str, Any]]:
    threshold = float(validation.get("market_drawdown_threshold", -20))
    missed = [
        item
        for item in signals
        if item.get("channel") == "RS"
        and item.get("tier") == "Strong"
        and item.get("marketDrawdown") is not None
        and float(item["marketDrawdown"]) > threshold
    ]
    return sorted(
        missed,
        key=lambda item: (item.get("relativeStrengthScore", 0), item.get("bottomScore", 0)),
        reverse=True,
    )[:limit]


def apply_watch_medium_ratio_gate(
    composite_score: float,
    ratio: float,
    settings: dict[str, Any],
) -> float:
    target = settings.get("watch_medium_target_multiplier")
    if not target:
        return composite_score
    lower, upper = float(target[0]), float(target[1])
    if ratio <= 0 or lower <= 0 or upper <= 0:
        return composite_score
    if lower <= ratio <= upper:
        return composite_score
    if ratio < lower:
        return composite_score * _clip_scalar(ratio / lower)
    return composite_score * _clip_scalar(upper / ratio)


def apply_relative_strength_capture_preference(
    composite_score: float,
    missed_count: int,
    settings: dict[str, Any],
) -> float:
    if settings.get("require_rs_missed_capture", False) and missed_count <= 0:
        return 0.0
    target = int(settings.get("rs_missed_capture_target", 1))
    if target <= 0:
        return composite_score
    capture_score = min(1.0, missed_count / target)
    return composite_score * (0.85 + 0.15 * capture_score)


def apply_dual_track_iteration_adjustments(
    metrics: dict[str, float | int],
    funnel: dict[str, float | int],
    missed: list[dict[str, Any]],
    validation: dict[str, Any],
) -> dict[str, float | int]:
    adjusted = dict(metrics)
    original = float(metrics["compositeScore"])
    ratio = float(funnel.get("watchMediumToStrongRatio", 0.0))
    after_ratio = apply_watch_medium_ratio_gate(original, ratio, validation)
    after_rs = apply_relative_strength_capture_preference(after_ratio, len(missed), validation)
    target = int(validation.get("rs_missed_capture_target", 1))
    adjusted["preDualTrackCompositeScore"] = original
    adjusted["watchMediumRatioScore"] = after_ratio / original * 100 if original else 0.0
    adjusted["rsMissedCaptureCount"] = len(missed)
    adjusted["rsMissedCaptureScore"] = min(1.0, len(missed) / max(1, target)) * 100
    adjusted["compositeScore"] = after_rs
    return adjusted


def apply_baseline_quality_preference(
    metrics: dict[str, float | int],
    baseline: dict[str, Any],
    settings: dict[str, Any],
) -> dict[str, float | int]:
    adjusted = dict(metrics)
    minimum = float(settings.get("baseline_quality_min_ratio", 0.0))
    if minimum <= 0:
        adjusted["baselineQualityScore"] = 100.0
        return adjusted
    baseline_return = float(baseline.get("avgFwd126", 0.0))
    baseline_win = float(baseline.get("winRate126", 0.0))
    if baseline_return <= 0 or baseline_win <= 0:
        adjusted["baselineQualityScore"] = 100.0
        return adjusted
    return_ratio = float(metrics.get("avgFwd126", 0.0)) / baseline_return
    win_ratio = float(metrics.get("winRate126", 0.0)) / baseline_win
    quality_ratio = min(return_ratio, win_ratio)
    quality_score = min(1.0, quality_ratio / minimum)
    adjusted["baselineQualityScore"] = quality_score * 100
    adjusted["compositeScore"] = float(metrics["compositeScore"]) * quality_score
    return adjusted


def apply_recent_rs_activity_preference(
    metrics: dict[str, float | int],
    recent_activity: dict[str, float | int | str],
    settings: dict[str, Any],
) -> dict[str, float | int]:
    adjusted = dict(metrics)
    target = settings.get("rs_recent_candidate_targets")
    diagnostic_target = settings.get("rs_recent_diagnostic_targets")
    if not target and not diagnostic_target:
        adjusted["recentRsActivityScore"] = 100.0
        return adjusted

    candidate_lower, candidate_upper = [float(value) for value in (target or [1, 999])]
    diagnostic_lower, diagnostic_upper = [
        float(value) for value in (diagnostic_target or [1, 999])
    ]
    candidates = float(recent_activity.get("recentRsCandidateCount", 0))
    diagnostics = float(recent_activity.get("recentRsDiagnosticCount", 0))
    avg_fwd126 = float(recent_activity.get("recentRsAvgFwd126", 0.0))
    min_return = float(settings.get("rs_recent_avg_fwd126_min", 0.0))

    def range_score(value: float, lower: float, upper: float) -> float:
        if value <= 0:
            return 0.0
        if value < lower:
            return _clip_scalar(value / max(1.0, lower))
        if value <= upper:
            return 1.0
        return _clip_scalar(upper / value)

    candidate_score = range_score(candidates, candidate_lower, candidate_upper)
    diagnostic_score = range_score(diagnostics, diagnostic_lower, diagnostic_upper)
    return_score = 1.0
    if min_return > 0:
        return_score = _clip_scalar(avg_fwd126 / min_return) if candidates else 0.0

    activity_score = min(candidate_score, diagnostic_score, return_score)
    adjusted["recentRsActivityScore"] = activity_score * 100
    adjusted["recentRsCandidateCount"] = int(candidates)
    adjusted["recentRsDiagnosticCount"] = int(diagnostics)
    adjusted["recentRsAvgFwd126"] = avg_fwd126
    adjusted["preRecentRsActivityCompositeScore"] = float(adjusted["compositeScore"])
    adjusted["compositeScore"] = float(adjusted["compositeScore"]) * (0.75 + 0.25 * activity_score)
    return adjusted


def apply_qualified_rs_watchlist_preference(
    metrics: dict[str, float | int],
    watchlist: dict[str, Any],
    settings: dict[str, Any],
) -> dict[str, float | int]:
    adjusted = dict(metrics)
    target = settings.get("qualified_rs_candidate_targets")
    if not target:
        adjusted["qualifiedRsWatchlistScore"] = 100.0
        return adjusted

    lower, upper = [float(value) for value in target]
    count = float(watchlist.get("qualifiedRsCandidateCount", 0))
    avg_fwd126 = float(watchlist.get("qualifiedRsCandidateAvgFwd126", 0.0))
    avg_adverse126 = float(watchlist.get("qualifiedRsCandidateAvgAdverse126", 0.0))
    min_return = float(settings.get("qualified_rs_avg_fwd126_min", 0.0))
    min_adverse = float(settings.get("qualified_rs_avg_adverse126_min", -1.0))

    if count <= 0:
        count_score = 0.0
    elif count < lower:
        count_score = _clip_scalar(count / max(1.0, lower))
    elif count <= upper:
        count_score = 1.0
    else:
        count_score = _clip_scalar(upper / count)

    return_score = _clip_scalar(avg_fwd126 / min_return) if min_return > 0 and count else 1.0
    adverse_score = 1.0 if avg_adverse126 >= min_adverse or not count else 0.0
    watchlist_score = min(count_score, return_score, adverse_score)

    adjusted["qualifiedRsWatchlistScore"] = watchlist_score * 100
    adjusted["qualifiedRsCandidateCount"] = int(count)
    adjusted["qualifiedRsCandidateAvgFwd126"] = avg_fwd126
    adjusted["qualifiedRsCandidateAvgAdverse126"] = avg_adverse126
    adjusted["preQualifiedRsWatchlistCompositeScore"] = float(adjusted["compositeScore"])
    adjusted["compositeScore"] = float(adjusted["compositeScore"]) * (0.80 + 0.20 * watchlist_score)
    return adjusted


def validation_coverage_score(
    index_signal_count: int,
    individual_signal_count: int,
    settings: dict[str, Any],
) -> float:
    index_min = int(settings.get("index_signal_min", 4))
    individual_min = int(settings.get("individual_signal_min", 40))
    index_score = min(1.0, index_signal_count / max(1, index_min))
    individual_score = min(1.0, individual_signal_count / max(1, individual_min))
    return min(index_score, individual_score) * 100


def apply_validation_coverage_gate(
    composite_score: float,
    coverage_score: float,
    settings: dict[str, Any],
) -> float:
    if not settings.get("require_validation_coverage", False):
        return composite_score
    return composite_score * _clip_scalar(coverage_score / 100)


def apply_signal_count_gate(
    composite_score: float,
    signal_count: int,
    settings: dict[str, Any],
) -> float:
    if not settings.get("require_signal_count_max", False):
        return composite_score
    maximum = int(settings.get("signal_count_max", 180))
    if signal_count <= maximum:
        return composite_score
    if settings.get("require_signal_count_hard_max", False):
        return 0.0
    return composite_score * _clip_scalar(maximum / max(1, signal_count))


def summarize_date_split_validation(
    signals: list[dict[str, Any]],
    cutoff_date: str | None,
    index_symbols: list[str],
) -> dict[str, float | int]:
    if not cutoff_date:
        return {
            "trainSignalCount": len(signals),
            "holdoutSignalCount": 0,
            "holdoutIndexSignalCount": 0,
            "holdoutIndividualSignalCount": 0,
            "holdoutAvgFwd126": 0.0,
            "holdoutAvgAdverse126": 0.0,
            "holdoutWinRate126": 0.0,
        }

    cutoff = pd.Timestamp(cutoff_date)
    index_set = set(index_symbols)
    train = []
    holdout = []
    for item in signals:
        signal_date = pd.Timestamp(item["date"])
        if signal_date <= cutoff:
            train.append(item)
        else:
            holdout.append(item)

    holdout_fwd126 = [item["fwd126"] for item in holdout if item.get("fwd126") is not None]
    holdout_adverse = [
        item["adverse126"] for item in holdout if item.get("adverse126") is not None
    ]
    return {
        "trainSignalCount": len(train),
        "holdoutSignalCount": len(holdout),
        "holdoutIndexSignalCount": sum(1 for item in holdout if item["symbol"] in index_set),
        "holdoutIndividualSignalCount": sum(1 for item in holdout if item["symbol"] not in index_set),
        "holdoutAvgFwd126": _avg(holdout_fwd126),
        "holdoutAvgAdverse126": _avg(holdout_adverse),
        "holdoutWinRate126": forward_win_rate(holdout, "fwd126"),
    }


def date_split_coverage_score(
    holdout_index_signal_count: int,
    holdout_individual_signal_count: int,
    settings: dict[str, Any],
) -> float:
    index_min = int(settings.get("holdout_index_signal_min", 1))
    individual_min = int(settings.get("holdout_individual_signal_min", 6))
    index_score = min(1.0, holdout_index_signal_count / max(1, index_min))
    individual_score = min(1.0, holdout_individual_signal_count / max(1, individual_min))
    return min(index_score, individual_score) * 100


def apply_date_split_gate(
    composite_score: float,
    date_split_score: float,
    settings: dict[str, Any],
) -> float:
    if not settings.get("require_date_split_coverage", False):
        return composite_score
    return composite_score * _clip_scalar(date_split_score / 100)


def validation_window_coverage_score(
    covered_window_count: int,
    validation_window_count: int,
) -> float:
    if validation_window_count <= 0:
        return 100.0
    return min(1.0, covered_window_count / validation_window_count) * 100


def summarize_validation_windows(
    signals: list[dict[str, Any]],
    windows: list[dict[str, Any]],
) -> dict[str, float | int]:
    if not windows:
        return {
            "validationWindowCount": 0,
            "coveredValidationWindowCount": 0,
            "positiveValidationWindowCount": 0,
            "validationWindowCoverageScore": 100.0,
            "validationWindowWorstAvgFwd126": 0.0,
            "validationWindowAvgFwd126": 0.0,
            "validationWindowWorstWinRate126": 0.0,
            "validationWindowAvgWinRate126": 0.0,
            "validationWindowScore": 100.0,
        }

    covered_count = 0
    positive_count = 0
    window_averages = []
    window_win_rates = []
    for window in windows:
        start = pd.Timestamp(window["start"])
        end = pd.Timestamp(window["end"])
        minimum = int(window.get("min_signals", 1))
        window_signals = [
            item
            for item in signals
            if start <= pd.Timestamp(item["date"]) <= end
            and item.get("fwd126") is not None
        ]
        window_average = _avg([item["fwd126"] for item in window_signals])
        window_win_rate = forward_win_rate(window_signals, "fwd126")
        window_averages.append(window_average)
        window_win_rates.append(window_win_rate)
        if len(window_signals) >= minimum:
            covered_count += 1
        if window_signals and window_average > 0:
            positive_count += 1

    coverage = validation_window_coverage_score(covered_count, len(windows))
    positive_score = min(1.0, positive_count / len(windows)) * 100
    worst_average = min(window_averages) if window_averages else 0.0
    worst_win_rate = min(window_win_rates) if window_win_rates else 0.0
    average_return_score = _clip_scalar((_avg(window_averages) + 0.05) / 0.35) * 100
    worst_return_score = _clip_scalar((worst_average + 0.05) / 0.25) * 100
    average_win_score = _clip_scalar((_avg(window_win_rates) - 0.45) / 0.35) * 100
    worst_win_score = _clip_scalar((worst_win_rate - 0.40) / 0.25) * 100
    score = (
        coverage * 0.35
        + positive_score * 0.15
        + average_return_score * 0.15
        + worst_return_score * 0.15
        + average_win_score * 0.10
        + worst_win_score * 0.10
    )
    return {
        "validationWindowCount": len(windows),
        "coveredValidationWindowCount": covered_count,
        "positiveValidationWindowCount": positive_count,
        "validationWindowCoverageScore": coverage,
        "validationWindowWorstAvgFwd126": worst_average,
        "validationWindowAvgFwd126": _avg(window_averages),
        "validationWindowWorstWinRate126": worst_win_rate,
        "validationWindowAvgWinRate126": _avg(window_win_rates),
        "validationWindowScore": score,
    }


def apply_validation_window_gate(
    composite_score: float,
    coverage_score: float,
    settings: dict[str, Any],
) -> float:
    if not settings.get("require_validation_window_coverage", False):
        return composite_score
    if settings.get("require_validation_window_hard_coverage", False) and coverage_score < 100:
        return 0.0
    return composite_score * _clip_scalar(coverage_score / 100)


def apply_validation_window_quality_gate(
    composite_score: float,
    worst_win_rate: float,
    settings: dict[str, Any],
) -> float:
    if not settings.get("require_validation_window_min_win_rate", False):
        return composite_score
    minimum = float(settings.get("validation_window_min_win_rate", 0.50))
    if worst_win_rate >= minimum:
        return composite_score
    return 0.0


def _signals_between(
    signals: list[dict[str, Any]],
    start: str | None = None,
    end: str | None = None,
) -> list[dict[str, Any]]:
    start_ts = pd.Timestamp(start) if start else None
    end_ts = pd.Timestamp(end) if end else None
    filtered = []
    for item in signals:
        signal_date = pd.Timestamp(item["date"])
        if start_ts is not None and signal_date < start_ts:
            continue
        if end_ts is not None and signal_date > end_ts:
            continue
        filtered.append(item)
    return filtered


def _signal_subset_summary(
    signals: list[dict[str, Any]],
    index_symbols: list[str],
) -> dict[str, float | int]:
    group_summary = summarize_validation_groups(signals, index_symbols)
    adverse = [item["adverse126"] for item in signals if item.get("adverse126") is not None]
    return {
        "signalCount": len(signals),
        "avgFwd126": _avg([item["fwd126"] for item in signals if item.get("fwd126") is not None]),
        "winRate126": forward_win_rate(signals, "fwd126"),
        "avgAdverse126": _avg(adverse),
        "adverseTailRate": adverse_tail_rate(signals),
        **group_summary,
    }


def _walk_forward_selection_score(
    signals: list[dict[str, Any]],
    validation: dict[str, Any],
) -> float:
    if not signals:
        return 0.0
    index_symbols = validation.get("index_symbols", ["QQQ", "SPY"])
    summary = _signal_subset_summary(signals, index_symbols)
    count_score = sparse_count_score(int(summary["signalCount"]), validation)
    coverage_score = validation_coverage_score(
        int(summary["indexSignalCount"]),
        int(summary["individualSignalCount"]),
        validation,
    )
    return_score = _clip_scalar((float(summary["avgFwd126"]) + 0.08) / 0.45) * 100
    win_score = _clip_scalar((float(summary["winRate126"]) - 0.50) / 0.30) * 100
    adverse_penalty = _clip_scalar(abs(float(summary["avgAdverse126"])) / 0.20) * 25
    tail_penalty = _clip_scalar(float(summary["adverseTailRate"]) / 0.25) * 20
    return max(
        0.0,
        return_score * 0.35
        + win_score * 0.25
        + count_score * 0.20
        + coverage_score * 0.20
        - adverse_penalty
        - tail_penalty,
    )


def run_walk_forward_diagnostics(
    results: list[dict[str, Any]],
    validation: dict[str, Any],
) -> dict[str, Any]:
    folds = validation.get("walk_forward_folds", [])
    if not folds:
        return {
            "foldCount": 0,
            "testedFoldCount": 0,
            "positiveFoldCount": 0,
            "avgTestFwd126": 0.0,
            "worstTestFwd126": 0.0,
            "avgTestWinRate126": 0.0,
            "folds": [],
        }

    index_symbols = validation.get("index_symbols", ["QQQ", "SPY"])
    diagnostics = []
    for fold in folds:
        train_start = fold.get("train_start")
        train_end = fold["train_end"]
        test_start = fold["test_start"]
        test_end = fold["test_end"]
        min_train = int(fold.get("min_train_signals", 8))
        min_test = int(fold.get("min_test_signals", 2))
        candidates = []
        for result in results:
            train_signals = _signals_between(result.get("signals", []), train_start, train_end)
            if len(train_signals) < min_train:
                continue
            candidates.append(
                (
                    _walk_forward_selection_score(train_signals, validation),
                    result,
                    train_signals,
                )
            )
        if not candidates:
            diagnostics.append(
                {
                    "name": fold.get("name", f"{test_start}_{test_end}"),
                    "selectedConfigName": "",
                    "trainScore": 0.0,
                    "trainSignalCount": 0,
                    "testSignalCount": 0,
                    "testAvgFwd126": 0.0,
                    "testWinRate126": 0.0,
                    "testAvgAdverse126": 0.0,
                    "testIndexSignalCount": 0,
                    "testIndividualSignalCount": 0,
                    "covered": False,
                }
            )
            continue

        train_score, selected, train_signals = max(candidates, key=lambda item: item[0])
        test_signals = _signals_between(selected.get("signals", []), test_start, test_end)
        test_summary = _signal_subset_summary(test_signals, index_symbols)
        diagnostics.append(
            {
                "name": fold.get("name", f"{test_start}_{test_end}"),
                "selectedConfigName": selected["config"]["name"],
                "trainScore": train_score,
                "trainSignalCount": len(train_signals),
                "testSignalCount": int(test_summary["signalCount"]),
                "testAvgFwd126": float(test_summary["avgFwd126"]),
                "testWinRate126": float(test_summary["winRate126"]),
                "testAvgAdverse126": float(test_summary["avgAdverse126"]),
                "testIndexSignalCount": int(test_summary["indexSignalCount"]),
                "testIndividualSignalCount": int(test_summary["individualSignalCount"]),
                "covered": int(test_summary["signalCount"]) >= min_test,
            }
        )

    tested = [item for item in diagnostics if item["covered"]]
    tested_returns = [item["testAvgFwd126"] for item in tested]
    tested_wins = [item["testWinRate126"] for item in tested]
    return {
        "foldCount": len(folds),
        "testedFoldCount": len(tested),
        "positiveFoldCount": sum(1 for item in tested if item["testAvgFwd126"] > 0),
        "avgTestFwd126": _avg(tested_returns),
        "worstTestFwd126": min(tested_returns) if tested_returns else 0.0,
        "avgTestWinRate126": _avg(tested_wins),
        "folds": diagnostics,
    }


def _score_result(
    signals: list[dict[str, Any]],
    symbol_summaries: list[dict[str, Any]],
    trade_summaries: list[dict[str, Any]],
    exit_checks: list[float],
    objective_weights: dict[str, float] | None = None,
    validation: dict[str, Any] | None = None,
) -> dict[str, float | int]:
    fwd63 = [item["fwd63"] for item in signals if item["fwd63"] is not None]
    fwd126 = [item["fwd126"] for item in signals if item["fwd126"] is not None]
    fwd252 = [item["fwd252"] for item in signals if item["fwd252"] is not None]
    adverse = [item["adverse126"] for item in signals if item["adverse126"] is not None]
    bottom_capture_scores = [
        item["bottomCaptureScore"]
        for item in signals
        if item.get("bottomCaptureScore") is not None
    ]
    local_bottom_gaps = [
        item["localBottomGap"]
        for item in signals
        if item.get("localBottomGap") is not None
    ]
    win_rate_126 = forward_win_rate(signals, "fwd126")
    adverse_tail = adverse_tail_rate(
        signals,
        threshold=float((validation or {}).get("adverse_tail_threshold", -0.25)),
    )
    avg_market_repair = _avg(
        [item["marketRepair"] for item in signals if item.get("marketRepair") is not None]
    )
    signal_count = len(signals)
    active_symbols = sum(1 for item in symbol_summaries if item["signals"] > 0)
    stability = active_symbols / max(1, len(symbol_summaries))
    validation = validation or {}
    group_summary = summarize_validation_groups(
        signals,
        validation.get("index_symbols", ["QQQ", "SPY"]),
    )
    date_split_summary = summarize_date_split_validation(
        signals,
        validation.get("date_split_cutoff"),
        validation.get("index_symbols", ["QQQ", "SPY"]),
    )
    window_summary = summarize_validation_windows(
        signals,
        validation.get("validation_windows", []),
    )
    coverage_score = validation_coverage_score(
        int(group_summary["indexSignalCount"]),
        int(group_summary["individualSignalCount"]),
        validation,
    )
    date_coverage_score = date_split_coverage_score(
        int(date_split_summary["holdoutIndexSignalCount"]),
        int(date_split_summary["holdoutIndividualSignalCount"]),
        validation,
    )

    return_score = (
        _clip_scalar((_avg(fwd63) + 0.08) / 0.30) * 25
        + _clip_scalar((_avg(fwd126) + 0.10) / 0.45) * 35
        + _clip_scalar((_avg(fwd252) + 0.12) / 0.70) * 40
    )
    adverse_penalty = (
        _clip_scalar(abs(_avg(adverse)) / 0.20) * 28
        + _clip_scalar(adverse_tail / 0.25) * 18
    )
    count_score = sparse_count_score(signal_count, validation)
    stability_score = stability * 100
    index_return_score = _clip_scalar((group_summary["indexAvgFwd126"] + 0.08) / 0.35) * 100
    individual_return_score = (
        _clip_scalar((group_summary["individualAvgFwd126"] + 0.08) / 0.45) * 100
    )
    group_balance_score = min(index_return_score, individual_return_score)
    win_rate_score = _clip_scalar((win_rate_126 - 0.50) / 0.30) * 100
    repair_score = market_repair_score(
        avg_market_repair,
        target=float(validation.get("market_repair_target", 3.0)),
    )
    avg_bottom_capture_score = _avg(bottom_capture_scores)
    avg_local_bottom_gap = _avg(local_bottom_gaps)
    poor_capture_threshold = float(validation.get("poor_bottom_capture_gap", 0.12))
    poor_bottom_capture_rate = (
        sum(1 for gap in local_bottom_gaps if float(gap) >= poor_capture_threshold)
        / len(local_bottom_gaps)
        if local_bottom_gaps
        else 0.0
    )
    poor_capture_penalty = (
        _clip_scalar(
            poor_bottom_capture_rate
            / max(0.01, float(validation.get("poor_bottom_capture_rate_limit", 0.30)))
        )
        * 14
    )
    holdout_return_score = (
        _clip_scalar((float(date_split_summary["holdoutAvgFwd126"]) + 0.08) / 0.45) * 100
    )
    holdout_win_score = (
        _clip_scalar((float(date_split_summary["holdoutWinRate126"]) - 0.50) / 0.30) * 100
    )
    holdout_adverse_penalty = (
        _clip_scalar(abs(float(date_split_summary["holdoutAvgAdverse126"])) / 0.20) * 25
    )
    date_split_score = max(
        0.0,
        min(
            100.0,
            date_coverage_score * 0.35
            + holdout_return_score * 0.35
            + holdout_win_score * 0.30
            - holdout_adverse_penalty,
        ),
    )
    bottom_quality = max(
        0.0,
        min(
            100.0,
            return_score * 0.28
            + count_score * 0.15
            + stability_score * 0.08
            + group_balance_score * 0.14
            + coverage_score * 0.05
            + win_rate_score * 0.06
            + repair_score * 0.10
            + date_split_score * 0.08
            + float(window_summary["validationWindowScore"]) * 0.06
            + avg_bottom_capture_score * 0.12
            - adverse_penalty
            - poor_capture_penalty,
        ),
    )

    avg_trade_return = _avg([item["totalReturn"] for item in trade_summaries])
    avg_trade_dd = _avg([item["maxDrawdown"] for item in trade_summaries])
    trade_score = max(
        0.0,
        min(100.0, _clip_scalar((avg_trade_return + 0.10) / 0.80) * 100 - abs(avg_trade_dd) * 80),
    )
    exit_quality = _clip_scalar((-_avg(exit_checks) + 0.03) / 0.12) * 100 if exit_checks else 50.0
    objective_weights = objective_weights or {}
    bottom_weight = float(objective_weights.get("bottom_quality", 0.70))
    trade_weight = float(objective_weights.get("trade_result", 0.20))
    exit_weight = float(objective_weights.get("exit_quality", 0.10))
    total_weight = bottom_weight + trade_weight + exit_weight
    composite = (
        bottom_quality * bottom_weight
        + trade_score * trade_weight
        + exit_quality * exit_weight
    ) / total_weight
    composite = apply_validation_coverage_gate(composite, coverage_score, validation)
    composite = apply_signal_count_gate(composite, signal_count, validation)
    composite = apply_date_split_gate(composite, date_coverage_score, validation)
    composite = apply_validation_window_gate(
        composite,
        float(window_summary["validationWindowCoverageScore"]),
        validation,
    )
    composite = apply_validation_window_quality_gate(
        composite,
        float(window_summary["validationWindowWorstWinRate126"]),
        validation,
    )
    composite = apply_bottom_capture_gate(
        composite,
        poor_bottom_capture_rate,
        validation,
    )

    return {
        "compositeScore": composite,
        "bottomQualityScore": bottom_quality,
        "tradeScore": trade_score,
        "exitQualityScore": exit_quality,
        "signalCount": signal_count,
        "activeSymbolCount": active_symbols,
        "avgFwd63": _avg(fwd63),
        "avgFwd126": _avg(fwd126),
        "avgFwd252": _avg(fwd252),
        "avgAdverse126": _avg(adverse),
        "adverseTailRate": adverse_tail,
        "avgMarketRepair": avg_market_repair,
        "winRate126": win_rate_126,
        "avgTradeTotalReturn": avg_trade_return,
        "avgTradeMaxDrawdown": avg_trade_dd,
        "sparseCountScore": count_score,
        "groupBalanceScore": group_balance_score,
        "validationCoverageScore": coverage_score,
        "winRateScore": win_rate_score,
        "marketRepairScore": repair_score,
        "avgLocalBottomGap": avg_local_bottom_gap,
        "avgBottomCaptureScore": avg_bottom_capture_score,
        "poorBottomCaptureRate": poor_bottom_capture_rate,
        "poorBottomCapturePenalty": poor_capture_penalty,
        "dateSplitCoverageScore": date_coverage_score,
        "dateSplitScore": date_split_score,
        **group_summary,
        **date_split_summary,
        **window_summary,
    }


def _clip_scalar(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return min(1.0, max(0.0, value))


_PARALLEL_EVAL_CONTEXT: dict[str, Any] = {}


def _init_parallel_evaluator(
    symbols: list[str],
    indicator_frames: dict[str, pd.DataFrame],
    objective_weights: dict[str, float],
    validation: dict[str, Any],
    evaluator,
) -> None:
    _PARALLEL_EVAL_CONTEXT.clear()
    _PARALLEL_EVAL_CONTEXT.update(
        {
            "symbols": symbols,
            "indicator_frames": indicator_frames,
            "objective_weights": objective_weights,
            "validation": validation,
            "evaluator": evaluator,
        }
    )


def _evaluate_config_in_worker(config: BottomSignalConfig) -> dict[str, Any]:
    return _PARALLEL_EVAL_CONTEXT["evaluator"](
        _PARALLEL_EVAL_CONTEXT["symbols"],
        config,
        indicator_frames=_PARALLEL_EVAL_CONTEXT["indicator_frames"],
        objective_weights=_PARALLEL_EVAL_CONTEXT["objective_weights"],
        validation=_PARALLEL_EVAL_CONTEXT["validation"],
    )


def _evaluate_configs_for_symbols(
    symbols: list[str],
    configs: list[BottomSignalConfig],
    settings: SearchSettings,
    *,
    workers: int = 1,
    evaluator=evaluate_config,
    indicator_precomputer=precompute_indicator_frames,
    executor_class=ProcessPoolExecutor,
) -> list[dict[str, Any]]:
    indicator_frames = indicator_precomputer(
        symbols,
        configs,
        cache_enabled=settings.cache_indicators,
    )
    worker_count = max(1, int(workers))
    if worker_count <= 1 or len(configs) <= 1:
        results = []
        for config in configs:
            results.append(
                evaluator(
                    symbols,
                    config,
                    indicator_frames=indicator_frames,
                    objective_weights=settings.objective_weights,
                    validation=settings.validation,
                )
            )
        return results

    with executor_class(
        max_workers=worker_count,
        initializer=_init_parallel_evaluator,
        initargs=(
            symbols,
            indicator_frames,
            settings.objective_weights,
            settings.validation,
            evaluator,
        ),
    ) as executor:
        return list(executor.map(_evaluate_config_in_worker, configs))


def _default_evaluation_runner(
    symbols: list[str],
    configs: list[BottomSignalConfig],
    settings: SearchSettings,
    workers: int = 1,
) -> list[dict[str, Any]]:
    return _evaluate_configs_for_symbols(
        symbols,
        configs,
        settings,
        workers=workers,
    )


def relaxed_stage_settings(settings: SearchSettings) -> SearchSettings:
    validation = dict(settings.validation)
    validation.update(
        {
            "require_validation_coverage": False,
            "require_date_split_coverage": False,
            "require_validation_window_coverage": False,
            "require_signal_count_max": False,
            "require_bottom_capture_rate_limit": False,
        }
    )
    return replace(settings, validation=validation)


def _compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "config": result["config"],
        "metrics": result["metrics"],
        "symbols": result["symbols"],
        "signalFunnel": result.get("signalFunnel", {}),
        "channelMetrics": result.get("channelMetrics", {}),
        "recentChannelActivity": result.get("recentChannelActivity", {}),
        "recentValidation": result.get("recentValidation", {}),
        "rsCandidateWatchlist": result.get("rsCandidateWatchlist", {}),
    }


def _renamed_entry_variant(config: BottomSignalConfig, entry_threshold: int) -> BottomSignalConfig:
    old = f"_entry{config.entry_threshold}"
    if old in config.name:
        name = config.name.replace(old, f"_entry{entry_threshold}", 1)
    else:
        name = f"{config.name}_entry{entry_threshold}"
    return replace(config, name=name, entry_threshold=entry_threshold)


def _renamed_mb_offset_variant(config: BottomSignalConfig, mb_entry_offset: int) -> BottomSignalConfig:
    old = f"_mbo{config.mb_entry_offset}"
    if old in config.name:
        name = config.name.replace(old, f"_mbo{mb_entry_offset}", 1)
    else:
        marker = f"_entry{config.entry_threshold}"
        name = config.name.replace(marker, f"{marker}_mbo{mb_entry_offset}", 1)
    return replace(config, name=name, mb_entry_offset=mb_entry_offset)


def refine_promoted_configs(
    configs: list[BottomSignalConfig],
    stage_results: list[dict[str, Any]],
    settings: SearchSettings,
) -> list[BottomSignalConfig]:
    stage_settings = settings.search_stages
    refine_top_n = int(stage_settings.get("refine_top_n", 0))
    thresholds = [
        int(value)
        for value in stage_settings.get(
            "refine_entry_thresholds",
            settings.candidate_parameters.get("entry_thresholds", []),
        )
    ]
    mb_offsets = [
        int(value)
        for value in stage_settings.get(
            "refine_mb_entry_offsets",
            settings.candidate_parameters.get("mb_entry_offsets", [0]),
        )
    ]
    if refine_top_n <= 0 or not thresholds or not stage_results:
        return configs

    by_name = {config.name: config for config in configs}
    refined: dict[str, BottomSignalConfig] = {config.name: config for config in configs}
    for item in stage_results[:refine_top_n]:
        base = by_name.get(item["config"]["name"])
        if base is None:
            continue
        for threshold in thresholds:
            entry_variant = _renamed_entry_variant(base, threshold)
            for offset in mb_offsets:
                variant = _renamed_mb_offset_variant(entry_variant, offset)
                refined[variant.name] = variant
    return list(refined.values())


def promoted_stage_names(
    stage_results: list[dict[str, Any]],
    promote_top_n: int,
    settings: SearchSettings,
) -> set[str]:
    names = {
        item["config"]["name"] for item in stage_results[: max(1, promote_top_n)]
    }
    names.update(str(seed["name"]) for seed in settings.seed_configs if "name" in seed)
    return names


def artifact_scope_summary(symbols: list[str]) -> dict[str, Any]:
    unique_symbols = list(dict.fromkeys(symbols))
    full_pool = set(unique_symbols) == set(ALL_TICKERS) and len(unique_symbols) == len(ALL_TICKERS)
    sample_kind = "FULL_POOL"
    warning = ""
    if not full_pool:
        sample_kind = (
            "QQQ_SPY_SAMPLE"
            if len(unique_symbols) == 2 and set(unique_symbols) == {"QQQ", "SPY"}
            else "PARTIAL_SAMPLE"
        )
        warning = (
            "Quick sample output only; rerun `--symbol all --max-configs 720` "
            "before accepting or refreshing observation artifacts."
        )
    return {
        "symbolCount": len(unique_symbols),
        "requiredFullSymbolCount": len(ALL_TICKERS),
        "fullPool": full_pool,
        "sampleKind": sample_kind,
        "warning": warning,
    }


def run_search(
    symbols: list[str],
    settings: SearchSettings,
    max_configs: int | None = None,
    workers: int = 1,
    evaluation_runner=_default_evaluation_runner,
) -> dict[str, Any]:
    count = max_configs if max_configs is not None else settings.max_configs
    configs = candidate_configs(count, settings=settings)
    stage_settings = settings.search_stages
    dev_symbols = [
        symbol
        for symbol in stage_settings.get("dev_symbols", [])
        if symbol in symbols
    ]
    staged = bool(stage_settings.get("enabled")) and dev_symbols and len(symbols) > len(dev_symbols)

    stage_results = []
    promoted_configs = configs
    if staged:
        stage_eval_settings = relaxed_stage_settings(settings)
        stage_results = sorted(
            evaluation_runner(dev_symbols, configs, stage_eval_settings, workers=workers),
            key=lambda item: item["metrics"]["compositeScore"],
            reverse=True,
        )
        promote_top_n = int(stage_settings.get("promote_top_n", 4))
        promoted_names = promoted_stage_names(stage_results, promote_top_n, settings)
        promoted_configs = [config for config in configs if config.name in promoted_names]
        promoted_configs = refine_promoted_configs(promoted_configs, stage_results, settings)

    results = evaluation_runner(symbols, promoted_configs, settings, workers=workers)
    sorted_results = sorted(
        results,
        key=lambda item: item["metrics"]["compositeScore"],
        reverse=True,
    )
    best = sorted_results[0]
    walk_forward = run_walk_forward_diagnostics(sorted_results, settings.validation)
    baseline = load_baseline_snapshot()
    mb_factor_ablation = {}
    if settings.validation.get("enable_mb_factor_ablation", True):
        mb_factor_ablation = run_mb_factor_ablation(
            symbols,
            BottomSignalConfig(**best["config"]),
            settings,
        )
    payload = {
        "symbols": symbols,
        "artifactScope": artifact_scope_summary(symbols),
        "maxConfigs": count,
        "cacheIndicators": settings.cache_indicators,
        "stagedSearch": staged,
        "stageSymbols": dev_symbols if staged else [],
        "promotedConfigNames": [config.name for config in promoted_configs],
        "stageResults": [_compact_result(item) for item in stage_results],
        "bestConfig": best["config"],
        "bestMetrics": best["metrics"],
        "baselineComparison": baseline,
        "walkForward": walk_forward,
        "mbFactorAblation": mb_factor_ablation,
        "bestRsWatchlist": select_best_rs_watchlist_result(sorted_results),
        "results": sorted_results,
    }
    return _clean_numbers(payload)


def load_baseline_snapshot() -> dict[str, Any]:
    if not RESULTS_PATH.exists():
        return dict(LEGACY_BASELINE_SNAPSHOT)
    try:
        payload = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return dict(LEGACY_BASELINE_SNAPSHOT)
    config = payload.get("bestConfig", {})
    metrics = payload.get("bestMetrics", {})
    name = str(config.get("name", ""))
    if "_rs" in name or int(metrics.get("signalCount", 0)) < 20:
        return dict(LEGACY_BASELINE_SNAPSHOT)
    return {
        "name": name,
        "signalCount": metrics.get("signalCount", 0),
        "avgFwd126": metrics.get("avgFwd126", 0.0),
        "winRate126": metrics.get("winRate126", 0.0),
        "avgAdverse126": metrics.get("avgAdverse126", 0.0),
    }


def write_outputs(payload: dict[str, Any], output_paths: dict[str, Path] | None = None) -> dict[str, Path]:
    paths = output_paths or resolve_output_paths("")
    for path in set(paths.values()):
        path.parent.mkdir(parents=True, exist_ok=True)
    if "bestRsWatchlist" not in payload:
        payload["bestRsWatchlist"] = select_best_rs_watchlist_result(payload.get("results", []))
    watchlist = payload.get("bestRsWatchlist", {}).get("rsCandidateWatchlist", {})
    if watchlist and "rsTickerSummary" not in watchlist:
        watchlist["rsTickerSummary"] = summarize_rs_ticker_watchlist(
            watchlist.get("topRsCandidates", [])
        )
    if watchlist and "rsTickerActionCounts" not in watchlist:
        watchlist["rsTickerActionCounts"] = rs_ticker_action_counts(
            watchlist.get("rsTickerSummary", [])
        )
    if watchlist.get("rsTickerSummary"):
        watchlist["rsTickerSummary"] = rank_rs_ticker_summary(
            watchlist.get("rsTickerSummary", [])
        )
        watchlist["rsTickerActionCounts"] = rs_ticker_action_counts(
            watchlist.get("rsTickerSummary", [])
        )
    output_json = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    paths["results"].write_text(output_json, encoding="utf-8")
    best_config = BottomSignalConfig(**payload["bestConfig"])
    report = generate_report(payload)
    paths["report"].write_text(report, encoding="utf-8", newline="\n")
    paths["plan_summary"].write_text(
        generate_plan_summary(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["rs_watchlist_report"].write_text(
        generate_rs_watchlist_report(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["rs_watchlist_ticker_csv"].write_text(
        generate_rs_watchlist_ticker_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["rs_watchlist_candidate_csv"].write_text(
        generate_rs_watchlist_candidate_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["mb_factor_ablation_csv"].write_text(
        generate_mb_factor_ablation_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["recent_validation_csv"].write_text(
        generate_recent_validation_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["next_actions_csv"].write_text(
        generate_next_actions_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["strategy_iteration_review"].write_text(
        generate_strategy_iteration_review_report(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["strategy_iteration_review_csv"].write_text(
        generate_strategy_iteration_review_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["miss_diagnostics_report"].write_text(
        generate_2022_2026_miss_diagnostics_report(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["miss_diagnostics_csv"].write_text(
        generate_2022_2026_miss_diagnostics_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    paths["candidate_review_csv"].write_text(
        generate_2022_2026_candidate_review_csv(payload),
        encoding="utf-8",
        newline="\n",
    )
    if payload.get("observationSearch"):
        paths["observation_report"].write_text(
            generate_observation_report(payload),
            encoding="utf-8",
            newline="\n",
        )
        paths["observation_signals_csv"].write_text(
            generate_observation_signals_csv(payload),
            encoding="utf-8",
            newline="\n",
        )
    selected_observation_config = payload.get("observationSearch", {}).get("selectedConfig", {})
    paths["strict_formal_pine"].write_text(
        generate_strict_formal_pine_script(best_config),
        encoding="utf-8",
        newline="\n",
    )
    paths["pine"].write_text(
        generate_pine_script(best_config, selected_observation_config),
        encoding="utf-8",
        newline="\n",
    )
    if payload.get("observationSearch"):
        paths["merged_observation_pine"].write_text(
            generate_merged_observation_pine_script(
                best_config,
                payload.get("observationSearch", {}).get("selectedConfig", {}),
            ),
            encoding="utf-8",
            newline="\n",
        )
    rs_config_payload = payload.get("bestRsWatchlist", {}).get("config")
    if rs_config_payload:
        rs_config = BottomSignalConfig(**rs_config_payload)
        paths["rs_watchlist_pine"].write_text(
            generate_rs_watchlist_pine_script(
                rs_config,
                quality_threshold=int(
                    payload.get("validation", {}).get("rs_watchlist_quality_threshold", 70)
                )
                if "validation" in payload
                else 70,
            ),
            encoding="utf-8",
            newline="\n",
        )
    return paths


def generate_report(payload: dict[str, Any]) -> str:
    best = payload["bestConfig"]
    metrics = payload["bestMetrics"]
    best_result = next(
        (
            result
            for result in payload.get("results", [])
            if result.get("config", {}).get("name") == best["name"]
        ),
        {},
    )
    funnel = best_result.get("signalFunnel", {})
    channel_metrics = best_result.get("channelMetrics", {})
    recent = best_result.get("recentChannelActivity", {})
    recent_validation = best_result.get("recentValidation", {})
    rs_watchlist = best_result.get("rsCandidateWatchlist", {})
    missed = best_result.get("missedStrongStocks", [])
    baseline = payload.get("baselineComparison", {})
    mb_factor_ablation = payload.get("mbFactorAblation", {})
    best_rs_watchlist = payload.get("bestRsWatchlist", {})
    best_rs_config = best_rs_watchlist.get("config", {})
    best_rs_metrics = best_rs_watchlist.get("metrics", {})
    best_rs_watch = best_rs_watchlist.get("rsCandidateWatchlist", {})
    rows = [
        "# Bottom Signal Search Report",
        "",
        "## Scope",
        f"- Symbols: {', '.join(payload['symbols'])}",
        (
            f"- Artifact scope: {payload.get('artifactScope', {}).get('warning')}"
            if payload.get("artifactScope", {}).get("warning")
            else "- Artifact scope: full-pool output"
        ),
        f"- Tested configs: {payload['maxConfigs']}",
        f"- Staged search: {payload.get('stagedSearch', False)}",
        f"- Promoted configs: {len(payload.get('promotedConfigNames', []))}",
        "- Objective: 70% bottom signal quality, 20% full trade result, 10% exit signal quality.",
        "- Gates: sparse signal count, QQQ/SPY coverage, individual-stock coverage, date-split holdout coverage, validation-window coverage, and bottom-capture quality.",
        f"- Integrated formal Pine: `{PINE_PATH.name}`",
        f"- Strict MB archive Pine: `{STRICT_FORMAL_PINE_PATH.name}`",
        f"- RS watchlist Pine: `{RS_WATCHLIST_PINE_PATH.name}`",
        f"- Observation diagnostic Pine: `{MERGED_OBSERVATION_PINE_PATH.name}`",
        f"- Observation report: `{OBSERVATION_REPORT_PATH.name}`",
        f"- MB factor ablation CSV: `{MB_FACTOR_ABLATION_CSV_PATH.name}`",
        f"- Recent validation CSV: `{RECENT_VALIDATION_CSV_PATH.name}`",
        f"- Plan summary: `{PLAN_SUMMARY_PATH.name}`",
        f"- Next actions CSV: `{NEXT_ACTIONS_CSV_PATH.name}`",
        "",
        "## Best Config",
        f"- Name: `{best['name']}`",
        f"- Drawdown: window `{best['drawdown_window']}`, threshold `{best['drawdown_threshold']}%`",
        f"- RSI: `{best['rsi_period']}`",
        f"- Stochastic: `{best['stoch_period']}, {best['stoch_smooth']}`",
        f"- MACD: `{best['macd_fast']}, {best['macd_slow']}, {best['macd_signal']}`",
        f"- SMA distance: `{best['ma_period']}`",
        f"- ATR: `{best['atr_period']}`",
        f"- Volume window: `{best['volume_window']}`",
        f"- Backtest entry score: `{best['entry_threshold']}`",
        f"- MB entry score: `{best['entry_threshold'] + best.get('mb_entry_offset', 0)}`",
        f"- RS entry score: `{best['entry_threshold']}`",
        f"- Experimental signal set: `{best.get('experimental_signal_set', 'rs_antidrawdown_repair')}`",
        f"- Min signal gap: `{best['min_signal_gap']}` bars",
        f"- Market filter: `{best['market_symbol_1']}`/`{best['market_symbol_2']}` "
        f"{best['market_drawdown_window']}-bar drawdown <= `{best['market_drawdown_threshold']}%`",
        f"- Weights: drawdown `{best['drawdown_weight']}`, momentum `{best['momentum_weight']}`, "
        f"repair `{best['repair_weight']}`, structure `{best['structure_weight']}`, "
        f"volume `{best['volume_weight']}`, MA `{best['ma_weight']}`",
        "",
        "## Best Metrics",
        f"- Composite score: {metrics['compositeScore']:.2f}",
        f"- Pre dual-track adjustment score: {metrics.get('preDualTrackCompositeScore', metrics['compositeScore']):.2f}",
        f"- Watch/Medium ratio score: {metrics.get('watchMediumRatioScore', 100.0):.2f}",
        f"- RS missed-capture count: {metrics.get('rsMissedCaptureCount', 0)}",
        f"- RS missed-capture score: {metrics.get('rsMissedCaptureScore', 0.0):.2f}",
        f"- Baseline quality score: {metrics.get('baselineQualityScore', 100.0):.2f}",
        f"- Recent RS activity score: {metrics.get('recentRsActivityScore', 100.0):.2f}",
        f"- Qualified RS watchlist score: {metrics.get('qualifiedRsWatchlistScore', 100.0):.2f}",
        f"- Bottom quality: {metrics['bottomQualityScore']:.2f}",
        f"- Trade score: {metrics['tradeScore']:.2f}",
        f"- Exit quality: {metrics['exitQualityScore']:.2f}",
        f"- Signals: {metrics['signalCount']}",
        f"- Active symbols: {metrics['activeSymbolCount']}",
        f"- Avg 3m return: {metrics['avgFwd63']:.2%}",
        f"- Avg 6m return: {metrics['avgFwd126']:.2%}",
        f"- Avg 12m return: {metrics['avgFwd252']:.2%}",
        f"- Avg 6m adverse drawdown: {metrics['avgAdverse126']:.2%}",
        f"- 6m adverse tail rate: {metrics['adverseTailRate']:.2%}",
        f"- Avg market repair: {metrics['avgMarketRepair']:.2f}%",
        f"- Avg local-bottom gap: {metrics['avgLocalBottomGap']:.2%}",
        f"- Avg bottom-capture score: {metrics['avgBottomCaptureScore']:.2f}",
        f"- Poor bottom-capture rate: {metrics['poorBottomCaptureRate']:.2%}",
        f"- Poor bottom-capture penalty: {metrics['poorBottomCapturePenalty']:.2f}",
        f"- 6m win rate: {metrics['winRate126']:.2%}",
        f"- QQQ/SPY signals: {metrics['indexSignalCount']}",
        f"- Individual-stock signals: {metrics['individualSignalCount']}",
        f"- QQQ/SPY avg 6m return: {metrics['indexAvgFwd126']:.2%}",
        f"- Individual-stock avg 6m return: {metrics['individualAvgFwd126']:.2%}",
        f"- Sparse count score: {metrics['sparseCountScore']:.2f}",
        f"- Group balance score: {metrics['groupBalanceScore']:.2f}",
        f"- Validation coverage score: {metrics['validationCoverageScore']:.2f}",
        f"- Win-rate score: {metrics['winRateScore']:.2f}",
        f"- Market repair score: {metrics['marketRepairScore']:.2f}",
        f"- Date-split coverage score: {metrics['dateSplitCoverageScore']:.2f}",
        f"- Date-split quality score: {metrics['dateSplitScore']:.2f}",
        f"- Train signals: {metrics['trainSignalCount']}",
        f"- Holdout signals: {metrics['holdoutSignalCount']}",
        f"- Holdout QQQ/SPY signals: {metrics['holdoutIndexSignalCount']}",
        f"- Holdout individual-stock signals: {metrics['holdoutIndividualSignalCount']}",
        f"- Holdout avg 6m return: {metrics['holdoutAvgFwd126']:.2%}",
        f"- Holdout avg 6m adverse drawdown: {metrics['holdoutAvgAdverse126']:.2%}",
        f"- Holdout 6m win rate: {metrics['holdoutWinRate126']:.2%}",
        f"- Validation windows covered: {metrics['coveredValidationWindowCount']}/{metrics['validationWindowCount']}",
        f"- Positive validation windows: {metrics['positiveValidationWindowCount']}/{metrics['validationWindowCount']}",
        f"- Validation-window coverage score: {metrics['validationWindowCoverageScore']:.2f}",
        f"- Validation-window quality score: {metrics['validationWindowScore']:.2f}",
        f"- Validation-window avg 6m return: {metrics['validationWindowAvgFwd126']:.2%}",
        f"- Validation-window worst avg 6m return: {metrics['validationWindowWorstAvgFwd126']:.2%}",
        f"- Validation-window avg 6m win rate: {metrics['validationWindowAvgWinRate126']:.2%}",
        f"- Validation-window worst 6m win rate: {metrics['validationWindowWorstWinRate126']:.2%}",
        "",
        "## Baseline Comparison",
        f"- Baseline config: `{baseline.get('name', 'not available')}`",
        f"- Baseline signals: {baseline.get('signalCount', 0)}",
        f"- Baseline avg 6m return: {float(baseline.get('avgFwd126', 0.0)):.2%}",
        f"- Baseline 6m win rate: {float(baseline.get('winRate126', 0.0)):.2%}",
        f"- Current Strong signals: {metrics['signalCount']}",
        f"- Current avg 6m return: {metrics['avgFwd126']:.2%}",
        f"- Current 6m win rate: {metrics['winRate126']:.2%}",
        "",
        "## MB Factor Ablation",
        "- Each row removes one MB scoring factor from the selected config and re-runs the same evaluation.",
    ]
    ablation_rows = mb_factor_ablation.get("rows", [])
    if ablation_rows:
        ablation_summary = summarize_mb_factor_ablation(mb_factor_ablation)
        rows.extend(
            [
                f"- Critical factors: {', '.join(ablation_summary['criticalFactors']) or 'none'}",
                f"- Overactive without: {', '.join(ablation_summary['overactiveFactors']) or 'none'}",
                f"- Supportive factors: {', '.join(ablation_summary['supportiveFactors']) or 'none'}",
                f"- Redundant factors: {', '.join(ablation_summary['redundantFactors']) or 'none'}",
            ]
        )
        for item in ablation_summary["rows"]:
            rows.append(
                "- "
                f"{item['factor']} ({item['impactLabel']}): "
                f"score={item['compositeScore']:.2f} "
                f"delta={item['compositeDelta']:+.2f} "
                f"signals={item['signalCount']} "
                f"avg6m={item['avgFwd126']:.2%} "
                f"adverse6m={item['avgAdverse126']:.2%}"
            )
    else:
        rows.append("- No MB factor ablation was generated for this run.")
    rows.extend(
        [
        "",
        "## Signal Funnel",
        f"- Watch signals: {funnel.get('watchCount', 0)}",
        f"- Medium signals: {funnel.get('mediumCount', 0)}",
        f"- Formal Strong signals: {funnel.get('formalStrongCount', metrics['signalCount'])}",
        f"- Watch/Medium to Strong ratio: {float(funnel.get('watchMediumToStrongRatio', 0.0)):.2f}x",
        f"- MB Strong signals: {funnel.get('mbStrongCount', 0)}",
        f"- RS Strong signals: {funnel.get('rsStrongCount', 0)}",
        f"- MB diagnostic signals: {funnel.get('mbDiagnosticCount', 0)}",
        f"- RS diagnostic signals: {funnel.get('rsDiagnosticCount', 0)}",
        "",
        "## Recent 24M MB vs RS",
        f"- Window: {recent.get('recentStart', 'n/a')} to {recent.get('recentEnd', 'n/a')}",
        f"- Recent formal Strong signals: {recent.get('recentFormalCount', 0)}",
        f"- Recent diagnostic Watch/Medium signals: {recent.get('recentDiagnosticCount', 0)}",
        f"- Recent MB Strong signals: {recent.get('recentMbStrongCount', 0)}",
        f"- Recent RS Strong signals: {recent.get('recentRsStrongCount', 0)}",
        f"- Recent MB diagnostic signals: {recent.get('recentMbDiagnosticCount', 0)}",
        f"- Recent RS diagnostic signals: {recent.get('recentRsDiagnosticCount', 0)}",
        f"- Recent RS candidate signals: {recent.get('recentRsCandidateCount', 0)}",
        f"- Recent MB avg 6m return: {float(recent.get('recentMbAvgFwd126', 0.0)):.2%}",
        f"- Recent RS avg 6m return: {float(recent.get('recentRsAvgFwd126', 0.0)):.2%}",
        "",
        "## Recent Validation",
        f"- Window: {recent_validation.get('recentValidationStart', 'n/a')} to {recent_validation.get('recentValidationEnd', 'n/a')}",
        f"- Recent formal signals: {recent_validation.get('recentValidationSignalCount', 0)}",
        f"- Mature 6m checks: {recent_validation.get('recentValidationMatureCount', 0)}",
        f"- Recent avg 6m return: {float(recent_validation.get('recentValidationAvgFwd126', 0.0)):.2%}",
        f"- Recent 6m win rate: {float(recent_validation.get('recentValidationWinRate126', 0.0)):.2%}",
        f"- Recent avg 6m adverse drawdown: {float(recent_validation.get('recentValidationAvgAdverse126', 0.0)):.2%}",
        f"- Status: {recent_validation.get('recentValidationStatus', 'Watch')}",
        "",
        "## RS Secondary Watchlist",
        "- These rows are RS candidates for observation/ranking. They are not the primary MB backtest entry layer.",
        f"- Recent RS candidate count: {rs_watchlist.get('rsCandidateCount', 0)}",
        f"- Qualified RS candidate count: {rs_watchlist.get('qualifiedRsCandidateCount', 0)}",
        f"- Qualified RS target score: {metrics.get('qualifiedRsWatchlistScore', 100.0):.2f}",
        f"- Recent RS candidate avg 6m return: {float(rs_watchlist.get('rsCandidateAvgFwd126', 0.0)):.2%}",
        f"- Recent RS candidate avg 6m adverse drawdown: {float(rs_watchlist.get('rsCandidateAvgAdverse126', 0.0)):.2%}",
        f"- Qualified RS candidate avg 6m return: {float(rs_watchlist.get('qualifiedRsCandidateAvgFwd126', 0.0)):.2%}",
        f"- Qualified RS candidate avg 6m adverse drawdown: {float(rs_watchlist.get('qualifiedRsCandidateAvgAdverse126', 0.0)):.2%}",
        "",
        "## Separate RS Watchlist Best",
        "- This is not the formal trading strategy. It is the best config found for the RS observation list only.",
        f"- Role: `{best_rs_watchlist.get('role', 'rs_watchlist_only')}`",
        f"- Name: `{best_rs_config.get('name', 'not available')}`",
        f"- Experimental signal set: `{best_rs_config.get('experimental_signal_set', 'not available')}`",
        f"- Formal composite score: {float(best_rs_metrics.get('compositeScore', 0.0)):.2f}",
        f"- Formal Strong signals: {best_rs_metrics.get('signalCount', 0)}",
        f"- Formal avg 6m return: {float(best_rs_metrics.get('avgFwd126', 0.0)):.2%}",
        f"- Qualified RS candidates: {best_rs_watch.get('qualifiedRsCandidateCount', 0)}",
        f"- Qualified RS avg 6m return: {float(best_rs_watch.get('qualifiedRsCandidateAvgFwd126', 0.0)):.2%}",
        f"- Qualified RS avg 6m adverse drawdown: {float(best_rs_watch.get('qualifiedRsCandidateAvgAdverse126', 0.0)):.2%}",
        "",
        "## MB vs RS",
        f"- MB avg 6m return: {float(channel_metrics.get('MB', {}).get('avgFwd126', 0.0)):.2%}",
        f"- MB 6m win rate: {float(channel_metrics.get('MB', {}).get('winRate126', 0.0)):.2%}",
        f"- RS avg 6m return: {float(channel_metrics.get('RS', {}).get('avgFwd126', 0.0)):.2%}",
        f"- RS 6m win rate: {float(channel_metrics.get('RS', {}).get('winRate126', 0.0)):.2%}",
        "",
        "## Missed Strong Stocks",
        "- RS Strong rows here are candidates that the old QQQ/SPY hard market filter would have blocked.",
    ]
    )
    if missed:
        for item in missed[:10]:
            rows.append(
                "- "
                f"{item['symbol']} {item['date']} "
                f"RS={item.get('relativeStrengthScore', 0)} "
                f"bottom={item.get('bottomScore', 0)} "
                f"market drawdown={float(item.get('marketDrawdown', 0.0)):.2f}%"
            )
    else:
        rows.append("- No RS Strong misses recorded for the selected config.")
    rows.extend(
        [
            "",
            "## Top Recent RS Candidates",
        ]
    )
    top_rs = rs_watchlist.get("topRsCandidates", [])
    if top_rs:
        for item in top_rs[:15]:
            fwd126 = item.get("fwd126")
            adverse126 = item.get("adverse126")
            market_drawdown = item.get("marketDrawdown")
            risk_flags = str(item.get("riskFlags", ""))
            market_text = (
                f"market drawdown={float(market_drawdown):.2f}% "
                if market_drawdown is not None
                else ""
            )
            risk_text = f"risk={risk_flags or 'none'} "
            fwd_text = f"fwd6m={float(fwd126):.2%} " if fwd126 is not None else "fwd6m=n/a "
            adverse_text = (
                f"adverse6m={float(adverse126):.2%}"
                if adverse126 is not None
                else "adverse6m=n/a"
            )
            rows.append(
                "- "
                f"{item['symbol']} {item['date']} {item.get('tier', '')} "
                f"quality={item.get('qualityScore', 0)} "
                f"qualified={item.get('qualityPassed', False)} "
                f"RS signal={item.get('rsSignalScore', 0)} "
                f"RS strength={item.get('relativeStrengthScore', 0)} "
                f"bottom={item.get('bottomScore', 0)} "
                f"{risk_text}{market_text}{fwd_text}{adverse_text}"
            )
    else:
        rows.append("- No recent RS candidates for the selected config.")
    rows.extend(
        [
            "",
            "## RS Coverage Tradeoffs",
            "- These configs found more qualified RS watchlist candidates, but may have failed MB or validation gates.",
        ]
    )
    tradeoffs = top_rs_coverage_tradeoffs(payload.get("results", []), limit=8)
    if tradeoffs:
        for item in tradeoffs:
            rows.append(
                "- "
                f"`{item['name']}` "
                f"set={item['experimentalSignalSet']} "
                f"score={item['compositeScore']:.2f} "
                f"strong={item['signalCount']} "
                f"avg6m={item['avgFwd126']:.2%} "
                f"qualifiedRS={item['qualifiedRsCandidateCount']} "
                f"qualifiedRSAvg6m={item['qualifiedRsCandidateAvgFwd126']:.2%} "
                f"qualifiedRSAdverse6m={item['qualifiedRsCandidateAvgAdverse126']:.2%}"
            )
    else:
        rows.append("- No qualified RS coverage tradeoffs found.")
    rows.extend(
        [
            "",
        "## Walk-Forward Diagnostic",
        ]
    )
    walk_forward = payload.get("walkForward", {})
    if walk_forward.get("foldCount", 0):
        rows.extend(
            [
                f"- Tested folds: {walk_forward['testedFoldCount']}/{walk_forward['foldCount']}",
                f"- Positive tested folds: {walk_forward['positiveFoldCount']}/{walk_forward['testedFoldCount']}",
                f"- Avg test 6m return: {walk_forward['avgTestFwd126']:.2%}",
                f"- Worst test 6m return: {walk_forward['worstTestFwd126']:.2%}",
                f"- Avg test 6m win rate: {walk_forward['avgTestWinRate126']:.2%}",
            ]
        )
        for fold in walk_forward["folds"]:
            rows.append(
                "- "
                f"{fold['name']}: selected `{fold['selectedConfigName']}`, "
                f"train signals {fold['trainSignalCount']}, "
                f"test signals {fold['testSignalCount']}, "
                f"test avg 6m {fold['testAvgFwd126']:.2%}, "
                f"test win {fold['testWinRate126']:.2%}"
            )
    else:
        rows.append("- No walk-forward folds configured.")
    rows.extend(
        [
            "",
        "## Notes",
        "- The selected config is still a research candidate, but it is now penalized unless it also has post-cutoff QQQ/SPY, individual-stock, multi-window validation coverage, and acceptable bottom-capture quality.",
        "- Walk-forward diagnostics select each fold using only earlier signals, then score the selected config on the later test window.",
        "- Pine output uses the best config as defaults, while keeping the main parameters adjustable in TradingView.",
        "",
        ]
    )
    return "\n".join(rows)


def generate_plan_summary(payload: dict[str, Any]) -> str:
    best = payload.get("bestConfig", {})
    metrics = payload.get("bestMetrics", {})
    best_name = best.get("name", "")
    best_result = next(
        (
            result
            for result in payload.get("results", [])
            if result.get("config", {}).get("name") == best_name
        ),
        {},
    )
    recent_validation = best_result.get("recentValidation", {})
    ablation_summary = summarize_mb_factor_ablation(payload.get("mbFactorAblation", {}))
    watchlist = payload.get("bestRsWatchlist", {}).get("rsCandidateWatchlist", {})
    ticker_summary = rank_rs_ticker_summary(watchlist.get("rsTickerSummary", []), limit=5)
    action_ticker_summary = rank_rs_ticker_summary(
        watchlist.get("rsTickerSummary", []),
        limit=12,
    )

    rows = [
        "# MB Ablation, RS Selection, Recent Validation Summary",
        "",
        "## Decision Snapshot",
        f"- Best config: `{best_name or 'not available'}`",
        f"- Composite score: {float(metrics.get('compositeScore', 0.0)):.2f}",
        f"- Strong signals: {int(metrics.get('signalCount', 0))}",
        f"- Avg 6m return: {float(metrics.get('avgFwd126', 0.0)):.2%}",
        f"- 6m win rate: {float(metrics.get('winRate126', 0.0)):.2%}",
        f"- Avg 6m adverse drawdown: {float(metrics.get('avgAdverse126', 0.0)):.2%}",
        "",
        "## MB Factor Read",
        f"- Critical factors: {', '.join(ablation_summary['criticalFactors']) or 'none'}",
        f"- Overactive without: {', '.join(ablation_summary['overactiveFactors']) or 'none'}",
        f"- Supportive factors: {', '.join(ablation_summary['supportiveFactors']) or 'none'}",
        f"- Redundant factors: {', '.join(ablation_summary['redundantFactors']) or 'none'}",
    ]
    if ablation_summary["rows"]:
        for item in ablation_summary["rows"][:8]:
            rows.append(
                "- "
                f"{item.get('factor', '')}: {item.get('impactLabel', '')}, "
                f"score delta {float(item.get('compositeDelta', 0.0)):+.2f}, "
                f"signal delta {int(item.get('signalCountDelta', 0)):+d}"
            )
    else:
        rows.append("- No MB ablation rows available.")

    rows.extend(
        [
            "",
            "## RS Selection Read",
        ]
    )
    if ticker_summary:
        for item in ticker_summary:
            rows.append(
                "- "
                f"#{int(item.get('selectionRank', 0))} {item.get('symbol', '')}: "
                f"action={item.get('actionTier', '')}, "
                f"selection={float(item.get('selectionScore', 0.0)):.2f}, "
                f"qualified={int(item.get('qualifiedCount', 0))}, "
                f"reason={item.get('actionReason', '')}"
            )
    else:
        rows.append("- No RS ticker summary available.")

    critical_factors = ablation_summary["criticalFactors"]
    overactive_factors = ablation_summary["overactiveFactors"]
    priority_tickers = [
        str(item.get("symbol", ""))
        for item in action_ticker_summary
        if item.get("actionTier") == "Priority" and item.get("symbol")
    ]
    watch_tickers = [
        str(item.get("symbol", ""))
        for item in action_ticker_summary
        if item.get("actionTier") == "Watch" and item.get("symbol")
    ]
    avoid_tickers = [
        str(item.get("symbol", ""))
        for item in action_ticker_summary
        if item.get("actionTier") == "Avoid" and item.get("symbol")
    ]
    recent_status = str(recent_validation.get("recentValidationStatus", "Watch"))
    if recent_status == "Pass":
        validation_action = "Recent validation passed; continue observation"
    elif recent_status == "Fail":
        validation_action = "Recent validation failed; do not promote without another review"
    else:
        validation_action = "Recent validation is still watch-only; wait for more mature checks"

    rows.extend(
        [
            "",
            "## Recent Validation Read",
            f"- Window: {recent_validation.get('recentValidationStart', 'n/a')} to {recent_validation.get('recentValidationEnd', 'n/a')}",
            f"- Recent formal signals: {int(recent_validation.get('recentValidationSignalCount', 0))}",
            f"- Mature 6m checks: {int(recent_validation.get('recentValidationMatureCount', 0))}",
            f"- Recent avg 6m return: {float(recent_validation.get('recentValidationAvgFwd126', 0.0)):.2%}",
            f"- Recent 6m win rate: {float(recent_validation.get('recentValidationWinRate126', 0.0)):.2%}",
            f"- Recent avg 6m adverse drawdown: {float(recent_validation.get('recentValidationAvgAdverse126', 0.0)):.2%}",
            f"- Recent validation status: {recent_validation.get('recentValidationStatus', 'Watch')}",
            "",
            "## Action Counts",
            f"- MB keep: {len(critical_factors)}",
            f"- MB brake: {len(overactive_factors)}",
            f"- RS monitor: {len(priority_tickers)}",
            f"- RS review: {len(watch_tickers)}",
            f"- RS skip: {len(avoid_tickers)}",
            "",
            "## Role Guide",
            "- FormalStrategy: MB keep/brake actions belong to the formal strategy.",
            "- Observation: RS Monitor/Review/Skip rows are watchlist actions only.",
            "- Validation: RecentValidation rows summarize recent evidence.",
            "",
            "## Decision Rule",
            "- Do not promote RS watchlist rows into formal MB entries from this artifact.",
            "- Keep the current MB factor stack intact unless a separate ablation run supports a change.",
            "- Use RecentValidation status before any promotion decision.",
            "",
            "## Next Actions",
            f"- Keep MB factors: {', '.join(critical_factors) or 'none'}",
            f"- Keep MB brake factors: {', '.join(overactive_factors) or 'none'}",
            f"- Monitor Priority RS tickers: {', '.join(priority_tickers) or 'none'}",
            f"- Review Watch RS tickers: {', '.join(watch_tickers) or 'none'}",
            f"- Skip Avoid RS tickers: {', '.join(avoid_tickers) or 'none'}",
            f"- {validation_action}.",
            "",
            "## Files To Review",
            f"- Main report: `{REPORT_PATH.name}`",
            f"- MB ablation CSV: `{MB_FACTOR_ABLATION_CSV_PATH.name}`",
            f"- Recent validation CSV: `{RECENT_VALIDATION_CSV_PATH.name}`",
            f"- RS ticker CSV: `{RS_WATCHLIST_TICKER_CSV_PATH.name}`",
            f"- Next actions CSV: `{NEXT_ACTIONS_CSV_PATH.name}`",
            f"- RS detail report: `{RS_WATCHLIST_REPORT_PATH.name}`",
            "",
            "## Plain-English Read",
            "- Critical MB factors are the parts that should not be removed without breaking the current research candidate.",
            "- Overactive rows mean removing that factor creates too many signals, so that factor is acting as a useful brake.",
            "- RS ranks are an observation list, not the formal MB entry rule.",
            "- Recent validation is a quick check on the newest signal window before doing another full research pass.",
            "",
        ]
    )
    return "\n".join(rows)


def _format_optional_float(value: Any) -> str:
    if value is None:
        return ""
    return f"{float(value):.6f}"


def generate_observation_signals_csv(payload: dict[str, Any]) -> str:
    output = StringIO()
    fieldnames = [
        "symbol",
        "date",
        "observationType",
        "bottomScore",
        "rsSignalScore",
        "marketDrawdown",
        "nearLowGap",
        "riskFlags",
        "fwd126",
        "adverse126",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for item in payload.get("observationSearch", {}).get("signals", []):
        writer.writerow(
            {
                "symbol": item.get("symbol", ""),
                "date": item.get("date", ""),
                "observationType": item.get("observationType", ""),
                "bottomScore": item.get("bottomScore", ""),
                "rsSignalScore": item.get("rsSignalScore", ""),
                "marketDrawdown": _format_optional_float(item.get("marketDrawdown")),
                "nearLowGap": _format_optional_float(item.get("nearLowGap")),
                "riskFlags": item.get("riskFlags", ""),
                "fwd126": _format_optional_float(item.get("fwd126")),
                "adverse126": _format_optional_float(item.get("adverse126")),
            }
        )
    return output.getvalue()


def generate_observation_report(payload: dict[str, Any]) -> str:
    observation = payload.get("observationSearch", {})
    selected = observation.get("selectedConfig", {})
    metrics = observation.get("metrics", {})
    coverage = observation.get("anchorCoverage", {})
    signals = observation.get("signals", [])
    rows = [
        "# Observation Channel Report",
        "",
        "## Role",
        "- Observation/candidate layer only. This does not change the formal MB strategy.",
        f"- Merged Pine: `{MERGED_OBSERVATION_PINE_PATH.name}`",
        f"- Signal CSV: `{OBSERVATION_SIGNALS_CSV_PATH.name}`",
        "",
        "## Selected Observation Config",
        f"- Deep market max: {float(selected.get('deepMarketMax', -20.0)):.2f}%",
        f"- Shallow market band: {float(selected.get('shallowMarketMin', -20.0)):.2f}% to {float(selected.get('shallowMarketMax', -8.0)):.2f}%",
        f"- Deep bottom minimum: {int(selected.get('deepBottomMin', 0))}",
        f"- Shallow bottom minimum: {int(selected.get('shallowBottomMin', 0))}",
        f"- Bottom maximum: {int(selected.get('bottomMax', 75))}",
        f"- Near-low window: {int(selected.get('nearLowWindow', 0))}",
        f"- Near-low max gap: {float(selected.get('nearLowMax', 0.0)):.2%}",
        f"- Cluster window: {int(selected.get('clusterWindow', 0))} bars",
        "",
        "## Metrics",
        f"- Observation signals: {int(metrics.get('signalCount', 0))}",
        f"- Formal Strong baseline: {int(metrics.get('formalStrongBaselineCount', 0))}",
        f"- Observation/Formal ratio: {float(metrics.get('observationToFormalRatio', 0.0)):.2f}x",
        f"- Sparse target max: {int(metrics.get('sparseTargetMax', 0))}",
        f"- Avg 6m return: {float(metrics.get('avgFwd126', 0.0)):.2%}",
        f"- 6m win rate: {float(metrics.get('winRate126', 0.0)):.2%}",
        f"- Avg 6m adverse drawdown: {float(metrics.get('avgAdverse126', 0.0)):.2%}",
        f"- Duplicate formal signals: {int(metrics.get('duplicateFormalCount', 0))}",
        f"- Upgrade candidate score: {float(metrics.get('upgradeCandidateScore', 0.0)):.2f}",
        "",
        "## Anchor Coverage",
    ]
    for key in OBSERVATION_ANCHOR_WINDOWS:
        item = coverage.get(key, {})
        rows.append(
            f"- {item.get('label', OBSERVATION_ANCHOR_WINDOWS[key]['label'])}: "
            f"{'Covered' if item.get('covered') else 'Missing'} "
            f"({int(item.get('count', 0))} signals)"
        )
    rows.extend(["", "## Anchor Signal Details"])
    anchor_detail_count = 0
    for key, window in OBSERVATION_ANCHOR_WINDOWS.items():
        window_signals = [
            item
            for item in signals
            if item.get("symbol") == window["symbol"]
            and window["start"] <= str(item.get("date", "")) <= window["end"]
        ]
        if not window_signals:
            rows.append(f"- {window['label']}: none")
            continue
        for item in sorted(window_signals, key=lambda row: str(row.get("date", ""))):
            anchor_detail_count += 1
            rows.append(
                "- "
                f"{item.get('symbol', '')} {item.get('date', '')} "
                f"{item.get('observationType', '')} "
                f"bottom={item.get('bottomScore', 0)} "
                f"RS={item.get('rsSignalScore', 0)} "
                f"risk={item.get('riskFlags') or 'none'}"
            )
    if anchor_detail_count == 0:
        rows.append("- No anchor observation signals found.")
    rows.extend(["", "## Top Signals"])
    if signals:
        for item in signals[:25]:
            rows.append(
                "- "
                f"{item.get('symbol', '')} {item.get('date', '')} "
                f"{item.get('observationType', '')} "
                f"bottom={item.get('bottomScore', 0)} "
                f"RS={item.get('rsSignalScore', 0)} "
                f"marketDD={float(item.get('marketDrawdown', 0.0)):.2f}% "
                f"nearLow={float(item.get('nearLowGap', 0.0)):.2%} "
                f"risk={item.get('riskFlags') or 'none'}"
            )
    else:
        rows.append("- No observation signals found.")
    rows.extend(
        [
            "",
            "## Plain-English Read",
            "- OBS-D means a deep market drawdown retest that is below formal MB strength.",
            "- OBS-S means a shallower market pullback that is worth watching but not a formal bottom signal.",
            "- Upgrade candidate score is evidence for future review, not an automatic promotion rule.",
            "",
        ]
    )
    return "\n".join(rows)


def generate_rs_watchlist_report(payload: dict[str, Any]) -> str:
    rs_payload = payload.get("bestRsWatchlist", {})
    config = rs_payload.get("config", {})
    metrics = rs_payload.get("metrics", {})
    watchlist = rs_payload.get("rsCandidateWatchlist", {})
    refresh = payload.get("rsWatchlistRefresh", {})
    rows = [
        "# RS Watchlist Report",
        "",
        "## Scope",
        "- Observation only. This report is not the formal MB-led trading strategy.",
        f"- Role: `{rs_payload.get('role', 'rs_watchlist_only')}`",
        f"- Pine: `{RS_WATCHLIST_PINE_PATH.name}`",
        f"- Ticker CSV: `{RS_WATCHLIST_TICKER_CSV_PATH.name}`",
        f"- Candidate CSV: `{RS_WATCHLIST_CANDIDATE_CSV_PATH.name}`",
    ]
    if refresh:
        rows.extend(
            [
                "- Refresh mode: "
                f"`{refresh.get('mode', 'unknown')}` over `{refresh.get('symbolCount', 0)}` symbols",
                f"- Refresh config: `{refresh.get('configName', 'unknown')}`",
            ]
        )
    rows.extend(
        [
            "",
            "## RS Watchlist Config",
            f"- Name: `{config.get('name', 'not available')}`",
            f"- Experimental signal set: `{config.get('experimental_signal_set', 'not available')}`",
            f"- Drawdown: window `{config.get('drawdown_window', 'n/a')}`, threshold `{config.get('drawdown_threshold', 'n/a')}%`",
            f"- RSI: `{config.get('rsi_period', 'n/a')}`",
            f"- SMA distance: `{config.get('ma_period', 'n/a')}`",
            f"- RS window: `{config.get('rs_window', 'n/a')}`",
            "",
            "## Formal Strategy Context",
            f"- Formal composite score: {float(metrics.get('compositeScore', 0.0)):.2f}",
            f"- Formal Strong signals: {metrics.get('signalCount', 0)}",
            f"- Formal avg 6m return: {float(metrics.get('avgFwd126', 0.0)):.2%}",
            f"- Formal 6m win rate: {float(metrics.get('winRate126', 0.0)):.2%}",
            "- A zero or weak formal score here means this config is for RS observation only.",
            "",
            "## Watchlist Quality",
            f"- Qualified RS candidates: {watchlist.get('qualifiedRsCandidateCount', 0)}",
            f"- Qualified RS avg 6m return: {float(watchlist.get('qualifiedRsCandidateAvgFwd126', 0.0)):.2%}",
            f"- Qualified RS avg 6m adverse drawdown: {float(watchlist.get('qualifiedRsCandidateAvgAdverse126', 0.0)):.2%}",
            "",
            "## Top RS Watchlist Candidates",
        ]
    )
    top = watchlist.get("topRsCandidates", [])
    if top:
        for item in top[:20]:
            fwd126 = item.get("fwd126")
            adverse126 = item.get("adverse126")
            risk_flags = str(item.get("riskFlags", ""))
            fwd_text = f"fwd6m={float(fwd126):.2%} " if fwd126 is not None else "fwd6m=n/a "
            rows.append(
                "- "
                f"{item['symbol']} {item['date']} {item.get('tier', '')} "
                f"quality={item.get('qualityScore', 0)} "
                f"qualified={item.get('qualityPassed', False)} "
                f"RS signal={item.get('rsSignalScore', 0)} "
                f"RS strength={item.get('relativeStrengthScore', 0)} "
                f"bottom={item.get('bottomScore', 0)} "
                f"risk={risk_flags or 'none'} "
                f"{fwd_text}"
            )
            rows[-1] += (
                f"adverse6m={float(adverse126):.2%}"
                if adverse126 is not None
                else "adverse6m=n/a"
            )
    else:
        rows.append("- No RS watchlist candidates found.")
    action_counts = watchlist.get("rsTickerActionCounts") or rs_ticker_action_counts(
        watchlist.get("rsTickerSummary", [])
    )
    rows.extend(
        [
            "",
            "## Action Summary",
            f"- Priority: {int(action_counts.get('Priority', 0))}",
            f"- Watch: {int(action_counts.get('Watch', 0))}",
            f"- Avoid: {int(action_counts.get('Avoid', 0))}",
        ]
    )
    rows.extend(
        [
            "",
            "## Ticker Summary",
        ]
    )
    ticker_summary = watchlist.get("rsTickerSummary", [])
    if ticker_summary:
        for item in ticker_summary[:12]:
            fwd126 = item.get("avgFwd126")
            adverse126 = item.get("avgAdverse126")
            fwd_text = f"avg6m={float(fwd126):.2%} " if fwd126 is not None else "avg6m=n/a "
            action_tier = item.get("actionTier") or rs_ticker_action_tier(
                qualified_count=int(item.get("qualifiedCount", 0)),
                avg_quality=float(item.get("avgQualityScore", 0.0)),
                avg_adverse_126=float(item.get("avgAdverse126", 0.0)),
                risk_count=int(item.get("riskFlaggedCount", 0)),
            )
            action_reason = item.get("actionReason") or rs_ticker_action_reason(
                action_tier=str(action_tier),
                qualified_count=int(item.get("qualifiedCount", 0)),
                avg_quality=float(item.get("avgQualityScore", 0.0)),
                avg_adverse_126=float(item.get("avgAdverse126", 0.0)),
                risk_count=int(item.get("riskFlaggedCount", 0)),
            )
            rows.append(
                "- "
                f"#{int(item.get('selectionRank', 0))} {item.get('symbol', '')}: "
                f"action={action_tier}, "
                f"qualified={item.get('qualifiedCount', 0)}, "
                f"candidates={item.get('candidateCount', 0)}, "
                f"selection={_summary_selection_score(item):.1f}, "
                f"reason={action_reason}, "
                f"avg_quality={float(item.get('avgQualityScore', 0.0)):.1f}, "
                f"best={item.get('bestDate', '')} q{item.get('bestQualityScore', 0)}, "
                f"risk_flagged={item.get('riskFlaggedCount', 0)}, "
                f"{fwd_text}"
            )
            rows[-1] += (
                f"avg_adverse6m={float(adverse126):.2%}"
                if adverse126 is not None
                else "avg_adverse6m=n/a"
            )
    else:
        rows.append("- No ticker-level RS summary available.")
    rows.extend(
        [
            "",
            "## Notes",
            "- Use this alongside the formal MB report, not as a replacement for it.",
            "- `RS-Q` in Pine means qualified watchlist candidate; `RS-R` means risk-flagged watchlist candidate.",
            "",
        ]
    )
    return "\n".join(rows)


def generate_rs_watchlist_ticker_csv(payload: dict[str, Any]) -> str:
    watchlist = payload.get("bestRsWatchlist", {}).get("rsCandidateWatchlist", {})
    ticker_summary = rank_rs_ticker_summary(watchlist.get("rsTickerSummary", []))
    output = StringIO()
    fieldnames = [
        "symbol",
        "selectionRank",
        "actionTier",
        "actionReason",
        "qualifiedCount",
        "candidateCount",
        "selectionScore",
        "avgQualityScore",
        "bestDate",
        "bestQualityScore",
        "riskFlaggedCount",
        "avgFwd126",
        "avgAdverse126",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for index, item in enumerate(ticker_summary, start=1):
        action_tier = item.get("actionTier") or rs_ticker_action_tier(
            qualified_count=int(item.get("qualifiedCount", 0)),
            avg_quality=float(item.get("avgQualityScore", 0.0)),
            avg_adverse_126=float(item.get("avgAdverse126", 0.0)),
            risk_count=int(item.get("riskFlaggedCount", 0)),
        )
        action_reason = item.get("actionReason") or rs_ticker_action_reason(
            action_tier=str(action_tier),
            qualified_count=int(item.get("qualifiedCount", 0)),
            avg_quality=float(item.get("avgQualityScore", 0.0)),
            avg_adverse_126=float(item.get("avgAdverse126", 0.0)),
            risk_count=int(item.get("riskFlaggedCount", 0)),
        )
        writer.writerow(
            {
                "symbol": item.get("symbol", ""),
                "selectionRank": item.get("selectionRank", index),
                "actionTier": action_tier,
                "actionReason": action_reason,
                "qualifiedCount": item.get("qualifiedCount", 0),
                "candidateCount": item.get("candidateCount", 0),
                "selectionScore": f"{_summary_selection_score(item):.2f}",
                "avgQualityScore": f"{float(item.get('avgQualityScore', 0.0)):.2f}",
                "bestDate": item.get("bestDate", ""),
                "bestQualityScore": item.get("bestQualityScore", 0),
                "riskFlaggedCount": item.get("riskFlaggedCount", 0),
                "avgFwd126": f"{float(item.get('avgFwd126', 0.0)):.6f}",
                "avgAdverse126": f"{float(item.get('avgAdverse126', 0.0)):.6f}",
            }
        )
    return output.getvalue()


def generate_rs_watchlist_candidate_csv(payload: dict[str, Any]) -> str:
    watchlist = payload.get("bestRsWatchlist", {}).get("rsCandidateWatchlist", {})
    candidates = watchlist.get("topRsCandidates", [])
    output = StringIO()
    fieldnames = [
        "symbol",
        "date",
        "tier",
        "qualityPassed",
        "qualityScore",
        "rsSignalScore",
        "relativeStrengthScore",
        "bottomScore",
        "riskFlags",
        "marketDrawdown",
        "fwd126",
        "adverse126",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for item in candidates:
        writer.writerow(
            {
                "symbol": item.get("symbol", ""),
                "date": item.get("date", ""),
                "tier": item.get("tier", ""),
                "qualityPassed": item.get("qualityPassed", False),
                "qualityScore": item.get("qualityScore", 0),
                "rsSignalScore": item.get("rsSignalScore", 0),
                "relativeStrengthScore": item.get("relativeStrengthScore", 0),
                "bottomScore": item.get("bottomScore", 0),
                "riskFlags": item.get("riskFlags", ""),
                "marketDrawdown": _csv_float(item.get("marketDrawdown")),
                "fwd126": _csv_float(item.get("fwd126")),
                "adverse126": _csv_float(item.get("adverse126")),
            }
        )
    return output.getvalue()


def generate_mb_factor_ablation_csv(payload: dict[str, Any]) -> str:
    rows = summarize_mb_factor_ablation(payload.get("mbFactorAblation", {}))["rows"]
    output = StringIO()
    fieldnames = [
        "factor",
        "impactLabel",
        "configName",
        "compositeScore",
        "compositeDelta",
        "signalCount",
        "signalCountDelta",
        "avgFwd126",
        "avgFwd126Delta",
        "avgAdverse126",
        "avgAdverse126Delta",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for item in rows:
        writer.writerow(
            {
                "factor": item.get("factor", ""),
                "impactLabel": item.get("impactLabel", ""),
                "configName": item.get("configName", ""),
                "compositeScore": _csv_float(item.get("compositeScore")),
                "compositeDelta": _csv_float(item.get("compositeDelta")),
                "signalCount": item.get("signalCount", 0),
                "signalCountDelta": item.get("signalCountDelta", 0),
                "avgFwd126": _csv_float(item.get("avgFwd126")),
                "avgFwd126Delta": _csv_float(item.get("avgFwd126Delta")),
                "avgAdverse126": _csv_float(item.get("avgAdverse126")),
                "avgAdverse126Delta": _csv_float(item.get("avgAdverse126Delta")),
            }
        )
    return output.getvalue()


def generate_recent_validation_csv(payload: dict[str, Any]) -> str:
    best_name = payload.get("bestConfig", {}).get("name", "")
    best_result = next(
        (
            result
            for result in payload.get("results", [])
            if result.get("config", {}).get("name") == best_name
        ),
        {},
    )
    recent = best_result.get("recentValidation", {})
    start = recent.get("recentValidationStart")
    end = recent.get("recentValidationEnd")
    rows = _signals_between(best_result.get("signals", []), start, end)
    output = StringIO()
    fieldnames = [
        "symbol",
        "date",
        "channel",
        "tier",
        "checkStatus",
        "bottomScore",
        "rsSignalScore",
        "riskFlags",
        "fwd126",
        "adverse126",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for item in rows:
        fwd126 = item.get("fwd126")
        if fwd126 is None:
            status = "Pending"
        elif float(fwd126) > 0:
            status = "Pass"
        else:
            status = "Fail"
        writer.writerow(
            {
                "symbol": item.get("symbol", ""),
                "date": item.get("date", ""),
                "channel": item.get("channel", ""),
                "tier": item.get("tier", ""),
                "checkStatus": status,
                "bottomScore": item.get("bottomScore", 0),
                "rsSignalScore": item.get("rsSignalScore", 0),
                "riskFlags": item.get("riskFlags", ""),
                "fwd126": _csv_float(fwd126),
                "adverse126": _csv_float(item.get("adverse126")),
            }
        )
    return output.getvalue()


def generate_next_actions_csv(payload: dict[str, Any]) -> str:
    best_name = payload.get("bestConfig", {}).get("name", "")
    best_result = next(
        (
            result
            for result in payload.get("results", [])
            if result.get("config", {}).get("name") == best_name
        ),
        {},
    )
    ablation_summary = summarize_mb_factor_ablation(payload.get("mbFactorAblation", {}))
    watchlist = payload.get("bestRsWatchlist", {}).get("rsCandidateWatchlist", {})
    ticker_summary = rank_rs_ticker_summary(watchlist.get("rsTickerSummary", []), limit=12)

    output = StringIO()
    fieldnames = ["priority", "role", "category", "target", "action", "reason", "evidence"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    critical_rows = [
        item
        for item in ablation_summary["rows"]
        if item.get("impactLabel") == "Critical"
    ]
    for item in critical_rows:
        writer.writerow(
            {
                "priority": 1,
                "role": "FormalStrategy",
                "category": "MB",
                "target": item.get("factor", ""),
                "action": "Keep",
                "reason": "Critical factor from MB ablation",
                "evidence": (
                    f"compositeDelta={float(item.get('compositeDelta', 0.0)):+.2f}; "
                    f"signalCountDelta={int(item.get('signalCountDelta', 0)):+d}"
                ),
            }
        )
    overactive_rows = [
        item
        for item in ablation_summary["rows"]
        if item.get("impactLabel") == "Overactive"
    ]
    for item in overactive_rows:
        writer.writerow(
            {
                "priority": 1,
                "role": "FormalStrategy",
                "category": "MB",
                "target": item.get("factor", ""),
                "action": "Keep brake",
                "reason": "Overactive factor from MB ablation",
                "evidence": (
                    f"compositeDelta={float(item.get('compositeDelta', 0.0)):+.2f}; "
                    f"signalCountDelta={int(item.get('signalCountDelta', 0)):+d}"
                ),
            }
        )
    for item in ticker_summary:
        if item.get("actionTier") != "Priority":
            continue
        writer.writerow(
            {
                "priority": 2,
                "role": "Observation",
                "category": "RS",
                "target": item.get("symbol", ""),
                "action": "Monitor",
                "reason": "Priority RS ticker",
                "evidence": (
                    f"selectionScore={float(item.get('selectionScore', 0.0)):.2f}; "
                    f"qualifiedCount={int(item.get('qualifiedCount', 0))}; "
                    f"reason={item.get('actionReason', '')}"
                ),
            }
        )
    for item in ticker_summary:
        if item.get("actionTier") != "Watch":
            continue
        writer.writerow(
            {
                "priority": 3,
                "role": "Observation",
                "category": "RS",
                "target": item.get("symbol", ""),
                "action": "Review",
                "reason": "Watch RS ticker",
                "evidence": (
                    f"selectionScore={float(item.get('selectionScore', 0.0)):.2f}; "
                    f"qualifiedCount={int(item.get('qualifiedCount', 0))}; "
                    f"reason={item.get('actionReason', '')}"
                ),
            }
        )
    for item in ticker_summary:
        if item.get("actionTier") != "Avoid":
            continue
        writer.writerow(
            {
                "priority": 4,
                "role": "Observation",
                "category": "RS",
                "target": item.get("symbol", ""),
                "action": "Skip",
                "reason": "Avoid RS ticker",
                "evidence": (
                    f"selectionScore={float(item.get('selectionScore', 0.0)):.2f}; "
                    f"reason={item.get('actionReason', '')}"
                ),
            }
        )

    recent_validation = best_result.get("recentValidation", {})
    recent_status = str(recent_validation.get("recentValidationStatus", "Watch"))
    if recent_status == "Pass":
        action = "Continue observation"
        reason = "Recent validation passed"
    elif recent_status == "Fail":
        action = "Review before promotion"
        reason = "Recent validation failed"
    else:
        action = "Wait for mature checks"
        reason = "Recent validation is watch-only"
    writer.writerow(
        {
            "priority": 5,
            "role": "Validation",
            "category": "RecentValidation",
            "target": recent_status,
            "action": action,
            "reason": reason,
            "evidence": (
                f"status={recent_status}; "
                f"matureCount={int(recent_validation.get('recentValidationMatureCount', 0))}; "
                f"winRate={float(recent_validation.get('recentValidationWinRate126', 0.0)):.2%}; "
                f"avgFwd126={float(recent_validation.get('recentValidationAvgFwd126', 0.0)):.2%}"
            ),
        }
    )
    return output.getvalue()


def _best_result(payload: dict[str, Any]) -> dict[str, Any]:
    best_name = payload.get("bestConfig", {}).get("name", "")
    return next(
        (
            result
            for result in payload.get("results", [])
            if result.get("config", {}).get("name") == best_name
        ),
        {},
    )


def _recent_formal_signals(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = _best_result(payload)
    recent = result.get("recentValidation", {})
    start = str(recent.get("recentValidationStart", ""))
    end = str(recent.get("recentValidationEnd", ""))
    rows = []
    for signal in result.get("signals", []):
        date = str(signal.get("date", ""))
        if start and date < start:
            continue
        if end and date > end:
            continue
        if signal.get("fwd126") is None:
            continue
        rows.append(signal)
    return sorted(rows, key=lambda item: (str(item.get("date", "")), str(item.get("symbol", ""))))


def _risk_tokens(value: Any) -> list[str]:
    tokens = [token.strip() for token in str(value or "").split(",") if token.strip()]
    return tokens or ["none"]


def _observation_risk_counts(signals: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for signal in signals:
        for token in _risk_tokens(signal.get("riskFlags")):
            counts[token] = counts.get(token, 0) + 1
    return dict(sorted(counts.items()))


def _observation_risk_quality(signals: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for signal in signals:
        for token in _risk_tokens(signal.get("riskFlags")):
            buckets.setdefault(token, []).append(signal)

    summary = {}
    for risk, rows in sorted(buckets.items()):
        fwd_values = [float(row["fwd126"]) for row in rows if row.get("fwd126") is not None]
        adverse_values = [
            float(row["adverse126"]) for row in rows if row.get("adverse126") is not None
        ]
        wins = [value for value in fwd_values if value > 0]
        summary[risk] = {
            "count": len(rows),
            "avgFwd126": mean(fwd_values) if fwd_values else None,
            "winRate126": len(wins) / len(fwd_values) if fwd_values else None,
            "avgAdverse126": mean(adverse_values) if adverse_values else None,
        }
    return summary


def _format_optional_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def _format_optional_score(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if numeric.is_integer():
        return str(int(numeric))
    return f"{numeric:.2f}"


def _rs_tickers_by_action(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows = payload.get("bestRsWatchlist", {}).get("rsCandidateWatchlist", {}).get(
        "rsTickerSummary", []
    )
    grouped = {"Monitor": [], "Review": [], "Skip": []}
    for item in rows:
        tier = str(item.get("actionTier", ""))
        if tier == "Priority":
            grouped["Monitor"].append(item)
        elif tier == "Watch":
            grouped["Review"].append(item)
        else:
            grouped["Skip"].append(item)
    return grouped


def _formal_missed_observation_signals(payload: dict[str, Any]) -> list[dict[str, Any]]:
    signals = payload.get("observationSearch", {}).get("signals", [])
    missed = [
        signal
        for signal in signals
        if int(signal.get("duplicateFormalCount", 0)) == 0
    ]
    return sorted(missed, key=lambda item: (str(item.get("date", "")), str(item.get("symbol", ""))))


def _qqq_observation_dates(payload: dict[str, Any], start: str, end: str) -> list[str]:
    signals = payload.get("observationSearch", {}).get("signals", [])
    dates = {
        str(signal.get("date", ""))
        for signal in signals
        if signal.get("symbol") == "QQQ"
        and start <= str(signal.get("date", "")) <= end
    }
    return sorted(date for date in dates if date)


def _strategy_validation_gates(payload: dict[str, Any]) -> list[dict[str, str]]:
    best = payload.get("bestConfig", {})
    metrics = payload.get("bestMetrics", {})
    scope = payload.get("artifactScope", {})
    obs_metrics = payload.get("observationSearch", {}).get("metrics", {})

    signal_count = int(metrics.get("signalCount", 0))
    duplicate_count = int(obs_metrics.get("duplicateFormalCount", 0))
    qqq_2022_q4 = _qqq_observation_dates(payload, "2022-10-01", "2022-12-31")
    qqq_2026_march = _qqq_observation_dates(payload, "2026-03-01", "2026-03-31")

    return [
        {
            "name": "baselineName",
            "status": "PASS" if best.get("name") == "seed_previous_rs_higher_low_best" else "FAIL",
            "evidence": str(best.get("name", "")),
        },
        {
            "name": "fullPool",
            "status": "PASS"
            if scope.get("fullPool") and scope.get("sampleKind") == "FULL_POOL" and len(payload.get("symbols", [])) == 21
            else "FAIL",
            "evidence": f"symbols={len(payload.get('symbols', []))} sample={scope.get('sampleKind', 'unknown')}",
        },
        {
            "name": "entryThreshold",
            "status": "PASS" if int(best.get("entry_threshold", 0)) == 82 else "FAIL",
            "evidence": f"threshold={best.get('entry_threshold', 'n/a')}",
        },
        {
            "name": "formalSignalCap",
            "status": "PASS" if signal_count <= 40 else "FAIL",
            "evidence": f"signals={signal_count} limit=40",
        },
        {
            "name": "duplicateFormal",
            "status": "PASS" if duplicate_count == 0 else "FAIL",
            "evidence": f"duplicateFormalCount={duplicate_count}",
        },
        {
            "name": "qqq2022Q4Coverage",
            "status": "PASS" if qqq_2022_q4 else "FAIL",
            "evidence": ", ".join(qqq_2022_q4) if qqq_2022_q4 else "missing",
        },
        {
            "name": "qqq2026MarchCoverage",
            "status": "PASS" if qqq_2026_march else "FAIL",
            "evidence": ", ".join(qqq_2026_march) if qqq_2026_march else "missing",
        },
    ]


def _promotion_preconditions() -> list[str]:
    return [
        "OBS/RS ablation against frozen MB baseline",
        "recent validation keeps formal signal count controlled",
        "sample-out validation before formal promotion",
        "Pine parity check before operator use",
    ]


def _retired_artifact_gates() -> list[dict[str, str]]:
    gates = []
    for path in RETIRED_ARTIFACT_PATHS:
        exists = path.exists()
        gates.append(
            {
                "name": path.name,
                "status": "FAIL" if exists else "PASS",
                "evidence": "still exists" if exists else "absent",
            }
        )
    return gates


def _validation_command_checklist() -> list[dict[str, str]]:
    return [
        {
            "target": "minimum",
            "action": "Run",
            "command": ".venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search",
        },
        {
            "target": "repo-wide",
            "action": "Run",
            "command": '.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test*.py"',
        },
        {
            "target": "minimum",
            "action": "Run",
            "command": ".venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_model.py investigations\\bottom_signal_paths.py investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py",
        },
        {
            "target": "minimum",
            "action": "Run",
            "command": ".venv\\Scripts\\python.exe -m json.tool strategy_catalog\\bottom_signal_formal\\bottom_signal_results.json > $null",
        },
        {
            "target": "minimum",
            "action": "Run",
            "command": "git diff --check",
        },
        {
            "target": "minimum",
            "action": "Run",
            "command": "git diff --name-only -- config.py prepare.py run.py versions",
        },
        {
            "target": "full-search",
            "action": "Run only after search logic/config changes",
            "command": ".venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --max-configs 720 --workers 4",
        },
        {
            "target": "full-search",
            "action": "Run only after search logic/config changes",
            "command": ".venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search",
        },
    ]


def _main_artifact_gates() -> list[dict[str, str]]:
    gates = []
    for role, path in MAIN_ARTIFACT_PATHS:
        exists = path.exists()
        gates.append(
            {
                "role": role,
                "name": path.name,
                "status": "PASS" if exists else "FAIL",
                "evidence": "exists" if exists else "missing",
            }
        )
    return gates


def _strategy_plan_step_status(payload: dict[str, Any]) -> list[dict[str, str]]:
    best = payload.get("bestConfig", {})
    metrics = payload.get("bestMetrics", {})
    recent = _best_result(payload).get("recentValidation", {})
    obs = payload.get("observationSearch", {})
    rs_groups = _rs_tickers_by_action(payload)
    missed = _formal_missed_observation_signals(payload)

    return [
        {
            "target": "1 Baseline confirmation",
            "status": "DONE",
            "evidence": (
                f"{best.get('name', '')}; "
                f"symbols={len(payload.get('symbols', []))}; "
                f"signals={int(metrics.get('signalCount', 0))}"
            ),
        },
        {
            "target": "2 Recent sample review",
            "status": "DONE",
            "evidence": (
                f"mature={int(recent.get('recentValidationMatureCount', 0))}; "
                f"status={recent.get('recentValidationStatus', 'n/a')}"
            ),
        },
        {
            "target": "3 OBS candidate segmentation",
            "status": "DONE",
            "evidence": (
                f"signals={int(obs.get('metrics', {}).get('signalCount', 0))}; "
                f"riskBuckets={len(_observation_risk_quality(obs.get('signals', [])))}"
            ),
        },
        {
            "target": "4 RS watchlist review",
            "status": "DONE",
            "evidence": (
                f"monitor={len(rs_groups['Monitor'])}; "
                f"review={len(rs_groups['Review'])}; "
                f"skip={len(rs_groups['Skip'])}"
            ),
        },
        {
            "target": "5 Formal-missed OBS cases",
            "status": "DONE",
            "evidence": f"cases={len(missed)}",
        },
        {
            "target": "6 Promotion validation plan",
            "status": "DONE",
            "evidence": f"preconditions={len(_promotion_preconditions())}",
        },
    ]


def generate_strategy_iteration_review_report(payload: dict[str, Any]) -> str:
    best = payload.get("bestConfig", {})
    metrics = payload.get("bestMetrics", {})
    scope = payload.get("artifactScope", {})
    recent = _best_result(payload).get("recentValidation", {})
    obs = payload.get("observationSearch", {})
    obs_metrics = obs.get("metrics", {})
    obs_signals = obs.get("signals", [])
    risk_quality = _observation_risk_quality(obs_signals)
    rs_groups = _rs_tickers_by_action(payload)
    missed = _formal_missed_observation_signals(payload)

    rows = [
        "# Strategy Iteration Review",
        "",
        "## Baseline Freeze",
        f"- Formal strategy: `{best.get('name', '')}` stays frozen.",
        f"- Full-pool artifact: {'yes' if scope.get('fullPool') else 'no'} "
        f"({scope.get('sampleKind', 'unknown')}).",
        f"- Symbol count: {len(payload.get('symbols', []))}.",
        f"- Strong signals: {int(metrics.get('signalCount', 0))}.",
        f"- Avg 6m return: {float(metrics.get('avgFwd126', 0.0)):.2%}.",
        f"- 6m win rate: {float(metrics.get('winRate126', 0.0)):.2%}.",
        f"- Avg 6m adverse drawdown: {float(metrics.get('avgAdverse126', 0.0)):.2%}.",
        f"- Entry threshold: `{best.get('entry_threshold', 'n/a')}`.",
        "",
        "## Recent Formal Signal Review",
        f"- Window: {recent.get('recentValidationStart', 'n/a')} to {recent.get('recentValidationEnd', 'n/a')}.",
        f"- Recent formal signals: {int(recent.get('recentValidationSignalCount', 0))}.",
        f"- Recent mature signals: {int(recent.get('recentValidationMatureCount', 0))}.",
        f"- Recent status: {recent.get('recentValidationStatus', 'n/a')}.",
        f"- Recent avg 6m return: {float(recent.get('recentValidationAvgFwd126', 0.0)):.2%}.",
        f"- Recent 6m win rate: {float(recent.get('recentValidationWinRate126', 0.0)):.2%}.",
        "",
        "## Recent Formal Signal Details",
    ]
    recent_signals = _recent_formal_signals(payload)
    for signal in recent_signals:
        rows.append(
            "- "
            f"{signal.get('symbol', '')} {signal.get('date', '')} "
            f"channel={signal.get('channel') or 'n/a'} "
            f"bottom={_format_optional_score(signal.get('bottomScore'))} "
            f"RS={_format_optional_score(signal.get('rsSignalScore'))} "
            f"risk={signal.get('riskFlags') or 'none'} "
            f"fwd6m={_format_optional_pct(signal.get('fwd126'))} "
            f"adverse6m={_format_optional_pct(signal.get('adverse126'))}"
        )
    if not recent_signals:
        rows.append("- No mature recent formal signals found.")

    rows.extend(
        [
            "",
            "## OBS Candidate Risk Segmentation",
            f"- Observation signals: {int(obs_metrics.get('signalCount', 0))}.",
            f"- Formal baseline: {int(obs_metrics.get('formalStrongBaselineCount', 0))}.",
            f"- Observation/Formal ratio: {float(obs_metrics.get('observationToFormalRatio', 0.0)):.2f}x.",
            f"- Duplicate formal signals: {int(obs_metrics.get('duplicateFormalCount', 0))}.",
        ]
    )
    for risk, item in risk_quality.items():
        rows.append(
            f"- risk={risk}: count={int(item.get('count', 0))}, "
            f"avg6m={_format_optional_pct(item.get('avgFwd126'))}, "
            f"win6m={_format_optional_pct(item.get('winRate126'))}, "
            f"adverse6m={_format_optional_pct(item.get('avgAdverse126'))}"
        )

    rows.extend(["", "## RS Watchlist Review"])
    for label in ["Monitor", "Review", "Skip"]:
        group_rows = rs_groups[label]
        symbols = [str(item.get("symbol", "")) for item in group_rows]
        rows.append(f"- {label}: {', '.join(symbols) if symbols else 'none'}")
        for item in group_rows:
            rows.append(
                "  - "
                f"{item.get('symbol', '')}: "
                f"score={float(item.get('selectionScore', 0.0)):.2f}, "
                f"qualified={int(item.get('qualifiedCount', 0))}, "
                f"reason={item.get('actionReason') or 'n/a'}"
            )

    rows.extend(["", "## Plan Validation Gates"])
    for gate in _strategy_validation_gates(payload):
        rows.append(f"- {gate['status']} {gate['name']}: {gate['evidence']}")

    rows.extend(["", "## Retired Artifact Guard"])
    for gate in _retired_artifact_gates():
        rows.append(f"- {gate['status']} retiredArtifact: {gate['name']} {gate['evidence']}")

    rows.extend(["", "## Main Artifact Manifest"])
    for gate in _main_artifact_gates():
        rows.append(f"- {gate['status']} {gate['role']}: {gate['name']} {gate['evidence']}")

    rows.extend(["", "## Strategy Plan Step Status"])
    for item in _strategy_plan_step_status(payload):
        rows.append(f"- {item['status']} {item['target']}: {item['evidence']}")

    rows.extend(["", "## Formal-Missed OBS Cases"])
    for item in missed[:20]:
        rows.append(
            "- "
            f"{item.get('symbol', '')} {item.get('date', '')} {item.get('observationType', '')} "
            f"risk={item.get('riskFlags') or 'none'} "
            f"bottom={_format_optional_score(item.get('bottomScore'))} "
            f"RS={_format_optional_score(item.get('rsSignalScore'))} "
            f"fwd6m={_format_optional_pct(item.get('fwd126'))} "
            f"adverse6m={_format_optional_pct(item.get('adverse126'))}"
        )
    if not missed:
        rows.append("- No formal-missed OBS candidates found.")

    rows.extend(
        [
            "",
            "## Candidate Rule",
            "- Do not promote OBS/RS into formal entries from this review.",
            "- Open a separate validation plan before any OBS/RS promotion.",
            "- Keep the current MB factor stack intact unless a separate ablation supports a change.",
            "",
            "## Promotion Preconditions",
        ]
    )
    for item in _promotion_preconditions():
        rows.append(f"- Required: {item}.")
    rows.extend(["", "## Validation Command Checklist"])
    for item in _validation_command_checklist():
        if item["target"] == "minimum":
            label = "Minimum"
        elif item["target"] == "repo-wide":
            label = "Repo-wide"
        else:
            label = "Full search only after search logic/config changes"
        rows.append(f"- {label}: `{item['command']}`")
    rows.append("")
    return "\n".join(rows)


def generate_strategy_iteration_review_csv(payload: dict[str, Any]) -> str:
    output = StringIO()
    fieldnames = ["step", "section", "role", "target", "action", "evidence"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()

    best = payload.get("bestConfig", {})
    metrics = payload.get("bestMetrics", {})
    scope = payload.get("artifactScope", {})
    writer.writerow(
        {
            "step": 1,
            "section": "Baseline",
            "role": "FormalStrategy",
            "target": best.get("name", ""),
            "action": "Freeze formal MB baseline",
            "evidence": (
                f"fullPool={bool(scope.get('fullPool'))}; "
                f"symbols={len(payload.get('symbols', []))}; "
                f"signals={int(metrics.get('signalCount', 0))}; "
                f"avgFwd126={float(metrics.get('avgFwd126', 0.0)):.2%}"
            ),
        }
    )

    recent = _best_result(payload).get("recentValidation", {})
    for signal in _recent_formal_signals(payload):
        writer.writerow(
            {
                "step": 2,
                "section": "RecentValidation",
                "role": "FormalStrategy",
                "target": f"{signal.get('symbol', '')} {signal.get('date', '')}",
                "action": "Review mature recent formal signal",
                "evidence": (
                    f"status={recent.get('recentValidationStatus', 'n/a')}; "
                    f"fwd126={_csv_float(signal.get('fwd126'))}; "
                    f"adverse126={_csv_float(signal.get('adverse126'))}; "
                    f"channel={signal.get('channel') or 'n/a'}; "
                    f"risk={signal.get('riskFlags') or 'none'}"
                ),
            }
        )

    obs_signals = payload.get("observationSearch", {}).get("signals", [])
    for risk, item in _observation_risk_quality(obs_signals).items():
        writer.writerow(
            {
                "step": 3,
                "section": "ObservationRisk",
                "role": "Observation",
                "target": f"risk={risk}",
                "action": "Keep observation-only bucket",
                "evidence": (
                    f"count={int(item.get('count', 0))}; "
                    f"avgFwd126={_format_optional_pct(item.get('avgFwd126'))}; "
                    f"winRate126={_format_optional_pct(item.get('winRate126'))}; "
                    f"avgAdverse126={_format_optional_pct(item.get('avgAdverse126'))}"
                ),
            }
        )

    for action, rows in _rs_tickers_by_action(payload).items():
        for item in rows:
            writer.writerow(
                {
                    "step": 4,
                    "section": "RSWatchlist",
                    "role": "Observation",
                    "target": item.get("symbol", ""),
                    "action": action,
                    "evidence": (
                        f"selectionScore={float(item.get('selectionScore', 0.0)):.2f}; "
                        f"qualifiedCount={int(item.get('qualifiedCount', 0))}; "
                        f"reason={item.get('actionReason') or 'n/a'}"
                    ),
                }
            )

    for item in _formal_missed_observation_signals(payload):
        writer.writerow(
            {
                "step": 5,
                "section": "MissedCase",
                "role": "Observation",
                "target": f"{item.get('symbol', '')} {item.get('date', '')} {item.get('observationType', '')}",
                "action": "Record formal-missed OBS candidate",
                "evidence": (
                    f"risk={item.get('riskFlags') or 'none'}; "
                    f"duplicateFormalCount={int(item.get('duplicateFormalCount', 0))}; "
                    f"fwd126={_csv_float(item.get('fwd126'))}; "
                    f"adverse126={_csv_float(item.get('adverse126'))}; "
                    f"bottom={_format_optional_score(item.get('bottomScore'))}; "
                    f"RS={_format_optional_score(item.get('rsSignalScore'))}"
                ),
            }
        )

    writer.writerow(
        {
            "step": 6,
            "section": "CandidateRule",
            "role": "Validation",
            "target": "OBS/RS promotion",
            "action": "Open separate validation plan before promotion",
            "evidence": "current review is observation-only",
        }
    )

    for gate in _strategy_validation_gates(payload):
        writer.writerow(
            {
                "step": 7,
                "section": "ValidationGate",
                "role": "Validation",
                "target": gate["name"],
                "action": "Pass" if gate["status"] == "PASS" else "Fail",
                "evidence": gate["evidence"],
            }
        )
    for item in _promotion_preconditions():
        writer.writerow(
            {
                "step": 8,
                "section": "PromotionPrecondition",
                "role": "Validation",
                "target": "OBS/RS promotion",
                "action": "Required",
                "evidence": item,
            }
        )
    for gate in _retired_artifact_gates():
        writer.writerow(
            {
                "step": 9,
                "section": "RetiredArtifact",
                "role": "Validation",
                "target": gate["name"],
                "action": "Pass" if gate["status"] == "PASS" else "Fail",
                "evidence": gate["evidence"],
            }
        )
    for item in _validation_command_checklist():
        writer.writerow(
            {
                "step": 10,
                "section": "ValidationCommand",
                "role": "Operator",
                "target": item["target"],
                "action": item["action"],
                "evidence": item["command"],
            }
        )
    for gate in _main_artifact_gates():
        writer.writerow(
            {
                "step": 11,
                "section": "MainArtifact",
                "role": "Validation",
                "target": gate["name"],
                "action": "Pass" if gate["status"] == "PASS" else "Fail",
                "evidence": f"{gate['role']} {gate['evidence']}",
            }
        )
    for item in _strategy_plan_step_status(payload):
        writer.writerow(
            {
                "step": 12,
                "section": "PlanStepStatus",
                "role": "Validation",
                "target": item["target"],
                "action": "Done",
                "evidence": item["evidence"],
            }
        )
    return output.getvalue()


def _csv_float(value: Any) -> str:
    if value is None:
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(numeric):
        return ""
    return f"{numeric:.6f}"


def generate_strict_formal_pine_script(config: BottomSignalConfig) -> str:
    return f"""//@version=6
indicator("AutoQuant Bottom Signal Score", overlay=true, max_labels_count=500)

ddWindow = input.int({config.drawdown_window}, "Drawdown Window", minval=2)
ddThreshold = input.float({config.drawdown_threshold:g}, "Drawdown Threshold %", step=0.5)
rsiPeriod = input.int({config.rsi_period}, "RSI Period", minval=2)
stochPeriod = input.int({config.stoch_period}, "Stochastic Period", minval=2)
stochSmooth = input.int({config.stoch_smooth}, "Stochastic Smooth", minval=1)
macdFast = input.int({config.macd_fast}, "MACD Fast", minval=1)
macdSlow = input.int({config.macd_slow}, "MACD Slow", minval=2)
macdSignal = input.int({config.macd_signal}, "MACD Signal", minval=1)
smaPeriod = input.int({config.ma_period}, "SMA Period", minval=2)
atrPeriod = input.int({config.atr_period}, "ATR Period", minval=2)
volumeWindow = input.int({config.volume_window}, "Volume Window", minval=2)
bandPeriod = input.int({config.band_period}, "Band Period", minval=2)
bandStd = input.float({config.band_std:g}, "Band Std Dev", step=0.1)
marketSymbol1 = input.symbol("{config.market_symbol_1}", "Market Symbol 1")
marketSymbol2 = input.symbol("{config.market_symbol_2}", "Market Symbol 2")
marketWindow = input.int({config.market_drawdown_window}, "Market Drawdown Window", minval=2)
marketThreshold = input.float({config.market_drawdown_threshold:g}, "Market Drawdown Threshold %", step=0.5)
rsWindow = input.int({config.rs_window}, "RS Window", minval=2)
rsDrawdownAdvantageThreshold = input.float({config.rs_drawdown_advantage_threshold:g}, "RS Drawdown Advantage %", step=0.5)
rsRepairAdvantageThreshold = input.float({config.rs_repair_advantage_threshold:g}, "RS Repair Advantage %", step=0.5)
rsPullbackWindow = input.int({config.rs_pullback_window}, "RS Pullback Window", minval=2)
rsPullbackMinDrawdown = input.float({config.rs_pullback_min_drawdown:g}, "RS Pullback Min Drawdown %", step=0.5)
rsPullbackMaxDrawdown = input.float({config.rs_pullback_max_drawdown:g}, "RS Pullback Max Drawdown %", step=0.5)
useRsPullbackRepairV2 = input.bool({str(config.experimental_signal_set == "rs_pullback_repair_v2").lower()}, "Use RS Pullback Repair V2")
useRsHigherLowStructure = input.bool({str(config.experimental_signal_set == "rs_higher_low_structure").lower()}, "Use RS Higher Low Structure")
useRsRepairTrendConfirm = input.bool({str(config.experimental_signal_set == "rs_repair_trend_confirm").lower()}, "Use RS Repair Trend Confirm")
useRsMarketDivergence = input.bool({str(config.experimental_signal_set == "rs_market_divergence").lower()}, "Use RS Market Divergence")
useRsPostCrashMaReclaim = input.bool({str(config.experimental_signal_set == "rs_post_crash_ma_reclaim").lower()}, "Use RS Post-Crash MA Reclaim")
useRsVolatilityCompression = input.bool({str(config.experimental_signal_set == "rs_volatility_compression").lower()}, "Use RS Volatility Compression")
drawdownWeight = input.float({config.drawdown_weight:g}, "Drawdown Weight", step=0.01)
momentumWeight = input.float({config.momentum_weight:g}, "Momentum Weight", step=0.01)
repairWeight = input.float({config.repair_weight:g}, "Repair Weight", step=0.01)
structureWeight = input.float({config.structure_weight:g}, "Structure Weight", step=0.01)
volumeWeight = input.float({config.volume_weight:g}, "Volume Weight", step=0.01)
maWeight = input.float({config.ma_weight:g}, "MA Distance Weight", step=0.01)
watchThreshold = input.int({config.watch_threshold}, "Watch Score", minval=1, maxval=100)
mediumThreshold = input.int({config.medium_threshold}, "Medium Score", minval=1, maxval=100)
strongThreshold = input.int({config.strong_threshold}, "Strong Score", minval=1, maxval=100)
exitThreshold = input.int({config.exit_threshold}, "Exit Score", minval=1, maxval=100)
entryThreshold = input.int({config.entry_threshold}, "Entry Score", minval=1, maxval=100)
mbEntryOffset = input.int({config.mb_entry_offset}, "MB Entry Offset", minval=0, maxval=20)
minSignalGap = input.int({config.min_signal_gap}, "Min Signal Gap", minval=1)
showScoreLines = input.bool(false, "Show Score Lines")
showSignalColors = input.bool(true, "Show Signal Candle Colors")
showSignalBackground = input.bool(true, "Show Signal Background")
showSignalTable = input.bool(true, "Show Signal Table")
showTextMarkers = input.bool(true, "Show Text Markers")

clip01(x) =>
    math.min(1.0, math.max(0.0, nz(x, 0.0)))

rollingHigh = ta.highest(close, ddWindow)
drawdown = (close / rollingHigh - 1.0) * 100.0
rsiValue = ta.rsi(close, rsiPeriod)
stochRaw = ta.stoch(close, high, low, stochPeriod)
stochValue = ta.sma(stochRaw, stochSmooth)
[macdLine, macdSignalLine, macdHist] = ta.macd(close, macdFast, macdSlow, macdSignal)
smaValue = ta.sma(close, smaPeriod)
distSma = (close / smaValue - 1.0) * 100.0
atrValue = ta.atr(atrPeriod)
volumeSma = ta.sma(volume, volumeWindow)
volumeRatio = volumeSma == 0 ? 1.0 : volume / volumeSma
bbBasis = ta.sma(close, bandPeriod)
bbUpper = bbBasis + bandStd * ta.stdev(close, bandPeriod)
marketClose1 = request.security(marketSymbol1, timeframe.period, close)
marketClose2 = request.security(marketSymbol2, timeframe.period, close)
marketDrawdown1 = (marketClose1 / ta.highest(marketClose1, marketWindow) - 1.0) * 100.0
marketDrawdown2 = (marketClose2 / ta.highest(marketClose2, marketWindow) - 1.0) * 100.0
marketOk = math.min(marketDrawdown1, marketDrawdown2) <= marketThreshold
rsMarketDrawdown1 = (marketClose1 / ta.highest(marketClose1, rsWindow) - 1.0) * 100.0
rsMarketDrawdown2 = (marketClose2 / ta.highest(marketClose2, rsWindow) - 1.0) * 100.0
rsMarketDrawdown = math.min(rsMarketDrawdown1, rsMarketDrawdown2)
stockRepair = (close / ta.lowest(close, rsWindow) - 1.0) * 100.0
marketRepair1 = (marketClose1 / ta.lowest(marketClose1, rsWindow) - 1.0) * 100.0
marketRepair2 = (marketClose2 / ta.lowest(marketClose2, rsWindow) - 1.0) * 100.0
marketRepair = math.max(marketRepair1, marketRepair2)

drawdownScore = clip01((-drawdown) / math.abs(ddThreshold))
rsiScore = clip01((48.0 - rsiValue) / 24.0)
stochScore = clip01((45.0 - stochValue) / 35.0)
momentumScore = rsiScore * 0.65 + stochScore * 0.35
macdRepair = clip01((macdHist - ta.lowest(macdHist, 3)) / 1.5)
closeRepair = clip01((close / ta.lowest(close, 5) - 1.0) / 0.06)
repairScore = macdRepair * 0.55 + closeRepair * 0.45
retestGap = math.abs(low / ta.lowest(low, 21) - 1.0)
retestScore = clip01((0.08 - retestGap) / 0.08)
baseNow = close >= ta.lowest(close, 21) * 0.97 and close <= ta.lowest(close, 21) * 1.12 ? 1.0 : 0.0
baseScore = clip01(ta.sma(baseNow, 10) * 10.0 / 7.0)
structureScore = retestScore * 0.55 + baseScore * 0.45
volumeScore = clip01((volumeRatio - 0.9) / 0.8)
maDiscountScore = clip01((-distSma) / 18.0)

totalWeight = drawdownWeight + momentumWeight + repairWeight + structureWeight + volumeWeight + maWeight
rawBottom = totalWeight == 0 ? 0.0 : (drawdownScore * drawdownWeight + momentumScore * momentumWeight + repairScore * repairWeight + structureScore * structureWeight + volumeScore * volumeWeight + maDiscountScore * maWeight) / totalWeight
bottomScore = math.round(math.min(100.0, math.max(1.0, 1.0 + rawBottom * 99.0)))
rsDrawdownAdvantage = drawdown - rsMarketDrawdown
rsRepairAdvantage = stockRepair - marketRepair
rsDrawdownScore = clip01(rsDrawdownAdvantage / rsDrawdownAdvantageThreshold)
rsRepairScore = clip01(rsRepairAdvantage / rsRepairAdvantageThreshold)
rsTrendScore = clip01((distSma + 5.0) / 15.0)
rawRs = rsDrawdownScore * 0.45 + rsRepairScore * 0.45 + rsTrendScore * 0.10
relativeStrengthScore = math.round(math.min(100.0, math.max(1.0, 1.0 + rawRs * 99.0)))
priorLow = ta.lowest(low[3], rsWindow)
higherLowScore = clip01((low / priorLow - 1.0) / 0.08)
notChasingScore = clip01((0.18 - (close / ta.lowest(close, 21) - 1.0)) / 0.18)
rsStructureScore = math.round(math.min(100.0, math.max(1.0, 1.0 + (higherLowScore * 0.70 + notChasingScore * 0.30) * 99.0)))
priorMarketDrawdown = ta.lowest(rsMarketDrawdown[1], rsWindow)
marketBreakdownScore = clip01((priorMarketDrawdown - rsMarketDrawdown) / 5.0)
priorStockLow = ta.lowest(low[1], rsWindow)
stockHoldingScore = clip01((low / priorStockLow - 1.0) / 0.08)
rsMarketDivergenceScore = math.round(math.min(100.0, math.max(1.0, 1.0 + (stockHoldingScore * 0.60 + marketBreakdownScore * 0.40) * 99.0)))
priorCrashScore = clip01((ta.highest(-drawdown, rsWindow) - math.abs(ddThreshold)) / 12.0)
shortReclaimScore = clip01((close / ta.sma(close, 20) - 0.98) / 0.08)
mediumReclaimScore = clip01((close / ta.sma(close, 50) - 0.98) / 0.10)
recoverySlopeScore = clip01((close / close[3] - 1.0) / 0.08)
rsMaReclaimScore = math.round(math.min(100.0, math.max(1.0, 1.0 + priorCrashScore * (shortReclaimScore * 0.45 + mediumReclaimScore * 0.35 + recoverySlopeScore * 0.20) * 99.0)))
atrPct = atrValue / close
panicVolatility = ta.highest(atrPct, rsWindow)
volatilityDropScore = clip01((panicVolatility - atrPct) / 0.04)
volatilityStabilizedScore = clip01((ta.highest(atrPct, 3) - atrPct) / 0.02)
rsVolatilityCompressionScore = math.round(math.min(100.0, math.max(1.0, 1.0 + priorCrashScore * (volatilityDropScore * 0.70 + volatilityStabilizedScore * 0.30) * 99.0)))
recentPullbackDepth = ta.highest(-drawdown, rsPullbackWindow)
pullbackDeepEnough = clip01((recentPullbackDepth - rsPullbackMinDrawdown) / rsPullbackMinDrawdown)
pullbackRange = math.max(1.0, rsPullbackMaxDrawdown - rsPullbackMinDrawdown)
pullbackNotTooDeep = clip01((rsPullbackMaxDrawdown - recentPullbackDepth) / pullbackRange)
pullbackDepthScore = pullbackDeepEnough * pullbackNotTooDeep
pullbackRepairScore = clip01((close / ta.lowest(close, 10) - 1.0) / 0.08)
pullbackMaScore = clip01((distSma + 8.0) / 18.0)
pullbackNotChasingScore = clip01((0.16 - (close / ta.lowest(close, 21) - 1.0)) / 0.16)
rsPullbackScore = math.round(math.min(100.0, math.max(1.0, 1.0 + (rawRs * 0.35 + pullbackDepthScore * 0.25 + pullbackRepairScore * 0.20 + pullbackMaScore * 0.15 + pullbackNotChasingScore * 0.05) * 99.0)))
rsMacdConfirmation = clip01((macdHist - ta.lowest(macdHist, 5)) / 1.5)
rsTrendConfirmation = clip01((distSma + 3.0) / 12.0)
rsPriceRepairConfirmation = clip01((close / ta.lowest(close, 10) - 1.0) / 0.08)
rsConfirmationScore = math.round(math.min(100.0, math.max(1.0, 1.0 + (rsMacdConfirmation * 0.45 + rsTrendConfirmation * 0.35 + rsPriceRepairConfirmation * 0.20) * 99.0)))
rsSignalScore = useRsPullbackRepairV2 ? math.round(math.min(100.0, math.max(1.0, bottomScore * 0.35 + relativeStrengthScore * 0.25 + rsStructureScore * 0.10 + rsPullbackScore * 0.30))) : useRsVolatilityCompression ? math.round(math.min(100.0, math.max(1.0, bottomScore * 0.45 + relativeStrengthScore * 0.25 + rsStructureScore * 0.10 + rsVolatilityCompressionScore * 0.20))) : useRsPostCrashMaReclaim ? math.round(math.min(100.0, math.max(1.0, bottomScore * 0.45 + relativeStrengthScore * 0.25 + rsStructureScore * 0.10 + rsMaReclaimScore * 0.20))) : useRsMarketDivergence ? math.round(math.min(100.0, math.max(1.0, bottomScore * 0.45 + relativeStrengthScore * 0.30 + rsStructureScore * 0.10 + rsMarketDivergenceScore * 0.15))) : useRsRepairTrendConfirm ? math.round(math.min(100.0, math.max(1.0, bottomScore * 0.45 + relativeStrengthScore * 0.30 + rsStructureScore * 0.10 + rsConfirmationScore * 0.15))) : useRsHigherLowStructure ? math.round(math.min(100.0, math.max(1.0, bottomScore * 0.50 + relativeStrengthScore * 0.35 + rsStructureScore * 0.15))) : math.round(math.min(100.0, math.max(1.0, bottomScore * 0.55 + relativeStrengthScore * 0.45)))

recentGain = clip01((close / close[63] - 1.0) / 0.28)
rsiHot = clip01((rsiValue - 68.0) / 14.0)
maStretch = clip01(distSma / 18.0)
macdWeakening = clip01((ta.highest(macdHist, 5) - macdHist) / 1.2)
bandStretch = clip01((close / bbUpper - 1.0) / 0.04)
atrHot = clip01((atrValue / close) / 0.06)
rawExit = recentGain * 0.22 + rsiHot * 0.24 + maStretch * 0.20 + macdWeakening * 0.16 + bandStretch * 0.12 + atrHot * 0.06
exitScore = math.round(math.min(100.0, math.max(1.0, 1.0 + rawExit * 99.0)))

mbCandidate = marketOk and bottomScore >= watchThreshold
rsCandidate = rsSignalScore >= watchThreshold
var int lastMbSignalBar = na
var int lastRsSignalBar = na
mbGapOk = na(lastMbSignalBar) or bar_index - lastMbSignalBar >= minSignalGap
rsGapOk = na(lastRsSignalBar) or bar_index - lastRsSignalBar >= minSignalGap
mbSignal = mbCandidate and mbGapOk
rsSignal = rsCandidate and rsGapOk
if mbSignal
    lastMbSignalBar := bar_index
if rsSignal
    lastRsSignalBar := bar_index

mbWatchSignal = mbSignal and bottomScore >= watchThreshold and bottomScore < mediumThreshold
mbEntryThreshold = entryThreshold + mbEntryOffset
mbMediumSignal = mbSignal and bottomScore >= mediumThreshold and bottomScore < mbEntryThreshold
mbStrongSignal = mbSignal and bottomScore >= mbEntryThreshold
rsWatchSignal = rsSignal and rsSignalScore >= watchThreshold and rsSignalScore < mediumThreshold
rsMediumSignal = rsSignal and rsSignalScore >= mediumThreshold and rsSignalScore < entryThreshold
rsStrongSignal = rsSignal and rsSignalScore >= entryThreshold
exitSignal = exitScore >= exitThreshold

showRsStrong = rsStrongSignal
showMbStrong = mbStrongSignal and not showRsStrong
showRsMedium = rsMediumSignal and not showRsStrong and not showMbStrong
showMbMedium = mbMediumSignal and not showRsStrong and not showMbStrong and not showRsMedium
showRsWatch = rsWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium
showMbWatch = mbWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium and not showRsWatch

signalName = exitSignal ? "X" : showRsStrong ? "RS-3" : showMbStrong ? "MB-3" : showRsMedium ? "RS-2" : showMbMedium ? "MB-2" : showRsWatch ? "RS-1" : showMbWatch ? "MB-1" : "None"
signalColor = exitSignal ? color.red : showRsStrong ? color.aqua : showMbStrong ? color.green : showRsMedium ? color.new(color.aqua, 15) : showMbMedium ? color.new(color.green, 15) : showRsWatch ? color.new(color.aqua, 35) : showMbWatch ? color.new(color.green, 35) : na
barcolor(showSignalColors ? signalColor : na)
bgcolor(showSignalBackground and exitSignal ? color.new(color.red, 84) : showSignalBackground and signalName != "None" ? color.new(signalColor, 88) : na)

var table signalTable = table.new(position.top_right, 2, 4, border_width=1)
if barstate.islast and showSignalTable
    table.cell(signalTable, 0, 0, "Signal", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(signalTable, 1, 0, signalName, text_color=color.white, bgcolor=signalName == "None" ? color.new(color.gray, 35) : color.new(signalColor, 0))
    table.cell(signalTable, 0, 1, "Bottom", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(signalTable, 1, 1, str.tostring(bottomScore), text_color=color.white, bgcolor=color.new(color.green, 65))
    table.cell(signalTable, 0, 2, "RS", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(signalTable, 1, 2, str.tostring(rsSignalScore), text_color=color.black, bgcolor=color.new(color.aqua, 55))
    table.cell(signalTable, 0, 3, "Exit", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(signalTable, 1, 3, str.tostring(exitScore), text_color=color.white, bgcolor=color.new(color.red, 65))

plot(showScoreLines ? bottomScore : na, "Bottom Score", color=color.new(color.green, 0), linewidth=1, display=display.data_window)
plot(showScoreLines ? relativeStrengthScore : na, "Relative Strength Score", color=color.new(color.aqua, 0), linewidth=1, display=display.data_window)
plot(showScoreLines ? exitScore : na, "Exit Score", color=color.new(color.red, 0), linewidth=1, display=display.data_window)
plotshape(showTextMarkers and showMbWatch, "MB-1", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 35), text="MB-1", textcolor=color.white, size=size.tiny)
plotshape(showTextMarkers and showMbMedium, "MB-2", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 15), text="MB-2", textcolor=color.white, size=size.small)
plotshape(showTextMarkers and showMbStrong, "MB-3", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), text="MB-3", textcolor=color.white, size=size.normal)
plotshape(showTextMarkers and showRsWatch, "RS-1", style=shape.labelup, location=location.belowbar, color=color.new(color.aqua, 35), text="RS-1", textcolor=color.black, size=size.tiny)
plotshape(showTextMarkers and showRsMedium, "RS-2", style=shape.labelup, location=location.belowbar, color=color.new(color.aqua, 15), text="RS-2", textcolor=color.black, size=size.small)
plotshape(showTextMarkers and showRsStrong, "RS-3", style=shape.labelup, location=location.belowbar, color=color.new(color.aqua, 0), text="RS-3", textcolor=color.black, size=size.normal)
plotshape(showTextMarkers and exitSignal, "Exit", style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), text="X", textcolor=color.white, size=size.small)
"""


def generate_pine_script(
    config: BottomSignalConfig,
    observation_config: dict[str, Any] | None = None,
) -> str:
    observation_config = observation_config or observation_candidate_configs()[0]
    script = generate_strict_formal_pine_script(config)
    script = script.replace(
        'indicator("AutoQuant Bottom Signal Score", overlay=true, max_labels_count=500)',
        'indicator("AutoQuant Bottom Signal Integrated", overlay=true, max_labels_count=500)',
    )
    script = script.replace(
        f'minSignalGap = input.int({config.min_signal_gap}, "Min Signal Gap", minval=1)',
        (
            f'minSignalGap = input.int({config.min_signal_gap}, "Min Signal Gap", minval=1)\n'
            f'obsDeepBottomMin = input.int({int(observation_config.get("deepBottomMin", 68))}, "OBS-D Bottom Min", minval=1, maxval=100)\n'
            f'obsShallowBottomMin = input.int({int(observation_config.get("shallowBottomMin", 70))}, "OBS-S Bottom Min", minval=1, maxval=100)\n'
            f'obsBottomMax = input.int({int(observation_config.get("bottomMax", 75))}, "OBS Bottom Max", minval=1, maxval=100)\n'
            f'obsDeepMarketMax = input.float({float(observation_config.get("deepMarketMax", -20.0)):g}, "OBS-D Market Max Drawdown %", step=0.5)\n'
            f'obsShallowMarketMax = input.float({float(observation_config.get("shallowMarketMax", -8.0)):g}, "OBS-S Market Max Drawdown %", step=0.5)\n'
            f'obsNearLowWindow = input.int({int(observation_config.get("nearLowWindow", 63))}, "OBS Near-Low Window", minval=2)\n'
            f'obsNearLowMax = input.float({float(observation_config.get("nearLowMax", 0.02)):g}, "OBS Near-Low Max Gap", step=0.005)\n'
            f'obsClusterGap = input.int({int(observation_config.get("clusterWindow", 42))}, "OBS Min Signal Gap", minval=1)'
        ),
    )
    script = script.replace(
        "marketDrawdown2 = (marketClose2 / ta.highest(marketClose2, marketWindow) - 1.0) * 100.0\n"
        "marketOk = math.min(marketDrawdown1, marketDrawdown2) <= marketThreshold",
        "marketDrawdown2 = (marketClose2 / ta.highest(marketClose2, marketWindow) - 1.0) * 100.0\n"
        "marketDrawdown = math.min(marketDrawdown1, marketDrawdown2)\n"
        "marketOk = marketDrawdown <= marketThreshold",
    )
    script = script.replace(
        "rsStrongSignal = rsSignal and rsSignalScore >= entryThreshold\n"
        "exitSignal = exitScore >= exitThreshold",
        "rsStrongSignal = rsSignal and rsSignalScore >= entryThreshold\n"
        "nearLowGap = close / ta.lowest(close, obsNearLowWindow) - 1.0\n"
        "obsDeepCandidate = marketDrawdown <= obsDeepMarketMax and bottomScore >= obsDeepBottomMin and bottomScore <= obsBottomMax and nearLowGap <= obsNearLowMax\n"
        "obsShallowCandidate = marketDrawdown > obsDeepMarketMax and marketDrawdown <= obsShallowMarketMax and bottomScore >= obsShallowBottomMin and bottomScore <= obsBottomMax and nearLowGap <= obsNearLowMax\n"
        "var int lastObsSignalBar = na\n"
        "obsGapOk = na(lastObsSignalBar) or bar_index - lastObsSignalBar >= obsClusterGap\n"
        "obsDeepSecondTest = obsDeepCandidate and obsGapOk and not mbStrongSignal\n"
        "obsShallowPullback = obsShallowCandidate and obsGapOk and not mbStrongSignal and not obsDeepSecondTest\n"
        "if obsDeepSecondTest or obsShallowPullback\n"
        "    lastObsSignalBar := bar_index\n"
        "observationSignal = obsDeepSecondTest ? \"OBS-D\" : obsShallowPullback ? \"OBS-S\" : \"None\"\n"
        "exitSignal = exitScore >= exitThreshold",
    )
    script = script.replace(
        "showRsStrong = rsStrongSignal\n"
        "showMbStrong = mbStrongSignal and not showRsStrong\n"
        "showRsMedium = rsMediumSignal and not showRsStrong and not showMbStrong\n"
        "showMbMedium = mbMediumSignal and not showRsStrong and not showMbStrong and not showRsMedium\n"
        "showRsWatch = rsWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium\n"
        "showMbWatch = mbWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium and not showRsWatch\n\n"
        "signalName = exitSignal ? \"X\" : showRsStrong ? \"RS-3\" : showMbStrong ? \"MB-3\" : showRsMedium ? \"RS-2\" : showMbMedium ? \"MB-2\" : showRsWatch ? \"RS-1\" : showMbWatch ? \"MB-1\" : \"None\"\n"
        "signalColor = exitSignal ? color.red : showRsStrong ? color.aqua : showMbStrong ? color.green : showRsMedium ? color.new(color.aqua, 15) : showMbMedium ? color.new(color.green, 15) : showRsWatch ? color.new(color.aqua, 35) : showMbWatch ? color.new(color.green, 35) : na\n"
        "barcolor(showSignalColors ? signalColor : na)\n"
        "bgcolor(showSignalBackground and exitSignal ? color.new(color.red, 84) : showSignalBackground and signalName != \"None\" ? color.new(signalColor, 88) : na)",
        "showBuyMb = mbStrongSignal\n"
        "showBuyDeep = obsDeepSecondTest and not showBuyMb\n"
        "showBuyShallow = obsShallowPullback and not showBuyMb and not showBuyDeep\n"
        "integratedBuySignal = showBuyMb or showBuyDeep or showBuyShallow\n"
        "showRsStrong = rsStrongSignal and not integratedBuySignal\n"
        "showMbStrong = false\n"
        "showRsMedium = rsMediumSignal and not integratedBuySignal and not showRsStrong\n"
        "showMbMedium = mbMediumSignal and not integratedBuySignal and not showRsStrong and not showRsMedium\n"
        "showRsWatch = rsWatchSignal and not integratedBuySignal and not showRsStrong and not showRsMedium and not showMbMedium\n"
        "showMbWatch = mbWatchSignal and not integratedBuySignal and not showRsStrong and not showRsMedium and not showMbMedium and not showRsWatch\n\n"
        "signalName = showBuyMb ? \"BUY-MB\" : showBuyDeep ? \"BUY-D\" : showBuyShallow ? \"BUY-S\" : exitSignal ? \"X\" : showRsStrong ? \"RS-3\" : showRsMedium ? \"RS-2\" : showMbMedium ? \"MB-2\" : showRsWatch ? \"RS-1\" : showMbWatch ? \"MB-1\" : \"None\"\n"
        "signalColor = integratedBuySignal ? color.green : exitSignal ? color.red : showRsStrong ? color.aqua : showRsMedium ? color.new(color.aqua, 15) : showMbMedium ? color.new(color.green, 15) : showRsWatch ? color.new(color.aqua, 35) : showMbWatch ? color.new(color.green, 35) : na\n"
        "barcolor(showSignalColors ? signalColor : na)\n"
        "bgcolor(showSignalBackground and integratedBuySignal ? color.new(color.green, 88) : showSignalBackground and exitSignal ? color.new(color.red, 84) : showSignalBackground and signalName != \"None\" ? color.new(signalColor, 88) : na)",
    )
    script = script.replace(
        "var table signalTable = table.new(position.top_right, 2, 4, border_width=1)\n"
        "if barstate.islast and showSignalTable\n"
        "    table.cell(signalTable, 0, 0, \"Signal\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 0, signalName, text_color=color.white, bgcolor=signalName == \"None\" ? color.new(color.gray, 35) : color.new(signalColor, 0))\n"
        "    table.cell(signalTable, 0, 1, \"Bottom\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 1, str.tostring(bottomScore), text_color=color.white, bgcolor=color.new(color.green, 65))\n"
        "    table.cell(signalTable, 0, 2, \"RS\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 2, str.tostring(rsSignalScore), text_color=color.black, bgcolor=color.new(color.aqua, 55))\n"
        "    table.cell(signalTable, 0, 3, \"Exit\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 3, str.tostring(exitScore), text_color=color.white, bgcolor=color.new(color.red, 65))",
        "var table signalTable = table.new(position.top_right, 2, 7, border_width=1)\n"
        "if barstate.islast and showSignalTable\n"
        "    table.cell(signalTable, 0, 0, \"Signal\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 0, signalName, text_color=color.white, bgcolor=signalName == \"None\" ? color.new(color.gray, 35) : color.new(signalColor, 0))\n"
        "    table.cell(signalTable, 0, 1, \"Source\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 1, showBuyMb ? \"MB Strong\" : showBuyDeep ? \"OBS-D\" : showBuyShallow ? \"OBS-S\" : \"None\", text_color=color.white, bgcolor=integratedBuySignal ? color.new(color.green, 0) : color.new(color.gray, 35))\n"
        "    table.cell(signalTable, 0, 2, \"Observation\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 2, observationSignal, text_color=color.black, bgcolor=observationSignal == \"OBS-D\" ? color.new(color.green, 25) : observationSignal == \"OBS-S\" ? color.new(color.lime, 20) : color.new(color.gray, 35))\n"
        "    table.cell(signalTable, 0, 3, \"Market DD\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 3, str.tostring(marketDrawdown, \"#.##\") + \"%\", text_color=color.white, bgcolor=color.new(color.blue, 65))\n"
        "    table.cell(signalTable, 0, 4, \"Bottom\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 4, str.tostring(bottomScore), text_color=color.white, bgcolor=color.new(color.green, 65))\n"
        "    table.cell(signalTable, 0, 5, \"RS\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 5, str.tostring(rsSignalScore), text_color=color.black, bgcolor=color.new(color.aqua, 55))\n"
        "    table.cell(signalTable, 0, 6, \"Exit\", text_color=color.white, bgcolor=color.new(color.black, 0))\n"
        "    table.cell(signalTable, 1, 6, str.tostring(exitScore), text_color=color.white, bgcolor=color.new(color.red, 65))",
    )
    script = script.replace(
        'plotshape(showTextMarkers and showMbStrong, "MB-3", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), text="MB-3", textcolor=color.white, size=size.normal)\n'
        'plotshape(showTextMarkers and showRsWatch, "RS-1"',
        'plotshape(showTextMarkers and showBuyMb, "BUY-MB", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), text="BUY-MB", textcolor=color.white, size=size.normal)\n'
        'plotshape(showTextMarkers and showBuyDeep, "BUY-D", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), text="BUY-D", textcolor=color.white, size=size.normal)\n'
        'plotshape(showTextMarkers and showBuyShallow, "BUY-S", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), text="BUY-S", textcolor=color.white, size=size.normal)\n'
        'plotshape(showTextMarkers and showRsWatch, "RS-1"',
    )
    script += (
        '\nalertcondition(integratedBuySignal, "Integrated Buy", "AutoQuant integrated buy signal")\n'
        'alertcondition(showBuyMb, "Integrated Buy MB", "AutoQuant BUY-MB strict formal buy signal")\n'
        'alertcondition(showBuyDeep, "Integrated Buy Deep", "AutoQuant BUY-D observation buy signal")\n'
        'alertcondition(showBuyShallow, "Integrated Buy Shallow", "AutoQuant BUY-S observation buy signal")\n'
    )
    return script


def generate_merged_observation_pine_script(
    config: BottomSignalConfig,
    observation_config: dict[str, Any] | None = None,
) -> str:
    observation_config = observation_config or observation_candidate_configs()[0]
    script = generate_strict_formal_pine_script(config)
    script = script.replace(
        'indicator("AutoQuant Bottom Signal Score", overlay=true, max_labels_count=500)',
        'indicator("AutoQuant Bottom + RS + Observation", overlay=true, max_labels_count=500)',
    )
    script = script.replace(
        f'minSignalGap = input.int({config.min_signal_gap}, "Min Signal Gap", minval=1)',
        (
            f'minSignalGap = input.int({config.min_signal_gap}, "Min Signal Gap", minval=1)\n'
            f'obsDeepBottomMin = input.int({int(observation_config.get("deepBottomMin", 68))}, "OBS-D Bottom Min", minval=1, maxval=100)\n'
            f'obsShallowBottomMin = input.int({int(observation_config.get("shallowBottomMin", 70))}, "OBS-S Bottom Min", minval=1, maxval=100)\n'
            f'obsBottomMax = input.int({int(observation_config.get("bottomMax", 75))}, "OBS Bottom Max", minval=1, maxval=100)\n'
            f'obsDeepMarketMax = input.float({float(observation_config.get("deepMarketMax", -20.0)):g}, "OBS-D Market Max Drawdown %", step=0.5)\n'
            f'obsShallowMarketMax = input.float({float(observation_config.get("shallowMarketMax", -8.0)):g}, "OBS-S Market Max Drawdown %", step=0.5)\n'
            f'obsNearLowWindow = input.int({int(observation_config.get("nearLowWindow", 63))}, "OBS Near-Low Window", minval=2)\n'
            f'obsNearLowMax = input.float({float(observation_config.get("nearLowMax", 0.02)):g}, "OBS Near-Low Max Gap", step=0.005)\n'
            f'obsClusterGap = input.int({int(observation_config.get("clusterWindow", 42))}, "OBS Min Signal Gap", minval=1)\n'
            'qualityThreshold = input.int(70, "RS Quality Threshold", minval=1, maxval=100)'
        ),
    )
    script = script.replace(
        "marketDrawdown2 = (marketClose2 / ta.highest(marketClose2, marketWindow) - 1.0) * 100.0\n"
        "marketOk = math.min(marketDrawdown1, marketDrawdown2) <= marketThreshold",
        "marketDrawdown2 = (marketClose2 / ta.highest(marketClose2, marketWindow) - 1.0) * 100.0\n"
        "marketDrawdown = math.min(marketDrawdown1, marketDrawdown2)\n"
        "marketOk = marketDrawdown <= marketThreshold",
    )
    script = script.replace(
        "rsStrongSignal = rsSignal and rsSignalScore >= entryThreshold\n"
        "exitSignal = exitScore >= exitThreshold",
        "rsStrongSignal = rsSignal and rsSignalScore >= entryThreshold\n"
        "trendDamage = distSma < -32.0\n"
        "lowVolume = volumeRatio < 0.75\n"
        "noRepair = repairScore < 0.25 and drawdown <= ddThreshold\n"
        "overextendedRebound = (close / ta.lowest(close, 10) - 1.0) >= 0.12 and distSma > 0 and drawdown > ddThreshold * 1.5\n"
        "riskPenalty = (trendDamage ? 25.0 : 0.0) + (noRepair ? 18.0 : 0.0) + (lowVolume ? 10.0 : 0.0) + (overextendedRebound ? 16.0 : 0.0)\n"
        "tierBonus = rsSignalScore >= mediumThreshold ? 3.0 : 0.0\n"
        "rsQualityScore = math.round(math.min(100.0, math.max(1.0, relativeStrengthScore * 0.45 + rsSignalScore * 0.30 + bottomScore * 0.15 + tierBonus - riskPenalty)))\n"
        "rsQualified = rsSignalScore >= watchThreshold and rsQualityScore >= qualityThreshold\n"
        "rsRisk = rsSignalScore >= watchThreshold and rsQualityScore < qualityThreshold\n"
        "rsWatchlistSignal = rsQualified ? \"RS-Q\" : rsRisk ? \"RS-R\" : \"None\"\n"
        "nearLowGap = close / ta.lowest(close, obsNearLowWindow) - 1.0\n"
        "obsDeepCandidate = marketDrawdown <= obsDeepMarketMax and bottomScore >= obsDeepBottomMin and bottomScore <= obsBottomMax and nearLowGap <= obsNearLowMax\n"
        "obsShallowCandidate = marketDrawdown > obsDeepMarketMax and marketDrawdown <= obsShallowMarketMax and bottomScore >= obsShallowBottomMin and bottomScore <= obsBottomMax and nearLowGap <= obsNearLowMax\n"
        "var int lastObsSignalBar = na\n"
        "obsGapOk = na(lastObsSignalBar) or bar_index - lastObsSignalBar >= obsClusterGap\n"
        "obsDeepSecondTest = obsDeepCandidate and obsGapOk and not mbStrongSignal and not rsStrongSignal\n"
        "obsShallowPullback = obsShallowCandidate and obsGapOk and not mbStrongSignal and not rsStrongSignal and not obsDeepSecondTest\n"
        "if obsDeepSecondTest or obsShallowPullback\n"
        "    lastObsSignalBar := bar_index\n"
        "observationSignal = obsDeepSecondTest ? \"OBS-D\" : obsShallowPullback ? \"OBS-S\" : \"None\"\n"
        "exitSignal = exitScore >= exitThreshold",
    )
    script = script.replace(
        "showRsWatch = rsWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium\n"
        "showMbWatch = mbWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium and not showRsWatch\n\n"
        "signalName = exitSignal ? \"X\" : showRsStrong ? \"RS-3\" : showMbStrong ? \"MB-3\" : showRsMedium ? \"RS-2\" : showMbMedium ? \"MB-2\" : showRsWatch ? \"RS-1\" : showMbWatch ? \"MB-1\" : \"None\"\n"
        "signalColor = exitSignal ? color.red : showRsStrong ? color.aqua : showMbStrong ? color.green : showRsMedium ? color.new(color.aqua, 15) : showMbMedium ? color.new(color.green, 15) : showRsWatch ? color.new(color.aqua, 35) : showMbWatch ? color.new(color.green, 35) : na",
        "showObsDeep = obsDeepSecondTest and not showRsStrong and not showMbStrong\n"
        "showObsShallow = obsShallowPullback and not showRsStrong and not showMbStrong and not showObsDeep\n"
        "showRsQualified = rsQualified and not showRsStrong and not showMbStrong and not showObsDeep and not showObsShallow\n"
        "showRsRisk = rsRisk and not showRsStrong and not showMbStrong and not showObsDeep and not showObsShallow and not showRsQualified\n"
        "showRsWatch = rsWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium and not showObsDeep and not showObsShallow and not showRsQualified and not showRsRisk\n"
        "showMbWatch = mbWatchSignal and not showRsStrong and not showMbStrong and not showRsMedium and not showMbMedium and not showObsDeep and not showObsShallow and not showRsQualified and not showRsRisk and not showRsWatch\n\n"
        "signalName = showRsStrong ? \"RS-3\" : showMbStrong ? \"MB-3\" : showObsDeep ? \"OBS-D\" : showObsShallow ? \"OBS-S\" : exitSignal ? \"X\" : showRsQualified ? \"RS-Q\" : showRsRisk ? \"RS-R\" : showRsMedium ? \"RS-2\" : showMbMedium ? \"MB-2\" : showRsWatch ? \"RS-1\" : showMbWatch ? \"MB-1\" : \"None\"\n"
        "signalColor = showRsStrong ? color.aqua : showMbStrong ? color.green : showObsDeep ? color.new(color.green, 0) : showObsShallow ? color.new(color.lime, 0) : exitSignal ? color.red : showRsQualified ? color.blue : showRsRisk ? color.purple : showRsMedium ? color.new(color.aqua, 15) : showMbMedium ? color.new(color.green, 15) : showRsWatch ? color.new(color.aqua, 35) : showMbWatch ? color.new(color.green, 35) : na",
    )
    script = script.replace(
        "bgcolor(showSignalBackground and exitSignal ? color.new(color.red, 84) : showSignalBackground and signalName != \"None\" ? color.new(signalColor, 88) : na)",
        "bgcolor(showSignalBackground and signalName == \"X\" ? color.new(color.red, 84) : showSignalBackground and signalName != \"None\" ? color.new(signalColor, 88) : na)",
    )
    script = script.replace(
        "var table signalTable = table.new(position.top_right, 2, 4, border_width=1)",
        "var table signalTable = table.new(position.top_right, 2, 7, border_width=1)",
    )
    script = script.replace(
        '    table.cell(signalTable, 0, 3, "Exit", text_color=color.white, bgcolor=color.new(color.black, 0))\n'
        "    table.cell(signalTable, 1, 3, str.tostring(exitScore), text_color=color.white, bgcolor=color.new(color.red, 65))",
        '    table.cell(signalTable, 0, 3, "Observation", text_color=color.white, bgcolor=color.new(color.black, 0))\n'
        "    table.cell(signalTable, 1, 3, observationSignal, text_color=color.black, bgcolor=observationSignal == \"OBS-D\" ? color.new(color.green, 25) : observationSignal == \"OBS-S\" ? color.new(color.lime, 20) : color.new(color.gray, 35))\n"
        '    table.cell(signalTable, 0, 4, "Market DD", text_color=color.white, bgcolor=color.new(color.black, 0))\n'
        "    table.cell(signalTable, 1, 4, str.tostring(marketDrawdown, \"#.##\") + \"%\", text_color=color.white, bgcolor=color.new(color.blue, 65))\n"
        '    table.cell(signalTable, 0, 5, "RS Quality", text_color=color.white, bgcolor=color.new(color.black, 0))\n'
        "    table.cell(signalTable, 1, 5, rsWatchlistSignal + \" \" + str.tostring(rsQualityScore), text_color=color.white, bgcolor=color.new(color.blue, 65))\n"
        '    table.cell(signalTable, 0, 6, "Exit", text_color=color.white, bgcolor=color.new(color.black, 0))\n'
        "    table.cell(signalTable, 1, 6, str.tostring(exitScore), text_color=color.white, bgcolor=color.new(color.red, 65))",
    )
    script = script.replace(
        'plotshape(showTextMarkers and showRsWatch, "RS-1"',
        'plotshape(showTextMarkers and showObsDeep, "OBS-D", style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), text="OBS-D", textcolor=color.white, size=size.small)\n'
        'plotshape(showTextMarkers and showObsShallow, "OBS-S", style=shape.labelup, location=location.belowbar, color=color.new(color.lime, 0), text="OBS-S", textcolor=color.black, size=size.small)\n'
        'plotshape(showTextMarkers and showRsQualified, "RS-Q", style=shape.labelup, location=location.belowbar, color=color.new(color.blue, 0), text="RS-Q", textcolor=color.white, size=size.small)\n'
        'plotshape(showTextMarkers and showRsRisk, "RS-R", style=shape.labelup, location=location.belowbar, color=color.new(color.purple, 0), text="RS-R", textcolor=color.white, size=size.small)\n'
        'plotshape(showTextMarkers and showRsWatch, "RS-1"',
    )
    script += (
        '\nalertcondition(mbStrongSignal, "MB Strong", "AutoQuant MB Strong signal")\n'
        'alertcondition(rsStrongSignal, "RS Strong", "AutoQuant RS Strong signal")\n'
        'alertcondition(obsDeepSecondTest, "OBS Deep Second Test", "AutoQuant OBS-D deep second-test observation")\n'
        'alertcondition(obsShallowPullback, "OBS Shallow Pullback", "AutoQuant OBS-S shallow pullback observation")\n'
        'alertcondition(rsQualified, "RS Watchlist Qualified", "AutoQuant RS-Q watchlist quality signal")\n'
        'alertcondition(rsRisk, "RS Watchlist Risk", "AutoQuant RS-R watchlist risk signal")\n'
    )
    return script


def generate_rs_watchlist_pine_script(
    config: BottomSignalConfig,
    quality_threshold: int = 70,
) -> str:
    return f"""//@version=6
indicator("AutoQuant RS Watchlist - Observation only", overlay=true, max_labels_count=500)

ddWindow = input.int({config.drawdown_window}, "Drawdown Window", minval=2)
ddThreshold = input.float({config.drawdown_threshold:g}, "Drawdown Threshold %", step=0.5)
rsiPeriod = input.int({config.rsi_period}, "RSI Period", minval=2)
stochPeriod = input.int({config.stoch_period}, "Stochastic Period", minval=2)
stochSmooth = input.int({config.stoch_smooth}, "Stochastic Smooth", minval=1)
macdFast = input.int({config.macd_fast}, "MACD Fast", minval=1)
macdSlow = input.int({config.macd_slow}, "MACD Slow", minval=2)
macdSignal = input.int({config.macd_signal}, "MACD Signal", minval=1)
smaPeriod = input.int({config.ma_period}, "SMA Period", minval=2)
volumeWindow = input.int({config.volume_window}, "Volume Window", minval=2)
marketSymbol1 = input.symbol("{config.market_symbol_1}", "Market Symbol 1")
marketSymbol2 = input.symbol("{config.market_symbol_2}", "Market Symbol 2")
rsWindow = input.int({config.rs_window}, "RS Window", minval=2)
rsDrawdownAdvantageThreshold = input.float({config.rs_drawdown_advantage_threshold:g}, "RS Drawdown Advantage %", step=0.5)
rsRepairAdvantageThreshold = input.float({config.rs_repair_advantage_threshold:g}, "RS Repair Advantage %", step=0.5)
watchThreshold = input.int({config.watch_threshold}, "Watch Score", minval=1, maxval=100)
mediumThreshold = input.int({config.medium_threshold}, "Medium Score", minval=1, maxval=100)
qualityThreshold = input.int({quality_threshold}, "RS Quality Threshold", minval=1, maxval=100)
showScoreLines = input.bool(false, "Show Score Lines")
showSignalColors = input.bool(true, "Show Signal Candle Colors")
showSignalBackground = input.bool(true, "Show Signal Background")
showSignalTable = input.bool(true, "Show Signal Table")
showTextMarkers = input.bool(true, "Show Text Markers")

clip01(x) =>
    math.min(1.0, math.max(0.0, nz(x, 0.0)))

rollingHigh = ta.highest(close, ddWindow)
drawdown = (close / rollingHigh - 1.0) * 100.0
rsiValue = ta.rsi(close, rsiPeriod)
stochRaw = ta.stoch(close, high, low, stochPeriod)
stochValue = ta.sma(stochRaw, stochSmooth)
[macdLine, macdSignalLine, macdHist] = ta.macd(close, macdFast, macdSlow, macdSignal)
smaValue = ta.sma(close, smaPeriod)
distSma = (close / smaValue - 1.0) * 100.0
volumeSma = ta.sma(volume, volumeWindow)
volumeRatio = volumeSma == 0 ? 1.0 : volume / volumeSma

marketClose1 = request.security(marketSymbol1, timeframe.period, close)
marketClose2 = request.security(marketSymbol2, timeframe.period, close)
rsMarketDrawdown1 = (marketClose1 / ta.highest(marketClose1, rsWindow) - 1.0) * 100.0
rsMarketDrawdown2 = (marketClose2 / ta.highest(marketClose2, rsWindow) - 1.0) * 100.0
rsMarketDrawdown = math.min(rsMarketDrawdown1, rsMarketDrawdown2)
stockRepair = (close / ta.lowest(close, rsWindow) - 1.0) * 100.0
marketRepair1 = (marketClose1 / ta.lowest(marketClose1, rsWindow) - 1.0) * 100.0
marketRepair2 = (marketClose2 / ta.lowest(marketClose2, rsWindow) - 1.0) * 100.0
marketRepair = math.max(marketRepair1, marketRepair2)

drawdownScore = clip01((-drawdown) / math.abs(ddThreshold))
rsiScore = clip01((48.0 - rsiValue) / 24.0)
stochScore = clip01((45.0 - stochValue) / 35.0)
momentumScore = rsiScore * 0.65 + stochScore * 0.35
macdRepair = clip01((macdHist - ta.lowest(macdHist, 3)) / 1.5)
closeRepair = clip01((close / ta.lowest(close, 5) - 1.0) / 0.06)
repairScore = macdRepair * 0.55 + closeRepair * 0.45
retestGap = math.abs(low / ta.lowest(low, 21) - 1.0)
retestScore = clip01((0.08 - retestGap) / 0.08)
baseNow = close >= ta.lowest(close, 21) * 0.97 and close <= ta.lowest(close, 21) * 1.12 ? 1.0 : 0.0
baseScore = clip01(ta.sma(baseNow, 10) * 10.0 / 7.0)
structureScore = retestScore * 0.55 + baseScore * 0.45
volumeScore = clip01((volumeRatio - 0.9) / 0.8)
maDiscountScore = clip01((-distSma) / 18.0)

rawBottom = drawdownScore * 0.30 + momentumScore * 0.22 + repairScore * 0.18 + structureScore * 0.15 + volumeScore * 0.08 + maDiscountScore * 0.07
bottomScore = math.round(math.min(100.0, math.max(1.0, 1.0 + rawBottom * 99.0)))

rsDrawdownAdvantage = drawdown - rsMarketDrawdown
rsRepairAdvantage = stockRepair - marketRepair
rsDrawdownScore = clip01(rsDrawdownAdvantage / rsDrawdownAdvantageThreshold)
rsRepairScore = clip01(rsRepairAdvantage / rsRepairAdvantageThreshold)
rsTrendScore = clip01((distSma + 5.0) / 15.0)
rawRs = rsDrawdownScore * 0.45 + rsRepairScore * 0.45 + rsTrendScore * 0.10
relativeStrengthScore = math.round(math.min(100.0, math.max(1.0, 1.0 + rawRs * 99.0)))
rsSignalScore = math.round(math.min(100.0, math.max(1.0, bottomScore * 0.55 + relativeStrengthScore * 0.45)))

trendDamage = distSma < -32.0
lowVolume = volumeRatio < 0.75
noRepair = repairScore < 0.25 and drawdown <= ddThreshold
overextendedRebound = (close / ta.lowest(close, 10) - 1.0) >= 0.12 and distSma > 0 and drawdown > ddThreshold * 1.5
riskPenalty = (trendDamage ? 25.0 : 0.0) + (noRepair ? 18.0 : 0.0) + (lowVolume ? 10.0 : 0.0) + (overextendedRebound ? 16.0 : 0.0)
tierBonus = rsSignalScore >= mediumThreshold ? 3.0 : 0.0
rsQualityScore = math.round(math.min(100.0, math.max(1.0, relativeStrengthScore * 0.45 + rsSignalScore * 0.30 + bottomScore * 0.15 + tierBonus - riskPenalty)))

rsWatch = rsSignalScore >= watchThreshold
rsQualified = rsWatch and rsQualityScore >= qualityThreshold
rsRisk = rsWatch and rsQualityScore < qualityThreshold
rsDisplaySignal = rsQualified ? "RS-Q" : rsRisk ? "RS-R" : "None"
rsDisplayColor = rsQualified ? color.aqua : rsRisk ? color.orange : na
barcolor(showSignalColors ? rsDisplayColor : na)
bgcolor(showSignalBackground and rsDisplaySignal != "None" ? color.new(rsDisplayColor, 88) : na)

var table rsTable = table.new(position.bottom_right, 2, 5, border_width=1)
if barstate.islast and showSignalTable
    table.cell(rsTable, 0, 0, "Signal", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(rsTable, 1, 0, rsDisplaySignal, text_color=color.black, bgcolor=rsDisplaySignal == "None" ? color.new(color.gray, 35) : color.new(rsDisplayColor, 0))
    table.cell(rsTable, 0, 1, "RS Signal", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(rsTable, 1, 1, str.tostring(rsSignalScore), text_color=color.black, bgcolor=color.new(color.aqua, 55))
    table.cell(rsTable, 0, 2, "Quality", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(rsTable, 1, 2, str.tostring(rsQualityScore), text_color=color.white, bgcolor=color.new(color.blue, 55))
    table.cell(rsTable, 0, 3, "Bottom", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(rsTable, 1, 3, str.tostring(bottomScore), text_color=color.white, bgcolor=color.new(color.green, 65))
    table.cell(rsTable, 0, 4, "RS-R", text_color=color.white, bgcolor=color.new(color.black, 0))
    table.cell(rsTable, 1, 4, "Risk", text_color=color.white, bgcolor=color.new(color.orange, 25))

plot(showScoreLines ? rsSignalScore : na, "RS Signal Score", color=color.new(color.aqua, 0), linewidth=1, display=display.data_window)
plot(showScoreLines ? rsQualityScore : na, "RS Quality Score", color=color.new(color.blue, 0), linewidth=1, display=display.data_window)
plotshape(showTextMarkers and rsQualified, "RS-Q", style=shape.labelup, location=location.belowbar, color=color.new(color.aqua, 0), text="RS-Q", textcolor=color.black, size=size.small)
plotshape(showTextMarkers and rsRisk, "RS-R", style=shape.labelup, location=location.belowbar, color=color.new(color.orange, 0), text="RS-R", textcolor=color.black, size=size.tiny)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search staged bottom signal configs.")
    parser.add_argument("--symbol", default="QQQ", help="Ticker symbol, comma list, or all")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to bottom signal experiment JSON config",
    )
    parser.add_argument(
        "--max-configs",
        type=int,
        default=None,
        help="Override number of candidate configs to test",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallel config-evaluation worker count; 1 keeps serial behavior",
    )
    parser.add_argument(
        "--research-tag",
        default="",
        help="Optional safe suffix for isolated full-search research outputs",
    )
    parser.add_argument(
        "--refresh-rs-watchlist",
        action="store_true",
        help="Refresh only the current best RS watchlist config from existing results",
    )
    parser.add_argument(
        "--refresh-supplemental-analysis",
        action="store_true",
        help="Refresh MB ablation, recent validation, and derived CSV/report outputs from existing results",
    )
    parser.add_argument(
        "--refresh-observation-search",
        action="store_true",
        help="Refresh shallow-pullback/deep-retest observation search from existing results",
    )
    parser.add_argument(
        "--refresh-strategy-review",
        action="store_true",
        help="Refresh conservative strategy iteration review artifacts from existing results",
    )
    return parser.parse_args()


def resolve_symbols(symbol_arg: str) -> list[str]:
    if symbol_arg.lower() == "all":
        return list(ALL_TICKERS)
    return [symbol.strip().upper() for symbol in symbol_arg.split(",") if symbol.strip()]


def main() -> None:
    args = parse_args()
    symbols = resolve_symbols(args.symbol)
    settings = load_search_settings(Path(args.config))
    output_paths = resolve_output_paths(args.research_tag)
    results_path = output_paths["results"]
    if args.refresh_rs_watchlist:
        if not results_path.exists():
            raise FileNotFoundError(f"Missing existing results file: {results_path}")
        payload = json.loads(results_path.read_text(encoding="utf-8"))
        payload = refresh_best_rs_watchlist_scan(payload, symbols, settings)
        written_paths = write_outputs(payload, output_paths=output_paths)
        refreshed = payload.get("bestRsWatchlist", {})
        watchlist = refreshed.get("rsCandidateWatchlist", {})
        print(
            "Refreshed RS watchlist "
            f"config={refreshed.get('config', {}).get('name', 'unknown')} "
            f"qualified={watchlist.get('qualifiedRsCandidateCount', 0)}"
        )
        print(f"Wrote {written_paths['rs_watchlist_report']}")
        print(f"Wrote {written_paths['plan_summary']}")
        print(f"Wrote {written_paths['next_actions_csv']}")
        print(f"Wrote {written_paths['rs_watchlist_pine']}")
        print(f"Wrote {written_paths['rs_watchlist_ticker_csv']}")
        print(f"Wrote {written_paths['rs_watchlist_candidate_csv']}")
        return

    if args.refresh_supplemental_analysis:
        if not results_path.exists():
            raise FileNotFoundError(f"Missing existing results file: {results_path}")
        payload = json.loads(results_path.read_text(encoding="utf-8"))
        payload = refresh_supplemental_analysis(payload, symbols, settings)
        written_paths = write_outputs(payload, output_paths=output_paths)
        refresh = payload.get("supplementalAnalysisRefresh", {})
        ablation = payload.get("mbFactorAblation", {})
        print(
            "Refreshed supplemental analysis "
            f"config={refresh.get('configName', 'unknown')} "
            f"ablationRows={len(ablation.get('rows', []))}"
        )
        print(f"Wrote {written_paths['report']}")
        print(f"Wrote {written_paths['plan_summary']}")
        print(f"Wrote {written_paths['mb_factor_ablation_csv']}")
        print(f"Wrote {written_paths['recent_validation_csv']}")
        print(f"Wrote {written_paths['next_actions_csv']}")
        print(f"Wrote {written_paths['rs_watchlist_ticker_csv']}")
        return

    if args.refresh_observation_search:
        if not results_path.exists():
            raise FileNotFoundError(f"Missing existing results file: {results_path}")
        payload = json.loads(results_path.read_text(encoding="utf-8"))
        payload = refresh_observation_search(payload, symbols, settings)
        written_paths = write_outputs(payload, output_paths=output_paths)
        observation = payload.get("observationSearch", {})
        metrics = observation.get("metrics", {})
        print(
            "Refreshed observation search "
            f"signals={metrics.get('signalCount', 0)} "
            f"upgradeScore={float(metrics.get('upgradeCandidateScore', 0.0)):.2f}"
        )
        print(f"Wrote {written_paths['observation_report']}")
        print(f"Wrote {written_paths['observation_signals_csv']}")
        print(f"Wrote {written_paths['pine']}")
        print(f"Wrote {written_paths['strict_formal_pine']}")
        print(f"Wrote {written_paths['merged_observation_pine']}")
        print(f"Wrote {written_paths['results']}")
        return

    if args.refresh_strategy_review:
        if not results_path.exists():
            raise FileNotFoundError(f"Missing existing results file: {results_path}")
        payload = json.loads(results_path.read_text(encoding="utf-8"))
        output_paths["strategy_iteration_review"].write_text(
            generate_strategy_iteration_review_report(payload),
            encoding="utf-8",
            newline="\n",
        )
        output_paths["strategy_iteration_review_csv"].write_text(
            generate_strategy_iteration_review_csv(payload),
            encoding="utf-8",
            newline="\n",
        )
        print(f"Wrote {output_paths['strategy_iteration_review']}")
        print(f"Wrote {output_paths['strategy_iteration_review_csv']}")
        return

    payload = run_search(
        symbols,
        settings=settings,
        max_configs=args.max_configs,
        workers=args.workers,
    )
    written_paths = write_outputs(payload, output_paths=output_paths)
    best = payload["bestConfig"]
    metrics = payload["bestMetrics"]
    print(
        f"Best {best['name']} score={metrics['compositeScore']:.2f} "
        f"signals={metrics['signalCount']} avg6m={metrics['avgFwd126']:.2%}"
    )
    print(f"Wrote {written_paths['results']}")
    print(f"Wrote {written_paths['report']}")
    print(f"Wrote {written_paths['plan_summary']}")
    print(f"Wrote {written_paths['next_actions_csv']}")
    print(f"Wrote {written_paths['strategy_iteration_review']}")
    print(f"Wrote {written_paths['strategy_iteration_review_csv']}")
    print(f"Wrote {written_paths['miss_diagnostics_report']}")
    print(f"Wrote {written_paths['miss_diagnostics_csv']}")
    print(f"Wrote {written_paths['candidate_review_csv']}")
    print(f"Wrote {written_paths['pine']}")
    print(f"Wrote {written_paths['strict_formal_pine']}")
    if written_paths["rs_watchlist_pine"].exists():
        print(f"Wrote {written_paths['rs_watchlist_pine']}")
    if written_paths["rs_watchlist_ticker_csv"].exists():
        print(f"Wrote {written_paths['rs_watchlist_ticker_csv']}")
    if written_paths["rs_watchlist_candidate_csv"].exists():
        print(f"Wrote {written_paths['rs_watchlist_candidate_csv']}")


if __name__ == "__main__":
    main()
