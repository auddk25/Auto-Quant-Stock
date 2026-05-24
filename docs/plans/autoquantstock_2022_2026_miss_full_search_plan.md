# AutoQuantStock 2022/2026 缺失正式信号的全量探索计划 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不破坏当前压缩基线的前提下，解释 QQQ 在 2022 Q4 和 2026 March 为什么没有触发正式 MB Strong 信号，并用隔离输出做更全量搜索。

**Architecture:** 当前正式策略 `seed_previous_rs_higher_low_best` 继续作为主基线，不直接降低正式门槛，也不把 OBS/RS 升级成正式买点。新增研究输出应使用独立 tag 或独立文件名，避免覆盖 `strategy_catalog/bottom_signal_formal/bottom_signal_results.json` 等主线产物。

**Tech Stack:** Python, unittest, JSON/CSV/Markdown research artifacts, existing `investigations/bottom_signal_search.py` workflow.

---

## Current Baseline

- Formal strategy: `seed_previous_rs_higher_low_best`.
- Formal Strong signals: 39.
- 6m average return: 39.24%.
- 6m win rate: 74.36%.
- Full pool: 21 symbols, `artifactScope.sampleKind=FULL_POOL`.
- OBS candidates: 48 signals, 6m average return 19.10%, win rate 72.34%.
- OBS/Formal ratio: 1.23x.
- OBS duplicate formal count: 0.
- QQQ 2022 Q4 is observation-covered by 2022-10-03, 2022-10-11, and 2022-12-28.
- QQQ 2026 March is observation-covered by 2026-03-27.
- Existing observation details show those QQQ OBS signals have `bottomScore` around 68-71, below formal `entry_threshold=82`; several have `riskFlags=no_repair`.

## File Structure

- Modify: `investigations/bottom_signal_paths.py`
  - Add named paths for isolated 2022/2026 research artifacts.
- Modify: `investigations/bottom_signal_search.py`
  - Add research-tag output routing.
  - Add missing-formal-signal diagnostics for QQQ 2022 Q4 and 2026 March.
  - Add report/CSV generation for near misses and full-search candidate review.
- Modify: `tests/test_bottom_signal_search.py`
  - Add regression tests for isolated outputs and miss diagnostics.
- Create: `strategy_catalog/bottom_signal_2022_2026_research/bottom_signal_2022_2026_miss_diagnostics.md`
  - Human-readable explanation of why formal MB Strong did not trigger.
- Create: `strategy_catalog/bottom_signal_2022_2026_research/bottom_signal_2022_2026_miss_diagnostics.csv`
  - Machine-readable rows for dates, scores, thresholds, risks, and failed gates.
- Create only when running isolated search: `strategy_catalog/bottom_signal_2022_2026_research/bottom_signal_results_2022_2026_miss_search.json`
  - Full research result that must not replace the compressed main baseline.

## Task 1: Add Research-Tag Output Isolation

- [x] **Step 1: Write failing tests**

Add tests in `tests/test_bottom_signal_search.py` that prove:

- default output still uses `bottom_signal_results.json`;
- `--research-tag 2022_2026_miss_search` routes results to a tagged JSON path;
- tagged output does not overwrite the main result path.

Expected command:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_research_tag_routes_outputs_without_overwriting_main_results
```

Expected first result: FAIL because the CLI/output routing does not exist yet.

- [x] **Step 2: Implement minimal routing**

Add a `--research-tag` CLI argument to `investigations/bottom_signal_search.py`.

Rules:

- Empty tag keeps current behavior.
- Non-empty tag may contain only letters, numbers, underscore, and dash.
- Tagged full-search output writes tagged research files.
- Refresh-only commands still use the main result file unless explicitly extended later.

- [x] **Step 3: Run targeted test**

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_research_tag_routes_outputs_without_overwriting_main_results
```

Expected result: PASS.

## Task 2: Add 2022/2026 Missing-Formal Diagnostics

- [x] **Step 1: Write failing diagnostic tests**

