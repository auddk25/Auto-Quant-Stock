# Strategy Iteration Review

## Baseline Freeze
- Formal strategy: `btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry78_mbo0_rs63_wmomentum_reset` stays frozen.
- Full-pool artifact: yes (FULL_POOL).
- Symbol count: 21.
- Strong signals: 124.
- Avg 6m return: 31.61%.
- 6m win rate: 79.34%.
- Avg 6m adverse drawdown: -11.66%.
- Entry threshold: `78`.

## Recent Formal Signal Review
- Window: 2024-05-01 to 2026-04-30.
- Recent formal signals: 21.
- Recent mature signals: 18.
- Recent status: Pass.
- Recent avg 6m return: 47.85%.
- Recent 6m win rate: 88.89%.

## Recent Formal Signal Details
- CRWD 2024-07-30 channel=MB bottom=88 RS=49 risk=none fwd6m=69.86% adverse6m=-6.75%
- AMD 2024-08-01 channel=MB bottom=80 RS=45 risk=no_repair fwd6m=-13.78% adverse6m=-13.86%
- WMT 2024-08-07 channel=RS bottom=58 RS=79 risk=none fwd6m=51.94% adverse6m=0.00%
- TSLA 2025-03-06 channel=MB bottom=79 RS=44 risk=none fwd6m=33.17% adverse6m=-15.79%
- V 2025-03-11 channel=RS bottom=67 RS=81 risk=no_repair fwd6m=2.15% adverse6m=-7.19%
- AVGO 2025-04-03 channel=MB bottom=78 RS=44 risk=no_repair fwd6m=120.60% adverse6m=-5.01%
- CAT 2025-04-03 channel=MB bottom=79 RS=56 risk=no_repair fwd6m=64.21% adverse6m=-10.41%
- AAPL 2025-04-04 channel=MB bottom=80 RS=46 risk=no_repair fwd6m=36.60% adverse6m=-8.47%
- AMD 2025-04-04 channel=MB bottom=80 RS=45 risk=trend_damage,no_repair fwd6m=137.53% adverse6m=-8.80%
- AMZN 2025-04-04 channel=MB bottom=78 RS=59 risk=no_repair fwd6m=29.18% adverse6m=-2.15%
- CRM 2025-04-04 channel=MB bottom=79 RS=60 risk=no_repair fwd6m=2.59% adverse6m=-3.48%
- LLY 2025-04-04 channel=MB bottom=79 RS=68 risk=no_repair fwd6m=14.96% adverse6m=-15.07%
- META 2025-04-04 channel=MB bottom=79 RS=51 risk=no_repair fwd6m=42.00% adverse6m=-3.98%
- NVDA 2025-04-04 channel=MB bottom=80 RS=45 risk=no_repair fwd6m=96.76% adverse6m=0.00%
- QQQ 2025-04-04 channel=MB bottom=79 RS=60 risk=no_repair fwd6m=44.11% adverse6m=-1.56%
- SPY 2025-04-04 channel=MB bottom=78 RS=60 risk=no_repair fwd6m=33.68% adverse6m=-1.74%
- TSM 2025-04-04 channel=MB bottom=80 RS=53 risk=no_repair fwd6m=107.40% adverse6m=-3.70%
- UNH 2025-04-28 channel=MB bottom=86 RS=48 risk=low_volume fwd6m=-11.69% adverse6m=-42.99%

## OBS Candidate Risk Segmentation
- Observation signals: 49.
- Formal baseline: 124.
- Observation/Formal ratio: 0.40x.
- Duplicate formal signals: 0.
- risk=low_volume: count=5, avg6m=28.63%, win6m=100.00%, adverse6m=-12.62%
- risk=no_repair: count=48, avg6m=25.41%, win6m=76.60%, adverse6m=-11.73%
- risk=trend_damage: count=6, avg6m=43.51%, win6m=66.67%, adverse6m=-20.31%

## RS Watchlist Review
- Monitor: none
- Review: AAPL, AVGO, META, JPM, NVDA, AMZN, CAT, TSM
  - AAPL: score=87.69, qualified=3, reason=qualified watchlist candidate
  - AVGO: score=79.09, qualified=2, reason=qualified but has risk flags
  - META: score=79.07, qualified=3, reason=qualified but has risk flags
  - JPM: score=74.55, qualified=1, reason=qualified but quality score is below priority
  - NVDA: score=71.59, qualified=1, reason=qualified but quality score is below priority
  - AMZN: score=67.26, qualified=1, reason=qualified watchlist candidate
  - CAT: score=61.11, qualified=1, reason=qualified but has risk flags
  - TSM: score=56.60, qualified=1, reason=qualified but has risk flags
- Skip: TSLA, PLTR, WMT, CRM
  - TSLA: score=84.59, qualified=3, reason=qualified but adverse drawdown is high
  - PLTR: score=59.46, qualified=1, reason=qualified but has risk flags
  - WMT: score=55.93, qualified=0, reason=no qualified RS candidates
  - CRM: score=55.65, qualified=1, reason=qualified but has risk flags

