# Auto-Quant Research Progress

## Branch: autoresearch/may17-baseline-next

## Current State Snapshot

- Updated: 2026-05-24.
- Current best strategy: `seed_previous_rs_higher_low_best`.
- Formal Strong signals: 39; avg 6m return: 39.24%.
- QQQ observation: 48 signals, Formal Strong baseline 39, Observation/Formal ratio 1.23x, duplicate formal signals 0.
- QQQ 2022-10-01 to 2022-12-31: Covered via 2022-10-03, 2022-10-11, 2022-12-28.
- QQQ 2026-03-01 to 2026-03-31: Covered via 2026-03-27.
- Full workers validation: `--symbol all --max-configs 720 --workers 4` passed again on 2026-05-20 in about 9 minutes 54 seconds; observation refresh passed afterward.
- Artifact guard: `bottom_signal_results.json` now records `artifactScope`; full-pool output has `fullPool=true`, QQQ/SPY quick samples are marked `QQQ_SPY_SAMPLE`.
- Pine parity guard: selected observation config now includes `bottomMax=75`; main TradingView Pine uses that value through `obsBottomMax`, independent from formal `watchThreshold`.
- Worker benchmark: on `QQQ,SPY / max-configs 72`, workers 4 was fastest in this run at 13.37s; keep `--workers 4` as the recommended full-search operator command.
- Observation sensitivity: nearest variants all preserved both QQQ anchor windows; keep current observation config as candidate-only default because looser `clusterWindow=21` raises signals to 74, close to the 78 sparse target.
- Stability prune: duplicate dual-track Bottom Signal artifacts were removed after confirming they matched the main report/JSON exactly; `bottom_signal_search.py` no longer writes those duplicate files.
- Current important commands:
  - `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - `.venv\Scripts\python.exe -m json.tool strategy_catalog\bottom_signal_formal\bottom_signal_results.json`
  - `git diff --check`
- Strategy catalog: Pine-capable strategy artifacts now live under `strategy_catalog/`; research scripts remain under `investigations/`.
- Unfinished / notes: strategy catalog cleanup is complete; TradingView main Pine now shows strict MB plus OBS-D/OBS-S as `BUY-MB`/`BUY-D`/`BUY-S`, while strict MB metrics remain the baseline.
- Archive: older sessions moved to `docs/archive/claude-progress-archive-2026-05.md`.
- Active plan file: `docs/plans/autoquantstock_2022_2026_miss_full_search_plan.md`.

## Recent Sessions

--- Session: 2026-05-24 Push Handoff ---
## Objective
- Leave a concise handoff before archiving and pushing the current strategy/documentation state.

## Completed
- Added `Codex-progress.md` as the short handoff file requested by project docs.
- Kept `claude-progress.md` as the detailed chronological research log.
- Handoff points the next agent to:
  - `strategy_catalog/bottom_signal_formal/README_中文学习版.md`;
  - `claude-progress.md`;
  - `docs/策略目录.md`.

## Pending
- Commit and push the current branch archive after this handoff entry.

## Known Issues
- The current worktree includes accumulated strategy catalog moves, generated strategy artifacts, Pine updates, documentation updates, and deleted old loose investigation artifacts.
- `bottom_signal_results_2022_2026_miss_expanded.json` exceeds GitHub's 100 MB file limit; archive push uses `bottom_signal_results_2022_2026_miss_expanded.json.gz`, while the raw JSON remains local and ignored.
- Full search was not rerun after the final README-only update.

## Verification
- Previously verified Bottom Signal unit tests, full test discovery, py_compile, JSON parsing, `git diff --check`, and protected-file checks.

--- Session: 2026-05-24 Bottom Signal 中文学习 README ---
## Objective
- 新增一份中文学习型 README，帮助非全职开发者理解 Bottom Signal 的策略搜索过程、推理路径和当前主 Pine 的信号含义。

## Completed
- 新增 `strategy_catalog/bottom_signal_formal/README_中文学习版.md`。
- 文档覆盖：
  - 当前主 Pine 为什么是统一入口；
  - 策略目标不是预测最低点，而是找深回撤后的高质量入场窗口；
  - 数据来源、21 个 symbol、日线 OHLCV、QQQ/SPY 市场过滤；
  - MB 六类核心因子：drawdown、momentum、structure、volume、ma、repair；
  - 参数搜索、打分、门槛、信号数量控制和过拟合过滤；
  - 为什么选择 `seed_previous_rs_higher_low_best`；
  - 2022/2026 严格 MB 缺失信号如何由 OBS 覆盖；
  - `BUY-MB`、`BUY-D`、`BUY-S`、RS、Exit 的含义；
  - 后续研究阅读顺序和命令；
  - 常用术语表。
- 更新 `strategy_catalog/bottom_signal_formal/README.md`，加入学习版入口。
- 更新 `docs/策略目录.md`，把学习版作为 Bottom Signal 的第一阅读入口。

## Validation Commands Run
- `Get-Content strategy_catalog\bottom_signal_formal\README_中文学习版.md -TotalCount 80`
  - PASS; 文档可读取。
- `rg -n "README_中文学习版|BUY-MB|BUY-D|BUY-S|seed_previous_rs_higher_low_best|2026-03-27" strategy_catalog\bottom_signal_formal docs\策略目录.md`
  - PASS; 学习入口和关键信号说明可检索。
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

--- Session: 2026-05-24 Integrated Formal Pine ---
## Objective
- Make `strategy_catalog/bottom_signal_formal/bottom_signal_pine.pine` the single TradingView entry point.
- Show strict MB Strong plus OBS-D/OBS-S as visible buy-style signals so 2026 March OBS coverage is not hidden in a separate script.

## Completed
- Changed the main Pine generator so `bottom_signal_pine.pine` outputs `BUY-MB`, `BUY-D`, and `BUY-S`.
- Kept `bottom_signal_strict_formal.pine` as the strict MB-only archive.
- Updated output routing so future Bottom Signal writes regenerate both integrated and strict Pine files.
- Updated tests for the integrated Pine contract: OBS inputs, `BUY-*` labels, green background, and alerts.
- Updated strategy catalog docs to make the integrated Pine the primary TradingView file and the merged observation Pine a diagnostic file.
- Confirmed QQQ `2026-03-27` is present in the OBS signal CSV as `OBS-S`; with the integrated Pine, that source maps to `BUY-S`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 108 tests.
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
  - PASS, 151 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool strategy_catalog\bottom_signal_formal\bottom_signal_results.json > $null`
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

--- Session: 2026-05-23 Strategy Catalog Reorganization ---
## Objective
- Move existing Pine-capable strategy artifacts out of `investigations/` into `strategy_catalog/`, with one folder per strategy and a single directory index.

## Completed
- Created `strategy_catalog/` folders for:
  - `bottom_signal_formal`;
  - `bottom_signal_observation_addon`;
  - `bottom_signal_2022_2026_research`;
  - `uptrend_dip_buy_sell`;
  - `long_term_addon_radar`;
  - `buy_dip_indicator`;
  - `_reference/us_index_zone`.
- Added `README.md` and `SEARCH_FLOW.md` for each Pine strategy folder.
- Added `docs/策略目录.md` as the strategy entry point.
- Updated `docs/策略目录.md` to list each strategy's status, purpose, Pine path, core report, search command, TradingView availability, and whether it is allowed as a formal buy point.
- Moved existing Pine, report, JSON, and CSV artifacts into the matching strategy folders.
- Kept `investigations/` as the script entry-point folder only.
- Updated output routing in:
  - `investigations/bottom_signal_paths.py`;
  - `investigations/bottom_signal_search.py`;
  - `investigations/uptrend_dip_search.py`;
  - `investigations/buy_dip_search.py`.
