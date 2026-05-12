# Uptrend Dip Buy + Sell Signal Report

Generated: 2026-05-12T21:01:40

## Method

Two buy strategies (trend pullback / breakout), two sell strategies (reversal / overbought).
Grid-searched weights, thresholds, and stop-loss. Discrete buy-sell cycle simulation.

Buy A (Pullback): EMA stack trend + RSI sweet spot + Stochastic + volume contraction
Buy B (Breakout): Range compression + N-bar high breakout + volume surge + momentum
Sell A (Reversal): EMA breakdown + death cross + RSI break
Sell B (Overbought): RSI/Stoch overbought + Keltner upper + profit target

## Stage 1: Buy Config Search

### QQQ
- Best buy: `bo_r0.20_s0.20_v0.25_m0.20_t0.15_t45` strategy=breakout
- Buy days: 15, 3m: 2.8%, win: 67%

### SPY
- Best buy: `bo_r0.15_s0.30_v0.20_m0.20_t0.15_t50` strategy=breakout
- Buy days: 5, 3m: -0.1%, win: 80%

## Stage 2: Recommended Buy+Sell Config

- Config: `bo_r0.20_s0.20_v0.25_m0.20_t0.15_t40_s45_sl15`
- Strategy: breakout
- Combined score: 63.04
- Buy threshold: 40
- Sell threshold: 45
- Stop loss: 15%

Per-symbol results:

### QQQ
- Trades: 9
- Win rate: 77.8%
- Avg return: 16.15%
- Total return: 145.3%
- Profit factor: 5.24
- Sharpe: 0.72
- Max drawdown: -25.2%
- Avg hold: 195 days
- Buy & Hold: 404.5%
- Exits: 2 stop / 7 signal

### SPY
- Trades: 7
- Win rate: 85.7%
- Avg return: 18.19%
- Total return: 127.3%
- Profit factor: 8.32
- Sharpe: 0.64
- Max drawdown: -24.5%
- Avg hold: 286 days
- Buy & Hold: 229.7%
- Exits: 1 stop / 6 signal

## Trade Log: QQQ

| Entry | Exit | Return | Days | Exit |
|-------|------|--------|------|------|
| 2017-10-27 | 2018-01-22 | +11.4% | 57 | sell_signal |
| 2018-01-23 | 2019-04-23 | +13.4% | 313 | sell_signal |
| 2019-05-07 | 2019-12-26 | +15.5% | 162 | sell_signal |
| 2020-01-02 | 2020-03-12 | -18.0% | 48 | stop_loss |
| 2020-07-14 | 2020-09-01 | +15.2% | 35 | sell_signal |
| 2020-09-02 | 2021-11-03 | +30.6% | 295 | sell_signal |
| 2022-01-10 | 2022-03-14 | -16.3% | 43 | stop_loss |
| 2023-02-02 | 2024-06-17 | +56.9% | 344 | sell_signal |
| 2024-06-21 | 2026-04-17 | +36.6% | 456 | sell_signal |

## Per-Symbol Optimal Configs

| Symbol | Strategy | Config | Trades | Win% | Avg Ret | Sharpe | PF |
|--------|----------|--------|--------|------|---------|--------|----|
| AAPL | breakout | `bo_r0.20_s0.20_v0.25_m0.20_t0.` | 10 | 90% | 5.0% | 4.13 | 9.3 |
| AMD | breakout | `bo_r0.25_s0.15_v0.20_m0.25_t0.` | 3 | 33% | 1023.0% | 0.94 | 10.0 |
| AMZN | breakout | `bo_r0.20_s0.20_v0.25_m0.20_t0.` | 9 | 67% | 1.8% | 4.95 | 10.0 |
| AVGO | pullback | `pb_t0.15_l0.30_r0.20_s0.15_v0.` | 7 | 14% | 207.0% | 0.88 | 10.0 |
| CAT | breakout | `bo_r0.25_s0.15_v0.20_m0.25_t0.` | 9 | 78% | 2.1% | 5.36 | 10.0 |
| CRM | breakout | `bo_r0.20_s0.20_v0.25_m0.20_t0.` | 37 | 84% | 2.7% | 1.87 | 10.0 |
| CRWD | breakout | `bo_r0.15_s0.30_v0.20_m0.20_t0.` | 2 | 100% | 7.7% | 18.45 | 10.0 |
| JPM | breakout | `bo_r0.20_s0.20_v0.25_m0.20_t0.` | 10 | 90% | 3.5% | 4.50 | 8.8 |
| LLY | breakout | `bo_r0.20_s0.20_v0.25_m0.20_t0.` | 14 | 93% | 19.5% | 0.94 | 10.0 |
| META | breakout | `bo_r0.20_s0.20_v0.25_m0.20_t0.` | 10 | 80% | 26.1% | 0.91 | 8.2 |
| MSFT | breakout | `bo_r0.25_s0.15_v0.20_m0.25_t0.` | 6 | 83% | 32.1% | 0.92 | 10.0 |
| NVDA | breakout | `bo_r0.20_s0.20_v0.20_m0.20_t0.` | 4 | 25% | 1095.0% | 1.15 | 10.0 |
| PLTR | breakout | `bo_r0.20_s0.20_v0.20_m0.20_t0.` | 10 | 80% | 6.5% | 4.70 | 4.1 |
| QQQ | pullback | `pb_t0.15_l0.30_r0.20_s0.15_v0.` | 11 | 73% | 20.3% | 0.94 | 5.4 |
| SPY | breakout | `bo_r0.20_s0.20_v0.25_m0.20_t0.` | 8 | 88% | 16.6% | 0.71 | 8.6 |
| TSLA | breakout | `bo_r0.10_s0.25_v0.15_m0.20_t0.` | 38 | 79% | 3.4% | 5.72 | 5.9 |
| TSM | breakout | `bo_r0.25_s0.15_v0.20_m0.25_t0.` | 5 | 20% | 170.0% | 0.78 | 10.0 |
| UNH | breakout | `bo_r0.20_s0.20_v0.20_m0.20_t0.` | 6 | 100% | 1.9% | 19.77 | 10.0 |
| V | breakout | `bo_r0.25_s0.15_v0.20_m0.25_t0.` | 7 | 71% | 0.6% | 8.36 | 8.8 |
| WMT | breakout | `bo_r0.20_s0.20_v0.20_m0.20_t0.` | 17 | 100% | 8.8% | 1.10 | 10.0 |
| XOM | breakout | `bo_r0.10_s0.25_v0.15_m0.20_t0.` | 7 | 86% | 19.2% | 0.65 | 8.8 |

## TradingView Pine Script

See `uptrend_dip_pine.pine` — ready to paste into TradingView Pine Editor.
