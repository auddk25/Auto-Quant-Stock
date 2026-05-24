# Observation Channel Report

## Role
- Observation/candidate layer only. This does not change the formal MB strategy.
- Merged Pine: `bottom_signal_merged_observation.pine`
- Signal CSV: `bottom_signal_observation_signals.csv`

## Selected Observation Config
- Deep market max: -20.00%
- Shallow market band: -20.00% to -8.00%
- Deep bottom minimum: 64
- Shallow bottom minimum: 68
- Bottom maximum: 75
- Near-low window: 63
- Near-low max gap: 8.00%
- Cluster window: 42 bars

## Metrics
- Observation signals: 49
- Formal Strong baseline: 124
- Observation/Formal ratio: 0.40x
- Sparse target max: 248
- Avg 6m return: 25.98%
- 6m win rate: 77.08%
- Avg 6m adverse drawdown: -11.57%
- Duplicate formal signals: 0
- Upgrade candidate score: 83.30

## Anchor Coverage
- QQQ 2022-10-01 to 2022-12-31: Covered (3 signals)
- QQQ 2026-03-01 to 2026-03-31: Covered (1 signals)

## Anchor Signal Details
- QQQ 2022-10-11 OBS-D bottom=71 RS=56 risk=no_repair
- QQQ 2022-11-03 OBS-D bottom=64 RS=56 risk=no_repair
- QQQ 2022-12-28 OBS-D bottom=70 RS=43 risk=no_repair
- QQQ 2026-03-30 OBS-S bottom=72 RS=51 risk=no_repair

## Top Signals
- AAPL 2008-09-29 OBS-D bottom=75 RS=42 marketDD=-25.08% nearLow=0.00% risk=no_repair
- AAPL 2016-05-05 OBS-S bottom=74 RS=43 marketDD=-8.26% nearLow=0.18% risk=low_volume,no_repair
- AAPL 2018-12-24 OBS-D bottom=75 RS=49 marketDD=-22.80% nearLow=0.00% risk=no_repair
- AAPL 2022-06-13 OBS-D bottom=75 RS=58 marketDD=-31.66% nearLow=0.00% risk=no_repair
- AMD 2008-11-19 OBS-D bottom=75 RS=42 marketDD=-46.79% nearLow=0.00% risk=trend_damage,no_repair
- AMD 2010-08-20 OBS-S bottom=75 RS=42 marketDD=-11.30% nearLow=0.00% risk=low_volume,no_repair
- AMD 2011-09-30 OBS-S bottom=75 RS=42 marketDD=-16.22% nearLow=0.00% risk=trend_damage,no_repair
- AMD 2012-07-25 OBS-S bottom=75 RS=42 marketDD=-8.16% nearLow=0.00% risk=trend_damage,no_repair
- AMD 2018-04-03 OBS-S bottom=75 RS=42 marketDD=-9.52% nearLow=0.21% risk=no_repair
- AMD 2024-07-30 OBS-S bottom=75 RS=42 marketDD=-9.03% nearLow=0.09% risk=no_repair
- AMZN 2011-11-21 OBS-S bottom=75 RS=48 marketDD=-11.14% nearLow=0.00% risk=no_repair
- AMZN 2018-10-11 OBS-S bottom=75 RS=45 marketDD=-9.02% nearLow=0.00% risk=no_repair
- AMZN 2022-01-20 OBS-S bottom=75 RS=42 marketDD=-10.35% nearLow=0.00% risk=no_repair
- AVGO 2015-08-21 OBS-S bottom=75 RS=42 marketDD=-10.16% nearLow=0.00% risk=no_repair
- CAT 2009-02-26 OBS-D bottom=75 RS=42 marketDD=-41.11% nearLow=0.00% risk=trend_damage,no_repair
- CAT 2016-01-08 OBS-S bottom=75 RS=42 marketDD=-9.41% nearLow=0.00% risk=no_repair
- CRM 2020-03-12 OBS-D bottom=75 RS=42 marketDD=-26.67% nearLow=0.00% risk=no_repair
- CRM 2021-03-04 OBS-S bottom=75 RS=42 marketDD=-9.62% nearLow=0.00% risk=no_repair
- CRM 2022-09-02 OBS-D bottom=75 RS=42 marketDD=-20.33% nearLow=0.10% risk=low_volume,no_repair
- CRM 2024-09-06 OBS-S bottom=68 RS=62 marketDD=-10.79% nearLow=6.69% risk=no_repair
- JPM 2012-05-17 OBS-S bottom=75 RS=42 marketDD=-9.73% nearLow=0.00% risk=no_repair
- JPM 2014-10-16 OBS-S bottom=74 RS=42 marketDD=-8.25% nearLow=0.00% risk=no_repair
- JPM 2020-05-13 OBS-S bottom=72 RS=58 marketDD=-16.28% nearLow=7.43% risk=no_repair
- JPM 2023-10-27 OBS-S bottom=75 RS=47 marketDD=-10.35% nearLow=0.00% risk=no_repair
- LLY 2008-10-06 OBS-D bottom=75 RS=58 marketDD=-30.94% nearLow=0.00% risk=no_repair

## Plain-English Read
- OBS-D means a deep market drawdown retest that is below formal MB strength.
- OBS-S means a shallower market pullback that is worth watching but not a formal bottom signal.
- Upgrade candidate score is evidence for future review, not an automatic promotion rule.