- Updated current documentation references in `docs/document_archive.md` and `docs/plans/`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 107 tests.
- `.venv\Scripts\python.exe -m unittest tests.test_uptrend_dip_search`
  - PASS, 39 tests.
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
  - PASS, 150 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py investigations\uptrend_dip_search.py investigations\buy_dip_search.py tests\test_bottom_signal_search.py tests\test_uptrend_dip_search.py`
  - PASS.
- JSON validation for:
  - `strategy_catalog\bottom_signal_formal\bottom_signal_results.json`;
  - `strategy_catalog\bottom_signal_2022_2026_research\bottom_signal_results_2022_2026_miss_expanded.json`;
  - `strategy_catalog\uptrend_dip_buy_sell\uptrend_dip_results.json`;
  - `strategy_catalog\buy_dip_indicator\buy_dip_results.json`.
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Completion audit:
  - all required strategy catalog files are present;
  - every Pine strategy folder has `README.md`, `SEARCH_FLOW.md`, and at least one `.pine`;
  - `investigations/` has no loose `.pine`, `.json`, `.csv`, or `.md` strategy artifacts;
  - README and SEARCH_FLOW content checks passed;
  - special status notes are explicit for formal MB Strong, OBS/RS add-on, 2022/2026 319-signal failure, long-term radar, and US Index Zone no-Pine reference.

## Notes
- `docs/archive/claude-progress-archive-2026-05.md` still contains historical old-path references by design; current docs and strategy artifacts point to `strategy_catalog/`.

--- Session: 2026-05-23 2022/2026 Plan Execution Audit ---
## Objective
- Check whether `docs/plans/autoquantstock_2022_2026_miss_full_search_plan.md` was executed correctly.
- Verify the result from current files and command outputs rather than relying on prior conversation memory.

## Completed
- Audited main baseline:
  - best config remains `seed_previous_rs_higher_low_best`;
  - symbol count remains 21;
  - formal signals remain 39;
  - OBS duplicate formal count remains 0.
- Audited standard tagged search:
  - `bottom_signal_results_2022_2026_miss_search.json` exists;
  - best config remains the baseline;
  - OBS covers QQQ 2022 Q4 and QQQ 2026 March in tagged outputs.
- Audited expanded search:
  - `bottom_signal_results_2022_2026_miss_expanded.json` exists;
  - 12 single-formal configs cover both target windows;
  - lowest single-formal signal count is 319, so replacement is rejected as too broad.
- Audited composite strategy:
  - `baseline_formal_plus_obs_addon_v1` has 39 formal rows, 48 OBS rows, 87 total rows;
  - QQQ 2022 Q4 has 3 covered anchor rows;
  - QQQ 2026 March has 1 covered anchor row.
- Created audit report:
  - `investigations/bottom_signal_2022_2026_plan_execution_audit.md`.
- Pruned intermediate `seed_probe` and `shallow_probe` tagged artifacts because final `miss_search`, `miss_expanded`, and composite reports retain the useful evidence.

## Deviations Recorded
- Research config intentionally went beyond the initial narrow expansion:
  - included `entry_threshold=72`;
  - used lower MB offsets such as `-8` and `-5`;
  - relaxed research-only market drawdown threshold to `-8`;
  - disabled research-only signal-count hard rejection to measure signal explosion.
- This is acceptable because it is isolated in the research config and tagged outputs, while the official baseline remains unchanged.
- Refresh commands were extended to honor `--research-tag`; this protects main outputs when refreshing OBS for tagged research results.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 106 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
  - PASS, 148 tests.
- JSON validation for:
  - `investigations\bottom_signal_results.json`;
  - `investigations\bottom_signal_results_2022_2026_miss_search.json`;
  - `investigations\bottom_signal_results_2022_2026_miss_expanded.json`;
  - `investigations\bottom_signal_config_2022_2026_miss_search.json`.
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

--- Session: 2026-05-23 2022/2026 Miss Full Search Execution ---
## Objective
- Execute `docs/plans/autoquantstock_2022_2026_miss_full_search_plan.md`.
- Continue until finding a strategy shape where the existing signals and QQQ 2022/2026 drawdown coverage coexist.

## Completed
- Implemented research-tag isolated output routing in `investigations/bottom_signal_search.py`.
- Added 2022/2026 missing-formal diagnostics and candidate-review CSV generation.
- Created research-only config `investigations/bottom_signal_config_2022_2026_miss_search.json`.
- Ran standard isolated full search:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4 --research-tag 2022_2026_miss_search`
  - Result: best stayed `seed_previous_rs_higher_low_best`; no single formal config covered QQQ 2022 Q4 and QQQ 2026 March.
- Refreshed tagged OBS search:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search --research-tag 2022_2026_miss_search`
  - Result: OBS signals 48, QQQ anchor windows covered.
- Ran expanded shallow-market isolated search:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --config investigations\bottom_signal_config_2022_2026_miss_search.json --max-configs 1440 --workers 4 --research-tag 2022_2026_miss_expanded`
  - Result: 12 single-formal configs covered both QQQ 2022 Q4 and QQQ 2026 March, but the lowest-count one still had 319 signals, so it is too broad as a replacement.
- Found current research strategy shape:
  - `baseline_formal_plus_obs_addon_v1`
  - rule: keep current 39 formal baseline signals and add current 48 OBS-D/OBS-S candidates as a research-only add-on.
  - combined signals: 87.
  - existing formal signals preserved: 39/39.
  - mature 6m avg return: 28.23%.
  - mature 6m win rate: 73.26%.
  - QQQ 2022 Q4 covered by 2022-10-03, 2022-10-11, 2022-12-28.
  - QQQ 2026 March covered by 2026-03-27.
- Created:
  - `investigations/bottom_signal_2022_2026_composite_strategy_report.md`
  - `investigations/bottom_signal_2022_2026_composite_strategy_signals.csv`

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 106 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS after rerun; first parallel attempt conflicted on Windows `__pycache__`.
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
  - PASS, 148 tests.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results_2022_2026_miss_expanded.json > $null`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_config_2022_2026_miss_search.json > $null`
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

## Notes
- Do not promote `baseline_formal_plus_obs_addon_v1` directly to live/Pine formal use without a separate promotion validation plan.
- Single formal parameter replacement is currently rejected because the configs that cover both 2022 and 2026 produce hundreds of signals.

--- Session: 2026-05-23 2022/2026 Miss Full Search Plan File ---
## Objective
- Persist the AutoQuantStock 2022/2026 missing-formal-signal full exploration plan locally.
- Keep the current compressed Bottom Signal baseline protected while documenting the next research path.

## Completed
- Created `docs/plans/autoquantstock_2022_2026_miss_full_search_plan.md`.
- The plan covers:
  - preserving `seed_previous_rs_higher_low_best` as the official baseline;
  - adding isolated research outputs with a `--research-tag`;
  - diagnosing why QQQ 2022 Q4 and 2026 March were formal-missed but OBS-covered;
  - reviewing existing 311 search results before expanding the grid;
  - running isolated full searches without overwriting the compressed main JSON/report;
  - optional narrow research-only grid expansion.

## Validation Commands Run
- `Get-Content docs\plans\autoquantstock_2022_2026_miss_full_search_plan.md -TotalCount 60`
  - PASS; document is readable and starts with the expected implementation-plan header.
- `git diff --check -- docs\plans\autoquantstock_2022_2026_miss_full_search_plan.md claude-progress.md`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

--- Session: 2026-05-23 Compressed Strategy Plan Completion Audit ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Audit the current worktree against the original plan requirements instead of adding another review feature.
- Confirm whether the compressed baseline and review artifacts are internally consistent.

## Audit Evidence
- `bottom_signal_results.json` current facts:
  - `bestConfig.name=seed_previous_rs_higher_low_best`;
  - `entry_threshold=82`;
  - symbol count 21;
  - `artifactScope.fullPool=true`, `sampleKind=FULL_POOL`;
  - formal Strong signals 39;
  - recent mature signals 7, status `Pass`;
  - OBS signals 48, Observation/Formal ratio 1.23x;
  - `duplicateFormalCount=0`.
- `bottom_signal_strategy_iteration_review.md` confirms:
  - all plan validation gates are PASS;
  - retired dual-track artifacts are absent;
  - five main artifacts exist;
  - original six plan steps are DONE with evidence.
- File checks confirm:
  - all five main artifacts exist;
  - `Get-ChildItem investigations -Filter '*dual_track_rs*'` is empty;
  - no diff in `config.py`, `prepare.py`, `run.py`, or `versions`.
- Rule checks confirm:
  - config weights retain `drawdown`, `momentum`, `repair`, `structure`, `volume`, and `ma`;
  - observation report says OBS is candidate-only and does not change the formal MB strategy;
  - strategy review says not to promote OBS/RS into formal entries.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
  - PASS, 145 tests.
- `.venv\Scripts\python.exe -m py_compile quant_indicators.py investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py investigations\uptrend_dip_search.py investigations\buy_dip_search.py investigations\us_index_zone_research.py tests\test_bottom_signal_search.py tests\test_uptrend_dip_search.py tests\test_quant_indicators.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- `Get-ChildItem investigations -Filter '*dual_track_rs*'`
  - PASS; empty output.
- Main artifact existence checks:
  - PASS for `bottom_signal_search.py`, `bottom_signal_config.json`, `bottom_signal_results.json`, `bottom_signal_report.md`, and `bottom_signal_observation_report.md`.
- Report failure scan:
  - PASS; no `FAIL`, `TODO`, or `missing` markers in `bottom_signal_strategy_iteration_review.md`.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Notes
- Full `all / 720 / --workers 4` search was not run because the audit did not modify search logic or configuration.
- The compressed strategy iteration plan is currently represented and verified by generated artifacts; future work should move to a separate promotion/ablation plan only if OBS/RS is being considered for formal entry.

--- Session: 2026-05-23 Strategy Plan Step Status Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Map the original six research steps into an explicit status checklist in the review artifacts.
- Make completion evidence easier to audit without changing strategy rules.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_reports_strategy_plan_step_status`
- Verified RED first:
  - strategy iteration report did not contain a `Strategy Plan Step Status` section.
