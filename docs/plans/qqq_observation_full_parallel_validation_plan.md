# QQQ Missed-Bottom Observation Full Parallel Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Continue the QQQ missed-bottom observation work using full-pool, parallel-validated search results, while keeping OBS signals as observation-only candidates.

**Architecture:** Full search uses `bottom_signal_search.py --workers` to parallelize config evaluation only. The main process still owns data precompute/cache, output writing, and observation refresh. The final accepted artifacts must be generated from `--symbol all --max-configs 720`, not from a quick `QQQ,SPY` sample.

**Tech Stack:** Python 3.11, `unittest`, pandas, `ProcessPoolExecutor`, TradingView Pine output generation.

---

## Current State Snapshot

- Current best strategy: `seed_previous_rs_higher_low_best`.
- Formal Strong signals: `39`.
- Full-search avg 6m return: `39.24%`.
- Observation signals: `48`.
- Formal Strong baseline: `39`.
- Observation/Formal ratio: `1.23x`.
- Duplicate formal signals: `0`.
- QQQ 2022-10-01 to 2022-12-31: Covered via `2022-10-03`, `2022-10-11`, `2022-12-28`.
- QQQ 2026-03-01 to 2026-03-31: Covered via `2026-03-27`.
- Full workers validation already passed once with:
  - `.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`
- Keep `OBS-D` and `OBS-S` candidate-only. Do not promote them into formal MB/RS Strong logic without a separate plan.

## Task 1: Verify Parallel Search Is Still Clean

**Files:**
- Read: `claude-progress.md`
- Read: `investigations/bottom_signal_search.py`
- Read: `tests/test_bottom_signal_search.py`

- [ ] **Step 1: Confirm no stale workers are running**

Run:

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'bottom_signal_search|multiprocessing|spawn' } | Select-Object ProcessId,CommandLine
```

Expected: empty output. If not empty, stop only those stale `bottom_signal_search` / multiprocessing workers before running a new full search.

- [ ] **Step 2: Run unit tests**

Run:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search
```

Expected: all tests pass. Current known baseline after workers implementation is `89 tests`.

- [ ] **Step 3: Run syntax check**

Run:

```powershell
.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py
```

Expected: exit code `0`. On Windows, if `__pycache__` has a transient access-denied error immediately after tests, wait 2 seconds and rerun once.

## Task 2: Prove Small Serial And Parallel Runs Match

**Files:**
- Write outputs through `investigations/bottom_signal_search.py`

- [ ] **Step 1: Run small serial search**

Run:

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 1
```

Expected best config:

```text
btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced
```

Expected metrics in stdout: `signals=2`, `avg6m=-4.32%`.

- [ ] **Step 2: Run small parallel search**

Run:

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol QQQ,SPY --max-configs 12 --workers 2
```

Expected: same best config, `signals=2`, `avg6m=-4.32%`.

## Task 3: Run Full Parallel Search And Refresh Observation

**Files:**
- Generate: `strategy_catalog/bottom_signal_formal/bottom_signal_results.json`
- Generate: `strategy_catalog/bottom_signal_formal/bottom_signal_report.md`
- Generate: `strategy_catalog/bottom_signal_formal/bottom_signal_plan_summary.md`
- Generate: `strategy_catalog/bottom_signal_formal/bottom_signal_next_actions.csv`
- Generate: `strategy_catalog/bottom_signal_observation_addon/bottom_signal_observation_report.md`
- Generate: `strategy_catalog/bottom_signal_observation_addon/bottom_signal_observation_signals.csv`
- Generate: `strategy_catalog/bottom_signal_observation_addon/bottom_signal_merged_observation.pine`

- [ ] **Step 1: Run full parallel search**

Run:

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4
```

Expected current baseline:

```text
Best seed_previous_rs_higher_low_best score=27.95 signals=39 avg6m=39.24%
```

Do not start a second full search while this command is running.

- [ ] **Step 2: Refresh observation from full results**

Run:

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search
```

