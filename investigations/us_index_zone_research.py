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

START_DATE = "2019-01-01"
CNN_FG_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2021-01-01"
SHILLER_URL = "https://posix4e.github.io/shiller_wrapper_data/data/stock_market_data.json"
TRAILING_PE_URL = "https://www.stockmarketperatio.com/js/historical-sp-500-pe-ratio-since-1990.js"
CURRENT_PE_URL = "https://www.stockmarketperatio.com"

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/121 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Origin": "https://www.cnn.com",
    "Referer": "https://www.cnn.com/markets/fear-and-greed",
}


@dataclass
class ResearchConfig:
    name: str
    fear_weight: float
    valuation_weight: float
    technical_weight: float
    repair_weight: float
    bottom_threshold: float
    heat_threshold: float
    conflict_gap: float


DEFAULT_CONFIG = ResearchConfig(
    name="balanced_zone_v1",
    fear_weight=0.35,
    valuation_weight=0.2,
    technical_weight=0.3,
    repair_weight=0.15,
    bottom_threshold=55,
    heat_threshold=55,
    conflict_gap=15,
)


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
        raise FileNotFoundError(f"Missing {path}; run uv run prepare.py first")
    df = pd.read_parquet(path).copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df.columns = [c.lower() for c in df.columns]
    return df


def fetch_yahoo(symbol: str, refresh: bool = False) -> pd.DataFrame:
    safe = symbol.replace("^", "")
    cache_path = CACHE_DIR / f"{safe}.parquet"
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
    price = load_local_price(symbol)
    vix = fetch_yahoo("^VIX", refresh)
    vix3m = fetch_yahoo("^VIX3M", refresh)
    skew = fetch_yahoo("^SKEW", refresh)
    fg = fetch_fear_greed(refresh)
    cape = fetch_shiller_cape(refresh)
    trailing_pe = fetch_trailing_pe(refresh)
    forward_pe = fetch_current_forward_pe(refresh)

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
    df["vix_pct"] = rolling_percentile(df["vix"])
    df["skew_pct"] = rolling_percentile(df["skew"])
    df["cape_pct"] = rolling_percentile(df["cape"], 1200)
    df["trailing_pe_pct"] = rolling_percentile(df["trailing_pe"], 1200)
    df["vix_curve"] = df["vix"] / df["vix3m"]
    df = df.dropna(subset=["sma200", "rsi14", "vix_pct"])

    meta = {
        "priceRows": int(len(price)),
        "start": df.index.min().date().isoformat() if len(df) else None,
        "end": df.index.max().date().isoformat() if len(df) else None,
        "cnnFearGreedRows": int(len(fg)),
        "capeRows": int(len(cape)),
        "trailingPeRows": int(len(trailing_pe)),
        "currentForwardPE": forward_pe,
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
            -out["ret20"] * 2,
            -out["dist_sma200"] * 2,
        ],
        axis=1,
    ).mean(axis=1)
    overbought = pd.concat(
        [
            (out["rsi14"] - 55) * 2,
            out["ret60"],
            out["dist_sma200"] * 1.5,
        ],
        axis=1,
    ).mean(axis=1)

    repair = pd.concat(
        [
            (out["close"] > out["ema20"]).astype(float) * 35,
            (out["ema20"] > out["ema50"]).astype(float) * 35,
            (out["ret20"] > 0).astype(float) * 30,
        ],
        axis=1,
    ).sum(axis=1)
    weakening = pd.concat(
        [
            (out["close"] < out["ema20"]).astype(float) * 35,
            (out["ema20"] < out["ema50"]).astype(float) * 35,
            (out["ret20"] < 0).astype(float) * 30,
        ],
        axis=1,
    ).sum(axis=1)

    out["bottom_score"] = clamp(
        cfg.fear_weight * clamp(fear_score)
        + cfg.valuation_weight * clamp(valuation_cheap)
        + cfg.technical_weight * clamp(oversold)
        + cfg.repair_weight * clamp(repair)
    )
    out["heat_score"] = clamp(
        cfg.fear_weight * clamp(greed_score)
        + cfg.valuation_weight * clamp(valuation_hot)
        + cfg.technical_weight * clamp(overbought)
        + cfg.repair_weight * clamp(weakening)
    )
    out["action"] = "hold"
    bottom_wins = (
        (out["bottom_score"] >= cfg.bottom_threshold)
        & ((out["bottom_score"] - out["heat_score"]) >= cfg.conflict_gap)
    )
    heat_wins = (
        (out["heat_score"] >= cfg.heat_threshold)
        & ((out["heat_score"] - out["bottom_score"]) >= cfg.conflict_gap)
    )
    out.loc[bottom_wins, "action"] = "dca_buy"
    out.loc[heat_wins, "action"] = "dca_sell"
    out["degree"] = 0
    active_score = out[["bottom_score", "heat_score"]].max(axis=1)
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
    equity = float(np.prod(1 + exposure[:-1] * daily[1:]))
    hold = float(df["close"].iloc[-1] / df["close"].iloc[0])
    return {
        "strategyReturnPct": (equity - 1) * 100,
        "buyHoldReturnPct": (hold - 1) * 100,
        "excessReturnPct": (equity - hold) * 100,
    }