- Implemented the minimum plan-step status output.

## Completed
- `bottom_signal_strategy_iteration_review.md` now includes `Strategy Plan Step Status`.
- `bottom_signal_strategy_iteration_review.csv` now includes `PlanStepStatus` rows.
- Current full-pool step status:
  - DONE 1 Baseline confirmation: `seed_previous_rs_higher_low_best`; symbols=21; signals=39.
  - DONE 2 Recent sample review: mature=7; status=Pass.
  - DONE 3 OBS candidate segmentation: signals=48; riskBuckets=4.
  - DONE 4 RS watchlist review: monitor=2; review=7; skip=3.
  - DONE 5 Formal-missed OBS cases: cases=48.
  - DONE 6 Promotion validation plan: preconditions=4.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_strategy_plan_step_status`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_plan_validation_gates tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_promotion_preconditions tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_retired_dual_track_artifact_guard tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_validation_command_checklist tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_main_artifact_manifest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_strategy_plan_step_status`
  - PASS, 12 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
  - PASS, 145 tests.
- `.venv\Scripts\python.exe -m py_compile quant_indicators.py investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py investigations\uptrend_dip_search.py investigations\buy_dip_search.py investigations\us_index_zone_research.py tests\test_bottom_signal_search.py tests\test_uptrend_dip_search.py tests\test_quant_indicators.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- `Get-ChildItem investigations -Filter '*dual_track_rs*'`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only adds a status checklist to the review layer.
- The checklist makes the original six-step plan auditable from the generated artifacts.

--- Session: 2026-05-23 Repo-Wide Validation Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Address the gap that recent turns only ran Bottom Signal focused tests.
- Add the repo-wide unittest discovery command to the strategy review validation checklist.

## Completed
- Ran the current full unittest discovery set:
  - `test_bottom_signal_search.py`
  - `test_quant_indicators.py`
  - `test_uptrend_dip_search.py`
- Added `repo-wide` validation command to `bottom_signal_strategy_iteration_review.md` and `.csv`:
  - `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"`
  - PASS, 144 tests.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_validation_command_checklist`
  - RED first after adding the new expected command, then PASS after implementation and CSV quoting adjustment.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m py_compile quant_indicators.py investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py investigations\uptrend_dip_search.py investigations\buy_dip_search.py investigations\us_index_zone_research.py tests\test_bottom_signal_search.py tests\test_uptrend_dip_search.py tests\test_quant_indicators.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- `Get-ChildItem investigations -Filter '*dual_track_rs*'`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Notes
- Full `all / 720 / --workers 4` search was not run because no search logic or config changed.
- Repo-wide unit discovery is now part of the review checklist, so future iterations can distinguish focused Bottom Signal checks from broader project unit checks.

--- Session: 2026-05-23 Main Artifact Manifest Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Make the current main Bottom Signal artifact set explicit in the strategy review.
- Keep retired/duplicate outputs out of the main line while preserving iteration history.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_reports_main_artifact_manifest`
- Verified RED first:
  - `bottom_signal_search.py` had no `MAIN_ARTIFACT_PATHS` manifest and report/CSV had no main artifact section.
- Implemented the minimum main artifact manifest.

## Completed
- `bottom_signal_strategy_iteration_review.md` now includes `Main Artifact Manifest`.
- `bottom_signal_strategy_iteration_review.csv` now includes `MainArtifact` rows.
- The manifest tracks the compressed main files:
  - `bottom_signal_search.py`
  - `bottom_signal_config.json`
  - `bottom_signal_results.json`
  - `bottom_signal_report.md`
  - `bottom_signal_observation_report.md`
- Current real workspace status:
  - PASS: all five main artifacts exist.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_main_artifact_manifest`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_plan_validation_gates tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_promotion_preconditions tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_retired_dual_track_artifact_guard tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_validation_command_checklist tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_main_artifact_manifest`
  - PASS, 11 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 102 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only adds an artifact manifest to the review layer.
- The manifest helps keep the compressed main line clear before future strategy work.

--- Session: 2026-05-23 Validation Command Checklist Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Put the minimum validation commands and full-search trigger conditions directly into the strategy review artifacts.
- Keep the change as operator guidance only; no strategy logic or config changes.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_lists_validation_command_checklist`
- Verified RED first:
  - strategy iteration report did not contain a `Validation Command Checklist` section.
- Implemented the minimum command checklist output.

## Completed
- `bottom_signal_strategy_iteration_review.md` now includes `Validation Command Checklist`.
- `bottom_signal_strategy_iteration_review.csv` now includes `ValidationCommand` rows.
- The checklist records:
  - minimum unittest command;
  - minimum py_compile command;
  - JSON validation command;
  - `git diff --check`;
  - forbidden-file diff check for `config.py`, `prepare.py`, `run.py`, and `versions`;
  - full search command, only after search logic/config changes;
  - observation refresh command, only after search logic/config changes.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_validation_command_checklist`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_plan_validation_gates tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_promotion_preconditions tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_retired_dual_track_artifact_guard tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_validation_command_checklist`
  - PASS, 10 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 101 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only documents operator validation commands.
- The checklist now makes it explicit that full search is reserved for search logic/config changes.

--- Session: 2026-05-23 Retired Artifact Guard Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Make the retired dual-track output files part of the repeatable audit.
- Preserve historical dual-track iteration logic/tests while keeping the main artifact set compressed.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_reports_retired_dual_track_artifact_guard`
- Verified RED first:
  - `bottom_signal_search.py` had no `RETIRED_ARTIFACT_PATHS` guard and report/CSV had no retired artifact section.
- Implemented the minimum retired artifact guard.

## Completed
- `bottom_signal_strategy_iteration_review.md` now includes `Retired Artifact Guard`.
- `bottom_signal_strategy_iteration_review.csv` now includes `RetiredArtifact` rows.
- The guard checks these retired files:
  - `bottom_signal_results_dual_track_rs.json`
  - `bottom_signal_report_dual_track_rs.md`
- Current real workspace status:
  - PASS: both retired dual-track output files are absent.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_retired_dual_track_artifact_guard`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_plan_validation_gates tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_promotion_preconditions tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_retired_dual_track_artifact_guard`
  - PASS, 9 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `Get-ChildItem investigations -Filter '*dual_track_rs*'`
  - PASS; empty output.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 100 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only adds a retired-artifact audit guard.
- Historical dual-track logic remains in code/tests as iteration history, but the duplicate dual-track result/report files remain retired.

--- Session: 2026-05-23 Promotion Preconditions Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Make future OBS/RS promotion requirements explicit without promoting OBS/RS now.
- Keep the formal MB baseline frozen.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_lists_promotion_preconditions`
- Verified RED first:
  - report only said to open a separate validation plan and did not list required proof items.
- Implemented the minimum precondition output.

## Completed
- `bottom_signal_strategy_iteration_review.md` now includes `Promotion Preconditions`.
- `bottom_signal_strategy_iteration_review.csv` now includes `PromotionPrecondition` rows.
- Required proof before any OBS/RS promotion:
  - OBS/RS ablation against the frozen MB baseline;
  - recent validation keeping formal signal count controlled;
  - sample-out validation before formal promotion;
  - Pine parity check before operator use.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_promotion_preconditions`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_plan_validation_gates tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_promotion_preconditions`
  - PASS, 8 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 99 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only documents validation prerequisites for a future promotion plan.
- OBS/RS remains observation-only.

--- Session: 2026-05-23 Plan Validation Gate Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Turn the core plan invariants into repeatable report/CSV validation gates.
- Keep the change as review-only and avoid strategy parameter changes.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_reports_plan_validation_gates`
- Verified RED first:
  - strategy iteration report did not contain a `Plan Validation Gates` section.
- Implemented the minimum validation gate output.

## Completed
- `bottom_signal_strategy_iteration_review.md` now includes `Plan Validation Gates`.
- `bottom_signal_strategy_iteration_review.csv` now includes `ValidationGate` rows.
- Gates currently check:
  - baseline name is `seed_previous_rs_higher_low_best`;
  - full-pool artifact has 21 symbols and `sampleKind=FULL_POOL`;
  - entry threshold remains 82;
  - formal signal count stays within the 40-signal cap;
  - OBS duplicate formal count remains 0;
  - QQQ 2022 Q4 observation window remains covered;
  - QQQ 2026 March observation window remains covered.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Current Gate Snapshot
