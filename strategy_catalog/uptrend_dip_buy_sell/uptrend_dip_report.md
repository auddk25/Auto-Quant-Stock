# Uptrend Dip Buy + Sell Signal Report

Generated: 2026-05-13T18:15:01

## Executive Summary

- Current broad long-term add-on default: `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` strategy=bottom_reversal.
- QQQ/SPY combined score: 96.86.
- Tech subset using this global default: avg 12m 54.8%, avg 12m drawdown -20.1%.
- Date-split 2023+ tech holdout, symbol-average: avg 12m 64.1%, avg 12m drawdown -12.2%.
- Date-split 2023+ tech holdout, signal-level: 35 signals, avg 12m 68.5%.
- Multi-window validation: 8 windows, min/median signal avg 12m 33.4% / 48.6%, worst signal 12m drawdown -30.4%.
- Latest tech signal in the generated log: CRM 2026-02-19 Deep Bottom - Strong.
- Research status: date-split, full-grid walk-forward, and multi-window validation are now present; production use still needs live paper-trading or future out-of-sample evidence.

## Current Strategy Card

- Primary use: long-term add-on buying for U.S. tech stocks, not short-term swing trading.
- Default signal family: `bottom_reversal`, which looks for deep drawdown, prior-low retest or multi-bottom behavior, RSI divergence, crash pressure, and capitulation volume.
- Entry rule: signal must pass the score threshold and close on a bearish candle, so it is not chasing a large green breakout day.
- Signal spacing: normal add-on signals are sparse and separated by about 63 trading bars.
- Strength labels: `Deep Bottom - Strong` is the preferred long-term add-on label; `Deep Bottom - Medium` is usable but weaker; `Watch` means the score barely qualifies.
- Separate index mode: `index_shallow_pullback` is for SPY/QQQ-style orderly pullbacks and should be read as `Shallow Pullback`, not as the same type of bottom signal.

## Method

Seven buy strategies (trend pullback / breakout / tech breakout / trend-filtered breakout / bottom reversal / RSI divergence / index shallow pullback), two sell strategies (reversal / overbought).
Grid-searched weights, thresholds, and stop-loss. Discrete buy-sell cycle simulation.

Buy A (Pullback): EMA stack trend + RSI sweet spot + Stochastic + volume contraction
Buy B (Breakout): Range compression + N-bar high breakout + volume surge + momentum
Buy C (Tech Breakout): Prior-high breakout + volatility contraction + relative strength vs SPY + volume expansion
Buy D (Trend Breakout): Breakout score adjusted by ADX trend strength and EMA55 slope
Buy E (Bottom Reversal): Large drawdown + prior-low retest/multi-bottom + RSI divergence + crash/capitulation
Buy F (RSI Divergence): Standalone RSI-divergence baseline with retest/drawdown context
Buy G (Index Shallow Pullback): Orderly index/ETF drawdown + EMA/SMA support + RSI reset + trend health
Sell A (Reversal): EMA breakdown + death cross + RSI break
Sell B (Overbought): RSI/Stoch overbought + Keltner upper + profit target

## Stage 1: Buy Config Search

### QQQ
- Best buy: `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` strategy=bottom_reversal
- Buy days: 35, 3m: 10.5%, win: 77%

### SPY
- Best buy: `btm_d0.20_b0.25_r0.20_c0.15_v0.20_t55` strategy=bottom_reversal
- Buy days: 6, 3m: 28.4%, win: 100%

## Long-Term Add-On Radar

This section scores buy signals as long-term add-on points, not as short trades.
Higher weight is given to 12-month and 24-month forward returns; drawdown is a penalty, and win rate is not the main target.

