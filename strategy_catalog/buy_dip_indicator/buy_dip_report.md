# Buy-the-Dip Indicator Search Report

Generated: 2026-05-12T19:46:19

## Method

Pure OHLCV-based indicators, grid-searched weights and thresholds.
No external data (VIX, CAPE, CNN F&G) — only price and volume.

Indicators:
- RSI(14) oversold score
- Keltner Channel (EMA20 ± 2×ATR20) lower breakout score
- Price below SMA(200) score
- 252-day drawdown score
- ATR volatility ratio: ATR(14)/SMA(ATR(14),70) panic spike
- RSI + Stochastic(14) dual confirmation score
- EMA 21/55/100/200 trend filter (bear bonus, bull penalty)

Evaluation: forward returns (3/6/12m) after buy signals, win rate,
DCA return vs buy-and-hold, crash phase coverage.

## QQQ

- Data: yfinance-cache (2017-10-17 to 2026-05-08)
- Rows: 2151

### Best single-symbol config

- Config: `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50`
- Score: 42.72
- Buy days: 29
- Avg 3m return: 16.00%
- Avg 6m return: 24.26%
- Avg 12m return: 40.24%
- Win rate (3m): 65.5%
- DCA return: 206.72%
- Buy & Hold: 404.52%
- Excess: -197.80%

Phase coverage:

- 2018_drawdown: 2 buy days / 70 total (2.9%)
- 2020_covid_crash: 10 buy days / 51 total (19.6%)
- 2022_bear: 13 buy days / 251 total (5.2%)
- 2024_2026_trend: 4 buy days / 590 total (0.7%)
- 2025_h2_pullback: 0 buy days / 128 total (0.0%)
- 2026_april_pullback: 0 buy days / 21 total (0.0%)

## SPY

- Data: yfinance-cache (2017-10-17 to 2026-05-08)
- Rows: 2151

### Best single-symbol config

- Config: `r0.25_k0.10_s0.20_d0.15_a0.15_st0.15_t50`
- Score: 87.69
- Buy days: 23
- Avg 3m return: 18.52%
- Avg 6m return: 26.59%
- Avg 12m return: 42.86%
- Win rate (3m): 100.0%
- DCA return: 181.46%
- Buy & Hold: 229.72%
- Excess: -48.26%

Phase coverage:

- 2018_drawdown: 4 buy days / 70 total (5.7%)
- 2020_covid_crash: 11 buy days / 51 total (21.6%)
- 2022_bear: 6 buy days / 251 total (2.4%)
- 2024_2026_trend: 2 buy days / 590 total (0.3%)
- 2025_h2_pullback: 0 buy days / 128 total (0.0%)
- 2026_april_pullback: 0 buy days / 21 total (0.0%)

## Recommended joint config

- Config: `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50`
- Combined score: 56.05
- Weights: RSI=0.20, Keltner=0.15, SMA200=0.15, DD=0.10, ATR=0.25, Stoch=0.15
- Buy threshold: 50

Per-symbol results:

### QQQ

- Buy days: 29
- Avg 3m return: 16.00%
- Win rate (3m): 65.5%
- DCA return: 206.72%
- Buy & Hold: 404.52%
- Excess: -197.80%

### SPY

- Buy days: 33
- Avg 3m return: 15.61%
- Win rate (3m): 93.9%
- DCA return: 184.69%
- Buy & Hold: 229.72%
- Excess: -45.03%

## Per-symbol optimal configs

| Symbol | Config | Threshold | Buy Days | 3m Return | Win Rate | DCA % | Excess % |
|--------|--------|-----------|----------|-----------|----------|-------|----------|
| AAPL | `r0.20_k0.15_s0.15_d0.20_a0.15_st0.15_t50` | 50 | 41 | 17.4% | 85% | 357.2% | -325.8% |
| AMD | `r0.20_k0.20_s0.10_d0.10_a0.20_st0.20_t50` | 50 | 111 | 10.8% | 51% | 870.0% | -2270.0% |
| AMZN | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t45` | 45 | 80 | 13.1% | 74% | 148.6% | -284.6% |
| AVGO | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 30 | 33.3% | 100% | 1853.4% | -297.4% |
| CAT | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 50 | 20.7% | 88% | 703.8% | -50.5% |
| CRM | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 87 | 4.4% | 40% | 1.7% | -84.5% |
| CRWD | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 74 | 21.4% | 81% | 260.5% | -564.2% |
| JPM | `r0.15_k0.15_s0.25_d0.20_a0.10_st0.15_t50` | 50 | 85 | 8.9% | 72% | 224.8% | -61.4% |
| LLY | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 17 | 38.7% | 100% | 461.6% | -714.6% |
| META | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 90 | 12.7% | 43% | 261.1% | 18.4% |
| MSFT | `r0.20_k0.15_s0.15_d0.20_a0.15_st0.15_t50` | 50 | 59 | 8.1% | 56% | 62.5% | -420.0% |
| NVDA | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 84 | 11.4% | 69% | 3418.4% | -973.4% |
| PLTR | `r0.30_k0.25_s0.05_d0.10_a0.10_st0.20_t50` | 50 | 102 | 3.7% | 39% | 1023.0% | 482.4% |
| QQQ | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 29 | 16.0% | 66% | 206.7% | -197.8% |
| SPY | `r0.25_k0.10_s0.20_d0.15_a0.15_st0.15_t50` | 50 | 23 | 18.5% | 100% | 181.5% | -48.3% |
| TSLA | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 106 | 19.5% | 74% | 791.9% | -984.4% |
| TSM | `r0.20_k0.20_s0.10_d0.10_a0.20_st0.20_t50` | 50 | 86 | 13.1% | 73% | 606.5% | -485.4% |
| UNH | `r0.20_k0.20_s0.10_d0.10_a0.20_st0.20_t50` | 50 | 110 | 4.7% | 66% | 23.9% | -92.8% |
| V | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 18 | 20.1% | 100% | 104.2% | -115.4% |
| WMT | `r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` | 50 | 12 | 12.3% | 100% | 247.5% | -163.2% |
| XOM | `r0.25_k0.10_s0.20_d0.15_a0.15_st0.15_t50` | 50 | 100 | 9.2% | 71% | 301.2% | 136.9% |

## TradingView Pine Script

See `buy_dip_pine.pine` — ready to paste into TradingView Pine Editor.
All weights and threshold are configurable via TradingView input panel.
