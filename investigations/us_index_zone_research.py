"""
US index bottom/heat zone research.

This script intentionally does not modify run.py or config.py. It is a local
research helper for the us-stock-analyzer Web strategy:
- Historical indicators are used for score/search.
- Current-only indicators such as forward PE are reported as realtime gates only.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import urllib.request
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
CNN_FG_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2021-01-01"
SHILLER_URL = "https://posix4e.github.io/shiller_wrapper_data/data/stock_market_data.json"
TRAILING_PE_URL = "https://www.stockmarketperatio.com/js/historical-sp-500-pe-ratio-since-1990.js"
CURRENT_PE_URL = "https://www.stockmarketperatio.com"
QQQ_PE_WARNING = 38
VIX_PANIC_THRESHOLD = 30
VIX_COMPLACENCY_THRESHOLD = 14
FEAR_EXTREME_THRESHOLD = 20
GREED_EXTREME_THRESHOLD = 80

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/121 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Origin": "https://www.cnn.com",
    "Referer": "https://www.cnn.com/markets/fear-and-greed",
}


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


@dataclass
class ResearchConfig:
    name: str
    fear_weight: float
    valuation_weight: float
    technical_weight: float
    repair_weight: float
    bottom_threshold: float
    panic_bottom_threshold: float
    pullback_bottom_threshold: float
    heat_threshold: float
    conflict_gap: float

    def web_config(self) -> dict[str, float | str | int]:
        return {
            "name": "USIndexZoneResearchOpt",
            "fearWeight": self.fear_weight,
            "valuationWeight": self.valuation_weight,
            "technicalWeight": self.technical_weight,
            "repairWeight": self.repair_weight,
            "bottomThreshold": self.bottom_threshold,
            "panicBottomThreshold": self.panic_bottom_threshold,
            "pullbackBottomThreshold": self.pullback_bottom_threshold,
            "heatThreshold": self.heat_threshold,
            "conflictGap": self.conflict_gap,
            "rsiPeriod": 14,
            "smaLongDays": 200,
            "emaFastDays": 20,
            "emaSlowDays": 50,
            "forwardPeLow": 18,
            "forwardPeHigh": 24,
            "qqqPeWarning": QQQ_PE_WARNING,
            "vixPanicThreshold": VIX_PANIC_THRESHOLD,
            "vixComplacencyThreshold": VIX_COMPLACENCY_THRESHOLD,
            "fearExtremeThreshold": FEAR_EXTREME_THRESHOLD,
            "greedExtremeThreshold": GREED_EXTREME_THRESHOLD,
        }


DEFAULT_CONFIG = ResearchConfig(
    name="balanced_zone_v1",
    fear_weight=0.4,
    valuation_weight=0.15,
    technical_weight=0.35,
    repair_weight=0.1,
    bottom_threshold=60,
    panic_bottom_threshold=60,
    pullback_bottom_threshold=60,
    heat_threshold=60,
    conflict_gap=15,
)

MARKET_PHASES = {
    "2018_drawdown": ("2018-09-20", "2018-12-31"),
    "2020_covid_crash": ("2020-02-19", "2020-04-30"),
    "2022_bear": ("2022-01-03", "2022-12-30"),
    "2024_2026_trend": ("2024-01-01", "2026-12-31"),
    "2025_h2_pullback": ("2025-07-01", "2025-12-31"),
    "2026_april_pullback": ("2026-04-01", "2026-04-30"),
}


def fetch_text(url: str, cache_name: str, refresh: bool = False) -> str:
    cache_path = CACHE_DIR / cache_name
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    cache_path.write_text(text, encoding="utf-8")
    return text


def load_local_price(symbol: str) -> pd.DataFrame:
    path = DATA_DIR / f"{symbol}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path).copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df.columns = [c.lower() for c in df.columns]
    return df


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

    local = load_local_price(symbol)
    if local.empty:
        raise FileNotFoundError(f"Missing price data for {symbol}; yfinance and local parquet failed")
    return local, "local-parquet"


def fetch_yahoo(symbol: str, refresh: bool = False) -> pd.DataFrame:
    safe = symbol.replace("^", "")
    cache_path = CACHE_DIR / f"{safe}_{START_DATE}.parquet"
    if cache_path.exists() and not refresh:
        return pd.read_parquet(cache_path)
    end = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.download(symbol, start=START_DATE, end=end, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[["Close"]].dropna().rename(columns={"Close": safe.lower()})
    df.to_parquet(cache_path)
    return df


def fetch_fear_greed(refresh: bool = False) -> pd.DataFrame:
    text = fetch_text(CNN_FG_URL, "cnn_fear_greed.json", refresh)
    raw = json.loads(text)
    points = raw.get("fear_and_greed_historical", {}).get("data", [])
    rows = []
    for point in points:
        score = point.get("y")
        ts = point.get("x")
        if score is None or ts is None:
            continue
        date = datetime.fromtimestamp(float(ts) / 1000, tz=timezone.utc).date().isoformat()
        rows.append({"date": date, "fear_greed": float(score)})
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["fear_greed"])
    df["date"] = pd.to_datetime(df["date"])
    return df.drop_duplicates("date").set_index("date").sort_index()


def fetch_shiller_cape(refresh: bool = False) -> pd.DataFrame:
    text = fetch_text(SHILLER_URL, "shiller_stock_market_data.json", refresh)
    raw = json.loads(text)
    records = raw.get("data", raw)
    rows = [
        {"date": r.get("date_string"), "cape": r.get("cape")}
        for r in records
        if r.get("date_string") and r.get("cape")
    ]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["cape"] = pd.to_numeric(df["cape"], errors="coerce")
    return df.dropna().set_index("date").sort_index()


def fetch_trailing_pe(refresh: bool = False) -> pd.DataFrame:
    text = fetch_text(TRAILING_PE_URL, "trailing_pe_history.js", refresh)
    rows = []
    for year, month, day, value in re.findall(
        r"new Date\((\d{4}),(\d{1,2}),(\d{1,2})\),([\d.]+)", text
    ):
        rows.append(
            {
                "date": f"{int(year):04d}-{int(month):02d}-{int(day):02d}",
                "trailing_pe": float(value),
            }
        )
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.dropna().set_index("date").sort_index()


def fetch_current_forward_pe(refresh: bool = False) -> dict[str, Any]:
    text = fetch_text(CURRENT_PE_URL, "current_pe.html", refresh)
    forward = re.search(r'id="forwardPE"[^>]*>([^<]+)<', text)
    trailing = re.search(r'id="trailingPE"[^>]*>([^<]+)<', text)
    date = re.search(r"Data as of ([\d-]+)", text)
    return {
        "date": date.group(1) if date else None,
        "forwardPE": float(forward.group(1)) if forward else None,
        "trailingPE": float(trailing.group(1)) if trailing else None,
        "historyAvailable": False,
        "usage": "current_only_gate",
    }


def fetch_current_qqq_pe() -> dict[str, Any]:
    try:
        info = yf.Ticker("QQQ").get_info()
        value = info.get("trailingPE")
        numeric_value = float(value) if value is not None and math.isfinite(float(value)) else None
        return {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "value": numeric_value,
            "source": "yfinance Yahoo Finance quoteSummary trailingPE for QQQ",
            "methodology": "current trailing PE snapshot for QQQ ETF; not a historical series",
            "historyAvailable": False,
            "usage": "current_only_auxiliary_gate",
            "threshold": QQQ_PE_WARNING,
            "signal": "warning" if numeric_value is not None and numeric_value >= QQQ_PE_WARNING else "neutral",
        }
    except Exception as exc:
        return {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "value": None,
            "source": "yfinance Yahoo Finance quoteSummary trailingPE for QQQ",
            "methodology": "current trailing PE snapshot for QQQ ETF; not a historical series",
            "historyAvailable": False,
            "usage": "current_only_auxiliary_gate",
            "threshold": QQQ_PE_WARNING,
            "signal": "unavailable",
            "error": str(exc),
        }


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def rolling_percentile(series: pd.Series, window: int = 756) -> pd.Series:
    def pct(values: np.ndarray) -> float:
        current = values[-1]
        valid = values[~np.isnan(values)]
        if len(valid) < 30 or math.isnan(current):
            return np.nan
        return float((valid <= current).mean() * 100)

    return series.rolling(window, min_periods=126).apply(pct, raw=True)


def clamp(series: pd.Series | float, low: float = 0, high: float = 100):
    return np.minimum(high, np.maximum(low, series))


def build_dataset(symbol: str, refresh: bool = False) -> tuple[pd.DataFrame, dict[str, Any]]:
    price, price_source = fetch_price(symbol, refresh)
    vix = fetch_yahoo("^VIX", refresh)
    vix3m = fetch_yahoo("^VIX3M", refresh)
    skew = fetch_yahoo("^SKEW", refresh)
    fg = fetch_fear_greed(refresh)
    cape = fetch_shiller_cape(refresh)
    trailing_pe = fetch_trailing_pe(refresh)
    forward_pe = fetch_current_forward_pe(refresh)
    qqq_pe = fetch_current_qqq_pe()

    df = price.join([vix, vix3m, skew], how="left")
    df = df.join(fg, how="left")
    df = df.join(cape, how="left")
    df = df.join(trailing_pe, how="left")
    df[["vix", "vix3m", "skew", "fear_greed", "cape", "trailing_pe"]] = df[
        ["vix", "vix3m", "skew", "fear_greed", "cape", "trailing_pe"]
    ].ffill()

    close = df["close"]
    df["rsi14"] = rsi(close)
    df["sma50"] = close.rolling(50).mean()
    df["sma200"] = close.rolling(200).mean()
    df["ema20"] = close.ewm(span=20, adjust=False).mean()
    df["ema50"] = close.ewm(span=50, adjust=False).mean()
    df["ret20"] = close.pct_change(20) * 100
    df["ret60"] = close.pct_change(60) * 100
    df["dist_sma200"] = (close / df["sma200"] - 1) * 100
    df["drawdown63"] = (close / close.rolling(63).max() - 1) * 100
    df["drawdown126"] = (close / close.rolling(126).max() - 1) * 100
    df["vix_pct"] = rolling_percentile(df["vix"])
    df["skew_pct"] = rolling_percentile(df["skew"])
    df["cape_pct"] = rolling_percentile(df["cape"], 1200)
    df["trailing_pe_pct"] = rolling_percentile(df["trailing_pe"], 1200)
    df["vix_curve"] = df["vix"] / df["vix3m"]
    df = df.dropna(subset=["sma200", "rsi14", "vix_pct"])

    meta = {
        "priceRows": int(len(price)),
        "priceSource": price_source,
        "priceStart": price.index.min().date().isoformat() if len(price) else None,
        "priceEnd": price.index.max().date().isoformat() if len(price) else None,
        "start": df.index.min().date().isoformat() if len(df) else None,
        "end": df.index.max().date().isoformat() if len(df) else None,
        "cnnFearGreedRows": int(len(fg)),
        "capeRows": int(len(cape)),
        "trailingPeRows": int(len(trailing_pe)),
        "currentForwardPE": forward_pe,
        "currentQQQPE": qqq_pe,
    }
    return df, meta


def score_zones(df: pd.DataFrame, cfg: ResearchConfig) -> pd.DataFrame:
    out = df.copy()
    fg = out["fear_greed"]
    fear_score = pd.concat(
        [
            out["vix_pct"],
            (100 - fg).where(fg.notna(), out["vix_pct"]),
            ((out["vix_curve"] - 0.85) / 0.35 * 100),
            out["skew_pct"] * 0.7,
        ],
        axis=1,
    ).mean(axis=1)
    greed_score = pd.concat(
        [
            100 - out["vix_pct"],
            fg.where(fg.notna(), 100 - out["vix_pct"]),
            (100 - ((out["vix_curve"] - 0.85) / 0.35 * 100)),
        ],
        axis=1,
    ).mean(axis=1)

    valuation_cheap = pd.concat(
        [100 - out["cape_pct"], 100 - out["trailing_pe_pct"]], axis=1
    ).mean(axis=1)
    valuation_hot = pd.concat([out["cape_pct"], out["trailing_pe_pct"]], axis=1).mean(axis=1)

    oversold = pd.concat(
        [
            (50 - out["rsi14"]) * 2,
            -out["ret20"] * 3,
            -out["dist_sma200"] * 2,
        ],
        axis=1,
    ).mean(axis=1)
    overbought = pd.concat(
        [
            (out["rsi14"] - 55) * 2,
            out["ret60"] * 2,
            out["dist_sma200"] * 2,
        ],
        axis=1,
    ).mean(axis=1)

    repair = pd.concat(
        [
            (out["close"] > out["ema20"]).astype(float) * 100,
            (out["ema20"] > out["ema50"]).astype(float) * 100,
            (out["ret20"] > 0).astype(float) * 100,
        ],
        axis=1,
    ).mean(axis=1)
    weakening = pd.concat(
        [
            (out["close"] < out["ema20"]).astype(float) * 100,
            (out["ema20"] < out["ema50"]).astype(float) * 100,
            (out["ret20"] < 0).astype(float) * 100,
        ],
        axis=1,
    ).mean(axis=1)

    weighted_bottom = clamp(
        cfg.fear_weight * clamp(fear_score)
        + cfg.valuation_weight * clamp(valuation_cheap)
        + cfg.technical_weight * clamp(oversold)
        + cfg.repair_weight * clamp(repair)
    )
    out["panic_bottom_score"] = clamp(
        0.55 * clamp(fear_score)
        + 0.30 * clamp(oversold)
        + 0.15 * clamp(valuation_cheap)
    )
    pullback_drawdown = pd.concat(
        [-out["drawdown63"] * 10, -out["drawdown126"] * 8],
        axis=1,
    ).mean(axis=1)
    pullback_raw = (
        0.35 * clamp(pullback_drawdown)
        + 0.20 * clamp(-out["ret20"] * 5)
        + 0.20 * clamp((50 - out["rsi14"]) * 3)
        + 0.15 * clamp((100 - fg).where(fg.notna(), out["vix_pct"]))
        + 0.10 * clamp(-out["ret60"] * 3)
    )
    valuation_drag = np.maximum(0, clamp(valuation_hot) - 65) * 0.08
    out["pullback_bottom_score"] = clamp(pullback_raw - valuation_drag)
    out["bottom_score"] = pd.concat(
        [weighted_bottom, out["panic_bottom_score"], out["pullback_bottom_score"]],
        axis=1,
    ).max(axis=1)
    out["heat_score"] = clamp(
        cfg.fear_weight * clamp(greed_score)
        + cfg.valuation_weight * clamp(valuation_hot)
        + cfg.technical_weight * clamp(overbought)
        + cfg.repair_weight * clamp(weakening)
    )
    out["action"] = "hold"
    panic_wins = (
        (out["panic_bottom_score"] >= cfg.panic_bottom_threshold)
        | (
            (out["bottom_score"] >= cfg.bottom_threshold)
            & (out["panic_bottom_score"] >= out["pullback_bottom_score"])
        )
    )
    pullback_wins = out["pullback_bottom_score"] >= cfg.pullback_bottom_threshold
    heat_wins = (
        (out["heat_score"] >= cfg.heat_threshold)
        & ((out["heat_score"] - out["bottom_score"]) >= cfg.conflict_gap)
    )
    out.loc[panic_wins | pullback_wins, "action"] = "dca_buy"
    out.loc[heat_wins & ~(panic_wins | pullback_wins), "action"] = "dca_sell"
    out["bottom_kind"] = "none"
    out.loc[panic_wins, "bottom_kind"] = "panic_bottom"
    out.loc[pullback_wins & ~panic_wins, "bottom_kind"] = "pullback_bottom"
    out["degree"] = 0
    buy_score = out[["panic_bottom_score", "pullback_bottom_score", "bottom_score"]].max(axis=1)
    active_score = np.where(out["action"] == "dca_buy", buy_score, out["heat_score"])
    out.loc[active_score >= 25, "degree"] = 25
    out.loc[active_score >= 40, "degree"] = 50
    out.loc[active_score >= 55, "degree"] = 75
    out.loc[active_score >= 70, "degree"] = 100
    out.loc[out["action"] == "hold", "degree"] = 0
    return out


def future_return(close: pd.Series, days: int) -> pd.Series:
    return (close.shift(-days) / close - 1) * 100


def forward_drawdown(close: pd.Series, days: int) -> pd.Series:
    values = []
    arr = close.to_numpy()
    for i, current in enumerate(arr):
        future = arr[i + 1 : i + days + 1]
        if len(future) == 0 or current <= 0:
            values.append(np.nan)
        else:
            values.append((np.nanmin(future) / current - 1) * 100)
    return pd.Series(values, index=close.index)


def reference_return(df: pd.DataFrame) -> dict[str, float]:
    exposure = np.where(df["action"] == "dca_buy", 1.0, np.where(df["action"] == "dca_sell", 0.5, 0.75))
    daily = df["close"].pct_change().fillna(0).to_numpy()
    curve = np.cumprod(1 + exposure[:-1] * daily[1:])
    equity = float(curve[-1]) if len(curve) else 1.0
    hold = float(df["close"].iloc[-1] / df["close"].iloc[0])
    peak = np.maximum.accumulate(curve) if len(curve) else np.array([1.0])
    max_drawdown = float(np.min(curve / peak - 1) * 100) if len(curve) else 0.0
    return {
        "strategyReturnPct": (equity - 1) * 100,
        "buyHoldReturnPct": (hold - 1) * 100,
        "excessReturnPct": (equity - hold) * 100,
        "maxDrawdownPct": max_drawdown,
    }


def phase_summary(scored: pd.DataFrame) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for name, (start, end) in MARKET_PHASES.items():
        phase = scored.loc[start:end]
        if phase.empty:
            summary[name] = {"available": False}
            continue
        bottom = phase["action"] == "dca_buy"
        heat = phase["action"] == "dca_sell"
        panic_bottom = bottom & (phase["bottom_kind"] == "panic_bottom")
        pullback_bottom = bottom & (phase["bottom_kind"] == "pullback_bottom")
        summary[name] = {
            "available": True,
            "start": phase.index.min().date().isoformat(),
            "end": phase.index.max().date().isoformat(),
            "bottomDays": int(bottom.sum()),
            "panicBottomDays": int(panic_bottom.sum()),
            "pullbackBottomDays": int(pullback_bottom.sum()),
            "heatDays": int(heat.sum()),
            "bottomCoveragePct": round(float(bottom.mean() * 100), 2),
            "heatCoveragePct": round(float(heat.mean() * 100), 2),
            "maxBottomScore": round(float(phase["bottom_score"].max()), 2),
            "maxPanicBottomScore": round(float(phase["panic_bottom_score"].max()), 2),
            "maxPullbackBottomScore": round(float(phase["pullback_bottom_score"].max()), 2),
            "maxHeatScore": round(float(phase["heat_score"].max()), 2),
        }
    return summary


def target_penalty(value: float, low: float, high: float, scale: float) -> float:
    if value < low:
        return (low - value) * scale
    if value > high:
        return (value - high) * scale
    return 0.0


def coverage_score(phases: dict[str, dict[str, Any]]) -> float:
    score = 0.0
    for name in ["2018_drawdown", "2020_covid_crash", "2022_bear"]:
        phase = phases.get(name, {})
        if phase.get("available"):
            score += min(float(phase.get("bottomDays", 0)), 20) * 0.8
            score -= 16 if float(phase.get("bottomDays", 0)) == 0 else 0
    trend = phases.get("2024_2026_trend", {})
    if trend.get("available"):
        score += min(float(trend.get("bottomDays", 0)), 20) * 0.5
        score += min(float(trend.get("heatDays", 0)), 35) * 0.45
        score -= 10 if float(trend.get("heatDays", 0)) == 0 else 0
    h2_2025 = phases.get("2025_h2_pullback", {})
    if h2_2025.get("available"):
        pullback_days = float(h2_2025.get("pullbackBottomDays", 0))
        score += min(pullback_days, 18) * 1.2
        score -= 120 if pullback_days == 0 else 0
        score -= target_penalty(pullback_days, 3, 35, 0.8)
    apr_2026 = phases.get("2026_april_pullback", {})
    if apr_2026.get("available"):
        pullback_days = float(apr_2026.get("pullbackBottomDays", 0))
        score += min(pullback_days, 10) * 1.5
        score -= 180 if pullback_days == 0 else 0
        score -= target_penalty(pullback_days, 1, 18, 1.0)
    return score


def evaluate(df: pd.DataFrame, cfg: ResearchConfig) -> dict[str, Any]:
    scored = score_zones(df, cfg)
    transitions = scored["action"].ne(scored["action"].shift()).sum()
    bottom = scored["action"] == "dca_buy"
    panic_bottom = bottom & (scored["bottom_kind"] == "panic_bottom")
    pullback_bottom = bottom & (scored["bottom_kind"] == "pullback_bottom")
    heat = scored["action"] == "dca_sell"
    all_future_126 = future_return(scored["close"], 126)
    all_draw_63 = forward_drawdown(scored["close"], 63)
    bottom_return_126 = all_future_126[bottom].mean()
    heat_draw_63 = all_draw_63[heat].mean()
    ordinary_return_126 = all_future_126[~bottom].mean()
    ordinary_draw_63 = all_draw_63[~heat].mean()
    ref = reference_return(scored)
    phases = phase_summary(scored)
    score = (
        (bottom_return_126 - ordinary_return_126) * 1.4
        + (ordinary_draw_63 - heat_draw_63) * 1.1
        + min(ref["excessReturnPct"], 30) * 0.25
        + max(0, ref["maxDrawdownPct"] + 35) * 0.35
        + coverage_score(phases)
        - target_penalty(int(bottom.sum()), 12, 260, 0.25)
        - target_penalty(int(heat.sum()), 20, 420, 0.16)
        - target_penalty(int(transitions), 8, 140, 0.35)
    )
    return {
        "score": float(score) if np.isfinite(score) else -999,
        "bottomDays": int(bottom.sum()),
        "panicBottomDays": int(panic_bottom.sum()),
        "pullbackBottomDays": int(pullback_bottom.sum()),
        "heatDays": int(heat.sum()),
        "transitions": int(transitions),
        "phaseCoverage": phases,
        "futureReturns": {
            "bottom3mAvgPct": float(future_return(scored["close"], 63)[bottom].mean()),
            "bottom6mAvgPct": float(bottom_return_126),
            "bottom12mAvgPct": float(future_return(scored["close"], 252)[bottom].mean()),
        },
        "futureDrawdowns": {
            "heat1mAvgMaxDrawdownPct": float(forward_drawdown(scored["close"], 21)[heat].mean()),
            "heat3mAvgMaxDrawdownPct": float(heat_draw_63),
            "heat6mAvgMaxDrawdownPct": float(forward_drawdown(scored["close"], 126)[heat].mean()),
        },
        "reference": ref,
        "latest": latest_snapshot(scored),
    }


def latest_snapshot(scored: pd.DataFrame) -> dict[str, Any]:
    row = scored.iloc[-1]
    return {
        "date": scored.index[-1].date().isoformat(),
        "close": float(row["close"]),
        "action": row["action"],
        "degree": int(row["degree"]),
        "bottomScore": round(float(row["bottom_score"]), 2),
        "panicBottomScore": round(float(row["panic_bottom_score"]), 2),
        "pullbackBottomScore": round(float(row["pullback_bottom_score"]), 2),
        "heatScore": round(float(row["heat_score"]), 2),
        "bottomKind": row["bottom_kind"],
        "vix": round(float(row["vix"]), 2),
        "fearGreed": None if pd.isna(row["fear_greed"]) else round(float(row["fear_greed"]), 2),
        "cape": None if pd.isna(row["cape"]) else round(float(row["cape"]), 2),
        "trailingPE": None if pd.isna(row["trailing_pe"]) else round(float(row["trailing_pe"]), 2),
    }


def candidate_configs() -> list[ResearchConfig]:
    configs = [DEFAULT_CONFIG]
    weight_sets = [
        (0.35, 0.20, 0.30, 0.15),
        (0.40, 0.15, 0.35, 0.10),
        (0.45, 0.15, 0.30, 0.10),
        (0.30, 0.25, 0.30, 0.15),
        (0.30, 0.15, 0.40, 0.15),
        (0.35, 0.15, 0.35, 0.15),
        (0.40, 0.20, 0.30, 0.10),
    ]
    for fear, valuation, tech, repair in weight_sets:
        for bottom_threshold in [42, 46, 50]:
            for panic_bottom_threshold in [46, 50, 54]:
                for pullback_bottom_threshold in [34, 38, 42, 46]:
                    for heat_threshold in [52, 56, 60]:
                        for conflict_gap in [5, 10, 15]:
                            configs.append(
                                ResearchConfig(
                                    name=(
                                        f"f{fear:.2f}_v{valuation:.2f}_t{tech:.2f}_r{repair:.2f}_"
                                        f"b{bottom_threshold}_p{panic_bottom_threshold}_"
                                        f"pb{pullback_bottom_threshold}_h{heat_threshold}_g{conflict_gap}"
                                    ),
                                    fear_weight=fear,
                                    valuation_weight=valuation,
                                    technical_weight=tech,
                                    repair_weight=repair,
                                    bottom_threshold=bottom_threshold,
                                    panic_bottom_threshold=panic_bottom_threshold,
                                    pullback_bottom_threshold=pullback_bottom_threshold,
                                    heat_threshold=heat_threshold,
                                    conflict_gap=conflict_gap,
                                )
                        )
    unique: dict[tuple[float, float, float, float, float, float, float, float, float], ResearchConfig] = {}
    for cfg in configs:
        key = (
            cfg.fear_weight,
            cfg.valuation_weight,
            cfg.technical_weight,
            cfg.repair_weight,
            cfg.bottom_threshold,
            cfg.panic_bottom_threshold,
            cfg.pullback_bottom_threshold,
            cfg.heat_threshold,
            cfg.conflict_gap,
        )
        unique[key] = cfg
    return list(unique.values())


def combined_rank(
    configs: list[ResearchConfig],
    metrics_by_symbol: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    ranked = []
    for index, cfg in enumerate(configs):
        by_symbol = {
            symbol: metrics[index]
            for symbol, metrics in metrics_by_symbol.items()
        }
        scores = [payload["score"] for payload in by_symbol.values()]
        bottom_days = [payload["bottomDays"] for payload in by_symbol.values()]
        heat_days = [payload["heatDays"] for payload in by_symbol.values()]
        excess = [payload["reference"]["excessReturnPct"] for payload in by_symbol.values()]
        stability_penalty = (
            (max(scores) - min(scores)) * 0.18
            + abs(max(bottom_days) - min(bottom_days)) * 0.04
            + abs(max(heat_days) - min(heat_days)) * 0.025
            + abs(max(excess) - min(excess)) * 0.08
        )
        combined_score = float(np.mean(scores) - stability_penalty)
        ranked.append(
            {
                "config": asdict(cfg),
                "webConfig": cfg.web_config(),
                "combinedScore": combined_score,
                "symbols": by_symbol,
            }
        )
    ranked.sort(key=lambda item: item["combinedScore"], reverse=True)
    return ranked


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    return value


def write_report(results: dict[str, Any]) -> None:
    lines = [
        "# US Index Zone Research Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Data availability",
        "",
    ]
    for symbol, payload in results["symbols"].items():
        meta = payload["dataMeta"]
        lines.extend(
            [
                f"### {symbol}",
                "",
                f"- Price source: {meta['priceSource']} ({meta['priceStart']} to {meta['priceEnd']})",
                f"- Price rows: {meta['priceRows']}",
                f"- Research window: {meta['start']} to {meta['end']}",
                f"- CNN Fear & Greed rows: {meta['cnnFearGreedRows']}",
                f"- Shiller CAPE rows: {meta['capeRows']}",
                f"- Trailing PE rows: {meta['trailingPeRows']}",
                f"- Current forward PE gate: {meta['currentForwardPE']}",
                f"- Current QQQ PE auxiliary gate: {meta['currentQQQPE']}",
                "",
            ]
        )
    gates = results["auxiliaryGateDefaults"]
    lines.extend(
        [
            "## Auxiliary valuation and sentiment gates",
            "",
            "These gates do not replace the panic bottom, pullback bottom, or heat model. They only adjust realtime interpretation, reason tags, and zone degree.",
            "",
            f"- QQQ PE warning: `{gates['currentOnly']['qqqPeWarning']}`. Source is the current yfinance/Yahoo trailing PE snapshot for QQQ. It is current-only because no stable free historical QQQ PE series was found in this workflow. It can reduce buy degree and increase sell confidence, but it must not fully block pullback bottom zones.",
            f"- VIX panic: `{gates['historical']['vixPanicThreshold']}`. Historical VIX is available from Yahoo, so this can add a `vix_panic` reason tag and strengthen panic-bottom buy zones.",
            f"- VIX complacency: `{gates['historical']['vixComplacencyThreshold']}`. Historical VIX is available from Yahoo, so this can add a `vix_complacency` reason tag and strengthen heat sell zones.",
            f"- Fear & Greed extreme fear: `{gates['historical']['fearExtremeThreshold']}`. CNN history is available from 2021, so this can add a `fear_extreme` reason tag and strengthen panic-bottom buy zones where available.",
            f"- Fear & Greed extreme greed: `{gates['historical']['greedExtremeThreshold']}`. CNN history is available from 2021, so this can add a `greed_extreme` reason tag and strengthen heat sell zones where available.",
            "",
            "Limit: QQQ PE is not included in the parameter search objective or historical score columns. Treat it as a current valuation warning layer only.",
            "",
        ]
    )
    recommended = results["recommendedDefault"]
    lines.extend(
        [
            "## Recommended default",
            "",
            f"- Config: `{recommended['config']['name']}`",
            f"- Combined score: {recommended['combinedScore']:.2f}",
            f"- Web config: `{json.dumps(recommended['webConfig'], ensure_ascii=False)}`",
            "",
            "Why this one:",
            "",
            "- It is selected by joint SPY/QQQ ranking, not by one symbol only.",
            "- The objective balances reference return, drawdown, zone coverage, transition count, and phase coverage.",
            "- Bottom is split into panic bottom and pullback bottom, so expensive markets can still produce DCA zones after clear drawdowns.",
            "- The objective explicitly penalizes missing pullback DCA zones in 2025 H2 and 2026-04 while keeping heat zones in the 2024-2026 rally.",
            "",
            "Known limits:",
            "",
            "- Scores use free public data and daily bars; they are zone hints, not exact trade signals.",
            "- Forward PE has no reliable free history here, so it remains a current-only gate.",
            "- The auxiliary gates are fixed, simple thresholds rather than a new fitted parameter grid. This is intentional to avoid overfitting VIX, Fear & Greed, or QQQ PE to a short recent sample.",
            "- The selected main model is still the joint SPY/QQQ default, so one ticker or one market phase cannot dominate the Web defaults.",
            "- 2026 coverage is limited to the available latest data date.",
            "",
        ]
    )
    lines.extend(["### Recommended default trigger coverage", ""])
    for symbol, metrics in recommended["symbols"].items():
        ref = metrics["reference"]
        lines.extend(
            [
                f"#### {symbol}",
                "",
                f"- Strategy reference return: {ref['strategyReturnPct']:.2f}%",
                f"- Buy & Hold return: {ref['buyHoldReturnPct']:.2f}%",
                f"- Excess return: {ref['excessReturnPct']:.2f}%",
                f"- Max drawdown: {ref['maxDrawdownPct']:.2f}%",
                f"- Bottom days: {metrics['bottomDays']}",
                f"- Panic bottom days: {metrics['panicBottomDays']}",
                f"- Pullback bottom days: {metrics['pullbackBottomDays']}",
                f"- Heat days: {metrics['heatDays']}",
                f"- Transitions: {metrics['transitions']}",
                "",
            ]
        )
        for phase, phase_payload in metrics["phaseCoverage"].items():
            if not phase_payload.get("available"):
                lines.append(f"- {phase}: unavailable")
                continue
            lines.append(
                f"- {phase}: bottom {phase_payload['bottomDays']} days, "
                f"panic {phase_payload['panicBottomDays']} days, "
                f"pullback {phase_payload['pullbackBottomDays']} days, "
                f"heat {phase_payload['heatDays']} days, "
                f"max bottom {phase_payload['maxBottomScore']}, max heat {phase_payload['maxHeatScore']}"
            )
        lines.append("")
    lines.extend(["## Recommended config by symbol", ""])
    for symbol, payload in results["symbols"].items():
        best = payload["best"]
        latest = best["metrics"]["latest"]
        ref = best["metrics"]["reference"]
        lines.extend(
            [
                f"### {symbol}",
                "",
                f"- Config: `{best['config']['name']}`",
                f"- Latest action: {latest['action']} ({latest['degree']}%)",
                f"- Bottom / Heat: {latest['bottomScore']} / {latest['heatScore']}",
                f"- Strategy reference return: {ref['strategyReturnPct']:.2f}%",
                f"- Buy & Hold return: {ref['buyHoldReturnPct']:.2f}%",
                f"- Excess return: {ref['excessReturnPct']:.2f}%",
                f"- Max drawdown: {ref['maxDrawdownPct']:.2f}%",
                f"- Bottom days: {best['metrics']['bottomDays']}",
                f"- Panic bottom days: {best['metrics']['panicBottomDays']}",
                f"- Pullback bottom days: {best['metrics']['pullbackBottomDays']}",
                f"- Heat days: {best['metrics']['heatDays']}",
                f"- Transitions: {best['metrics']['transitions']}",
                "",
                "Phase coverage:",
                "",
            ]
        )
        for phase, phase_payload in best["metrics"]["phaseCoverage"].items():
            if not phase_payload.get("available"):
                lines.append(f"- {phase}: unavailable")
                continue
            lines.append(
                f"- {phase}: bottom {phase_payload['bottomDays']} days, "
                f"panic {phase_payload['panicBottomDays']} days, "
                f"pullback {phase_payload['pullbackBottomDays']} days, "
                f"heat {phase_payload['heatDays']} days, "
                f"max bottom {phase_payload['maxBottomScore']}, max heat {phase_payload['maxHeatScore']}"
            )
        lines.append("")
    write_text_lf(OUT_DIR / "us_index_zone_report.md", "\n".join(lines))


def run(symbols: list[str], refresh: bool) -> dict[str, Any]:
    output: dict[str, Any] = {"symbols": {}, "generatedAt": datetime.now().isoformat()}
    configs = candidate_configs()
    metas: dict[str, dict[str, Any]] = {}
    metrics_by_symbol: dict[str, list[dict[str, Any]]] = {}
    for symbol in symbols:
        df, meta = build_dataset(symbol, refresh)
        metas[symbol] = meta
        ranked = []
        for cfg in configs:
            metrics = evaluate(df, cfg)
            ranked.append({"config": asdict(cfg), "webConfig": cfg.web_config(), "metrics": metrics})
        metrics_by_symbol[symbol] = [item["metrics"] for item in ranked]
        ranked.sort(key=lambda item: item["metrics"]["score"], reverse=True)
        output["symbols"][symbol] = {
            "dataMeta": meta,
            "best": ranked[0],
            "topConfigs": ranked[:10],
        }
    combined = combined_rank(configs, metrics_by_symbol)
    output["searchSpace"] = {
        "configCount": len(configs),
        "symbols": symbols,
        "marketPhases": MARKET_PHASES,
        "objective": (
            "combined SPY/QQQ score using reference return, buy-and-hold comparison, "
            "max drawdown, zone count, split panic/pullback bottom coverage, "
            "2025 H2 / 2026-04 pullback requirements, heat coverage, transition count, and stability penalties"
        ),
    }
    output["auxiliaryGateDefaults"] = {
        "historical": {
            "vixPanicThreshold": VIX_PANIC_THRESHOLD,
            "vixComplacencyThreshold": VIX_COMPLACENCY_THRESHOLD,
            "fearExtremeThreshold": FEAR_EXTREME_THRESHOLD,
            "greedExtremeThreshold": GREED_EXTREME_THRESHOLD,
            "usage": "historical_reason_tags_and_degree_enhancers",
        },
        "currentOnly": {
            "qqqPeWarning": QQQ_PE_WARNING,
            "usage": "current_realtime_auxiliary_gate_only",
            "historicalScoring": False,
        },
    }
    output["recommendedDefault"] = combined[0]
    output["combinedTopConfigs"] = combined[:25]
    output = json_safe(output)
    write_text_lf(
        OUT_DIR / "us_index_zone_results.json",
        json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False),
    )
    write_report(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Research SPY/QQQ bottom and heat zones")
    parser.add_argument("--symbol", choices=["SPY", "QQQ", "all"], default="all")
    parser.add_argument("--refresh", action="store_true", help="Refresh HTTP/yfinance caches")
    args = parser.parse_args()
    symbols = ["SPY", "QQQ"] if args.symbol == "all" else [args.symbol]
    result = run(symbols, args.refresh)
    recommended = result["recommendedDefault"]
    print(
        f"Recommended: {recommended['config']['name']} combined={recommended['combinedScore']:.2f} "
        f"bottom={recommended['webConfig']['bottomThreshold']} "
        f"panic={recommended['webConfig']['panicBottomThreshold']} "
        f"pullback={recommended['webConfig']['pullbackBottomThreshold']} "
        f"heat={recommended['webConfig']['heatThreshold']} gap={recommended['webConfig']['conflictGap']}"
    )
    for symbol, payload in result["symbols"].items():
        latest = payload["best"]["metrics"]["latest"]
        print(
            f"{symbol}: {latest['date']} {latest['action']} {latest['degree']}% "
            f"bottom={latest['bottomScore']} heat={latest['heatScore']}"
        )
    print(f"Wrote {OUT_DIR / 'us_index_zone_results.json'}")
    print(f"Wrote {OUT_DIR / 'us_index_zone_report.md'}")


if __name__ == "__main__":
    main()
