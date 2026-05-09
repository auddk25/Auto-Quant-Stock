# Auto-Quant Research Progress

## Branch: autoresearch/apr29

== Session: 2026-04-29 18:00 ==
## Completed
- Ran 38 autonomous experiments on DEV tickers (SPY, QQQ, AAPL, MSFT, JPM, WMT)
- Tested paradigms: SMA crossover, EMA + momentum, mean-reversion, breakout, buy-and-hold hybrids
- Established buy-and-hold baseline (905% avg return on 21 tickers) as optimization target
- Final best strategy: EMA_Mom (EMA 10/30 + 10-day momentum + 12% stop) — sharpe 2.76 on DEV
- Wrote detailed analysis report: `docs/analysis_report_apr29.md`
- Pushed all results to `origin/autoresearch/apr29`

## Pending
- None. Core finding established: buy-and-hold beats timing on absolute returns in 2019-2025 bull market

## Known Issues
- EMA_Mom fails VAL_CROSS validation (cross-sector generalization weak)
- Backtesting.py doesn't support trailing stops or position.entry_bar (caused 2 crashes)
- BuyHold strategy shows 0 trades (buy-on-first-bar semantics differ from active strategies)
==

## Key Finding
**Buy-and-hold beats all timing strategies on absolute returns (2019-2025 bull market).**

| Strategy | avg_return | sharpe | worst_dd |
|----------|-----------|--------|----------|
| BuyHold | 905.21% | 0.7284 | -84.6% |
| EMA_Mom | 341.04% | 0.6646 | -61.3% |

EMA_Mom provides 23% less drawdown (-61.3% vs -84.6%) but 63% lower returns.

## Best Strategy: EMA_Mom
- EMA 10/30 crossover + 10-day momentum filter + 12% stop-loss
- Works well on tech/indices, struggles on cross-sector
- Full details in `docs/analysis_report_apr29.md`

## Experiments Completed: 38
## Results: See `results.tsv` and `docs/analysis_report_apr29.md`

== Session: 2026-05-09 US Index auxiliary gates ==
## Completed
- Extended `investigations/us_index_zone_research.py` to report auxiliary valuation/sentiment gates for the Web app without modifying `run.py` or `config.py`.
- Verified current QQQ PE through yfinance/Yahoo as a current-only trailing PE snapshot; no reliable free historical QQQ PE series is used in backtest scoring.
- Kept the existing joint SPY/QQQ default parameters unchanged to avoid overfitting; auxiliary VIX/Fear/QQQ PE gates are fixed explanatory thresholds, not a new fitted grid.
- Regenerated `investigations/us_index_zone_results.json` and `investigations/us_index_zone_report.md`.

## Current Web thresholds
- QQQ PE warning: 38
- VIX panic/complacency: 30 / 14
- Fear & Greed extreme fear/greed: 20 / 80
==