- Config: `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
- Strategy: bottom_reversal
- Combined score: 96.86
- Buy threshold: 45

Per-symbol radar results:

### QQQ
- Signals: 6
- Mature 12m signals: 6
- Avg 6m / 12m / 24m: 22.4% / 39.4% / 72.7%
- Avg max drawdown 6m / 12m: -6.4% / -7.0%

### SPY
- Signals: 3
- Mature 12m signals: 3
- Avg 6m / 12m / 24m: 13.4% / 26.6% / 54.3%
- Avg max drawdown 6m / 12m: -9.0% / -9.0%

## Add-On Signal Log: QQQ

| Date | Price | Score | Strength | Age Bars | 6m | 12m | 24m | 12m/Partial DD |
|------|-------|-------|----------|----------|----|-----|-----|----------------|
| 2020-03-12 | 170.89 | 53.6 | Deep Bottom - Medium | 1547 | 54.18 | 78.92 | 84.87 | -4.52 |
| 2022-03-07 | 316.37 | 47.0 | Deep Bottom - Medium | 1047 | -9.51 | -7.65 | 37.08 | -19.42 |
| 2022-06-10 | 281.64 | 56.0 | Deep Bottom - Strong | 980 | -1.99 | 26.73 | 67.43 | -9.48 |
| 2022-09-22 | 274.11 | 55.9 | Deep Bottom - Strong | 909 | 11.44 | 29.27 | 75.84 | -6.99 |
| 2022-12-27 | 258.59 | 58.7 | Deep Bottom - Strong | 843 | 38.43 | 57.12 | 98.14 | -1.32 |
| 2025-04-21 | 431.02 | 46.0 | Deep Bottom - Medium | 264 | 41.52 | 51.99 | - | 0.0 |

## Long-Term Radar Strategy Comparison

| Strategy | Config | Combined | QQQ Signals / 12m | SPY Signals / 12m |
|----------|--------|----------|-------------------|-------------------|
| bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | 96.86 | 6 / 39.4% | 3 / 26.6% |
| rsi_divergence | `rdiv_d0.55_b0.15_r0.10_c0.10_v0.10_t55` | 81.41 | 8 / 29.1% | 9 / 21.9% |
| trend_breakout | `tr_c0.15_b0.30_v0.20_m0.20_rs0.15_t40` | 66.06 | 11 / 28.1% | 6 / 21.0% |
| tech_breakout | `tb_c0.20_b0.20_v0.25_m0.15_rs0.20_t50` | 60.89 | 3 / 25.9% | 6 / 20.2% |
| breakout | `bo_c0.20_b0.20_v0.25_m0.20_rs0.15_t45` | 59.51 | 6 / 28.5% | 9 / 17.9% |
| pullback | `pb_d0.15_b0.30_r0.20_c0.15_v0.20_t55` | 57.15 | 22 / 20.1% | 22 / 13.3% |
| both | `both_t0.15_l0.30_r0.20_s0.15_v0.20_t55` | 57.15 | 22 / 20.1% | 22 / 13.3% |
| index_shallow_pullback | `idx_d0.15_b0.25_r0.20_c0.25_v0.15_t55` | 52.49 | 33 / 24.3% | 28 / 15.8% |

## Index Shallow Pullback Signal Log: SPY

| Date | Price | Score | Strength | Age Bars | 6m | 12m | 12m/Partial DD |
|------|-------|-------|----------|----------|----|-----|----------------|
| 2024-04-15 | 492.46 | 57.2 | Shallow Pullback - Medium | 518 | 16.56 | 5.53 | -1.84 |
| 2024-07-24 | 530.08 | 68.0 | Shallow Pullback - Strong | 449 | 13.05 | 19.15 | -7.4 |
| 2024-12-18 | 575.96 | 60.2 | Shallow Pullback - Strong | 346 | 4.47 | 18.58 | -14.78 |
| 2025-03-10 | 552.56 | 60.6 | Shallow Pullback - Medium | 293 | 16.7 | 22.07 | -11.17 |
| 2025-11-18 | 656.34 | 55.7 | Shallow Pullback - Medium | 117 | - | - | -3.71 |
| 2026-03-13 | 660.49 | 55.2 | Shallow Pullback - Medium | 39 | - | - | -4.32 |

## Stage 2: Recommended Buy+Sell Config

- Config: `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t50_s15_sl3`
- Strategy: bottom_reversal
- Combined score: 68.89
- Buy threshold: 50
- Sell threshold: 15
- Stop loss: 3%

Per-symbol results:

### QQQ
- Trades: 31
- Win rate: 61.3%
- Avg return: 0.87%
- Total return: 26.9%
- Profit factor: 2.07
- Sharpe: 3.95
- Max drawdown: -4.7%
- Avg hold: 1 days
- Buy & Hold: 404.5%
- Exits: 3 stop / 0 trailing / 28 signal

### SPY
- Trades: 10
- Win rate: 70.0%
- Avg return: 1.84%
- Total return: 18.4%
- Profit factor: 5.40
- Sharpe: 8.42
- Max drawdown: -2.6%
- Avg hold: 1 days
- Buy & Hold: 229.7%
- Exits: 0 stop / 0 trailing / 10 signal

## Trade Log: QQQ

| Entry | Exit | Return | Days | Exit |
|-------|------|--------|------|------|
| 2020-03-12 | 2020-03-13 | +8.5% | 1 | sell_signal |
| 2020-03-16 | 2020-03-17 | +7.6% | 1 | sell_signal |
| 2020-03-18 | 2020-03-19 | +0.6% | 1 | sell_signal |
| 2020-03-20 | 2020-03-23 | +0.1% | 1 | sell_signal |
| 2022-04-27 | 2022-04-28 | +3.5% | 1 | sell_signal |
| 2022-04-29 | 2022-05-02 | +1.7% | 1 | sell_signal |
| 2022-05-05 | 2022-05-06 | -1.2% | 1 | sell_signal |
| 2022-05-16 | 2022-05-17 | +2.6% | 1 | sell_signal |
| 2022-05-23 | 2022-05-24 | -2.1% | 1 | sell_signal |
| 2022-05-25 | 2022-05-26 | +2.8% | 1 | sell_signal |
| 2022-06-10 | 2022-06-13 | -4.7% | 1 | stop_loss |
| 2022-06-14 | 2022-06-15 | +2.5% | 1 | sell_signal |
| 2022-06-16 | 2022-06-17 | +1.2% | 1 | sell_signal |
| 2022-06-22 | 2022-06-23 | +1.5% | 1 | sell_signal |
| 2022-06-27 | 2022-06-28 | -3.0% | 1 | stop_loss |
| 2022-06-30 | 2022-07-01 | +0.7% | 1 | sell_signal |
| 2022-09-22 | 2022-09-23 | -1.6% | 1 | sell_signal |
| 2022-09-26 | 2022-09-27 | +0.0% | 1 | sell_signal |
| 2022-09-28 | 2022-09-29 | -2.9% | 1 | sell_signal |
| 2022-10-03 | 2022-10-04 | +3.1% | 1 | sell_signal |
| 2022-10-06 | 2022-10-07 | -3.8% | 1 | stop_loss |
| 2022-10-10 | 2022-10-11 | -1.4% | 1 | sell_signal |
| 2022-10-12 | 2022-10-13 | +2.4% | 1 | sell_signal |
| 2022-10-14 | 2022-10-17 | +3.3% | 1 | sell_signal |
| 2022-10-18 | 2022-10-19 | -0.4% | 1 | sell_signal |
| 2022-10-20 | 2022-10-27 | +1.4% | 5 | sell_signal |
| 2022-11-02 | 2022-11-03 | -1.9% | 1 | sell_signal |
| 2022-11-04 | 2022-11-07 | +1.1% | 1 | sell_signal |
| 2022-11-09 | 2022-11-10 | +7.4% | 1 | sell_signal |
| 2022-12-27 | 2022-12-28 | -1.3% | 1 | sell_signal |

## Per-Symbol Optimal Configs

| Symbol | Strategy | Config | Trades | Win% | Avg Ret | Sharpe | PF |
|--------|----------|--------|--------|------|---------|--------|----|
| AAPL | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s40_sl10` | 7 | 71% | 14.0% | 2.81 | 5.6 |
| AMD | bottom_reversal | `btm_d0.20_b0.25_r0.20_c0.15_v0.20_t55_s45_sl10` | 15 | 53% | 7.9% | 1.20 | 2.5 |
| AMZN | bottom_reversal | `btm_d0.20_b0.25_r0.20_c0.15_v0.20_t50_s40_sl10` | 16 | 81% | 8.8% | 2.82 | 5.1 |
| AVGO | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s15_sl7` | 11 | 91% | 7.1% | 5.43 | 10.0 |
| CAT | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s30_sl7` | 8 | 100% | 10.1% | 5.45 | 10.0 |
| CRM | tech_breakout | `tb_c0.15_b0.25_v0.20_m0.20_rs0.20_t50_s25_sl3` | 48 | 71% | 1.3% | 2.88 | 2.6 |
| CRWD | breakout | `bo_c0.15_b0.30_v0.20_m0.20_rs0.15_t55_s15_sl3` | 2 | 100% | 7.7% | 18.45 | 10.0 |
| JPM | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s15_sl10` | 12 | 92% | 5.9% | 4.18 | 10.0 |
| LLY | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s15_sl3` | 5 | 60% | 4.4% | 10.96 | 5.5 |
| META | trend_breakout | `tr_c0.25_b0.15_v0.20_m0.25_rs0.15_t50_s15_sl7` | 47 | 77% | 2.2% | 2.56 | 3.3 |
| MSFT | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s20_sl10` | 7 | 100% | 4.8% | 3.35 | 10.0 |
| NVDA | bottom_reversal | `btm_d0.20_b0.20_r0.35_c0.15_v0.10_t55_s35_sl15` | 9 | 67% | 1.6% | 0.33 | 1.2 |
| PLTR | breakout | `bo_c0.20_b0.20_v0.20_m0.20_rs0.20_t55_s45_sl5` | 10 | 80% | 6.5% | 4.70 | 4.1 |
| QQQ | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s15_sl7` | 6 | 100% | 5.0% | 3.03 | 10.0 |
| SPY | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t50_s15_sl3` | 10 | 70% | 2.0% | 10.09 | 5.8 |
| TSLA | trend_breakout | `tr_c0.15_b0.30_v0.20_m0.20_rs0.15_t55_s25_sl5` | 24 | 83% | 4.8% | 6.73 | 5.6 |
| TSM | trend_breakout | `tr_c0.25_b0.15_v0.20_m0.25_rs0.15_t55_s40_sl15` | 33 | 82% | 3.4% | 1.40 | 3.3 |
| UNH | breakout | `bo_c0.20_b0.20_v0.20_m0.20_rs0.20_t55_s15_sl3` | 6 | 100% | 1.9% | 19.77 | 10.0 |
| V | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s25_sl3` | 3 | 33% | 5.0% | 6.04 | 2.6 |
| WMT | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s15_sl3` | 4 | 100% | 2.3% | 17.08 | 10.0 |
| XOM | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55_s30_sl15` | 5 | 40% | -2.0% | -0.64 | 0.8 |