- PASS `baselineName`: `seed_previous_rs_higher_low_best`.
- PASS `fullPool`: symbols=21, sample=FULL_POOL.
- PASS `entryThreshold`: threshold=82.
- PASS `formalSignalCap`: signals=39, limit=40.
- PASS `duplicateFormal`: duplicateFormalCount=0.
- PASS `qqq2022Q4Coverage`: 2022-10-03, 2022-10-11, 2022-12-28.
- PASS `qqq2026MarchCoverage`: 2026-03-27.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_plan_validation_gates`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_reports_plan_validation_gates`
  - PASS, 7 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 98 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only adds validation gates for existing full-pool results.
- These gates make the compressed baseline easier to audit before any future strategy research step.

--- Session: 2026-05-23 RS Watchlist Detail Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Make the RS observation list more reviewable without turning RS into a formal entry rule.
- Keep AVGO/META as monitor, CRM/PLTR/AMZN/TSLA/AAPL/V/JPM as review, and CAT/NVDA/CRWD as skip.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_lists_rs_watchlist_details`
- Verified RED first:
  - Markdown only listed grouped RS ticker symbols and omitted per-ticker score, qualified count, and action reason.
- Implemented the minimum RS detail rendering.

## Completed
- `bottom_signal_strategy_iteration_review.md` now lists each RS ticker under Monitor/Review/Skip with:
  - selection score;
  - qualified candidate count;
  - action reason.
- `bottom_signal_strategy_iteration_review.csv` now includes `reason=` in each `RSWatchlist` row.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Current RS Snapshot
- Monitor: AVGO 92.40, META 92.11; both have repeated qualified candidates with clean risk profile.
- Review: CRM 79.71, PLTR 73.24, AMZN 66.77, TSLA 62.33, AAPL 59.07, V 57.94, JPM 56.34.
- Skip: CAT 50.93, NVDA 49.46, CRWD 38.20; all have no qualified RS candidates.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_rs_watchlist_details`
  - PASS, 6 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 97 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only enriches review artifacts from existing full-pool results.
- RS remains an observation-priority layer only and does not replace the formal MB entry rule.

--- Session: 2026-05-23 Formal-Missed OBS Case Detail Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Make formal-missed OBS cases easier to review without tuning parameters.
- Keep the failure-case collection observation-only.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_records_formal_missed_obs_case_details`
- Verified RED first:
  - report only showed raw decimal `fwd6m` for missed OBS cases and omitted adverse drawdown, bottom score, and RS score.
- Implemented the minimum detail rendering.

## Completed
- `bottom_signal_strategy_iteration_review.md` now records formal-missed OBS cases with:
  - risk flags;
  - bottom score;
  - RS score;
  - 6m forward return as a percentage;
  - 6m adverse drawdown as a percentage.
- `bottom_signal_strategy_iteration_review.csv` now includes the same case evidence in each `MissedCase` row.
- Duplicate formal signals remain excluded from `MissedCase` rows.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - Initial parallel run hit a Windows `__pycache__` access conflict while another Python process was active; sequential rerun passed.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_records_formal_missed_obs_case_details`
  - PASS, 5 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 96 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only enriches review artifacts from existing full-pool results.
- Missed-case details are evidence for future review only; no OBS/RS promotion or threshold change was made.

--- Session: 2026-05-23 Recent Formal Signal Detail Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Make recent formal signal review actionable by listing the mature signals directly in the Markdown report.
- Keep this as reporting-only; do not modify strategy parameters or search logic.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_lists_recent_formal_signal_details`
- Verified RED first:
  - report had only recent aggregate metrics and no `Recent Formal Signal Details` section.
- Implemented the minimum detail rendering.

## Completed
- `bottom_signal_strategy_iteration_review.md` now lists the 7 mature recent formal signals with:
  - symbol/date;
  - channel;
  - bottom score;
  - RS score;
  - risk flags;
  - 6m forward return and adverse drawdown.
- `bottom_signal_strategy_iteration_review.csv` now appends channel and risk to each `RecentValidation` evidence row.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Current Recent Formal Snapshot
- AAPL 2025-04-04, MB, risk `no_repair`, fwd6m 36.60%.
- AVGO 2025-04-04, MB, risk `no_repair`, fwd6m 130.27%.
- CAT 2025-04-04, MB, risk `no_repair`, fwd6m 73.42%.
- META 2025-04-04, MB, risk `no_repair`, fwd6m 42.00%.
- NVDA 2025-04-04, MB, risk `no_repair`, fwd6m 96.76%.
- QQQ 2025-04-04, MB, risk `no_repair`, fwd6m 44.11%.
- TSM 2025-04-04, MB, risk `no_repair`, fwd6m 107.40%.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_lists_recent_formal_signal_details`
  - PASS, 4 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 95 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only enriches review artifacts from existing full-pool results.
- The recent signal details are for manual review; they do not promote OBS/RS or alter the formal MB entry rule.

--- Session: 2026-05-23 OBS Risk Bucket Quality Review ---
## Objective
- Continue the compressed-state strategy iteration plan.
- Make OBS candidate review more useful by adding quality metrics to each risk bucket.
- Keep OBS/RS observation-only and avoid formal strategy promotion.

## TDD
- Added failing test:
  - `test_strategy_iteration_review_summarizes_observation_bucket_quality`
- Verified RED first:
  - report only showed OBS risk bucket counts and did not include avg 6m return, win rate, or adverse drawdown.
- Implemented the minimum bucket-quality summary.

## Completed
- `bottom_signal_strategy_iteration_review.md` now shows each OBS risk bucket with:
  - count;
  - average 6m return;
  - 6m win rate;
  - average 6m adverse drawdown.
- `bottom_signal_strategy_iteration_review.csv` now includes the same bucket-quality evidence in `ObservationRisk` rows.
- Refreshed strategy iteration review artifacts from existing full-pool results with `--refresh-strategy-review`.

## Current OBS Bucket Snapshot
- `risk=low_volume`: count 1, avg 6m 52.15%, win 100.00%, adverse -3.75%.
- `risk=no_repair`: count 45, avg 6m 19.38%, win 72.73%, adverse -10.98%.
- `risk=none`: count 3, avg 6m 14.86%, win 66.67%, adverse -10.51%.
- `risk=trend_damage`: count 3, avg 6m 48.59%, win 66.67%, adverse -21.47%.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality`
  - RED first, then PASS after implementation.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_summarizes_observation_bucket_quality`
  - PASS, 3 tests.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; refreshed review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 94 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration only enriches review artifacts from existing full-pool results.
- The bucket metrics are evidence for future review only; they do not promote OBS/RS to formal entries.

--- Session: 2026-05-23 Conservative Strategy Iteration Review ---
## Objective
- Implement the current compressed-state strategy iteration plan.
- Keep `seed_previous_rs_higher_low_best` frozen as the formal MB baseline.
- Add repeatable review artifacts for recent formal signals, OBS risk buckets, RS watchlist actions, and formal-missed OBS cases.

## TDD
- Added failing tests for:
  - strategy iteration review report freezing the formal strategy and segmenting OBS risks;
  - strategy iteration review CSV exporting the ordered research steps.
- Verified RED first:
  - tests failed because `generate_strategy_iteration_review_report()` and `generate_strategy_iteration_review_csv()` did not exist.
- Implemented the minimum review generators and CLI refresh path.

## Completed
- Added generated review artifacts:
  - `investigations/bottom_signal_strategy_iteration_review.md`
  - `investigations/bottom_signal_strategy_iteration_review.csv`
- Added `--refresh-strategy-review` to `investigations/bottom_signal_search.py`.
- `write_outputs()` now also writes the strategy iteration review artifacts on normal result generation.
- The review keeps OBS/RS observation-only and explicitly requires a separate validation plan before any OBS/RS promotion.
- Updated `docs/document_archive.md` so the new review report is discoverable.

## Current Review Snapshot
- Full-pool artifact: yes, `FULL_POOL`.
- Formal baseline: `seed_previous_rs_higher_low_best`.
- Strong signals: 39.
- Recent mature formal signals: 7, status `Pass`.
- OBS risk buckets:
  - `risk=none`: 3.
  - `risk=no_repair`: 45.
  - `risk=low_volume`: 1.
  - `risk=trend_damage`: 3.
- RS actions:
  - Monitor: AVGO, META.
  - Review: CRM, PLTR, AMZN, TSLA, AAPL, V, JPM.
  - Skip: CAT, NVDA, CRWD.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_report_freezes_formal_and_segments_observation tests.test_bottom_signal_search.BottomSignalSearchTest.test_strategy_iteration_review_csv_exports_ordered_research_steps`
  - RED first with missing imports, then PASS after implementation.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-strategy-review`
  - PASS; wrote strategy iteration review Markdown and CSV.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 93 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
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