Add tests that use the current result payload shape:

- best formal signals come from `results[0].signals`;
- formal diagnostics come from `results[0].diagnosticSignals`;
- observation candidates come from `observationSearch.signals`.

Test expectations:

- QQQ 2022 Q4 has no formal signal and has OBS coverage.
- QQQ 2026 March has no formal signal and has OBS coverage.
- diagnostic output includes `bottomScore`, formal threshold, score gap, and `riskFlags`.

Expected command:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_2022_2026_miss_diagnostics_explain_formal_absence
```

Expected first result: FAIL because the diagnostic report does not exist yet.

- [x] **Step 2: Implement diagnostic extraction**

Add a helper that takes the existing payload and emits rows for:

- window label: `QQQ 2022 Q4` or `QQQ 2026 March`;
- date;
- symbol;
- source: `formal`, `diagnostic`, or `observation`;
- bottom score;
- formal entry threshold;
- score gap to formal entry;
- risk flags;
- forward 6m return when mature;
- reason bucket.

Reason buckets should be plain English:

- `below_formal_threshold`;
- `no_repair`;
- `market_or_structure_filter`;
- `min_signal_gap_filter`;
- `no_near_formal_candidate`.

- [x] **Step 3: Generate report and CSV writers**

Add Markdown and CSV output functions.

The Markdown must explain in simple terms:

- OBS means "candidate/watch only";
- formal MB Strong means "actual strategy buy signal";
- current evidence says the formal layer rejected 2022/2026 mainly because score and repair quality were not high enough.

- [x] **Step 4: Run targeted test**

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_2022_2026_miss_diagnostics_explain_formal_absence
```

Expected result: PASS.

## Task 3: Reuse Existing 311 Search Results Before Expanding Grid

- [x] **Step 1: Add candidate-review test**

Add a test that scans `payload["results"]` and produces a review table:

- configs with formal signals in QQQ 2022 Q4;
- configs with formal signals in QQQ 2026 March;
- configs with diagnostic near misses in each window;
- each config's signal count, 6m average return, win rate, and validation-window coverage.

Expected command:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_existing_results_review_lists_2022_2026_candidate_configs
```

Expected first result: FAIL because the review table does not exist yet.

- [x] **Step 2: Implement review table**

Use the existing full-pool result first. Do not expand the parameter grid until this table proves what is missing.

Current observed fact to preserve:

- existing result pool has 311 configs;
- QQQ 2022 Q4 has diagnostic candidates in some configs but no formal hits;
- QQQ 2026 March currently has no formal or diagnostic hit in the checked pool.

- [x] **Step 3: Run targeted test**

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search.BottomSignalSearchTest.test_existing_results_review_lists_2022_2026_candidate_configs
```

Expected result: PASS.

## Task 4: Run Isolated Full Search

- [x] **Step 1: Run the standard full search into isolated outputs**

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4 --research-tag 2022_2026_miss_search
```

Expected result:

- command completes successfully;
- main `strategy_catalog/bottom_signal_formal/bottom_signal_results.json` remains the compressed baseline;
- tagged research JSON is created;
- best config and candidate review are reported separately.

- [x] **Step 2: Compare tagged result against baseline**

Run a read-only check that prints:

- main best config;
- tagged best config;
- main formal signal count;
- tagged formal signal count;
- whether QQQ 2022 Q4 or 2026 March formal coverage changed.

If tagged search still does not cover 2022/2026 formally, do not force a strategy change. Record that the current grid does not find a safe formal replacement.

## Task 5: Optional Narrow Grid Expansion

Only do this task if Task 4 cannot explain 2026 March or finds no useful candidate.

- [x] **Step 1: Create a separate research config**

Create `strategy_catalog/bottom_signal_2022_2026_research/bottom_signal_config_2022_2026_miss_search.json` by copying the current config and changing only research parameters.

Allowed research-only expansions:

- add `entry_thresholds`: 76, 78, 80, 82;
- add `mb_entry_offset`: -4, -2, 0;
- keep or compare `min_signal_gap`: 21, 42, 63;
- make small repair/structure weight variants.

Do not edit the main `strategy_catalog/bottom_signal_formal/bottom_signal_config.json` for this task.

- [x] **Step 2: Run expanded isolated search**

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --config strategy_catalog\bottom_signal_2022_2026_research\bottom_signal_config_2022_2026_miss_search.json --max-configs 1440 --workers 4 --research-tag 2022_2026_miss_expanded
```