## Tech Stock Long-Term Radar Summary

### Global Default Applied To Tech Stocks

- Symbols covered: 12
- Avg signals: 8.5
- Avg 6m / 12m / 24m: 29.0% / 54.8% / 175.9%
- Median 12m: 51.3%
- Avg 12m max drawdown: -20.1%
- Strategy mix: bottom_reversal: 12

### Per-Symbol Best Tech Configs

- Symbols covered: 12
- Avg signals: 6.8
- Avg 6m / 12m / 24m: 40.2% / 102.0% / 249.4%
- Median 12m: 75.6%
- Avg 12m max drawdown: -14.7%
- Strategy mix: bottom_reversal: 6, breakout: 1, rsi_divergence: 2, tech_breakout: 1, trend_breakout: 2

### Tech Segment Summary

Large-cap quality tech separates steadier megacap names from the high-beta group, so the averages are not dominated by the most volatile stocks.

| Segment | Scope | Symbols | Avg Signals | Avg 12m | Median 12m | 12m DD |
|---------|-------|---------|-------------|---------|------------|--------|
| Large-cap quality tech | Global default | 7 | 7.4 | 39.4% | 30.0% | -17.7% |
| High-beta tech | Global default | 5 | 10.0 | 76.5% | 83.1% | -23.4% |
| Large-cap quality tech | Per-symbol best | 7 | 7.3 | 52.7% | 50.2% | -15.9% |
| High-beta tech | Per-symbol best | 5 | 6.2 | 171.0% | 110.1% | -13.1% |

