# Claude Progress Archive 2026-05

- Source: `claude-progress.md`.
- Archived on: 2026-05-20.
- Archived sessions: 114.
- This file preserves older session history moved out of the active progress file.

## Archived Sessions

--- Session: 2026-05-19 Plan Summary Decision Rule Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Add a concise decision rule to the one-page summary.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `Decision Rule` to `generate_plan_summary()`.
- The section states:
  - do not promote RS watchlist rows into formal MB entries from this artifact;
  - keep the current MB factor stack intact unless a separate ablation run supports a change;
  - use RecentValidation status before any promotion decision.
- Added unit coverage for the new Markdown section.

## Current Result Snapshot
- `investigations/bottom_signal_plan_summary.md` now includes:
  - `Do not promote RS watchlist rows into formal MB entries from this artifact.`
  - `Keep the current MB factor stack intact unless a separate ablation run supports a change.`
  - `Use RecentValidation status before any promotion decision.`

## Refreshed Artifacts
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target summary test first failed because `## Decision Rule` was missing.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 24 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Plan Summary Role Guide Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Bring the action role explanation from CSV into the one-page Markdown summary.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `Role Guide` to `generate_plan_summary()`.
- The section explains:
  - `FormalStrategy`: MB keep/brake actions belong to the formal strategy.
  - `Observation`: RS Monitor/Review/Skip rows are watchlist actions only.
  - `Validation`: RecentValidation rows summarize recent evidence.
- Added unit coverage for the new Markdown section.

## Current Result Snapshot
- `investigations/bottom_signal_plan_summary.md` now includes:
  - `FormalStrategy: MB keep/brake actions belong to the formal strategy.`
  - `Observation: RS Monitor/Review/Skip rows are watchlist actions only.`
  - `Validation: RecentValidation rows summarize recent evidence.`

## Refreshed Artifacts
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target summary test first failed because `## Role Guide` was missing.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 26 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Next Actions Role Column Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make `bottom_signal_next_actions.csv` clearly separate formal strategy actions from RS observation and validation rows.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added a `role` column to `generate_next_actions_csv()`.
- Role values:
  - `FormalStrategy` for MB keep/brake rows;
  - `Observation` for RS Monitor/Review/Skip rows;
  - `Validation` for RecentValidation rows.
- Updated unit coverage for the new CSV shape.

## Current Result Snapshot
- `investigations/bottom_signal_next_actions.csv` now starts with:
  - `priority,role,category,target,action,reason,evidence`.
- Example rows:
  - `1,FormalStrategy,MB,drawdown,Keep,...`
  - `2,Observation,RS,AVGO,Monitor,...`
  - `5,Validation,RecentValidation,Pass,...`

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target CSV test first failed because the `role` column was missing.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 26 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Action Counts Summary Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Add a quick count summary before the detailed Next Actions list.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `Action Counts` to `generate_plan_summary()`.
- The section counts:
  - MB keep factors;
  - MB brake factors;
  - RS monitor tickers;
  - RS review tickers;
  - RS skip tickers.
- Added unit coverage for the new summary section.

## Current Result Snapshot
- `investigations/bottom_signal_plan_summary.md` now includes:
  - MB keep: 5.
  - MB brake: 1.
  - RS monitor: 2.
  - RS review: 7.
  - RS skip: 3.

## Refreshed Artifacts
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target summary test first failed because `## Action Counts` was missing.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 28 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Action Reason Evidence Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make RS Monitor/Review action rows explain why each ticker is in that tier.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `actionReason` text to RS Monitor and RS Review evidence in `generate_next_actions_csv()`.
- Priority RS rows now show why they are `Monitor`.
- Watch RS rows now show whether the reason is risk flags, lower quality, or general watchlist qualification.
- Added unit coverage for the richer RS evidence string.

## Current Result Snapshot
- `investigations/bottom_signal_next_actions.csv` now includes examples like:
  - `AVGO`: `reason=repeated qualified candidates with clean risk profile`.
  - `CRM`: `reason=qualified but has risk flags`.
  - `PLTR`: `reason=qualified but quality score is below priority`.

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target CSV test first failed because RS Monitor/Review evidence did not include `reason=...`.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 27 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Recent Validation Evidence Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make the RecentValidation action row auditable without opening the main report.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Enriched the RecentValidation row in `generate_next_actions_csv()`.
- The row now includes:
  - status;
  - mature check count;
  - 6m win rate;
  - average 6m forward return.
- Added unit coverage for the richer RecentValidation evidence string.

## Current Result Snapshot
- `investigations/bottom_signal_next_actions.csv` now ends with:
  - `5,RecentValidation,Pass,Continue observation,Recent validation passed,status=Pass; matureCount=7; winRate=100.00%; avgFwd126=75.79%`.

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target CSV test first failed because RecentValidation evidence only contained `status=Pass`.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 27 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Avoid RS Action Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Complete RS action coverage by adding a Skip path for RS `Avoid` tickers.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `Skip Avoid RS tickers` to `generate_plan_summary()`.
- Added priority 4 RS `Skip` rows to `generate_next_actions_csv()`.
- Shifted RecentValidation action rows to priority 5.
- Fixed the action-list coverage bug where only the top 5 RS ticker rows were considered:
  - the display section still shows the top 5;
  - the Next Actions and CSV now inspect up to the top 12 ticker rows.
- Added unit coverage so lower-ranked Avoid rows are still exported as Skip actions.

## Current Result Snapshot
- `investigations/bottom_signal_plan_summary.md` now includes:
  - `Skip Avoid RS tickers: CAT, NVDA, CRWD`.
- `investigations/bottom_signal_next_actions.csv` now includes priority 4 Skip rows:
  - CAT, selectionScore 50.93;
  - NVDA, selectionScore 49.46;
  - CRWD, selectionScore 38.20.

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target tests first failed because lower-ranked Avoid tickers were clipped by the top-5 action list.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 28 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Watch RS Action Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Add a lower-priority action path for RS `Watch` tickers.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `Review Watch RS tickers` to `generate_plan_summary()`.
- Added priority 3 RS `Review` rows to `generate_next_actions_csv()`.
- Shifted RecentValidation action rows to priority 4 so RS Watch review sits between Priority RS monitoring and validation status.
- Added unit coverage for Watch RS tickers in both Markdown and CSV outputs.

## Current Result Snapshot
- `investigations/bottom_signal_plan_summary.md` now includes:
  - `Review Watch RS tickers: CRM, PLTR, AMZN`.
- `investigations/bottom_signal_next_actions.csv` now includes priority 3 rows:
  - CRM, selectionScore 79.71, qualifiedCount 2.
  - PLTR, selectionScore 73.24, qualifiedCount 1.
  - AMZN, selectionScore 66.77, qualifiedCount 1.

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target tests first failed because Watch RS tickers appeared in the RS read section but not in the Next Actions section or next-actions CSV.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 26 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Overactive MB Brake Action Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make overactive MB ablation conclusions actionable, not just descriptive.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added overactive MB factor handling to `generate_plan_summary()`.
- Added overactive MB factor rows to `generate_next_actions_csv()`.
- `repair` is now listed as a `Keep brake` action because removing it creates too many signals.
- Added unit coverage for both Markdown summary and CSV checklist behavior.

## Current Result Snapshot
- `investigations/bottom_signal_plan_summary.md` now includes:
  - `Keep MB brake factors: repair`.
- `investigations/bottom_signal_next_actions.csv` now includes:
  - `1,MB,repair,Keep brake,Overactive factor from MB ablation,compositeDelta=-27.95; signalCountDelta=+86`.

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target tests first failed because overactive `repair` did not appear in summary next actions or next-actions CSV.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 27 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Next Actions Evidence Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make `bottom_signal_next_actions.csv` easier to sort and audit.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `priority` and `evidence` columns to `bottom_signal_next_actions.csv`.
- MB keep rows now include:
  - `compositeDelta`;
  - `signalCountDelta`.
- RS monitor rows now include:
  - `selectionScore`;
  - `qualifiedCount`.
- RecentValidation row now includes the validation status as evidence.
- Updated unit coverage for the enriched CSV shape.

## Current Result Snapshot
- `investigations/bottom_signal_next_actions.csv` now starts with:
  - `priority,category,target,action,reason,evidence`.
- Current priority rows:
  - priority 1: keep critical MB factors;
  - priority 2: monitor Priority RS tickers AVGO and META;
  - priority 3: continue observation because recent validation is Pass.

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target CSV test first failed because `priority` and `evidence` columns were missing.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 28 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Next Actions CSV Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Export the plan summary actions as a small CSV checklist for spreadsheet review or automation.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added `NEXT_ACTIONS_CSV_PATH`.
- Added `generate_next_actions_csv()`.
- Wired `bottom_signal_next_actions.csv` into `write_outputs()`.
- Added references to the next-actions CSV in the main report and plan summary.
- Updated supplemental refresh CLI output to print the new CSV path.
- Added unit coverage for the generated action checklist.

## Current Result Snapshot
- `investigations/bottom_signal_next_actions.csv` now contains:
  - MB keep rows for drawdown, momentum, structure, volume, ma.
  - RS monitor rows for AVGO and META.
  - RecentValidation row: Pass / Continue observation.

## Refreshed Artifacts
- `investigations/bottom_signal_next_actions.csv`
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target CSV test first failed because `generate_next_actions_csv` did not exist.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_next_actions_csv_exports_review_checklist`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 79 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 29 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Plan Summary Next Actions Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Turn the one-page plan summary from passive results into a short action checklist.
- Keep MB/RS formulas and formal entry logic unchanged.

## Completed
- Added a `Next Actions` section to `investigations/bottom_signal_plan_summary.md`.
- The section now states:
  - which MB factors to keep;
  - which Priority RS tickers to monitor;
  - what to do with the recent validation status.
- Added unit coverage so the summary must include the action checklist.

## Current Result Snapshot
- `Next Actions` now says:
  - Keep MB factors: drawdown, momentum, structure, volume, ma.
  - Monitor Priority RS tickers: AVGO, META.
  - Recent validation passed; continue observation.

## Refreshed Artifacts
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target summary test first failed because `## Next Actions` was missing.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 78 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 27 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Plan Summary Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Add a simple one-page artifact that ties together MB factor ablation, RS ticker ranking, and recent validation.
- Keep MB/RS formulas unchanged.

## Completed
- Added `bottom_signal_plan_summary.md` generation.
- Added `generate_plan_summary()` with plain-English sections:
  - decision snapshot;
  - MB factor read;
  - RS selection read;
  - recent validation read;
  - files to review.
- Wired the summary into `write_outputs()`.
- Added the plan summary path to the main report scope.
- Updated supplemental refresh CLI output to print the new summary path.
- Added unit coverage for the summary artifact.

## Current Result Snapshot
- Best config remains `seed_previous_rs_higher_low_best`.
- MB ablation conclusion:
  - Critical factors: drawdown, momentum, structure, volume, ma.
  - Overactive without: repair.
- RS selection top observations:
  - `#1 AVGO`, Priority, selection `92.40`;
  - `#2 META`, Priority, selection `92.11`;
  - `#3 CRM`, Watch, selection `79.71`;
  - `#4 PLTR`, Watch, selection `73.24`;
  - `#5 AMZN`, Watch, selection `66.77`.
- Recent validation status is `Pass`:
  - 7 recent formal signals;
  - 7 mature 6m checks;
  - 75.79% recent avg 6m return;
  - 100.00% recent 6m win rate.

## Refreshed Artifacts
- `investigations/bottom_signal_plan_summary.md`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing RS watchlist report/candidate/Pine outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - Target summary test first failed because `generate_plan_summary` did not exist.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_plan_summary_connects_mb_rs_and_recent_validation_outputs`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 78 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 28 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Selection Rank Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make RS ticker selection priority explicit and correctly sorted.
- Keep RS score formulas unchanged.

## Completed
- Added `selectionRank` to RS ticker summary rows.
- Added `rank_rs_ticker_summary()` so rank, score, action tier, and reason are computed consistently.
- Updated `write_outputs()` and CSV generation to re-rank existing ticker summaries by `selectionScore`.
- Updated RS watchlist report to show numbered ticker rows:
  - `#1 AVGO`;
  - `#2 META`;
  - `#3 CRM`;
  - etc.
- Updated `bottom_signal_rs_watchlist_tickers.csv` with `selectionRank`.
- Added unit coverage to ensure ranking follows `selectionScore`, not stale JSON order.

## Current Result Snapshot
- Top RS observation ranks:
  - `#1 AVGO`, selection `92.40`, `Priority`;
  - `#2 META`, selection `92.11`, `Priority`;
  - `#3 CRM`, selection `79.71`, `Watch`;
  - `#4 PLTR`, selection `73.24`, `Watch`.
- This changes output ordering only; it does not change RS candidate scoring or formal MB entry logic.

## Refreshed Artifacts
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_rs_watchlist_report.md`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing MB ablation, recent validation, Pine, and RS candidate outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - `tests.test_bottom_signal_search` failed because `selectionRank` was missing / stale ordering was not re-ranked.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 27 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 77 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- Static artifact checks:
  - RS ticker CSV contains `selectionRank`;
  - RS ticker CSV is ordered by selection score;
  - RS watchlist report shows `#1 AVGO`;
  - `config.py`, `prepare.py`, `run.py`, and `versions/` remain untouched.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 MB Ablation Interpretation Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Turn MB factor ablation from raw rows into readable conclusions.
- Keep MB/RS signal formulas unchanged.

## Completed
- Added `summarize_mb_factor_ablation()`.
- Added MB ablation impact labels:
  - `Critical`: removing the factor destroys or materially weakens the selected setup;
  - `Overactive`: removing the factor creates too many signals and fails the evaluation discipline;
  - `Supportive`: removing the factor hurts but does not break the setup;
  - `Redundant`: removing the factor does not hurt.
- Updated `bottom_signal_mb_factor_ablation.csv` with `impactLabel`.
- Updated `bottom_signal_report.md` with MB ablation summary lines:
  - Critical factors;
  - Overactive without;
  - Supportive factors;
  - Redundant factors.
- Added unit coverage for MB ablation summary labels.

## Current Result Snapshot
- Critical factors:
  - `drawdown`;
  - `momentum`;
  - `structure`;
  - `volume`;
  - `ma`.
- Overactive without:
  - `repair`.
- Supportive factors:
  - none.
- Redundant factors:
  - none.
- Interpretation:
  - The current selected MB setup depends on the full factor stack.
  - Removing `repair` especially makes the signal set too loose/overactive.

## Refreshed Artifacts
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_report.md`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing Pine/RS candidate outputs through `write_outputs()`.

## Verification
- TDD RED check:
  - `tests.test_bottom_signal_search` initially failed because `summarize_mb_factor_ablation` did not exist.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 26 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 76 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- Static artifact checks:
  - MB ablation CSV contains `impactLabel`;
  - report contains `Critical factors`;
  - report contains `Overactive without`;
  - report labels each ablation row.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Recent Validation CSV and RS Reason Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make recent validation inspectable at signal-row level.
- Make RS ticker `Priority / Watch / Avoid` labels easier to understand without reading scoring code.

## Completed
- Added recent validation CSV export:
  - `investigations/bottom_signal_recent_validation.csv`.
- The recent validation CSV lists each recent formal signal with:
  - symbol;
  - date;
  - channel;
  - tier;
  - check status: `Pass` / `Fail` / `Pending`;
  - bottom score;
  - RS signal score;
  - risk flags;
  - 6m return;
  - 6m adverse drawdown.
- Added RS ticker action reason:
  - `repeated qualified candidates with clean risk profile`;
  - `qualified but has risk flags`;
  - `qualified but quality score is below priority`;
  - `qualified watchlist candidate`;
  - `no qualified RS candidates`.
- Included action reason in:
  - `investigations/bottom_signal_rs_watchlist_tickers.csv`;
  - `investigations/bottom_signal_rs_watchlist_report.md`.
- Added report link:
  - `bottom_signal_report.md` now lists `bottom_signal_recent_validation.csv`.
- Added tests for:
  - recent validation CSV row export;
  - RS action reason text.

## Refreshed Artifacts
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_recent_validation.csv`
- `investigations/bottom_signal_rs_watchlist_report.md`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- Existing Pine/RS candidate outputs through `write_outputs()`.

## Current Result Snapshot
- Recent validation CSV currently has 7 recent formal MB signal rows.
- All 7 rows are `Pass` on 6m check status.
- RS ticker CSV now includes an `actionReason` column.

## Verification
- TDD RED check:
  - `tests.test_bottom_signal_search` initially failed because `generate_recent_validation_csv` did not exist.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 27 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 75 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- Static artifact checks:
  - report references `bottom_signal_recent_validation.csv`;
  - recent validation CSV contains recent signal rows;
  - RS ticker CSV contains `actionReason`;
  - RS watchlist report contains `reason=...` for ticker rows.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 MB Ablation Plan Continuation ---
## Objective
- Continue executing `MB 因子消融、RS 选股增强与近期验证计划`.
- Make the supplemental analysis repeatable without ad-hoc Python snippets.
- Export MB factor ablation to CSV for spreadsheet-style review.

## Completed
- Added first-class supplemental refresh command:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
- Added `refresh_supplemental_analysis()`:
  - reads the existing best config payload;
  - rebuilds MB factor ablation;
  - recomputes recent validation summaries for stored result rows;
  - preserves the full search results without rerunning the 720-config grid.
- Added MB factor ablation CSV export:
  - `investigations/bottom_signal_mb_factor_ablation.csv`.
- Added report link:
  - `bottom_signal_report.md` now lists the MB factor ablation CSV in Scope.
- Added tests for:
  - MB factor ablation CSV formatting;
  - supplemental refresh rebuilding ablation and recent validation.

## Refreshed Artifacts
- `investigations/bottom_signal_results.json`
- `investigations/bottom_signal_results_dual_track_rs.json`
- `investigations/bottom_signal_report.md`
- `investigations/bottom_signal_report_dual_track_rs.md`
- `investigations/bottom_signal_rs_watchlist_report.md`
- `investigations/bottom_signal_rs_watchlist_tickers.csv`
- `investigations/bottom_signal_mb_factor_ablation.csv`
- Pine/RS candidate outputs through existing `write_outputs()`.

## Current Result Snapshot
- Supplemental refresh command completed successfully.
- Refresh config: `seed_previous_rs_higher_low_best`.
- MB ablation rows: `6`.
- New CSV rows show each factor removal and its deltas vs the selected baseline.

## Verification
- TDD RED check:
  - `tests.test_bottom_signal_search` initially failed because `generate_mb_factor_ablation_csv` did not exist.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-supplemental-analysis`
  - PASS, about 29 seconds.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 73 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- Static artifact checks:
  - report references `bottom_signal_mb_factor_ablation.csv`;
  - report contains `MB Factor Ablation`;
  - report contains `Recent Validation`;
  - CLI contains `--refresh-supplemental-analysis`;
  - MB ablation CSV has six comparison rows.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` still does not have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 MB Ablation, RS Selection, Recent Validation Plan ---
## Objective
- Execute the `MB 因子消融、RS 选股增强与近期验证计划`.
- Keep the formal MB strategy and RS watchlist roles unchanged.
- Explain outputs in report artifacts so they are easier to review without reading code.

## Assumptions
- No exact same-name plan file existed under `docs/` or `investigations/`.
- Interpreted the plan as:
  - add MB factor ablation reporting;
  - improve RS stock-level ranking with a single selection score;
  - add recent-window validation status for formal signals.
- Avoided a full 720-config grid rerun; refreshed only the new supplemental analysis from the existing best config/results.

## Completed
- Added MB factor ablation helpers:
  - one row per removed MB scoring factor: drawdown, momentum, repair, structure, volume, MA;
  - each ablation variant sets that factor weight to `0.0` and reuses the same evaluation pipeline.
- Added recent formal-signal validation summary:
  - window start/end;
  - recent signal count;
  - mature 6m check count;
  - avg 6m return;
  - 6m win rate;
  - avg 6m adverse drawdown;
  - status: `Pass` / `Watch` / `Fail`.
- Added RS ticker `selectionScore`:
  - rewards qualified repeated RS candidates and quality;
  - penalizes risk flags and weak adverse-drawdown profile;
  - included in RS ticker JSON, CSV, and report output.
- Regenerated:
  - `investigations/bottom_signal_results.json`;
  - `investigations/bottom_signal_results_dual_track_rs.json`;
  - `investigations/bottom_signal_report.md`;
  - `investigations/bottom_signal_report_dual_track_rs.md`;
  - `investigations/bottom_signal_rs_watchlist_report.md`;
  - `investigations/bottom_signal_rs_watchlist_tickers.csv`;
  - Pine/RS candidate artifacts via existing `write_outputs()`.

## Current Result Snapshot
- MB factor ablation rows: `6`.
- Best-config recent validation:
  - window: `2024-05-01` to `2026-04-30`;
  - recent formal signals: `7`;
  - mature 6m checks: `7`;
  - avg 6m return: about `+75.79%`;
  - 6m win rate: `100.00%`;
  - avg 6m adverse drawdown: about `-3.23%`;
  - status: `Pass`.
- RS ticker report now shows `selection=...` for each ticker row.

## Verification
- TDD RED check:
  - `tests.test_bottom_signal_search` initially failed on missing new functions.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 71 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- Static artifact checks:
  - report contains `MB Factor Ablation`;
  - report contains `Recent Validation`;
  - RS watchlist report contains `selection=`;
  - JSON/CSV contain `mbFactorAblation`, `recentValidation`, and `selectionScore`.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Ruff was not run because `.venv` does not currently have the `ruff` module installed.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Pine Table Placement Fix ---
## Objective
- Prevent table overlap when both Pine scripts are loaded in TradingView.
- Clarify that `RS-R` means risk-flagged RS watchlist signal.
- Keep MB strategy logic and RS watchlist logic unchanged.

## Completed
- Kept formal MB table at:
  - `position.top_right`.
- Moved RS watchlist table to:
  - `position.bottom_right`.
- Expanded RS table from 4 rows to 5 rows.
- Added RS table explanation row:
  - `RS-R` / `Risk`.
- Regenerated:
  - `investigations/bottom_signal_pine.pine`;
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.

## Result
- Loading both Pine scripts together should no longer stack both tables in the same corner.
- Formal MB script owns the top-right table.
- RS watchlist script owns the bottom-right table.
- The orange/yellow `RS-R` state is explained directly in the RS table as risk.
- This changes display rendering only. It does not change scores, thresholds, MB logic, RS logic, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 7 seconds.
- Static Pine check:
  - formal table uses `position.top_right`;
  - RS table uses `position.bottom_right`;
  - RS table includes `RS-R` and `Risk`.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Pine Scheme C Display Iteration ---
## Objective
- Implement Scheme C for TradingView display:
  - candle coloring;
  - background highlighting;
  - top-right table with current signal and scores.
- Keep MB strategy logic and RS watchlist logic unchanged.

## Completed
- Updated `generate_pine_script()`.
- Updated `generate_rs_watchlist_pine_script()`.
- Added Pine inputs:
  - `Show Signal Candle Colors`;
  - `Show Signal Background`;
  - `Show Signal Table`;
  - `Show Text Markers`.
- Formal Pine now:
  - uses `barcolor()` for MB/RS/Exit signal candles;
  - uses `bgcolor()` for signal-bar highlighting;
  - uses a `table.new(position.top_right, ...)` dashboard showing current `Signal`, `Bottom`, `RS`, and `Exit`;
  - keeps `plotshape(...)` text markers available but default-disabled with `Show Text Markers=false`.
