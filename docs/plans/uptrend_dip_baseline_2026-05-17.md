# Uptrend Dip Baseline Archive - 2026-05-17

## Purpose

This is the short entry point for the completed uptrend-dip / long-term add-on
research baseline. Use this document before starting a new exploration branch
instead of rereading the full `claude-progress.md` history.

## Current Baseline

- Primary use: long-term add-on buying for U.S. tech stocks, not short-term swing trading.
- Current broad default: `bottom_reversal`.
- Current broad config: `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
- The signal looks for deep drawdown, prior-low retest or multi-bottom behavior,
  RSI divergence, crash pressure, and capitulation volume.
- Entry is intentionally conservative: it avoids chasing large green breakout days.

## Evidence Snapshot

- QQQ/SPY combined long-term radar score: `96.86`.
- QQQ radar: 6 signals, avg 6m `+22.4%`, avg 12m `+39.4%`, avg 24m `+72.7%`,
  avg 12m max drawdown `-7.0%`.
- SPY radar: 3 signals, avg 6m `+13.4%`, avg 12m `+26.6%`, avg 24m `+54.3%`,
  avg 12m max drawdown `-9.0%`.
- Tech subset using the global default: avg 12m `+54.8%`, avg 12m drawdown `-20.1%`.
- Date-split 2023+ tech holdout: symbol-average 12m `+64.1%`, signal-level 12m `+68.5%`.
- Multi-window validation: 8 windows; min/median signal avg 12m `+33.4%` / `+48.6%`.

## Current Limitations

- This is still research, not production trading logic.
- Future paper evidence is not mature yet.
- Do not judge the strategy by a single future signal.
- Do not add new filters from one paper-tracking result.
- Historical grid searches should not be repeated unless strategy logic changes or
  market data is intentionally refreshed.

## Paper Tracking

- Tracked current signals: 7.
- As of the latest lightweight audit, all 6m and 12m checks were pending.
- Next meaningful paper check date: `2026-05-19`.
- Lightweight status command:

```powershell
.venv\Scripts\python.exe investigations\uptrend_dip_search.py --paper-status --as-of YYYY-MM-DD
```

## Data And Tooling State

- Daily OHLCV data was refreshed locally for all configured tickers from
  `2008-01-01` through `2026-04-30`.
- Later-listed tickers begin at their first available trading history.
- Four-hour data is intentionally out of scope for now because yfinance intraday
  history does not reach back to 2019.
- Shared indicator wrapper added for future research: `quant_indicators.py`.
  It is parameterized: strategy or investigation code must pass the periods and
  indicator combinations to test instead of relying on fixed defaults like RSI 14
  or SMA 200.
- Installed indicator libraries:
  - `ta==0.11.0`
  - `pandas-ta-classic==0.5.44`

## Evidence Files

- Full report: `strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_report.md`
- Full results JSON: `strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_results.json`
- Research script: `investigations/uptrend_dip_search.py`
- TradingView Pine output: `strategy_catalog/uptrend_dip_buy_sell/uptrend_dip_pine.pine`
- Long-term radar Pine output: `strategy_catalog/long_term_addon_radar/long_term_addon_radar.pine`
- Tests: `tests/test_uptrend_dip_search.py`
- Indicator wrapper tests: `tests/test_quant_indicators.py`

## Next Exploration Guidance

- Start new research from this baseline document.
- Prefer new investigation scripts or new strategy files over further expanding
  `investigations/uptrend_dip_search.py`.
- Reuse `quant_indicators.py` for technical indicators, but pass candidate
  parameter sets from the experiment layer.
- Do not treat common periods such as `14` or `200` as fixed strategy truth;
  they are only candidate values to test.
- Keep `config.py`, `prepare.py`, and `run.py` as fixed evaluation-contract files
  unless the user explicitly changes the project contract.