### Recent Tech Signal Window

Signals dated 2023-01-01 or later. Recent windows have fewer mature 12m/24m observations.

| Scope | Signals | Mature 12m | Avg 6m | Avg 12m | Avg 24m | 12m DD |
|-------|---------|------------|--------|---------|---------|--------|
| Global default | 31 | 22 | 47.7% | 62.5% | 334.6% | -13.7% |
| Per-symbol best | 33 | 21 | 57.0% | 147.3% | 601.2% | -10.9% |

### Global Default Tech Signals By Year

| Year | Signals | Mature 12m | Avg 6m | Avg 12m | 12m DD |
|------|---------|------------|--------|---------|--------|
| 2023 | 3 | 3 | 101.9% | 114.4% | -4.3% |
| 2024 | 8 | 8 | 32.7% | 60.6% | -16.2% |
| 2025 | 14 | 11 | 44.5% | 49.8% | -15.9% |
| 2026 | 6 | 0 | - | - | -9.6% |

### Tech Signal Risk Diagnostics

Groups global-default tech signals dated 2023-01-01 or later by the signal's own risk tags. A signal with multiple risk tags appears in multiple risk rows.

| Risk Flag | Signals | Mature 12m | Avg 12m | 12m DD |
|-----------|---------|------------|---------|--------|
| no_risk_flags | 7 | 5 | 41.9% | -10.4% |
| no_volume_expansion | 10 | 8 | 69.6% | -19.7% |
| weak_bottom_retest | 12 | 9 | 86.2% | -10.9% |
| weak_rsi_divergence | 16 | 12 | 82.6% | -11.8% |

| Strength | Signals | Mature 12m | Avg 12m | 12m DD |
|----------|---------|------------|---------|--------|
| Deep Bottom - Medium | 22 | 15 | 64.5% | -14.2% |
| Deep Bottom - Strong | 9 | 7 | 58.4% | -12.2% |

### Latest Global-Default Tech Signals

| Symbol | Date | Price | Score | Strength | Action | Risk Flags | Drivers | Age Bars | 6m | 12m | 12m/Partial DD |
|--------|------|-------|-------|----------|--------|------------|---------|----------|----|-----|----------------|
| CRM | 2026-02-19 | 184.83 | 65.4 | Deep Bottom - Strong | Strong Add-On Candidate | no_volume_expansion | DD -42.5%; retest 100; RSI div 63; cap 6; RSI 25.8; vol 0.72x | 56 | - | - | -10.75 |
| AMZN | 2026-02-09 | 208.72 | 54.4 | Deep Bottom - Medium | Medium Add-On Candidate | - | DD -17.8%; retest 100; RSI div 60; cap 34; RSI 30.9; vol 1.68x | 63 | - | - | -4.76 |
| MSFT | 2026-02-05 | 392.77 | 47.7 | Deep Bottom - Medium | Medium Add-On Candidate | weak_bottom_retest | DD -27.2%; retest 40; RSI div 37; cap 38; RSI 29.1; vol 1.66x | 65 | - | - | -9.17 |
| CRWD | 2026-02-05 | 377.16 | 57.5 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence, weak_bottom_retest | DD -32.4%; retest 36; RSI div 13; cap 70; RSI 23.8; vol 2.00x | 65 | - | - | -7.13 |
| PLTR | 2026-01-30 | 146.59 | 52.9 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence | DD -29.2%; retest 63; RSI div 0; cap 62; RSI 14.3; vol 1.20x | 69 | - | - | -12.64 |
| META | 2026-01-20 | 603.60 | 48.5 | Deep Bottom - Medium | Medium Add-On Candidate | - | DD -23.4%; retest 90; RSI div 87; cap 22; RSI 26.1; vol 1.09x | 77 | - | - | -12.9 |
| CRM | 2025-11-17 | 236.06 | 60.1 | Deep Bottom - Strong | Strong Add-On Candidate | no_volume_expansion | DD -35.2%; retest 79; RSI div 100; cap 0; RSI 34.9; vol 0.77x | 119 | - | - | -30.12 |
| CRM | 2025-08-08 | 239.11 | 47.7 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence | DD -34.3%; retest 79; RSI div 23; cap 40; RSI 25.4; vol 1.45x | 189 | -19.05 | - | -31.01 |
| TSLA | 2025-06-05 | 284.70 | 49.0 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence, weak_bottom_retest | DD -40.7%; retest 40; RSI div 0; cap 75; RSI 29.5; vol 2.49x | 233 | 59.65 | - | 0.0 |
| AAPL | 2025-04-03 | 202.12 | 58.2 | Deep Bottom - Strong | Strong Add-On Candidate | - | DD -21.5%; retest 100; RSI div 100; cap 15; RSI 40.2; vol 1.88x | 276 | 27.3 | 25.3 | -15.14 |
| MSFT | 2025-04-03 | 370.28 | 45.9 | Deep Bottom - Medium | Medium Add-On Candidate | - | DD -19.7%; retest 100; RSI div 100; cap 2; RSI 36.1; vol 1.32x | 276 | 39.14 | 0.54 | -4.97 |
| AMZN | 2025-04-03 | 178.41 | 66.1 | Deep Bottom - Strong | Strong Add-On Candidate | - | DD -26.3%; retest 100; RSI div 100; cap 40; RSI 33.3; vol 1.98x | 276 | 23.04 | 19.82 | -6.22 |

