# RS Watchlist Report

## Scope
- Observation only. This report is not the formal MB-led trading strategy.
- Role: `rs_watchlist_only`
- Pine: `bottom_signal_rs_watchlist_pine.pine`
- Ticker CSV: `bottom_signal_rs_watchlist_tickers.csv`
- Candidate CSV: `bottom_signal_rs_watchlist_candidates.csv`

## RS Watchlist Config
- Name: `btm_dw21_dt12_r14_st9x3_m8x21x5_sma150_atr14_vol10_gap21_entry78_mbo-4_rs63_wdeep_repair`
- Experimental signal set: `rs_antidrawdown_repair`
- Drawdown: window `21`, threshold `-12.0%`
- RSI: `14`
- SMA distance: `150`
- RS window: `63`

## Formal Strategy Context
- Formal composite score: 0.00
- Formal Strong signals: 179
- Formal avg 6m return: 25.52%
- Formal 6m win rate: 70.62%
- A zero or weak formal score here means this config is for RS observation only.

## Watchlist Quality
- Qualified RS candidates: 19
- Qualified RS avg 6m return: 65.27%
- Qualified RS avg 6m adverse drawdown: -6.75%

## Top RS Watchlist Candidates
- TSM 2026-03-31 Watch quality=75 qualified=True RS signal=74 RS strength=100 bottom=53 risk=none fwd6m=n/a adverse6m=0.00%
- CAT 2026-03-31 Watch quality=74 qualified=True RS signal=71 RS strength=100 bottom=48 risk=none fwd6m=n/a adverse6m=0.00%
- PLTR 2024-08-06 Watch quality=73 qualified=True RS signal=71 RS strength=100 bottom=47 risk=none fwd6m=318.50% adverse6m=-1.02%
- AAPL 2024-08-02 Watch quality=71 qualified=True RS signal=67 RS strength=100 bottom=40 risk=none fwd6m=6.12% adverse6m=-5.74%
- LLY 2026-02-04 Watch quality=70 qualified=True RS signal=65 RS strength=100 bottom=37 risk=none fwd6m=n/a adverse6m=-22.99%
- META 2025-01-27 Watch quality=70 qualified=True RS signal=65 RS strength=100 bottom=37 risk=none fwd6m=6.26% adverse6m=-26.49%
- AVGO 2025-11-24 Watch quality=70 qualified=True RS signal=67 RS strength=96 bottom=44 risk=none fwd6m=n/a adverse6m=-22.06%
- META 2024-09-06 Watch quality=70 qualified=True RS signal=68 RS strength=95 bottom=46 risk=none fwd6m=21.29% adverse6m=0.00%
- NVDA 2025-04-10 Strong quality=80 qualified=True RS signal=79 RS strength=90 bottom=70 risk=none fwd6m=70.29% adverse6m=-9.91%
- JPM 2025-04-08 Strong quality=79 qualified=True RS signal=78 RS strength=90 bottom=68 risk=none fwd6m=41.55% adverse6m=0.00%
- TSLA 2025-04-10 Strong quality=79 qualified=True RS signal=78 RS strength=90 bottom=68 risk=none fwd6m=63.82% adverse6m=-9.87%
- AAPL 2025-04-14 Watch quality=72 qualified=True RS signal=75 RS strength=90 bottom=62 risk=none fwd6m=22.64% adverse6m=-4.62%
- CRM 2026-03-30 Watch quality=72 qualified=True RS signal=74 RS strength=90 bottom=60 risk=none fwd6m=n/a adverse6m=-10.62%
- TSLA 2025-04-24 Watch quality=70 qualified=True RS signal=71 RS strength=90 bottom=56 risk=none fwd6m=73.01% adverse6m=0.00%
- AVGO 2025-04-08 Strong quality=81 qualified=True RS signal=83 RS strength=87 bottom=80 risk=none fwd6m=122.33% adverse6m=0.00%

## Action Summary
- Priority: 0
- Watch: 8
- Avoid: 4

## Ticker Summary
- #1 AAPL: action=Watch, qualified=3, candidates=4, selection=87.7, reason=qualified watchlist candidate, avg_quality=71.0, best=2025-04-09 q77, risk_flagged=0, avg6m=15.03% avg_adverse6m=-9.70%
- #2 TSLA: action=Avoid, qualified=3, candidates=6, selection=84.6, reason=qualified but adverse drawdown is high, avg_quality=69.2, best=2025-04-10 q79, risk_flagged=0, avg6m=42.49% avg_adverse6m=-13.16%
- #3 AVGO: action=Watch, qualified=2, candidates=7, selection=79.1, reason=qualified but has risk flags, avg_quality=62.6, best=2025-04-08 q81, risk_flagged=1, avg6m=77.52% avg_adverse6m=-8.11%
- #4 META: action=Watch, qualified=3, candidates=7, selection=79.1, reason=qualified but has risk flags, avg_quality=61.3, best=2025-04-07 q72, risk_flagged=1, avg6m=31.04% avg_adverse6m=-5.74%
- #5 JPM: action=Watch, qualified=1, candidates=3, selection=74.5, reason=qualified but quality score is below priority, avg_quality=69.0, best=2025-04-08 q79, risk_flagged=0, avg6m=37.53% avg_adverse6m=-4.15%
- #6 NVDA: action=Watch, qualified=1, candidates=3, selection=71.6, reason=qualified but quality score is below priority, avg_quality=66.3, best=2025-04-10 q80, risk_flagged=0, avg6m=55.56% avg_adverse6m=-6.90%
- #7 AMZN: action=Watch, qualified=1, candidates=1, selection=67.3, reason=qualified watchlist candidate, avg_quality=72.0, best=2025-04-07 q72, risk_flagged=0, avg6m=26.54% avg_adverse6m=-4.53%
- #8 CAT: action=Watch, qualified=1, candidates=4, selection=61.1, reason=qualified but has risk flags, avg_quality=64.5, best=2026-03-31 q74, risk_flagged=1, avg6m=10.03% avg_adverse6m=-7.92%
- #9 PLTR: action=Avoid, qualified=1, candidates=3, selection=59.5, reason=qualified but has risk flags, avg_quality=59.0, best=2024-08-06 q73, risk_flagged=1, avg6m=212.76% avg_adverse6m=-7.63%
- #10 TSM: action=Watch, qualified=1, candidates=5, selection=56.6, reason=qualified but has risk flags, avg_quality=62.4, best=2026-03-31 q75, risk_flagged=2, avg6m=51.86% avg_adverse6m=-3.16%
- #11 WMT: action=Avoid, qualified=0, candidates=3, selection=55.9, reason=no qualified RS candidates, avg_quality=68.3, best=2024-07-31 q69, risk_flagged=0, avg6m=30.84% avg_adverse6m=-3.12%
- #12 CRM: action=Avoid, qualified=1, candidates=5, selection=55.6, reason=qualified but has risk flags, avg_quality=60.8, best=2026-03-30 q72, risk_flagged=1, avg6m=5.79% avg_adverse6m=-12.66%

## Notes
- Use this alongside the formal MB report, not as a replacement for it.
- `RS-Q` in Pine means qualified watchlist candidate; `RS-R` means risk-flagged watchlist candidate.