- RS watchlist Pine now:
  - uses `barcolor()` for `RS-Q` / `RS-R`;
  - uses `bgcolor()` for highlighted RS watchlist bars;
  - uses a top-right table showing `Signal`, `RS Signal`, `Quality`, and `Bottom`;
  - keeps `plotshape(...)` text markers available but default-disabled.
- Score plots remain:
  - `display=display.data_window`.
- Regenerated:
  - `investigations/bottom_signal_pine.pine`;
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.

## Result
- Default display no longer depends on floating labels or always-visible text markers.
- Signal visibility is carried by candle color, background highlight, and current-bar table.
- Optional text markers can still be enabled manually in TradingView.
- This changes display rendering only. It does not change scores, thresholds, MB logic, RS logic, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 8 seconds.
- Static Pine check:
  - `barcolor()` present;
  - `bgcolor()` present;
  - `table.new(position.top_right, ...)` present;
  - `display=display.data_window` present;
  - `Show Text Markers` default-disabled;
  - `label.new` absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Pine Data Window Score Plot Fix ---
## Objective
- Fix TradingView main-chart Y-axis distortion caused by score plots.
- Keep MB strategy logic and RS watchlist logic unchanged.

## Root Cause
- The score plots use 1-100 values while the chart price may be hundreds or thousands.
- Even when `showScoreLines=false`, TradingView can still let plot objects affect main-chart scaling.
- This stretched the Y axis and made marker positions look detached from candles.

## Completed
- Kept `plotshape(...)` markers from the prior iteration.
- Updated score plots in `generate_pine_script()`:
  - `Bottom Score`;
  - `Relative Strength Score`;
  - `Exit Score`.
- Updated score plots in `generate_rs_watchlist_pine_script()`:
  - `RS Signal Score`;
  - `RS Quality Score`.
- Added:
  - `display=display.data_window`.
- Regenerated:
  - `investigations/bottom_signal_pine.pine`;
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.

## Result
- Score values are available in TradingView's data window.
- Score lines no longer render on the main price chart.
- Score plots should no longer affect the main-chart Y-axis scale.
- Markers remain native `plotshape(...)` elements bound to `location.belowbar` / `location.abovebar`.
- This changes display rendering only. It does not change scores, thresholds, MB logic, RS logic, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 8 seconds.
- Static Pine check:
  - `display=display.data_window` present on score plots;
  - `plotshape` present;
  - `label.new` absent;
  - `yloc=` absent;
  - `Marker ATR Offset` absent;
  - `markerOffset` absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Pine Plotshape Marker Fix ---
## Objective
- Replace floating Pine labels with TradingView native `plotshape` markers.
- Keep MB strategy logic and RS watchlist logic unchanged.

## Rationale
- `label.new` creates floating label objects.
- `plotshape` is TradingView's native signal marker series and is better suited for candle-bound signal display.
- User requested replacing all marker `label.new(...)` blocks with `plotshape(...)`.

## Completed
- Updated `generate_pine_script()`.
- Updated `generate_rs_watchlist_pine_script()`.
- Removed all marker `if ... label.new(...)` blocks.
- Formal Pine now uses:
  - `plotshape(showMbWatch, "MB-1", ...)`;
  - `plotshape(showMbMedium, "MB-2", ...)`;
  - `plotshape(showMbStrong, "MB-3", ...)`;
  - `plotshape(showRsWatch, "RS-1", ...)`;
  - `plotshape(showRsMedium, "RS-2", ...)`;
  - `plotshape(showRsStrong, "RS-3", ...)`;
  - `plotshape(exitSignal, "Exit", style=shape.labeldown, location=location.abovebar, text="X", ...)`.
- RS watchlist Pine now uses:
  - `plotshape(rsQualified, "RS-Q", ...)`;
  - `plotshape(rsRisk, "RS-R", ...)`.
- Regenerated:
  - `investigations/bottom_signal_pine.pine`;
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.

## Result
- Pine scripts no longer use:
  - `label.new`;
  - `yloc`;
  - ATR marker offsets;
  - manual marker prices.
- This changes display rendering only. It does not change scores, thresholds, MB logic, RS logic, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 6 seconds.
- Static Pine check:
  - `plotshape` present;
  - `label.new` absent;
  - `yloc=` absent;
  - `Marker ATR Offset` absent;
  - `markerOffset` absent;
  - `buyMarkerPrice` absent;
  - `sellMarkerPrice` absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Pine Auto Bar Label Fix ---
## Objective
- Fix TradingView marker display using the correct engine-managed bar-relative label placement.
- Keep MB strategy logic and RS watchlist logic unchanged.

## Root Cause Correction
- The previous `yloc=yloc.price + ATR offset` approach still produced poor visual behavior because ATR price offsets change visually under zoom.
- Correct TradingView placement for this case is:
  - pass `na` as the y argument;
  - use `yloc=yloc.belowbar` for buy/watch labels;
  - use `yloc=yloc.abovebar` for sell labels.

## Completed
- Updated `generate_pine_script()`.
- Updated `generate_rs_watchlist_pine_script()`.
- Removed:
  - `Marker ATR Offset`;
  - `markerOffset`;
  - `buyMarkerPrice`;
  - `sellMarkerPrice`;
  - `yloc=yloc.price`.
- Formal Pine labels now use:
  - `label.new(bar_index, na, ..., yloc=yloc.belowbar)` for `MB-1/2/3` and `RS-1/2/3`;
  - `label.new(bar_index, na, ..., yloc=yloc.abovebar)` for `X`.
- RS watchlist Pine labels now use:
  - `label.new(bar_index, na, ..., yloc=yloc.belowbar)` for `RS-Q` and `RS-R`.
- Regenerated:
  - `investigations/bottom_signal_pine.pine`;
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.

## Result
- Label placement is now delegated back to the TradingView engine while preserving `bar_index` anchoring.
- This changes display rendering only. It does not change scores, thresholds, MB logic, RS logic, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 6 seconds.
- Static Pine check:
  - `label.new(bar_index, na` present;
  - `yloc=yloc.belowbar` present;
  - `yloc=yloc.abovebar` present in formal Pine;
  - `Marker ATR Offset` absent;
  - `markerOffset` absent;
  - `buyMarkerPrice` absent;
  - `sellMarkerPrice` absent;
  - `yloc=yloc.price` absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Pine Price Anchor Fix ---
## Objective
- Fix TradingView display issue where buy/sell labels still appeared too far from candles after the previous label conversion.
- Keep MB strategy logic and RS watchlist logic unchanged.

## Root Cause
- Previous Pine used `label.new(...)`, but still relied on:
  - `yloc=yloc.belowbar`;
  - `yloc=yloc.abovebar`.
- Those are TradingView candle-relative label layers, not explicit price coordinates, so labels can still appear visually detached from candles during zooming.

## Completed
- Updated `generate_pine_script()`.
- Updated `generate_rs_watchlist_pine_script()`.
- Replaced `yloc.belowbar` / `yloc.abovebar` with:
  - `yloc=yloc.price`.
- Added explicit marker prices:
  - buy/watch labels use `buyMarkerPrice = low - markerOffset`;
  - sell labels use `sellMarkerPrice = high + markerOffset`.
- Added user-adjustable Pine input:
  - `Marker ATR Offset`, default `0.12`.
- Removed `scale=scale.none` from both Pine indicators.
- Regenerated:
  - `investigations/bottom_signal_pine.pine`;
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.

## Result
- Markers are now anchored to explicit price coordinates near each candle.
- If TradingView still shows markers too far away, lower `Marker ATR Offset` in the script settings:
  - try `0.05`;
  - then `0.03` if needed.
- This changes display rendering only. It does not change scores, thresholds, MB logic, RS logic, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 6 seconds.
- Static Pine check:
  - `yloc=yloc.price` present;
  - `buyMarkerPrice` present;
  - `sellMarkerPrice` present in formal Pine;
  - `yloc.belowbar` absent;
  - `yloc.abovebar` absent;
  - `scale=scale.none` absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Pine Label Anchor Fix ---
## Objective
- Fix TradingView display issue where MB/RS buy-sell markers did not visually follow candles during chart zoom.
- Keep MB strategy logic and RS watchlist logic unchanged.

## Completed
- Updated `generate_pine_script()`.
- Updated `generate_rs_watchlist_pine_script()`.
- Replaced Pine `plotshape(...)` markers with candle-anchored `label.new(...)` markers.
- Labels now use:
  - `xloc=xloc.bar_index`;
  - `yloc=yloc.belowbar` for MB/RS buy/watch labels;
  - `yloc=yloc.abovebar` for exit `X`;
  - `max_labels_count=500`.
- Regenerated:
  - `investigations/bottom_signal_pine.pine`;
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.

## Result
- `bottom_signal_pine.pine` no longer uses `plotshape`.
- `bottom_signal_rs_watchlist_pine.pine` no longer uses `plotshape`.
- Labels are bound to bar index and candle-relative y locations, so they should move with candles when zooming or panning in TradingView.
- This changes display rendering only. It does not change scores, thresholds, MB logic, RS logic, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 6 seconds.
- Static Pine check:
  - `label.new` present;
  - `xloc=xloc.bar_index` present;
  - `yloc=yloc.belowbar` present;
  - `yloc=yloc.abovebar` present in formal Pine;
  - `plotshape` absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Candidate CSV Export Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal trading strategy.
- Export RS candidate-level signal rows so ticker summaries can be traced back to exact dates.

## Completed
- Added `RS_WATCHLIST_CANDIDATE_CSV_PATH`.
- Added `generate_rs_watchlist_candidate_csv()`.
- Added `_csv_float()` helper for stable CSV numeric formatting.
- `write_outputs()` now writes:
  - `investigations/bottom_signal_rs_watchlist_candidates.csv`.
- `generate_rs_watchlist_report()` now links the candidate CSV.
- The refresh CLI now prints the candidate CSV path after writing it.
- Added unit coverage for candidate CSV export.
- Refreshed RS watchlist with:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`.

## Result
- New CSV:
  - `investigations/bottom_signal_rs_watchlist_candidates.csv`.
- CSV columns:
  - `symbol`;
  - `date`;
  - `tier`;
  - `qualityPassed`;
  - `qualityScore`;
  - `rsSignalScore`;
  - `relativeStrengthScore`;
  - `bottomScore`;
  - `riskFlags`;
  - `marketDrawdown`;
  - `fwd126`;
  - `adverse126`.
- This is an observation export only. It does not change formal MB scoring, Pine labels, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 68 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 6 seconds.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Ticker CSV Export Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal trading strategy.
- Make RS `Priority / Watch / Avoid` ticker summaries easier to inspect outside Markdown.

## Completed
- Added `RS_WATCHLIST_TICKER_CSV_PATH`.
- Added `generate_rs_watchlist_ticker_csv()`.
- `write_outputs()` now writes:
  - `investigations/bottom_signal_rs_watchlist_tickers.csv`.
- `generate_rs_watchlist_report()` now links the ticker CSV.
- The refresh CLI now prints the CSV path after writing it.
- Added unit coverage for CSV export and backward-compatible action-tier calculation.
- Refreshed RS watchlist with:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`.

## Result
- New CSV:
  - `investigations/bottom_signal_rs_watchlist_tickers.csv`.
- CSV columns:
  - `symbol`;
  - `actionTier`;
  - `qualifiedCount`;
  - `candidateCount`;
  - `avgQualityScore`;
  - `bestDate`;
  - `bestQualityScore`;
  - `riskFlaggedCount`;
  - `avgFwd126`;
  - `avgAdverse126`.
- Current top rows:
  - `META, Priority`;
  - `CRM, Watch`;
  - `AVGO, Priority`.
- This is an observation export only. It does not change formal MB scoring, Pine labels, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 67 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 7 seconds.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Action Summary Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal trading strategy.
- Add an at-a-glance RS observation summary so each refresh shows whether the RS watchlist is improving.

## Completed
- Added `rs_ticker_action_counts()`.
- `summarize_rs_candidate_watchlist()` now returns:
  - `rsTickerActionCounts`.
- `write_outputs()` now backfills `rsTickerActionCounts` for older result payloads.
- `generate_rs_watchlist_report()` now includes:
  - `Action Summary`.
- Added unit coverage for action-count calculation and report output.
- Refreshed RS watchlist with:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`.

## Result
- RS report now shows:
  - `Priority: 2`;
  - `Watch: 7`;
  - `Avoid: 3`.
- JSON result now includes:
  - `bestRsWatchlist.rsCandidateWatchlist.rsTickerActionCounts`.
- This gives a quick health check for RS observation quality without changing formal MB scoring, Pine labels, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 66 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 7 seconds.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Ticker Action Tier Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal trading strategy.
- Make RS ticker-level output easier to act on without changing entry/exit logic.

## Completed
- Added `rs_ticker_action_tier()`.
- `summarize_rs_ticker_watchlist()` now adds:
  - `actionTier`.
- `generate_rs_watchlist_report()` now prints:
  - `action=Priority`;
  - `action=Watch`;
  - `action=Avoid`.
- Added backward-compatible report handling for older summaries that do not yet include `actionTier`.
- Refreshed RS watchlist with:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`.

## Result
- RS ticker summary now separates observation candidates:
  - `Priority`: repeated qualified candidates, good average quality, controlled adverse drawdown, no risk flags.
  - `Watch`: usable but less clean candidates.
  - `Avoid`: weak or unqualified candidates.
- Current RS ticker action distribution:
  - `Priority`: 2.
  - `Watch`: 7.
  - `Avoid`: 3.
- Current Priority tickers:
  - `META`.
  - `AVGO`.
- This does not change formal MB scoring, Pine labels, entry rules, or exit rules.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 66 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
  - PASS, about 7 seconds.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Single-Config Refresh Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal trading strategy.
- Make RS watchlist iteration faster after the previous full `--symbol all` grid search exceeded the command timeout.

## Completed
- Added `refresh_best_rs_watchlist_scan()`.
- Added CLI flag:
  - `--refresh-rs-watchlist`.
- The new mode:
  - loads existing `investigations/bottom_signal_results.json`;
  - uses the current `bestRsWatchlist` config;
  - evaluates only that single RS config over the requested symbols;
  - refreshes `bestRsWatchlist`, `rsCandidateWatchlist`, `rsTickerSummary`, RS report, and RS Pine.
- `generate_rs_watchlist_report()` now shows:
  - refresh mode;
  - symbol count;
  - refresh config.
- Added unit coverage for the single-config refresh path.