### Current Tech Radar Watchlist

Global-default tech signals from the last 126 trading bars. These are recent enough to monitor, but 6m/12m outcomes may not be mature.

| Symbol | Date | Price | Score | Strength | Action | Risk Flags | Drivers | Age Bars | 6m | 12m | 12m/Partial DD |
|--------|------|-------|-------|----------|--------|------------|---------|----------|----|-----|----------------|
| CRM | 2026-02-19 | 184.83 | 65.4 | Deep Bottom - Strong | Strong Add-On Candidate | no_volume_expansion | DD -42.5%; retest 100; RSI div 63; cap 6; RSI 25.8; vol 0.72x | 56 | - | - | -10.75 |
| AMZN | 2026-02-09 | 208.72 | 54.4 | Deep Bottom - Medium | Medium Add-On Candidate | - | DD -17.8%; retest 100; RSI div 60; cap 34; RSI 30.9; vol 1.68x | 63 | - | - | -4.76 |
| MSFT | 2026-02-05 | 392.77 | 47.7 | Deep Bottom - Medium | Medium Add-On Candidate | weak_bottom_retest | DD -27.2%; retest 40; RSI div 37; cap 38; RSI 29.1; vol 1.66x | 65 | - | - | -9.17 |
| CRWD | 2026-02-05 | 377.16 | 57.5 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence, weak_bottom_retest | DD -32.4%; retest 36; RSI div 13; cap 70; RSI 23.8; vol 2.00x | 65 | - | - | -7.13 |
| PLTR | 2026-01-30 | 146.59 | 52.9 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence | DD -29.2%; retest 63; RSI div 0; cap 62; RSI 14.3; vol 1.20x | 69 | - | - | -12.64 |
| META | 2026-01-20 | 603.60 | 48.5 | Deep Bottom - Medium | Medium Add-On Candidate | - | DD -23.4%; retest 90; RSI div 87; cap 22; RSI 26.1; vol 1.09x | 77 | - | - | -12.9 |
| CRM | 2025-11-17 | 236.06 | 60.1 | Deep Bottom - Strong | Strong Add-On Candidate | no_volume_expansion | DD -35.2%; retest 79; RSI div 100; cap 0; RSI 34.9; vol 0.77x | 119 | - | - | -30.12 |

### Paper Tracking Plan

These are not completed returns. They are the calendar dates to revisit current radar signals for future 6m/12m evidence.

- Generated date: 2026-05-13
- Current signals tracked: 7
- Pending 6m checks: 7
- Pending 12m checks: 7
- Overdue pending 6m checks: 0
- Overdue pending 12m checks: 0
- Next pending check date: 2026-05-19
- Quick check command: `.venv\Scripts\python.exe investigations/uptrend_dip_search.py --paper-status --as-of YYYY-MM-DD`

