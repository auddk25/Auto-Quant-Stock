# US Index Zone Research Report

Generated: 2026-05-09T21:45:47

## Data availability

### SPY

- Price source: yfinance-cache (2017-01-03 to 2026-05-08)
- Price rows: 2350
- Research window: 2017-10-17 to 2026-05-08
- CNN Fear & Greed rows: 1342
- Shiller CAPE rows: 1740
- Trailing PE rows: 437
- Current forward PE gate: {'date': '2026-04-30', 'forwardPE': 24.98, 'trailingPE': 28.25, 'historyAvailable': False, 'usage': 'current_only_gate'}
- Current QQQ PE auxiliary gate: {'date': '2026-05-09', 'value': 34.694794, 'source': 'yfinance Yahoo Finance quoteSummary trailingPE for QQQ', 'methodology': 'current trailing PE snapshot for QQQ ETF; not a historical series', 'historyAvailable': False, 'usage': 'current_only_auxiliary_gate', 'threshold': 38, 'signal': 'neutral'}

### QQQ

- Price source: yfinance-cache (2017-01-03 to 2026-05-08)
- Price rows: 2350
- Research window: 2017-10-17 to 2026-05-08
- CNN Fear & Greed rows: 1342
- Shiller CAPE rows: 1740
- Trailing PE rows: 437
- Current forward PE gate: {'date': '2026-04-30', 'forwardPE': 24.98, 'trailingPE': 28.25, 'historyAvailable': False, 'usage': 'current_only_gate'}
- Current QQQ PE auxiliary gate: {'date': '2026-05-09', 'value': 34.694794, 'source': 'yfinance Yahoo Finance quoteSummary trailingPE for QQQ', 'methodology': 'current trailing PE snapshot for QQQ ETF; not a historical series', 'historyAvailable': False, 'usage': 'current_only_auxiliary_gate', 'threshold': 38, 'signal': 'neutral'}

## Auxiliary valuation and sentiment gates

These gates do not replace the panic bottom, pullback bottom, or heat model. They only adjust realtime interpretation, reason tags, and zone degree.

- QQQ PE warning: `38`. Source is the current yfinance/Yahoo trailing PE snapshot for QQQ. It is current-only because no stable free historical QQQ PE series was found in this workflow. It can reduce buy degree and increase sell confidence, but it must not fully block pullback bottom zones.
- VIX panic: `30`. Historical VIX is available from Yahoo, so this can add a `vix_panic` reason tag and strengthen panic-bottom buy zones.
- VIX complacency: `14`. Historical VIX is available from Yahoo, so this can add a `vix_complacency` reason tag and strengthen heat sell zones.
- Fear & Greed extreme fear: `20`. CNN history is available from 2021, so this can add a `fear_extreme` reason tag and strengthen panic-bottom buy zones where available.
- Fear & Greed extreme greed: `80`. CNN history is available from 2021, so this can add a `greed_extreme` reason tag and strengthen heat sell zones where available.

Limit: QQQ PE is not included in the parameter search objective or historical score columns. Treat it as a current valuation warning layer only.

## Recommended default

- Config: `f0.30_v0.15_t0.40_r0.15_b50_p50_pb34_h52_g5`
- Combined score: -42.03
- Web config: `{"name": "USIndexZoneResearchOpt", "fearWeight": 0.3, "valuationWeight": 0.15, "technicalWeight": 0.4, "repairWeight": 0.15, "bottomThreshold": 50, "panicBottomThreshold": 50, "pullbackBottomThreshold": 34, "heatThreshold": 52, "conflictGap": 5, "rsiPeriod": 14, "smaLongDays": 200, "emaFastDays": 20, "emaSlowDays": 50, "forwardPeLow": 18, "forwardPeHigh": 24, "qqqPeWarning": 38, "vixPanicThreshold": 30, "vixComplacencyThreshold": 14, "fearExtremeThreshold": 20, "greedExtremeThreshold": 80}`

Why this one:

- It is selected by joint SPY/QQQ ranking, not by one symbol only.
- The objective balances reference return, drawdown, zone coverage, transition count, and phase coverage.
- Bottom is split into panic bottom and pullback bottom, so expensive markets can still produce DCA zones after clear drawdowns.
- The objective explicitly penalizes missing pullback DCA zones in 2025 H2 and 2026-04 while keeping heat zones in the 2024-2026 rally.

Known limits:

- Scores use free public data and daily bars; they are zone hints, not exact trade signals.
- Forward PE has no reliable free history here, so it remains a current-only gate.
- The auxiliary gates are fixed, simple thresholds rather than a new fitted parameter grid. This is intentional to avoid overfitting VIX, Fear & Greed, or QQQ PE to a short recent sample.
- The selected main model is still the joint SPY/QQQ default, so one ticker or one market phase cannot dominate the Web defaults.
- 2026 coverage is limited to the available latest data date.

### Recommended default trigger coverage

#### SPY