## Result
- Fast refresh command:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-rs-watchlist`
- Runtime:
  - about 7 seconds in this workspace.
- Refreshed RS config:
  - `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`.
- Refreshed symbol count:
  - `21`.
- Qualified RS candidates:
  - `12`.
- RS ticker summary count:
  - `12`.
- This solves the immediate iteration-speed problem for RS observation work without changing the formal MB strategy.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 65 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Ticker Summary Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal strategy.
- Improve RS watchlist diagnostics so repeated strong-stock candidates are easier to review by ticker.

## Completed
- Added `summarize_rs_ticker_watchlist()`.
- `summarize_rs_candidate_watchlist()` now returns:
  - `rsTickerSummary`.
- `generate_rs_watchlist_report()` now includes:
  - `Ticker Summary`.
- `write_outputs()` now backfills `rsTickerSummary` from existing top RS candidates when older JSON results do not contain the new field.
- Refreshed outputs from existing results without forcing a full search.

## Result
- New RS report section:
  - `Ticker Summary`.
- Current ticker-level RS summary highlights:
  - `AVGO`: qualified `2`, candidates `2`, avg 6m `+105.76%`.
  - `META`: qualified `2`, candidates `2`, avg 6m `+29.81%`.
  - `CRM`: qualified `2`, candidates `2`, avg 6m `+41.44%`.
  - `V`: qualified `1`, candidates `2`, one risk-flagged candidate.
- This does not change formal MB scoring, Pine labels, or entry/exit rules.

## Search Runtime Note
- Attempted a full `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`.
- It exceeded the 15-minute command timeout.
- Root cause: full staged search is still expensive for a report-only schema refresh.
- Resolution for this iteration:
  - reuse existing result JSON;
  - backfill ticker summary from existing top RS candidates;
  - future full searches will generate ticker summary from the complete RS candidate set.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 64 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Separate RS Watchlist Report Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Add a separate RS-only report so RS watchlist output is easier to review.
- Keep the formal MB report and Pine script unchanged.

## Completed
- Added `RS_WATCHLIST_REPORT_PATH`.
- Added `generate_rs_watchlist_report()`.
- `write_outputs()` now writes:
  - `investigations/bottom_signal_rs_watchlist_report.md`.
- The new report is clearly labeled:
  - `Observation only`;
  - `rs_watchlist_only`.
- The report lists:
  - RS watchlist config;
  - formal-strategy context;
  - watchlist quality;
  - top RS candidates;
  - risk-flagged RS candidates.

## Result
- Formal best remains:
  - `seed_previous_rs_higher_low_best`
  - experimental set: `rs_higher_low_structure`.
- Separate RS watchlist best remains:
  - `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`
  - experimental set: `rs_antidrawdown_repair`.
- Qualified RS candidates:
  - `12`.
- Qualified RS avg 6m return:
  - `+72.01%`.
- Qualified RS avg adverse drawdown:
  - `-4.33%`.
- New report path:
  - `investigations/bottom_signal_rs_watchlist_report.md`.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 63 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS after retrying a transient Windows pycache write-lock.
- JSON validation for `bestRsWatchlist.role == rs_watchlist_only`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Separate RS Watchlist Pine Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Generate a separate TradingView Pine script for the RS watchlist.
- Keep the formal MB Pine script unchanged and tied to `bestConfig`.

## Completed
- Added `RS_WATCHLIST_PINE_PATH`.
- Added `generate_rs_watchlist_pine_script()`.
- `write_outputs()` now writes:
  - `investigations/bottom_signal_pine.pine` for the formal MB-led strategy;
  - `investigations/bottom_signal_rs_watchlist_pine.pine` for RS observation only.
- Updated the report scope section to list both Pine files.
- RS watchlist Pine markers:
  - `RS-Q` for qualified RS watchlist candidates;
  - `RS-R` for risk-flagged RS watchlist candidates.
- RS watchlist Pine includes:
  - `rsQualityScore`;
  - `overextendedRebound`;
  - quality threshold input.
- It intentionally does not include MB markers or exit markers.

## Result
- Formal Pine remains:
  - `investigations/bottom_signal_pine.pine`.
- New RS watchlist Pine:
  - `investigations/bottom_signal_rs_watchlist_pine.pine`.
- The RS script is labeled:
  - `AutoQuant RS Watchlist - Observation only`.
- This separates TradingView usage:
  - use MB Pine for formal bottom-entry strategy;
  - use RS Pine as a strong-stock observation overlay.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 62 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS after retrying a transient Windows pycache write-lock.
- JSON validation for `bestRsWatchlist.role == rs_watchlist_only`
  - PASS.
- Static Pine/report checks for `RS-Q`, `RS-R`, and RS watchlist file references
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Separate RS Watchlist Best Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Separate the formal MB-led strategy best from the RS watchlist best.
- Avoid forcing one config to satisfy both formal-entry and observation-list goals.

## Completed
- Added `select_best_rs_watchlist_result()`.
- Added `bestRsWatchlist` to result JSON.
- Added report section:
  - `Separate RS Watchlist Best`.
- The report now explicitly labels this role as:
  - `rs_watchlist_only`.
- Pine output still uses `bestConfig`, so the TradingView script remains tied to the formal MB-led strategy.

## Result
- Formal best remains:
  - `seed_previous_rs_higher_low_best`
  - experimental set: `rs_higher_low_structure`.
- Separate RS watchlist best is:
  - `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`
  - experimental set: `rs_antidrawdown_repair`.
- RS watchlist best metrics:
  - qualified RS candidates: `12`;
  - qualified RS avg 6m return: `+72.01%`;
  - qualified RS avg adverse drawdown: `-4.33%`.
- Its formal composite score is still `0`, so it is not a formal trading replacement.

## Interpretation
- MB and RS now have separate roles in the artifacts:
  - `bestConfig` = formal MB-led strategy;
  - `bestRsWatchlist` = observation-only RS watchlist config.
- This removes the previous objective conflict.
- Next useful iteration: generate a separate RS watchlist Pine mode or separate RS-only report output, while keeping the formal MB Pine unchanged.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 61 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- JSON validation for `bestRsWatchlist.role == rs_watchlist_only`
  - PASS.
- Report static check for separate RS watchlist section
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Qualified RS Coverage Target Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal entry strategy.
- Add a soft target for qualified RS watchlist coverage, so future config selection prefers more usable RS candidates when MB quality is not harmed.

## Completed
- Added `apply_qualified_rs_watchlist_preference()`.
- Added config values:
  - `qualified_rs_candidate_targets: [3, 8]`;
  - `qualified_rs_avg_fwd126_min: 0.15`;
  - `qualified_rs_avg_adverse126_min: -0.12`.
- Added `qualifiedRsWatchlistScore` to best metrics.
- Added `top_rs_coverage_tradeoffs()` and a report section:
  - `RS Coverage Tradeoffs`.
- The tradeoff section lists configs that find more qualified RS candidates, even if they fail MB/validation gates.

## Result
- Active best config remains `seed_previous_rs_higher_low_best`.
- Active best experimental set remains `rs_higher_low_structure`.
- Strong signals: `39`.
- Avg 6m return: `+39.24%`.
- 6m win rate: `74.36%`.
- Avg 6m adverse drawdown: `-13.80%`.
- Qualified RS watchlist candidates: `2`.
- Qualified RS watchlist score: `66.67`.
- Composite score changed from about `29.95` to `27.95` because qualified RS coverage is below the target minimum of `3`.
- The best remains unchanged, meaning the new coverage preference did not promote a lower-quality MB strategy.

## Tradeoff Findings
- Several configs found more qualified RS candidates but failed other formal strategy gates.
- Example high-coverage config:
  - `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`
  - qualified RS candidates: `12`;
  - qualified RS avg 6m return: about `+72.0%`;
  - qualified RS avg adverse drawdown: about `-4.3%`;
  - composite score: `0`, so it is not a formal replacement.

## Interpretation
- The current best is still the best MB-led formal strategy.
- RS has promising high-coverage variants, but they fail the formal MB/validation framework.
- Next useful iteration: separate RS watchlist optimization from MB formal-entry optimization, instead of forcing one config to satisfy both jobs.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 60 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS.
- JSON validation for config/results
  - PASS.
- Report static check for qualified RS coverage fields
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Overextended Rebound Risk Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal entry strategy.
- Improve RS watchlist live-risk detection after `LLY 2025-04-17` passed the old quality filter but later had a large adverse move.

## Completed
- Added a new at-signal risk flag:
  - `overextended_rebound`.
- The flag triggers when:
  - price has rebounded at least `12%` from the recent 10-day low;
  - price is above the configured SMA distance baseline;
  - the stock has not reached a deep enough drawdown relative to the config threshold.
- Added a quality-score penalty for `overextended_rebound`.
- Updated tests to confirm:
  - `score_from_indicators()` emits `overextended_rebound`;
  - RS candidate quality score penalizes `overextended_rebound`.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - dual-track result/report copies.

## Result
- Active best config remains `seed_previous_rs_higher_low_best`.
- Active best experimental set remains `rs_higher_low_structure`.
- Strong signals: `39`.
- Avg 6m return: `+39.24%`.
- 6m win rate: `74.36%`.
- Avg 6m adverse drawdown: `-13.80%`.
- Recent RS watchlist candidates: `4`.
- Qualified RS watchlist candidates: `2`.
- Recent RS watchlist avg 6m return: `+12.79%`.
- Qualified RS watchlist avg 6m return: `+26.51%`.
- Recent RS watchlist avg adverse drawdown: `-10.57%`.
- Qualified RS watchlist avg adverse drawdown: `-4.86%`.
- Candidate newly downgraded:
  - `LLY 2025-04-17 Watch`, quality `59`, risk `overextended_rebound`.

## Interpretation
- This is the first RS watchlist iteration that specifically catches the recent LLY false-positive style.
- The improvement is only for RS observation/ranking; it does not change MB as the formal backtested strategy.
- The qualified RS sample is now only `2`, so it is cleaner but still too small to treat as a standalone strategy.
- Next useful RS iteration: add a separate "qualified watchlist coverage" target so the system can search for more qualified RS candidates without lowering quality.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 57 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS after rerun with corrected threshold logic.
- JSON validation for config/results
  - PASS.
- Report static check for `risk=overextended_rebound`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Watchlist Quality Filter Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the formal entry strategy.
- Improve RS as a secondary observation list by adding an at-signal quality filter.

## Completed
- Added `rs_candidate_quality_score()` for RS watchlist rows.
- Quality score uses only at-signal data:
  - relative-strength score;
  - RS signal score;
  - bottom score;
  - signal tier;
  - current `riskFlags`.
- Added penalties for:
  - `trend_damage`;
  - `no_repair`;
  - `low_volume`.
- Added config value:
  - `rs_watchlist_quality_threshold: 70`.
- Updated `rsCandidateWatchlist` with:
  - `qualityScore`;
  - `qualityPassed`;
  - `qualifiedRsCandidateCount`;
  - qualified candidate forward-return/adverse-drawdown diagnostics.
- Updated report output so each Top Recent RS Candidate shows:
  - `quality`;
  - `qualified`;
  - `risk`.

## Result
- Active best config remains `seed_previous_rs_higher_low_best`.
- Active best experimental set remains `rs_higher_low_structure`.
- Strong signals: `39`.
- Avg 6m return: `+39.24%`.
- 6m win rate: `74.36%`.
- Avg 6m adverse drawdown: `-13.80%`.
- Recent RS watchlist candidates: `4`.
- Qualified RS watchlist candidates: `3`.
- Recent RS watchlist avg 6m return: `+12.79%`.
- Qualified RS watchlist avg 6m return: `+16.34%`.
- Candidate downgraded by quality filter:
  - `V 2025-03-11 Medium`, quality `59`, risk `no_repair`.

## Interpretation
- The quality filter improves report readability and makes RS usable as an observation list.
- It still does not make RS a formal entry strategy.
- `LLY 2025-04-17` passed the current at-signal quality filter but later had a large adverse move; that means the next useful RS iteration should add a better live risk detector, not use future drawdown directly.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 56 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS.
- JSON validation for config/results
  - PASS.
- Report static check for quality/risk fields
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 RS Secondary Watchlist Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Do not force RS to become the formal entry strategy.
- Make RS useful as a strong-stock observation/ranking layer.

## Completed
- Added `summarize_rs_candidate_watchlist()` to the bottom-signal researcher.
- Added `rsCandidateWatchlist` to each evaluated result.
- Updated the report with:
  - `RS Secondary Watchlist`;
  - `Top Recent RS Candidates`.
- RS watchlist ranking now prioritizes:
  - relative-strength score first;
  - RS signal score second;
  - bottom score third.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - dual-track result/report copies.

## Result
- Active best config remains `seed_previous_rs_higher_low_best`.
- Active best experimental set remains `rs_higher_low_structure`.
- Strong signals: `39`.
- Avg 6m return: `+39.24%`.
- 6m win rate: `74.36%`.
- Avg 6m adverse drawdown: `-13.80%`.
- Recent RS watchlist candidates: `4`.
- Recent RS watchlist avg 6m return: `+12.79%`.
- Recent RS watchlist avg 6m adverse drawdown: `-10.57%`.
- Top recent RS candidates:
  - `V 2025-03-10 Watch`, RS strength `98`, RS signal `76`, fwd6m `+1.08%`.
  - `WMT 2024-08-07 Watch`, RS strength `96`, RS signal `78`, fwd6m `+51.94%`.
  - `LLY 2025-04-17 Watch`, RS strength `96`, RS signal `76`, fwd6m `-4.01%`.
  - `V 2025-03-11 Medium`, RS strength `88`, RS signal `80`, fwd6m `+2.15%`.

## Interpretation
- This confirms RS should remain a secondary watchlist/ranking layer for now.
- The recent RS candidate sample is still small and mixed.
- MB remains the formal backtested bottom-entry strategy.
- Next useful iteration: improve RS watchlist usefulness by adding a "quality filter" for RS candidates, such as requiring less severe 6m adverse drawdown risk or stronger post-pullback recovery confirmation.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 54 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS.
- JSON validation for config/results
  - PASS.
- Report static check for RS watchlist sections
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 MB Primary + RS Secondary Candidate Iteration ---
## Objective
- Continue the `MB 主策略 + RS 二级候选通道` redesign.
- Keep MB as the primary formal bottom strategy.
- Test whether a new RS pullback/recovery candidate can improve recent strong-stock capture.

## Completed
- Added recent 24-month MB vs RS diagnostics to the bottom-signal search result and report.
- Added a soft recent-RS activity preference instead of making recent RS scarcity a hard rejection.
- Added `rs_pullback_repair_v2` as a new experimental RS channel.
- Added Pine inputs/calculation support for `RS Pullback Repair V2`.
- Updated `investigations/bottom_signal_config.json`:
  - added RS pullback windows and drawdown ranges;
  - added recent RS activity validation settings;
  - changed `require_rs_missed_capture` from `true` to `false` so RS is a secondary preference, not a hard gate.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - dual-track result/report copies.

## Result
- Active best config remains `seed_previous_rs_higher_low_best`.
- Active best experimental set remains `rs_higher_low_structure`.
- Strong signals: `39`.
- Avg 6m return: `+39.24%`.
- 6m win rate: `74.36%`.
- Avg 6m adverse drawdown: `-13.80%`.
- Recent 24M window: `2024-05-01` to `2026-04-30`.
- Recent MB Strong signals: `7`.
- Recent RS Strong signals: `0`.
- Recent RS Watch/Medium candidates: `4`.
- Recent RS avg 6m return: `+12.79%`.
- New `rs_pullback_repair_v2` did not improve the best result:
  - best candidate had `9` Strong signals;
  - recent RS candidates: `1`;
  - recent RS avg 6m return: `-32.22%`.

## Interpretation
- User observation is confirmed: RS is weaker than MB and too rare in the last two years.
- `rs_pullback_repair_v2` should stay as an experimental candidate, not become the default.
- Next useful iteration should not try to force RS Strong.
- Better next direction: keep MB as formal entry, and make RS a looser watchlist/ranking layer for stocks that are pulling back but still outperforming the market.

## Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 53 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS after two full runs.
- JSON validation for config/results
  - PASS.
- Pine static marker check
  - PASS; `MB-1/2/3`, `RS-1/2/3`, `X`, and `rsPullbackScore` exist.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-18 23:43 ---
## Completed
- Changed Pine buy marker labels from letter tiers to numeric tiers:
  - `MB-1`, `MB-2`, `MB-3`
  - `RS-1`, `RS-2`, `RS-3`
- Regenerated `investigations/bottom_signal_pine.pine` from current best config.

## Pending
- User still needs to paste/import the updated Pine into TradingView to visually confirm label readability.

## Known Issues
- None for this display-only change.

## Verification
- Verified: `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search` passed with `50` tests.
- Verified: static Pine check confirmed numeric labels exist and old `W/M/S` labels are absent.
- Verified: `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py` passed.
- Verified: `git diff --check` passed.
- Not verified: no live TradingView UI import was performed.
---

--- Session: 2026-05-18 23:41 ---
## Completed
- Fixed Pine signal marker readability for `bottom_signal_pine.pine`.
- Changed buy markers from text-on-shape style to visible label markers:
  - `MB-W`, `MB-M`, `MB-S`
  - `RS-W`, `RS-M`, `RS-S`
- Kept exit marker as red `X`.
- Regenerated `investigations/bottom_signal_pine.pine` from current best config `seed_previous_rs_higher_low_best`.

## Pending
- User still needs to paste/import the updated Pine into TradingView to visually confirm labels render as expected.

## Known Issues
- Previous `shape.circle` / `shape.triangleup` / `shape.diamond` markers had `text="RS"` in source, but TradingView did not visibly show the text.
- The fix uses `shape.labelup`, which is clearer but visually more label-like than the earlier shape-only markers.

## Verification
- Verified: `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search` passed with `50` tests.
- Verified: Pine static check found `MB-W`, `MB-M`, `MB-S`, `RS-W`, `RS-M`, `RS-S`, and `X`.
- Verified: `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py` passed.
- Verified: `git diff --check` passed.
- Not verified: no live TradingView UI import was performed.
---

--- Session: 2026-05-18 23:36 ---
## Completed
- Built and iterated the dual-track bottom signal researcher in `investigations/bottom_signal_search.py`.
- Current active best remains `seed_previous_rs_higher_low_best`, experimental set `rs_higher_low_structure`.
- Tested RS add-on factors: repair/trend confirmation, market divergence, post-crash MA reclaim, and volatility compression.
- Added `seed_configs` plus forced seed promotion so future searches always compare against the known best baseline.
- Pine output now supports `MB`, `RS`, `X` markers plus hidden score lines and experimental toggles.

## Pending
- Decide next exploration direction after the initial RS factor loop.
- Best next technical step is probably to relax/tune failed factors as secondary diagnostic scores instead of using them as hard Strong-score ingredients.
- Consider improving RS channel directly; current RS Strong quality is weaker than MB Strong quality.

## Known Issues
- Several experimental RS factors were too restrictive:
  - `rs_repair_trend_confirm`: best variant produced `0` Strong signals.
  - `rs_post_crash_ma_reclaim`: best variant produced `1` Strong signal with negative 6m result.
  - `rs_volatility_compression`: best variant produced `0` Strong signals.
- `rs_market_divergence` produced usable signals but underperformed the current seed.
- Occasional Windows `__pycache__` write-lock errors appeared during `py_compile`; retry passed, so this was not a source syntax problem.

## Verification
- Verified: `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search` passed with `50` tests.
- Verified: `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators` passed with `4` tests.
- Verified: `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search` passed with `38` tests.
- Verified: `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all` passed after each iteration and regenerated reports/Pine/results.
- Verified: JSON validation, Pine static checks, `git diff --check`, and protected-file diff checks passed.
- Not verified: no live TradingView import was performed inside TradingView UI.
---

== Session: 2026-05-18 Dual-Track RS Volatility Compression Iteration ==
## Objective
- Continue the dual-track bottom signal plan.
- Test whether a volatility-compression factor improves strong-stock capture.
- The factor checks whether ATR/price has fallen from a recent panic high after a meaningful drawdown.

## Completed
- Added `rs_volatility_compression` experimental signal set.
- Updated `add_relative_strength_scores()`:
  - adds `rs_volatility_compression_score`;
  - scores prior crash depth, ATR/price drop from panic high, and short-term volatility stabilization;
  - blends volatility compression into `rs_signal_score` only when this experiment is enabled.
- Updated Pine generation:
  - adds `Use RS Volatility Compression`;
  - calculates `rsVolatilityCompressionScore`;
  - keeps `MB`, `RS`, `X` markers and hidden score lines.
- Updated `investigations/bottom_signal_config.json` to include `rs_volatility_compression`.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Result
- Active best config remains:
  - `seed_previous_rs_higher_low_best`
- Active best experimental signal set: `rs_higher_low_structure`
- Strong signals: `39`
- Avg 3m return: `+21.46%`
- Avg 6m return: `+39.24%`
- Avg 12m return: `+76.67%`
- Avg 6m adverse drawdown: `-13.80%`
- 6m win rate: `74.36%`
- Seed config was promoted into the full search: yes.

## Volatility Compression Comparison
- Best `rs_volatility_compression` config:
  - `btm_dw21_dt12_r7_st21x5_m12x26x9_sma150_atr20_vol20_gap63_entry90_mbo6_rs42_wdeep_repair`
- Composite score: `0.00`
- Strong signals: `0`
- Avg 6m return: `0.00%`
- 6m win rate: `0.00%`
- Avg 6m adverse drawdown: `0.00%`

## Interpretation
- `rs_volatility_compression` is too restrictive in the current formulation.
- It did not produce formal Strong signals in the full-universe search.
- Keep the code as an experimental option, but do not make it the default strategy.
- The current `rs_higher_low_structure` seed remains the best candidate.
- The initial planned RS factor loop has now tested:
  - higher-low structure;
  - market divergence;
  - post-crash MA reclaim;
  - volatility compression;
  - repair/trend confirmation.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 50 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS after one retry; first attempt hit a transient Windows pycache write lock.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated final dual-track outputs.
- JSON validation for bottom signal config/results
  - PASS.
- Pine static marker check
  - PASS; `MB`, `RS`, `X`, hidden score lines, and RS volatility-compression fields exist.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

== Session: 2026-05-18 Dual-Track RS Post-Crash MA Reclaim Iteration ==
## Objective
- Continue the dual-track bottom signal plan.
- Test whether a post-crash MA reclaim factor improves strong-stock capture.
- The factor checks whether a stock suffered a meaningful recent drawdown and then reclaimed short/intermediate moving-average structure.

## Completed
- Added `rs_post_crash_ma_reclaim` experimental signal set.
- Updated `add_relative_strength_scores()`:
  - adds `rs_ma_reclaim_score`;
  - scores prior crash depth, SMA20/SMA50 reclaim, and short recovery slope;
  - blends MA reclaim into `rs_signal_score` only when this experiment is enabled.
- Updated Pine generation:
  - adds `Use RS Post-Crash MA Reclaim`;
  - calculates `rsMaReclaimScore`;
  - keeps `MB`, `RS`, `X` markers and hidden score lines.
- Updated `investigations/bottom_signal_config.json` to include `rs_post_crash_ma_reclaim`.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Result
- Active best config remains:
  - `seed_previous_rs_higher_low_best`
- Active best experimental signal set: `rs_higher_low_structure`
- Strong signals: `39`
- Avg 3m return: `+21.46%`
- Avg 6m return: `+39.24%`
- Avg 12m return: `+76.67%`
- Avg 6m adverse drawdown: `-13.80%`
- 6m win rate: `74.36%`
- Seed config was promoted into the full search: yes.

## Post-Crash MA Reclaim Comparison
- Best `rs_post_crash_ma_reclaim` config:
  - `btm_dw252_dt18_r7_st14x3_m16x35x9_sma100_atr14_vol10_gap21_entry85_mbo3_rs126_wstructure_retest`
- Composite score: `-0.00`
- Strong signals: `1`
- Avg 6m return: `-16.38%`
- 6m win rate: `0.00%`
- Avg 6m adverse drawdown: `-17.91%`

## Interpretation
- `rs_post_crash_ma_reclaim` is too restrictive in the current formulation.
- It did not improve RS strong-stock capture and produced too few formal Strong signals.
- Keep the code as an experimental option, but do not make it the default strategy.
- The current `rs_higher_low_structure` seed remains the best candidate.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 49 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated final dual-track outputs.
- JSON validation for bottom signal config/results
  - PASS.
- Pine static marker check
  - PASS; `MB`, `RS`, `X`, hidden score lines, and RS MA reclaim fields exist.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

== Session: 2026-05-18 Dual-Track RS Market Divergence Iteration ==
## Objective
- Continue the dual-track bottom signal plan.
- Test whether an RS market-divergence factor improves strong-stock capture.
- Market divergence means the stock holds a higher low while QQQ/SPY market drawdown keeps worsening.

## Completed
- Added `rs_market_divergence` experimental signal set.
- Updated `add_relative_strength_scores()`:
  - adds `rs_market_divergence_score`;
  - rewards stock low holding above recent low while market drawdown breaks lower;
  - blends divergence into `rs_signal_score` only when the experiment is enabled.
- Updated Pine generation:
  - adds `Use RS Market Divergence`;
  - calculates `rsMarketDivergenceScore`;
  - keeps `MB`, `RS`, `X` markers and hidden score lines.
- Updated `investigations/bottom_signal_config.json` to include `rs_market_divergence`.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Result
- Active best config remains:
  - `seed_previous_rs_higher_low_best`
- Active best experimental signal set: `rs_higher_low_structure`
- Strong signals: `39`
- Avg 3m return: `+21.46%`
- Avg 6m return: `+39.24%`
- Avg 12m return: `+76.67%`
- Avg 6m adverse drawdown: `-13.80%`
- 6m win rate: `74.36%`
- Seed config was promoted into the full search: yes.

## Market Divergence Comparison
- Best `rs_market_divergence` config:
  - `btm_dw63_dt8_r7_st14x3_m16x35x9_sma100_atr14_vol20_gap42_entry82_mbo0_rs63_wbalanced`
- Composite score: `24.42`
- Strong signals: `40`
- Avg 6m return: `+37.78%`
- 6m win rate: `75.00%`
- Avg 6m adverse drawdown: `-14.06%`
- RS missed-capture count: `3`

## Interpretation
- `rs_market_divergence` produced usable signals, but it did not beat the current `rs_higher_low_structure` seed.
- It slightly increased missed RS captures, but average 6m return was lower and adverse drawdown was slightly worse.
- Keep the code as an experimental option, but do not make it the default strategy.
- Next useful iteration should test `post_crash_ma_reclaim`, which is more directly tied to confirmed recovery after a sharp decline.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 48 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS after one retry; first attempt hit a transient Windows pycache write lock.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated final dual-track outputs.
- JSON validation for bottom signal config/results
  - PASS.
- Pine static marker check
  - PASS; `MB`, `RS`, `X`, hidden score lines, and RS market-divergence fields exist.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

== Session: 2026-05-18 Dual-Track RS Repair Confirmation Iteration ==
## Objective
- Continue the dual-track bottom signal plan.
- Test whether an RS-specific repair/trend confirmation factor improves strong-stock capture.
- Keep prior winning configs in every future search so new iterations do not accidentally forget the current baseline.

## Completed
- Added `rs_repair_trend_confirm` experimental signal set.
- Updated `add_relative_strength_scores()`:
  - adds `rs_confirmation_score`;
  - scores MACD repair, trend reclaim, and price repair confirmation;
  - blends confirmation into `rs_signal_score` only when the new experiment is enabled.
- Updated Pine generation:
  - adds `Use RS Repair Trend Confirm`;
  - calculates `rsConfirmationScore`;
  - keeps score lines hidden by default and keeps `MB`, `RS`, `X` markers.
- Added `seed_configs` support in `investigations/bottom_signal_config.json`.
- Added `promoted_stage_names()` so seed configs always pass the staged DEV filter and get full-universe evaluation.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Result
- Best config:
  - `seed_previous_rs_higher_low_best`
- Experimental signal set: `rs_higher_low_structure`
- Strong signals: `39`
- Avg 3m return: `+21.46%`
- Avg 6m return: `+39.24%`
- Avg 12m return: `+76.67%`
- Avg 6m adverse drawdown: `-13.80%`
- 6m win rate: `74.36%`
- RS missed-capture count: `2`
- Holdout avg 6m return: `+75.79%`
- Validation-window coverage score: `100.00`
- Seed config was promoted into the full search: yes.

## Interpretation
- The new `rs_repair_trend_confirm` experiment did not beat the current baseline.
- Its best searched variant produced `0` Strong signals, so it is too restrictive for the current objective.
- The previous `rs_higher_low_structure` baseline remains the active best candidate.
- The important process improvement is `seed_configs`: future iterations will always compare against the known best candidate instead of depending on the rotating candidate sampler.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 47 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated final dual-track outputs.
- JSON validation for bottom signal config/results
  - PASS.
- Pine static marker check
  - PASS; `MB`, `RS`, `X`, hidden score lines, and RS confirmation fields exist.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

== Session: 2026-05-18 Dual-Track RS Higher-Low Structure Iteration ==
## Objective
- Continue the dual-track bottom signal plan.
- Improve RS quality by adding a higher-low structure factor instead of only changing thresholds.

## Completed
- Added `rs_higher_low_structure` experimental signal set.
- Updated `add_relative_strength_scores()`:
  - adds `rs_structure_score`;
  - blends bottom score, relative-strength score, and higher-low structure score for RS signal scoring when enabled.
- Updated Pine generation:
  - adds `Use RS Higher Low Structure`;
  - calculates `rsStructureScore`;
  - keeps `MB`, `RS`, and `X` markers.
- Updated `investigations/bottom_signal_config.json` to search:
  - `rs_antidrawdown_repair`
  - `rs_higher_low_structure`
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Result
- Best config:
  - `btm_dw126_dt8_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap42_entry82_mbo0_rs63_wbalanced`
- Experimental signal set: `rs_higher_low_structure`
- Strong signals: `39`
- MB Strong: `35`
- RS Strong: `4`
- Watch/Medium to Strong ratio: `2.33x`
- RS missed-capture examples:
  - `LLY` on `2015-08-24`
  - `V` on `2011-08-08`
- Avg 6m return: `+39.24%`
- Avg 12m return: `+76.67%`
- Avg 6m adverse drawdown: `-13.80%`
- 6m win rate: `74.36%`
- Holdout avg 6m return: `+75.79%`
- Validation windows covered: `4/4`
- Walk-forward tested folds: `2/3`

## Interpretation
- This iteration improved over the prior RS-capture config:
  - prior avg 6m `+37.92%`;
  - new avg 6m `+39.24%`.
- Watch/Medium noise improved:
  - prior ratio `2.83x`;
  - new ratio `2.33x`.
- RS channel quality is still weak:
  - RS avg 6m return `+17.73%`;
  - one missed-capture case, `LLY 2015-08-24`, had negative 6m return.
- Next useful iteration should add an RS-specific forward-quality gate or repair confirmation, not more general bottom-score tuning.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 44 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated RS higher-low outputs.
- JSON validation for bottom signal config/results
  - PASS.
- Pine static marker check
  - PASS; `MB`, `RS`, `X`, and RS structure fields exist.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-18 Dual-Track Split Entry Threshold Iteration ==
## Objective
- Continue the dual-track bottom signal plan.
- Try to improve return quality while preserving RS missed-capture.
- Test whether MB can use a stricter entry threshold while RS keeps the original strong-stock threshold.

## Completed
- Added channel-specific entry support in `investigations/bottom_signal_search.py`.
  - `mb_entry_threshold()`
  - `rs_entry_threshold()`
  - `mb_entry_offset`
- Updated Pine generation with `MB Entry Offset`.
- Updated promoted-config refinement:
  - Keep original promoted candidates.
  - Add a limited number of entry-threshold and MB-offset variants.
  - Reduced `refine_top_n` to `10` so full searches remain practical.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Result
- Best config stayed:
  - `btm_dw63_dt8_r7_st14x3_m16x35x9_sma100_atr14_vol20_gap42_entry82_mbo0_rs63_wbalanced`
- Strong signals: `40`
- MB Strong: `37`
- RS Strong: `3`
- Watch/Medium to Strong ratio: `2.83x`
- RS missed-capture examples:
  - `LLY` on `2018-12-17`
  - `V` on `2011-08-08`
- Avg 6m return: `+37.92%`
- 6m win rate: `77.50%`

## Interpretation
- Channel-specific MB/RS entry thresholds are now supported and tested.
- The search did not find an MB-stricter variant that beats the current RS-capture config.
- Raising entry thresholds often improved average return on tiny samples, but removed the RS missed-capture cases or failed validation gates.
- Next useful iteration should target RS signal quality itself, not just stricter MB thresholds.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 43 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated dual-track split-entry outputs.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-18 Dual-Track RS Missed-Capture Iteration ==
## Objective
- Continue the dual-track bottom signal plan.
- Make the search prioritize RS Strong cases that the old QQQ/SPY hard market filter would have blocked.
- Keep Watch/Medium diagnostic density near the target `2-4x` of Strong.

## Completed
- Added dual-track scoring adjustments in `investigations/bottom_signal_search.py`.
  - `apply_watch_medium_ratio_gate()`
  - `apply_relative_strength_capture_preference()`
  - `apply_dual_track_iteration_adjustments()`
- Updated `investigations/bottom_signal_config.json`.
  - Raised Watch/Medium threshold candidates to reduce display noise.
  - Added `require_rs_missed_capture: true`.
  - Added `rs_missed_capture_target: 2`.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Latest Best RS Missed-Capture Config
- Name: `btm_dw63_dt8_r7_st14x3_m16x35x9_sma100_atr14_vol20_gap42_entry82_rs63_wbalanced`
- Strong signals: `40`
- MB Strong: `37`
- RS Strong: `3`
- Watch signals: `81`
- Medium signals: `32`
- Watch/Medium to Strong ratio: `2.83x`
- RS missed-capture count: `2`
- RS missed examples:
  - `LLY` on `2018-12-17`
  - `V` on `2011-08-08`
- Avg 6m return: `+37.92%`
- Avg 12m return: `+75.68%`
- Avg 6m adverse drawdown: `-13.92%`
- 6m win rate: `77.50%`
- Holdout avg 6m return: `+70.52%`
- Validation windows covered: `4/4`
- Walk-forward tested folds: `3/3`

## Interpretation
- This iteration successfully shifted selection toward actual RS missed-capture.
- It also fixed the Watch/Medium density problem:
  - previous ratio `4.47x`;
  - new ratio `2.83x`.
- Tradeoff:
  - prior strict baseline avg 6m `+46.33%`, win rate `80.00%`;
  - new RS-capture config avg 6m `+37.92%`, win rate `77.50%`.
- This is better for discovering strong stocks that broad-market filtering misses, but it gives up some average return quality versus the strict market-bottom baseline.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 40 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated dual-track RS missed-capture outputs.
- JSON validation for bottom signal config/results
  - PASS.
- Pine static marker check
  - PASS; `MB`, `RS`, `X` markers exist and old long labels are absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-18 Dual-Track Bottom Signal RS Iteration ==
## Objective
- Implement the dual-track bottom signal plan:
  - `MB` for market-wide bottom context.
  - `RS` for relative-strength bottom candidates.
  - `Watch`/`Medium` as diagnostic-only layers.
  - `Strong` as the formal backtest layer.

## Completed
- Updated `investigations/bottom_signal_search.py`.
  - Added `relative_strength_score` and `rs_signal_score`.
  - Added dual-track MB/RS position selection.
  - Kept formal metrics on Strong only.
  - Added Signal Funnel, MB vs RS, and Missed Strong Stocks report sections.
  - Added MB/RS/X Pine markers.
- Updated `investigations/bottom_signal_config.json`.
  - Added strategy modes, Watch/Medium threshold candidates, RS windows, RS advantage thresholds, and experimental signal-set config.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`

