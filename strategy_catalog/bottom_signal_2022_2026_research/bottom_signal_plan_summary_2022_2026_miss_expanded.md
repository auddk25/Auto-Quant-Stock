# MB Ablation, RS Selection, Recent Validation Summary

## Decision Snapshot
- Best config: `btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry78_mbo0_rs63_wmomentum_reset`
- Composite score: 30.28
- Strong signals: 124
- Avg 6m return: 31.61%
- 6m win rate: 79.34%
- Avg 6m adverse drawdown: -11.66%

## MB Factor Read
- Critical factors: drawdown, structure, ma
- Overactive without: momentum, repair
- Supportive factors: volume
- Redundant factors: none
- drawdown: Critical, score delta -30.28, signal delta -116
- momentum: Overactive, score delta -30.28, signal delta +90
- repair: Overactive, score delta -30.28, signal delta +579
- structure: Critical, score delta -30.28, signal delta -96
- ma: Critical, score delta -14.79, signal delta +55
- volume: Supportive, score delta -5.05, signal delta +39

## RS Selection Read
- #1 AAPL: action=Watch, selection=87.69, qualified=3, reason=qualified watchlist candidate
- #2 TSLA: action=Avoid, selection=84.59, qualified=3, reason=qualified but adverse drawdown is high
- #3 AVGO: action=Watch, selection=79.09, qualified=2, reason=qualified but has risk flags
- #4 META: action=Watch, selection=79.07, qualified=3, reason=qualified but has risk flags
- #5 JPM: action=Watch, selection=74.55, qualified=1, reason=qualified but quality score is below priority

## Recent Validation Read
- Window: 2024-05-01 to 2026-04-30
- Recent formal signals: 21
- Mature 6m checks: 18
- Recent avg 6m return: 47.85%
- Recent 6m win rate: 88.89%
- Recent avg 6m adverse drawdown: -8.39%
- Recent validation status: Pass

## Action Counts
- MB keep: 3
- MB brake: 2
- RS monitor: 0
- RS review: 8
- RS skip: 4

## Role Guide
- FormalStrategy: MB keep/brake actions belong to the formal strategy.
- Observation: RS Monitor/Review/Skip rows are watchlist actions only.
- Validation: RecentValidation rows summarize recent evidence.

## Decision Rule
- Do not promote RS watchlist rows into formal MB entries from this artifact.
- Keep the current MB factor stack intact unless a separate ablation run supports a change.
- Use RecentValidation status before any promotion decision.

## Next Actions
- Keep MB factors: drawdown, structure, ma
- Keep MB brake factors: momentum, repair
- Monitor Priority RS tickers: none
- Review Watch RS tickers: AAPL, AVGO, META, JPM, NVDA, AMZN, CAT, TSM
- Skip Avoid RS tickers: TSLA, PLTR, WMT, CRM
- Recent validation passed; continue observation.

## Files To Review
- Main report: `bottom_signal_report.md`
- MB ablation CSV: `bottom_signal_mb_factor_ablation.csv`
- Recent validation CSV: `bottom_signal_recent_validation.csv`
- RS ticker CSV: `bottom_signal_rs_watchlist_tickers.csv`
- Next actions CSV: `bottom_signal_next_actions.csv`
- RS detail report: `bottom_signal_rs_watchlist_report.md`

## Plain-English Read
- Critical MB factors are the parts that should not be removed without breaking the current research candidate.
- Overactive rows mean removing that factor creates too many signals, so that factor is acting as a useful brake.
- RS ranks are an observation list, not the formal MB entry rule.
- Recent validation is a quick check on the newest signal window before doing another full research pass.