Expected current baseline:

```text
Refreshed observation search signals=48 upgradeScore=80.52
```

## Task 4: Verify Full Artifacts

**Files:**
- Read: `strategy_catalog/bottom_signal_formal/bottom_signal_results.json`
- Read: `strategy_catalog/bottom_signal_observation_addon/bottom_signal_observation_report.md`
- Read: `strategy_catalog/bottom_signal_observation_addon/bottom_signal_observation_signals.csv`
- Read: `strategy_catalog/bottom_signal_observation_addon/bottom_signal_merged_observation.pine`

- [ ] **Step 1: Validate JSON parses**

Run:

```powershell
.venv\Scripts\python.exe -m json.tool strategy_catalog\bottom_signal_formal\bottom_signal_results.json > $null
```

Expected: exit code `0`.

- [ ] **Step 2: Confirm full-pool result**

Run:

```powershell
@'
import json
from pathlib import Path
p=json.loads(Path("strategy_catalog/bottom_signal_formal/bottom_signal_results.json").read_text())
print(len(p["symbols"]), p["bestConfig"]["name"], p["bestMetrics"]["signalCount"])
print(p["observationSearch"]["metrics"])
print(p["observationSearch"]["anchorCoverage"])
'@ | .venv\Scripts\python.exe -
```

Expected:

```text
21 seed_previous_rs_higher_low_best 39
```

Observation metrics should include `signalCount=48`, `formalStrongBaselineCount=39`, `duplicateFormalCount=0`, and `observationToFormalRatio` near `1.23`.

- [ ] **Step 3: Confirm QQQ anchors**

Run:

```powershell
Select-String -Path strategy_catalog\bottom_signal_observation_addon\bottom_signal_observation_report.md -Pattern "2022-10-01|2026-03-01|2022-10-03|2026-03-27|Duplicate formal|Observation/Formal ratio"
```

Expected: both anchor windows are `Covered`, and anchor detail rows include `2022-10-03`, `2022-10-11`, `2022-12-28`, and `2026-03-27`.

- [ ] **Step 4: Confirm merged Pine labels and alerts**

Run:

```powershell
Select-String -Path strategy_catalog\bottom_signal_observation_addon\bottom_signal_merged_observation.pine -Pattern "OBS-D|OBS-S|RS-Q|RS-R|obsBottomMax|alertcondition"
```

Expected: all patterns appear.

## Task 5: Optional Exploration Queue

These are follow-up iterations, not blockers for the current full validation gate.

- [ ] **Worker scaling benchmark**

Run `--symbol QQQ,SPY --max-configs 72` or staged full-pool searches with `--workers 1`, `2`, `4`, and `6`. Record elapsed time and recommend the default operator command.

- [ ] **Observation sensitivity**

Explore `nearLowMax`, `deepBottomMin`, `shallowBottomMin`, and `clusterWindow` around the selected config. Keep the output observation-only. Do not promote `OBS-D` or `OBS-S`.

- [ ] **Pine parity guard**

Add tests ensuring generated Pine uses the selected observation config values from JSON and keeps `obsBottomMax` independent from formal `watchThreshold`.

- [ ] **Artifact guard**

Add a report or JSON check that warns if `bottom_signal_results.json` only contains the `QQQ,SPY` sample after a quick test run. The next full validation must overwrite sample outputs with full `all` outputs before observation refresh.

## Final Verification Checklist

- [ ] `.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search`
- [ ] `.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_search.py tests\test_bottom_signal_search.py`
- [ ] `.venv\Scripts\python.exe -m json.tool strategy_catalog\bottom_signal_formal\bottom_signal_results.json > $null`
- [ ] `git diff --check`
- [ ] `git diff --name-only -- config.py prepare.py run.py versions` returns empty output.
- [ ] Update `claude-progress.md` with the final result of the iteration.
