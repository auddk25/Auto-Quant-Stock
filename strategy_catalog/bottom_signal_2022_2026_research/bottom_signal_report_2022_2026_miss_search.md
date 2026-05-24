# Bottom Signal Search Report

## Scope
- Symbols: AAPL, AMD, AMZN, AVGO, CAT, CRM, CRWD, JPM, LLY, META, MSFT, NVDA, PLTR, QQQ, SPY, TSLA, TSM, UNH, V, WMT, XOM
- Artifact scope: full-pool output
- Tested configs: 720
- Staged search: True
- Promoted configs: 311
- Objective: 70% bottom signal quality, 20% full trade result, 10% exit signal quality.
- Gates: sparse signal count, QQQ/SPY coverage, individual-stock coverage, date-split holdout coverage, validation-window coverage, and bottom-capture quality.
- Formal Pine: `bottom_signal_pine.pine`
- RS watchlist Pine: `bottom_signal_rs_watchlist_pine.pine`
- Merged observation Pine: `bottom_signal_merged_observation.pine`
- Observation report: `bottom_signal_observation_report.md`
- MB factor ablation CSV: `bottom_signal_mb_factor_ablation.csv`
- Recent validation CSV: `bottom_signal_recent_validation.csv`
- Plan summary: `bottom_signal_plan_summary.md`
- Next actions CSV: `bottom_signal_next_actions.csv`

## Best Config
- Name: `seed_previous_rs_higher_low_best`
- Drawdown: window `126`, threshold `-8%`
- RSI: `10`
- Stochastic: `21, 5`
- MACD: `16, 35, 9`
- SMA distance: `100`
- ATR: `14`
- Volume window: `20`
- Backtest entry score: `82`
- MB entry score: `82`
- RS entry score: `82`
- Experimental signal set: `rs_higher_low_structure`
- Min signal gap: `42` bars
- Market filter: `QQQ`/`SPY` 126-bar drawdown <= `-20.0%`
- Weights: drawdown `0.3`, momentum `0.22`, repair `0.18`, structure `0.15`, volume `0.08`, MA `0.07`

## Best Metrics
- Composite score: 27.95
- Pre dual-track adjustment score: 34.35
- Watch/Medium ratio score: 100.00
- RS missed-capture count: 2
- RS missed-capture score: 100.00
- Baseline quality score: 99.64
- Recent RS activity score: 50.00
- Qualified RS watchlist score: 66.67
- Bottom quality: 33.24
- Trade score: 98.32
- Exit quality: 0.00
- Signals: 39
- Active symbols: 20
- Avg 3m return: 21.46%
- Avg 6m return: 39.24%
- Avg 12m return: 76.67%
- Avg 6m adverse drawdown: -13.80%
- 6m adverse tail rate: 20.51%
- Avg market repair: 0.77%
- Avg local-bottom gap: 10.20%
- Avg bottom-capture score: 55.11
- Poor bottom-capture rate: 28.21%
- Poor bottom-capture penalty: 11.28
- 6m win rate: 74.36%
- QQQ/SPY signals: 4
- Individual-stock signals: 35
- QQQ/SPY avg 6m return: 19.71%
- Individual-stock avg 6m return: 41.47%
- Sparse count score: 6.67
- Group balance score: 79.18
- Validation coverage score: 80.00
- Win-rate score: 81.20
- Market repair score: 25.70
- Date-split coverage score: 100.00
- Date-split quality score: 95.96
- Train signals: 32
- Holdout signals: 7
- Holdout QQQ/SPY signals: 1
- Holdout individual-stock signals: 6
- Holdout avg 6m return: 75.79%
- Holdout avg 6m adverse drawdown: -3.23%
- Holdout 6m win rate: 100.00%
- Validation windows covered: 4/4
- Positive validation windows: 4/4
- Validation-window coverage score: 100.00
- Validation-window quality score: 88.29
- Validation-window avg 6m return: 48.85%
- Validation-window worst avg 6m return: 7.67%
- Validation-window avg 6m win rate: 79.55%
- Validation-window worst 6m win rate: 54.55%

## Baseline Comparison
- Baseline config: `btm_dw42_dt12_r10_st14x3_m8x21x5_sma50_atr10_vol10_gap42_entry82_wstructure_retest`
- Baseline signals: 40
- Baseline avg 6m return: 46.33%
- Baseline 6m win rate: 80.00%
- Current Strong signals: 39
- Current avg 6m return: 39.24%
- Current 6m win rate: 74.36%