def evaluate(df: pd.DataFrame, cfg: ResearchConfig) -> dict[str, Any]:
    scored = score_zones(df, cfg)
    transitions = scored["action"].ne(scored["action"].shift()).sum()
    bottom = scored["action"] == "dca_buy"
    heat = scored["action"] == "dca_sell"
    all_future_126 = future_return(scored["close"], 126)
    all_draw_63 = forward_drawdown(scored["close"], 63)
    bottom_return_126 = all_future_126[bottom].mean()
    heat_draw_63 = all_draw_63[heat].mean()
    ordinary_return_126 = all_future_126[~bottom].mean()
    ordinary_draw_63 = all_draw_63[~heat].mean()
    score = (
        (bottom_return_126 - ordinary_return_126) * 1.4
        + (ordinary_draw_63 - heat_draw_63) * 1.1
        - max(0, transitions - 80) * 0.1
        - max(0, 8 - transitions) * 2
    )
    return {
        "score": float(score) if np.isfinite(score) else -999,
        "bottomDays": int(bottom.sum()),
        "heatDays": int(heat.sum()),
        "transitions": int(transitions),
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
        "reference": reference_return(scored),
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
        "heatScore": round(float(row["heat_score"]), 2),
        "vix": round(float(row["vix"]), 2),
        "fearGreed": None if pd.isna(row["fear_greed"]) else round(float(row["fear_greed"]), 2),
        "cape": None if pd.isna(row["cape"]) else round(float(row["cape"]), 2),
        "trailingPE": None if pd.isna(row["trailing_pe"]) else round(float(row["trailing_pe"]), 2),
    }


def candidate_configs() -> list[ResearchConfig]:
    configs = [DEFAULT_CONFIG]
    for fear in [0.3, 0.4]:
        for valuation in [0.15, 0.25]:
            for tech in [0.25, 0.35]:
                repair = max(0.05, 1 - fear - valuation - tech)
                for threshold in [50, 55, 60]:
                    configs.append(
                        ResearchConfig(
                            name=f"f{fear:.2f}_v{valuation:.2f}_t{tech:.2f}_th{threshold}",
                            fear_weight=fear,
                            valuation_weight=valuation,
                            technical_weight=tech,
                            repair_weight=repair,
                            bottom_threshold=threshold,
                            heat_threshold=threshold,
                            conflict_gap=15,
                        )
                    )
    return configs


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
                f"- Price rows: {meta['priceRows']}",
                f"- Research window: {meta['start']} to {meta['end']}",
                f"- CNN Fear & Greed rows: {meta['cnnFearGreedRows']}",
                f"- Shiller CAPE rows: {meta['capeRows']}",
                f"- Trailing PE rows: {meta['trailingPeRows']}",
                f"- Current forward PE gate: {meta['currentForwardPE']}",
                "",
            ]
        )
    lines.extend(["## Best configs", ""])
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
                f"- Bottom days: {best['metrics']['bottomDays']}",
                f"- Heat days: {best['metrics']['heatDays']}",
                f"- Transitions: {best['metrics']['transitions']}",
                "",
            ]
        )
    (OUT_DIR / "us_index_zone_report.md").write_text("\n".join(lines), encoding="utf-8")


def run(symbols: list[str], refresh: bool) -> dict[str, Any]:
    output: dict[str, Any] = {"symbols": {}, "generatedAt": datetime.now().isoformat()}
    for symbol in symbols:
        df, meta = build_dataset(symbol, refresh)
        ranked = []
        for cfg in candidate_configs():
            metrics = evaluate(df, cfg)
            ranked.append({"config": asdict(cfg), "metrics": metrics})
        ranked.sort(key=lambda item: item["metrics"]["score"], reverse=True)
        output["symbols"][symbol] = {
            "dataMeta": meta,
            "best": ranked[0],
            "topConfigs": ranked[:5],
        }
    (OUT_DIR / "us_index_zone_results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
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