## Latest Best Dual-Track Config
- Name: `btm_dw126_dt18_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap63_entry82_rs126_wstructure_retest`
- Strong signals: `40`
- MB Strong: `36`
- RS Strong: `4`
- Watch signals: `127`
- Medium signals: `52`
- Watch/Medium to Strong ratio: `4.47x`
- Avg 6m return: `+45.81%`
- Avg 12m return: `+84.65%`
- Avg 6m adverse drawdown: `-13.79%`
- 6m win rate: `77.50%`
- Holdout avg 6m return: `+60.26%`
- Validation windows covered: `4/4`
- Walk-forward tested folds: `3/3`

## Interpretation
- The dual-track implementation works and produces separate MB/RS reporting.
- The selected config stays near the prior baseline quality:
  - Prior baseline avg 6m: `+46.33%`, win rate `80.00%`.
  - New dual-track avg 6m: `+45.81%`, win rate `77.50%`.
- The first RS iteration adds `4` RS Strong signals, all positive at the 6m horizon in historical data.
- No selected RS Strong row was a pure "missed by old QQQ/SPY filter" case. Some candidate configs did find missed cases, but they failed the existing sparse/validation gates.
- Watch/Medium ratio is `4.47x`, slightly above the target `2-4x`; next iteration should tune diagnostic thresholds or add a score penalty before accepting a final display density.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 37 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated dual-track outputs.
- JSON validation for bottom signal config/results
  - PASS.
- Pine static marker check
  - PASS; `MB`, `RS`, `X` markers exist and old long labels are absent.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
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

## v1 → v2: completed in next session
==

== Session: 2026-05-18 Bottom Signal Pine Display Cleanup ==
## Objective
- Make the TradingView Pine chart display icon-only buy/sell signals.
- Reduce score-line interference with candles without changing strategy logic.

## Completed
- Updated `investigations/bottom_signal_search.py` Pine generator:
  - Buy signals now render as green shapes by strength.
  - Sell signals now render as a red down triangle.
  - Visible chart labels no longer use `WATCH`, `BOTTOM`, or `EXIT` text.
  - Score lines are hidden by default behind `Show Score Lines`.
  - Pine indicator uses `scale=scale.none` so score lines do not resize the price chart.
- Regenerated `investigations/bottom_signal_pine.pine` from existing `bottom_signal_results.json` best config only.
- Did not rerun the strategy search because this was display-only.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 34 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- Pine static content check
  - PASS; no visible text labels remain and expected shapes/options exist.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Date-Split Cross Validation ==
## Objective
- Continue iterating toward sparse, high-conviction bottom entries.
- Prefer configs that work across QQQ/SPY, individual stocks, and a post-2022 holdout segment.

## Completed
- Added date-split validation helpers to `investigations/bottom_signal_search.py`.
  - `summarize_date_split_validation()`
  - `date_split_coverage_score()`
  - `apply_date_split_gate()`
- Updated scoring so the selected config is penalized unless holdout coverage exists after `2022-12-31`.
- Updated `investigations/bottom_signal_config.json`.
  - `date_split_cutoff`: `2022-12-31`
  - `holdout_index_signal_min`: `1`
  - `holdout_individual_signal_min`: `6`
  - `require_date_split_coverage`: `true`
- Updated `investigations/bottom_signal_report.md` to show train/holdout signal counts and holdout return/drawdown metrics.
- Updated `docs/plans/bottom_signal_iteration_2026-05-17.md` with the date-split validation rule.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Latest Best Bottom Signal Config
- Name: `btm_dw126_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap63_wstructure_retest`
- Signals: `43`
- QQQ/SPY signals: `6`
- Individual-stock signals: `37`
- Avg 3m return: `+23.91%`
- Avg 6m return: `+46.26%`
- Avg 12m return: `+80.35%`
- Avg 6m adverse drawdown: `-13.44%`
- 6m win rate: `79.07%`
- Holdout signals after 2022-12-31: `9`
- Holdout QQQ/SPY signals: `1`
- Holdout individual-stock signals: `8`
- Holdout avg 6m return: `+64.00%`
- Holdout avg 6m adverse drawdown: `-3.67%`
- Holdout 6m win rate: `100.00%`

## Interpretation
- The strategy remains intentionally low frequency: 43 entries across 21 symbols and roughly 18 years.
- In the current strict market-drawdown setup, no promoted candidate produced 2 or more post-2022 QQQ/SPY holdout signals, so `holdout_index_signal_min=1` is intentional rather than loose.
- This is still historical research, not a production trading rule. The next meaningful improvement is a stricter walk-forward selection process, not simply adding more indicator knobs.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 23 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated bottom-signal outputs.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `uv run run.py`
  - PASS with existing warnings from `run.py` about open trades and a path message; exit code was 0.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Validation Windows And Sparse Preference ==
## Objective
- Continue iterating toward fewer, higher-conviction bottom entries.
- Require the best config to work across QQQ/SPY, individual stocks, post-2022 holdout data, and multiple historical drawdown windows.

## Completed
- Added validation-window helpers to `investigations/bottom_signal_search.py`.
  - `summarize_validation_windows()`
  - `validation_window_coverage_score()`
  - `apply_validation_window_gate()`
- Added tests for validation-window coverage and gate behavior.
- Updated `investigations/bottom_signal_config.json`.
  - Added validation windows:
    - 2008-2010 global financial crisis window.
    - 2020 Covid crash window.
    - 2022 inflation bear-market window.
    - 2023+ recent holdout window.
  - Set `require_validation_window_coverage=true`.
  - Tightened sparse signal preference:
    - `signal_count_target`: `30`
    - `signal_count_max`: `50`
  - Aligned full individual-stock coverage with lower frequency:
    - `individual_signal_min`: `30`
- Updated `investigations/bottom_signal_report.md` to show validation-window metrics.
- Updated `docs/plans/bottom_signal_iteration_2026-05-17.md` to document the validation-window rule.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Latest Best Bottom Signal Config
- Name: `btm_dw126_dt18_r10_st14x3_m8x21x5_sma50_atr10_vol50_gap42_wstructure_retest`
- Signals: `38`
- QQQ/SPY signals: `6`
- Individual-stock signals: `32`
- Avg 3m return: `+25.05%`
- Avg 6m return: `+46.69%`
- Avg 12m return: `+84.74%`
- Avg 6m adverse drawdown: `-13.68%`
- 6m win rate: `76.32%`
- Holdout signals after 2022-12-31: `7`
- Holdout QQQ/SPY signals: `1`
- Holdout individual-stock signals: `6`
- Holdout avg 6m return: `+75.00%`
- Holdout avg 6m adverse drawdown: `-4.23%`
- Holdout 6m win rate: `100.00%`
- Validation windows covered: `4/4`
- Positive validation windows: `4/4`
- Validation-window worst avg 6m return: `+7.82%`

## Interpretation
- This iteration intentionally chose a lower-frequency winner than the previous 43-46 signal configs.
- The current best config has fewer total signals while still passing QQQ/SPY, individual-stock, holdout, and 4-window validation.
- The strategy is still research-grade. The next improvement should be true walk-forward selection, where each period chooses parameters only from earlier data and tests later data.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 25 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated bottom-signal outputs.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `uv run run.py`
  - PASS with existing warnings from `run.py` about open trades and a path message; exit code was 0.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Walk-Forward Diagnostic ==
## Objective
- Continue validating the sparse bottom-entry strategy without simply adding more indicator knobs.
- Add a walk-forward diagnostic where each test period selects a config using only earlier signals.

## Completed
- Added walk-forward helpers to `investigations/bottom_signal_search.py`.
  - `_signals_between()`
  - `_signal_subset_summary()`
  - `_walk_forward_selection_score()`
  - `run_walk_forward_diagnostics()`
- Changed stored bottom-signal result payloads to keep full signal lists for promoted configs, so diagnostics do not depend on truncated signal history.
- Added walk-forward folds to `investigations/bottom_signal_config.json`.
  - Select through 2019, test 2020.
  - Select through 2021, test 2022.
  - Select through 2022, test 2023-2026.
- Updated `investigations/bottom_signal_report.md` with a Walk-Forward Diagnostic section.
- Updated `docs/plans/bottom_signal_iteration_2026-05-17.md` to document walk-forward diagnostics.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Latest Best Bottom Signal Config
- Unchanged from prior sparse/window iteration:
  - `btm_dw126_dt18_r10_st14x3_m8x21x5_sma50_atr10_vol50_gap42_wstructure_retest`
- Signals: `38`
- Avg 6m return: `+46.69%`
- Avg 12m return: `+84.74%`
- Validation windows covered: `4/4`

## Walk-Forward Diagnostic
- Tested folds: `2/3`
- Positive tested folds: `2/2`
- Avg test 6m return: `+85.99%`
- Worst tested 6m return: `+4.00%`
- Avg tested 6m win rate: `72.22%`
- Fold details:
  - `select_to_2019_test_2020`: 5 test signals, avg 6m `+167.99%`, win rate `100.00%`.
  - `select_to_2021_test_2022`: 9 test signals, avg 6m `+4.00%`, win rate `44.44%`.
  - `select_to_2022_test_recent`: 2 test signals, avg 6m `+133.90%`, win rate `100.00%`, but not counted as fully tested because min test signals is 4.

## Interpretation
- Walk-forward did not overturn the current sparse best config, but it exposed a weak point:
  - the 2022 fold is only mildly positive with weak win rate;
  - the 2023+ fold is positive but too sparse to treat as conclusive.
- The current Pine default remains the full-sample sparse/window winner, not the per-fold walk-forward selected config.
- Next meaningful work would be a walk-forward-aware selector that can decide whether to freeze the full-sample winner or switch to a more robust family.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 26 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated bottom-signal outputs.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `uv run run.py`
  - PASS with existing warnings from `run.py` about open trades and a path message; exit code was 0.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Local Bottom Capture Gate ==
## Objective
- Continue aligning the strategy with the user's priority:
  - few entries;
  - entries should be close to staged or historical bottoms;
  - still cross-validated across QQQ/SPY and individual stocks.

## Completed
- Added bottom-capture evaluation to `investigations/bottom_signal_search.py`.
  - `local_bottom_gap()` measures how far the signal close is from the local low around the signal.
  - `bottom_capture_score()` converts that gap into a 0-100 capture score.
  - `apply_bottom_capture_gate()` rejects configs when too many signals are far from local lows.
- Each signal now records:
  - `localBottomGap`
  - `bottomCaptureScore`
- Updated scoring and report metrics:
  - average local-bottom gap;
  - average bottom-capture score;
  - poor bottom-capture rate;
  - poor bottom-capture penalty.
- Updated `investigations/bottom_signal_config.json`.
  - `bottom_capture_before`: `21`
  - `bottom_capture_after`: `21`
  - `poor_bottom_capture_gap`: `0.12`
  - `poor_bottom_capture_rate_limit`: `0.35`
  - `require_bottom_capture_rate_limit`: `true`
- Updated `docs/plans/bottom_signal_iteration_2026-05-17.md` with the bottom-capture rule.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Latest Best Bottom Signal Config
- Previous sparse/window winner was rejected by the new bottom-capture hard gate.
- New best:
  - `btm_dw63_dt18_r7_st9x3_m8x21x5_sma50_atr10_vol50_gap42_wstructure_retest`
- Signals: `38`
- QQQ/SPY signals: `5`
- Individual-stock signals: `33`
- Avg 3m return: `+25.73%`
- Avg 6m return: `+46.01%`
- Avg 12m return: `+82.01%`
- Avg 6m adverse drawdown: `-14.33%`
- 6m win rate: `68.42%`
- Holdout signals after 2022-12-31: `7`
- Holdout avg 6m return: `+75.00%`
- Validation windows covered: `4/4`
- Validation-window worst avg 6m return: `+4.59%`
- Avg local-bottom gap: `10.63%`
- Avg bottom-capture score: `51.95`
- Poor bottom-capture rate: `34.21%`

## Interpretation
- This iteration deliberately traded a little return and win rate for better bottom-capture discipline.
- The new default is more aligned with "do not shoot often, but shoot closer to staged bottoms."
- The poor bottom-capture rate is still close to the limit, so the next improvement should focus on reducing early entries without destroying QQQ/SPY and individual-stock coverage.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 29 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated bottom-signal outputs.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `uv run run.py`
  - PASS with existing warnings from `run.py` about open trades and a path message; exit code was 0.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Hard Sparse Cap And Entry Threshold Search ==
## Objective
- Continue tightening the bottom-entry strategy toward:
  - not many entries;
  - close-to-bottom entries;
  - QQQ/SPY and individual-stock cross-validation;
  - complete validation-window coverage.

## Completed
- Added entry-threshold candidate search.
  - `entry_thresholds`: `[82, 85, 88, 90]`
  - Candidate names now include `_entryXX`.
- Increased search breadth.
  - `max_configs`: `720`
  - `promote_top_n`: `200`
- Added hard signal-count cap.
  - `signal_count_target`: `25`
  - `signal_count_max`: `40`
  - `require_signal_count_hard_max`: `true`
- Added hard validation-window coverage.
  - `require_validation_window_hard_coverage`: `true`
- Fixed staged DEV screening.
  - DEV screening now uses relaxed validation settings so full-universe hard gates do not wrongly reject configs before full-market evaluation.
- Added tests for:
  - entry-threshold candidate generation;
  - hard signal-count rejection;
  - hard validation-window rejection;
  - relaxed staged-search settings.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Latest Best Bottom Signal Config
- New strict best:
  - `btm_dw42_dt12_r10_st14x3_m8x21x5_sma50_atr10_vol10_gap42_entry82_wstructure_retest`
- Signals: `40`
- QQQ/SPY signals: `5`
- Individual-stock signals: `35`
- Avg 3m return: `+24.19%`
- Avg 6m return: `+46.33%`
- Avg 12m return: `+77.25%`
- Avg 6m adverse drawdown: `-13.31%`
- 6m win rate: `80.00%`
- Holdout signals after 2022-12-31: `9`
- Holdout avg 6m return: `+64.00%`
- Validation windows covered: `4/4`
- Validation-window worst avg 6m return: `+14.06%`
- Avg local-bottom gap: `9.45%`
- Avg bottom-capture score: `53.67`
- Poor bottom-capture rate: `32.50%`

## Walk-Forward Diagnostic
- Tested folds: `3/3`
- Positive tested folds: `3/3`
- Avg test 6m return: `+83.22%`
- Worst test 6m return: `+1.33%`
- Avg test 6m win rate: `80.00%`
- Fold details:
  - `select_to_2019_test_2020`: 3 test signals, avg 6m `+168.20%`, win rate `100.00%`.
  - `select_to_2021_test_2022`: 10 test signals, avg 6m `+1.33%`, win rate `40.00%`.
  - `select_to_2022_test_recent`: 6 test signals, avg 6m `+80.15%`, win rate `100.00%`.

## Interpretation
- This is stricter than the previous 38-signal version because it enforces all hard gates instead of accepting partial validation-window coverage.
- Only 4 promoted configs passed every hard gate in the latest run.
- The weakest remaining area is still the 2022 walk-forward fold: it is positive, but only mildly and with a weak win rate.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 33 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated bottom-signal outputs.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `uv run run.py`
  - PASS with existing warnings from `run.py` about open trades and a path message; exit code was 0.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Validation Window Win-Rate Gate ==
## Objective
- Continue tightening the sparse bottom strategy around the remaining weak area:
  - 2022-style grinding bear markets.
- Require each validation window to have acceptable 6-month win rate, not only positive average return.

## Completed
- Extended `summarize_validation_windows()` in `investigations/bottom_signal_search.py`.
  - Adds `validationWindowWorstWinRate126`.
  - Adds `validationWindowAvgWinRate126`.
  - Incorporates validation-window win rate into `validationWindowScore`.
- Added `apply_validation_window_quality_gate()`.
  - Hard rejects configs when the worst validation-window win rate is below the configured minimum.
- Updated `investigations/bottom_signal_config.json`.
  - `validation_window_min_win_rate`: `0.5`
  - `require_validation_window_min_win_rate`: `true`
- Updated `investigations/bottom_signal_report.md` with validation-window win-rate metrics.
- Updated `docs/plans/bottom_signal_iteration_2026-05-17.md`.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Latest Best Bottom Signal Config
- Best remains:
  - `btm_dw42_dt12_r10_st14x3_m8x21x5_sma50_atr10_vol10_gap42_entry82_wstructure_retest`
- Signals: `40`
- QQQ/SPY signals: `5`
- Individual-stock signals: `35`
- Avg 3m return: `+24.19%`
- Avg 6m return: `+46.33%`
- Avg 12m return: `+77.25%`
- Avg 6m adverse drawdown: `-13.31%`
- 6m win rate: `80.00%`
- Holdout signals after 2022-12-31: `9`
- Holdout avg 6m return: `+64.00%`
- Validation windows covered: `4/4`
- Validation-window worst avg 6m return: `+14.06%`
- Validation-window average 6m win rate: `82.95%`
- Validation-window worst 6m win rate: `50.00%`
- Avg local-bottom gap: `9.45%`
- Poor bottom-capture rate: `32.50%`

## Interpretation
- Only 1 promoted config now passes every hard gate.
- The 50% validation-window win-rate threshold is the current boundary. Raising it above 50% removes all candidates in the current search space.
- The remaining weak point is still 2022-style grinding bear-market behavior, but it now must at least be non-negative and at least 50% win-rate at the validation-window level.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 34 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS; regenerated bottom-signal outputs.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `uv run run.py`
  - PASS with existing warnings from `run.py` about open trades and a path message; exit code was 0.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-13 Index Shallow Pullback Radar ==
## User Feedback
- `bottom_reversal` is good for deep crash / multi-bottom setups, but it misses some SPY/QQQ index-style shallow pullbacks.
- User asked to add `index_shallow_pullback` and give strength labels that are clearly different from `bottom_reversal`.

## Completed
- Added `index_shallow_pullback` buy strategy in `investigations/uptrend_dip_search.py`.
- New index shallow-pullback components:
  - orderly 252-day drawdown band
  - EMA21 / EMA55 / SMA200 support proximity
  - RSI reset near the low-40s
  - recent 5-day / 20-day decline
  - trend-health score using EMA stack, SMA200 buffer, and EMA55 slope
- Added strategy-specific candidate weight sets with `idx_...` config names.
- Added `score_buy_index_shallow_pullback()` and wired it into:
  - `compute_buy_score()`
  - stage-2 scoring
  - long-term radar evaluation
  - generated Pine Script
- Added distinct long-term add-on labels:
  - `Deep Bottom - Strong/Medium/Watch`
  - `Shallow Pullback - Strong/Medium/Watch`
  - `Momentum Add-On - Strong/Medium/Watch`
- Added an index-specific re-signal rule:
  - normal minimum gap remains 63 trading bars
  - for `index_shallow_pullback` only, a new signal inside the gap is allowed if drawdown deepens by at least 4 percentage points
  - this avoids blindly lowering the gap for all strategies
- Updated reports to show a `Strength` column in add-on signal logs.
- Added a long-term radar strategy comparison table to `uptrend_dip_report.md`, so `index_shallow_pullback` remains visible even when `bottom_reversal` is the global default.
- Added an `Index Shallow Pullback Signal Log` report section for recent SPY/QQQ-style shallow pullback signals.
- Added `techSubsetRadarSummary` to generated results and report so the tech-stock subset is visible without manual post-processing.
- Added `recommendedRadarBySymbol` and `techSubsetRecommendedRadarSummary` to separate:
  - global default strategy applied to tech stocks
  - per-symbol best strategy for each tech stock
