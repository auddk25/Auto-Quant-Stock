# US Index Zone Research Report

Generated: 2026-05-09T16:35:02

## Data availability

### SPY

- Price source: yfinance-cache (2017-01-03 to 2026-05-08)
- Price rows: 2350
- Research window: 2017-10-17 to 2026-05-08
- CNN Fear & Greed rows: 1342
- Shiller CAPE rows: 1740
- Trailing PE rows: 437
- Current forward PE gate: {'date': '2026-04-30', 'forwardPE': 24.98, 'trailingPE': 28.25, 'historyAvailable': False, 'usage': 'current_only_gate'}

### QQQ

- Price source: yfinance-cache (2017-01-03 to 2026-05-08)
- Price rows: 2350
- Research window: 2017-10-17 to 2026-05-08
- CNN Fear & Greed rows: 1342
- Shiller CAPE rows: 1740
- Trailing PE rows: 437
- Current forward PE gate: {'date': '2026-04-30', 'forwardPE': 24.98, 'trailingPE': 28.25, 'historyAvailable': False, 'usage': 'current_only_gate'}

## Recommended default

- Config: `f0.45_v0.15_t0.30_r0.10_b46_h56_g15`
- Combined score: 41.94
- Web config: `{"name": "USIndexZoneResearchOpt", "fearWeight": 0.45, "valuationWeight": 0.15, "technicalWeight": 0.3, "repairWeight": 0.1, "bottomThreshold": 46, "heatThreshold": 56, "conflictGap": 15, "rsiPeriod": 14, "smaLongDays": 200, "emaFastDays": 20, "emaSlowDays": 50, "forwardPeLow": 18, "forwardPeHigh": 24}`

Why this one:

- It is selected by joint SPY/QQQ ranking, not by one symbol only.
- The objective balances reference return, drawdown, zone coverage, transition count, and phase coverage.
- It requires both Bottom/Heat score level and a score gap, so conflicted days remain hold.

Known limits:

- Scores use free public data and daily bars; they are zone hints, not exact trade signals.
- Forward PE has no reliable free history here, so it remains a current-only gate.
- 2026 coverage is limited to the available latest data date.

### Recommended default trigger coverage

#### SPY

- Strategy reference return: 140.30%
- Buy & Hold return: 229.72%
- Excess return: -89.42%
- Max drawdown: -32.91%
- Bottom days: 93
- Heat days: 190
- Transitions: 149

- 2018_drawdown: bottom 18 days, heat 0 days, max bottom 61.64, max heat 45.19
- 2020_covid_crash: bottom 29 days, heat 0 days, max bottom 62.08, max heat 40.13
- 2022_bear: bottom 17 days, heat 0 days, max bottom 51.9, max heat 55.18
- 2024_2026_trend: bottom 7 days, heat 67 days, max bottom 58.66, max heat 63.44

#### QQQ

- Strategy reference return: 274.56%
- Buy & Hold return: 404.52%
- Excess return: -129.96%
- Max drawdown: -27.32%
- Bottom days: 93
- Heat days: 220
- Transitions: 167

- 2018_drawdown: bottom 14 days, heat 0 days, max bottom 59.7, max heat 46.6
- 2020_covid_crash: bottom 29 days, heat 0 days, max bottom 60.18, max heat 45.55
- 2022_bear: bottom 25 days, heat 0 days, max bottom 52.8, max heat 54.98
- 2024_2026_trend: bottom 7 days, heat 85 days, max bottom 59.05, max heat 64.22

## Recommended config by symbol

### SPY

- Config: `f0.40_v0.20_t0.30_r0.10_b46_h56_g5`
- Latest action: hold (0%)
- Bottom / Heat: 22.21 / 53.37
- Strategy reference return: 155.02%
- Buy & Hold return: 229.72%
- Excess return: -74.69%
- Max drawdown: -31.80%
- Bottom days: 97
- Heat days: 178
- Transitions: 155

Phase coverage:

- 2018_drawdown: bottom 19 days, heat 0 days, max bottom 61.31, max heat 44.33
- 2020_covid_crash: bottom 27 days, heat 0 days, max bottom 59.96, max heat 39.96
- 2022_bear: bottom 24 days, heat 0 days, max bottom 53.98, max heat 55.01
- 2024_2026_trend: bottom 4 days, heat 67 days, max bottom 56.96, max heat 63.24

### QQQ

- Config: `f0.40_v0.15_t0.35_r0.10_b46_h56_g5`
- Latest action: dca_sell (75%)
- Bottom / Heat: 21.83 / 56.23
- Strategy reference return: 279.00%
- Buy & Hold return: 404.52%
- Excess return: -125.53%
- Max drawdown: -24.92%
- Bottom days: 55
- Heat days: 120
- Transitions: 112

Phase coverage:

- 2018_drawdown: bottom 11 days, heat 0 days, max bottom 57.94, max heat 44.24
- 2020_covid_crash: bottom 18 days, heat 0 days, max bottom 57.28, max heat 44.89
- 2022_bear: bottom 19 days, heat 0 days, max bottom 52.3, max heat 51.61
- 2024_2026_trend: bottom 3 days, heat 29 days, max bottom 56.8, max heat 62.58
