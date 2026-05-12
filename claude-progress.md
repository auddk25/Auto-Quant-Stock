# Auto-Quant Research Progress

## Branch: autoresearch/apr29

== Session: 2026-05-12 Buy-the-Dip Indicator v1 ==
## Completed
- Built `investigations/buy_dip_search.py` — pure OHLCV-based panic buy indicator grid search
- 5 indicators: RSI(14), BB(20,2) lower band, SMA200 distance, 252-day drawdown, volume ratio
- Grid search on QQQ+SPY, validation on all 21 tickers
- Best QQQ config: equal weights (0.20 each), threshold=40
  - 8 buy signals over 6 years, avg 3m return 22.6%, win rate 87.5%, avg 12m return 47%
- Generated `investigations/buy_dip_pine.pine` (TradingView Pine Script v5)
- Generated `investigations/buy_dip_report.md` and `buy_dip_results.json`
- Per-symbol optimal configs computed for all 21 tickers

## v1 Limitations
- No trend awareness — fires in both bull and bear markets equally
- BB (std-dev channel) less stable than Keltner (ATR channel) in trending markets
- RSI-only oversold, no dual confirmation with Stochastic
- Volume ratio as panic proxy, ATR spike would be better
- 2025 H2 and 2026 Apr pullbacks not captured (zero buy signals in those phases)

## v1 → v2: completed in next session
==

== Session: 2026-05-12 Buy-the-Dip Indicator v2 ==
## Completed
- Merged 4 new modules into `investigations/buy_dip_search.py`:
  1. **Keltner Channel** replaces BB: `EMA(20) ± 2*ATR(20)`, scored by distance from EMA20 in ATR units (`*30` scaling)
  2. **RSI + Stochastic dual confirmation**: `Stochastic(14)`, RSI<30 AND Stoch<20 = +20 bonus points
  3. **EMA trend filter**: EMA 21/55/100/200 alignment, additive modifier (-4 bull to +4 bear)
  4. **ATR volatility ratio** replaces volume: `ATR(14)/SMA(ATR(14),70)` > 1.5 = panic signal
- Updated `DipConfig` (6 weights: rsi, keltner, sma200, drawdown, atr, stoch)
- Updated `WEIGHT_SETS` (10 sets including oscillator-heavy variants)
- Updated `candidate_configs()` for 6-weight grid search
- Updated `generate_pine_script()` — TradingView Pine Script v5
- Updated `write_report()` with v2 indicator descriptions
- Regenerated `buy_dip_pine.pine`, `buy_dip_report.md`, `buy_dip_results.json`

## v2 Results vs v1
| Metric | v1 QQQ | v2 QQQ |
|--------|--------|--------|
| Buy signals | 8 | 29 |
| Avg 3m return | 22.6% | 16.0% |
| Win rate (3m) | 87.5% | 66% |
| Threshold | 40 | 50 |
| Weights | equal 0.20×5 | rsi=0.20 keltner=0.15 sma200=0.15 dd=0.10 atr=0.25 stoch=0.15 |

## Key Design Decisions
- **Keltner scoring**: Uses `(EMA20 - close) / ATR20 * 30` instead of band-edge distance. This gives meaningful scores even when price is near (but not below) the Keltner lower band.
- **Trend filter**: Additive modifier (-4 to +4) instead of multiplicative (0.7-1.3x). Multiplicative was too harsh — suppressed all bull-market signals below threshold.
- **2025 H2 / 2026 Apr**: Grid search does NOT select configs that catch these pullbacks. The pullbacks were too mild (8% drawdown, RSI 26.5 for 2025 H2, RSI 42.7 for 2026 Apr). Composite max was 37.1 for 2025 H2 — just above threshold=35, but threshold=35 produces 127 signals (too much noise). At threshold=50 (optimal), these phases have 0 signals.
- The v2 system is better at detecting real panics (2020 Covid: 10 signals vs v1's 8, 2022 bear: 13 vs v1's fewer) but correctly avoids firing on mild pullbacks.

