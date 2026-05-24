"""Filesystem paths used by the Bottom Signal research workflow."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "investigations"
CATALOG_DIR = ROOT / "strategy_catalog"
FORMAL_STRATEGY_DIR = CATALOG_DIR / "bottom_signal_formal"
OBSERVATION_ADDON_DIR = CATALOG_DIR / "bottom_signal_observation_addon"
RESEARCH_2022_2026_DIR = CATALOG_DIR / "bottom_signal_2022_2026_research"

RESULTS_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_results.json"
REPORT_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_report.md"
PINE_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_pine.pine"
STRICT_FORMAL_PINE_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_strict_formal.pine"
MB_FACTOR_ABLATION_CSV_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_mb_factor_ablation.csv"
RECENT_VALIDATION_CSV_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_recent_validation.csv"
PLAN_SUMMARY_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_plan_summary.md"
NEXT_ACTIONS_CSV_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_next_actions.csv"
STRATEGY_ITERATION_REVIEW_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_strategy_iteration_review.md"
STRATEGY_ITERATION_REVIEW_CSV_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_strategy_iteration_review.csv"
DEFAULT_CONFIG_PATH = FORMAL_STRATEGY_DIR / "bottom_signal_config.json"

RS_WATCHLIST_PINE_PATH = OBSERVATION_ADDON_DIR / "bottom_signal_rs_watchlist_pine.pine"
RS_WATCHLIST_REPORT_PATH = OBSERVATION_ADDON_DIR / "bottom_signal_rs_watchlist_report.md"
RS_WATCHLIST_TICKER_CSV_PATH = OBSERVATION_ADDON_DIR / "bottom_signal_rs_watchlist_tickers.csv"
RS_WATCHLIST_CANDIDATE_CSV_PATH = OBSERVATION_ADDON_DIR / "bottom_signal_rs_watchlist_candidates.csv"
OBSERVATION_REPORT_PATH = OBSERVATION_ADDON_DIR / "bottom_signal_observation_report.md"
OBSERVATION_SIGNALS_CSV_PATH = OBSERVATION_ADDON_DIR / "bottom_signal_observation_signals.csv"
MERGED_OBSERVATION_PINE_PATH = OBSERVATION_ADDON_DIR / "bottom_signal_merged_observation.pine"

MISS_DIAGNOSTICS_REPORT_PATH = RESEARCH_2022_2026_DIR / "bottom_signal_2022_2026_miss_diagnostics.md"
MISS_DIAGNOSTICS_CSV_PATH = RESEARCH_2022_2026_DIR / "bottom_signal_2022_2026_miss_diagnostics.csv"
CANDIDATE_REVIEW_CSV_PATH = RESEARCH_2022_2026_DIR / "bottom_signal_2022_2026_candidate_review.csv"
CACHE_DIR = OUT_DIR / ".cache" / "bottom_signal_indicators"