- Added a `Current Interpretation` section to the report:
  - `bottom_reversal` is the current broad tech-stock add-on default.
  - per-symbol configs are stronger but more in-sample.
  - `index_shallow_pullback` is useful as a higher-frequency ETF/index radar, not the return-maximizing default.
  - Stage 2 remains a short-term trade comparison, not the final long-term sell rule.
- Report tables now show full config names instead of truncating them, so thresholds and sell/stop settings remain reproducible.
- Added TradingView usage notes to the report:
  - generated default is the broad long-term add-on radar
  - standalone Pine can switch between `bottom_reversal` and `index_shallow_pullback`
  - `IDX` and `BTM` labels should be treated as separate signal families
- Added report caveats:
  - current numbers are grid-search/in-sample, not walk-forward out-of-sample
  - global default is the conservative read
  - per-symbol best configs are useful but easier to overfit
  - next validation should freeze candidate configs and run date-split or rolling walk-forward tests
- Added recent tech signal window summaries (`startDate=2023-01-01`) for:
  - global default applied to tech stocks
  - per-symbol best tech configs
- Added yearly breakdown for global-default tech-stock signals from 2023 onward.
- Added latest global-default tech-stock signal log to the report and JSON.
- Added report executive summary with current default, tech subset metrics, date-split holdout metrics, latest tech signal, and research status.
- Added `Candidate Configs To Freeze Next` report section:
  - broad long-term default
  - best trend-breakout family
  - best tech-breakout family
  - best index-shallow-pullback family
  - fixed a report-variable shadowing issue so broad default points to long-term radar config, not Stage 2 short-trade config
- Added date-split radar diagnostic:
  - train/select on QQQ/SPY signals dated up to 2022-12-31
  - evaluate the frozen selected config on tech-stock signals dated 2023-01-01 or later
  - clearly labeled as signal-date split diagnostic, not full rolling walk-forward
- Updated Pine outputs:
  - `investigations/uptrend_dip_pine.pine` includes `index_shallow_pullback` and `IDX/BTM` strength labels.
  - `investigations/long_term_addon_radar.pine` now supports mode switching between `bottom_reversal` and `index_shallow_pullback`.
  - Removed both `ta.sum` and `math.sum` from Pine output; Pine now uses a local `rolling_count()` helper for better TradingView compatibility.
  - Generated Pine output is now ASCII-only to avoid TradingView editor issues with decorative Unicode comments.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 13 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - Replaced with non-`.pyc` `compile()` syntax check after Windows locked `tests/__pycache__`.
  - PASS for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - Long-term radar still selected `bottom_reversal`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.2%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - Long-term radar still selected `bottom_reversal`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -6.5%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
  - Report now includes best long-term radar config by strategy family.
  - Global default on tech subset: avg 6m +29.0%, avg 12m +54.8%, avg 24m +175.9%, avg 12m max drawdown -19.6%.
  - Per-symbol best tech subset: avg 6m +40.4%, avg 12m +102.0%, avg 24m +247.1%, avg 12m max drawdown -13.7%.
  - Recent 2023+ global default tech signals: 31 signals, 22 mature 12m, avg 12m +62.5%, avg 12m max drawdown -13.0%.
  - Recent 2023+ per-symbol best tech signals: 34 signals, 22 mature 12m, avg 12m +141.0%, avg 12m max drawdown -9.1%.
  - Yearly global-default tech signal split:
    - 2023: 3 signals, 3 mature 12m, avg 12m +114.4%.
    - 2024: 8 signals, 8 mature 12m, avg 12m +60.6%.
    - 2025: 14 signals, 11 mature 12m, avg 12m +49.8%.
    - 2026: 6 signals, 0 mature 12m; too recent to score 12m.
  - Date-split diagnostic:
    - trained config remains `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
    - 2023+ tech holdout summary: avg 6m +55.3%, avg 12m +64.1%, avg 24m +223.4%, avg 12m max drawdown -11.8%.
  - Latest global-default tech signals include 2026 signals in CRM, AMZN, MSFT, CRWD, PLTR, and META.
- `git diff --check`
  - PASS after normalizing `uptrend_dip_results.json` to LF and updating the results writer to use `newline="\n"`.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS; generated JSON remains valid.
- Report-only regeneration:
  - Rebuilt `uptrend_dip_report.md` from existing `uptrend_dip_results.json` after adding interpretation text.
  - Rebuilt again after removing config-name truncation from per-symbol tables.
  - Rebuilt again after adding TradingView usage notes.
  - Rebuilt again after adding validation caveats.
  - Rebuilt again after adding the executive summary.
- Pine compatibility check:
  - `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no Pine sum function remains.
  - `uptrend_dip_pine.pine` and `long_term_addon_radar.pine` both pass `text.isascii()`.

## Index Shallow Pullback Diagnostic
- The new strategy does not beat `bottom_reversal` as the global default, but it gives a separate index/ETF mode.
- Example SPY config inspected: `idx_d0.15_b0.25_r0.20_c0.25_v0.15_t50`.
- It now emits shallow-pullback labels such as:
  - 2025-02-21: `Shallow Pullback - Medium`
  - 2025-03-06: `Shallow Pullback - Medium`
  - 2025-04-03: `Shallow Pullback - Medium`
  - 2026-03-20: `Shallow Pullback - Medium`
- Interpretation:
  - 2025 April was previously blocked mainly by the 63-bar gap; the new drawdown-deepening re-signal rule allows a fresh SPY signal on a bearish candle.
  - In cached data, the 2026 SPY pullback produced bearish-candle signals mainly in March before the April rebound, not on the later April green rebound bars.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-19 QQQ Observation Pine Merge Continuation ==
## Objective
- Continue the QQQ missed-bottom observation plan.
- Fix the merged Pine artifact so it truly combines the MB/RS/OBS layers plus the separate RS watchlist quality layer.
- Keep official MB Strong and RS Strong logic unchanged.

## Assumptions
- Observation signals are still candidate/reference signals only.
- RS-Q and RS-R are display/alert aids in the merged Pine, not new official entry signals.
- Do not touch `config.py`, `prepare.py`, `run.py`, or `versions/`.

## TDD
- Added a failing assertion that `generate_merged_observation_pine_script()` includes:
  - `qualityThreshold`
  - `rsQualityScore`
  - `RS-Q` / `RS-R`
  - RS quality table row
  - RS watchlist alert conditions
- Verified the targeted test failed before implementation.
- Added the minimum generator changes to pass it.

## Completed
- Updated `investigations/bottom_signal_search.py` merged Pine generator:
  - Added `RS Quality Threshold` input.
  - Added RS quality score and risk penalty calculation.
  - Added `RS-Q` and `RS-R` display states.
  - Added table row for RS Quality.
  - Added `RS Watchlist Qualified` and `RS Watchlist Risk` alert conditions.
- Regenerated:
  - `investigations/bottom_signal_observation_report.md`
  - `investigations/bottom_signal_observation_signals.csv`
  - `investigations/bottom_signal_merged_observation.pine`
  - `investigations/bottom_signal_results.json`

## Current Observation Result
- Observation signals: 50.
- Upgrade candidate score: 81.59.
- QQQ 2022-10-01 to 2022-12-31: covered.
- QQQ 2026-03-01 to 2026-03-31: covered.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_merged_observation_pine_script_includes_rs_watchlist_quality_layer`
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 83 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals=50, upgradeScore=81.59.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `Select-String -Path investigations\\bottom_signal_merged_observation.pine -Pattern "RS-Q|RS-R|rsQualityScore|qualityThreshold|RS Watchlist|OBS-D|OBS-S"`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Config And Acceleration ==
## Objective
- Move bottom-signal experiment tuning out of Python defaults and into a config file.
- Speed up repeated iteration by precomputing indicators once per ticker and using staged search.
- Continue on a new exploration branch.

## Branch
- Switched from `autoresearch/apr29` to `autoresearch/may17-baseline-next`.

## Completed
- Added `investigations/bottom_signal_config.json`.
  - Candidate indicator periods, thresholds, score weights, objective weights, and stage-search settings now live in JSON.
- Updated `investigations/bottom_signal_search.py`.
  - Loads experiment settings from JSON with `--config`.
  - Unions indicator requirements across candidate configs.
  - Precomputes indicator frames once per ticker.
  - Caches enriched indicator parquet files under `investigations/.cache/bottom_signal_indicators/`.
  - Uses staged search by default:
    - DEV symbols first.
    - Promote top configs.
    - Full ticker evaluation only for promoted configs.
- Added `docs/plans/bottom_signal_iteration_2026-05-17.md`.
  - Documents the config-driven iteration baseline and speed plan.
- Updated `tests/test_bottom_signal_search.py`.
  - Covers config loading, indicator spec union, and one-build-per-symbol precompute behavior.

## Latest Bottom Signal Run
- Command:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
- Best config:
  - `btm_dw252_dt12_r10_st9x3_m12x26x9_sma200_atr20_vol20`
- Metrics:
  - Composite score: `57.46`
  - Signals: `3244`
  - Avg 3m return: `+8.80%`
  - Avg 6m return: `+17.93%`
  - Avg 12m return: `+37.29%`
  - Avg 6m adverse drawdown: `-11.12%`
- Runtime after staged search:
  - about `22.66` seconds for `--symbol all`.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 9 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol QQQ`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all`
  - PASS.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Market Repair Preference ==
## Objective
- Continue refining sparse bottom entries so signals occur closer to stage or
  historical bottoms.
- Preserve QQQ/SPY and individual-stock cross-validation.

## Completed
- Tested market-repair behavior offline.
  - Hard market-repair filtering produced too few QQQ/SPY samples.
  - A soft market-repair score was added instead.
- Added market-repair scoring:
  - Market symbols: `QQQ`, `SPY`
  - Repair window: `21`
  - Repair target: `3%`
  - Scoring now favors signals after QQQ/SPY have started lifting from local lows.
- Shifted the quality objective slightly away from pure forward return and toward
  market repair / confirmation.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Current Best Repair-Preference Config
- Name: `btm_dw42_dt18_r10_st14x3_m8x21x5_sma50_atr10_vol10_gap63_wstructure_retest`
- Entry score threshold: `82`
- Min signal gap: `63` bars
- Market filter: QQQ/SPY 126-bar drawdown <= `-20%`
- Drawdown: 42-day window, `-18%`
- RSI: `10`
- Stochastic: `14, 3`
- MACD: `8, 21, 5`
- SMA distance: `50`
- ATR: `10`
- Volume window: `10`
- Weights:
  - drawdown `0.28`
  - momentum `0.18`
  - repair `0.18`
  - structure `0.26`
  - volume `0.05`
  - MA distance `0.05`

## Current Metrics
- Composite score: `55.73`
- Signals: `40`
- Active symbols: `20`
- QQQ/SPY signals: `5`
- Individual-stock signals: `35`
- Avg 3m return: `+23.34%`
- Avg 6m return: `+45.88%`
- Avg 12m return: `+78.78%`
- Avg 6m adverse drawdown: `-13.7%`
- 6m adverse tail rate: `17.5%`
- 6m win rate: `80.0%`
- Avg market repair: `1.86%`

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 21 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Sparse Gap And Tail Risk ==
## Objective
- Continue pushing the bottom signal toward fewer, higher-conviction stage or
  historical bottom entries.
- Keep QQQ/SPY and individual-stock cross-validation.

## Completed
- Tested deeper broad-market filters:
  - QQQ/SPY 126-bar drawdown `-20%` improved the prior `-18%` run.
  - `-22%` became too strict and lost individual-stock coverage.
- Added 6m adverse-tail penalty:
  - Default tail threshold: `-25%`
  - This penalizes configs that buy too early and tolerate deep drawdowns before
    eventual recovery.
- Added `min_signal_gaps` as a candidate parameter:
  - Tested `21`, `42`, `63` bars.
  - Best current sparse baseline uses `63` bars.
- Adjusted validation config toward fewer signals:
  - `individual_signal_min`: `35`
  - `signal_count_target`: `45`
  - `signal_count_max`: `100`
- Updated Pine generation:
  - includes selected score weights;
  - includes QQQ/SPY market filter;
  - includes `Min Signal Gap`;
  - only plots bottom labels when the entry score and gap rules pass.

## Current Best Sparse Gap Config
- Name: `btm_dw126_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap63_wstructure_retest`
- Entry score threshold: `82`
- Min signal gap: `63` bars
- Market filter: QQQ/SPY 126-bar drawdown <= `-20%`
- Drawdown: 126-day window, `-8%`
- RSI: `7`
- Stochastic: `9, 3`
- MACD: `8, 21, 5`
- SMA distance: `50`
- ATR: `10`
- Volume window: `10`
- Weights:
  - drawdown `0.28`
  - momentum `0.18`
  - repair `0.18`
  - structure `0.26`
  - volume `0.05`
  - MA distance `0.05`

## Current Metrics
- Composite score: `59.89`
- Signals: `43`
- Active symbols: `20`
- QQQ/SPY signals: `6`
- Individual-stock signals: `37`
- Avg 3m return: `+23.91%`
- Avg 6m return: `+46.26%`
- Avg 12m return: `+80.35%`
- Avg 6m adverse drawdown: `-13.44%`
- 6m adverse tail rate: `18.60%`
- 6m win rate: `79.07%`
- Validation coverage score: `100.00`

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 20 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Weight Search ==
## Objective
- Continue improving sparse stage-bottom entries.
- Keep the strategy cross-validated across QQQ/SPY and individual stocks.
- Avoid changing fixed project contract files.

## Completed
- Diagnosed current losers.
  - Many losing or high-adverse signals carried `no_repair`, but fully excluding
    `no_repair` removed almost all QQQ/SPY validation samples, so it was not used
    as a hard filter.
- Added score weight profiles to `bottom_signal_config.json`.
  - `balanced`
  - `deep_repair`
  - `structure_retest`
  - `momentum_reset`
- Updated candidate generation so weight profiles are part of the parameter search.
- Increased default `max_configs` to `360`.
- Kept staged-search promotion at `50` to reduce DEV-stage false negatives.
- Fixed Pine generation so it uses the selected Python weight values instead of
  old hard-coded weights.

## Current Best Weight-Search Config
- Name: `btm_dw126_dt12_r7_st9x3_m8x21x5_sma50_atr10_vol10_wstructure_retest`
- Entry score threshold: `82`
- Market filter: QQQ/SPY 126-bar drawdown <= `-18%`
- Drawdown: 126-day window, `-12%`
- RSI: `7`
- Stochastic: `9, 3`
- MACD: `8, 21, 5`
- SMA distance: `50`
- ATR: `10`
- Volume window: `10`
- Weights:
  - drawdown `0.28`
  - momentum `0.18`
  - repair `0.18`
  - structure `0.26`
  - volume `0.05`
  - MA distance `0.05`

## Current Metrics
- Composite score: `64.21`
- Signals: `53`
- QQQ/SPY signals: `6`
- Individual-stock signals: `47`
- 6m win rate: `75.5%`
- Avg 6m return: `+44.75%`
- Avg 12m return: `+79.7%`
- Avg 6m adverse drawdown: `-14.5%`

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 18 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Market Context Filter ==
## Objective
- Make sparse bottom signals closer to true stage or historical bottoms.
- Cross-validate across QQQ/SPY and individual stocks.
- Avoid counting ordinary single-stock pullbacks when the broad market is not also in drawdown.

## Completed
- Added a broad-market context filter.
  - Market symbols: `QQQ`, `SPY`
  - Market drawdown window: `126`
  - Final market drawdown threshold: `-18%`
  - A candidate signal is counted only when at least one of QQQ/SPY is below the threshold.
- Added forward 6m win-rate scoring.
- Updated Pine generation to include the same QQQ/SPY market filter using `request.security`.
- Tested market thresholds:
  - `-15%`: 59 signals, avg 6m `+41.73%`, avg 12m `+75.2%`.
  - `-18%`: selected final run; 45 signals, avg 6m `+47.20%`, avg 12m `+84.90%`.
  - `-20%`: worse coverage and weaker selected result.

## Current Best Market-Context Config
- Name: `btm_dw63_dt8_r7_st14x3_m16x35x9_sma100_atr14_vol20`
- Entry score threshold: `82`
- Market filter: QQQ/SPY 126-bar drawdown <= `-18%`
- Drawdown: 63-day window, `-8%`
- RSI: `7`
- Stochastic: `14, 3`
- MACD: `16, 35, 9`
- SMA distance: `100`
- ATR: `14`
- Volume window: `20`

## Current Metrics
- Composite score: `63.95`
- Signals: `45`
- Active symbols: `20`
- Avg 3m return: `+25.61%`
- Avg 6m return: `+47.20%`
- Avg 12m return: `+84.90%`
- Avg 6m adverse drawdown: `-14.11%`
- 6m win rate: `77.78%`
- QQQ/SPY signals: `5`
- Individual-stock signals: `40`
- QQQ/SPY avg 6m return: `+20.34%`
- Individual-stock avg 6m return: `+50.56%`
- Validation coverage score: `100.00`

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 17 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Sparse Cross-Validation ==
## Objective
- Continue iterating toward fewer, higher-conviction bottom entries.
- Require cross-validation across QQQ/SPY and individual stocks.

## Completed
- Added sparse signal-count scoring.
  - Too many signals no longer helps.
  - Configs above `signal_count_max` are discounted.
- Added validation group scoring.
  - QQQ/SPY are measured separately from individual stocks.
  - Configs need enough index and individual-stock samples to avoid a coverage discount.
- Increased staged-search promotion count from `8` to `20` so DEV does not screen out sparse configs too early.
- Tested entry thresholds:
  - `80`: 143 signals, QQQ/SPY 8, avg 6m `+26.50%`, avg 12m `+49.50%`.
  - `82`: selected final sparse cross-validation baseline.
  - `83`: only 33 signals and QQQ/SPY 2; too little index validation.
  - `85`: only 22 signals and QQQ/SPY 2; too little index validation.
- Final config uses:
  - `entry=82`
  - `index_signal_min=5`
  - `individual_signal_min=40`
  - `signal_count_max=180`
  - hard validation coverage gate enabled
  - hard signal-count max gate enabled

## Current Best Sparse Cross-Validated Config
- Name: `btm_dw42_dt25_r7_st21x5_m12x26x9_sma150_atr20_vol50`
- Entry score threshold: `82`
- Drawdown: 42-day window, `-25%`
- RSI: `7`
- Stochastic: `21, 5`
- MACD: `12, 26, 9`
- SMA distance: `150`
- ATR: `20`
- Volume window: `50`

## Current Metrics
- Composite score: `54.78`
- Signals: `92`
- Active symbols: `20`
- Avg 3m return: `+14.92%`
- Avg 6m return: `+29.49%`
- Avg 12m return: `+53.95%`
- Avg 6m adverse drawdown: `-17.09%`
- QQQ/SPY signals: `5`
- Individual-stock signals: `87`
- QQQ/SPY avg 6m return: `+20.49%`
- Individual-stock avg 6m return: `+30.04%`
- Validation coverage score: `100.00`

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 15 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Bottom Signal Iteration - Entry Threshold Search ==
## Objective
- Continue searching for a better staged bottom-entry strategy.
- Keep configuration-driven iteration and avoid modifying fixed project contract files.

## Completed
- Increased default bottom-signal search breadth:
  - `max_configs`: `120`
  - staged search promotion: top `8` DEV configs
- Added separate `entry_threshold` handling.
  - `Watch`, `Medium`, and `Strong` labels still exist for chart reading.
  - Backtest entry evaluation now uses the configured `entry` score threshold.
  - This prevents low-confidence `Watch` rows from inflating the strategy sample.
- Tested entry thresholds:
  - `50`: too loose; 1361 signals, avg 6m `+20.14%`.
  - `60`: better; 472 signals, avg 6m `+23.99%`.
  - `65`: better; 385 signals, avg 6m `+25.71%`.
  - `70`: stronger; 138 signals, avg 6m `+33.60%`.
  - `75`: best current run; 143 signals, avg 6m `+32.99%`, composite `63.30`.
  - `80`: too strict; 99 signals, composite `62.70`.
- Updated `docs/plans/bottom_signal_iteration_2026-05-17.md`.
- Regenerated:
  - `investigations/bottom_signal_results.json`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_pine.pine`

## Current Best Bottom Signal Config
- Name: `btm_dw252_dt35_r14_st21x5_m12x26x9_sma50_atr10_vol50`
- Entry score threshold: `75`
- Drawdown: 252-day window, `-35%`
- RSI: `14`
- Stochastic: `21, 5`
- MACD: `12, 26, 9`
- SMA distance: `50`
- ATR: `10`
- Volume window: `50`

## Current Metrics
- Composite score: `63.30`
- Bottom quality: `67.63`
- Trade score: `78.66`
- Exit quality: `2.26`
- Signals: `143`
- Active symbols: `21`
- Avg 3m return: `+16.44%`
- Avg 6m return: `+32.99%`
- Avg 12m return: `+55.97%`
- Avg 6m adverse drawdown: `-16.18%`

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 10 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_config.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`
==

== Session: 2026-05-17 Progress Status Check ==
## Objective
- Answer the user's question about current project progress without changing strategy code.

## Checked
- Read the latest `claude-progress.md` entries.
- Confirmed no `Codex-progress.md` file is present.
- Reviewed `investigations/uptrend_dip_report.md`.
- Ran lightweight paper tracking status:
  - `.venv\\Scripts\\python.exe investigations\\uptrend_dip_search.py --paper-status --as-of 2026-05-17`
  - PASS.
- Ran existing unit tests:
  - `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.

## Current Status
- Historical research and reporting for the uptrend-dip / long-term add-on radar are implemented.
- Current broad default remains `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
- Paper tracking has 7 current signals, all still pending.
- As of 2026-05-17, no paper checks are overdue.
- Next pending check date is 2026-05-19.

## Not Modified
- Strategy code.
- `config.py`
- `run.py`
==

== Session: 2026-05-17 Daily Data Refresh ==
## Objective
- Refresh all configured daily ticker data from 2008-01-01 through 2026-04-30.
- Do not fetch 4h data.
- Do not modify strategy code or readonly config files in this step.

## Completed
- Used `config.ALL_TICKERS` as the ticker universe.
- Downloaded daily yfinance data with:
  - start: `2008-01-01`
  - end exclusive: `2026-05-01`
- Rewrote local ignored data files:
  - `data/{ticker}.parquet`
- Download completed successfully for all 21 tickers.
- Elapsed time:
  - about 67 seconds.

## Data Coverage
- Most long-history tickers now cover:
  - `2008-01-02` to `2026-04-30`
- Later-listed tickers start from their available public history:
  - `AVGO`: `2009-08-06`
  - `TSLA`: `2010-06-29`
  - `META`: `2012-05-18`
  - `CRWD`: `2019-06-12`
  - `PLTR`: `2020-09-30`
- All refreshed files end at:
  - `2026-04-30`

## Validation Commands Run
- Local parquet coverage check
  - PASS.
  - Confirmed every configured ticker file exists.
  - Confirmed every file has columns `Open`, `High`, `Low`, `Close`, `Volume`.
  - Confirmed every file ends at `2026-04-30`.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- Strategy code
==

== Session: 2026-05-17 Technical Indicator Wrapper ==
## Objective
- Install Python technical indicator libraries.
- Add a project-level indicator wrapper for future strategy research.
- Keep `config.py`, `prepare.py`, `run.py`, and existing investigation logic unchanged.

## Completed
- Installed dependencies with `uv add ta pandas-ta-classic`:
  - `ta==0.11.0`
  - `pandas-ta-classic==0.5.44`
- Added `quant_indicators.py`.
- Added `tests/test_quant_indicators.py`.
- Implemented wrapper functions:
  - `validate_ohlcv()`
  - `pandas_ta_classic_available()`
  - `add_trend_indicators()`
  - `add_momentum_indicators()`
  - `add_volatility_indicators()`
  - `add_volume_indicators()`
  - `add_custom_research_indicators()`
  - `add_common_indicators()`
- Default backend is `ta`; `pandas-ta-classic` is installed and exposed as a supplemental availability check.

## Indicator Coverage
- Trend:
  - `sma20`, `sma50`, `sma100`, `sma200`
  - `ema20`, `ema21`, `ema55`, `ema100`, `ema200`
  - `adx14`
- Momentum:
  - `rsi14`, `stoch14`
  - `macd`, `macd_signal`, `macd_diff`
  - `roc12`, `willr14`, `cci20`
- Volatility:
  - `atr14`, `atr20`, `natr14`
  - `bb_mid20`, `bb_upper20`, `bb_lower20`, `bb_width20`
  - `keltner_upper20`, `keltner_lower20`
- Volume:
  - `obv`, `mfi14`, `volume_sma20`, `volume_ratio20`, `cmf20`
- Project research:
  - `drawdown63`, `drawdown126`, `drawdown252`
  - `dist_sma200`
  - `atr_ratio14_70`

## TDD
- Added `tests/test_quant_indicators.py` before implementation.
- Verified expected RED:
  - `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - failed because `quant_indicators` did not exist.
