# Buy-the-Dip Indicator Search Report

Generated: 2026-05-12T17:51:58

## Method

Pure OHLCV-based indicators, grid-searched weights and thresholds.
No external data (VIX, CAPE, CNN F&G) — only price and volume.

Indicators:
- RSI(14) oversold score
- Bollinger Band (20,2) lower breakout score
- Price below SMA(200) score
- 252-day drawdown score
- Volume spike vs 20-day average score

Evaluation: forward returns (3/6/12m) after buy signals, win rate,
DCA return vs buy-and-hold, crash phase coverage.

## QQQ

- Data: yfinance-cache (2017-10-17 to 2026-05-08)
- Rows: 2151

### Best single-symbol config

- Config: `r0.20_b0.20_s0.20_d0.20_v0.20_t40`
- Score: 59.45
- Buy days: 8
- Avg 3m return: 22.62%
- Avg 6m return: 33.64%
- Avg 12m return: 47.11%
- Win rate (3m): 87.5%
- DCA return: 210.84%
- Buy & Hold: 404.52%
- Excess: -193.69%

Phase coverage:

- 2018_drawdown: 2 buy days / 70 total (2.9%)
- 2020_covid_crash: 1 buy days / 51 total (2.0%)
- 2022_bear: 2 buy days / 251 total (0.8%)
- 2024_2026_trend: 3 buy days / 590 total (0.5%)
- 2025_h2_pullback: 0 buy days / 128 total (0.0%)
- 2026_april_pullback: 0 buy days / 21 total (0.0%)

## SPY

- Data: yfinance-cache (2017-10-17 to 2026-05-08)
- Rows: 2151

### Best single-symbol config

- Config: `r0.20_b0.15_s0.25_d0.25_v0.15_t45`
- Score: 90.14
- Buy days: 6
- Avg 3m return: 28.88%
- Avg 6m return: 39.88%
- Avg 12m return: 58.91%
- Win rate (3m): 100.0%
- DCA return: 178.01%
- Buy & Hold: 229.72%
- Excess: -51.71%

Phase coverage:

- 2018_drawdown: 0 buy days / 70 total (0.0%)
- 2020_covid_crash: 4 buy days / 51 total (7.8%)
- 2022_bear: 0 buy days / 251 total (0.0%)
- 2024_2026_trend: 2 buy days / 590 total (0.3%)
- 2025_h2_pullback: 0 buy days / 128 total (0.0%)
- 2026_april_pullback: 0 buy days / 21 total (0.0%)

## Recommended joint config

- Config: `r0.20_b0.20_s0.20_d0.20_v0.20_t40`
- Combined score: 66.19
- Weights: RSI=0.20, BB=0.20, SMA200=0.20, DD=0.20, Vol=0.20
- Buy threshold: 40

Per-symbol results:

### QQQ

- Buy days: 8
- Avg 3m return: 22.62%
- Win rate (3m): 87.5%
- DCA return: 210.84%
- Buy & Hold: 404.52%
- Excess: -193.69%

### SPY

- Buy days: 12
- Avg 3m return: 19.81%
- Win rate (3m): 91.7%
- DCA return: 179.88%
- Buy & Hold: 229.72%
- Excess: -49.83%

## Per-symbol optimal configs

| Symbol | Config | Threshold | Buy Days | 3m Return | Win Rate | DCA % | Excess % |
|--------|--------|-----------|----------|-----------|----------|-------|----------|
| AAPL | `r0.20_b0.15_s0.25_d0.25_v0.15_t45` | 45 | 10 | 26.6% | 100% | 470.5% | -212.5% |
| AMD | `r0.25_b0.30_s0.10_d0.20_v0.15_t50` | 50 | 9 | 38.3% | 89% | 1611.5% | -1528.6% |
| AMZN | `r0.20_b0.15_s0.25_d0.25_v0.15_t50` | 50 | 61 | 16.8% | 97% | 176.3% | -256.8% |
| AVGO | `r0.30_b0.15_s0.20_d0.20_v0.15_t50` | 50 | 12 | 50.6% | 100% | 1970.4% | -180.5% |
| CAT | `r0.20_b0.15_s0.25_d0.25_v0.15_t50` | 50 | 18 | 29.1% | 100% | 734.4% | -19.9% |
| CRM | `r0.30_b0.25_s0.15_d0.20_v0.10_t45` | 45 | 72 | 4.0% | 40% | 1.1% | -85.2% |
| CRWD | `r0.20_b0.15_s0.25_d0.25_v0.15_t50` | 50 | 97 | 20.5% | 87% | 299.9% | -524.8% |
| JPM | `r0.20_b0.15_s0.25_d0.25_v0.15_t50` | 50 | 16 | 12.7% | 81% | 268.8% | -17.4% |
| LLY | `r0.25_b0.20_s0.15_d0.15_v0.25_t50` | 50 | 3 | 51.7% | 100% | 261.6% | -914.6% |
| META | `r0.30_b0.25_s0.15_d0.20_v0.10_t50` | 50 | 46 | 15.9% | 39% | 280.7% | 38.0% |
| MSFT | `r0.25_b0.30_s0.10_d0.20_v0.15_t35` | 35 | 23 | 15.5% | 56% | 62.0% | -420.4% |
| NVDA | `r0.25_b0.30_s0.10_d0.20_v0.15_t45` | 45 | 24 | 26.1% | 83% | 3954.5% | -437.4% |
| PLTR | `r0.25_b0.20_s0.15_d0.15_v0.25_t50` | 50 | 20 | 4.8% | 35% | 1126.5% | 586.0% |
| QQQ | `r0.20_b0.20_s0.20_d0.20_v0.20_t40` | 40 | 8 | 22.6% | 88% | 210.8% | -193.7% |
| SPY | `r0.20_b0.15_s0.25_d0.25_v0.15_t45` | 45 | 6 | 28.9% | 100% | 178.0% | -51.7% |
| TSLA | `r0.25_b0.30_s0.10_d0.20_v0.15_t50` | 50 | 27 | 33.4% | 85% | 1193.8% | -582.5% |
| TSM | `r0.25_b0.30_s0.10_d0.20_v0.15_t50` | 50 | 8 | 30.4% | 88% | 441.3% | -650.6% |
| UNH | `r0.20_b0.15_s0.25_d0.25_v0.15_t50` | 50 | 90 | 8.7% | 77% | 32.4% | -84.3% |
| V | `r0.20_b0.15_s0.25_d0.25_v0.15_t40` | 40 | 15 | 16.2% | 100% | 91.9% | -127.7% |
| WMT | `r0.30_b0.25_s0.15_d0.20_v0.10_t35` | 35 | 17 | 10.0% | 88% | 297.3% | -113.3% |
| XOM | `r0.20_b0.15_s0.25_d0.25_v0.15_t50` | 50 | 65 | 16.6% | 82% | 401.5% | 237.2% |

## TradingView Pine Script

See `buy_dip_pine.pine` — ready to paste into TradingView Pine Editor.
All weights and threshold are configurable via TradingView input panel.