## Notes
- Full `all / 720 / --workers 4` search was not run because this iteration did not change search logic or experiment config.
- The new review artifacts are a research-control layer, not a formal strategy promotion.

--- Session: 2026-05-23 Post-Prune Code Audit ---
## Objective
- Re-audit the modified code after the stable prune/refactor.
- Confirm the minimum test path still runs.

## Completed
- Re-read the current progress header and worktree status.
- Audited the Bottom Signal refactor boundary:
  - `investigations/bottom_signal_model.py` owns `BottomSignalConfig` and `SearchSettings`.
  - `investigations/bottom_signal_paths.py` owns generated artifact paths.
  - `investigations/bottom_signal_search.py` still imports and re-exports those names through the existing module import surface.
  - `write_outputs()` no longer writes duplicate dual-track report/JSON files.
- Confirmed no active code/test references remain for:
  - `ITERATION_RESULTS_PATH`
  - `ITERATION_REPORT_PATH`
  - `bottom_signal_results_dual_track_rs`
  - `bottom_signal_report_dual_track_rs`

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_quant_indicators tests.test_uptrend_dip_search tests.test_bottom_signal_search`
  - PASS, 133 tests.
- `.venv\Scripts\python.exe -m py_compile quant_indicators.py investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py investigations\uptrend_dip_search.py investigations\buy_dip_search.py investigations\us_index_zone_research.py tests\test_bottom_signal_search.py tests\test_uptrend_dip_search.py tests\test_quant_indicators.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --help > $null`
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

## Notes
- No blocking issues found in the audited Bottom Signal prune/refactor code.
- The worktree still contains pre-existing modified/untracked research files; they were not reverted.

--- Session: 2026-05-23 Stable Prune And Duplicate Artifact Removal ---
## Objective
- Execute the AutoQuantStock stable pruning plan.
- Preserve current Bottom Signal results and the iteration process.
- Remove files that are temporary, duplicated, or no longer part of the active workflow.

## Completed
- Removed temporary root outputs:
  - `run_all.log`
  - `run_dev.log`
  - `run_vai.log`
  - `run_vcross.log`
  - `run.log`
  - `results.tsv`
- Removed early exploratory artifacts:
  - `analysis.ipynb`
  - `sharpe-frontier.png`
- Removed duplicate Bottom Signal artifacts after hash-checking they matched the main files exactly:
  - `investigations/bottom_signal_results_dual_track_rs.json`
  - `investigations/bottom_signal_report_dual_track_rs.md`
- Updated `investigations/bottom_signal_search.py` so future runs write only the main `bottom_signal_results.json` and `bottom_signal_report.md`, not the removed duplicates.
- Split the Bottom Signal config dataclasses into `investigations/bottom_signal_model.py` while keeping the existing `investigations.bottom_signal_search` import surface compatible.
- Split Bottom Signal filesystem paths into `investigations/bottom_signal_paths.py` so generated artifact destinations are centralized.
- Updated `docs/document_archive.md` to explain that the dual-track artifacts were folded into the main Bottom Signal report/JSON.
- Updated `README.md` so `results.tsv` is described as an old generated file, not an always-present repo file.
- Removed the redundant root `venv/` and Python cache directories. Kept `.venv/` because current verification commands use it.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_quant_indicators tests.test_uptrend_dip_search tests.test_bottom_signal_search`
  - PASS, 133 tests.
- `.venv\Scripts\python.exe -m py_compile quant_indicators.py investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py investigations\uptrend_dip_search.py investigations\buy_dip_search.py investigations\us_index_zone_research.py tests\test_bottom_signal_search.py tests\test_uptrend_dip_search.py tests\test_quant_indicators.py`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 91 tests after extracting `bottom_signal_model.py`.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Notes
- This was a stable prune, not an aggressive compression. Historical research branches such as Uptrend Dip, Buy Dip, and US Index Zone were kept as iteration evidence.
- `config.json` remains deleted because the current README identifies it as old crypto/Freqtrade configuration, not part of the active Backtesting.py + yfinance workflow.

--- Session: 2026-05-20 Merged Pine Path Paste Check ---
## Objective
- Check the reported Pine issue around `indicator("AutoQuant Bottom + RS + Observation", ...)` in `investigations/bottom_signal_merged_observation.pine`.

## Completed
- Confirmed `investigations/bottom_signal_merged_observation.pine` starts with:
  - `//@version=5`
  - `indicator("AutoQuant Bottom + RS + Observation", overlay=true, max_labels_count=500)`
- Confirmed the file does not contain the local Windows path `E:\code\AutoQuantStock\...`.
- Confirmed the file does not contain another `indicator()` / `strategy()` declaration.
- Working conclusion: if TradingView shows the path next to the `indicator(...)` line, the local path was copied into Pine Editor accidentally. Pine Editor should receive only the Pine file contents, not the Windows file path.

## Verification Commands Run
- `Get-Content investigations\bottom_signal_merged_observation.pine -TotalCount 80`
  - PASS.
- `Select-String -Path investigations\bottom_signal_merged_observation.pine -Pattern 'E:\\'`
  - PASS; empty output.
- `Select-String -Path investigations\bottom_signal_merged_observation.pine -Pattern ':\\'`
  - PASS; empty output.
- `Format-Hex -Path investigations\bottom_signal_merged_observation.pine -Count 80`
  - PASS; no BOM or hidden path before `indicator`.

## Not Modified
- `investigations/bottom_signal_search.py`
- `investigations/bottom_signal_merged_observation.pine`
- `tests/test_bottom_signal_search.py`
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

--- Session: 2026-05-20 Observation Sensitivity Sweep ---
## Objective
- Continue `docs/plans/qqq_observation_full_parallel_validation_plan.md`.
- Complete the optional observation sensitivity follow-up.
- Explore `nearLowMax`, `deepBottomMin`, `shallowBottomMin`, and `clusterWindow` around the selected observation config.
- Keep OBS-D / OBS-S observation-only and do not promote them to formal MB/RS Strong logic.

## Completed
- Ran required validation gate first:
  - unit tests;
  - syntax check;
  - stale worker check;
  - small `QQQ,SPY / 12` serial-vs-parallel comparison.
- Because small comparison writes sample artifacts, reran full-pool search and observation refresh afterward.
- Ran a read-only sensitivity sweep using the same observation search logic, without writing official artifacts.
- Base selected observation config:
  - `deepBottomMin=66`
  - `shallowBottomMin=68`
  - `bottomMax=75`
  - `nearLowWindow=63`
  - `nearLowMax=0.06`
  - `clusterWindow=42`
- Sensitivity findings:
  - `nearLowMax`: 0.04 to 0.08 all preserved both QQQ anchor windows. Current 0.06 kept 48 signals, score 80.52, duplicate formal 0. Looser 0.07/0.08 introduced 1 duplicate formal signal.
  - `deepBottomMin`: 64/65/66 gave identical 48 signals and score 80.52. 67/68 still covered anchors but score slipped to 79.48.
  - `shallowBottomMin`: 66 and 67 increased signal count to 50/49 and marginally higher total selection score, but current 68 stayed sparse at 48 with no duplicate formal signals.
  - `clusterWindow`: 21 increased signals to 74, close to sparse target max 78; 35 gave 55; current 42 gave 48; 56/63 reduced to 38/36. All preserved both QQQ anchor windows.
- Recommendation:
  - keep the current observation config as candidate-only default;
  - do not promote OBS-D / OBS-S;
  - treat `clusterWindow=21` as an aggressive watchlist-only scenario, not a default.