- Implemented `quant_indicators.py`.
- Verified GREEN:
  - `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 3 tests.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 3 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile quant_indicators.py tests\\test_quant_indicators.py`
  - PASS.
- `uv run run.py`
  - PASS, exit code 0.
  - Note: output still includes existing Backtesting.py open-trade warnings and a Windows path message.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- Existing investigation strategy logic
==

== Session: 2026-05-17 Remove Legacy Crypto Config And Archive Baseline ==
## Objective
- Remove the root legacy crypto/Freqtrade `config.json`.
- Keep historical `versions/` archives unchanged.
- Document that the active US-stock workflow uses `config.py`.
- Add a short baseline archive document for the current uptrend-dip research.

## Completed
- Deleted root `config.json`.
- Updated `README.md` to explain:
  - legacy crypto/Freqtrade config is archived under `versions/`;
  - active US-stock workflow uses `config.py`;
  - old root `config.json` is not part of the active Backtesting.py + yfinance setup.
- Added:
  - `docs/plans/uptrend_dip_baseline_2026-05-17.md`
- Baseline archive summarizes:
  - current `bottom_reversal` default;
  - key evidence snapshot;
  - current limitations and paper-tracking gate;
  - data/tooling state;
  - evidence files;
  - next exploration guidance.

## Validation Commands Run
- `rg -n "config\\.json" README.md program.md plan.md prepare.py run.py strategies investigations tests pyproject.toml docs`
  - PASS; only active reference is the README archival note.
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 3 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `uv run run.py`
  - PASS, exit code 0.
  - Note: existing Backtesting.py open-trade warnings and Windows path message still appear.
- `git diff --check`
  - PASS.

## Not Modified
- `versions/`
- `config.py`
- `program.md`
- `prepare.py`
- `run.py`
==

== Session: 2026-05-17 Parameterized Indicator Wrapper Revision ==
## Objective
- Revise `quant_indicators.py` so technical indicator periods and combinations are experiment inputs.
- Avoid treating common periods like RSI 14, SMA 200, or ATR 14 as fixed strategy defaults.

## Completed
- Replaced fixed `add_common_indicators()` style with parameterized functions:
  - `add_sma(df, periods)`
  - `add_ema(df, periods)`
  - `add_rsi(df, periods)`
  - `add_macd(df, configs)`
  - `add_atr(df, periods)`
  - `add_adx(df, periods)`
  - `add_bollinger(df, configs)`
  - `add_stochastic(df, configs)`
  - `add_volume_features(df, periods)`
  - `add_drawdown(df, periods)`
  - `add_distance_to_sma(df, periods)`
  - `add_atr_ratio(df, pairs)`
  - `build_indicators(df, spec)`
- Updated indicator tests to prove:
  - requested RSI periods generate only requested columns;
  - `rsi_14` is not auto-generated when not requested;
  - MACD columns include the full parameter combination;
  - `build_indicators()` combines requested specs while preserving OHLCV rows.
- Updated `docs/plans/uptrend_dip_baseline_2026-05-17.md` to state that indicator parameters must come from the experiment layer.

## TDD
- Rewrote `tests/test_quant_indicators.py` first.
- Verified expected RED:
  - `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - failed because parameterized functions did not exist.
- Implemented the parameterized API.
- Verified GREEN:
  - `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_quant_indicators`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe -m py_compile quant_indicators.py tests\\test_quant_indicators.py`
  - PASS.
- `uv run run.py`
  - PASS, exit code 0.
  - Note: existing Backtesting.py open-trade warnings and Windows path message still appear.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- Existing uptrend-dip investigation logic
==

== Session: 2026-05-13 Holdout Report Weighting Clarification ==
## User Question
- First QQQ run timed out.
- User asked why it timed out and requested a retest.

## Cause
- The first command used a 120-second tool timeout.
- The QQQ grid search currently takes about 3-4 minutes on this machine, so the tool killed the process before completion.
- Re-running with a 600-second timeout completed normally.

## Completed
- Clarified date-split holdout reporting in `investigations/uptrend_dip_search.py`.
- Added `dateSplitRadar.techSubsetHoldoutSignalSummary` to JSON output.
- Updated the report executive summary and date-split section to distinguish:
  - symbol-average results: each ticker has equal weight
  - signal-level results: each signal has equal weight, so active tickers carry more weight
- Updated the frozen candidate holdout table to show both:
  - `Symbol Avg 12m`
  - `Signal Avg 12m`
- Added a unit test proving symbol-average and signal-level summaries can intentionally differ.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 19 tests.
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS with longer timeout.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.2%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 12m +39.4%, avg 12m max drawdown -6.5%.
  - SPY: 3 signals, avg 12m +26.6%, avg 12m max drawdown -9.0%.
- `git diff --check`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.

## Current Interpretation
- No strategy signal logic changed in this session.
- The 64.1% vs 68.5% difference is now explicit:
  - 64.1% = 2023+ tech holdout by symbol-average.
  - 68.5% = 2023+ tech holdout by signal-level average.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Restricted Walk-Forward Diagnostic ==
## Objective
- Continue validating the tech-stock long-term add-on radar.
- Reduce overfitting risk before adding more strategy indicators.

## Completed
- Added `evaluate_restricted_walk_forward()` in `investigations/uptrend_dip_search.py`.
- The diagnostic uses only the already frozen candidate configs:
  - Broad default
  - Date-split selected config when different
  - Best trend-breakout family
  - Best tech-breakout family
  - Best index-shallow-pullback family
- For each calendar year 2023-2026:
  - Train/select on QQQ/SPY signal history available up to the prior year-end.
  - Evaluate the selected config on the tech-stock subset during that calendar year only.
- Added `restrictedWalkForwardRadar` to `investigations/uptrend_dip_results.json`.
- Added `Restricted Walk-Forward Diagnostic` to `investigations/uptrend_dip_report.md`.
- Added a unit test covering the restricted walk-forward helper.

## Latest Full-Test Result
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Long-term radar remains `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 12m +39.4%, avg 12m max drawdown -6.5%.
  - SPY: 3 signals, avg 12m +26.6%, avg 12m max drawdown -9.0%.

## Restricted Walk-Forward Results
- 2023 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - 7 tech signals, 7 mature 12m, symbol avg 12m +116.0%, signal avg 12m +107.0%, signal 12m DD -3.2%.
- 2024 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - 8 tech signals, 8 mature 12m, symbol avg 12m +53.0%, signal avg 12m +60.6%, signal 12m DD -15.0%.
- 2025 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - 15 tech signals, 12 mature 12m, symbol avg 12m +52.4%, signal avg 12m +58.4%, signal 12m DD -15.4%.
- 2026 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - 7 tech signals, 0 mature 12m, too recent to judge 12m return.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 20 tests.
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - QQQ long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - 4 signals, avg 12m +50.9%, avg 12m max drawdown -4.2%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
- `git diff --check`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.

## Interpretation
- The restricted walk-forward result strengthens the case for the broad `bottom_reversal` default.
- It is more conservative than per-symbol optimization because the same frozen config is repeatedly selected.
- It is still not a full-grid rolling walk-forward; the next stronger validation would rerank the entire config grid inside each training window.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Full-Grid Walk-Forward Diagnostic ==
## Objective
- Strengthen validation beyond the restricted frozen-candidate walk-forward.
- Test whether the full 245-config stage-1 grid still selects the same long-term add-on strategy when each year can only use prior QQQ/SPY signal history.

## Completed
- Added `evaluate_full_grid_walk_forward()` in `investigations/uptrend_dip_search.py`.
- Added `fullGridWalkForwardRadar` to `investigations/uptrend_dip_results.json`.
- Added `Full-Grid Walk-Forward Diagnostic` to `investigations/uptrend_dip_report.md`.
- Updated validation caveats to distinguish:
  - full-grid walk-forward: stricter validation because it reranks the whole grid yearly
  - restricted walk-forward: more operationally conservative because it only selects from frozen candidates
- Added a unit test for the full-grid walk-forward helper.

## Latest Full-Test Result
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Long-term radar remains `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 12m +39.4%, avg 12m max drawdown -6.5%.
  - SPY: 3 signals, avg 12m +26.6%, avg 12m max drawdown -9.0%.

## Full-Grid Walk-Forward Results
- 2023 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - Train score 95.40.
  - 7 tech signals, 7 mature 12m, symbol avg 12m +116.0%, signal avg 12m +107.0%, signal 12m DD -3.2%.
- 2024 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - Train score 95.40.
  - 8 tech signals, 8 mature 12m, symbol avg 12m +53.0%, signal avg 12m +60.6%, signal 12m DD -15.0%.
- 2025 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - Train score 95.40.
  - 15 tech signals, 12 mature 12m, symbol avg 12m +52.4%, signal avg 12m +58.4%, signal 12m DD -15.4%.
- 2026 selected `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
  - Train score 96.86.
  - 7 tech signals, 0 mature 12m, too recent to judge 12m return.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 21 tests.
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - QQQ long-term radar remains `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - 4 signals, avg 12m +50.9%, avg 12m max drawdown -4.2%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
- `git diff --check`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg -n "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.

## Interpretation
- The full-grid yearly test strengthens the case that `bottom_reversal` is not just a one-shot full-sample artifact.
- The same broad config was selected in every yearly training window from 2023 through 2026.
- 2026 signals should be monitored later because none have mature 12-month outcomes yet.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Standalone Pine Guard Test ==
## Objective
- Verify the standalone TradingView radar file stays aligned with the current validated long-term default.

## Completed
- Added a test for `investigations/long_term_addon_radar.pine` in `tests/test_uptrend_dip_search.py`.
- The test checks:
  - default `Radar Mode = bottom_reversal`
  - `bottom_threshold = 45`
  - `index_threshold = 50`
  - bearish-candle requirement remains present
  - `BTM` and `IDX` strength labels remain present
  - no `ta.sum` or `math.sum` usage
  - ASCII-only Pine output

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 22 tests.
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Report Strategy Card Cleanup ==
## Objective
- Make the report easier to read for a non-full-time developer.
- Remove stale wording that said full rolling validation was still missing after full-grid yearly walk-forward had already been added.

## Completed
- Updated `write_report()` in `investigations/uptrend_dip_search.py`.
- Regenerated `investigations/uptrend_dip_report.md` from the existing JSON results.
- Added a `Current Strategy Card` near the top of the report explaining:
  - primary use is long-term add-on buying, not short-term trading
  - default signal family is `bottom_reversal`
  - entry requires a qualifying score plus bearish candle
  - signals are sparse, normally separated by about 63 trading bars
  - `Deep Bottom - Strong/Medium/Watch` should be read separately from `Shallow Pullback`
- Updated research-status wording:
  - full-grid yearly walk-forward has been added
  - future validation should add more rolling windows before treating it as production-grade

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 22 tests.
- `git diff --check`
  - PASS.
- Checked report output to confirm no stale `still needs full rolling` wording remains.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Standalone Pine Index Threshold Alignment ==
## Objective
- Keep the standalone TradingView radar aligned with the latest report and grid-search result.

## Issue Found
- Report's best `index_shallow_pullback` family was `idx_d0.15_b0.25_r0.20_c0.25_v0.15_t55`.
- `investigations/long_term_addon_radar.pine` still had `index_threshold = 50`.
- That meant switching standalone Pine to `index_shallow_pullback` could show signals that did not match the latest reported best index-shallow config.

## Completed
- Updated `investigations/long_term_addon_radar.pine`:
  - `index_threshold = 55`.
- Updated `tests/test_uptrend_dip_search.py` to lock the standalone Pine default at 55.
- Updated TradingView usage notes in `investigations/uptrend_dip_report.md` to state the standalone index-shallow default threshold is 55.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 22 tests.
- Pine compatibility check:
  - `long_term_addon_radar.pine` ASCII-only, no `ta.sum`, no `math.sum`.
  - `uptrend_dip_pine.pine` ASCII-only, no `ta.sum`, no `math.sum`.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Signal Maturity Fields ==
## Objective
- Make recent signal logs harder to misread.
- Distinguish mature 6m/12m/24m forward returns from partial, still-in-progress signals.

## Issue Found
- Recent 2026 signals have no mature 6m/12m return yet.
- The report still displayed a `12m DD` column, even though drawdown for immature signals is only measured through the latest available data.

## Completed
- Updated `evaluate_long_term_radar()` in `investigations/uptrend_dip_search.py` to add per-signal fields:
  - `barsSinceSignal`
  - `mature6m`
  - `mature12m`
  - `mature24m`
- Updated report tables:
  - Add-on signal logs now include `Age Bars`.
  - Drawdown column now reads `12m/Partial DD`.
- Regenerated `investigations/uptrend_dip_results.json` and `investigations/uptrend_dip_report.md`.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 22 tests.
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - QQQ long-term radar unchanged: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - 4 signals, avg 12m +50.9%, avg 12m max drawdown -4.2%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Full default unchanged: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 12m +39.4%, avg 12m max drawdown -6.5%.
  - SPY: 3 signals, avg 12m +26.6%, avg 12m max drawdown -9.0%.
- `git diff --check`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Immature Return Display Cleanup ==
## Objective
- Prevent immature 6m/12m/24m windows from being shown as `0.0%`.

## Issue Found
- `summarize_signal_window()` and `summarize_signal_years()` returned `0.0` when no mature return samples existed.
- This made 2026 rows look like actual 0.0% forward returns even though those 12-month windows are not mature.
- Walk-forward tables also showed `Symbol Avg 12m = 0.0%` for 2026 despite 0 mature 12m signals.

## Completed
- Added `_mean_present_or_none()` in `investigations/uptrend_dip_search.py`.
- Updated signal-window and yearly summaries:
  - `avg6mPct`, `avg12mPct`, and `avg24mPct` now become `None` when no mature samples exist.
  - Added `mature6mSignalCount`.
- Updated report formatting:
  - Missing immature averages render as `-`.
  - 2026 walk-forward symbol-average 12m also renders as `-` when there are 0 mature 12m signals.
- Regenerated `investigations/uptrend_dip_results.json` and `investigations/uptrend_dip_report.md`.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 23 tests.
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS; QQQ result unchanged.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS; full default unchanged.
- `git diff --check`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Drawdown Semantics Fix ==
## Objective
- Make `maxDrawdown6mPct` / `maxDrawdown12mPct` mean maximum adverse drawdown, never a positive number.

## Issue Found
- `_forward_max_drawdown_pct()` returned the future minimum price relative to entry.
- If the future minimum stayed above the entry price, the reported "drawdown" became positive.
- Example before fix:
  - QQQ 2025-04-21 showed `12m/Partial DD = +2.63%`.
  - TSLA 2025-06-05 showed `12m/Partial DD = +3.25%`.
- That is misleading: no adverse drawdown should be `0.0%`, not a positive number.

## Completed
- Updated `_forward_max_drawdown_pct()` in `investigations/uptrend_dip_search.py`:
  - caps max adverse drawdown at `0.0`.
- Added a unit test ensuring long-term radar drawdown is never positive.
- Regenerated `investigations/uptrend_dip_results.json` and `investigations/uptrend_dip_report.md`.