Expected result:

- tagged research outputs only;
- no overwrite of main compressed baseline;
- report explains whether lower threshold/offset variants create too many signals or reduce quality.

## Acceptance Criteria

- Main baseline remains unchanged unless a later separate promotion plan is approved.
- `bestConfig.name == seed_previous_rs_higher_low_best` remains true for the main compressed result.
- Main full-pool symbol count remains 21.
- Main formal signal count remains 39.
- OBS duplicate formal count remains 0.
- QQQ 2022 Q4 and 2026 March are explicitly explained as formal-missed but OBS-covered windows.
- Every candidate replacement is labeled research-only.
- No changes to `config.py`, `prepare.py`, `run.py`, or `versions/`.

## Validation Commands

Minimum validation after code changes:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search
.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py
.venv\Scripts\python.exe -m json.tool strategy_catalog\bottom_signal_formal\bottom_signal_results.json > $null
git diff --check
git diff --name-only -- config.py prepare.py run.py versions
```

Full regression before claiming the implementation is complete:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"
```

Full isolated research run:

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4 --research-tag 2022_2026_miss_search
```

## Assumptions

- "2022 年和 2026 年为什么没有触发信号" means no formal MB Strong signal, not no OBS candidate.
- Current compressed result is the official baseline.
- This plan allows broader search, but only as research evidence.
- OBS/RS promotion requires a separate validation and Pine parity plan.

## Execution Result 2026-05-23

- Implemented `--research-tag` isolated output routing.
- Generated tagged full-search artifacts for `2022_2026_miss_search` and `2022_2026_miss_expanded`.
- Standard 720-grid search did not find a safe single formal replacement; 2022 had only diagnostic near misses and 2026 had no formal/diagnostic hit.
- Expanded shallow-market research found 12 single-formal configs covering both QQQ 2022 Q4 and 2026 March, but the lowest-count candidate still had 319 formal signals, so it is not a good replacement for the 39-signal baseline.
- Found current best research strategy shape: `baseline_formal_plus_obs_addon_v1`.
- `baseline_formal_plus_obs_addon_v1` preserves 39/39 existing formal baseline signals and adds the current 48 OBS candidates, for 87 combined signals.
- The combined strategy covers QQQ 2022 Q4 via 2022-10-03, 2022-10-11, and 2022-12-28, and covers QQQ 2026 March via 2026-03-27.
- Research artifacts:
  - `strategy_catalog/bottom_signal_2022_2026_research/bottom_signal_2022_2026_composite_strategy_report.md`
  - `strategy_catalog/bottom_signal_2022_2026_research/bottom_signal_2022_2026_composite_strategy_signals.csv`

## Execution Audit 2026-05-23

- Audit verdict: PASS with documented research-only deviations.
- Audit artifact: `strategy_catalog/bottom_signal_2022_2026_research/bottom_signal_2022_2026_plan_execution_audit.md`.
- Deviations from the initial narrow expansion were intentional and isolated:
  - expanded `entry_thresholds` to include `72`;
  - added lower MB offsets to test whether bottom scores around 68-71 can become formal signals;
  - relaxed research-only `market_drawdown_threshold` to `-8` to test shallow 2026 coverage;
  - disabled research-only signal-count hard rejection to measure signal explosion.
- The deviations did not touch the official baseline config and did not change `config.py`, `prepare.py`, `run.py`, or `versions/`.
- Intermediate `seed_probe` and `shallow_probe` artifacts were pruned after final tagged search and composite reports retained the useful conclusions.
