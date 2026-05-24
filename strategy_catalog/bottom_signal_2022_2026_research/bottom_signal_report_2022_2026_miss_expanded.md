# Bottom Signal Search Report

## Scope
- Symbols: AAPL, AMD, AMZN, AVGO, CAT, CRM, CRWD, JPM, LLY, META, MSFT, NVDA, PLTR, QQQ, SPY, TSLA, TSM, UNH, V, WMT, XOM
- Artifact scope: full-pool output
- Tested configs: 1440
- Staged search: True
- Promoted configs: 395
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
- Name: `btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry78_mbo0_rs63_wmomentum_reset`
- Drawdown: window `21`, threshold `-8.0%`
- RSI: `10`
- Stochastic: `9, 3`
- MACD: `12, 26, 9`
- SMA distance: `200`
- ATR: `20`
- Volume window: `10`
- Backtest entry score: `78`
- MB entry score: `78`
- RS entry score: `78`
- Experimental signal set: `rs_higher_low_structure`
- Min signal gap: `21` bars
- Market filter: `QQQ`/`SPY` 126-bar drawdown <= `-8.0%`
- Weights: drawdown `0.26`, momentum `0.3`, repair `0.2`, structure `0.14`, volume `0.05`, MA `0.05`

## Best Metrics
- Composite score: 30.28
- Pre dual-track adjustment score: 54.91
- Watch/Medium ratio score: 90.51
- RS missed-capture count: 0
- RS missed-capture score: 0.00
- Baseline quality score: 80.27
- Recent RS activity score: 57.14
- Qualified RS watchlist score: 100.00
- Bottom quality: 52.31
- Trade score: 91.47
- Exit quality: 0.00
- Signals: 124
- Active symbols: 21
- Avg 3m return: 16.52%
- Avg 6m return: 31.61%
- Avg 12m return: 51.98%
- Avg 6m adverse drawdown: -11.66%
- 6m adverse tail rate: 11.29%
- Avg market repair: 0.87%
- Avg local-bottom gap: 8.48%
- Avg bottom-capture score: 61.90
- Poor bottom-capture rate: 25.00%
- Poor bottom-capture penalty: 10.00
- 6m win rate: 79.34%
- QQQ/SPY signals: 7
- Individual-stock signals: 117
- QQQ/SPY avg 6m return: 29.36%
- Individual-stock avg 6m return: 31.75%
- Sparse count score: 49.23
- Group balance score: 88.33
- Validation coverage score: 100.00
- Win-rate score: 97.80
- Market repair score: 29.14
- Date-split coverage score: 100.00
- Date-split quality score: 90.90
- Train signals: 102
- Holdout signals: 22
- Holdout QQQ/SPY signals: 2
- Holdout individual-stock signals: 20
- Holdout avg 6m return: 48.38%
- Holdout avg 6m adverse drawdown: -7.28%
- Holdout 6m win rate: 89.47%
- Validation windows covered: 4/4
- Positive validation windows: 4/4
- Validation-window coverage score: 100.00
- Validation-window quality score: 91.94
- Validation-window avg 6m return: 39.20%
- Validation-window worst avg 6m return: 12.05%
- Validation-window avg 6m win rate: 81.74%
- Validation-window worst 6m win rate: 56.76%

## Baseline Comparison
- Baseline config: `btm_dw42_dt12_r10_st14x3_m8x21x5_sma50_atr10_vol10_gap42_entry82_wstructure_retest`
- Baseline signals: 40
- Baseline avg 6m return: 46.33%
- Baseline 6m win rate: 80.00%
- Current Strong signals: 124
- Current avg 6m return: 31.61%
- Current 6m win rate: 79.34%

## MB Factor Ablation
- Each row removes one MB scoring factor from the selected config and re-runs the same evaluation.
- Critical factors: drawdown, structure, ma
- Overactive without: momentum, repair
- Supportive factors: volume
- Redundant factors: none
- drawdown (Critical): score=0.00 delta=-30.28 signals=8 avg6m=21.08% adverse6m=-20.39%
- momentum (Overactive): score=0.00 delta=-30.28 signals=214 avg6m=23.32% adverse6m=-16.98%
- repair (Overactive): score=0.00 delta=-30.28 signals=703 avg6m=20.33% adverse6m=-13.11%
- structure (Critical): score=0.00 delta=-30.28 signals=28 avg6m=26.15% adverse6m=-12.41%
- ma (Critical): score=15.48 delta=-14.79 signals=179 avg6m=23.46% adverse6m=-13.28%
- volume (Supportive): score=25.23 delta=-5.05 signals=163 avg6m=29.59% adverse6m=-13.04%