## Latest Result Impact
- Default strategy unchanged:
  - `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
- QQQ full-test long-term radar:
  - 6 signals.
  - avg 12m +39.4%.
  - avg 12m max adverse drawdown now -7.0% after the stricter drawdown semantics.
- Positive drawdown count in current generated recommended-radar signals:
  - 0.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 24 tests.
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
- `git diff --check`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Frozen Candidate Report Wording Cleanup ==
## Objective
- Remove stale report wording after restricted and full-grid walk-forward validation had already been added.

## Issue Found
- Report still had a section titled `Candidate Configs To Freeze Next`.
- Its description said the configs were worth freezing before a real rolling walk-forward test.
- That was outdated because those configs are already used in the restricted walk-forward diagnostic.

## Completed
- Updated `write_report()` in `investigations/uptrend_dip_search.py`.
- Regenerated `investigations/uptrend_dip_report.md`.
- Renamed the section:
  - from `Candidate Configs To Freeze Next`
  - to `Frozen Candidate Set Used For Validation`
- Updated restricted walk-forward description:
  - it is operationally conservative because it only selects from a small predeclared candidate set.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 24 tests.
- `git diff --check`
  - PASS.
- Checked report text to confirm stale `Candidate Configs To Freeze Next` wording is gone.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Pine Usage Wording Fix ==
## Objective
- Make TradingView usage guidance match the actual Pine files.

## Issue Found
- Report said to use the generated default as the broad long-term add-on radar.
- That was misleading because:
  - `uptrend_dip_pine.pine` is the full buy/sell comparison indicator with position-state and sell logic.
  - `long_term_addon_radar.pine` is the standalone long-term add-on radar that matches the investment use case.

## Completed
- Updated `write_report()` in `investigations/uptrend_dip_search.py`.
- Regenerated `investigations/uptrend_dip_report.md`.
- TradingView section now says:
  - use `long_term_addon_radar.pine` for the long-term add-on radar
  - use `uptrend_dip_pine.pine` only for the fuller buy/sell comparison indicator
- Added a regression test ensuring the report does not reintroduce the old misleading wording.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 25 tests.
- `git diff --check`
  - PASS.
- Checked report text for the corrected Pine guidance.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 JSON Pine Path Exposure ==
## Objective
- Keep machine-readable results aligned with the report's Pine guidance.

## Issue Found
- `investigations/uptrend_dip_results.json` only exposed `pineScript`, pointing to `uptrend_dip_pine.pine`.
- The report now correctly says long-term add-on users should use `long_term_addon_radar.pine`.
- Without a standalone Pine path in JSON, automation or future readers could still pick the wrong Pine file.

## Completed
- Added `longTermAddonPineScript` to generated JSON output in `investigations/uptrend_dip_search.py`.
- Regenerated `investigations/uptrend_dip_results.json`.
- Added a unit test checking:
  - `pineScript` ends with `uptrend_dip_pine.pine`
  - `longTermAddonPineScript` ends with `long_term_addon_radar.pine`

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS; QQQ result unchanged.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS; full default unchanged.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 26 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Standalone Pine Generation ==
## Objective
- Make `long_term_addon_radar.pine` reproducible from `investigations/uptrend_dip_search.py`, not just a manually maintained side file.

## Issue Found
- `run()` regenerated `uptrend_dip_pine.pine`, but only pointed to `long_term_addon_radar.pine`.
- The standalone long-term radar could drift unless manually edited.

## Completed
- Added `generate_long_term_addon_pine_script()` in `investigations/uptrend_dip_search.py`.
- Updated `run()` to regenerate `investigations/long_term_addon_radar.pine` every time the search runs.
- Added a unit test requiring the checked-in standalone Pine file to exactly equal the generator output.
- Regenerated both Pine files through the normal script flow.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 26 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS; QQQ result unchanged.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS; full default unchanged.
- Standalone Pine generator check:
  - `long_term_addon_radar.pine == generate_long_term_addon_pine_script()`.
- Pine compatibility:
  - both Pine files are ASCII-only.
  - no `ta.sum`.
  - no `math.sum`.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Parameterized Standalone Pine Defaults ==
## Objective
- Prevent future drift between grid-search-selected configs and standalone Pine defaults.

## Issue Found
- `generate_long_term_addon_pine_script()` regenerated the standalone Pine file, but still hardcoded:
  - bottom threshold and weights
  - index-shallow threshold and weights
- If a future full search selects different defaults, the standalone Pine could still silently use old values.

## Completed
- Updated `generate_long_term_addon_pine_script()` to accept optional configs:
  - `bottom_cfg`
  - `index_cfg`
- The standalone Pine now derives:
  - bottom threshold and weights from the current long-term radar default
  - index-shallow threshold and weights from the current best `index_shallow_pullback` family config
- Updated `run()` to pass those configs when regenerating `long_term_addon_radar.pine`.
- Added a unit test proving supplied configs change Pine defaults.
- Preserved the TradingView alert placeholder as `{{ticker}}`.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 27 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS; QQQ result unchanged.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS; full default unchanged.
- Standalone Pine checks:
  - file matches default generator output for current full-search defaults.
  - has `bottom_threshold = 45`.
  - has `index_threshold = 55`.
  - has `{{ticker}}` alert placeholder.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Current Tech Radar Watchlist ==
## Objective
- Make the generated outputs more directly usable for monitoring current tech-stock add-on candidates.

## Issue Found
- The report and JSON had a latest-signal history, but no machine-readable "current watchlist" field.
- A user or automation had to manually filter recent signals by age.

## Completed
- Added `summarize_active_signal_log()` in `investigations/uptrend_dip_search.py`.
- Added `techSubsetCurrentSignalLog` to generated JSON.
- Added `Current Tech Radar Watchlist` to `investigations/uptrend_dip_report.md`.
- The watchlist filters global-default tech signals to the last 126 trading bars.

## Current Watchlist From Latest Full Run
- CRM 2026-02-19, age 56 bars, `Deep Bottom - Strong`.
- AMZN 2026-02-09, age 63 bars, `Deep Bottom - Medium`.
- MSFT 2026-02-05, age 65 bars, `Deep Bottom - Medium`.
- CRWD 2026-02-05, age 65 bars, `Deep Bottom - Medium`.
- PLTR 2026-01-30, age 69 bars, `Deep Bottom - Medium`.
- META 2026-01-20, age 77 bars, `Deep Bottom - Medium`.
- CRM 2025-11-17, age 119 bars, `Deep Bottom - Strong`.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 28 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS; QQQ result unchanged.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS; full default unchanged.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Tech Segment Summary ==
## Objective
- Make the tech-stock evaluation less dependent on a single mixed average.
- Separate steadier large-cap tech names from high-beta tech names.

## Completed
- Added `TECH_SEGMENTS` in `investigations/uptrend_dip_search.py`:
  - `large_cap_quality_tech`: AAPL, MSFT, AMZN, META, AVGO, CRM, TSM
  - `high_beta_tech`: NVDA, AMD, TSLA, PLTR, CRWD
- Added `summarize_radar_segments()`.
- Added JSON fields:
  - `techSegmentRecommendedRadarSummaries`
  - `techSegmentBestRadarSummaries`
- Added `Tech Segment Summary` to `investigations/uptrend_dip_report.md`.
- Added unit test coverage for segment summarization.

## Latest Segment Results
- Global default, large-cap quality tech:
  - 7 symbols, avg 12m +39.4%, median 12m +30.0%, avg 12m DD -17.7%.
- Global default, high-beta tech:
  - 5 symbols, avg 12m +76.5%, median 12m +83.1%, avg 12m DD -23.4%.
- Per-symbol best, large-cap quality tech:
  - avg 12m +52.5%, median 12m +50.2%, avg 12m DD -15.5%.
- Per-symbol best, high-beta tech:
  - avg 12m +171.2%, median 12m +110.2%, avg 12m DD -12.8%.

## Interpretation
- The broad `bottom_reversal` default works on both segments.
- High-beta tech has higher forward returns but deeper default-strategy drawdowns.
- Per-symbol optimization greatly boosts high-beta results, but remains more overfit-prone than the global default.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 29 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS; QQQ result unchanged.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS; full default unchanged.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-12 Buy-the-Dip Indicator v2 ==
## Completed
- Merged 4 new modules into `investigations/buy_dip_search.py`:
  1. **Keltner Channel** replaces BB: `EMA(20) ± 2*ATR(20)`, scored by distance from EMA20 in ATR units (`*30` scaling)
  2. **RSI + Stochastic dual confirmation**: `Stochastic(14)`, RSI<30 AND Stoch<20 = +20 bonus points
  3. **EMA trend filter**: EMA 21/55/100/200 alignment, additive modifier (-4 bull to +4 bear)
  4. **ATR volatility ratio** replaces volume: `ATR(14)/SMA(ATR(14),70)` > 1.5 = panic signal
- Updated `DipConfig` (6 weights: rsi, keltner, sma200, drawdown, atr, stoch)
- Updated `WEIGHT_SETS` (10 sets including oscillator-heavy variants)
- Updated `candidate_configs()` for 6-weight grid search
- Updated `generate_pine_script()` — TradingView Pine Script v5
- Updated `write_report()` with v2 indicator descriptions
- Regenerated `buy_dip_pine.pine`, `buy_dip_report.md`, `buy_dip_results.json`

## v2 Results vs v1
| Metric | v1 QQQ | v2 QQQ |
|--------|--------|--------|
| Buy signals | 8 | 29 |
| Avg 3m return | 22.6% | 16.0% |
| Win rate (3m) | 87.5% | 66% |
| Threshold | 40 | 50 |
| Weights | equal 0.20×5 | rsi=0.20 keltner=0.15 sma200=0.15 dd=0.10 atr=0.25 stoch=0.15 |

## Key Design Decisions
- **Keltner scoring**: Uses `(EMA20 - close) / ATR20 * 30` instead of band-edge distance. This gives meaningful scores even when price is near (but not below) the Keltner lower band.
- **Trend filter**: Additive modifier (-4 to +4) instead of multiplicative (0.7-1.3x). Multiplicative was too harsh — suppressed all bull-market signals below threshold.
- **2025 H2 / 2026 Apr**: Grid search does NOT select configs that catch these pullbacks. The pullbacks were too mild (8% drawdown, RSI 26.5 for 2025 H2, RSI 42.7 for 2026 Apr). Composite max was 37.1 for 2025 H2 — just above threshold=35, but threshold=35 produces 127 signals (too much noise). At threshold=50 (optimal), these phases have 0 signals.
- The v2 system is better at detecting real panics (2020 Covid: 10 signals vs v1's 8, 2022 bear: 13 vs v1's fewer) but correctly avoids firing on mild pullbacks.

## Modified Functions
- `build_indicators()`: Keltner, Stochastic(14), EMA 21/55/100/200, ATR ratio
- `score_buy_signals()`: 6 weighted components + EMA trend additive modifier
- `DipConfig`: 6 weight fields (w_rsi, w_keltner, w_sma200, w_drawdown, w_atr, w_stoch)
- `WEIGHT_SETS`: 10 weight combinations
- `candidate_configs()`: 6-weight unpacking, threshold 20-50
- `generate_pine_script()`: v2 indicators
- `write_report()`: v2 descriptions

## Not Modified
- `config.py`, `run.py`, `prepare.py` — untouched as specified

## Key Files
- `investigations/buy_dip_search.py` — v2 main script
- `investigations/buy_dip_pine.pine` — v2 Pine Script
- `investigations/buy_dip_report.md` — v2 search report
- `investigations/buy_dip_results.json` — v2 raw results
==

== Session: 2026-05-12 Uptrend Dip Buy+Sell Strategy (v2) ==
## Completed
- Built `investigations/uptrend_dip_search.py` — uptrend dip buy + sell signal grid search
- Two buy strategies: **trend pullback** (EMA stack + RSI sweet spot + Stoch + volume contraction) and **breakout** (range compression + N-bar high + volume surge + momentum)
- Two sell strategies: **trend reversal** (EMA breakdown + death cross + RSI break) and **overbought exit** (RSI/Stoch overbought + Keltner upper + profit target)
- Discrete trade simulation (buy→sell cycles, not DCA)
- Two-stage grid search: Stage 1 = buy config (forward returns), Stage 2 = sell config (trade simulation)
- Generated `uptrend_dip_report.md`, `uptrend_dip_results.json`, `uptrend_dip_pine.pine`

## Key Fixes Applied This Session
- **Sell overbought base lowered**: RSI-55 → RSI-45, Stoch-55 → RSI-45 (score_sell_overbought). Old base made sell signals nearly impossible to trigger.
- **Sell weight sets expanded**: 5 → 10 sets, including pure-overbought and pure-profit variants
- **Stage 2 scoring fixed**: Changed from avg_return to total_return as primary metric. Old scoring rewarded 1 huge trade over many good trades, causing grid search to converge on "never sell" configs.
- **Trade count penalty**: <5 trades = -30 per missing trade. Noise trade penalty for |return| < 3%.
- **Pine Script regenerated** by framework with optimized params.

## Recommended Config (QQQ+SPY combined)
- Strategy: **breakout** (buy_threshold=40, sell_threshold=45, stop_loss=15%)
- Breakout weights: range=0.20, signal=0.20, volume=0.25, momentum=0.20, trend=0.15

## Key Results
| Symbol | Trades | Win% | Avg Return | Total Return | Sharpe |
|--------|--------|------|------------|--------------|--------|
| QQQ | 9 | 78% | +16.2% | +145.3% | 0.72 |
| SPY | 7 | 86% | +18.2% | +127.3% | 0.64 |

## QQQ Trade Log
1. 2017-10-27 → 2018-01-22: +11.4% (57d, signal)
2. 2018-01-23 → 2019-04-23: +13.4% (313d, signal)
3. 2019-05-07 → 2019-12-26: +15.5% (162d, signal)
4. 2020-01-02 → 2020-03-12: -18.0% (48d, stop-loss)
5. 2020-07-14 → 2020-09-01: +15.2% (35d, signal)
6. 2020-09-02 → 2021-11-03: +30.6% (295d, signal)
7. 2022-01-10 → 2022-03-14: -16.3% (43d, stop-loss)
8. 2023-02-02 → 2024-06-17: +56.9% (344d, signal)
9. 2024-06-21 → 2026-04-17: +36.6% (456d, signal)

## Design Notes
- Breakout strategy selected over pullback by grid search (higher total return)
- 7 out of 9 exits are sell signals (not stop-loss) — sell logic is now working
- Buy & Hold still beats on absolute return (404% vs 145%) but strategy avoids 2022 bear market
- Per-symbol optimization: breakout dominates for individual stocks, pullback still competitive for indices

## Key Files
- `investigations/uptrend_dip_search.py` — main script (~1200 lines)
- `investigations/uptrend_dip_pine.pine` — TradingView Pine Script (auto-generated by framework)
- `investigations/uptrend_dip_report.md` — search report
- `investigations/uptrend_dip_results.json` — raw results
==

== Session: 2026-05-12 Tech Stock Buy/Sell Strategy Exploration ==
## Goal
- Continue improving `investigations/uptrend_dip_search.py` for U.S. technology stocks.
- Do not modify `config.py` or `run.py`.
- Validate every code change with `--symbol QQQ`; run `--symbol all` when QQQ risk/reward does not obviously deteriorate or shows clear improvement.

## Completed This Session
- Added `tech_breakout` buy strategy:
  - Prior 20-day high breakout using yesterday's rolling high.
  - Relative strength score vs SPY.
  - Volume expansion and volatility contraction.
  - Pine Script generator updated with a benchmark symbol input.
- Added `trend_breakout` strategy:
  - ADX(14) trend strength.
  - EMA55 20-day slope.
  - Breakout score adjusted by trend quality.
- Updated Stage 2 buy-config selection:
  - Old behavior used only Stage 1 top 3, which could be crowded by one strategy.
  - New behavior keeps top configs plus the best config from each buy strategy, capped at 8 buy configs.
- Added trailing/profit-protection exit logic:
  - Tracks peak price while in position.
  - Exits on `trailing_stop` after a profitable peak drawdown.
  - Adds ATR trailing stop using `peak_price - 3 * ATR(14)`.
  - Pine Script generator updated with position-state tracking and stop/trailing exits.
- Added focused `unittest` coverage in `tests/test_uptrend_dip_search.py`.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 4 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - After tech breakout: QQQ 5 trades, 100% win rate, total return 64.3%, Sharpe 1.81.
  - After trend filter: `trend_breakout` did not beat `tech_breakout`; best trend-only QQQ check was about 6 trades, 94.6% total return, Sharpe 0.79.
  - After trailing stop: QQQ 5 trades, 100% win rate, total return 65.1%, Sharpe 2.13, max drawdown -8.5%, 2 trailing exits.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - Recommended default remained `tech_breakout`, but QQQ/SPY default was too short-term: QQQ total return 7.7%, SPY total return 5.5%.

## Current Full-Test Tech Subset Result
Tech subset checked: AAPL, MSFT, NVDA, AMD, AMZN, META, AVGO, CRM, TSLA, TSM, PLTR, CRWD.

- Average trade count: 23.2
- Average win rate: 79.0%
- Average total return: 107.3%
- Average Sharpe: 4.32
- Average max drawdown: -11.1%
- Total trailing exits across the tech subset: 34

## Interpretation
- `tech_breakout` is much more selective and risk-controlled than the old QQQ baseline, but it gives up too much QQQ/SPY total return to be the default index strategy.
- The trailing stop fixed a major problem in individual high-beta stocks: earlier results for NVDA/AMD/TSM were dominated by huge open-trade style gains and very large drawdowns; after trailing stops, results are more realistic and risk-controlled.
- `trend_breakout` did not become the best QQQ strategy, but it became useful for several high-beta tech names in per-symbol optimization.

## Not Modified
- `config.py`
- `run.py`

## Next Suggested Step
- Improve the scoring objective before adding more indicators:
  - Penalize very low QQQ/SPY total return even when win rate and Sharpe are high.
  - Add a tech-subset aggregate section to the report so the framework can rank strategies for technology stocks directly, not only QQQ+SPY.
- Then re-run `--symbol QQQ` and `--symbol all`.
==

== Session: 2026-05-12 Long-Term Add-On Radar ==
## User Clarification
- The goal is not high win rate or short-term trading.
- The goal is to find better buy points for long-term investing / add-on buying.
- Sell signals are now secondary; they can remain as a comparison, but they should not drive the main strategy choice.

## Completed
- Added `evaluate_long_term_radar()` in `investigations/uptrend_dip_search.py`.
- Added long-term radar output to `run()`:
  - `longTermRadar`
  - `perSymbolRadarBest`
- Radar scoring now focuses on:
  - 6-month forward return
  - 12-month forward return
  - 24-month forward return
  - 6/12-month maximum adverse drawdown after the signal
  - sparse signals, using a 63-trading-day minimum gap between add-on signals
- Win rate is not used as the main objective.
- Pine Script generation now uses the long-term radar recommended buy config, not the short-term trading config.
- Report now includes:
  - Long-Term Add-On Radar section
  - Add-on signal log for QQQ/SPY
  - Per-symbol long-term radar config table
- Added unit test for long-term radar scoring in `tests/test_uptrend_dip_search.py`.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 5 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - Long-term radar selected `trend_breakout`.
  - QQQ: 6 signals, avg 6m +15.2%, avg 12m +29.8%, avg 24m +55.4%, avg 12m max drawdown -10.9%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - Long-term radar selected `tech_breakout`.
  - QQQ: 6 signals, avg 6m +12.7%, avg 12m +31.4%, avg 24m +52.2%, avg 12m max drawdown -5.7%.
  - SPY: 9 signals, avg 6m +7.9%, avg 12m +19.4%, avg 24m +32.5%, avg 12m max drawdown -10.2%.

## Full-Test Tech Subset Radar Results
Tech subset: AAPL, MSFT, NVDA, AMD, AMZN, META, AVGO, CRM, TSLA, TSM, PLTR, CRWD.

- Average signals: 12.6
- Average mature 12m signals: 11.3
- Average 6m return: +30.1%
- Average 12m return: +82.7%
- Average 24m return: +205.0%
- Average 12m max drawdown: -15.3%

## Interpretation
- The long-term radar is now much closer to the intended use case: infrequent add-on signals for long holding periods.
- QQQ results are sensible and not based on high win-rate trading: the key result is average 12m/24m forward return after sparse signals.
- High-beta names such as TSLA, PLTR, NVDA, and AMD strongly lift the tech-subset average, so future reports should show median results too, not only averages.
- Current best default for QQQ+SPY full search: `tech_breakout` with threshold 55.

## Not Modified
- `config.py`
- `run.py`

## Next Suggested Step
- Add median 6m/12m/24m returns and worst-signal drawdown to the radar report.
- Consider a separate "large-cap quality tech" subset excluding extreme high-beta names, so AAPL/MSFT/AMZN/META/AVGO can be judged separately from TSLA/PLTR/NVDA/AMD.
==

== Session: 2026-05-12 Pine Export for Long-Term Add-On Radar ==
## Completed
- Added standalone TradingView Pine v5 indicator:
  - `investigations/long_term_addon_radar.pine`
- Purpose:
  - Show long-term add-on signals only.
  - Hide short-term sell logic.
  - Use the full-search default long-term radar config:
    - Strategy: `tech_breakout`
    - Threshold: 55
    - Weights: compression 0.15, breakout 0.20, volume 0.25, momentum 0.15, relative strength 0.25
  - Enforce minimum 63 bars between add-on signals, matching the radar's sparse-signal design.
- Existing generated file still exists:
  - `investigations/uptrend_dip_pine.pine`
  - This is the fuller buy/sell indicator generated by the Python framework.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-12 Pine Compile Fix ==
## Issue
- TradingView compile error:
  - `Could not find function or function reference 'ta.sum'`

## Fix
- Replaced `ta.sum(...)` with `math.sum(...)` in:
  - `investigations/long_term_addon_radar.pine`
  - `investigations/uptrend_dip_pine.pine`
  - `generate_pine_script()` template inside `investigations/uptrend_dip_search.py`

## Validation
- Confirmed no remaining `ta.sum` references in Pine outputs or template.
- Ran `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 8 tests.
- Opened `investigations/long_term_addon_radar.pine` in the default editor for TradingView copy/paste.
==

== Session: 2026-05-12 Bottom Reversal / RSI Divergence Exploration ==
## User Feedback
- Add-on points should not be limited to uptrends.
- Large drawdowns can be valid long-term add-on points.
- Double bottoms / multiple bottoms are especially important.
- User noted RSI divergence may be more accurate than the previous buy/sell logic.

## Completed
- Added `bottom_reversal` buy strategy to `investigations/uptrend_dip_search.py`.
- New bottom indicators in `build_indicators()`:
  - 252-day drawdown
  - 5-day and 20-day crash return
  - prior 120-day low retest score
  - multi-bottom bonus based on repeated tests near the 120-day low
  - RSI divergence score: price near/lower prior low while RSI is higher than prior RSI low
  - capitulation score: volume expansion plus low RSI
- Added `score_buy_bottom_reversal()`.
- Added bottom-reversal candidate weight sets.
- Long-term radar can now select bottom-reversal configs.
- Updated Pine generation to support `bottom_reversal`.
- Updated standalone Pine:
  - `investigations/long_term_addon_radar.pine`
  - Default strategy is now `bottom_reversal`, threshold 45.
- Added unit test for bottom-reversal scoring.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 8 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS after disabling bytecode writes due a Windows `__pycache__` lock.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - Selected `bottom_reversal`, threshold 55.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.2%.
  - Signals were in 2020 crash and 2022 bottoming area, not trend-chasing points.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - Selected `bottom_reversal`, threshold 45.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -6.5%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.

## Full-Test Tech Subset After Bottom Strategy
Tech subset: AAPL, MSFT, NVDA, AMD, AMZN, META, AVGO, CRM, TSLA, TSM, PLTR, CRWD.

- Average signals: 7.3
- Average mature 12m signals: 6.3
- Average 6m return: +40.4%
- Average 12m return: +102.0%
- Average 24m return: +247.1%
- Average 12m max drawdown: -13.7%
- Median 6m return: +35.2%
- Median 12m return: +75.6%
- Median 24m return: +137.3%
- Median 12m max drawdown: -13.7%

## Interpretation
- This is a materially better match for the requested behavior than breakout/trend add-on.
- QQQ default signals now cluster around major crash/bottoming windows:
  - 2020-03 crash
  - 2022-03 / 2022-06 / 2022-09 / 2022-12 bottoming process
  - 2025-04 drawdown
- Current best full-search default:
  - `bottom_reversal`
  - `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`
- Still needs stricter walk-forward validation later; current search is still in-sample grid search.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-12 Bearish-Candle Add-On Constraint ==
## User Feedback
- Current long-term radar was buying into the middle of a large up day.
- User does not require buying the exact low, but add-on signals should at least occur on a bearish candle.

## Root Cause
- The prior `tech_breakout` radar was not using future data to generate signals, but it was a momentum confirmation signal.
- It used same-day close, volume, breakout, RSI, and relative strength, so historical labels appeared on the large up candle itself.
- This made the radar too close to chase-buying instead of long-term add-on buying.

## Completed
- Updated `evaluate_long_term_radar()`:
  - Long-term radar signals now require `close < open`.
  - This restriction applies only to long-term radar scoring.
- Added sample protection:
  - Configs with fewer than 3 mature 12-month signals get a negative score and cannot dominate because of one lucky historical signal.
- Updated generated Pine template in `investigations/uptrend_dip_search.py`:
  - Buy signals require bearish candle.
- Updated standalone Pine file:
  - `investigations/long_term_addon_radar.pine`
  - Default changed to current full-search radar:
    - Strategy: `trend_breakout`
    - Threshold: 40
    - Weights: compression 0.15, breakout 0.30, volume 0.20, momentum 0.20, trend 0.15
  - Signals require `close < open`.
- Added tests:
  - Radar ignores bullish-candle signals.
  - Radar penalizes too few mature signals.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 7 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - Selected `trend_breakout`, threshold 50.
  - QQQ: 6 bearish-candle signals, avg 6m +13.7%, avg 12m +28.1%, avg 24m +54.5%, avg 12m max drawdown -12.2%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - Selected `trend_breakout`, threshold 40.
  - QQQ: 11 bearish-candle signals, avg 6m +14.7%, avg 12m +28.1%, avg 24m +49.2%, avg 12m max drawdown -8.9%.
  - SPY: 6 bearish-candle signals, avg 6m +11.8%, avg 12m +21.0%, avg 24m +31.7%, avg 12m max drawdown -4.5%.

## Current Tech Subset After Bearish-Candle Filter
- Average signals: 10.3
- Average mature 12m signals: 8.7
- Average 6m return: +33.1%
- Average 12m return: +93.7%
- Average 24m return: +217.0%
- Average 12m max drawdown: -12.6%

## Current Pine Files
- `investigations/long_term_addon_radar.pine`
  - Clean long-term add-on radar, bearish-candle only.
- `investigations/uptrend_dip_pine.pine`
  - Full generated buy/sell indicator, also updated by the search run.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Prompt-To-Artifact Audit Checklist ==
## Objective
- Continue the tech-stock buy/sell timing research without adding new signal complexity.
- Make the current deliverables easier to audit against the user's explicit requirements.

## Completed
- Added `build_prompt_to_artifact_checklist()` to `investigations/uptrend_dip_search.py`.
- Added `promptToArtifactChecklist` to `investigations/uptrend_dip_results.json`.
- Added `Prompt-To-Artifact Checklist` to `investigations/uptrend_dip_report.md`.
- The checklist maps requirements to evidence for:
  - strategy implementation location
  - `config.py` / `run.py` protection gate
  - buy-signal exploration
  - trend-filter exploration
  - sell-protection exploration
  - long-term add-on scoring
  - bearish-candle entry requirement
  - bottom-reversal / multi-bottom / RSI-divergence support
  - `index_shallow_pullback` labels
  - tech-subset validation
  - QQQ and full-search validation commands
  - walk-forward / overfitting checks
  - Pine synchronization
- Added unit coverage for the checklist helper and JSON/report exposure.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 30 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Current Interpretation
- This session did not change strategy behavior.
- The current broad long-term add-on default remains `bottom_reversal`.
- The work is better documented and auditable, but still should not be called production-grade until more rolling or anchored validation windows are added.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Multi-Window Validation ==
## Objective
- Continue reducing overfitting risk for the tech-stock long-term add-on radar.
- Address the previous caveat that more rolling / anchored validation windows were still missing.

## Completed
- Added `evaluate_multi_window_validation()` in `investigations/uptrend_dip_search.py`.
- The new diagnostic freezes the current broad default config and evaluates it across:
  - anchored holdout starts: 2021, 2022, 2023, 2024
  - fixed two-year windows: 2021-2022, 2022-2023, 2023-2024, 2024-2025
- Added `multiWindowValidationRadar` to `investigations/uptrend_dip_results.json`.
- Added `Multi-Window Validation` to `investigations/uptrend_dip_report.md`.
- Updated validation caveats:
  - the report no longer says rolling/anchored windows are missing
  - it now says production readiness still needs live paper-trading or a later true out-of-sample period
- Updated the prompt-to-artifact checklist so the overfitting-risk item cites the new multi-window validation.
- Added tests for:
  - the multi-window helper
  - JSON exposure
  - report exposure

