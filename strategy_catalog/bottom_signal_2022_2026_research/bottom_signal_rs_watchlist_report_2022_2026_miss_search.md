# RS Watchlist Report

## Scope
- Observation only. This report is not the formal MB-led trading strategy.
- Role: `rs_watchlist_only`
- Pine: `bottom_signal_rs_watchlist_pine.pine`
- Ticker CSV: `bottom_signal_rs_watchlist_tickers.csv`
- Candidate CSV: `bottom_signal_rs_watchlist_candidates.csv`

## RS Watchlist Config
- Name: `btm_dw21_dt8_r7_st9x3_m8x21x5_sma50_atr10_vol10_gap21_entry82_mbo0_rs42_wbalanced`
- Experimental signal set: `rs_antidrawdown_repair`
- Drawdown: window `21`, threshold `-8.0%`
- RSI: `7`
- SMA distance: `50`
- RS window: `42`

## Formal Strategy Context
- Formal composite score: 0.00
- Formal Strong signals: 38
- Formal avg 6m return: 43.06%
- Formal 6m win rate: 76.32%
- A zero or weak formal score here means this config is for RS observation only.

## Watchlist Quality
- Qualified RS candidates: 12
- Qualified RS avg 6m return: 72.01%
- Qualified RS avg 6m adverse drawdown: -4.33%

## Top RS Watchlist Candidates
- PLTR 2024-08-06 Watch quality=74 qualified=True RS signal=73 RS strength=97 bottom=54 risk=none fwd6m=318.50% adverse6m=-1.02%
- V 2025-03-10 Watch quality=73 qualified=True RS signal=73 RS strength=95 bottom=55 risk=none fwd6m=1.08% adverse6m=-9.73%
- META 2024-09-06 Watch quality=75 qualified=True RS signal=78 RS strength=93 bottom=65 risk=none fwd6m=21.29% adverse6m=0.00%
- CRM 2024-08-02 Watch quality=74 qualified=True RS signal=76 RS strength=92 bottom=63 risk=none fwd6m=41.44% adverse6m=-2.27%
- JPM 2025-04-08 Medium quality=78 qualified=True RS signal=80 RS strength=90 bottom=71 risk=none fwd6m=41.55% adverse6m=0.00%
- AVGO 2025-04-10 Watch quality=72 qualified=True RS signal=75 RS strength=90 bottom=62 risk=none fwd6m=89.18% adverse6m=-3.53%
- TSLA 2025-04-10 Watch quality=71 qualified=True RS signal=73 RS strength=90 bottom=59 risk=none fwd6m=63.82% adverse6m=-9.87%
- AVGO 2025-04-08 Medium quality=78 qualified=True RS signal=81 RS strength=87 bottom=76 risk=none fwd6m=122.33% adverse6m=0.00%
- CRM 2026-03-30 Watch quality=70 qualified=True RS signal=73 RS strength=86 bottom=63 risk=none fwd6m=n/a adverse6m=-10.62%
- AAPL 2025-04-09 Watch quality=71 qualified=True RS signal=78 RS strength=80 bottom=76 risk=none fwd6m=28.07% adverse6m=-4.24%
- AMZN 2025-04-07 Watch quality=71 qualified=True RS signal=79 RS strength=79 bottom=79 risk=none fwd6m=26.54% adverse6m=-4.53%
- META 2025-04-07 Medium quality=74 qualified=True RS signal=81 RS strength=76 bottom=85 risk=none fwd6m=38.33% adverse6m=-6.12%
- LLY 2024-08-09 Watch quality=56 qualified=False RS signal=72 RS strength=95 bottom=54 risk=overextended_rebound fwd6m=-2.70% adverse6m=-18.36%
- V 2025-03-11 Medium quality=61 qualified=False RS signal=80 RS strength=93 bottom=70 risk=no_repair fwd6m=2.15% adverse6m=-7.19%
- CRWD 2025-04-04 Watch quality=57 qualified=False RS signal=79 RS strength=90 bottom=70 risk=no_repair fwd6m=54.20% adverse6m=0.00%

## Action Summary
- Priority: 2
- Watch: 7
- Avoid: 3

## Ticker Summary
- #1 AVGO: action=Priority, qualified=2, candidates=2, selection=92.4, reason=repeated qualified candidates with clean risk profile, avg_quality=75.0, best=2025-04-08 q78, risk_flagged=0, avg6m=105.76% avg_adverse6m=-1.77%
- #2 META: action=Priority, qualified=2, candidates=3, selection=92.1, reason=repeated qualified candidates with clean risk profile, avg_quality=70.3, best=2024-09-06 q75, risk_flagged=0, avg6m=33.48% avg_adverse6m=-3.72%
- #3 CRM: action=Watch, qualified=2, candidates=3, selection=79.7, reason=qualified but has risk flags, avg_quality=62.7, best=2024-08-02 q74, risk_flagged=1, avg6m=20.05% avg_adverse6m=-5.91%
- #4 PLTR: action=Watch, qualified=1, candidates=2, selection=73.2, reason=qualified but quality score is below priority, avg_quality=69.5, best=2024-08-06 q74, risk_flagged=0, avg6m=226.27% avg_adverse6m=-0.84%
- #5 AMZN: action=Watch, qualified=1, candidates=1, selection=66.8, reason=qualified watchlist candidate, avg_quality=71.0, best=2025-04-07 q71, risk_flagged=0, avg6m=26.54% avg_adverse6m=-4.53%
- #6 TSLA: action=Watch, qualified=1, candidates=1, selection=62.3, reason=qualified watchlist candidate, avg_quality=71.0, best=2025-04-10 q71, risk_flagged=0, avg6m=63.82% avg_adverse6m=-9.87%
- #7 AAPL: action=Watch, qualified=1, candidates=3, selection=59.1, reason=qualified but has risk flags, avg_quality=64.7, best=2025-04-09 q71, risk_flagged=1, avg6m=14.23% avg_adverse6m=-9.81%
- #8 V: action=Watch, qualified=1, candidates=2, selection=57.9, reason=qualified but has risk flags, avg_quality=67.0, best=2025-03-10 q73, risk_flagged=1, avg6m=1.61% avg_adverse6m=-8.46%
- #9 JPM: action=Watch, qualified=1, candidates=3, selection=56.3, reason=qualified but has risk flags, avg_quality=60.0, best=2025-04-08 q78, risk_flagged=2, avg6m=38.23% avg_adverse6m=-3.20%
- #10 CAT: action=Avoid, qualified=0, candidates=1, selection=50.9, reason=no qualified RS candidates, avg_quality=67.0, best=2024-08-06 q67, risk_flagged=0, avg6m=12.76% avg_adverse6m=-0.20%
- #11 NVDA: action=Avoid, qualified=0, candidates=1, selection=49.5, reason=no qualified RS candidates, avg_quality=66.0, best=2025-04-07 q66, risk_flagged=0, avg6m=89.54% avg_adverse6m=-1.37%
- #12 CRWD: action=Avoid, qualified=0, candidates=1, selection=38.2, reason=no qualified RS candidates, avg_quality=57.0, best=2025-04-04 q57, risk_flagged=1, avg6m=54.20% avg_adverse6m=0.00%

## Notes
- Use this alongside the formal MB report, not as a replacement for it.
- `RS-Q` in Pine means qualified watchlist candidate; `RS-R` means risk-flagged watchlist candidate.
