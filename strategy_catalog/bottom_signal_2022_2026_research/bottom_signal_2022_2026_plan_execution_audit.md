# 2022/2026 Full Search Plan Execution Audit

## Verdict

- Status: PASS with documented research-only deviations.
- The plan was executed far enough to answer the goal: the current formal baseline alone should stay frozen, and the strategy shape that preserves existing signals while covering QQQ 2022/2026 is `baseline_formal_plus_obs_addon_v1`.
- `baseline_formal_plus_obs_addon_v1` is not a live promotion. It is a research result that combines the frozen formal baseline with the current OBS-D/OBS-S add-on layer.

## Requirement Check

| Requirement | Evidence | Status |
|---|---:|---|
| Main baseline remains `seed_previous_rs_higher_low_best` | `bottom_signal_results.json` best config | PASS |
| Main full-pool symbol count remains 21 | `artifactScope.sampleKind=FULL_POOL`, symbols=21 | PASS |
| Main formal signal count remains 39 | `bestMetrics.signalCount=39` | PASS |
| Main OBS duplicate formal count remains 0 | `observationSearch.metrics.duplicateFormalCount=0` | PASS |
| Standard isolated 720 search ran with tagged outputs | `bottom_signal_results_2022_2026_miss_search.json` | PASS |
| Standard search did not overwrite main result | main best/signal count unchanged | PASS |
| Tagged observation refresh covers anchors | QQQ 2022 Q4 has 3 OBS rows; QQQ 2026 March has 1 OBS row | PASS |
| Expanded research search ran with tagged outputs | `bottom_signal_results_2022_2026_miss_expanded.json.gz` | PASS |
| Single-formal replacement reviewed | 12 configs cover both windows; lowest signal count is 319 | PASS |
| Existing formal signals coexist with 2022/2026 coverage | composite CSV has 39 formal + 48 OBS = 87 rows | PASS |
| Forbidden files not changed | `git diff --name-only -- config.py prepare.py run.py versions` empty | PASS |

## Important Findings

- The original formal MB baseline misses QQQ 2022 Q4 and 2026 March because the anchor rows have bottom scores around 68-71, below the formal threshold 82, and several rows have `no_repair`.
- A single formal configuration can be forced to cover both target windows only by loosening rules enough that signal count explodes. The lowest-count expanded formal candidate has 319 signals, so it is not a good replacement for the 39-signal baseline.
- The correct current strategy shape is therefore additive: keep all existing formal signals and add OBS-D/OBS-S as a research-only layer.

## Documented Deviations

- The research config went beyond the original narrow expansion list:
  - added `entry_threshold=72`;
  - added lower MB offsets such as `-8` and `-5`;
  - relaxed `market_drawdown_threshold` from `-20` to `-8`;
  - disabled research-config signal-count hard rejection to observe how bad the signal explosion gets.
- This deviation is acceptable only because it is isolated in `bottom_signal_config_2022_2026_miss_search.json`, tagged outputs, and research reports. It does not change the main config or official strategy.
- Refresh commands were extended to honor `--research-tag` so tagged searches can refresh OBS without touching the main baseline. This is safer than refreshing tagged work through the main result file.

## Retained Artifacts

- `bottom_signal_results_2022_2026_miss_search.json`
- `bottom_signal_results_2022_2026_miss_expanded.json.gz`
- `bottom_signal_2022_2026_miss_diagnostics_2022_2026_miss_search.md`
- `bottom_signal_2022_2026_miss_diagnostics_2022_2026_miss_expanded.md`
- `bottom_signal_2022_2026_candidate_review_2022_2026_miss_search.csv`
- `bottom_signal_2022_2026_candidate_review_2022_2026_miss_expanded.csv`
- `bottom_signal_2022_2026_composite_strategy_report.md`
- `bottom_signal_2022_2026_composite_strategy_signals.csv`

## Pruned Artifacts

- Removed intermediate `seed_probe` and `shallow_probe` tagged outputs after the final `miss_search`, `miss_expanded`, and composite reports captured their useful conclusions.

## Validation

- `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search` PASS, 106 tests.
- `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py` PASS.
- `.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"` PASS, 148 tests.
- JSON validation PASS for main, standard tagged, expanded tagged, and research config JSON.
- `git diff --check` PASS.
- `git diff --name-only -- config.py prepare.py run.py versions` PASS; empty output.