## Signal Funnel
- Watch signals: 208
- Medium signals: 340
- Formal Strong signals: 124
- Watch/Medium to Strong ratio: 4.42x
- MB Strong signals: 100
- RS Strong signals: 24
- MB diagnostic signals: 420
- RS diagnostic signals: 128

## Recent 24M MB vs RS
- Window: 2024-05-01 to 2026-04-30
- Recent formal Strong signals: 21
- Recent diagnostic Watch/Medium signals: 57
- Recent MB Strong signals: 19
- Recent RS Strong signals: 2
- Recent MB diagnostic signals: 45
- Recent RS diagnostic signals: 12
- Recent RS candidate signals: 14
- Recent MB avg 6m return: 38.53%
- Recent RS avg 6m return: 35.85%

## Recent Validation
- Window: 2024-05-01 to 2026-04-30
- Recent formal signals: 21
- Mature 6m checks: 18
- Recent avg 6m return: 47.85%
- Recent 6m win rate: 88.89%
- Recent avg 6m adverse drawdown: -8.39%
- Status: Pass

## RS Secondary Watchlist
- These rows are RS candidates for observation/ranking. They are not the primary MB backtest entry layer.
- Recent RS candidate count: 14
- Qualified RS candidate count: 8
- Qualified RS target score: 100.00
- Recent RS candidate avg 6m return: 35.85%
- Recent RS candidate avg 6m adverse drawdown: -4.54%
- Qualified RS candidate avg 6m return: 37.00%
- Qualified RS candidate avg 6m adverse drawdown: -4.04%

## Separate RS Watchlist Best
- This is not the formal trading strategy. It is the best config found for the RS observation list only.
- Role: `rs_watchlist_only`
- Name: `btm_dw21_dt12_r14_st9x3_m8x21x5_sma150_atr14_vol10_gap21_entry78_mbo-4_rs63_wdeep_repair`
- Experimental signal set: `rs_antidrawdown_repair`
- Formal composite score: 0.00
- Formal Strong signals: 179
- Formal avg 6m return: 25.52%
- Qualified RS candidates: 19
- Qualified RS avg 6m return: 65.27%
- Qualified RS avg 6m adverse drawdown: -6.75%

## MB vs RS
- MB avg 6m return: 34.62%
- MB 6m win rate: 80.41%
- RS avg 6m return: 19.45%
- RS 6m win rate: 75.00%

## Missed Strong Stocks
- RS Strong rows here are candidates that the old QQQ/SPY hard market filter would have blocked.
- No RS Strong misses recorded for the selected config.

## Top Recent RS Candidates
- WMT 2024-08-07 Strong quality=82 qualified=True RS signal=79 RS strength=100 bottom=58 risk=none market drawdown=-13.56% fwd6m=51.94% adverse6m=0.00%
- V 2025-03-10 Medium quality=79 qualified=True RS signal=76 RS strength=100 bottom=52 risk=none market drawdown=-12.38% fwd6m=1.08% adverse6m=-9.73%
- WMT 2024-08-05 Medium quality=78 qualified=True RS signal=76 RS strength=100 bottom=51 risk=none market drawdown=-13.44% fwd6m=52.36% adverse6m=-1.01%
- META 2024-08-07 Watch quality=74 qualified=True RS signal=72 RS strength=100 bottom=48 risk=none market drawdown=-13.56% fwd6m=46.40% adverse6m=0.00%
- WMT 2024-08-06 Watch quality=73 qualified=True RS signal=72 RS strength=100 bottom=45 risk=none market drawdown=-12.61% fwd6m=52.60% adverse6m=-1.23%
- V 2025-03-06 Watch quality=71 qualified=True RS signal=72 RS strength=95 bottom=47 risk=none market drawdown=-9.51% fwd6m=0.07% adverse6m=-10.43%
- META 2024-09-06 Medium quality=75 qualified=True RS signal=76 RS strength=90 bottom=59 risk=none market drawdown=-10.79% fwd6m=21.29% adverse6m=0.00%
- NVDA 2025-04-10 Watch quality=71 qualified=True RS signal=72 RS strength=90 bottom=58 risk=none market drawdown=-17.18% fwd6m=70.29% adverse6m=-9.91%
- PLTR 2025-04-10 Watch quality=58 qualified=False RS signal=72 RS strength=100 bottom=52 risk=overextended_rebound market drawdown=-17.18% fwd6m=98.04% adverse6m=-0.05%
- V 2025-03-11 Strong quality=63 qualified=False RS signal=81 RS strength=93 bottom=67 risk=no_repair market drawdown=-12.59% fwd6m=2.15% adverse6m=-7.19%
- CRM 2024-08-05 Medium quality=56 qualified=False RS signal=77 RS strength=85 bottom=64 risk=no_repair market drawdown=-13.44% fwd6m=45.97% adverse6m=-0.25%
- CRM 2024-08-02 Watch quality=66 qualified=False RS signal=72 RS strength=78 bottom=60 risk=none market drawdown=-10.78% fwd6m=41.44% adverse6m=-2.27%
- AAPL 2024-08-05 Watch quality=48 qualified=False RS signal=72 RS strength=78 bottom=59 risk=no_repair market drawdown=-13.44% fwd6m=11.34% adverse6m=-0.97%
- LLY 2025-04-03 Watch quality=45 qualified=False RS signal=72 RS strength=70 bottom=64 risk=no_repair market drawdown=-16.35% fwd6m=6.89% adverse6m=-20.55%