| Symbol | Signal Date | Strength | Action | Risk Flags | 6m Check | 12m Check | 6m Status | 12m Status |
|--------|-------------|----------|--------|------------|----------|-----------|-----------|------------|
| CRM | 2026-02-19 | Deep Bottom - Strong | Strong Add-On Candidate | no_volume_expansion | 2026-08-21 | 2027-02-19 | pending | pending |
| AMZN | 2026-02-09 | Deep Bottom - Medium | Medium Add-On Candidate | - | 2026-08-11 | 2027-02-09 | pending | pending |
| MSFT | 2026-02-05 | Deep Bottom - Medium | Medium Add-On Candidate | weak_bottom_retest | 2026-08-07 | 2027-02-05 | pending | pending |
| CRWD | 2026-02-05 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence, weak_bottom_retest | 2026-08-07 | 2027-02-05 | pending | pending |
| PLTR | 2026-01-30 | Deep Bottom - Medium | Medium Add-On Candidate | weak_rsi_divergence | 2026-08-01 | 2027-01-30 | pending | pending |
| META | 2026-01-20 | Deep Bottom - Medium | Medium Add-On Candidate | - | 2026-07-22 | 2027-01-20 | pending | pending |
| CRM | 2025-11-17 | Deep Bottom - Strong | Strong Add-On Candidate | no_volume_expansion | 2026-05-19 | 2026-11-17 | pending | pending |

### Date-Split Diagnostic

Trains on QQQ/SPY signals dated up to 2022-12-31, then evaluates tech-stock signals dated 2023-01-01 or later.

- Trained config: `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` strategy=bottom_reversal
- Tech holdout symbols: 12
- Avg signals: 2.9
- Avg 6m / 12m / 24m: 55.3% / 64.1% / 223.4%
- Median 12m: 63.9%
- Avg 12m max drawdown: -12.2%
- Signal-level holdout: 35 signals, 26 mature 12m, avg 12m 68.5%, avg 12m drawdown -12.4%.
- Note: this is a signal-date split diagnostic, not a full rolling walk-forward test.

### Frozen Candidate Set Used For Validation

These configs are the frozen candidate set used by the restricted walk-forward diagnostic below.

| Reason | Strategy | Config | Combined |
|--------|----------|--------|----------|
| Broad default | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | 96.86 |
| Best trend-breakout family | trend_breakout | `tr_c0.15_b0.30_v0.20_m0.20_rs0.15_t40` | 66.06 |
| Best tech-breakout family | tech_breakout | `tb_c0.20_b0.20_v0.25_m0.15_rs0.20_t50` | 60.89 |
| Best RSI-divergence baseline | rsi_divergence | `rdiv_d0.55_b0.15_r0.10_c0.10_v0.10_t55` | 81.41 |
| Best index-shallow-pullback family | index_shallow_pullback | `idx_d0.15_b0.25_r0.20_c0.25_v0.15_t55` | 52.49 |

### Frozen Candidate 2023+ Tech Holdout Comparison

Symbol-average treats each ticker equally. Signal-level treats each signal equally, so active tickers can carry more weight.

| Reason | Strategy | Config | Symbols | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |
|--------|----------|--------|---------|---------|------------|----------------|----------------|---------------|
| Broad default | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | 12 | 35 | 26 | 64.1% | 68.5% | -12.4% |
| Best trend-breakout family | trend_breakout | `tr_c0.15_b0.30_v0.20_m0.20_rs0.15_t40` | 12 | 79 | 56 | 61.1% | 69.3% | -13.0% |
| Best tech-breakout family | tech_breakout | `tb_c0.20_b0.20_v0.25_m0.15_rs0.20_t50` | 12 | 67 | 49 | 70.7% | 79.8% | -12.7% |
| Best RSI-divergence baseline | rsi_divergence | `rdiv_d0.55_b0.15_r0.10_c0.10_v0.10_t55` | 12 | 30 | 21 | 49.6% | 58.1% | -12.8% |
| Best index-shallow-pullback family | index_shallow_pullback | `idx_d0.15_b0.25_r0.20_c0.25_v0.15_t55` | 12 | 171 | 127 | 63.6% | 71.1% | -12.5% |

### Restricted Walk-Forward Diagnostic

Each year selects only from the frozen candidate configs using prior QQQ/SPY signal history, then evaluates that selected config on tech-stock signals in the next calendar year.
This is more operationally conservative than the full-grid walk-forward because it only selects from a small predeclared candidate set.

| Year | Selected | Strategy | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |
|------|----------|----------|---------|------------|----------------|----------------|---------------|
| 2023 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 7 | 7 | 116.0% | 107.0% | -3.6% |
| 2024 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 8 | 8 | 53.0% | 60.6% | -16.2% |
| 2025 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 15 | 12 | 52.4% | 58.4% | -15.9% |
| 2026 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 7 | 0 | - | - | -11.5% |

### Full-Grid Walk-Forward Diagnostic

Each year reranks the full stage-1 grid using only prior QQQ/SPY signal history, then evaluates the selected config on tech-stock signals in the next calendar year.

| Year | Selected | Strategy | Train Score | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |
|------|----------|----------|-------------|---------|------------|----------------|----------------|---------------|
| 2023 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 95.40 | 7 | 7 | 116.0% | 107.0% | -3.6% |
| 2024 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 95.40 | 8 | 8 | 53.0% | 60.6% | -16.2% |
| 2025 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 95.40 | 15 | 12 | 52.4% | 58.4% | -15.9% |
| 2026 | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | bottom_reversal | 96.86 | 7 | 0 | - | - | -11.5% |

### Multi-Window Validation