## Modified Functions
- `build_indicators()`: Keltner, Stochastic(14), EMA 21/55/100/200, ATR ratio
- `score_buy_signals()`: 6 weighted components + EMA trend additive modifier
- `DipConfig`: 6 weight fields (w_rsi, w_keltner, w_sma200, w_drawdown, w_atr, w_stoch)
- `WEIGHT_SETS`: 10 weight combinations
- `candidate_configs()`: 6-weight unpacking, threshold 20-50
- `generate_pine_script()`: v2 indicators
- `write_report()`: v2 descriptions

## Not Modified
- `config.py`, `run.py`, `prepare.py` — untouched as specified

## Key Files
- `investigations/buy_dip_search.py` — v2 main script
- `investigations/buy_dip_pine.pine` — v2 Pine Script
- `investigations/buy_dip_report.md` — v2 search report
- `investigations/buy_dip_results.json` — v2 raw results
==

== Session: 2026-05-12 Uptrend Dip Buy+Sell Strategy (v2) ==
## Completed
- Built `investigations/uptrend_dip_search.py` — uptrend dip buy + sell signal grid search
- Two buy strategies: **trend pullback** (EMA stack + RSI sweet spot + Stoch + volume contraction) and **breakout** (range compression + N-bar high + volume surge + momentum)
- Two sell strategies: **trend reversal** (EMA breakdown + death cross + RSI break) and **overbought exit** (RSI/Stoch overbought + Keltner upper + profit target)
- Discrete trade simulation (buy→sell cycles, not DCA)
- Two-stage grid search: Stage 1 = buy config (forward returns), Stage 2 = sell config (trade simulation)
- Generated `uptrend_dip_report.md`, `uptrend_dip_results.json`, `uptrend_dip_pine.pine`

## Key Fixes Applied This Session
- **Sell overbought base lowered**: RSI-55 → RSI-45, Stoch-55 → RSI-45 (score_sell_overbought). Old base made sell signals nearly impossible to trigger.
- **Sell weight sets expanded**: 5 → 10 sets, including pure-overbought and pure-profit variants
- **Stage 2 scoring fixed**: Changed from avg_return to total_return as primary metric. Old scoring rewarded 1 huge trade over many good trades, causing grid search to converge on "never sell" configs.
- **Trade count penalty**: <5 trades = -30 per missing trade. Noise trade penalty for |return| < 3%.
- **Pine Script regenerated** by framework with optimized params.

## Recommended Config (QQQ+SPY combined)
- Strategy: **breakout** (buy_threshold=40, sell_threshold=45, stop_loss=15%)
- Breakout weights: range=0.20, signal=0.20, volume=0.25, momentum=0.20, trend=0.15

## Key Results
| Symbol | Trades | Win% | Avg Return | Total Return | Sharpe |
|--------|--------|------|------------|--------------|--------|
| QQQ | 9 | 78% | +16.2% | +145.3% | 0.72 |
| SPY | 7 | 86% | +18.2% | +127.3% | 0.64 |

## QQQ Trade Log
1. 2017-10-27 → 2018-01-22: +11.4% (57d, signal)
2. 2018-01-23 → 2019-04-23: +13.4% (313d, signal)
3. 2019-05-07 → 2019-12-26: +15.5% (162d, signal)
4. 2020-01-02 → 2020-03-12: -18.0% (48d, stop-loss)
5. 2020-07-14 → 2020-09-01: +15.2% (35d, signal)
6. 2020-09-02 → 2021-11-03: +30.6% (295d, signal)
7. 2022-01-10 → 2022-03-14: -16.3% (43d, stop-loss)
8. 2023-02-02 → 2024-06-17: +56.9% (344d, signal)
9. 2024-06-21 → 2026-04-17: +36.6% (456d, signal)

## Design Notes
- Breakout strategy selected over pullback by grid search (higher total return)
- 7 out of 9 exits are sell signals (not stop-loss) — sell logic is now working
- Buy & Hold still beats on absolute return (404% vs 145%) but strategy avoids 2022 bear market
- Per-symbol optimization: breakout dominates for individual stocks, pullback still competitive for indices

## Key Files
- `investigations/uptrend_dip_search.py` — main script (~1200 lines)
- `investigations/uptrend_dip_pine.pine` — TradingView Pine Script (auto-generated by framework)
- `investigations/uptrend_dip_report.md` — search report
- `investigations/uptrend_dip_results.json` — raw results
==