## RS Coverage Tradeoffs
- These configs found more qualified RS watchlist candidates, but may have failed MB or validation gates.
- `btm_dw21_dt12_r14_st9x3_m8x21x5_sma150_atr14_vol10_gap21_entry78_mbo-4_rs63_wdeep_repair` set=rs_antidrawdown_repair score=0.00 strong=179 avg6m=25.52% qualifiedRS=19 qualifiedRSAvg6m=65.27% qualifiedRSAdverse6m=-6.75%
- `btm_dw252_dt8_r7_st14x3_m16x35x9_sma100_atr14_vol10_gap21_entry78_mbo-4_rs42_wstructure_retest` set=rs_higher_low_structure score=14.75 strong=435 avg6m=21.76% qualifiedRS=19 qualifiedRSAvg6m=16.80% qualifiedRSAdverse6m=-11.67%
- `btm_dw126_dt12_r21_st9x3_m12x26x9_sma100_atr10_vol10_gap21_entry76_mbo-2_rs126_wstructure_retest` set=rs_higher_low_structure score=9.17 strong=301 avg6m=19.75% qualifiedRS=15 qualifiedRSAvg6m=35.76% qualifiedRSAdverse6m=-8.13%
- `btm_dw126_dt12_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry78_mbo-4_rs63_wdeep_repair` set=rs_antidrawdown_repair score=16.12 strong=151 avg6m=32.78% qualifiedRS=15 qualifiedRSAvg6m=25.63% qualifiedRSAdverse6m=-17.87%
- `btm_dw252_dt12_r7_st14x3_m16x35x9_sma100_atr14_vol10_gap42_entry76_mbo-2_rs126_wstructure_retest` set=rs_higher_low_structure score=14.81 strong=319 avg6m=20.76% qualifiedRS=15 qualifiedRSAvg6m=15.18% qualifiedRSAdverse6m=-8.95%
- `btm_dw21_dt12_r21_st21x5_m16x35x9_sma200_atr20_vol20_gap21_entry72_mbo-2_rs42_wmomentum_reset` set=rs_repair_trend_confirm score=0.00 strong=177 avg6m=24.44% qualifiedRS=14 qualifiedRSAvg6m=38.62% qualifiedRSAdverse6m=-10.23%
- `btm_dw21_dt18_r14_st9x3_m8x21x5_sma150_atr14_vol10_gap21_entry76_mbo-2_rs42_wdeep_repair` set=rs_antidrawdown_repair score=0.00 strong=129 avg6m=32.06% qualifiedRS=13 qualifiedRSAvg6m=71.41% qualifiedRSAdverse6m=-4.52%
- `btm_dw252_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol20_gap21_entry76_mbo0_rs63_wdeep_repair` set=rs_antidrawdown_repair score=18.04 strong=146 avg6m=27.72% qualifiedRS=13 qualifiedRSAvg6m=41.83% qualifiedRSAdverse6m=-8.22%

## Walk-Forward Diagnostic
- Tested folds: 3/3
- Positive tested folds: 3/3
- Avg test 6m return: 36.46%
- Worst test 6m return: 13.58%
- Avg test 6m win rate: 76.87%
- select_to_2019_test_2020: selected `btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry82_mbo-4_rs63_wmomentum_reset`, train signals 46, test signals 7, test avg 6m 44.92%, test win 85.71%
- select_to_2021_test_2022: selected `btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry82_mbo-4_rs63_wmomentum_reset`, train signals 53, test signals 30, test avg 6m 13.58%, test win 56.67%
- select_to_2022_test_recent: selected `btm_dw21_dt8_r10_st9x3_m12x26x9_sma200_atr20_vol10_gap21_entry82_mbo-4_rs63_wmomentum_reset`, train signals 83, test signals 20, test avg 6m 50.89%, test win 88.24%

## Notes
- The selected config is still a research candidate, but it is now penalized unless it also has post-cutoff QQQ/SPY, individual-stock, multi-window validation coverage, and acceptable bottom-capture quality.
- Walk-forward diagnostics select each fold using only earlier signals, then score the selected config on the later test window.
- Pine output uses the best config as defaults, while keeping the main parameters adjustable in TradingView.
