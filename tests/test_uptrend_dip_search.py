import unittest
from pathlib import Path

import pandas as pd

from investigations.uptrend_dip_search import (
    LONG_TERM_ADDON_DIR,
    UPTREND_DIP_DIR,
    UptrendDipConfig,
    build_paper_tracking_plan,
    build_prompt_to_artifact_checklist,
    classify_addon_signal,
    evaluate_full_grid_walk_forward,
    evaluate_long_term_radar,
    evaluate_multi_window_validation,
    evaluate_restricted_walk_forward,
    format_paper_tracking_status,
    generate_long_term_addon_pine_script,
    generate_pine_script,
    candidate_configs_stage1,
    select_freeze_candidate_entries,
    score_buy_bottom_reversal,
    score_buy_index_shallow_pullback,
    score_buy_rsi_divergence,
    score_buy_tech_breakout,
    score_buy_trend_breakout,
    select_stage2_buy_configs,
    simulate_trades,
    summarize_active_signal_log,
    summarize_recent_signal_log,
    summarize_radar_subset,
    summarize_radar_segments,
    summarize_signal_risk_diagnostics,
    summarize_signal_years,
    summarize_signal_window,
)

from investigations.buy_dip_search import BUY_DIP_DIR


def make_cfg() -> UptrendDipConfig:
    return UptrendDipConfig(
        name="test",
        buy_strategy="tech_breakout",
        w_pb_trend=0,
        w_pb_level=0,
        w_pb_rsi=0,
        w_pb_stoch=0,
        w_pb_volume=0,
        w_bo_range=0.20,
        w_bo_signal=0.20,
        w_bo_volume=0.25,
        w_bo_momentum=0.20,
        w_bo_trend=0.15,
        buy_threshold=40,
        w_sell_breakdown=0.20,
        w_sell_cross=0.15,
        w_sell_rsi_break=0.15,
        w_sell_overbought=0.20,
        w_sell_keltner_upper=0.15,
        w_sell_profit=0.15,
        sell_threshold=35,
        stop_loss_pct=7,
    )