## Plan Validation Gates
- FAIL baselineName: btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry78_mbo0_rs63_wmomentum_reset
- PASS fullPool: symbols=21 sample=FULL_POOL
- FAIL entryThreshold: threshold=78
- FAIL formalSignalCap: signals=124 limit=40
- PASS duplicateFormal: duplicateFormalCount=0
- PASS qqq2022Q4Coverage: 2022-10-11, 2022-11-03, 2022-12-28
- PASS qqq2026MarchCoverage: 2026-03-30

## Retired Artifact Guard
- PASS retiredArtifact: bottom_signal_results_dual_track_rs.json absent
- PASS retiredArtifact: bottom_signal_report_dual_track_rs.md absent

## Main Artifact Manifest
- PASS script: bottom_signal_search.py exists
- PASS config: bottom_signal_config.json exists
- PASS results: bottom_signal_results.json exists
- PASS report: bottom_signal_report.md exists
- PASS observation-report: bottom_signal_observation_report.md exists

## Strategy Plan Step Status
- DONE 1 Baseline confirmation: btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry78_mbo0_rs63_wmomentum_reset; symbols=21; signals=124
- DONE 2 Recent sample review: mature=18; status=Pass
- DONE 3 OBS candidate segmentation: signals=49; riskBuckets=3
- DONE 4 RS watchlist review: monitor=0; review=8; skip=4
- DONE 5 Formal-missed OBS cases: cases=49
- DONE 6 Promotion validation plan: preconditions=4

## Formal-Missed OBS Cases
- NVDA 2008-07-03 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=-30.26% adverse6m=-52.76%
- AAPL 2008-09-29 OBS-D risk=no_repair bottom=75 RS=42 fwd6m=-0.13% adverse6m=-25.71%
- LLY 2008-10-06 OBS-D risk=no_repair bottom=75 RS=58 fwd6m=-14.73% adverse6m=-26.52%
- AMD 2008-11-19 OBS-D risk=trend_damage,no_repair bottom=75 RS=42 fwd6m=100.94% adverse6m=-15.09%
- V 2009-01-23 OBS-D risk=trend_damage,low_volume bottom=75 RS=41 fwd6m=52.37% adverse6m=-3.90%
- CAT 2009-02-26 OBS-D risk=trend_damage,no_repair bottom=75 RS=42 fwd6m=100.00% adverse6m=-8.50%
- WMT 2009-04-24 OBS-S risk=no_repair bottom=72 RS=46 fwd6m=6.60% adverse6m=-0.09%
- XOM 2010-01-29 OBS-S risk=no_repair bottom=74 RS=42 fwd6m=-6.13% adverse6m=-11.03%
- NVDA 2010-05-18 OBS-S risk=low_volume,no_repair bottom=75 RS=42 fwd6m=4.30% adverse6m=-29.30%
- XOM 2010-07-01 OBS-S risk=no_repair bottom=75 RS=58 fwd6m=31.34% adverse6m=-0.07%
- AMD 2010-08-20 OBS-S risk=low_volume,no_repair bottom=75 RS=42 fwd6m=46.88% adverse6m=-10.24%
- MSFT 2011-03-16 OBS-S risk=no_repair bottom=75 RS=43 fwd6m=8.28% adverse6m=-3.73%
- NVDA 2011-06-16 OBS-S risk=no_repair bottom=75 RS=43 fwd6m=-16.12% adverse6m=-27.55%
- TSLA 2011-08-04 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=25.86% adverse6m=-11.31%
- AMD 2011-09-30 OBS-S risk=trend_damage,no_repair bottom=75 RS=42 fwd6m=61.42% adverse6m=-10.83%
- AMZN 2011-11-21 OBS-S risk=no_repair bottom=75 RS=48 fwd6m=14.81% adverse6m=-8.53%
- JPM 2012-05-17 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=18.34% adverse6m=-8.64%
- AMD 2012-07-25 OBS-S risk=trend_damage,no_repair bottom=75 RS=42 fwd6m=-29.68% adverse6m=-53.62%
- MSFT 2012-11-13 OBS-S risk=no_repair bottom=75 RS=48 fwd6m=27.73% adverse6m=-2.66%
- JPM 2014-10-16 OBS-S risk=no_repair bottom=74 RS=42 fwd6m=16.32% adverse6m=-0.64%

## Candidate Rule
- Do not promote OBS/RS into formal entries from this review.
- Open a separate validation plan before any OBS/RS promotion.
- Keep the current MB factor stack intact unless a separate ablation supports a change.

## Promotion Preconditions
- Required: OBS/RS ablation against frozen MB baseline.
- Required: recent validation keeps formal signal count controlled.
- Required: sample-out validation before formal promotion.
- Required: Pine parity check before operator use.

## Validation Command Checklist
- Minimum: `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
- Repo-wide: `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
- Minimum: `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
- Minimum: `.venv\Scripts\python.exe -m json.tool strategy_catalog\bottom_signal_formal\bottom_signal_results.json > $null`
- Minimum: `git diff --check`
- Minimum: `git diff --name-only -- config.py prepare.py run.py versions`
- Full search only after search logic/config changes: `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
- Full search only after search logic/config changes: `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
