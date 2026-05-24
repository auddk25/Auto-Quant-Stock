# 2022/2026 Composite Candidate Strategy

## Summary

- Strategy name: `baseline_formal_plus_obs_addon_v1`.
- Rule: keep the current formal MB Strong baseline unchanged, then add the current OBS-D/OBS-S observation layer as a research-only add-on.
- This is not a formal promotion yet; it is the first strategy shape found that preserves existing signals and covers the 2022/2026 QQQ drawdown windows.

## Metrics

- Formal baseline signals preserved: 39/39.
- Add-on OBS signals: 48.
- Combined signals: 87.
- Mature 6m signals: 86.
- Combined 6m average return: 28.23%.
- Combined 6m win rate: 73.26%.
- Combined average adverse 6m drawdown: -12.36%.

## Anchor Coverage

- QQQ 2022 Q4: 2022-10-03 observation OBS-D bottom=68 risk=none fwd126=17.11%.
- QQQ 2022 Q4: 2022-10-11 observation OBS-D bottom=69 risk=no_repair fwd126=21.95%.
- QQQ 2022 Q4: 2022-12-28 observation OBS-D bottom=68 risk=no_repair fwd126=42.44%.
- QQQ 2026 March: 2026-03-27 observation OBS-S bottom=71 risk=no_repair fwd126=n/a.

## Expanded Formal Search Result

- Expanded single-formal-config search found 12 configs that cover both QQQ 2022 Q4 and QQQ 2026 March.
- Those configs are not good replacements because they produce hundreds of formal signals and preserve only a small subset of the current formal signal dates.
- Lowest-count formal candidate: `btm_dw252_dt12_r7_st14x3_m16x35x9_sma100_atr14_vol10_gap42_entry76_mbo-2_rs126_wstructure_retest` signals=319, avg6m=20.76%, win6m=76.77%, 2022=2022-12-28, 2026=2026-03-27.
- Lowest-count formal candidate: `seed_previous_rs_higher_low_research_mb68_entry76_mbo-8` signals=344, avg6m=20.79%, win6m=72.84%, 2022=2022-12-28, 2026=2026-03-20.
- Lowest-count formal candidate: `seed_previous_rs_higher_low_research_mb68_entry72_mbo-4` signals=378, avg6m=21.08%, win6m=72.63%, 2022=2022-12-28, 2026=2026-03-20.
- Lowest-count formal candidate: `btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry78_mbo-8_rs63_wmomentum_reset` signals=388, avg6m=18.33%, win6m=73.49%, 2022=2022-10-11, 2026=2026-03-27.
- Lowest-count formal candidate: `btm_dw252_dt8_r7_st14x3_m16x35x9_sma100_atr14_vol10_gap21_entry78_mbo-4_rs42_wstructure_retest` signals=435, avg6m=21.76%, win6m=78.96%, 2022=2022-10-11, 2026=2026-03-20.

## Decision

- Keep `seed_previous_rs_higher_low_best` as the official formal baseline.
- Treat `baseline_formal_plus_obs_addon_v1` as the current found research strategy for the user goal: existing formal signals remain present, and 2022/2026 QQQ drawdown windows are covered.
- Before live use or Pine promotion, run a separate promotion validation covering ablation, sample-out validation, signal-count limits, and Pine parity.