## MB Factor Ablation
- Each row removes one MB scoring factor from the selected config and re-runs the same evaluation.
- Critical factors: drawdown, momentum, structure, volume, ma
- Overactive without: repair
- Supportive factors: none
- Redundant factors: none
- drawdown (Critical): score=-0.00 delta=-27.95 signals=2 avg6m=-6.15% adverse6m=-11.41%
- momentum (Critical): score=0.00 delta=-27.95 signals=46 avg6m=40.73% adverse6m=-16.16%
- repair (Overactive): score=0.00 delta=-27.95 signals=125 avg6m=18.71% adverse6m=-15.00%
- structure (Critical): score=0.00 delta=-27.95 signals=8 avg6m=65.96% adverse6m=-14.84%
- volume (Critical): score=0.00 delta=-27.95 signals=21 avg6m=64.94% adverse6m=-14.73%
- ma (Critical): score=0.00 delta=-27.95 signals=17 avg6m=37.98% adverse6m=-14.16%

## Signal Funnel
- Watch signals: 88
- Medium signals: 41
- Formal Strong signals: 39
- Watch/Medium to Strong ratio: 3.31x
- MB Strong signals: 35
- RS Strong signals: 4
- MB diagnostic signals: 100
- RS diagnostic signals: 29

## Recent 24M MB vs RS
- Window: 2024-05-01 to 2026-04-30
- Recent formal Strong signals: 7
- Recent diagnostic Watch/Medium signals: 16
- Recent MB Strong signals: 7
- Recent RS Strong signals: 0
- Recent MB diagnostic signals: 12
- Recent RS diagnostic signals: 4
- Recent RS candidate signals: 4
- Recent MB avg 6m return: 54.03%
- Recent RS avg 6m return: 12.79%

## Recent Validation
- Window: 2024-05-01 to 2026-04-30
- Recent formal signals: 7
- Mature 6m checks: 7
- Recent avg 6m return: 75.79%
- Recent 6m win rate: 100.00%
- Recent avg 6m adverse drawdown: -3.23%
- Status: Pass

## RS Secondary Watchlist
- These rows are RS candidates for observation/ranking. They are not the primary MB backtest entry layer.
- Recent RS candidate count: 4
- Qualified RS candidate count: 2
- Qualified RS target score: 66.67
- Recent RS candidate avg 6m return: 12.79%
- Recent RS candidate avg 6m adverse drawdown: -10.57%
- Qualified RS candidate avg 6m return: 26.51%
- Qualified RS candidate avg 6m adverse drawdown: -4.86%

## Separate RS Watchlist Best
- This is not the formal trading strategy. It is the best config found for the RS observation list only.
- Role: `rs_watchlist_only`
- Name: `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`
- Experimental signal set: `rs_antidrawdown_repair`
- Formal composite score: 0.00
- Formal Strong signals: 38
- Formal avg 6m return: 43.06%
- Qualified RS candidates: 12
- Qualified RS avg 6m return: 72.01%
- Qualified RS avg 6m adverse drawdown: -4.33%

## MB vs RS
- MB avg 6m return: 41.70%
- MB 6m win rate: 74.29%
- RS avg 6m return: 17.73%
- RS 6m win rate: 75.00%

## Missed Strong Stocks
- RS Strong rows here are candidates that the old QQQ/SPY hard market filter would have blocked.
- LLY 2015-08-24 RS=95 bottom=67 market drawdown=-13.62%
- V 2011-08-08 RS=93 bottom=72 market drawdown=-17.31%

## Top Recent RS Candidates
- V 2025-03-10 Watch quality=75 qualified=True RS signal=76 RS strength=98 bottom=53 risk=none market drawdown=-12.38% fwd6m=1.08% adverse6m=-9.73%
- WMT 2024-08-07 Watch quality=75 qualified=True RS signal=78 RS strength=96 bottom=58 risk=none market drawdown=-13.56% fwd6m=51.94% adverse6m=0.00%
- LLY 2025-04-17 Watch quality=59 qualified=False RS signal=76 RS strength=96 bottom=63 risk=overextended_rebound market drawdown=-17.56% fwd6m=-4.01% adverse6m=-25.36%
- V 2025-03-11 Medium quality=59 qualified=False RS signal=80 RS strength=88 bottom=69 risk=no_repair market drawdown=-12.59% fwd6m=2.15% adverse6m=-7.19%