class TechBreakoutScoringTest(unittest.TestCase):
    def test_pine_strategy_outputs_live_in_strategy_catalog(self) -> None:
        self.assertEqual(UPTREND_DIP_DIR.name, "uptrend_dip_buy_sell")
        self.assertEqual(LONG_TERM_ADDON_DIR.name, "long_term_addon_radar")
        self.assertEqual(BUY_DIP_DIR.name, "buy_dip_indicator")
        self.assertEqual(UPTREND_DIP_DIR.parent.name, "strategy_catalog")
        self.assertEqual(LONG_TERM_ADDON_DIR.parent.name, "strategy_catalog")
        self.assertEqual(BUY_DIP_DIR.parent.name, "strategy_catalog")

    def test_relative_strength_volume_and_breakout_raise_score(self) -> None:
        cfg = make_cfg()
        index = pd.date_range("2024-01-01", periods=2)
        weak = pd.DataFrame(
            {
                "atr_compression": [20.0, 20.0],
                "breakout_dist": [0.0, 0.0],
                "tech_breakout_dist": [0.0, 0.0],
                "vol_ratio": [1.0, 1.0],
                "rsi14": [50.0, 50.0],
                "rsi_delta": [0.0, 0.0],
                "close": [100.0, 100.0],
                "sma200": [95.0, 95.0],
                "trend_pairs": [0.5, 0.5],
                "relative_strength_score": [35.0, 35.0],
            },
            index=index,
        )
        strong = weak.copy()
        strong.loc[index[-1], "atr_compression"] = 75.0
        strong.loc[index[-1], "tech_breakout_dist"] = 1.0
        strong.loc[index[-1], "vol_ratio"] = 1.8
        strong.loc[index[-1], "rsi14"] = 62.0
        strong.loc[index[-1], "rsi_delta"] = 4.0
        strong.loc[index[-1], "relative_strength_score"] = 90.0

        weak_score = score_buy_tech_breakout(weak, cfg).iloc[-1]
        strong_score = score_buy_tech_breakout(strong, cfg).iloc[-1]

        self.assertGreater(strong_score, weak_score + 40)

    def test_adx_and_ema_slope_raise_trend_breakout_score(self) -> None:
        cfg = make_cfg()
        index = pd.date_range("2024-01-01", periods=2)
        weak = pd.DataFrame(
            {
                "atr_compression": [50.0, 50.0],
                "breakout_dist": [0.6, 0.6],
                "vol_ratio": [1.4, 1.4],
                "rsi14": [58.0, 58.0],
                "rsi_delta": [2.0, 2.0],
                "close": [100.0, 100.0],
                "sma200": [95.0, 95.0],
                "trend_pairs": [1.0, 1.0],
                "adx14": [12.0, 12.0],
                "ema55_slope20": [-1.0, -1.0],
            },
            index=index,
        )
        strong = weak.copy()
        strong.loc[index[-1], "adx14"] = 32.0
        strong.loc[index[-1], "ema55_slope20"] = 4.0

        weak_score = score_buy_trend_breakout(weak, cfg).iloc[-1]
        strong_score = score_buy_trend_breakout(strong, cfg).iloc[-1]

        self.assertGreater(strong_score, weak_score + 20)

    def test_stage2_selection_keeps_best_config_from_each_strategy(self) -> None:
        configs = []
        for strategy, score in [
            ("tech_breakout", 100),
            ("tech_breakout", 99),
            ("tech_breakout", 98),
            ("breakout", 80),
            ("trend_breakout", 79),
        ]:
            cfg = make_cfg()
            cfg.name = f"{strategy}_{score}"
            cfg.buy_strategy = strategy
            configs.append({"config": cfg.__dict__, "combinedScore": score})

        selected = select_stage2_buy_configs(configs, max_configs=5)
        selected_strategies = {cfg.buy_strategy for cfg in selected}

        self.assertIn("breakout", selected_strategies)
        self.assertIn("trend_breakout", selected_strategies)

    def test_trailing_stop_exits_after_profitable_peak_drawdown(self) -> None:
        cfg = make_cfg()
        index = pd.date_range("2024-01-01", periods=5)
        df = pd.DataFrame(
            {
                "close": [100.0, 100.0, 115.0, 120.0, 110.0],
                "atr14": [2.0, 2.0, 2.0, 2.0, 2.0],
                "buy_score": [0.0, 50.0, 0.0, 0.0, 0.0],
            },
            index=index,
        )
        sell_reversal = pd.Series(0.0, index=index)
        sell_components = (
            pd.Series(0.0, index=index),
            pd.Series(0.0, index=index),
            pd.Series(0.0, index=index),
        )

        trades = simulate_trades(df, cfg, sell_reversal, sell_components)

        self.assertEqual(trades[0]["exit_reason"], "trailing_stop")
        self.assertEqual(trades[0]["exit_date"], "2024-01-05")

    def test_long_term_radar_scores_long_holding_returns_not_win_rate(self) -> None:
        cfg = make_cfg()
        index = pd.bdate_range("2020-01-01", periods=620)
        close = pd.Series(100.0, index=index)
        close.iloc[126] = 95.0
        close.iloc[252] = 140.0
        close.iloc[504] = 210.0
        close = close.interpolate()
        df = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        for pos in [0, 80, 160]:
            df.loc[index[pos], "buy_score"] = 80.0

        result = evaluate_long_term_radar(df, cfg)

        self.assertEqual(result["signalCount"], 3)
        self.assertGreater(result["score"], 50)
        self.assertEqual(result["signals"][0]["barsSinceSignal"], 619)
        self.assertTrue(result["signals"][0]["mature12m"])
        self.assertEqual(result["signals"][0]["return12mPct"], 40.0)
        self.assertEqual(result["signals"][0]["return24mPct"], 110.0)

    def test_long_term_radar_drawdown_is_never_positive(self) -> None:
        cfg = make_cfg()
        index = pd.bdate_range("2020-01-01", periods=620)
        close = pd.Series(100.0, index=index)
        close.iloc[1:253] = 110.0
        close.iloc[252] = 140.0
        close.iloc[504] = 210.0
        close = close.interpolate()
        df = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        for pos in [0, 80, 160]:
            df.loc[index[pos], "buy_score"] = 80.0

        result = evaluate_long_term_radar(df, cfg)

        self.assertEqual(result["signals"][0]["maxDrawdown12mPct"], 0.0)

    def test_long_term_radar_requires_bearish_candle(self) -> None:
        cfg = make_cfg()
        index = pd.bdate_range("2020-01-01", periods=620)
        close = pd.Series(100.0, index=index)
        close.iloc[252] = 130.0
        close.iloc[504] = 180.0
        close = close.interpolate()
        df = pd.DataFrame(
            {
                "open": close,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        df.loc[index[0], "open"] = 99.0
        df.loc[index[0], "close"] = 100.0
        df.loc[index[0], "buy_score"] = 80.0
        df.loc[index[1], "open"] = 102.0
        df.loc[index[1], "close"] = 100.0
        df.loc[index[1], "buy_score"] = 80.0

        result = evaluate_long_term_radar(df, cfg, min_gap_days=1)

        self.assertEqual(result["signalCount"], 1)
        self.assertEqual(result["signals"][0]["date"], "2020-01-02")

    def test_long_term_radar_penalizes_too_few_mature_signals(self) -> None:
        cfg = make_cfg()
        index = pd.bdate_range("2020-01-01", periods=620)
        close = pd.Series(100.0, index=index)
        close.iloc[252] = 180.0
        close.iloc[504] = 260.0
        close = close.interpolate()
        df = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        df.loc[index[0], "buy_score"] = 80.0

        result = evaluate_long_term_radar(df, cfg)

        self.assertLess(result["score"], 0)

    def test_long_term_radar_can_filter_signal_dates(self) -> None:
        cfg = make_cfg()
        index = pd.bdate_range("2020-01-01", periods=900)
        close = pd.Series(100.0, index=index)
        close.iloc[252] = 130.0
        close.iloc[504] = 180.0
        close = close.interpolate()
        df = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        df.loc[pd.Timestamp("2020-01-01"), "buy_score"] = 80.0
        df.loc[pd.Timestamp("2023-01-02"), "buy_score"] = 80.0

        result = evaluate_long_term_radar(df, cfg, signal_start_date="2023-01-01")

        self.assertEqual(result["signalCount"], 1)
        self.assertEqual(result["signals"][0]["date"], "2023-01-02")

    def test_bottom_reversal_scores_crash_retest_and_rsi_divergence(self) -> None:
        cfg = make_cfg()
        cfg.buy_strategy = "bottom_reversal"
        cfg.w_pb_trend = 0.20
        cfg.w_pb_level = 0.25
        cfg.w_pb_rsi = 0.25
        cfg.w_pb_stoch = 0.15
        cfg.w_pb_volume = 0.15
        index = pd.date_range("2024-01-01", periods=2)
        weak = pd.DataFrame(
            {
                "drawdown_252": [-5.0, -5.0],
                "bottom_retest_score": [0.0, 0.0],
                "rsi_divergence_score": [0.0, 0.0],
                "crash_score": [0.0, 0.0],
                "capitulation_score": [0.0, 0.0],
            },
            index=index,
        )
        strong = weak.copy()
        strong.loc[index[-1], "drawdown_252"] = -35.0
        strong.loc[index[-1], "bottom_retest_score"] = 90.0
        strong.loc[index[-1], "rsi_divergence_score"] = 100.0
        strong.loc[index[-1], "crash_score"] = 80.0
        strong.loc[index[-1], "capitulation_score"] = 70.0

        weak_score = score_buy_bottom_reversal(weak, cfg).iloc[-1]
        strong_score = score_buy_bottom_reversal(strong, cfg).iloc[-1]

        self.assertGreater(strong_score, weak_score + 70)

    def test_rsi_divergence_scores_divergence_as_standalone_buy_baseline(self) -> None:
        cfg = make_cfg()
        cfg.buy_strategy = "rsi_divergence"
        cfg.w_pb_trend = 0.50
        cfg.w_pb_level = 0.20
        cfg.w_pb_rsi = 0.15
        cfg.w_pb_stoch = 0.10
        cfg.w_pb_volume = 0.05
        index = pd.date_range("2024-01-01", periods=2)
        weak = pd.DataFrame(
            {
                "rsi_divergence_score": [0.0, 0.0],
                "bottom_retest_score": [0.0, 0.0],
                "drawdown_252": [-4.0, -4.0],
                "rsi14": [48.0, 48.0],
                "capitulation_score": [0.0, 0.0],
            },
            index=index,
        )
        strong = weak.copy()
        strong.loc[index[-1], "rsi_divergence_score"] = 100.0
        strong.loc[index[-1], "bottom_retest_score"] = 80.0
        strong.loc[index[-1], "drawdown_252"] = -24.0
        strong.loc[index[-1], "rsi14"] = 31.0
        strong.loc[index[-1], "capitulation_score"] = 40.0

        weak_score = score_buy_rsi_divergence(weak, cfg).iloc[-1]
        strong_score = score_buy_rsi_divergence(strong, cfg).iloc[-1]

        self.assertGreater(strong_score, weak_score + 65)

    def test_candidate_configs_include_rsi_divergence_buy_baseline(self) -> None:
        strategies = {cfg.buy_strategy for cfg in candidate_configs_stage1()}

        self.assertIn("rsi_divergence", strategies)

    def test_index_shallow_pullback_scores_orderly_index_dip(self) -> None:
        cfg = make_cfg()
        cfg.buy_strategy = "index_shallow_pullback"
        cfg.w_pb_trend = 0.20
        cfg.w_pb_level = 0.25
        cfg.w_pb_rsi = 0.25
        cfg.w_pb_stoch = 0.15
        cfg.w_pb_volume = 0.15
        index = pd.date_range("2024-01-01", periods=2)
        weak = pd.DataFrame(
            {
                "index_pullback_drawdown_score": [0.0, 0.0],
                "index_pullback_support_score": [10.0, 10.0],
                "index_pullback_rsi_score": [15.0, 15.0],
                "index_pullback_decline_score": [0.0, 0.0],
                "index_pullback_trend_score": [50.0, 50.0],
            },
            index=index,
        )
        strong = weak.copy()
        strong.loc[index[-1], "index_pullback_drawdown_score"] = 85.0
        strong.loc[index[-1], "index_pullback_support_score"] = 90.0
        strong.loc[index[-1], "index_pullback_rsi_score"] = 80.0
        strong.loc[index[-1], "index_pullback_decline_score"] = 70.0
        strong.loc[index[-1], "index_pullback_trend_score"] = 85.0

        weak_score = score_buy_index_shallow_pullback(weak, cfg).iloc[-1]
        strong_score = score_buy_index_shallow_pullback(strong, cfg).iloc[-1]

        self.assertGreater(strong_score, weak_score + 45)

    def test_long_term_radar_labels_shallow_pullback_differently_from_bottom_reversal(self) -> None:
        cfg = make_cfg()
        cfg.buy_strategy = "index_shallow_pullback"
        cfg.buy_threshold = 40
        index = pd.bdate_range("2020-01-01", periods=620)
        close = pd.Series(100.0, index=index)
        close.iloc[252] = 130.0
        close.iloc[504] = 170.0
        close = close.interpolate()
        df = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
                "index_pullback_support_score": 80.0,
                "index_pullback_rsi_score": 75.0,
            },
            index=index,
        )
        for pos in [0, 80, 160]:
            df.loc[index[pos], "buy_score"] = 55.0

        result = evaluate_long_term_radar(df, cfg)
        label = result["signals"][0]["strengthLabel"]

        self.assertTrue(label.startswith("Shallow Pullback"))
        self.assertNotIn("Deep Bottom", label)
        self.assertEqual(label, classify_addon_signal(df, 0, cfg, 55.0))

    def test_index_shallow_pullback_can_resignal_when_drawdown_deepens(self) -> None:
        cfg = make_cfg()
        cfg.buy_strategy = "index_shallow_pullback"
        cfg.buy_threshold = 50
        index = pd.bdate_range("2020-01-01", periods=620)
        close = pd.Series(100.0, index=index)
        close.iloc[252] = 130.0
        close.iloc[504] = 170.0
        close = close.interpolate()
        df = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
                "drawdown_252": 0.0,
            },
            index=index,
        )
        df.loc[index[0], ["buy_score", "drawdown_252"]] = [55.0, -5.0]
        df.loc[index[20], ["buy_score", "drawdown_252"]] = [55.0, -6.0]
        df.loc[index[30], ["buy_score", "drawdown_252"]] = [55.0, -10.0]

        result = evaluate_long_term_radar(df, cfg)

        self.assertEqual([s["date"] for s in result["signals"]], ["2020-01-01", "2020-02-12"])

    def test_summarize_radar_subset_averages_tech_stock_metrics(self) -> None:
        per_symbol = {
            "AAPL": {
                "config": {"buy_strategy": "bottom_reversal"},
                "signalCount": 4,
                "avgForwardReturns": {"avg6mPct": 10.0, "avg12mPct": 20.0, "avg24mPct": 30.0},
                "avgDrawdowns": {"avgMaxDrawdown12mPct": -8.0},
            },
            "NVDA": {
                "config": {"buy_strategy": "index_shallow_pullback"},
                "signalCount": 6,
                "avgForwardReturns": {"avg6mPct": 30.0, "avg12mPct": 60.0, "avg24mPct": 90.0},
                "avgDrawdowns": {"avgMaxDrawdown12mPct": -12.0},
            },
            "JPM": {
                "config": {"buy_strategy": "bottom_reversal"},
                "signalCount": 20,
                "avgForwardReturns": {"avg6mPct": 1.0, "avg12mPct": 2.0, "avg24mPct": 3.0},
                "avgDrawdowns": {"avgMaxDrawdown12mPct": -2.0},
            },
        }

        summary = summarize_radar_subset(per_symbol, ["AAPL", "NVDA"])

        self.assertEqual(summary["symbolCount"], 2)
        self.assertEqual(summary["avgSignals"], 5.0)
        self.assertEqual(summary["avg12mPct"], 40.0)
        self.assertEqual(summary["median12mPct"], 40.0)
        self.assertEqual(summary["avgMaxDrawdown12mPct"], -10.0)
        self.assertEqual(summary["strategyCounts"], {"bottom_reversal": 1, "index_shallow_pullback": 1})

    def test_summarize_radar_segments_splits_large_cap_and_high_beta_tech(self) -> None:
        per_symbol = {
            "AAPL": {
                "config": {"buy_strategy": "bottom_reversal"},
                "signalCount": 4,
                "avgForwardReturns": {"avg6mPct": 10.0, "avg12mPct": 20.0, "avg24mPct": 30.0},
                "avgDrawdowns": {"avgMaxDrawdown12mPct": -8.0},
            },
            "NVDA": {
                "config": {"buy_strategy": "bottom_reversal"},
                "signalCount": 8,
                "avgForwardReturns": {"avg6mPct": 40.0, "avg12mPct": 80.0, "avg24mPct": 120.0},
                "avgDrawdowns": {"avgMaxDrawdown12mPct": -18.0},
            },
        }

        summary = summarize_radar_segments(
            per_symbol,
            {
                "large_cap_quality_tech": ["AAPL"],
                "high_beta_tech": ["NVDA"],
            },
        )

        self.assertEqual(summary["large_cap_quality_tech"]["avg12mPct"], 20.0)
        self.assertEqual(summary["high_beta_tech"]["avg12mPct"], 80.0)

    def test_summarize_signal_window_filters_by_date_and_maturity(self) -> None:
        per_symbol = {
            "AAPL": {
                "signals": [
                    {"date": "2021-01-01", "return12mPct": 10.0, "return24mPct": 20.0, "maxDrawdown12mPct": -5.0},
                    {"date": "2024-01-01", "return12mPct": 30.0, "return24mPct": None, "maxDrawdown12mPct": -8.0},
                ],
            },
            "NVDA": {
                "signals": [
                    {"date": "2024-02-01", "return12mPct": None, "return24mPct": None, "maxDrawdown12mPct": -12.0},
                ],
            },
        }

        summary = summarize_signal_window(per_symbol, ["AAPL", "NVDA"], start_date="2023-01-01")

        self.assertEqual(summary["signalCount"], 2)
        self.assertEqual(summary["mature12mSignalCount"], 1)
        self.assertEqual(summary["avg12mPct"], 30.0)
        self.assertEqual(summary["avgMaxDrawdown12mPct"], -10.0)

    def test_summarize_signal_window_uses_none_when_returns_are_not_mature(self) -> None:
        per_symbol = {
            "AAPL": {
                "signals": [
                    {"date": "2026-01-01", "return6mPct": None, "return12mPct": None, "maxDrawdown12mPct": -8.0},
                ],
            },
        }

        summary = summarize_signal_window(per_symbol, ["AAPL"], start_date="2026-01-01")

        self.assertEqual(summary["signalCount"], 1)
        self.assertEqual(summary["mature6mSignalCount"], 0)
        self.assertEqual(summary["mature12mSignalCount"], 0)
        self.assertIsNone(summary["avg6mPct"])
        self.assertIsNone(summary["avg12mPct"])
        self.assertEqual(summary["avgMaxDrawdown12mPct"], -8.0)

    def test_symbol_average_and_signal_level_summaries_use_different_weighting(self) -> None:
        per_symbol = {
            "AAPL": {
                "config": {"buy_strategy": "bottom_reversal"},
                "signalCount": 1,
                "avgForwardReturns": {"avg6mPct": 5.0, "avg12mPct": 10.0, "avg24mPct": 15.0},
                "avgDrawdowns": {"avgMaxDrawdown12mPct": -4.0},
                "signals": [
                    {"date": "2024-01-01", "return12mPct": 10.0, "maxDrawdown12mPct": -4.0},
                ],
            },
            "NVDA": {
                "config": {"buy_strategy": "bottom_reversal"},
                "signalCount": 3,
                "avgForwardReturns": {"avg6mPct": 20.0, "avg12mPct": 40.0, "avg24mPct": 60.0},
                "avgDrawdowns": {"avgMaxDrawdown12mPct": -10.0},
                "signals": [
                    {"date": "2024-01-01", "return12mPct": 40.0, "maxDrawdown12mPct": -10.0},
                    {"date": "2024-02-01", "return12mPct": 40.0, "maxDrawdown12mPct": -10.0},
                    {"date": "2024-03-01", "return12mPct": 40.0, "maxDrawdown12mPct": -10.0},
                ],
            },
        }

        symbol_average = summarize_radar_subset(per_symbol, ["AAPL", "NVDA"])
        signal_level = summarize_signal_window(per_symbol, ["AAPL", "NVDA"], start_date="2023-01-01")

        self.assertEqual(symbol_average["avg12mPct"], 25.0)
        self.assertEqual(signal_level["avg12mPct"], 32.5)

    def test_summarize_signal_years_groups_signals_by_calendar_year(self) -> None:
        per_symbol = {
            "AAPL": {
                "signals": [
                    {"date": "2023-01-10", "return12mPct": 10.0, "maxDrawdown12mPct": -5.0},
                    {"date": "2024-03-10", "return12mPct": 30.0, "maxDrawdown12mPct": -8.0},
                ],
            },
            "NVDA": {
                "signals": [
                    {"date": "2024-05-10", "return12mPct": None, "maxDrawdown12mPct": -12.0},
                ],
            },
        }

        summary = summarize_signal_years(per_symbol, ["AAPL", "NVDA"], start_year=2023)

        self.assertEqual(summary["2023"]["signalCount"], 1)
        self.assertEqual(summary["2023"]["avg12mPct"], 10.0)
        self.assertEqual(summary["2024"]["signalCount"], 2)
        self.assertEqual(summary["2024"]["mature12mSignalCount"], 1)
        self.assertEqual(summary["2024"]["avgMaxDrawdown12mPct"], -10.0)

    def test_summarize_signal_risk_diagnostics_groups_flags_and_strength(self) -> None:
        per_symbol = {
            "AAPL": {
                "signals": [
                    {
                        "date": "2024-01-10",
                        "strengthLabel": "Deep Bottom - Strong",
                        "return12mPct": 20.0,
                        "maxDrawdown12mPct": -6.0,
                        "actionProfile": {"riskFlags": []},
                    },
                    {
                        "date": "2024-02-10",
                        "strengthLabel": "Deep Bottom - Medium",
                        "return12mPct": -5.0,
                        "maxDrawdown12mPct": -22.0,
                        "actionProfile": {"riskFlags": ["weak_rsi_divergence"]},
                    },
                ],
            },
            "NVDA": {
                "signals": [
                    {
                        "date": "2022-01-10",
                        "strengthLabel": "Deep Bottom - Medium",
                        "return12mPct": 30.0,
                        "maxDrawdown12mPct": -10.0,
                        "actionProfile": {"riskFlags": ["weak_rsi_divergence", "weak_bottom_retest"]},
                    },
                ],
            },
        }

        summary = summarize_signal_risk_diagnostics(
            per_symbol,
            ["AAPL", "NVDA"],
            start_date="2023-01-01",
        )

        self.assertEqual(summary["signalCount"], 2)
        self.assertEqual(summary["riskFlagGroups"]["no_risk_flags"]["signalCount"], 1)
        self.assertEqual(summary["riskFlagGroups"]["weak_rsi_divergence"]["avg12mPct"], -5.0)
        self.assertEqual(summary["riskFlagGroups"]["weak_rsi_divergence"]["avgMaxDrawdown12mPct"], -22.0)
        self.assertEqual(summary["strengthGroups"]["Deep Bottom - Strong"]["avg12mPct"], 20.0)
        self.assertEqual(summary["strengthGroups"]["Deep Bottom - Medium"]["signalCount"], 1)

    def test_summarize_recent_signal_log_returns_latest_signals(self) -> None:
        per_symbol = {
            "AAPL": {
                "signals": [
                    {"date": "2024-01-10", "buyScore": 51.0, "strengthLabel": "Deep Bottom - Medium"},
                    {"date": "2025-04-10", "buyScore": 60.0, "strengthLabel": "Deep Bottom - Strong"},
                ],
            },
            "NVDA": {
                "signals": [
                    {"date": "2025-02-10", "buyScore": 55.0, "strengthLabel": "Shallow Pullback - Medium"},
                ],
            },
        }

        recent = summarize_recent_signal_log(per_symbol, ["AAPL", "NVDA"], limit=2)

        self.assertEqual([row["symbol"] for row in recent], ["AAPL", "NVDA"])
        self.assertEqual([row["date"] for row in recent], ["2025-04-10", "2025-02-10"])
        self.assertEqual(recent[0]["strengthLabel"], "Deep Bottom - Strong")

    def test_summarize_active_signal_log_filters_recent_watchlist(self) -> None:
        per_symbol = {
            "AAPL": {
                "signals": [
                    {"date": "2025-01-10", "barsSinceSignal": 140, "strengthLabel": "Deep Bottom - Medium"},
                    {"date": "2026-01-10", "barsSinceSignal": 40, "strengthLabel": "Deep Bottom - Strong"},
                ],
            },
            "NVDA": {
                "signals": [
                    {"date": "2026-02-10", "barsSinceSignal": 20, "strengthLabel": "Deep Bottom - Medium"},
                ],
            },
        }

        active = summarize_active_signal_log(per_symbol, ["AAPL", "NVDA"], max_age_bars=126)

        self.assertEqual([row["symbol"] for row in active], ["NVDA", "AAPL"])
        self.assertEqual([row["date"] for row in active], ["2026-02-10", "2026-01-10"])

    def test_build_paper_tracking_plan_adds_future_check_dates(self) -> None:
        signals = [
            {
                "symbol": "AAPL",
                "date": "2026-01-01",
                "price": 100.0,
                "strengthLabel": "Deep Bottom - Strong",
                "return6mPct": None,
                "return12mPct": None,
                "maxDrawdown12mPct": -5.0,
                "actionProfile": {"grade": "Strong Add-On Candidate", "riskFlags": []},
            },
            {
                "symbol": "NVDA",
                "date": "2025-01-01",
                "price": 120.0,
                "strengthLabel": "Deep Bottom - Medium",
                "return6mPct": 20.0,
                "return12mPct": None,
                "maxDrawdown12mPct": -12.0,
                "actionProfile": {"grade": "Medium Add-On Candidate", "riskFlags": ["no_volume_expansion"]},
            },
        ]

        plan = build_paper_tracking_plan(signals, generated_at="2026-05-13T00:00:00")

        self.assertEqual(plan["generatedDate"], "2026-05-13")
        self.assertEqual(plan["signalCount"], 2)
        self.assertEqual(plan["pending6mCount"], 1)
        self.assertEqual(plan["pending12mCount"], 2)
        self.assertEqual(plan["overduePending6mCount"], 0)
        self.assertEqual(plan["overduePending12mCount"], 1)
        self.assertEqual(plan["nextPending6mDate"], "2026-07-03")
        self.assertEqual(plan["nextPending12mDate"], "2026-01-01")
        self.assertEqual(plan["nextPendingCheckDate"], "2026-01-01")
        self.assertEqual(plan["signals"][0]["symbol"], "AAPL")
        self.assertEqual(plan["signals"][0]["check6mDate"], "2026-07-03")
        self.assertEqual(plan["signals"][0]["check12mDate"], "2027-01-01")
        self.assertEqual(plan["signals"][0]["status6m"], "pending")
        self.assertEqual(plan["signals"][1]["status6m"], "mature")

    def test_format_paper_tracking_status_summarizes_next_check(self) -> None:
        results = {
            "paperTrackingPlan": {
                "generatedDate": "2026-05-13",
                "signalCount": 2,
                "pending6mCount": 1,
                "pending12mCount": 2,
                "overduePending6mCount": 0,
                "overduePending12mCount": 1,
                "nextPendingCheckDate": "2026-05-19",
                "signals": [
                    {
                        "symbol": "CRM",
                        "signalDate": "2025-11-17",
                        "strengthLabel": "Deep Bottom - Strong",
                        "action": "Strong Add-On Candidate",
                        "riskFlags": ["no_volume_expansion"],
                        "check6mDate": "2026-05-19",
                        "check12mDate": "2026-11-17",
                        "status6m": "pending",
                        "status12m": "pending",
                    }
                ],
            }
        }

        status = format_paper_tracking_status(results, as_of_date="2026-05-20")

        self.assertIn("As-of date: 2026-05-20", status)
        self.assertIn("Next pending check date: 2026-05-19", status)
        self.assertIn("Overdue pending checks: 6m=1, 12m=0", status)
        self.assertIn("CRM | signal=2025-11-17 | 6m=2026-05-19 overdue", status)

    def test_long_term_radar_signal_includes_factor_snapshot(self) -> None:
        cfg = make_cfg()
        cfg.buy_strategy = "bottom_reversal"
        cfg.buy_threshold = 50
        index = pd.bdate_range("2024-01-01", periods=260)
        close = pd.Series([100.0 + i * 0.1 for i in range(len(index))], index=index)
        df = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
                "drawdown_252": -28.4,
                "bottom_retest_score": 82.0,
                "rsi_divergence_score": 76.0,
                "crash_score": 64.0,
                "capitulation_score": 58.0,
                "rsi14": 31.0,
                "vol_ratio": 1.7,
            },
            index=index,
        )
        df.loc[index[0], "buy_score"] = 90.0

        result = evaluate_long_term_radar(df, cfg)

        snapshot = result["signals"][0]["factorSnapshot"]
        self.assertEqual(snapshot["strategy"], "bottom_reversal")
        self.assertEqual(snapshot["drawdown252Pct"], -28.4)
        self.assertEqual(snapshot["bottomRetestScore"], 82.0)
        self.assertEqual(snapshot["rsiDivergenceScore"], 76.0)
        action = result["signals"][0]["actionProfile"]
        self.assertEqual(action["grade"], "Strong Add-On Candidate")
        self.assertIn("deep_drawdown", action["confirmations"])

    def test_select_freeze_candidate_entries_deduplicates_configs(self) -> None:
        broad = {
            "config": {"name": "btm", "buy_strategy": "bottom_reversal"},
            "combinedScore": 90.0,
        }
        strategy_best = {
            "bottom_reversal": broad,
            "tech_breakout": {
                "config": {"name": "tb", "buy_strategy": "tech_breakout"},
                "combinedScore": 60.0,
            },
        }
        date_split = {"trainedDefault": broad}

        entries = select_freeze_candidate_entries(broad, date_split, strategy_best)

        self.assertEqual([entry["name"] for entry in entries], ["btm", "tb"])
        self.assertEqual(entries[0]["reason"], "Broad default")
        self.assertEqual(entries[1]["reason"], "Best tech-breakout family")

    def test_restricted_walk_forward_selects_from_frozen_candidates(self) -> None:
        cfg = make_cfg()
        cfg.name = "loose"
        cfg.buy_threshold = 50
        strict = make_cfg()
        strict.name = "strict"
        strict.buy_threshold = 80
        index = pd.bdate_range("2020-01-01", periods=1100)
        close = pd.Series(100.0, index=index)
        close.iloc[252] = 130.0
        close.iloc[504] = 180.0
        close.iloc[756] = 230.0
        close.iloc[1008] = 260.0
        close = close.interpolate()
        base = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        for date in ["2020-01-02", "2020-04-02", "2020-07-02", "2023-03-02"]:
            base.loc[pd.Timestamp(date), "buy_score"] = 90.0

        result = evaluate_restricted_walk_forward(
            {"QQQ": base, "SPY": base, "AAPL": base},
            ["QQQ", "SPY"],
            ["AAPL"],
            [
                {"reason": "Loose candidate", "name": cfg.name, "config": cfg.__dict__},
                {"reason": "Strict candidate", "name": strict.name, "config": strict.__dict__},
            ],
            years=[2023],
        )

        row = result["years"][0]
        self.assertEqual(row["year"], 2023)
        self.assertIn(row["selectedConfig"]["name"], {"loose", "strict"})
        self.assertEqual(row["techSignalSummary"]["signalCount"], 1)
        self.assertEqual(row["techHoldoutSummary"]["symbolCount"], 1)

    def test_full_grid_walk_forward_reranks_all_configs(self) -> None:
        loose = make_cfg()
        loose.name = "loose"
        loose.buy_threshold = 50
        strict = make_cfg()
        strict.name = "strict"
        strict.buy_threshold = 80
        index = pd.bdate_range("2020-01-01", periods=1100)
        close = pd.Series(100.0, index=index)
        close.iloc[252] = 130.0
        close.iloc[504] = 180.0
        close.iloc[756] = 230.0
        close.iloc[1008] = 260.0
        close = close.interpolate()
        base = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        for date in ["2020-01-02", "2020-04-02", "2020-07-02", "2023-03-02"]:
            base.loc[pd.Timestamp(date), "buy_score"] = 90.0

        result = evaluate_full_grid_walk_forward(
            {"QQQ": base, "SPY": base, "AAPL": base},
            ["QQQ", "SPY"],
            ["AAPL"],
            [loose, strict],
            years=[2023],
        )

        row = result["years"][0]
        self.assertEqual(result["configCount"], 2)
        self.assertEqual(row["year"], 2023)
        self.assertIn(row["selectedConfig"]["name"], {"loose", "strict"})
        self.assertEqual(len(row["trainTop5"]), 2)
        self.assertEqual(row["techSignalSummary"]["signalCount"], 1)

    def test_multi_window_validation_reports_anchored_and_rolling_windows(self) -> None:
        cfg = make_cfg()
        cfg.name = "btm"
        cfg.buy_threshold = 50
        index = pd.bdate_range("2020-01-01", periods=1300)
        close = pd.Series([100.0 + i * 0.1 for i in range(len(index))], index=index)
        base = pd.DataFrame(
            {
                "open": close + 1,
                "close": close,
                "buy_score": 0.0,
            },
            index=index,
        )
        for date in ["2021-03-01", "2022-03-01", "2023-03-01", "2024-03-01"]:
            base.loc[pd.Timestamp(date), "buy_score"] = 90.0

        result = evaluate_multi_window_validation(
            {"AAPL": base, "NVDA": base},
            ["AAPL", "NVDA"],
            cfg,
            anchored_start_years=[2022, 2023],
            rolling_windows=[("2022-01-01", "2023-12-31")],
        )

        self.assertEqual(result["config"]["name"], "btm")
        self.assertEqual([row["startDate"] for row in result["anchoredWindows"]], ["2022-01-01", "2023-01-01"])
        self.assertEqual(result["anchoredWindows"][0]["signalSummary"]["signalCount"], 6)
        self.assertEqual(result["rollingWindows"][0]["label"], "2022-01-01 to 2023-12-31")
        self.assertEqual(result["rollingWindows"][0]["signalSummary"]["signalCount"], 4)
        self.assertEqual(result["summary"]["windowCount"], 3)
        self.assertEqual(result["summary"]["totalSignals"], 14)
        self.assertEqual(result["summary"]["windowsWithPositiveAvg12m"], 3)
        self.assertIn("worstSignalDrawdown12mPct", result["summary"])

    def test_generated_pine_uses_compatible_rolling_count_helper(self) -> None:
        pine = generate_pine_script(make_cfg())

        self.assertIn("rolling_count(", pine)
        self.assertNotIn("ta.sum", pine)
        self.assertNotIn("math.sum", pine)
        self.assertTrue(pine.isascii())

    def test_standalone_long_term_pine_matches_current_radar_defaults(self) -> None:
        import json

        pine = (LONG_TERM_ADDON_DIR / "long_term_addon_radar.pine").read_text(encoding="utf-8")
        results = json.loads((UPTREND_DIP_DIR / "uptrend_dip_results.json").read_text(encoding="utf-8"))
        radar = results["longTermRadar"]
        bottom_cfg = UptrendDipConfig(**radar["recommendedDefault"]["config"])
        best_by_strategy = radar["bestByStrategy"]
        index_cfg = UptrendDipConfig(**best_by_strategy["index_shallow_pullback"]["config"])
        rsi_cfg = UptrendDipConfig(**best_by_strategy["rsi_divergence"]["config"])
        generated = generate_long_term_addon_pine_script(bottom_cfg, index_cfg, rsi_cfg)

        self.assertEqual(pine, generated)
        self.assertIn('radar_mode = input.string("bottom_reversal"', pine)
        self.assertIn(f"bottom_threshold = input.float({bottom_cfg.buy_threshold:.0f}", pine)
        self.assertIn(f"rsi_threshold = input.float({rsi_cfg.buy_threshold:.0f}", pine)
        self.assertIn(f"index_threshold = input.float({index_cfg.buy_threshold:.0f}", pine)
        self.assertIn("rolling_count(", pine)
        self.assertIn("bearish_candle = close < open", pine)
        self.assertIn("BTM STRONG", pine)
        self.assertIn("RSI DIV STRONG", pine)
        self.assertIn("IDX STRONG", pine)
        self.assertNotIn("ta.sum", pine)
        self.assertNotIn("math.sum", pine)
        self.assertTrue(pine.isascii())

    def test_standalone_long_term_pine_uses_supplied_config_defaults(self) -> None:
        bottom_cfg = make_cfg()
        bottom_cfg.buy_strategy = "bottom_reversal"
        bottom_cfg.buy_threshold = 50
        bottom_cfg.w_pb_trend = 0.25
        index_cfg = make_cfg()
        index_cfg.buy_strategy = "index_shallow_pullback"
        index_cfg.buy_threshold = 60
        index_cfg.w_pb_level = 0.30

        pine = generate_long_term_addon_pine_script(bottom_cfg, index_cfg)

        self.assertIn('bottom_threshold = input.float(50', pine)
        self.assertIn('index_threshold = input.float(60', pine)
        self.assertIn('"rsi_divergence"', pine)
        self.assertIn('w_drawdown = input.float(0.25', pine)
        self.assertIn('w_idx_support = input.float(0.30', pine)
        self.assertIn("{{ticker}}", pine)

    def test_generated_pine_exposes_rsi_divergence_strategy(self) -> None:
        cfg = make_cfg()
        cfg.buy_strategy = "rsi_divergence"

        pine = generate_pine_script(cfg)

        self.assertIn('"rsi_divergence"', pine)
        self.assertIn("buy_rsi_divergence", pine)
        self.assertIn("RSI DIV", pine)

    def test_report_directs_long_term_users_to_standalone_pine(self) -> None:
        report = (UPTREND_DIP_DIR / "uptrend_dip_report.md").read_text(encoding="utf-8")

        self.assertIn(
            "Use `long_term_addon_radar.pine` for the long-term add-on radar",
            report,
        )
        self.assertIn(
            "Use `uptrend_dip_pine.pine` only when you want the fuller buy/sell comparison",
            report,
        )
        self.assertNotIn(
            "Use the generated default as the broad long-term add-on radar",
            report,
        )
        self.assertIn("Prompt-To-Artifact Checklist", report)
        self.assertIn("Multi-Window Validation", report)
        self.assertIn("Positive 12m windows", report)
        self.assertIn("Drivers", report)
        self.assertIn("Risk Flags", report)
        self.assertIn("Tech Signal Risk Diagnostics", report)
        self.assertIn("Paper Tracking Plan", report)
        self.assertIn("--paper-status --as-of", report)

    def test_results_json_exposes_long_term_addon_pine_path(self) -> None:
        import json

        results = json.loads((UPTREND_DIP_DIR / "uptrend_dip_results.json").read_text(encoding="utf-8"))

        self.assertTrue(str(results.get("pineScript", "")).endswith("uptrend_dip_pine.pine"))
        self.assertTrue(
            str(results.get("longTermAddonPineScript", "")).endswith("long_term_addon_radar.pine")
        )
        self.assertTrue(results.get("promptToArtifactChecklist"))
        self.assertTrue(results.get("multiWindowValidationRadar"))

    def test_prompt_to_artifact_checklist_maps_core_requirements(self) -> None:
        results = {
            "longTermRadar": {
                "recommendedDefault": {
                    "config": {
                        "buy_strategy": "bottom_reversal",
                        "name": "btm_test",
                    }
                },
                "bestByStrategy": {
                    "tech_breakout": {},
                    "trend_breakout": {},
                    "bottom_reversal": {},
                    "index_shallow_pullback": {},
                },
            },
            "techSubsetRecommendedRadarSummary": {"symbolCount": 12},
            "dateSplitRadar": {"holdoutSignalStartDate": "2023-01-01"},
            "fullGridWalkForwardRadar": {"years": [{"year": 2023}]},
            "techSubsetCurrentSignalLog": [{"symbol": "QQQ"}],
            "paperTrackingPlan": {
                "signalCount": 1,
                "nextPendingCheckDate": "2026-05-19",
                "overduePending6mCount": 0,
                "overduePending12mCount": 0,
            },
            "pineScript": str(UPTREND_DIP_DIR / "uptrend_dip_pine.pine"),
            "longTermAddonPineScript": str(LONG_TERM_ADDON_DIR / "long_term_addon_radar.pine"),
        }

        checklist = build_prompt_to_artifact_checklist(results)

        joined_requirements = "\n".join(item["requirement"] for item in checklist)
        self.assertIn("Do not modify config.py or run.py", joined_requirements)
        self.assertIn("Explore buy signals", joined_requirements)
        self.assertIn("Keep TradingView Pine output synchronized", joined_requirements)
        self.assertIn("Track future paper-validation checkpoints", joined_requirements)
        self.assertTrue(any(item["status"] == "external gate" for item in checklist))


if __name__ == "__main__":
    unittest.main()