This freezes the current broad default config and evaluates it across additional anchored and fixed holdout windows on the tech-stock subset.

- Windows: 8 total, 8 with mature 12m samples.
- Positive 12m windows: 8.
- Signal avg 12m, min / median / max: 33.4% / 48.6% / 82.2%.
- Worst signal 12m drawdown across windows: -30.4%.

Anchored windows:

| Start | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |
|-------|---------|------------|----------------|----------------|---------------|
| 2021-01-01 | 77 | 68 | 42.8% | 42.9% | -23.3% |
| 2022-01-01 | 71 | 62 | 43.3% | 42.4% | -24.2% |
| 2023-01-01 | 35 | 26 | 64.1% | 68.5% | -12.4% |
| 2024-01-01 | 28 | 19 | 50.8% | 54.4% | -14.7% |

Fixed rolling windows:

| Window | Signals | Mature 12m | Symbol Avg 12m | Signal Avg 12m | Signal 12m DD |
|--------|---------|------------|----------------|----------------|---------------|
| 2021-01-01 to 2022-12-31 | 46 | 46 | 32.7% | 33.4% | -29.7% |
| 2022-01-01 to 2023-12-31 | 43 | 43 | 37.1% | 37.1% | -30.4% |
| 2023-01-01 to 2024-12-31 | 15 | 15 | 91.7% | 82.2% | -10.3% |
| 2024-01-01 to 2025-12-31 | 22 | 19 | 55.4% | 54.4% | -16.1% |

### Current Interpretation

- Unified tech-stock add-on default: `bottom_reversal` remains the strongest broad strategy found so far.
- Per-symbol best configs show higher returns, but they are more likely to contain in-sample fitting because each ticker gets its own best setup.
- `index_shallow_pullback` is useful as a higher-frequency ETF/index pullback radar, but it is not the current return-maximizing default.
- Stage 2 trade simulation is a short-term buy/sell comparison; it should not be treated as the final sell rule for long-term investment add-ons.

### Validation Caveats

- The full-grid walk-forward table is the stricter validation view because each year reranks the whole stage-1 grid using only prior data.
- The restricted walk-forward table is more conservative operationally because it only selects from a small frozen candidate set.
- The multi-window table freezes the current broad default and checks whether the same config remains reasonable across additional anchored and fixed windows.
- The conservative read is the global default applied to tech stocks; the per-symbol best table is useful for research, but easier to overfit.
- Future validation should still add live paper-trading or a later out-of-sample period before treating the radar as production-grade.
- Signal quality should be judged by 12m/24m forward return and post-entry drawdown, not by short-term trade win rate.

### Prompt-To-Artifact Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Keep the main implementation inside investigations/uptrend_dip_search.py. | covered | All strategy families, radar evaluation, walk-forward diagnostics, report writing, and Pine generation are wired from investigations/uptrend_dip_search.py. |
| Do not modify config.py or run.py. | external gate | Session gate: git diff --name-only -- config.py run.py must stay empty. |
| Explore buy signals: volatility contraction breakout, relative strength, abnormal volume, and large-drawdown add-on points. | covered | tech_breakout covers compression / relative strength / volume expansion; bottom_reversal covers deep drawdown, multi-bottom/retest, RSI divergence, crash and capitulation; rsi_divergence is a standalone RSI-divergence baseline; index_shallow_pullback covers orderly index dips. |
| Explore trend filters with ADX and moving-average slope; keep Ichimoku as backup only. | covered | trend_breakout uses ADX and EMA55 slope. Ichimoku is intentionally not added to avoid unnecessary complexity before the simpler filters are validated. |
| Explore sell protection: trailing stop, ATR trailing, and profit drawdown protection. | covered | simulate_trades() includes fixed stop, profit drawdown trailing, ATR trailing, and sell-signal exits; Stage 2 report keeps this separate from the long-term add-on radar. |
| Optimize for long-term add-on quality, not high short-term win rate. | covered | Current default is bottom_reversal / btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45; long-term score weights 12m/24m forward returns and penalizes post-entry drawdown. |
| Avoid buying green momentum-chase bars for the long-term add-on radar. | covered | evaluate_long_term_radar() requires close < open for add-on entries, so long-term radar signals occur on bearish candles. |
| Support deep crashes, double bottoms / multi-bottoms, and RSI divergence. | covered | bottom_reversal scoring uses drawdown_252, bottom_retest_score, multi-bottom count, RSI divergence, crash score, and capitulation score. |
| Add index_shallow_pullback with strength labels distinct from bottom_reversal. | covered | Report and Pine emit Deep Bottom vs Shallow Pullback labels; index_shallow_pullback has its own threshold, weights, and re-signal rule. |
| Expand validation to the requested tech subset. | covered | Tech subset summary covers 12 symbols; current watchlist contains 7 recent global-default tech signals. |
| Run QQQ quick validation, then full --symbol all validation when it does not deteriorate. | external gate | Session gates: python investigations/uptrend_dip_search.py --symbol QQQ and python investigations/uptrend_dip_search.py --symbol all. |
| Reduce overfitting risk before treating the strategy as usable. | covered | Date-split holdout starts at 2023-01-01; full-grid walk-forward covers years [2023, 2024, 2025, 2026]; multi-window validation has 4 anchored windows and 4 rolling windows. |
| Keep TradingView Pine output synchronized and compatible with TradingView's function set. | covered | run() regenerates uptrend_dip_pine.pine and long_term_addon_radar.pine; Pine uses rolling_count() instead of unsupported rolling-sum function calls. |
| Provide user-facing artifacts for review. | covered | Generated artifacts: strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_report.md, strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_results.json, strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_pine.pine, strategy_catalog/long_term_addon_radar/long_term_addon_radar.pine, tests/test_uptrend_dip_search.py. |
| Do not claim production readiness from in-sample or proxy signals alone. | covered | Report caveats keep the conservative read separate from per-symbol in-sample best configs and call for live paper-trading or a later true out-of-sample period before production use. |
| Track future paper-validation checkpoints for current tech signals. | covered | paperTrackingPlan tracks 7 signals; next pending check date is 2026-05-19; overdue pending 6m/12m checks are 0 / 0. |

