# Strategy Iteration Review

## Baseline Freeze
- Formal strategy: `seed_previous_rs_higher_low_best` stays frozen.
- Full-pool artifact: yes (FULL_POOL).
- Symbol count: 21.
- Strong signals: 39.
- Avg 6m return: 39.24%.
- 6m win rate: 74.36%.
- Avg 6m adverse drawdown: -13.80%.
- Entry threshold: `82`.

## Recent Formal Signal Review
- Window: 2024-05-01 to 2026-04-30.
- Recent formal signals: 7.
- Recent mature signals: 7.
- Recent status: Pass.
- Recent avg 6m return: 75.79%.
- Recent 6m win rate: 100.00%.

## Recent Formal Signal Details
- AAPL 2025-04-04 channel=MB bottom=82 RS=46 risk=no_repair fwd6m=36.60% adverse6m=-8.47%
- AVGO 2025-04-04 channel=MB bottom=82 RS=46 risk=no_repair fwd6m=130.27% adverse6m=0.00%
- CAT 2025-04-04 channel=MB bottom=82 RS=46 risk=no_repair fwd6m=73.42% adverse6m=-4.91%
- META 2025-04-04 channel=MB bottom=82 RS=46 risk=no_repair fwd6m=42.00% adverse6m=-3.98%
- NVDA 2025-04-04 channel=MB bottom=82 RS=46 risk=no_repair fwd6m=96.76% adverse6m=0.00%
- QQQ 2025-04-04 channel=MB bottom=82 RS=46 risk=no_repair fwd6m=44.11% adverse6m=-1.56%
- TSM 2025-04-04 channel=MB bottom=82 RS=46 risk=no_repair fwd6m=107.40% adverse6m=-3.70%

## OBS Candidate Risk Segmentation
- Observation signals: 48.
- Formal baseline: 39.
- Observation/Formal ratio: 1.23x.
- Duplicate formal signals: 0.
- risk=low_volume: count=1, avg6m=52.15%, win6m=100.00%, adverse6m=-3.75%
- risk=no_repair: count=45, avg6m=19.38%, win6m=72.73%, adverse6m=-10.98%
- risk=none: count=3, avg6m=14.86%, win6m=66.67%, adverse6m=-10.51%
- risk=trend_damage: count=3, avg6m=48.59%, win6m=66.67%, adverse6m=-21.47%

## RS Watchlist Review
- Monitor: AVGO, META
  - AVGO: score=92.40, qualified=2, reason=repeated qualified candidates with clean risk profile
  - META: score=92.11, qualified=2, reason=repeated qualified candidates with clean risk profile
- Review: CRM, PLTR, AMZN, TSLA, AAPL, V, JPM
  - CRM: score=79.71, qualified=2, reason=qualified but has risk flags
  - PLTR: score=73.24, qualified=1, reason=qualified but quality score is below priority
  - AMZN: score=66.77, qualified=1, reason=qualified watchlist candidate
  - TSLA: score=62.33, qualified=1, reason=qualified watchlist candidate
  - AAPL: score=59.07, qualified=1, reason=qualified but has risk flags
  - V: score=57.94, qualified=1, reason=qualified but has risk flags
  - JPM: score=56.34, qualified=1, reason=qualified but has risk flags
- Skip: CAT, NVDA, CRWD
  - CAT: score=50.93, qualified=0, reason=no qualified RS candidates
  - NVDA: score=49.46, qualified=0, reason=no qualified RS candidates
  - CRWD: score=38.20, qualified=0, reason=no qualified RS candidates

## Plan Validation Gates
- PASS baselineName: seed_previous_rs_higher_low_best
- PASS fullPool: symbols=21 sample=FULL_POOL
- PASS entryThreshold: threshold=82
- PASS formalSignalCap: signals=39 limit=40
- PASS duplicateFormal: duplicateFormalCount=0
- PASS qqq2022Q4Coverage: 2022-10-03, 2022-10-11, 2022-12-28
- PASS qqq2026MarchCoverage: 2026-03-27

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
- DONE 1 Baseline confirmation: seed_previous_rs_higher_low_best; symbols=21; signals=39
- DONE 2 Recent sample review: mature=7; status=Pass
- DONE 3 OBS candidate segmentation: signals=48; riskBuckets=4
- DONE 4 RS watchlist review: monitor=2; review=7; skip=3
- DONE 5 Formal-missed OBS cases: cases=48
- DONE 6 Promotion validation plan: preconditions=4

## Formal-Missed OBS Cases
- AMD 2008-07-01 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=-60.88% adverse6m=-68.14%
- LLY 2008-09-17 OBS-D risk=no_repair bottom=75 RS=48 fwd6m=-25.52% adverse6m=-35.72%
- SPY 2008-10-16 OBS-D risk=none bottom=75 RS=46 fwd6m=-9.66% adverse6m=-26.78%
- WMT 2009-01-08 OBS-D risk=no_repair bottom=75 RS=51 fwd6m=-6.39% adverse6m=-9.65%
- CAT 2009-02-19 OBS-D risk=no_repair bottom=75 RS=42 fwd6m=71.45% adverse6m=-17.95%
- WMT 2009-04-24 OBS-S risk=no_repair bottom=71 RS=45 fwd6m=6.60% adverse6m=-0.09%
- XOM 2010-01-29 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=-6.13% adverse6m=-11.03%
- MSFT 2010-05-07 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=-2.84% adverse6m=-18.07%
- XOM 2010-06-29 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=29.88% adverse6m=-1.26%
- AMD 2010-08-25 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=48.45% adverse6m=-8.48%
- QQQ 2011-03-16 OBS-S risk=no_repair bottom=75 RS=43 fwd6m=2.61% adverse6m=-7.27%
- NVDA 2011-06-15 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=-15.74% adverse6m=-30.05%
- TSLA 2011-08-05 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=31.19% adverse6m=-9.45%
- JPM 2011-09-21 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=49.53% adverse6m=-5.64%
- AVGO 2011-11-18 OBS-S risk=no_repair bottom=74 RS=52 fwd6m=5.53% adverse6m=-7.35%
- TSM 2012-05-31 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=30.31% adverse6m=-5.17%
- AMD 2012-07-25 OBS-S risk=trend_damage,no_repair bottom=75 RS=42 fwd6m=-29.68% adverse6m=-53.62%
- AMD 2012-11-07 OBS-S risk=trend_damage,no_repair bottom=74 RS=42 fwd6m=96.52% adverse6m=-7.46%
- QQQ 2014-10-16 OBS-S risk=no_repair bottom=74 RS=42 fwd6m=17.93% adverse6m=0.00%
- AVGO 2015-08-24 OBS-S risk=no_repair bottom=75 RS=42 fwd6m=19.29% adverse6m=-1.30%

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
