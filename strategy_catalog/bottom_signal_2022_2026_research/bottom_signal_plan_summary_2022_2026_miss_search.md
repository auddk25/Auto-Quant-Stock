# MB Ablation, RS Selection, Recent Validation Summary

## Decision Snapshot
- Best config: `seed_previous_rs_higher_low_best`
- Composite score: 27.95
- Strong signals: 39
- Avg 6m return: 39.24%
- 6m win rate: 74.36%
- Avg 6m adverse drawdown: -13.80%

## MB Factor Read
- Critical factors: drawdown, momentum, structure, volume, ma
- Overactive without: repair
- Supportive factors: none
- Redundant factors: none
- drawdown: Critical, score delta -27.95, signal delta -37
- momentum: Critical, score delta -27.95, signal delta +7
- repair: Overactive, score delta -27.95, signal delta +86
- structure: Critical, score delta -27.95, signal delta -31
- volume: Critical, score delta -27.95, signal delta -18
- ma: Critical, score delta -27.95, signal delta -22

## RS Selection Read
- #1 AVGO: action=Priority, selection=92.40, qualified=2, reason=repeated qualified candidates with clean risk profile
- #2 META: action=Priority, selection=92.11, qualified=2, reason=repeated qualified candidates with clean risk profile
- #3 CRM: action=Watch, selection=79.71, qualified=2, reason=qualified but has risk flags
- #4 PLTR: action=Watch, selection=73.24, qualified=1, reason=qualified but quality score is below priority
- #5 AMZN: action=Watch, selection=66.77, qualified=1, reason=qualified watchlist candidate

## Recent Validation Read
- Window: 2024-05-01 to 2026-04-30
- Recent formal signals: 7
- Mature 6m checks: 7
- Recent avg 6m return: 75.79%
- Recent 6m win rate: 100.00%
- Recent avg 6m adverse drawdown: -3.23%
- Recent validation status: Pass

## Action Counts
- MB keep: 5
- MB brake: 1
- RS monitor: 2
- RS review: 7
- RS skip: 3

## Role Guide
- FormalStrategy: MB keep/brake actions belong to the formal strategy.
- Observation: RS Monitor/Review/Skip rows are watchlist actions only.
- Validation: RecentValidation rows summarize recent evidence.

## Decision Rule
- Do not promote RS watchlist rows into formal MB entries from this artifact.
- Keep the current MB factor stack intact unless a separate ablation run supports a change.
- Use RecentValidation status before any promotion decision.

## Next Actions
- Keep MB factors: drawdown, momentum, structure, volume, ma
- Keep MB brake factors: repair
- Monitor Priority RS tickers: AVGO, META
- Review Watch RS tickers: CRM, PLTR, AMZN, TSLA, AAPL, V, JPM
- Skip Avoid RS tickers: CAT, NVDA, CRWD
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