## Multi-Window Results
- Anchored 2021+: 77 signals, 68 mature 12m, signal avg 12m +42.9%, signal 12m DD -23.3%.
- Anchored 2022+: 71 signals, 62 mature 12m, signal avg 12m +42.4%, signal 12m DD -24.2%.
- Anchored 2023+: 35 signals, 26 mature 12m, signal avg 12m +68.5%, signal 12m DD -12.4%.
- Anchored 2024+: 28 signals, 19 mature 12m, signal avg 12m +54.4%, signal 12m DD -14.7%.
- Rolling 2021-2022: 46 signals, 46 mature 12m, signal avg 12m +33.4%, signal 12m DD -29.7%.
- Rolling 2022-2023: 43 signals, 43 mature 12m, signal avg 12m +37.1%, signal 12m DD -30.4%.
- Rolling 2023-2024: 15 signals, 15 mature 12m, signal avg 12m +82.2%, signal 12m DD -10.3%.
- Rolling 2024-2025: 22 signals, 19 mature 12m, signal avg 12m +54.4%, signal 12m DD -16.1%.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- Targeted multi-window unit test
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 31 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Current Interpretation
- This session did not change strategy signals or thresholds.
- The new windows show the default `bottom_reversal` config remains positive across multiple historical cuts, but older 2021-2022 style windows had deeper drawdown.
- The current strategy is better validated than before, but still should be paper-tested before being treated as production-grade.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Multi-Window Stability Summary ==
## Objective
- Make the multi-window validation easier to interpret.
- Surface the worst historical window and drawdown risk without changing strategy signals.

## Completed
- Added `summary` to `multiWindowValidationRadar`.
- Summary fields include:
  - total window count
  - mature 12m window count
  - total signals
  - number of positive 12m windows
  - min / median / max signal-level 12m return
  - worst signal-level 12m drawdown
- Added the summary to the executive summary and `Multi-Window Validation` report section.
- Updated the prompt-to-artifact checklist wording so production-readiness caveat now points to live paper-trading or later true out-of-sample validation, not missing rolling windows.
- Added unit coverage for the summary fields and report text.

## Stability Summary
- Windows: 8 total, 8 with mature 12m samples.
- Total multi-window signals: 337.
- Positive 12m windows: 8.
- Signal avg 12m min / median / max: +33.4% / +48.6% / +82.2%.
- Worst signal 12m drawdown across windows: -30.4%.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- Targeted multi-window unit test
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 31 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Current Interpretation
- No signal logic changed.
- The current `bottom_reversal` default now has a compact stability summary: returns stayed positive across all added validation windows, but older 2021-2023 windows show drawdown risk around -30%.
- This makes the strategy easier to judge as a long-term add-on radar rather than a short-term high-win-rate system.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Signal Factor Snapshot ==
## Objective
- Improve explainability of current tech-stock radar signals.
- Show why a signal fired without changing any strategy formula, threshold, or Pine behavior.

## Completed
- Added `addon_factor_snapshot()` in `investigations/uptrend_dip_search.py`.
- Each long-term radar signal now includes `factorSnapshot` in JSON output.
- For `bottom_reversal`, snapshots include:
  - 252-day drawdown
  - bottom retest score
  - RSI divergence score
  - crash score
  - capitulation score
  - RSI(14)
  - volume ratio
- For `index_shallow_pullback`, snapshots include:
  - 252-day drawdown
  - drawdown-band score
  - support score
  - RSI reset score
  - decline score
  - trend-health score
- Added a compact `Drivers` column to:
  - Latest Global-Default Tech Signals
  - Current Tech Radar Watchlist
- Added unit coverage proving long-term radar signals include factor snapshots and the report exposes the `Drivers` column.

## Current Watchlist Examples
- CRM 2026-02-19: DD -42.5%, bottom retest 100, RSI divergence 63, capitulation 6, RSI 25.8, volume 0.72x.
- AMZN 2026-02-09: DD -17.8%, bottom retest 100, RSI divergence 60, capitulation 34, RSI 30.9, volume 1.68x.
- MSFT 2026-02-05: DD -27.2%, bottom retest 40, RSI divergence 37, capitulation 38, RSI 29.1, volume 1.66x.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- Targeted factor snapshot unit test
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 32 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Current Interpretation
- No signal logic changed.
- The current radar is now easier to inspect: a signal can be checked by its actual contributing factors, not only by a combined score.
- This directly addresses earlier concerns about unclear or suspicious signal placement.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Retest After Timeout ==
## Objective
- Re-run the latest strategy search after the previous command timed out.
- Confirm whether the issue was a real failure or a too-short command timeout.

## Completed
- Re-ran the quick single-symbol validation on QQQ.
- Re-ran the full `--symbol all` validation.
- Confirmed the new actionability fields are present in both report and JSON output:
  - `Action`
  - `Risk Flags`
  - `actionProfile`

## Validation Commands Run
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 113.8 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 323.6 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 32 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Current Interpretation
- The timeout was not reproduced with longer command timeouts.
- The QQQ quick run took about 2 minutes.
- The full all-symbol run took about 5 minutes 24 seconds.
- No strategy signal formula changed in this retest; the latest code change only adds action/risk explanation fields to report and JSON output.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 RSI Divergence Baseline ==
## Objective
- Test the user's concern that a plain RSI-divergence indicator may be more accurate than the current composite bottom strategy.
- Add the comparison as a buy-signal-only experiment, without changing sell logic or trend filters.

## Completed
- Added a standalone `rsi_divergence` buy strategy.
- Added RSI-divergence candidate configs to stage-1 grid search.
- Added `score_buy_rsi_divergence()` as a separate scoring function.
- Added RSI-divergence strength labels:
  - `RSI Divergence - Strong`
  - `RSI Divergence - Medium`
  - `RSI Divergence - Watch`
- Added factor snapshots and action/risk flags for RSI-divergence signals.
- Added the RSI-divergence baseline to frozen candidate validation.
- Synchronized both Pine outputs:
  - `investigations/uptrend_dip_pine.pine`
  - `investigations/long_term_addon_radar.pine`
- Added unit coverage for:
  - standalone RSI-divergence scoring
  - stage-1 candidate inclusion
  - generated Pine support
  - standalone Pine matching generated defaults from JSON

## Comparison Result
- Current default remains `bottom_reversal`.
- `bottom_reversal`: combined 96.86, QQQ 6 signals / avg 12m +39.4%, SPY 3 signals / avg 12m +26.6%.
- `rsi_divergence`: combined 81.41, QQQ 8 signals / avg 12m +29.1%, SPY 9 signals / avg 12m +21.9%.
- Interpretation: RSI divergence is useful, but as a standalone signal it underperformed the composite `bottom_reversal` strategy. The better read is to keep RSI divergence as one component inside the deep-bottom model, not as the only entry trigger.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 116.9 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 333.3 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 35 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Completion Audit Snapshot ==
## Objective
- Audit whether the active goal can be marked complete.
- Avoid mistaking a well-tested research artifact for a production-proven strategy.

## Concrete Deliverables Checked
- Strategy implementation stays in `investigations/uptrend_dip_search.py`.
- `config.py` and `run.py` remain untouched.
- Buy-signal exploration includes:
  - tech breakout
  - trend breakout
  - bottom reversal
  - standalone RSI divergence baseline
  - index shallow pullback
- Trend filters include ADX and moving-average slope through `trend_breakout`.
- Sell protection exists in the stage-2 trade simulator:
  - fixed stop
  - profit drawdown trailing
  - ATR trailing
  - sell-signal exits
- Long-term add-on optimization is represented by `longTermRadar`.
- TradingView Pine outputs exist for:
  - full buy/sell indicator
  - standalone long-term add-on radar
- Validation evidence exists for:
  - QQQ quick run
  - `--symbol all`
  - date split
  - restricted walk-forward
  - full-grid walk-forward
  - multi-window validation
  - risk diagnostics

## Evidence Checked
- `investigations/uptrend_dip_results.json`
  - JSON parse: PASS.
  - Prompt-to-artifact checklist count: 15.
  - Recommended default: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - `techSubsetSignalRiskDiagnostics`: present.
  - Pine paths present.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.
- `git diff --check`
  - PASS.

## Audit Result
- The research implementation is substantially covered.
- The active goal should not be marked complete yet because the remaining proof gap is external to historical backtests:
  - live paper-trading or future out-of-sample evidence is still missing.
- This is consistent with the report caveat that production use still needs future evidence.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Signal Risk Diagnostics ==
## Objective
- Quantify the weak spots of the current `bottom_reversal` radar before adding any new filter.
- Avoid guessing which risk flags should be removed.

## Completed
- Added `summarize_signal_risk_diagnostics()`.
- Added `techSubsetSignalRiskDiagnostics` to JSON output.
- Added `Tech Signal Risk Diagnostics` to the report.
- Diagnostics group global-default tech signals dated 2023-01-01 or later by:
  - risk flags
  - strength labels
- Added unit coverage for the diagnostic grouping.

## Diagnostic Result
- Global-default tech signals since 2023: 31.
- Risk flag groups:
  - `no_risk_flags`: 7 signals, 5 mature 12m, avg 12m +41.9%, avg 12m DD -10.4%.
  - `no_volume_expansion`: 10 signals, 8 mature 12m, avg 12m +69.6%, avg 12m DD -19.7%.
  - `weak_bottom_retest`: 12 signals, 9 mature 12m, avg 12m +86.2%, avg 12m DD -11.0%.
  - `weak_rsi_divergence`: 16 signals, 12 mature 12m, avg 12m +82.6%, avg 12m DD -11.8%.
- Strength groups:
  - `Deep Bottom - Medium`: 22 signals, 15 mature 12m, avg 12m +64.5%, avg 12m DD -14.2%.
  - `Deep Bottom - Strong`: 9 signals, 7 mature 12m, avg 12m +58.4%, avg 12m DD -12.2%.

## Interpretation
- Do not blindly filter out `weak_rsi_divergence` or `weak_bottom_retest`; historically those tags did not worsen 12m drawdown in this sample.
- `no_volume_expansion` is the clearest higher-drawdown flag, but it also had strong 12m returns, so it is better treated as a position-sizing or monitoring warning rather than a hard exclusion.
- This supports keeping the current composite `bottom_reversal` formula unchanged for now.

## Validation Commands Run
- Non-`.pyc` syntax check for `investigations/uptrend_dip_search.py` and `tests/test_uptrend_dip_search.py`
  - PASS after rerun.
  - Note: the first syntax check ran in parallel with unittest and hit a Windows `__pycache__` write conflict; rerunning it alone passed.
- Targeted diagnostic unit test
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 117.0 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 335.5 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 36 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Timeout Retest ==
## Objective
- Re-run the strategy search after the user asked why the previous command timed out.
- Confirm whether the timeout was a strategy/code failure or simply a long-running full search.

## Result
- No code changes were made in this retest.
- The timeout was not reproduced when the command timeout was increased.
- Likely cause: `--symbol all` takes about 5.5 minutes, so a shorter tool timeout can interrupt it even when the strategy itself is still running normally.

## Validation Commands Run
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 115.5 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 334.7 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Active Goal Audit ==
## Objective
- Continue the active goal of finding a suitable U.S. tech-stock timing strategy.
- Avoid repeating completed strategy work.
- Audit the current state before deciding whether the goal is complete.

## Concrete Deliverables Checked
- Main strategy implementation remains in `investigations/uptrend_dip_search.py`.
- Generated user artifacts exist:
  - `investigations/uptrend_dip_report.md`
  - `investigations/uptrend_dip_results.json`
  - `investigations/uptrend_dip_pine.pine`
  - `investigations/long_term_addon_radar.pine`
  - `tests/test_uptrend_dip_search.py`
- Prompt-to-artifact checklist in JSON has 15 items.
- Covered strategy requirements include:
  - buy signal exploration
  - ADX / moving-average slope trend filters
  - sell protection
  - long-term add-on optimization instead of short-term win-rate chasing
  - bearish-candle entry requirement
  - deep crash / double-bottom / RSI-divergence support
  - `index_shallow_pullback`
  - tech subset validation
  - Pine synchronization
- External gates checked:
  - QQQ quick validation was rerun in the previous retest.
  - Full `--symbol all` validation was rerun in the previous retest.
  - `config.py` and `run.py` remain untouched.

## Fresh Verification
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 37 tests.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- Pine ASCII check
  - PASS; both generated Pine files are ASCII-only.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Paper Tracking State
- `paperTrackingPlan.generatedDate`: 2026-05-13.
- Current tracked signals: 7.
- Pending 6m checks: 7.
- Pending 12m checks: 7.
- Next 6m paper check: CRM signal from 2025-11-17, check date 2026-05-19.

## Audit Result
- Do not mark the active goal complete yet.
- Historical backtests, reports, Pine outputs, and tests are in place.
- The remaining proof gap is future/paper evidence; current signals have not matured to 6m/12m outcomes.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Future Check Scheduling Attempt ==
## Objective
- Continue the active goal without repeating completed historical backtests.
- Try to schedule a future follow-up for the first pending paper-tracking checkpoint.

## Attempted Next Action
- Target follow-up:
  - CRM signal date: 2025-11-17.
  - 6-month paper check date: 2026-05-19.
  - Purpose: verify whether the first current paper-tracking signal strengthens or weakens the long-term add-on radar.

## Result
- Attempted to create a thread heartbeat automation through the Codex automation tool.
- The tool returned `dynamic tool request failed` on multiple valid-looking heartbeat schedules.
- No automation was created.
- I did not hand-write automation files, because raw automation workarounds are not the intended interface.

## Current State
- The active goal is still not complete.
- The next concrete evidence-based step remains:
  - On or after 2026-05-19, rerun/refresh the radar and inspect the CRM 2025-11-17 signal's 6-month outcome and drawdown.
- Historical backtest work should not be repeated unless the strategy logic changes or new market data is available.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Paper Tracking Summary Fields ==
## Objective
- Continue the active goal by improving the future-validation workflow rather than repeating historical backtests.
- Make the next paper-tracking checkpoint visible directly in JSON and the report.

## TDD
- Added failing test coverage to `test_build_paper_tracking_plan_adds_future_check_dates`.
- Verified the test failed because `overduePending6mCount` was missing.
- Implemented the minimal change in `build_paper_tracking_plan()`.
- Re-ran the targeted test and full test suite.

## Completed
- Added paper-tracking summary fields:
  - `overduePending6mCount`
  - `overduePending12mCount`
  - `nextPending6mDate`
  - `nextPending12mDate`
  - `nextPendingCheckDate`
- Updated `investigations/uptrend_dip_report.md` generation to display:
  - overdue pending 6m checks
  - overdue pending 12m checks
  - next pending check date
- Did not change buy/sell scoring, strategy thresholds, Pine strategy formulas, `config.py`, or `run.py`.

## Latest Paper Tracking Output
- `nextPendingCheckDate`: 2026-05-19.
- `nextPending6mDate`: 2026-05-19.
- `nextPending12mDate`: 2026-11-17.
- `overduePending6mCount`: 0.
- `overduePending12mCount`: 0.

## Validation Commands Run
- Targeted paper-tracking unit test
  - PASS after the expected RED failure.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 37 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 115.8 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 329.9 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "Overdue pending|Next pending check date|Paper Tracking Plan" investigations/uptrend_dip_report.md`
  - PASS; report contains the new summary rows.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Audit Result
- The active goal remains open.
- The next evidence-based step is now explicit in generated artifacts: revisit paper tracking on 2026-05-19.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Paper Tracking Checklist Coverage ==
## Objective
- Continue the active goal by tightening the completion audit trail.
- Make future paper-validation tracking an explicit prompt-to-artifact checklist item.

## TDD
- Added a failing assertion to `test_prompt_to_artifact_checklist_maps_core_requirements`.
- Verified it failed because `Track future paper-validation checkpoints` was missing from the checklist.
- Added the checklist item in `build_prompt_to_artifact_checklist()`.
- Re-ran the targeted test and full validation.

## Completed
- `promptToArtifactChecklist` now has 16 items.
- New checklist item:
  - `Track future paper-validation checkpoints for current tech signals.`
- Evidence in generated artifacts:
  - `paperTrackingPlan` tracks 7 signals.
  - `nextPendingCheckDate` is 2026-05-19.
  - overdue pending 6m / 12m checks are 0 / 0.
- This is an audit/reporting improvement only; buy/sell formulas and Pine strategy formulas were not changed.

## Validation Commands Run
- Targeted checklist unit test
  - PASS after the expected RED failure.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 37 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 129.0 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 367.9 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- Checklist artifact check
  - PASS; JSON/report include the paper-validation checklist item.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Audit Result
- Active goal remains open.
- The strategy research and generated artifacts now explicitly acknowledge and track the remaining future-evidence requirement.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Paper Status CLI ==
## Objective
- Continue the active goal by making future paper validation easier to check without rerunning the full grid search.
- Avoid repeating 5-6 minute historical backtests just to inspect the current paper-tracking state.

## TDD
- Added a failing test for `format_paper_tracking_status()`.
- Verified it failed because the function did not exist.
- Implemented `format_paper_tracking_status()`.
- Added `--paper-status` to print the latest `paperTrackingPlan` from `investigations/uptrend_dip_results.json`.

## Completed
- New lightweight command:
  - `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status`
- The command reads existing JSON only; it does not rerun the strategy search.
- Output includes:
  - generated date
  - tracked signal count
  - pending 6m/12m counts
  - overdue pending 6m/12m counts
  - next pending check date
  - signal rows with 6m/12m check dates, status, strength, action, and risk flags

## Latest Paper Status Output
- Generated date: 2026-05-13.
- Tracked signals: 7.
- Pending checks: 6m=7, 12m=7.
- Overdue pending checks: 6m=0, 12m=0.
- Next pending check date: 2026-05-19.

## Validation Commands Run
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status`
  - PASS.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 127.3 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 365.3 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Audit Result
- Active goal remains open.
- The next evidence-based step is still future paper validation on or after 2026-05-19, but it can now be checked quickly with `--paper-status`.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Paper Status As-Of Date ==
## Objective
- Finish the paper-status CLI so it remains useful after a future check date passes, even before a full search is rerun.
- Stop repeating strategy grid searches unless strategy logic changes or new market data needs to be refreshed.

## Completed
- Added dynamic as-of-date handling to `format_paper_tracking_status()`.
- Added CLI option:
  - `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status --as-of YYYY-MM-DD`
- The command now computes overdue pending checks at display time.
- Example verified:
  - As of 2026-05-20, the CRM 2025-11-17 signal's 6m check date 2026-05-19 is displayed as `overdue`.

## Validation Commands Run
- Targeted `format_paper_tracking_status()` unit test
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status`
  - PASS.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status --as-of 2026-05-20`
  - PASS; overdue pending checks show 6m=1, 12m=0.
- `.venv\\Scripts\\python.exe -m py_compile investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol QQQ`
  - PASS.
  - Exit code: 0.
  - Elapsed: 130.8 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t55`.
  - QQQ: 4 signals, avg 6m +27.8%, avg 12m +50.9%, avg 24m +84.3%, avg 12m max drawdown -4.5%.
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --symbol all`
  - PASS.
  - Exit code: 0.
  - Elapsed: 362.5 seconds.
  - Long-term radar: `bottom_reversal` / `btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`.
  - QQQ: 6 signals, avg 6m +22.4%, avg 12m +39.4%, avg 24m +72.7%, avg 12m max drawdown -7.0%.
  - SPY: 3 signals, avg 6m +13.4%, avg 12m +26.6%, avg 24m +54.3%, avg 12m max drawdown -9.0%.
- `.venv\\Scripts\\python.exe -m json.tool investigations/uptrend_dip_results.json`
  - PASS.
- `rg "ta\\.sum|math\\.sum" investigations/uptrend_dip_search.py investigations/uptrend_dip_pine.pine investigations/long_term_addon_radar.pine`
  - PASS; no matches.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Current Stop Point
- The active goal remains open because future/paper evidence is not mature yet.
- Do not keep looping historical grid searches.
- Next meaningful action:
  - On or after 2026-05-19, run `--paper-status --as-of 2026-05-20`.
  - If overdue, refresh market data/search once and compare the CRM 2025-11-17 6m outcome and drawdown.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Stop-Loop Audit ==
## Objective
- Respond to the user's concern that work was looping.
- Verify the active goal state without repeating heavy grid searches.

## Lightweight Audit
- Active goal status:
  - Still active.
  - Not complete because 6m/12m future paper evidence has not matured.
- Current default:
  - `bottom_reversal`.
- Prompt-to-artifact checklist:
  - 16 items.
- Paper tracking:
  - Current tracked signals: 7.
  - Pending checks: 6m=7, 12m=7.
  - Overdue checks as of 2026-05-13: 6m=0, 12m=0.
  - Next pending check date: 2026-05-19.

## Verification Commands Run
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status`
  - PASS.
- JSON quick audit command
  - PASS; checklist=16, next=2026-05-19, signals=7, default=bottom_reversal.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Stop Condition
- Do not continue looping historical backtests now.
- Next meaningful action is after 2026-05-19:
  - run `--paper-status --as-of 2026-05-20`;
  - if CRM 2025-11-17 is overdue, refresh once and inspect the actual 6m result/drawdown.

## Next Paper-Validation Decision Rule
- Do not judge the strategy by whether one signal is perfect.
- For the CRM 2025-11-17 signal, record:
  - actual 6m return once available;
  - max drawdown from signal date to the 6m check;
  - whether the original `no_volume_expansion` risk flag corresponded to worse drawdown;
  - whether the signal still fits the intended `Deep Bottom - Strong` behavior.
- Interpret the result conservatively:
  - strengthens radar: 6m return is positive and drawdown is not worse than the historical risk profile already documented for similar signals;
  - weakens radar: 6m return is negative with large drawdown, or the risk flag clearly identifies avoidable damage;
  - inconclusive: return is flat/mixed or data is incomplete, then wait for 12m evidence.
- Do not add new filters from a single paper signal; use it as evidence for future risk-flag weighting or position sizing only.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Final Lightweight Audit ==
## Objective
- Re-check whether any non-future-data work remains.
- Avoid additional strategy-search loops.

## Audit Evidence
- Active goal remains active.
- Current default strategy:
  - `bottom_reversal`.
- Prompt-to-artifact checklist:
  - 16 items.
- Paper tracking:
  - tracked signals: 7.
  - pending 6m checks: 7.
  - pending 12m checks: 7.
  - overdue checks as of 2026-05-13: 6m=0, 12m=0.
  - next pending check date: 2026-05-19.

## Verification Commands Run
- `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status --as-of 2026-05-13`
  - PASS.
- JSON quick audit command
  - PASS; default=bottom_reversal, checklist=16, next=2026-05-19, tracked=7, pending6m=7, pending12m=7.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Audit Result
- Do not mark the goal complete.
- No useful non-future-data work remains at this point.
- Next action is still after 2026-05-19.

## Not Modified
- `config.py`
- `run.py`
==

== Session: 2026-05-13 Report Paper Status Command ==
## Objective
- Make the report itself explain how to check paper-tracking status without rerunning the full grid search.
- Keep this as documentation/report generation only; do not change strategy formulas.

## TDD
- Added a failing report assertion for `--paper-status --as-of`.
- Verified the report test failed because the command was missing.
- Added the quick-check command to the Paper Tracking Plan report section.
- Regenerated the report from existing `uptrend_dip_results.json` without rerunning the full grid search.

## Completed
- `investigations/uptrend_dip_report.md` now includes:
  - `.venv\\Scripts\\python.exe investigations/uptrend_dip_search.py --paper-status --as-of YYYY-MM-DD`
- This lets a non-developer find the lightweight paper-status command directly from the report.

## Validation Commands Run
- Targeted report test
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 38 tests.
- `rg -n -e "--paper-status --as-of" investigations/uptrend_dip_report.md investigations/uptrend_dip_search.py tests/test_uptrend_dip_search.py`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py run.py`
  - PASS; empty output.

## Stop Condition
- Do not rerun historical grid search for this documentation-only change.
- Next meaningful strategy evidence is still after 2026-05-19.

## Not Modified
- `config.py`
- `run.py`
==
