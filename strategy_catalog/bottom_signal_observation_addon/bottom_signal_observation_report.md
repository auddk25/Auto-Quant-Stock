# Observation Channel Report

## Role
- Observation/candidate layer only. This does not change the formal MB strategy.
- Merged Pine: `bottom_signal_merged_observation.pine`
- Signal CSV: `bottom_signal_observation_signals.csv`

## Selected Observation Config
- Deep market max: -20.00%
- Shallow market band: -20.00% to -8.00%
- Deep bottom minimum: 66
- Shallow bottom minimum: 68
- Bottom maximum: 75
- Near-low window: 63
- Near-low max gap: 6.00%
- Cluster window: 42 bars

## Metrics
- Observation signals: 48
- Formal Strong baseline: 39
- Observation/Formal ratio: 1.23x
- Sparse target max: 78
- Avg 6m return: 19.10%
- 6m win rate: 72.34%
- Avg 6m adverse drawdown: -10.95%
- Duplicate formal signals: 0
- Upgrade candidate score: 80.52

## Anchor Coverage
- QQQ 2022-10-01 to 2022-12-31: Covered (3 signals)
- QQQ 2026-03-01 to 2026-03-31: Covered (1 signals)

## Anchor Signal Details
- QQQ 2022-10-03 OBS-D bottom=68 RS=38 risk=none
- QQQ 2022-10-11 OBS-D bottom=69 RS=40 risk=no_repair
- QQQ 2022-12-28 OBS-D bottom=68 RS=42 risk=no_repair
- QQQ 2026-03-27 OBS-S bottom=71 RS=40 risk=no_repair

## Top Signals
- AAPL 2016-05-04 OBS-S bottom=70 RS=42 marketDD=-8.23% nearLow=0.59% risk=no_repair
- AAPL 2019-01-07 OBS-S bottom=70 RS=39 marketDD=-14.95% nearLow=4.04% risk=none
- AAPL 2022-06-13 OBS-D bottom=75 RS=42 marketDD=-31.66% nearLow=0.00% risk=no_repair
- AAPL 2023-10-26 OBS-S bottom=75 RS=42 marketDD=-10.78% nearLow=0.00% risk=no_repair
- AMD 2008-07-01 OBS-S bottom=75 RS=42 marketDD=-10.54% nearLow=0.00% risk=no_repair
- AMD 2010-08-25 OBS-S bottom=75 RS=42 marketDD=-12.61% nearLow=2.34% risk=no_repair
- AMD 2012-07-25 OBS-S bottom=75 RS=42 marketDD=-8.16% nearLow=0.00% risk=trend_damage,no_repair
- AMD 2012-11-07 OBS-S bottom=74 RS=42 marketDD=-8.59% nearLow=0.00% risk=trend_damage,no_repair
- AMD 2021-03-04 OBS-S bottom=75 RS=42 marketDD=-9.62% nearLow=0.00% risk=no_repair
- AMD 2024-08-02 OBS-S bottom=75 RS=42 marketDD=-10.78% nearLow=0.00% risk=no_repair
- AMZN 2018-12-24 OBS-D bottom=75 RS=42 marketDD=-22.80% nearLow=0.00% risk=no_repair
- AVGO 2011-11-18 OBS-S bottom=74 RS=52 marketDD=-9.42% nearLow=2.36% risk=no_repair
- AVGO 2015-08-24 OBS-S bottom=75 RS=42 marketDD=-13.62% nearLow=0.00% risk=no_repair
- AVGO 2024-09-06 OBS-S bottom=70 RS=48 marketDD=-10.79% nearLow=0.54% risk=no_repair
- CAT 2009-02-19 OBS-D bottom=75 RS=42 marketDD=-39.25% nearLow=0.00% risk=no_repair
- CAT 2022-07-14 OBS-D bottom=73 RS=42 marketDD=-25.76% nearLow=0.00% risk=low_volume,no_repair
- JPM 2011-09-21 OBS-S bottom=75 RS=42 marketDD=-13.64% nearLow=0.00% risk=no_repair
- JPM 2018-10-11 OBS-S bottom=75 RS=49 marketDD=-9.02% nearLow=0.00% risk=no_repair
- JPM 2022-01-18 OBS-S bottom=75 RS=42 marketDD=-8.16% nearLow=0.00% risk=no_repair
- LLY 2008-09-17 OBS-D bottom=75 RS=48 marketDD=-20.40% nearLow=0.00% risk=no_repair
- LLY 2018-02-09 OBS-S bottom=74 RS=42 marketDD=-8.75% nearLow=2.72% risk=no_repair
- LLY 2020-10-30 OBS-S bottom=75 RS=42 marketDD=-11.03% nearLow=0.00% risk=no_repair
- MSFT 2010-05-07 OBS-S bottom=75 RS=42 marketDD=-10.11% nearLow=2.24% risk=no_repair
- MSFT 2020-03-12 OBS-D bottom=75 RS=44 marketDD=-26.67% nearLow=0.00% risk=no_repair
- MSFT 2023-01-05 OBS-D bottom=73 RS=47 marketDD=-21.13% nearLow=4.05% risk=no_repair

## Plain-English Read
- OBS-D means a deep market drawdown retest that is below formal MB strength.
- OBS-S means a shallower market pullback that is worth watching but not a formal bottom signal.
- Upgrade candidate score is evidence for future review, not an automatic promotion rule.