## Per-Symbol Long-Term Radar Configs

| Symbol | Strategy | Config | Signals | 6m | 12m | 24m | 12m DD |
|--------|----------|--------|---------|----|-----|-----|--------|
| AAPL | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` | 5 | 38.4% | 59.5% | 140.9% | -8.4% |
| AMD | tech_breakout | `tb_c0.20_b0.20_v0.25_m0.15_rs0.20_t55` | 7 | 31.9% | 86.3% | 177.0% | -14.6% |
| AMZN | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | 9 | 24.5% | 30.0% | 87.7% | -12.8% |
| AVGO | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` | 4 | 58.4% | 97.5% | 244.5% | -13.3% |
| CAT | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` | 5 | 43.9% | 87.4% | 95.9% | -6.5% |
| CRM | rsi_divergence | `rdiv_d0.50_b0.20_r0.15_c0.10_v0.05_t50` | 13 | 17.4% | 29.3% | 64.5% | -17.7% |
| CRWD | trend_breakout | `tr_c0.15_b0.30_v0.20_m0.20_rs0.15_t55` | 3 | 43.0% | 110.1% | 101.5% | -7.9% |
| JPM | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` | 4 | 19.9% | 42.8% | 71.1% | -9.4% |
| LLY | bottom_reversal | `btm_d0.25_b0.25_r0.25_c0.15_v0.10_t50` | 4 | 29.1% | 55.1% | 127.5% | -8.1% |
| META | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` | 6 | 10.3% | 50.2% | 132.3% | -29.6% |
| MSFT | bottom_reversal | `btm_d0.20_b0.25_r0.20_c0.15_v0.20_t40` | 9 | 25.0% | 37.8% | 91.3% | -11.5% |
| NVDA | rsi_divergence | `rdiv_d0.50_b0.20_r0.15_c0.10_v0.05_t30` | 8 | 55.4% | 108.8% | 406.1% | -17.6% |
| PLTR | breakout | `bo_c0.20_b0.20_v0.25_m0.20_rs0.15_t40` | 9 | 74.6% | 283.2% | 1019.8% | -8.5% |
| QQQ | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` | 4 | 27.8% | 50.9% | 84.3% | -4.5% |
| SPY | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45` | 3 | 13.4% | 26.6% | 54.3% | -9.0% |
| TSLA | trend_breakout | `tr_c0.15_b0.30_v0.20_m0.20_rs0.15_t55` | 4 | 73.8% | 266.4% | 394.0% | -17.1% |
| TSM | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t50` | 5 | 29.8% | 64.8% | 133.8% | -17.7% |
| UNH | bottom_reversal | `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55` | 5 | 9.0% | 20.1% | 93.1% | -16.4% |
| V | bottom_reversal | `btm_d0.20_b0.25_r0.20_c0.15_v0.20_t50` | 8 | 24.2% | 29.0% | 48.6% | -4.6% |
| WMT | trend_breakout | `tr_c0.25_b0.15_v0.20_m0.25_rs0.15_t55` | 5 | 9.3% | 24.9% | 79.3% | -5.7% |
| XOM | bottom_reversal | `btm_d0.20_b0.25_r0.20_c0.15_v0.20_t55` | 3 | 19.4% | 49.2% | 122.5% | -17.4% |

## TradingView Pine Script

Two Pine files are available, and they serve different purposes.

Recommended use:

- Use `long_term_addon_radar.pine` for the long-term add-on radar that matches this report's investment use case.
- Use `uptrend_dip_pine.pine` only when you want the fuller buy/sell comparison indicator with position-state and sell logic.
- Keep `Radar Mode = bottom_reversal` for rare deep-drawdown add-on signals.
- Switch `Radar Mode = index_shallow_pullback` for higher-frequency SPY/QQQ-style shallow pullback alerts; its standalone default threshold is 55.
- Treat `IDX WATCH/MED/STRONG` and `BTM WATCH/MED/STRONG` as different signal families, not as the same score scale.