## RS Coverage Tradeoffs
- These configs found more qualified RS watchlist candidates, but may have failed MB or validation gates.
- `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced` set=rs_antidrawdown_repair score=0.00 strong=38 avg6m=43.06% qualifiedRS=12 qualifiedRSAvg6m=72.01% qualifiedRSAdverse6m=-4.33%
- `btm_dw21_dt8_r21_st14x3_m8x21x5_sma150_atr14_vol50_gap42_entry90_mbo3_rs126_wdeep_repair` set=rs_repair_trend_confirm score=0.00 strong=0 avg6m=0.00% qualifiedRS=8 qualifiedRSAvg6m=49.45% qualifiedRSAdverse6m=-4.35%
- `btm_dw21_dt12_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap21_entry82_mbo0_rs42_wbalanced` set=rs_antidrawdown_repair score=0.00 strong=43 avg6m=38.65% qualifiedRS=7 qualifiedRSAvg6m=52.98% qualifiedRSAdverse6m=-3.42%
- `btm_dw21_dt12_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap21_entry82_mbo3_rs42_wbalanced` set=rs_antidrawdown_repair score=0.00 strong=11 avg6m=35.91% qualifiedRS=7 qualifiedRSAvg6m=52.98% qualifiedRSAdverse6m=-3.42%
- `btm_dw21_dt12_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap21_entry82_mbo6_rs42_wbalanced` set=rs_antidrawdown_repair score=0.00 strong=6 avg6m=22.00% qualifiedRS=7 qualifiedRSAvg6m=52.98% qualifiedRSAdverse6m=-3.42%
- `btm_dw21_dt12_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap21_entry85_mbo0_rs42_wbalanced` set=rs_antidrawdown_repair score=0.00 strong=7 avg6m=47.33% qualifiedRS=7 qualifiedRSAvg6m=52.98% qualifiedRSAdverse6m=-3.42%
- `btm_dw21_dt12_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap21_entry85_mbo3_rs42_wbalanced` set=rs_antidrawdown_repair score=0.00 strong=2 avg6m=34.17% qualifiedRS=7 qualifiedRSAvg6m=52.98% qualifiedRSAdverse6m=-3.42%
- `btm_dw21_dt12_r10_st21x5_m16x35x9_sma100_atr14_vol20_gap21_entry85_mbo6_rs42_wbalanced` set=rs_antidrawdown_repair score=0.00 strong=1 avg6m=64.26% qualifiedRS=7 qualifiedRSAvg6m=52.98% qualifiedRSAdverse6m=-3.42%

## Walk-Forward Diagnostic
- Tested folds: 3/3
- Positive tested folds: 3/3
- Avg test 6m return: 83.65%
- Worst test 6m return: 21.60%
- Avg test 6m win rate: 87.88%
- select_to_2019_test_2020: selected `btm_dw252_dt8_r7_st14x3_m16x35x9_sma100_atr14_vol10_gap21_entry82_mbo0_rs42_wbalanced`, train signals 9, test signals 3, test avg 6m 154.47%, test win 100.00%
- select_to_2021_test_2022: selected `btm_dw252_dt18_r7_st9x3_m8x21x5_sma50_atr10_vol20_gap42_entry82_mbo0_rs63_wbalanced`, train signals 15, test signals 11, test avg 6m 21.60%, test win 63.64%
- select_to_2022_test_recent: selected `btm_dw252_dt18_r7_st9x3_m8x21x5_sma50_atr10_vol20_gap42_entry82_mbo0_rs63_wbalanced`, train signals 26, test signals 5, test avg 6m 74.87%, test win 100.00%

## Notes
- The selected config is still a research candidate, but it is now penalized unless it also has post-cutoff QQQ/SPY, individual-stock, multi-window validation coverage, and acceptable bottom-capture quality.
- Walk-forward diagnostics select each fold using only earlier signals, then score the selected config on the later test window.
- Pine output uses the best config as defaults, while keeping the main parameters adjustable in TradingView.
