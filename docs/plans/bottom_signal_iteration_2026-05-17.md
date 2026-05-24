# Bottom Signal Iteration Plan - 2026-05-17

## Objective

Build a repeatable bottom-signal research loop for U.S. stocks. The goal is to
find staged pullback or bottom-entry signals scored from 1 to 100, then generate
TradingView Pine only from the selected best Python configuration.

## Current Baseline

- Main script: `investigations/bottom_signal_search.py`
- Experiment config: `strategy_catalog/bottom_signal_formal/bottom_signal_config.json`
- Results: `strategy_catalog/bottom_signal_formal/bottom_signal_results.json`
- Report: `strategy_catalog/bottom_signal_formal/bottom_signal_report.md`
- Pine output: `strategy_catalog/bottom_signal_formal/bottom_signal_pine.pine`

## Iteration Rules

- Change experiment parameters in `bottom_signal_config.json`, not inside the
  Python dataclass unless adding a new field.
- `BottomSignalConfig` is the schema for one candidate, not the place to tune
  every experiment.
- Candidate periods, thresholds, weights, and stage-search settings come from
  JSON.
- Keep `config.py`, `prepare.py`, `run.py`, and `versions/` unchanged.

## Speed Plan

- Precompute all indicator columns needed by candidate configs once per ticker.
- Cache precomputed indicator parquet files under
  `investigations/.cache/bottom_signal_indicators/`.
- Use staged search by default:
  - test all configs on DEV symbols first;
  - promote the top configs;
  - run only promoted configs on the full ticker universe.
- Tune `promote_top_n` in `bottom_signal_config.json` when choosing between
  speed and exhaustive validation.
- Keep staged DEV selection relaxed. DEV uses only a small symbol subset, so
  full-universe hard gates are applied only during promoted full-market
  evaluation.

## Next Strategy Work

- Improve signal quality before expanding parameter count.
- Keep `Watch` as a visual radar label, but evaluate entry quality from the
  configured `entry` score threshold.
- Current best entry threshold is `75`; looser thresholds created too many
  lower-quality signals. After adding QQQ/SPY cross-validation coverage, the
  current stricter research baseline uses `entry=82`.
- Require enough QQQ/SPY and individual-stock samples before a config can win.
- Penalize configs that exceed the configured signal-count maximum.
- Require a broad-market drawdown context using QQQ/SPY before a signal is
  counted as an entry candidate. The current baseline uses a 126-bar market
  drawdown threshold of `-20%`.
- Search score weight profiles as strategy parameters. The current best profile
  emphasizes structure/retest more than the original balanced profile.
- Search minimum signal gap as a strategy parameter. The current best sparse
  baseline uses a 63-bar gap to reduce repeated entries during the same bear
  market leg.
- Penalize large 6m adverse drawdown tails so the strategy does not simply buy
  earlier and tolerate deep pain before the rebound.
- Add market-repair scoring as a soft preference. This favors signals after
  QQQ/SPY have started to lift from local lows, without making repair a hard
  filter that would destroy cross-validation sample size.
- Add date-split validation before accepting a winner. The current baseline
  treats signals after `2022-12-31` as a holdout segment and penalizes configs
  unless that segment includes both QQQ/SPY and individual-stock samples.
- Add validation-window coverage before accepting a winner. The current
  baseline requires enough signals across 2008-2010, 2020, 2022, and 2023+
  windows so a config cannot win by fitting only one crash regime.
- Add walk-forward diagnostics. Each fold selects a config using only earlier
  signals, then scores that selected config on a later test window. This is a
  diagnostic rather than a Pine default selector because recent low-frequency
  folds can have too few signals to be conclusive.
- Add bottom-capture quality. Each entry is evaluated against the local low in
  a configurable window around the signal. Configs with too many entries far
  from local lows are rejected so the selected strategy favors actual staged
  bottoms over generic pullbacks.
- Search entry score thresholds and enforce a hard signal-count cap. The
  current strict baseline rejects configs with more than 40 full-universe
  signals.
- Enforce minimum validation-window win rate. The current strict baseline
  requires every validation window to have at least a 50% 6-month win rate;
  raising that threshold currently removes all candidates.
- Treat exit scoring as auxiliary until bottom-entry quality is stronger.
