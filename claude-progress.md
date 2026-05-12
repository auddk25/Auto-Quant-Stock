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

## Pending: v2 Merge
Merge user's "综合交易信号系统" indicators into buy_dip_search.py:

1. **Keltner Channel 替代 BB**：`EMA(20) - 2*ATR(20)` 替代 `SMA(20) - 2*STD(20)`
2. **RSI + Stochastic 双重确认**：加 Stochastic(14)，RSI<30 且 Stoch<20 同时满足才计高分
3. **EMA 趋势过滤器**：EMA 21/55/100/200 四线排列，熊市超卖加分，牛市超卖减分
4. **ATR 波动预警替代成交量**：`ATR(14)/SMA(ATR(14),70)` > 1.5 = 恐慌放量

修改文件：`investigations/buy_dip_search.py`（build_indicators, score_buy_signals, DipConfig, candidate_configs, generate_pine_script）
不改：`config.py`, `run.py`, `prepare.py`

验证命令：`.venv/Scripts/python.exe investigations/buy_dip_search.py --symbol all`
对比 v1：QQQ 8 次信号 / 3m 回报 22.6% / 胜率 87.5%，看 v2 是否改善 2025 H2 和 2026 Apr 覆盖

## Key Files
- `investigations/buy_dip_search.py` — v1 主脚本，待升级
- `investigations/buy_dip_pine.pine` — v1 Pine Script，待重写
- `investigations/buy_dip_report.md` — v1 搜索报告
- `investigations/us_index_zone_research.py` — 参考模式（fetch_price, clamp, evaluate）
- `config.py` — ticker 列表（不要修改）
==