- Strategy reference return: 178.43%
- Buy & Hold return: 229.72%
- Excess return: -51.29%
- Max drawdown: -32.91%
- Bottom days: 526
- Panic bottom days: 94
- Pullback bottom days: 432
- Heat days: 23
- Transitions: 147

- 2018_drawdown: bottom 51 days, panic 20 days, pullback 31 days, heat 0 days, max bottom 86.11, max heat 36.0
- 2020_covid_crash: bottom 48 days, panic 30 days, pullback 18 days, heat 0 days, max bottom 91.98, max heat 34.22
- 2022_bear: bottom 173 days, panic 21 days, pullback 152 days, heat 0 days, max bottom 79.4, max heat 46.89
- 2024_2026_trend: bottom 74 days, panic 11 days, pullback 63 days, heat 2 days, max bottom 83.06, max heat 53.9
- 2025_h2_pullback: bottom 3 days, panic 0 days, pullback 3 days, heat 0 days, max bottom 44.02, max heat 51.6
- 2026_april_pullback: bottom 1 days, panic 0 days, pullback 1 days, heat 0 days, max bottom 39.53, max heat 48.1

#### QQQ

- Strategy reference return: 314.98%
- Buy & Hold return: 404.52%
- Excess return: -89.55%
- Max drawdown: -32.28%
- Bottom days: 638
- Panic bottom days: 102
- Pullback bottom days: 536
- Heat days: 59
- Transitions: 167

- 2018_drawdown: bottom 55 days, panic 22 days, pullback 33 days, heat 0 days, max bottom 86.35, max heat 40.26
- 2020_covid_crash: bottom 48 days, panic 29 days, pullback 19 days, heat 0 days, max bottom 88.05, max heat 41.45
- 2022_bear: bottom 221 days, panic 31 days, pullback 190 days, heat 0 days, max bottom 84.12, max heat 47.6
- 2024_2026_trend: bottom 111 days, panic 11 days, pullback 100 days, heat 12 days, max bottom 83.98, max heat 56.69
- 2025_h2_pullback: bottom 5 days, panic 0 days, pullback 5 days, heat 4 days, max bottom 54.98, max heat 52.94
- 2026_april_pullback: bottom 4 days, panic 0 days, pullback 4 days, heat 0 days, max bottom 44.07, max heat 48.55

## Recommended config by symbol

### SPY

- Config: `f0.30_v0.15_t0.40_r0.15_b50_p50_pb34_h52_g5`
- Latest action: hold (0%)
- Bottom / Heat: 24.16 / 44.2
- Strategy reference return: 178.43%
- Buy & Hold return: 229.72%
- Excess return: -51.29%
- Max drawdown: -32.91%
- Bottom days: 526
- Panic bottom days: 94
- Pullback bottom days: 432
- Heat days: 23
- Transitions: 147

Phase coverage:

- 2018_drawdown: bottom 51 days, panic 20 days, pullback 31 days, heat 0 days, max bottom 86.11, max heat 36.0
- 2020_covid_crash: bottom 48 days, panic 30 days, pullback 18 days, heat 0 days, max bottom 91.98, max heat 34.22
- 2022_bear: bottom 173 days, panic 21 days, pullback 152 days, heat 0 days, max bottom 79.4, max heat 46.89
- 2024_2026_trend: bottom 74 days, panic 11 days, pullback 63 days, heat 2 days, max bottom 83.06, max heat 53.9
- 2025_h2_pullback: bottom 3 days, panic 0 days, pullback 3 days, heat 0 days, max bottom 44.02, max heat 51.6
- 2026_april_pullback: bottom 1 days, panic 0 days, pullback 1 days, heat 0 days, max bottom 39.53, max heat 48.1

### QQQ

- Config: `f0.30_v0.15_t0.40_r0.15_b50_p50_pb42_h52_g5`
- Latest action: hold (0%)
- Bottom / Heat: 24.16 / 51.38
- Strategy reference return: 307.64%
- Buy & Hold return: 404.52%
- Excess return: -96.88%
- Max drawdown: -32.65%
- Bottom days: 509
- Panic bottom days: 102
- Pullback bottom days: 407
- Heat days: 59
- Transitions: 151

Phase coverage:

- 2018_drawdown: bottom 51 days, panic 22 days, pullback 29 days, heat 0 days, max bottom 86.35, max heat 40.26
- 2020_covid_crash: bottom 46 days, panic 29 days, pullback 17 days, heat 0 days, max bottom 88.05, max heat 41.45
- 2022_bear: bottom 205 days, panic 31 days, pullback 174 days, heat 0 days, max bottom 84.12, max heat 47.6
- 2024_2026_trend: bottom 79 days, panic 11 days, pullback 68 days, heat 12 days, max bottom 83.98, max heat 56.69
- 2025_h2_pullback: bottom 3 days, panic 0 days, pullback 3 days, heat 4 days, max bottom 54.98, max heat 52.94
- 2026_april_pullback: bottom 2 days, panic 0 days, pullback 2 days, heat 0 days, max bottom 44.07, max heat 48.55