## Current Result Snapshot
- Full search best config remains `seed_previous_rs_higher_low_best`.
- Formal Strong signals remain 39.
- Full search avg 6m return remains 39.24%.
- Observation signals remain 48.
- Formal Strong baseline remains 39.
- Observation/Formal ratio remains 1.23x.
- Duplicate formal signals remain 0.
- QQQ 2022-10-01 to 2022-12-31 remains covered by 2022-10-03, 2022-10-11, 2022-12-28.
- QQQ 2026-03-01 to 2026-03-31 remains covered by 2026-03-27.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 91 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'bottom_signal_search|multiprocessing|spawn' } | Select-Object ProcessId,CommandLine`
  - PASS after tests completed; empty output.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 1`
  - PASS; expected small serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 2`
  - PASS; matched serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; best `seed_previous_rs_higher_low_best`, score 27.95, signals 39, avg6m 39.24%.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals 48, upgradeScore 80.52.
- Observation sensitivity inline Python sweep
  - PASS; all tested nearby variants preserved both QQQ anchor windows.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Unfinished / Notes
- No remaining items in `docs/plans/qqq_observation_full_parallel_validation_plan.md`.
- Keep OBS-D / OBS-S as candidate-only observation labels unless a separate validation plan promotes them.

--- Session: 2026-05-20 Worker Scaling Benchmark ---
## Objective
- Continue `docs/plans/qqq_observation_full_parallel_validation_plan.md`.
- Complete the optional worker scaling benchmark.
- Compare `--workers 1`, `2`, `4`, and `6` on the same `QQQ,SPY / max-configs 72` sample.

## Completed
- Confirmed no stale `bottom_signal_search` / multiprocessing Python workers before benchmark.
- Ran the benchmark with:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 72 --workers 1`
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 72 --workers 2`
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 72 --workers 4`
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 72 --workers 6`
- Benchmark results:
  - workers 1: 28.01s
  - workers 2: 17.51s
  - workers 4: 13.37s
  - workers 6: 13.97s
- All benchmark runs selected the same sample best config:
  - `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`
  - `signals=2`, `avg6m=-4.32%`
- Recommendation:
  - keep `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4` as the default full-search operator command;
  - workers 6 did not beat workers 4 on this small benchmark.
- Because the benchmark commands write sample artifacts, reran full-pool search and observation refresh afterward.

## Current Result Snapshot
- Full search best config remains `seed_previous_rs_higher_low_best`.
- Formal Strong signals remain 39.
- Full search avg 6m return remains 39.24%.
- Observation signals remain 48.
- Formal Strong baseline remains 39.
- Observation/Formal ratio remains 1.23x.
- Duplicate formal signals remain 0.
- QQQ 2022-10-01 to 2022-12-31 remains covered by 2022-10-03, 2022-10-11, 2022-12-28.
- QQQ 2026-03-01 to 2026-03-31 remains covered by 2026-03-27.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 91 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'bottom_signal_search|multiprocessing|spawn' } | Select-Object ProcessId,CommandLine`
  - PASS after tests completed; empty output.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; elapsed about 9 minutes 54 seconds; best `seed_previous_rs_higher_low_best`, score 27.95, signals 39, avg6m 39.24%.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals 48, upgradeScore 80.52.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- JSON / CSV / report / Pine audit commands
  - PASS; final artifacts are full-pool, not QQQ/SPY sample output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Unfinished / Notes
- Remaining optional follow-up from the plan: observation sensitivity.
- Keep OBS-D / OBS-S as candidate-only observation labels unless a separate validation plan promotes them.

--- Session: 2026-05-20 Pine Observation BottomMax Parity Guard ---
## Objective
- Continue `docs/plans/qqq_observation_full_parallel_validation_plan.md`.
- Complete the optional Pine parity guard follow-up with TDD.
- Make the Python observation search config and merged Pine OBS score ceiling use the same explicit `bottomMax` value.

## TDD
- Added failing test:
  - `test_merged_observation_pine_script_uses_selected_obs_bottom_max`
  - Expected merged Pine to use custom selected observation config values including `bottomMax=73`, while keeping formal `watchThreshold=91` separate.
- Verified RED first:
  - test failed because Pine still generated `obsBottomMax = input.int(75, ...)`.
- Implemented the minimum parity change:
  - added `bottomMax: 75` to observation candidate configs;
  - changed Python observation deep/shallow masks from implicit `bottom < 76` to explicit `bottom <= bottomMax`;
  - changed merged Pine generation to read `observation_config["bottomMax"]`;
  - added `Bottom maximum` to the observation report.

## Completed
- Target Pine parity tests pass:
  - selected `bottomMax` flows into Pine as `obsBottomMax`;
  - `obsBottomMax` remains independent from formal `watchThreshold`;
  - OBS-D / OBS-S still exclude formal Strong overlap via `not mbStrongSignal` / `not rsStrongSignal`.
- Small `QQQ,SPY / 12` serial and parallel runs still match:
  - best config `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`;
  - `signals=2`, `avg6m=-4.32%`.
- Full pool rerun restored accepted artifacts:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; elapsed about 12 minutes 9 seconds.
- Observation refresh passed:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; `signals=48`, `upgradeScore=80.52`.
- Full artifact audit:
  - `bottom_signal_results.json` parses as JSON.
  - `artifactScope`: `symbolCount=21`, `requiredFullSymbolCount=21`, `fullPool=true`, `sampleKind=FULL_POOL`.
  - best config remains `seed_previous_rs_higher_low_best`.
  - Formal Strong signals remain 39; avg 6m return remains 39.24%.
  - selected observation config includes `bottomMax=75`.
  - QQQ 2022-10-01 to 2022-12-31 remains covered by 2022-10-03, 2022-10-11, 2022-12-28.
  - QQQ 2026-03-01 to 2026-03-31 remains covered by 2026-03-27.
  - observation CSV has 48 rows and includes all four QQQ anchor dates.
  - observation report shows `Bottom maximum: 75`.
  - merged Pine includes `obsBottomMax = input.int(75, "OBS Bottom Max", ...)` and uses `bottomScore <= obsBottomMax`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_merged_observation_pine_script_uses_selected_obs_bottom_max`
  - RED first with hard-coded `obsBottomMax=75`, then PASS after implementation.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_merged_observation_pine_script_uses_selected_obs_bottom_max tests.test_bottom_signal_search.BottomSignalSearchTest.test_merged_observation_pine_script_uses_independent_obs_bottom_max`
  - PASS.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 91 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'bottom_signal_search|multiprocessing|spawn' } | Select-Object ProcessId,CommandLine`
  - PASS after tests completed; empty output.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 1`
  - PASS; expected small serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 2`
  - PASS; matched serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; best `seed_previous_rs_higher_low_best`, score 27.95, signals 39, avg6m 39.24%.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals 48, upgradeScore 80.52.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- JSON / CSV / report / Pine audit commands
  - PASS.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Unfinished / Notes
- Remaining optional follow-ups from the plan: worker scaling benchmark and observation sensitivity.
- Keep OBS-D / OBS-S as candidate-only observation labels unless a separate validation plan promotes them.

--- Session: 2026-05-20 Artifact Scope Guard ---
## Objective
- Continue `docs/plans/qqq_observation_full_parallel_validation_plan.md`.
- Complete the optional artifact guard follow-up with TDD.
- Warn when `bottom_signal_results.json` comes from a quick `QQQ,SPY` sample instead of the full `all / 720` pool.

## TDD
- Added failing test:
  - `test_run_search_marks_qqq_spy_sample_artifacts`
  - Expected `run_search(["QQQ", "SPY"])` to emit `artifactScope.fullPool=false`, `sampleKind=QQQ_SPY_SAMPLE`, and a quick-sample warning.
- Verified RED first:
  - test failed with `KeyError: 'artifactScope'`.
- Implemented the minimum guard:
  - added `artifact_scope_summary(symbols)`;
  - added `artifactScope` to `run_search()` payload;
  - added an `Artifact scope` line to `bottom_signal_report.md`.

## Completed
- Small `QQQ,SPY / 12` serial and parallel runs still match:
  - best config `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`;
  - `signals=2`, `avg6m=-4.32%`.
- Full pool rerun restored accepted artifacts:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; elapsed about 21 minutes 27 seconds.
- Observation refresh passed:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; `signals=48`, `upgradeScore=80.52`.
- Full artifact audit:
  - `bottom_signal_results.json` parses as JSON.
  - `artifactScope`: `symbolCount=21`, `requiredFullSymbolCount=21`, `fullPool=true`, `sampleKind=FULL_POOL`.
  - best config remains `seed_previous_rs_higher_low_best`.
  - Formal Strong signals remain 39; avg 6m return remains 39.24%.
  - QQQ 2022-10-01 to 2022-12-31 remains covered by 2022-10-03, 2022-10-11, 2022-12-28.
  - QQQ 2026-03-01 to 2026-03-31 remains covered by 2026-03-27.
  - observation CSV has 48 rows and includes all four QQQ anchor dates.
  - merged Pine includes OBS-D, OBS-S, RS-Q, RS-R, `obsBottomMax`, alertconditions, and excludes formal Strong overlap via `not mbStrongSignal` / `not rsStrongSignal`.
  - `bottom_signal_report.md` shows `Artifact scope: full-pool output`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_run_search_marks_qqq_spy_sample_artifacts`
  - RED first with missing `artifactScope`, then PASS after implementation.
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 90 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 1`
  - PASS; expected small serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 2`
  - PASS; matched serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; best `seed_previous_rs_higher_low_best`, score 27.95, signals 39, avg6m 39.24%.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals 48, upgradeScore 80.52.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- JSON / CSV / report / Pine audit commands
  - PASS.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Unfinished / Notes
- Remaining optional follow-ups from the plan: worker scaling benchmark, observation sensitivity, Pine parity guard.
- Keep OBS-D / OBS-S as candidate-only observation labels unless a separate validation plan promotes them.

--- Session: 2026-05-20 Full Parallel Revalidation Round ---
## Objective
- Continue `docs/plans/qqq_observation_full_parallel_validation_plan.md`.
- Re-run the required TDD-style validation gate: unit tests, syntax check, small serial-vs-parallel comparison, full parallel search, observation refresh, and artifact audit.
- Keep OBS-D / OBS-S observation-only and avoid changing formal MB Strong / RS Strong strategy logic.

## Completed
- Confirmed no stale `bottom_signal_search` / multiprocessing Python workers before starting.
- Confirmed current branch is `autoresearch/may17-baseline-next`.
- Ran the small `QQQ,SPY / 12` serial and parallel searches:
  - both selected `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`;
  - both produced `signals=2`, `avg6m=-4.32%`.
- Because the small runs overwrite generated artifacts with sample output, reran the full pool:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; elapsed about 20 minutes 33 seconds.
- Refreshed observation artifacts from the full results:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; `signals=48`, `upgradeScore=80.52`.
- Audited generated artifacts:
  - `bottom_signal_results.json` parses as JSON and contains 21 symbols.
  - best config remains `seed_previous_rs_higher_low_best`.
  - Formal Strong signals remain 39; avg 6m return remains 39.24%.
  - observation metrics remain 48 signals, Formal Strong baseline 39, Observation/Formal ratio 1.23x, duplicate formal signals 0.
  - QQQ 2022-10-01 to 2022-12-31 remains covered by 2022-10-03, 2022-10-11, 2022-12-28.
  - QQQ 2026-03-01 to 2026-03-31 remains covered by 2026-03-27.
  - observation CSV has 48 rows and includes all four QQQ anchor dates.
  - merged Pine includes OBS-D, OBS-S, RS-Q, RS-R, `obsBottomMax`, and alertconditions.
  - merged Pine keeps OBS candidates separate from formal strong logic by excluding `mbStrongSignal` and `rsStrongSignal`.

## Validation Commands Run
- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 89 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
  - PASS.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 1`
  - PASS; expected small serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 2`
  - PASS; matched serial baseline.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; best `seed_previous_rs_higher_low_best`, score 27.95, signals 39, avg6m 39.24%.
- `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals 48, upgradeScore 80.52.
- `.venv\Scripts\python.exe -m json.tool investigations\bottom_signal_results.json > $null`
  - PASS.
- JSON / CSV / report / Pine audit commands
  - PASS after correcting the audit script to use the actual CSV column `observationType`.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

## Unfinished / Notes
- Optional follow-ups from the plan remain optional: worker scaling benchmark, observation sensitivity, Pine parity guard, and artifact guard.
- Keep OBS-D / OBS-S as candidate-only observation labels unless a separate validation plan promotes them.

--- Session: 2026-05-20 Goal Handoff Wording Review ---
## Objective
- Review the proposed `/goal` wording for the next agent.
- Make sure the next agent can continue from persisted local files instead of relying only on conversation memory.

## Recommendation
- Keep the same high-level objective, but include the absolute plan path and explicit execution boundaries:
  - read `claude-progress.md` first;
  - read `docs/plans/qqq_observation_full_parallel_validation_plan.md`;
  - execute the next unchecked / unresolved validation step;
  - use full `--symbol all --max-configs 720 --workers 4` only when a full validation run is needed;
  - keep `OBS-D` / `OBS-S` observation-only and do not modify formal MB/RS Strong logic without a separate plan.

--- Session: 2026-05-20 QQQ Full Parallel Validation Plan File ---
## Objective
- Persist the latest QQQ missed-bottom + merged Pine observation plan locally.
- Make the plan discoverable for the next agent.

## Completed
- Created `docs/plans/qqq_observation_full_parallel_validation_plan.md`.
- The plan covers:
  - full `all / 720 / --workers 4` validation;
  - observation refresh from full results;
  - QQQ 2022 Q4 and 2026 March anchor checks;
  - merged Pine parity checks;
  - optional worker benchmark, sensitivity, Pine parity, and artifact-guard follow-ups.

## Verification Commands Run
- `Get-Content docs\plans\qqq_observation_full_parallel_validation_plan.md -TotalCount 20`
  - PASS after creation.
- `git diff --check`
  - PASS.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

--- Session: 2026-05-20 Full Search Workers Acceleration ---
## Objective
- Continue implementation of full-search acceleration with tests first.
- Add optional multiprocessing for config evaluation while keeping default serial behavior.
- Complete full `all` / `720` validation and then refresh QQQ observation artifacts from the full result.

## TDD
- Added failing tests for:
  - `--workers` defaulting to 1.
  - CLI parsing `--workers 4`.
  - serial and parallel config evaluation producing the same config/score set.
  - `run_search()` passing `workers` through both staged and final evaluation.
- Verified the tests failed before implementation.
- Implemented the minimum worker plumbing and verified tests pass.

## Completed
- Updated `investigations/bottom_signal_search.py`:
  - Added `ProcessPoolExecutor` config-evaluation path.
  - Added `--workers` CLI argument.
  - Added `run_search(..., workers=1)` and evaluation-runner injection for tests.
  - Kept data precompute/cache and output writing in the main process.
- Updated `tests/test_bottom_signal_search.py`:
  - Added fake precomputer/evaluator/executor tests for workers.
- Cleaned stale interrupted multiprocessing processes before rerunning validation.
- Ran full parallel search:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS; elapsed about 11 minutes.
- Refreshed observation search from the full result:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS.

## Current Result Snapshot
- Full search best config: `seed_previous_rs_higher_low_best`.
- Formal Strong signals: 39.
- Full search avg 6m return: 39.24%.
- Observation signals: 48.
- Formal Strong baseline: 39.
- Observation/Formal ratio: 1.23x.
- Duplicate formal signals: 0.
- QQQ 2022-10-01 to 2022-12-31: covered.
- QQQ 2026-03-01 to 2026-03-31: covered.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 89 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 1`
  - PASS; best config and metrics matched the parallel small run.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 2`
  - PASS; best config and metrics matched the serial small run.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals=48, upgradeScore=80.52.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- `git diff --check`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.
- Residual process check for `bottom_signal_search|multiprocessing|spawn`
  - PASS; empty output after completion.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

--- Session: 2026-05-20 Observation Sparsity Ratio Report ---
## Objective
- Continue the QQQ missed-bottom observation plan.
- Make the strict-sparsity target understandable in the report and JSON.
- Show how many formal Strong signals the observation layer is being compared against.

## TDD
- Added failing tests requiring:
  - `formalStrongBaselineCount` in observation metrics.
  - `observationToFormalRatio` in observation metrics.
  - report lines for `Formal Strong baseline` and `Observation/Formal ratio`.
- Verified the tests failed before implementation.
- Added the minimum metrics/report fields to pass them.

## Completed
- Updated `investigations/bottom_signal_search.py`:
  - `_observation_metrics()` now emits formal Strong baseline count.
  - `_observation_metrics()` now emits observation/formal ratio.
  - `generate_observation_report()` now prints both fields.
- Regenerated observation artifacts:
  - `investigations/bottom_signal_observation_report.md`
  - `investigations/bottom_signal_observation_signals.csv`
  - `investigations/bottom_signal_merged_observation.pine`
  - `investigations/bottom_signal_results.json`

## Current Result Snapshot
- Observation signals: 48.
- Formal Strong baseline: 39.
- Observation/Formal ratio: 1.23x.
- Sparse target max: 78.
- Duplicate formal signals: 0.
- Upgrade candidate score: 80.52.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_observation_search_covers_qqq_anchor_windows_and_keeps_sparse`
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_observation_csv_and_report_export_anchor_evidence`
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 85 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals=48, upgradeScore=80.52.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
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

--- Session: 2026-05-20 Observation Pine Bottom-Max Decoupling ---
## Objective
- Continue the QQQ missed-bottom observation plan.
- Make the merged Pine OBS score ceiling match the Python search rule.
- Avoid coupling OBS visibility to the user-editable formal `Watch Score`.

## TDD
- Added a failing Pine-generation test requiring:
  - `obsBottomMax = input.int(75, "OBS Bottom Max", ...)`
  - OBS-D/OBS-S candidate logic using `bottomScore <= obsBottomMax`
  - no OBS candidate dependency on `bottomScore < watchThreshold`.
- Verified the test failed before implementation.
- Added the minimum generator change to pass it.

## Completed
- Updated `investigations/bottom_signal_search.py`:
  - merged Pine now has independent `OBS Bottom Max` input.
  - OBS-D/OBS-S candidates now cap bottom score with `bottomScore <= obsBottomMax`.
- Regenerated observation artifacts:
  - `investigations/bottom_signal_observation_report.md`
  - `investigations/bottom_signal_observation_signals.csv`
  - `investigations/bottom_signal_merged_observation.pine`
  - `investigations/bottom_signal_results.json`

## Current Result Snapshot
- Observation signals remain 48.
- Duplicate formal signals remain 0.
- Upgrade candidate score remains 80.52.
- The generated Pine now includes:
  - `obsBottomMax = input.int(75, "OBS Bottom Max", minval=1, maxval=100)`.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_merged_observation_pine_script_uses_independent_obs_bottom_max`
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 85 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals=48, upgradeScore=80.52.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
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

--- Session: 2026-05-20 Observation Anchor Risk Detail Report ---
## Objective
- Continue the QQQ missed-bottom observation plan.
- Make the observation report show exact QQQ anchor-window signals and risk flags, not only covered/missing counts.
- Keep formal MB/RS strategy logic unchanged.

## TDD
- Added a failing report test requiring:
  - `## Anchor Signal Details`
  - QQQ anchor signal row with date, OBS type, bottom score, RS score, and risk flags.
- Verified the test failed before implementation.
- Added the minimum report-generation section to pass it.

## Completed
- Updated `investigations/bottom_signal_search.py`:
  - `generate_observation_report()` now emits `Anchor Signal Details`.
  - Each QQQ anchor-window signal is listed with `risk=...`.
- Regenerated observation artifacts:
  - `investigations/bottom_signal_observation_report.md`
  - `investigations/bottom_signal_observation_signals.csv`
  - `investigations/bottom_signal_merged_observation.pine`
  - `investigations/bottom_signal_results.json`

## Current Anchor Detail Snapshot
- QQQ 2022-10-03 OBS-D bottom=68 RS=38 risk=none.
- QQQ 2022-10-11 OBS-D bottom=69 RS=40 risk=no_repair.
- QQQ 2022-12-28 OBS-D bottom=68 RS=42 risk=no_repair.
- QQQ 2026-03-27 OBS-S bottom=71 RS=40 risk=no_repair.
- Observation signals remain 48.
- Upgrade candidate score remains 80.52.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_observation_csv_and_report_export_anchor_evidence`
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 84 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals=48, upgradeScore=80.52.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
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

--- Session: 2026-05-20 Observation Formal-Overlap Penalty ---
## Objective
- Continue the QQQ missed-bottom observation plan.
- Make the observation search actually penalize configs that produce candidates overlapping existing MB/RS Strong dates.
- Keep the formal MB/RS strategy logic unchanged.

## TDD
- Added a failing unit test showing that two otherwise identical observation configs selected the one with a formal-overlap candidate.
- Verified the test failed before implementation.
- Added a duplicate-formal penalty to the observation config score.
- Verified the targeted test passed after implementation.

## Completed
- Updated `investigations/bottom_signal_search.py`:
  - `search_observation_channel()` now subtracts `20 * duplicateFormalCount` from candidate score.
- Regenerated observation artifacts after the scoring change:
  - `investigations/bottom_signal_observation_report.md`
  - `investigations/bottom_signal_observation_signals.csv`
  - `investigations/bottom_signal_merged_observation.pine`
  - `investigations/bottom_signal_results.json`

## Current Result Snapshot
- Observation signals: 48.
- Sparse target max: 78.
- Duplicate formal signals: 0.
- Upgrade candidate score: 80.52.
- Selected config:
  - deep bottom minimum: 66.
  - shallow bottom minimum: 68.
  - near-low window: 63.
  - near-low max gap: 6.00%.
- QQQ 2022-10-01 to 2022-12-31: Covered.
  - Dates: 2022-10-03, 2022-10-11, 2022-12-28.
- QQQ 2026-03-01 to 2026-03-31: Covered.
  - Date: 2026-03-27.

## Validation Commands Run
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_observation_search_penalizes_formal_overlap_candidates`
  - PASS after expected RED failure.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 84 tests.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; signals=48, upgradeScore=80.52.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
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

--- Session: 2026-05-19 Observation Search And Merged Pine ---
## Objective
- Implement the QQQ missed-bottom observation search plan.
- Cover QQQ 2022-10-01 to 2022-12-31 and QQQ 2026-03-01 to 2026-03-31 with a new observation/candidate layer.
- Keep the formal MB strategy unchanged.

## Completed
- Added observation-channel search to `investigations/bottom_signal_search.py`.
- Added CLI:
  - `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
- Added generated artifacts:
  - `investigations/bottom_signal_observation_report.md`
  - `investigations/bottom_signal_observation_signals.csv`
  - `investigations/bottom_signal_merged_observation.pine`
- Added unit coverage for:
  - merged Pine OBS-D/OBS-S layers and alerts;
  - QQQ anchor-window coverage;
  - sparse observation signal constraint;
  - observation CSV/report exports.

## Current Result Snapshot
- Observation signals: 50.
- Sparse target max: 78.
- Upgrade candidate score: 81.59.
- QQQ 2022-10-01 to 2022-12-31: Covered.
  - QQQ OBS-D examples: 2022-10-03, 2022-10-11, 2022-12-28.
- QQQ 2026-03-01 to 2026-03-31: Covered.
  - QQQ OBS-S example: 2026-03-27.
- Selected observation config:
  - deep market max: -20.00%;
  - shallow market band: -20.00% to -8.00%;
  - deep bottom min: 68;
  - shallow bottom min: 70;
  - near-low window: 42;
  - near-low max gap: 8.00%;
  - cluster window: 42 bars.

## Verification
- TDD RED check:
  - Target tests first failed because observation search and merged Pine functions did not exist.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_merged_observation_pine_script_adds_obs_layers_and_alerts tests.test_bottom_signal_search.BottomSignalSearchTest.test_observation_search_covers_qqq_anchor_windows_and_keeps_sparse tests.test_bottom_signal_search.BottomSignalSearchTest.test_observation_csv_and_report_export_anchor_evidence`
  - PASS after implementation.
- `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`
  - PASS, 82 tests.
- `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --refresh-observation-search`
  - PASS; generated 50 observation signals and wrote observation report, CSV, merged Pine, and refreshed JSON.
- `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`
  - PASS.
- `.venv\\Scripts\\python.exe -m json.tool investigations\\bottom_signal_results.json`
  - PASS.
- Anchor artifact checks:
  - observation report includes both QQQ anchor windows as Covered;
  - observation CSV includes QQQ 2022 and 2026 observation rows;
  - merged Pine includes OBS-D, OBS-S, table rows, and alertconditions.
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

--- Session: 2026-05-19 Document Archive Index ---
## Objective
- 整理当前文件夹里的所有文档。
- 如果没有统一归档入口，就新建一个归档文件放进去。

## Assumption
- 不移动现有文档，避免破坏报告、脚本或说明里的相对路径。
- 新建一个文档索引，用来说明每份文档的用途和阅读顺序。

## Completed
- 新增 `docs/document_archive.md`。
- 归档内容覆盖：
  - 根目录文档；
  - `docs/` 文档；
  - `investigations/` Markdown 研究报告；
  - `versions/` 回顾文档；
  - CSV/JSON/Pine/log/TSV/PNG 等非 Markdown 研究产物的阅读入口。
- 标出当前主线：
  - `investigations/bottom_signal_strategy_overview.md`
  - `investigations/bottom_signal_report.md`
  - `investigations/bottom_signal_plan_summary.md`
  - `investigations/bottom_signal_next_actions.csv`

## Verification
- `rg --files -g "*.md" -g "*.txt" -g "*.rst"`
  - PASS; 用于盘点当前文档。
- 文档覆盖检查
  - PASS; 当前发现的 Markdown 文档都已登记到 `docs/document_archive.md`。
- `git diff --check -- docs\\document_archive.md claude-progress.md investigations\\bottom_signal_strategy_overview.md`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---

--- Session: 2026-05-19 Strategy Exploration Overview ---
## Objective
- 整理策略探索流程以及当前策略的具体内容。
- 用非全职开发者也能看懂的方式说明 MB 正式策略、RS 观察名单、近期验证和下一步规则。

## Completed
- 新增 `investigations/bottom_signal_strategy_overview.md`。
- 文档内容包括：
  - 策略探索流程；
  - 当前正式策略参数；
  - MB 因子含义与消融结论；
  - RS 选股增强分层；
  - 近期验证结果；
  - 当前行动规则；
  - 主要产物路径。

## Verification
- `Get-Content investigations\\bottom_signal_strategy_overview.md | Select-Object -First 80`
  - PASS; 文档可读取，核心章节已写入。
- `git diff --check -- investigations\\bottom_signal_strategy_overview.md`
  - PASS.
- `git diff --name-only -- config.py prepare.py run.py versions`
  - PASS; empty output.

## Not Modified
- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

---
