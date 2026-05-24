import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from investigations.bottom_signal_search import (
    BottomSignalConfig,
    SearchSettings,
    build_indicator_spec,
    candidate_configs,
    classify_bottom_signal,
    collect_indicator_spec,
    load_search_settings,
    precompute_indicator_frames,
    generate_mb_factor_ablation_csv,
    generate_next_actions_csv,
    generate_strategy_iteration_review_csv,
    generate_strategy_iteration_review_report,
    generate_plan_summary,
    generate_recent_validation_csv,
    generate_rs_watchlist_candidate_csv,
    generate_rs_watchlist_report,
    generate_rs_watchlist_ticker_csv,
    generate_2022_2026_candidate_review_csv,
    generate_2022_2026_miss_diagnostics_csv,
    generate_2022_2026_miss_diagnostics_report,
    generate_pine_script,
    generate_rs_watchlist_pine_script,
    generate_merged_observation_pine_script,
    generate_observation_report,
    generate_observation_signals_csv,
    add_relative_strength_scores,
    score_from_indicators,
    search_observation_channel,
    select_dual_track_positions,
    summarize_signal_funnel,
    apply_watch_medium_ratio_gate,
    apply_relative_strength_capture_preference,
    selected_signal_rows,
    sparse_count_score,
    validation_coverage_score,
    apply_validation_coverage_gate,
    apply_signal_count_gate,
    filter_positions_by_market_context,
    forward_win_rate,
    promoted_stage_names,
    adverse_tail_rate,
    market_repair_score,
    summarize_validation_groups,
    summarize_date_split_validation,
    date_split_coverage_score,
    apply_date_split_gate,
    summarize_validation_windows,
    validation_window_coverage_score,
    apply_validation_window_gate,
    apply_validation_window_quality_gate,
    run_walk_forward_diagnostics,
    build_mb_factor_ablation_configs,
    local_bottom_gap,
    bottom_capture_score,
    apply_bottom_capture_gate,
    relaxed_stage_settings,
    refine_promoted_configs,
    apply_baseline_quality_preference,
    apply_recent_rs_activity_preference,
    apply_qualified_rs_watchlist_preference,
    mb_entry_threshold,
    summarize_recent_channel_activity,
    summarize_mb_factor_ablation,
    rs_candidate_quality_score,
    rs_ticker_action_reason,
    rs_ticker_action_tier,
    rs_ticker_action_counts,
    rs_selection_score,
    summarize_rs_candidate_watchlist,
    rank_rs_ticker_summary,
    summarize_rs_ticker_watchlist,
    summarize_recent_validation,
    refresh_supplemental_analysis,
    refresh_best_rs_watchlist_scan,
    select_best_rs_watchlist_result,
    top_rs_coverage_tradeoffs,
    _evaluate_configs_for_symbols,
    resolve_output_paths,
    resolve_results_path,
    parse_args,
    run_search,
    rs_entry_threshold,
    sanitize_research_tag,
)
from investigations.bottom_signal_paths import (
    CATALOG_DIR,
    DEFAULT_CONFIG_PATH,
    FORMAL_STRATEGY_DIR,
    OBSERVATION_ADDON_DIR,
    RESEARCH_2022_2026_DIR,
    RESULTS_PATH,
    MERGED_OBSERVATION_PINE_PATH,
    MISS_DIAGNOSTICS_REPORT_PATH,
    STRICT_FORMAL_PINE_PATH,
)


def fake_parallel_precomputer(symbols, configs, cache_enabled=True):
    return {symbol: pd.DataFrame({"Close": [1.0, 2.0]}) for symbol in symbols}


def fake_parallel_evaluator(
    symbols,
    config,
    indicator_frames=None,
    objective_weights=None,
    validation=None,
):
    score = float(config.drawdown_window)
    return {
        "config": {"name": config.name},
        "metrics": {"compositeScore": score, "signalCount": int(score)},
        "symbols": list(symbols),
        "signals": [],
        "rsCandidateWatchlist": {},
    }


class FakeProcessPoolExecutor:
    def __init__(self, max_workers=None, initializer=None, initargs=()):
        self.max_workers = max_workers
        if initializer is not None:
            initializer(*initargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def map(self, fn, items):
        return [fn(item) for item in reversed(list(items))]


def indicator_frame() -> pd.DataFrame:
    cfg = BottomSignalConfig(
        name="test_cfg",
        drawdown_window=42,
        drawdown_threshold=-12,
        rsi_period=7,
        stoch_period=9,
        stoch_smooth=3,
        macd_fast=8,
        macd_slow=21,
        macd_signal=5,
        ma_period=150,
        atr_period=10,
        volume_window=10,
    )
    index = pd.date_range("2024-01-01", periods=4, freq="D")
    return pd.DataFrame(
        {
            "Open": [100.0, 94.0, 84.0, 82.0],
            "High": [101.0, 95.0, 86.0, 87.0],
            "Low": [99.0, 91.0, 79.0, 80.0],
            "Close": [100.0, 92.0, 81.0, 86.0],
            "Volume": [1_000_000, 950_000, 1_400_000, 1_600_000],
            "drawdown_42": [-2.0, -8.0, -28.0, -22.0],
            "rsi_7": [58.0, 45.0, 24.0, 31.0],
            "stoch_9_3": [62.0, 36.0, 12.0, 24.0],
            "macd_diff_8_21_5": [-0.2, -0.3, -0.1, 0.4],
            "dist_sma_150": [3.0, -4.0, -24.0, -18.0],
            "atr_10": [2.0, 2.5, 5.0, 4.5],
            "volume_ratio_10": [0.8, 0.9, 1.4, 1.7],
            "bb_upper_10_2": [105.0, 101.0, 95.0, 94.0],
        },
        index=index,
    )


class BottomSignalSearchTest(unittest.TestCase):
    def test_workers_default_to_serial(self) -> None:
        with patch("sys.argv", ["bottom_signal_search.py"]):
            args = parse_args()

        self.assertEqual(args.workers, 1)

    def test_cli_accepts_workers_argument(self) -> None:
        with patch("sys.argv", ["bottom_signal_search.py", "--workers", "4"]):
            args = parse_args()

        self.assertEqual(args.workers, 4)

    def test_research_tag_routes_outputs_without_overwriting_main_results(self) -> None:
        with patch(
            "sys.argv",
            ["bottom_signal_search.py", "--research-tag", "2022_2026_miss_search"],
        ):
            args = parse_args()

        self.assertEqual(args.research_tag, "2022_2026_miss_search")
        self.assertEqual(sanitize_research_tag("2022_2026_miss_search"), "2022_2026_miss_search")
        with self.assertRaises(ValueError):
            sanitize_research_tag("../bad")

        default_paths = resolve_output_paths("")
        research_paths = resolve_output_paths("2022_2026_miss_search")

        self.assertEqual(default_paths["results"].name, "bottom_signal_results.json")
        self.assertEqual(
            research_paths["results"].name,
            "bottom_signal_results_2022_2026_miss_search.json",
        )
        self.assertNotEqual(research_paths["results"], default_paths["results"])
        self.assertEqual(
            research_paths["report"].name,
            "bottom_signal_report_2022_2026_miss_search.md",
        )
        self.assertEqual(resolve_results_path("").name, "bottom_signal_results.json")
        self.assertEqual(
            resolve_results_path("2022_2026_miss_search").name,
            "bottom_signal_results_2022_2026_miss_search.json",
        )

    def test_bottom_signal_outputs_live_in_strategy_catalog(self) -> None:
        self.assertEqual(CATALOG_DIR.name, "strategy_catalog")
        self.assertEqual(FORMAL_STRATEGY_DIR.name, "bottom_signal_formal")
        self.assertEqual(OBSERVATION_ADDON_DIR.name, "bottom_signal_observation_addon")
        self.assertEqual(RESEARCH_2022_2026_DIR.name, "bottom_signal_2022_2026_research")
        self.assertEqual(RESULTS_PATH.parent, FORMAL_STRATEGY_DIR)
        self.assertEqual(STRICT_FORMAL_PINE_PATH.parent, FORMAL_STRATEGY_DIR)
        self.assertEqual(MERGED_OBSERVATION_PINE_PATH.parent, OBSERVATION_ADDON_DIR)
        self.assertEqual(MISS_DIAGNOSTICS_REPORT_PATH.parent, RESEARCH_2022_2026_DIR)

        tagged = resolve_output_paths("2022_2026_miss_search")

        self.assertEqual(tagged["results"].parent, RESEARCH_2022_2026_DIR)
        self.assertEqual(tagged["pine"].parent, RESEARCH_2022_2026_DIR)
        self.assertEqual(tagged["merged_observation_pine"].parent, RESEARCH_2022_2026_DIR)

    def test_2022_2026_miss_diagnostics_explain_formal_absence(self) -> None:
        payload = {
            "bestConfig": {
                "name": "seed_previous_rs_higher_low_best",
                "entry_threshold": 82,
                "mb_entry_offset": 0,
            },
            "results": [
                {
                    "config": {"name": "seed_previous_rs_higher_low_best"},
                    "signals": [
                        {"symbol": "AAPL", "date": "2022-10-13", "bottomScore": 90},
                    ],
                    "diagnosticSignals": [
                        {
                            "symbol": "QQQ",
                            "date": "2022-10-11",
                            "channel": "MB",
                            "tier": "Medium",
                            "bottomScore": 79,
                            "riskFlags": "no_repair",
                            "fwd126": 0.21,
                        },
                    ],
                    "metrics": {
                        "signalCount": 39,
                        "avgFwd126": 0.3924,
                        "winRate126": 0.7436,
                    },
                }
            ],
            "observationSearch": {
                "signals": [
                    {
                        "symbol": "QQQ",
                        "date": "2022-10-03",
                        "observationType": "OBS-D",
                        "bottomScore": 68,
                        "riskFlags": "",
                        "fwd126": 0.17,
                    },
                    {
                        "symbol": "QQQ",
                        "date": "2026-03-27",
                        "observationType": "OBS-S",
                        "bottomScore": 71,
                        "riskFlags": "no_repair",
                        "fwd126": None,
                    },
                ]
            },
        }

        report = generate_2022_2026_miss_diagnostics_report(payload)
        csv_text = generate_2022_2026_miss_diagnostics_csv(payload)

        self.assertIn("# 2022/2026 Missing Formal Signal Diagnostics", report)
        self.assertIn("Formal MB Strong means the actual strategy buy signal", report)
        self.assertIn("OBS means candidate/watch only", report)
        self.assertIn("QQQ 2022 Q4", report)
        self.assertIn("QQQ 2026 March", report)
        self.assertIn("formal signals: 0", report)
        self.assertIn("observation signals: 1", report)
        self.assertIn("bottom=68 threshold=82 gap=14 risk=none", report)
        self.assertIn("bottom=71 threshold=82 gap=11 risk=no_repair", report)
        self.assertIn("score and repair quality were not high enough", report)
        self.assertIn("window,source,symbol,date,channel,tier,bottomScore,formalThreshold,scoreGap,riskFlags,fwd126,reasonBucket", csv_text)
        self.assertIn("QQQ 2022 Q4,observation,QQQ,2022-10-03,OBS-D,Observation,68,82,14,,0.17,below_formal_threshold", csv_text)
        self.assertIn("QQQ 2026 March,observation,QQQ,2026-03-27,OBS-S,Observation,71,82,11,no_repair,,below_formal_threshold", csv_text)

    def test_existing_results_review_lists_2022_2026_candidate_configs(self) -> None:
        payload = {
            "results": [
                {
                    "config": {"name": "baseline"},
                    "metrics": {
                        "signalCount": 39,
                        "avgFwd126": 0.39,
                        "winRate126": 0.74,
                        "coveredValidationWindowCount": 4,
                    },
                    "signals": [],
                    "diagnosticSignals": [
                        {"symbol": "QQQ", "date": "2022-10-11", "bottomScore": 79},
                    ],
                },
                {
                    "config": {"name": "candidate_hits_2026"},
                    "metrics": {
                        "signalCount": 38,
                        "avgFwd126": 0.35,
                        "winRate126": 0.70,
                        "coveredValidationWindowCount": 4,
                    },
                    "signals": [
                        {"symbol": "QQQ", "date": "2026-03-27", "bottomScore": 83},
                    ],
                    "diagnosticSignals": [],
                },
            ]
        }

        csv_text = generate_2022_2026_candidate_review_csv(payload)

        self.assertIn("configName,signalCount,avgFwd126,winRate126,coveredValidationWindowCount,formal2022Q4,formal2026March,diagnostic2022Q4,diagnostic2026March", csv_text)
        self.assertIn("baseline,39,0.39,0.74,4,0,0,1,0", csv_text)
        self.assertIn("candidate_hits_2026,38,0.35,0.7,4,0,1,0,0", csv_text)

    def test_parallel_config_evaluation_matches_serial_order_independent_results(self) -> None:
        settings = SearchSettings(
            max_configs=3,
            cache_indicators=False,
            search_stages={},
            candidate_parameters={},
            seed_configs=[],
            thresholds={},
            weights={},
            weight_profiles=[],
            objective_weights={},
            validation={},
        )
        configs = [
            BottomSignalConfig(name="cfg_low", drawdown_window=21),
            BottomSignalConfig(name="cfg_mid", drawdown_window=42),
            BottomSignalConfig(name="cfg_high", drawdown_window=63),
        ]

        serial = _evaluate_configs_for_symbols(
            ["QQQ"],
            configs,
            settings,
            workers=1,
            evaluator=fake_parallel_evaluator,
            indicator_precomputer=fake_parallel_precomputer,
        )
        parallel = _evaluate_configs_for_symbols(
            ["QQQ"],
            configs,
            settings,
            workers=2,
            evaluator=fake_parallel_evaluator,
            indicator_precomputer=fake_parallel_precomputer,
            executor_class=FakeProcessPoolExecutor,
        )

        serial_scores = {
            item["config"]["name"]: item["metrics"]["compositeScore"] for item in serial
        }
        parallel_scores = {
            item["config"]["name"]: item["metrics"]["compositeScore"] for item in parallel
        }
        self.assertEqual(serial_scores, parallel_scores)

    def test_run_search_passes_workers_to_stage_and_final_evaluation(self) -> None:
        settings = SearchSettings(
            max_configs=3,
            cache_indicators=False,
            search_stages={
                "enabled": True,
                "dev_symbols": ["QQQ"],
                "promote_top_n": 1,
                "refine_top_n": 0,
            },
            candidate_parameters={},
            seed_configs=[],
            thresholds={},
            weights={},
            weight_profiles=[],
            objective_weights={},
            validation={"enable_mb_factor_ablation": False},
        )
        calls = []

        def fake_runner(symbols, configs, settings, workers=1):
            calls.append((list(symbols), [config.name for config in configs], workers))
            return [
                {
                    "config": dict(config.__dict__),
                    "metrics": {"compositeScore": float(index + 1), "signalCount": index + 1},
                    "symbols": list(symbols),
                    "signals": [],
                    "rsCandidateWatchlist": {},
                }
                for index, config in enumerate(configs)
            ]

        run_search(
            ["QQQ", "SPY"],
            settings=settings,
            max_configs=3,
            workers=2,
            evaluation_runner=fake_runner,
        )

        self.assertEqual(calls[0][0], ["QQQ"])
        self.assertEqual(calls[0][2], 2)
        self.assertEqual(calls[1][0], ["QQQ", "SPY"])
        self.assertEqual(calls[1][2], 2)

    def test_run_search_marks_qqq_spy_sample_artifacts(self) -> None:
        settings = SearchSettings(
            max_configs=1,
            cache_indicators=False,
            search_stages={"enabled": False},
            candidate_parameters={},
            seed_configs=[],
            thresholds={},
            weights={},
            weight_profiles=[],
            objective_weights={},
            validation={"enable_mb_factor_ablation": False},
        )

        def fake_runner(symbols, configs, settings, workers=1):
            return [
                {
                    "config": dict(configs[0].__dict__),
                    "metrics": {
                        "compositeScore": 1.0,
                        "signalCount": 2,
                        "avgFwd126": -0.0432,
                    },
                    "symbols": list(symbols),
                    "signals": [],
                    "rsCandidateWatchlist": {},
                }
            ]

        payload = run_search(
            ["QQQ", "SPY"],
            settings=settings,
            max_configs=1,
            workers=1,
            evaluation_runner=fake_runner,
        )
        self.assertFalse(payload["artifactScope"]["fullPool"])
        self.assertEqual(payload["artifactScope"]["symbolCount"], 2)
        self.assertEqual(payload["artifactScope"]["sampleKind"], "QQQ_SPY_SAMPLE")
        self.assertIn("Quick sample output", payload["artifactScope"]["warning"])

    def test_bottom_and_exit_scores_stay_in_range(self) -> None:
        cfg = BottomSignalConfig(name="range_test")

        scored = score_from_indicators(indicator_frame(), cfg)

        self.assertTrue(scored["bottom_score"].between(1, 100).all())
        self.assertTrue(scored["exit_score"].between(1, 100).all())

    def test_deeper_drawdown_with_repair_confirmation_scores_higher(self) -> None:
        cfg = BottomSignalConfig(
            name="repair_test",
            drawdown_window=42,
            drawdown_threshold=-12,
            rsi_period=7,
            stoch_period=9,
            stoch_smooth=3,
            macd_fast=8,
            macd_slow=21,
            macd_signal=5,
            ma_period=150,
            atr_period=10,
            volume_window=10,
        )

        scored = score_from_indicators(indicator_frame(), cfg)

        self.assertGreater(scored["bottom_score"].iloc[-1], scored["bottom_score"].iloc[1])

    def test_indicator_spec_uses_only_requested_parameters(self) -> None:
        cfg = BottomSignalConfig(
            name="parameter_test",
            drawdown_window=42,
            rsi_period=7,
            stoch_period=9,
            stoch_smooth=3,
            macd_fast=8,
            macd_slow=21,
            macd_signal=5,
            ma_period=150,
            atr_period=10,
            volume_window=10,
        )

        spec = build_indicator_spec(cfg)

        self.assertEqual(spec["rsi"], [7])
        self.assertNotIn(14, spec["rsi"])
        self.assertEqual(spec["sma"], [150])
        self.assertEqual(spec["macd"], [(8, 21, 5)])
        self.assertEqual(spec["stochastic"], [(9, 3)])

    def test_labels_follow_score_thresholds(self) -> None:
        cfg = BottomSignalConfig(
            name="label_test",
            watch_threshold=35,
            medium_threshold=55,
            strong_threshold=75,
        )

        self.assertIsNone(classify_bottom_signal(20, cfg))
        self.assertEqual(classify_bottom_signal(35, cfg), "Watch")
        self.assertEqual(classify_bottom_signal(55, cfg), "Medium")
        self.assertEqual(classify_bottom_signal(75, cfg), "Strong")

    def test_exit_score_does_not_override_bottom_label(self) -> None:
        cfg = BottomSignalConfig(
            name="separate_scores",
            watch_threshold=35,
            medium_threshold=55,
            strong_threshold=75,
        )
        frame = indicator_frame()
        frame.loc[frame.index[-1], "drawdown_42"] = -2.0
        frame.loc[frame.index[-1], "rsi_7"] = 78.0
        frame.loc[frame.index[-1], "stoch_9_3"] = 88.0
        frame.loc[frame.index[-1], "dist_sma_150"] = 24.0
        frame.loc[frame.index[-1], "Close"] = 120.0
        frame.loc[frame.index[-1], "bb_upper_10_2"] = 115.0

        scored = score_from_indicators(frame, cfg)

        self.assertGreater(scored["exit_score"].iloc[-1], scored["bottom_score"].iloc[-1])
        self.assertIsNone(scored["signal_label"].iloc[-1])

    def test_score_from_indicators_flags_overextended_rebound(self) -> None:
        cfg = BottomSignalConfig(
            name="overextended",
            drawdown_window=42,
            drawdown_threshold=-12,
            rsi_period=7,
            stoch_period=9,
            stoch_smooth=3,
            macd_fast=8,
            macd_slow=21,
            macd_signal=5,
            ma_period=150,
            atr_period=10,
            volume_window=10,
        )
        index = pd.date_range("2025-01-01", periods=10, freq="D")
        close = [100, 99, 98, 97, 96, 95, 96, 102, 108, 112]
        frame = pd.DataFrame(
            {
                "Open": close,
                "High": [value + 1 for value in close],
                "Low": [value - 1 for value in close],
                "Close": close,
                "Volume": [1_000_000] * 10,
                "drawdown_42": [-8.0] * 10,
                "rsi_7": [45.0] * 10,
                "stoch_9_3": [35.0] * 10,
                "macd_diff_8_21_5": [0.1] * 10,
                "dist_sma_150": [4.0] * 10,
                "atr_10": [3.0] * 10,
                "volume_ratio_10": [1.2] * 10,
                "bb_upper_20_2": [120.0] * 10,
            },
            index=index,
        )

        scored = score_from_indicators(frame, cfg)

        self.assertIn("overextended_rebound", scored["risk_flags"].iloc[-1])

    def test_pine_script_uses_best_config_values(self) -> None:
        cfg = BottomSignalConfig(
            name="pine_test",
            drawdown_window=42,
            drawdown_threshold=-18,
            rsi_period=21,
            stoch_period=9,
            stoch_smooth=3,
            macd_fast=16,
            macd_slow=35,
            macd_signal=9,
            ma_period=150,
            atr_period=20,
            volume_window=50,
        )

        script = generate_pine_script(cfg)

        self.assertIn('input.int(21, "RSI Period"', script)
        self.assertIn('input.int(150, "SMA Period"', script)
        self.assertIn('input.int(16, "MACD Fast"', script)
        self.assertIn('input.float(0.3, "Drawdown Weight"', script)
        self.assertIn('input.int(21, "Min Signal Gap"', script)
        self.assertIn("lastMbSignalBar", script)
        self.assertIn("lastRsSignalBar", script)
        self.assertNotIn('input.int(14, "RSI Period"', script)
        self.assertIn('input.symbol("QQQ", "Market Symbol 1"', script)
        self.assertIn('request.security(marketSymbol1', script)
        self.assertIn('input.bool(false, "Show Score Lines"', script)
        self.assertIn('input.bool(true, "Show Signal Candle Colors"', script)
        self.assertIn('input.bool(true, "Show Signal Background"', script)
        self.assertIn('input.bool(true, "Show Signal Table"', script)
        self.assertIn('input.bool(true, "Show Text Markers"', script)
        self.assertIn("plot(showScoreLines ? bottomScore : na", script)
        self.assertIn("display=display.data_window", script)
        self.assertIn("max_labels_count=500", script)
        self.assertNotIn("Marker ATR Offset", script)
        self.assertNotIn("markerOffset", script)
        self.assertNotIn("buyMarkerPrice", script)
        self.assertNotIn("sellMarkerPrice", script)
        self.assertNotIn("label.new", script)
        self.assertNotIn("xloc=xloc.bar_index", script)
        self.assertIn("barcolor(showSignalColors ? signalColor : na)", script)
        self.assertIn("bgcolor(showSignalBackground", script)
        self.assertIn("table.new(position.top_right", script)
        self.assertNotIn("table.new(position.bottom_right", script)
        self.assertIn("table.cell(signalTable", script)
        self.assertIn('signalName = showBuyMb ? "BUY-MB"', script)
        self.assertIn("plotshape(showTextMarkers and showMbWatch, \"MB-1\"", script)
        self.assertIn("plotshape(showTextMarkers and showMbMedium, \"MB-2\"", script)
        self.assertIn("plotshape(showTextMarkers and showBuyMb, \"BUY-MB\"", script)
        self.assertIn("plotshape(showTextMarkers and showBuyDeep, \"BUY-D\"", script)
        self.assertIn("plotshape(showTextMarkers and showBuyShallow, \"BUY-S\"", script)
        self.assertIn("plotshape(showTextMarkers and showRsWatch, \"RS-1\"", script)
        self.assertIn("plotshape(showTextMarkers and showRsMedium, \"RS-2\"", script)
        self.assertIn("plotshape(showTextMarkers and showRsStrong, \"RS-3\"", script)
        self.assertIn("plotshape(showTextMarkers and exitSignal, \"Exit\"", script)
        self.assertIn("location=location.belowbar", script)
        self.assertIn("location=location.abovebar", script)
        self.assertNotIn("yloc=yloc.price", script)
        self.assertIn("shape.labelup", script)
        self.assertIn("shape.labeldown", script)
        self.assertIn('text="MB-1"', script)
        self.assertIn('text="MB-2"', script)
        self.assertIn('text="BUY-MB"', script)
        self.assertIn('text="BUY-D"', script)
        self.assertIn('text="BUY-S"', script)
        self.assertIn('text="RS-1"', script)
        self.assertIn('text="RS-2"', script)
        self.assertIn('text="RS-3"', script)
        self.assertIn('text="X"', script)
        self.assertIn('"Use RS Repair Trend Confirm"', script)
        self.assertIn("rsConfirmationScore", script)
        self.assertIn('"Use RS Market Divergence"', script)
        self.assertIn("rsMarketDivergenceScore", script)
        self.assertIn('"Use RS Post-Crash MA Reclaim"', script)
        self.assertIn("rsMaReclaimScore", script)
        self.assertIn('"Use RS Volatility Compression"', script)
        self.assertIn("rsVolatilityCompressionScore", script)
        self.assertIn('"Use RS Pullback Repair V2"', script)
        self.assertIn("rsPullbackScore", script)
        self.assertNotIn('text="WATCH"', script)
        self.assertNotIn('text="BOTTOM MED"', script)
        self.assertNotIn('text="BOTTOM STRONG"', script)
        self.assertNotIn('text="EXIT"', script)

    def test_pine_script_integrates_observation_buys_as_primary_signals(self) -> None:
        cfg = BottomSignalConfig(name="integrated_formal")

        script = generate_pine_script(
            cfg,
            {
                "deepBottomMin": 66,
                "shallowBottomMin": 68,
                "bottomMax": 75,
                "nearLowWindow": 63,
                "nearLowMax": 0.06,
                "clusterWindow": 42,
            },
        )

        self.assertIn("AutoQuant Bottom Signal Integrated", script)
        self.assertIn('obsDeepBottomMin = input.int(66, "OBS-D Bottom Min"', script)
        self.assertIn('obsShallowBottomMin = input.int(68, "OBS-S Bottom Min"', script)
        self.assertIn('obsNearLowMax = input.float(0.06, "OBS Near-Low Max Gap"', script)
        self.assertIn("obsDeepSecondTest", script)
        self.assertIn("obsShallowPullback", script)
        self.assertIn("integratedBuySignal = showBuyMb or showBuyDeep or showBuyShallow", script)
        self.assertIn(
            'signalName = showBuyMb ? "BUY-MB" : showBuyDeep ? "BUY-D" : showBuyShallow ? "BUY-S" : exitSignal ? "X"',
            script,
        )
        self.assertIn(
            "signalColor = integratedBuySignal ? color.green : exitSignal ? color.red",
            script,
        )
        self.assertIn(
            "bgcolor(showSignalBackground and integratedBuySignal ? color.new(color.green, 88)",
            script,
        )
        self.assertIn('plotshape(showTextMarkers and showBuyMb, "BUY-MB"', script)
        self.assertIn('plotshape(showTextMarkers and showBuyDeep, "BUY-D"', script)
        self.assertIn('plotshape(showTextMarkers and showBuyShallow, "BUY-S"', script)
        self.assertIn('alertcondition(integratedBuySignal, "Integrated Buy"', script)
        self.assertIn('alertcondition(showBuyDeep, "Integrated Buy Deep"', script)
        self.assertIn('alertcondition(showBuyShallow, "Integrated Buy Shallow"', script)

    def test_rs_watchlist_pine_script_is_observation_only(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_watchlist_pine",
            drawdown_window=21,
            drawdown_threshold=-8,
            rsi_period=7,
            stoch_period=9,
            stoch_smooth=3,
            macd_fast=8,
            macd_slow=21,
            macd_signal=5,
            ma_period=50,
            atr_period=10,
            volume_window=10,
            experimental_signal_set="rs_antidrawdown_repair",
        )

        script = generate_rs_watchlist_pine_script(cfg, quality_threshold=70)

        self.assertIn("AutoQuant RS Watchlist", script)
        self.assertIn("Observation only", script)
        self.assertIn('input.int(70, "RS Quality Threshold"', script)
        self.assertIn("rsQualityScore", script)
        self.assertIn("overextendedRebound", script)
        self.assertIn("max_labels_count=500", script)
        self.assertIn("display=display.data_window", script)
        self.assertIn('input.bool(true, "Show Signal Candle Colors"', script)
        self.assertIn('input.bool(true, "Show Signal Background"', script)
        self.assertIn('input.bool(true, "Show Signal Table"', script)
        self.assertIn('input.bool(true, "Show Text Markers"', script)
        self.assertNotIn("Marker ATR Offset", script)
        self.assertNotIn("markerAtr = ta.atr(14)", script)
        self.assertNotIn("markerOffset", script)
        self.assertNotIn("buyMarkerPrice", script)
        self.assertNotIn("label.new", script)
        self.assertNotIn("xloc=xloc.bar_index", script)
        self.assertIn("barcolor(showSignalColors ? rsDisplayColor : na)", script)
        self.assertIn("bgcolor(showSignalBackground", script)
        self.assertIn("table.new(position.bottom_right, 2, 5", script)
        self.assertNotIn("table.new(position.top_right", script)
        self.assertIn("table.cell(rsTable", script)
        self.assertIn('table.cell(rsTable, 0, 4, "RS-R"', script)
        self.assertIn('table.cell(rsTable, 1, 4, "Risk"', script)
        self.assertIn('rsDisplaySignal = rsQualified ? "RS-Q"', script)

    def test_merged_observation_pine_script_adds_obs_layers_and_alerts(self) -> None:
        cfg = BottomSignalConfig(name="merged_obs")

        script = generate_merged_observation_pine_script(
            cfg,
            {
                "deepBottomMin": 68,
                "shallowBottomMin": 70,
                "nearLowWindow": 63,
                "nearLowMax": 0.02,
                "clusterWindow": 42,
            },
        )

        self.assertIn("AutoQuant Bottom + RS + Observation", script)
        self.assertIn("OBS-D", script)
        self.assertIn("OBS-S", script)
        self.assertIn("obsDeepSecondTest", script)
        self.assertIn("obsShallowPullback", script)
        self.assertIn('table.cell(signalTable, 0, 3, "Observation"', script)
        self.assertIn('table.cell(signalTable, 0, 4, "Market DD"', script)
        self.assertIn('alertcondition(obsDeepSecondTest', script)
        self.assertIn('alertcondition(obsShallowPullback', script)
        self.assertIn('alertcondition(mbStrongSignal', script)
        self.assertIn('alertcondition(rsStrongSignal', script)
        self.assertIn(
            'signalName = showRsStrong ? "RS-3" : showMbStrong ? "MB-3" : showObsDeep ? "OBS-D" : showObsShallow ? "OBS-S" : exitSignal ? "X"',
            script,
        )
        self.assertIn(
            'bgcolor(showSignalBackground and signalName == "X" ? color.new(color.red, 84) : showSignalBackground and signalName != "None" ? color.new(signalColor, 88) : na)',
            script,
        )

    def test_merged_observation_pine_script_includes_rs_watchlist_quality_layer(self) -> None:
        cfg = BottomSignalConfig(name="merged_rs_quality")

        script = generate_merged_observation_pine_script(cfg, {"deepBottomMin": 68})

        self.assertIn('qualityThreshold = input.int(70, "RS Quality Threshold"', script)
        self.assertIn("rsQualityScore", script)
        self.assertIn('rsWatchlistSignal = rsQualified ? "RS-Q"', script)
        self.assertIn('table.cell(signalTable, 0, 5, "RS Quality"', script)
        self.assertIn('plotshape(showTextMarkers and showRsQualified, "RS-Q"', script)
        self.assertIn('plotshape(showTextMarkers and showRsRisk, "RS-R"', script)
        self.assertIn('alertcondition(rsQualified, "RS Watchlist Qualified"', script)
        self.assertIn('alertcondition(rsRisk, "RS Watchlist Risk"', script)

    def test_merged_observation_pine_script_uses_independent_obs_bottom_max(self) -> None:
        cfg = BottomSignalConfig(name="merged_obs_bottom_max")

        script = generate_merged_observation_pine_script(cfg, {"deepBottomMin": 66})

        self.assertIn('obsBottomMax = input.int(75, "OBS Bottom Max"', script)
        self.assertIn("bottomScore <= obsBottomMax", script)
        self.assertNotIn("bottomScore < watchThreshold and nearLowGap", script)

    def test_merged_observation_pine_script_uses_selected_obs_bottom_max(self) -> None:
        cfg = BottomSignalConfig(name="merged_obs_selected_bottom_max", watch_threshold=91)

        script = generate_merged_observation_pine_script(
            cfg,
            {
                "deepBottomMin": 61,
                "shallowBottomMin": 62,
                "bottomMax": 73,
                "nearLowWindow": 34,
                "nearLowMax": 0.035,
                "clusterWindow": 21,
            },
        )

        self.assertIn('obsDeepBottomMin = input.int(61, "OBS-D Bottom Min"', script)
        self.assertIn('obsShallowBottomMin = input.int(62, "OBS-S Bottom Min"', script)
        self.assertIn('obsBottomMax = input.int(73, "OBS Bottom Max"', script)
        self.assertIn('obsNearLowWindow = input.int(34, "OBS Near-Low Window"', script)
        self.assertIn('obsNearLowMax = input.float(0.035, "OBS Near-Low Max Gap"', script)
        self.assertIn('obsClusterGap = input.int(21, "OBS Min Signal Gap"', script)
        self.assertIn('watchThreshold = input.int(91, "Watch Score"', script)
        self.assertIn("bottomScore <= obsBottomMax", script)
        self.assertNotIn("bottomScore <= watchThreshold", script)

    def test_rs_watchlist_report_is_observation_only(self) -> None:
        payload = {
            "bestRsWatchlist": {
                "role": "rs_watchlist_only",
                "config": {
                    "name": "rs_best",
                    "experimental_signal_set": "rs_antidrawdown_repair",
                },
                "metrics": {
                    "compositeScore": 0.0,
                    "signalCount": 38,
                    "avgFwd126": 0.43,
                    "winRate126": 0.76,
                },
                "rsCandidateWatchlist": {
                    "qualifiedRsCandidateCount": 12,
                    "qualifiedRsCandidateAvgFwd126": 0.72,
                    "qualifiedRsCandidateAvgAdverse126": -0.043,
                    "topRsCandidates": [
                        {
                            "symbol": "AAPL",
                            "date": "2025-04-10",
                            "tier": "Watch",
                            "qualityScore": 88,
                            "qualityPassed": True,
                            "rsSignalScore": 82,
                            "relativeStrengthScore": 94,
                            "bottomScore": 70,
                            "riskFlags": "",
                            "fwd126": 0.25,
                            "adverse126": -0.04,
                        }
                    ],
                    "rsTickerSummary": [
                        {
                            "symbol": "AAPL",
                            "candidateCount": 2,
                            "qualifiedCount": 2,
                            "avgQualityScore": 84.0,
                            "avgFwd126": 0.25,
                            "avgAdverse126": -0.04,
                            "bestDate": "2025-04-10",
                            "bestQualityScore": 88,
                            "riskFlaggedCount": 0,
                        }
                    ],
                },
            },
            "rsWatchlistRefresh": {
                "mode": "single_config",
                "configName": "rs_best",
                "symbolCount": 21,
            },
        }

        report = generate_rs_watchlist_report(payload)

        self.assertIn("RS Watchlist Report", report)
        self.assertIn("Observation only", report)
        self.assertIn("rs_watchlist_only", report)
        self.assertIn("bottom_signal_rs_watchlist_pine.pine", report)
        self.assertIn("bottom_signal_rs_watchlist_tickers.csv", report)
        self.assertIn("bottom_signal_rs_watchlist_candidates.csv", report)
        self.assertIn("Refresh mode", report)
        self.assertIn("single_config", report)
        self.assertIn("Qualified RS candidates: 12", report)
        self.assertIn("AAPL 2025-04-10", report)
        self.assertIn("Action Summary", report)
        self.assertIn("Priority: 1", report)
        self.assertIn("Ticker Summary", report)
        self.assertIn("AAPL: action=Priority, qualified=2, candidates=2", report)
        self.assertNotIn("Formal MB-led strategy", report)

    def test_rs_watchlist_ticker_csv_exports_action_summary_rows(self) -> None:
        payload = {
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "rsTickerSummary": [
                        {
                            "symbol": "AAPL",
                            "actionTier": "Priority",
                            "candidateCount": 2,
                            "qualifiedCount": 2,
                            "avgQualityScore": 84.0,
                            "avgFwd126": 0.25,
                            "avgAdverse126": -0.04,
                            "bestDate": "2025-04-10",
                            "bestQualityScore": 88,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "RISK",
                            "candidateCount": 1,
                            "qualifiedCount": 0,
                            "avgQualityScore": 55.0,
                            "avgFwd126": -0.10,
                            "avgAdverse126": -0.20,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 55,
                            "riskFlaggedCount": 1,
                        },
                    ]
                }
            }
        }

        csv_text = generate_rs_watchlist_ticker_csv(payload)

        self.assertIn("symbol,selectionRank,actionTier,actionReason,qualifiedCount,candidateCount,selectionScore", csv_text)
        self.assertIn(
            "AAPL,1,Priority,repeated qualified candidates with clean risk profile,2,2,93.33,84.00,2025-04-10,88,0,0.250000,-0.040000",
            csv_text,
        )
        self.assertIn(
            "RISK,2,Avoid,no qualified RS candidates,0,1,22.23,55.00,2025-04-11,55,1,-0.100000,-0.200000",
            csv_text,
        )

    def test_rs_watchlist_candidate_csv_exports_signal_rows(self) -> None:
        payload = {
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "topRsCandidates": [
                        {
                            "symbol": "AAPL",
                            "date": "2025-04-10",
                            "tier": "Watch",
                            "qualityPassed": True,
                            "qualityScore": 88,
                            "rsSignalScore": 82,
                            "relativeStrengthScore": 94,
                            "bottomScore": 70,
                            "riskFlags": "",
                            "marketDrawdown": -12.5,
                            "fwd126": 0.25,
                            "adverse126": -0.04,
                        },
                        {
                            "symbol": "RISK",
                            "date": "2025-04-11",
                            "tier": "Medium",
                            "qualityPassed": False,
                            "qualityScore": 55,
                            "rsSignalScore": 80,
                            "relativeStrengthScore": 90,
                            "bottomScore": 60,
                            "riskFlags": "no_repair",
                            "marketDrawdown": None,
                            "fwd126": None,
                            "adverse126": -0.20,
                        },
                    ]
                }
            }
        }

        csv_text = generate_rs_watchlist_candidate_csv(payload)

        self.assertIn("symbol,date,tier,qualityPassed,qualityScore", csv_text)
        self.assertIn("AAPL,2025-04-10,Watch,True,88,82,94,70,,-12.500000,0.250000,-0.040000", csv_text)
        self.assertIn("RISK,2025-04-11,Medium,False,55,80,90,60,no_repair,,,-0.200000", csv_text)

    def test_mb_factor_ablation_csv_exports_comparison_rows(self) -> None:
        payload = {
            "mbFactorAblation": {
                "rows": [
                    {
                        "factor": "drawdown",
                        "impactLabel": "Critical",
                        "configName": "best_no_drawdown",
                        "compositeScore": 12.5,
                        "compositeDelta": -8.25,
                        "signalCount": 3,
                        "signalCountDelta": -2,
                        "avgFwd126": 0.10,
                        "avgFwd126Delta": -0.04,
                        "avgAdverse126": -0.12,
                        "avgAdverse126Delta": -0.02,
                    }
                ]
            }
        }

        csv_text = generate_mb_factor_ablation_csv(payload)

        self.assertIn("factor,impactLabel,configName,compositeScore,compositeDelta", csv_text)
        self.assertIn(
            "drawdown,Critical,best_no_drawdown,12.500000,-8.250000,3,-2,0.100000,-0.040000,-0.120000,-0.020000",
            csv_text,
        )

    def test_mb_factor_ablation_summary_labels_critical_and_overactive_factors(self) -> None:
        ablation = {
            "baselineSignalCount": 39,
            "rows": [
                {
                    "factor": "drawdown",
                    "compositeScore": 0.0,
                    "compositeDelta": -27.0,
                    "signalCount": 2,
                    "signalCountDelta": -37,
                },
                {
                    "factor": "repair",
                    "compositeScore": 0.0,
                    "compositeDelta": -27.0,
                    "signalCount": 125,
                    "signalCountDelta": 86,
                },
                {
                    "factor": "volume",
                    "compositeScore": 26.0,
                    "compositeDelta": -1.0,
                    "signalCount": 41,
                    "signalCountDelta": 2,
                },
            ],
        }

        summary = summarize_mb_factor_ablation(ablation)

        self.assertEqual(summary["factorCount"], 3)
        self.assertIn("drawdown", summary["criticalFactors"])
        self.assertIn("repair", summary["overactiveFactors"])
        self.assertEqual(summary["rows"][0]["impactLabel"], "Critical")
        self.assertEqual(summary["rows"][1]["impactLabel"], "Overactive")
        self.assertEqual(summary["rows"][2]["impactLabel"], "Supportive")

    def test_recent_validation_csv_exports_best_config_signal_rows(self) -> None:
        payload = {
            "bestConfig": {"name": "best"},
            "results": [
                {
                    "config": {"name": "best"},
                    "recentValidation": {
                        "recentValidationStart": "2024-05-01",
                        "recentValidationEnd": "2026-04-30",
                    },
                    "signals": [
                        {
                            "symbol": "AAPL",
                            "date": "2025-04-10",
                            "channel": "MB",
                            "tier": "Strong",
                            "bottomScore": 91,
                            "rsSignalScore": 75,
                            "fwd126": 0.25,
                            "adverse126": -0.04,
                            "riskFlags": "",
                        },
                        {
                            "symbol": "MSFT",
                            "date": "2025-05-01",
                            "channel": "MB",
                            "tier": "Strong",
                            "bottomScore": 88,
                            "rsSignalScore": 70,
                            "fwd126": None,
                            "adverse126": None,
                            "riskFlags": "low_volume",
                        },
                        {
                            "symbol": "OLD",
                            "date": "2023-01-01",
                            "channel": "MB",
                            "tier": "Strong",
                            "bottomScore": 90,
                            "rsSignalScore": 70,
                            "fwd126": 0.10,
                            "adverse126": -0.03,
                            "riskFlags": "",
                        },
                    ],
                }
            ],
        }

        csv_text = generate_recent_validation_csv(payload)

        self.assertIn("symbol,date,channel,tier,checkStatus", csv_text)
        self.assertIn("AAPL,2025-04-10,MB,Strong,Pass,91,75,,0.250000,-0.040000", csv_text)
        self.assertIn("MSFT,2025-05-01,MB,Strong,Pending,88,70,low_volume,,", csv_text)
        self.assertNotIn("OLD", csv_text)

    def test_observation_search_covers_qqq_anchor_windows_and_keeps_sparse(self) -> None:
        dates = pd.to_datetime(
            [
                "2022-10-11",
                "2022-12-28",
                "2025-04-04",
                "2026-03-27",
                "2026-03-30",
            ]
        )
        qqq = pd.DataFrame(
            {
                "Open": [120.0, 120.0, 120.0, 120.0, 121.0],
                "High": [121.0, 121.0, 121.0, 121.0, 122.0],
                "Low": [119.0, 119.0, 119.0, 119.0, 120.0],
                "Close": [120.0, 120.0, 120.0, 120.0, 121.0],
                "Volume": [1_000_000] * 5,
                "bottom_score": [69, 68, 90, 71, 71],
                "rs_signal_score": [40, 42, 55, 40, 40],
                "exit_score": [10, 10, 10, 10, 10],
                "risk_flags": ["no_repair", "no_repair", "", "no_repair", "no_repair"],
            },
            index=dates,
        )
        aapl = qqq.copy()
        aapl.index = pd.to_datetime(
            [
                "2022-10-12",
                "2022-12-29",
                "2025-04-05",
                "2026-03-28",
                "2026-03-31",
            ]
        )
        aapl["bottom_score"] = [74, 73, 88, 72, 72]
        market_context = pd.Series(
            [-23.0, -21.0, -21.0, -11.0, -11.0],
            index=dates,
        )
        market_context = pd.concat(
            [
                market_context,
                pd.Series([-23.0, -21.0, -21.0, -11.0, -11.0], index=aapl.index),
            ]
        ).sort_index()
        formal_keys = {("QQQ", "2025-04-04"), ("AAPL", "2025-04-05")}

        search = search_observation_channel(
            {"QQQ": qqq, "AAPL": aapl},
            market_context,
            formal_keys=formal_keys,
            formal_signal_count=4,
        )

        self.assertTrue(search["anchorCoverage"]["qqq_2022_q4"]["covered"])
        self.assertTrue(search["anchorCoverage"]["qqq_2026_march"]["covered"])
        self.assertLessEqual(search["metrics"]["signalCount"], search["metrics"]["sparseTargetMax"])
        self.assertEqual(search["metrics"]["formalStrongBaselineCount"], 4)
        self.assertAlmostEqual(
            search["metrics"]["observationToFormalRatio"],
            search["metrics"]["signalCount"] / 4,
        )
        self.assertLessEqual(search["metrics"]["duplicateFormalCount"], 0)
        self.assertIn(
            ("QQQ", "2022-12-28", "OBS-D"),
            [
                (item["symbol"], item["date"], item["observationType"])
                for item in search["signals"]
            ],
        )
        self.assertIn(
            ("QQQ", "2026-03-27", "OBS-S"),
            [
                (item["symbol"], item["date"], item["observationType"])
                for item in search["signals"]
            ],
        )

    def test_observation_search_penalizes_formal_overlap_candidates(self) -> None:
        dates = pd.to_datetime(
            [
                "2022-10-11",
                "2026-03-27",
                "2025-04-04",
            ]
        )
        qqq = pd.DataFrame(
            {
                "Open": [120.0, 120.0, 120.0],
                "High": [121.0, 121.0, 121.0],
                "Low": [119.0, 119.0, 119.0],
                "Close": [120.0, 120.0, 120.0],
                "Volume": [1_000_000] * 3,
                "bottom_score": [70, 71, 69],
                "rs_signal_score": [40, 40, 42],
                "exit_score": [10, 10, 10],
                "risk_flags": ["", "no_repair", ""],
            },
            index=dates,
        )
        market_context = pd.Series([-23.0, -11.0, -21.0], index=dates)
        overlap_config = {
            "deepMarketMax": -20.0,
            "shallowMarketMin": -20.0,
            "shallowMarketMax": -8.0,
            "deepBottomMin": 68,
            "shallowBottomMin": 70,
            "nearLowWindow": 21,
            "nearLowMax": 0.10,
            "clusterWindow": 42,
            "maxPerCluster": 1,
        }
        clean_config = dict(overlap_config, deepBottomMin=70)

        search = search_observation_channel(
            {"QQQ": qqq},
            market_context,
            formal_keys={("QQQ", "2025-04-04")},
            formal_signal_count=4,
            candidate_configs_list=[overlap_config, clean_config],
        )

        self.assertEqual(search["selectedConfig"]["deepBottomMin"], 70)
        self.assertEqual(search["metrics"]["duplicateFormalCount"], 0)

    def test_observation_csv_and_report_export_anchor_evidence(self) -> None:
        payload = {
            "observationSearch": {
                "selectedConfig": {
                    "deepBottomMin": 68,
                    "shallowBottomMin": 70,
                    "nearLowWindow": 63,
                    "nearLowMax": 0.02,
                    "clusterWindow": 42,
                },
                "metrics": {
                    "signalCount": 2,
                    "avgFwd126": 0.20,
                    "winRate126": 1.0,
                    "avgAdverse126": -0.05,
                    "upgradeCandidateScore": 72.0,
                    "sparseTargetMax": 78,
                    "formalStrongBaselineCount": 39,
                    "observationToFormalRatio": 0.05,
                },
                "anchorCoverage": {
                    "qqq_2022_q4": {
                        "label": "QQQ 2022-10-01 to 2022-12-31",
                        "covered": True,
                        "count": 1,
                    },
                    "qqq_2026_march": {
                        "label": "QQQ 2026-03-01 to 2026-03-31",
                        "covered": True,
                        "count": 1,
                    },
                },
                "signals": [
                    {
                        "symbol": "QQQ",
                        "date": "2022-12-28",
                        "observationType": "OBS-D",
                        "bottomScore": 68,
                        "rsSignalScore": 42,
                        "marketDrawdown": -21.5,
                        "nearLowGap": 0.0,
                        "riskFlags": "no_repair",
                        "fwd126": 0.15,
                        "adverse126": -0.04,
                    }
                ],
            }
        }

        csv_text = generate_observation_signals_csv(payload)
        report = generate_observation_report(payload)

        self.assertIn(
            "symbol,date,observationType,bottomScore,rsSignalScore,marketDrawdown,nearLowGap,riskFlags,fwd126,adverse126",
            csv_text,
        )
        self.assertIn("QQQ,2022-12-28,OBS-D,68,42,-21.500000,0.000000,no_repair,0.150000,-0.040000", csv_text)
        self.assertIn("QQQ 2022-10-01 to 2022-12-31: Covered", report)
        self.assertIn("QQQ 2026-03-01 to 2026-03-31: Covered", report)
        self.assertIn("Formal Strong baseline: 39", report)
        self.assertIn("Observation/Formal ratio: 0.05x", report)
        self.assertIn("## Anchor Signal Details", report)
        self.assertIn(
            "QQQ 2022-12-28 OBS-D bottom=68 RS=42 risk=no_repair",
            report,
        )
        self.assertIn("Upgrade candidate score: 72.00", report)

    def test_plan_summary_connects_mb_rs_and_recent_validation_outputs(self) -> None:
        payload = {
            "bestConfig": {"name": "best"},
            "bestMetrics": {
                "compositeScore": 27.0,
                "signalCount": 7,
                "avgFwd126": 0.42,
                "winRate126": 1.0,
                "avgAdverse126": -0.03,
            },
            "mbFactorAblation": {
                "baselineSignalCount": 7,
                "rows": [
                    {
                        "factor": "drawdown",
                        "configName": "best_no_drawdown",
                        "compositeScore": 0.0,
                        "compositeDelta": -27.0,
                        "signalCount": 1,
                        "signalCountDelta": -6,
                        "avgFwd126": 0.10,
                        "avgAdverse126": -0.08,
                    },
                    {
                        "factor": "repair",
                        "configName": "best_no_repair",
                        "compositeScore": 0.0,
                        "compositeDelta": -27.0,
                        "signalCount": 40,
                        "signalCountDelta": 33,
                        "avgFwd126": 0.05,
                        "avgAdverse126": -0.12,
                    }
                ],
            },
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "rsTickerSummary": [
                        {
                            "symbol": "AVGO",
                            "candidateCount": 3,
                            "qualifiedCount": 2,
                            "avgQualityScore": 84.0,
                            "avgFwd126": 0.50,
                            "avgAdverse126": -0.04,
                            "bestDate": "2025-04-10",
                            "bestQualityScore": 88,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "CRM",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 68.0,
                            "avgFwd126": 0.18,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 68,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "TSLA",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 67.0,
                            "avgFwd126": 0.16,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 67,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "AMZN",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 66.0,
                            "avgFwd126": 0.15,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 66,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "PLTR",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 65.0,
                            "avgFwd126": 0.14,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 65,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "V",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 64.0,
                            "avgFwd126": 0.13,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 64,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "RISK",
                            "candidateCount": 1,
                            "qualifiedCount": 0,
                            "avgQualityScore": 55.0,
                            "avgFwd126": -0.10,
                            "avgAdverse126": -0.20,
                            "bestDate": "2025-04-12",
                            "bestQualityScore": 55,
                            "riskFlaggedCount": 1,
                        }
                    ]
                }
            },
            "results": [
                {
                    "config": {"name": "best"},
                    "recentValidation": {
                        "recentValidationStart": "2024-05-01",
                        "recentValidationEnd": "2026-04-30",
                        "recentValidationSignalCount": 7,
                        "recentValidationMatureCount": 7,
                        "recentValidationAvgFwd126": 0.42,
                        "recentValidationWinRate126": 1.0,
                        "recentValidationAvgAdverse126": -0.03,
                        "recentValidationStatus": "Pass",
                    },
                }
            ],
        }

        summary = generate_plan_summary(payload)

        self.assertIn("# MB Ablation, RS Selection, Recent Validation Summary", summary)
        self.assertIn("Critical factors: drawdown", summary)
        self.assertIn("#1 AVGO", summary)
        self.assertIn("Recent validation status: Pass", summary)
        self.assertIn("bottom_signal_mb_factor_ablation.csv", summary)
        self.assertIn("bottom_signal_recent_validation.csv", summary)
        self.assertIn("bottom_signal_rs_watchlist_tickers.csv", summary)
        self.assertIn("## Action Counts", summary)
        self.assertIn("MB keep: 1", summary)
        self.assertIn("MB brake: 1", summary)
        self.assertIn("RS monitor: 1", summary)
        self.assertIn("RS review: 5", summary)
        self.assertIn("RS skip: 1", summary)
        self.assertIn("## Role Guide", summary)
        self.assertIn("FormalStrategy: MB keep/brake actions belong to the formal strategy", summary)
        self.assertIn("Observation: RS Monitor/Review/Skip rows are watchlist actions only", summary)
        self.assertIn("Validation: RecentValidation rows summarize recent evidence", summary)
        self.assertIn("## Decision Rule", summary)
        self.assertIn("Do not promote RS watchlist rows into formal MB entries from this artifact", summary)
        self.assertIn("Keep the current MB factor stack intact", summary)
        self.assertIn("Use RecentValidation status before any promotion decision", summary)
        self.assertIn("## Next Actions", summary)
        self.assertIn("Keep MB factors: drawdown", summary)
        self.assertIn("Keep MB brake factors: repair", summary)
        self.assertIn("Monitor Priority RS tickers: AVGO", summary)
        self.assertIn("Review Watch RS tickers: CRM", summary)
        self.assertIn("Skip Avoid RS tickers: RISK", summary)
        self.assertIn("Recent validation passed; continue observation", summary)

    def test_next_actions_csv_exports_review_checklist(self) -> None:
        payload = {
            "bestConfig": {"name": "best"},
            "mbFactorAblation": {
                "baselineSignalCount": 7,
                "rows": [
                    {
                        "factor": "drawdown",
                        "compositeScore": 0.0,
                        "compositeDelta": -27.0,
                        "signalCount": 1,
                        "signalCountDelta": -6,
                    },
                    {
                        "factor": "repair",
                        "compositeScore": 0.0,
                        "compositeDelta": -27.0,
                        "signalCount": 40,
                        "signalCountDelta": 33,
                    }
                ],
            },
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "rsTickerSummary": [
                        {
                            "symbol": "AVGO",
                            "candidateCount": 3,
                            "qualifiedCount": 2,
                            "avgQualityScore": 84.0,
                            "avgFwd126": 0.50,
                            "avgAdverse126": -0.04,
                            "bestDate": "2025-04-10",
                            "bestQualityScore": 88,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "CRM",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 68.0,
                            "avgFwd126": 0.18,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 68,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "TSLA",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 67.0,
                            "avgFwd126": 0.16,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 67,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "AMZN",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 66.0,
                            "avgFwd126": 0.15,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 66,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "PLTR",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 65.0,
                            "avgFwd126": 0.14,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 65,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "V",
                            "candidateCount": 1,
                            "qualifiedCount": 1,
                            "avgQualityScore": 64.0,
                            "avgFwd126": 0.13,
                            "avgAdverse126": -0.05,
                            "bestDate": "2025-04-11",
                            "bestQualityScore": 64,
                            "riskFlaggedCount": 0,
                        },
                        {
                            "symbol": "RISK",
                            "candidateCount": 1,
                            "qualifiedCount": 0,
                            "avgQualityScore": 55.0,
                            "avgFwd126": -0.10,
                            "avgAdverse126": -0.20,
                            "bestDate": "2025-04-12",
                            "bestQualityScore": 55,
                            "riskFlaggedCount": 1,
                        }
                    ]
                }
            },
            "results": [
                {
                    "config": {"name": "best"},
                    "recentValidation": {
                        "recentValidationStatus": "Pass",
                        "recentValidationMatureCount": 7,
                        "recentValidationWinRate126": 1.0,
                        "recentValidationAvgFwd126": 0.42,
                    },
                }
            ],
        }

        csv_text = generate_next_actions_csv(payload)

        self.assertIn("priority,role,category,target,action,reason,evidence", csv_text)
        self.assertIn(
            "1,FormalStrategy,MB,drawdown,Keep,Critical factor from MB ablation,compositeDelta=-27.00; signalCountDelta=-6",
            csv_text,
        )
        self.assertIn(
            "1,FormalStrategy,MB,repair,Keep brake,Overactive factor from MB ablation,compositeDelta=-27.00; signalCountDelta=+33",
            csv_text,
        )
        self.assertIn(
            "2,Observation,RS,AVGO,Monitor,Priority RS ticker,selectionScore=96.67; qualifiedCount=2; reason=repeated qualified candidates with clean risk profile",
            csv_text,
        )
        self.assertIn(
            "3,Observation,RS,CRM,Review,Watch RS ticker,selectionScore=64.92; qualifiedCount=1; reason=qualified but quality score is below priority",
            csv_text,
        )
        self.assertIn(
            "4,Observation,RS,RISK,Skip,Avoid RS ticker,selectionScore=22.23; reason=no qualified RS candidates",
            csv_text,
        )
        self.assertIn(
            "5,Validation,RecentValidation,Pass,Continue observation,Recent validation passed,status=Pass; matureCount=7; winRate=100.00%; avgFwd126=42.00%",
            csv_text,
        )

    def test_strategy_iteration_review_report_freezes_formal_and_segments_observation(self) -> None:
        payload = {
            "symbols": ["QQQ", "SPY", "AAPL"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {
                "signalCount": 39,
                "avgFwd126": 0.3924,
                "winRate126": 0.7436,
                "avgAdverse126": -0.138,
            },
            "observationSearch": {
                "metrics": {
                    "signalCount": 48,
                    "formalStrongBaselineCount": 39,
                    "observationToFormalRatio": 1.23,
                    "avgFwd126": 0.191,
                    "winRate126": 0.7234,
                    "duplicateFormalCount": 0,
                },
                "signals": [
                    {
                        "symbol": "QQQ",
                        "date": "2026-03-27",
                        "observationType": "OBS-S",
                        "riskFlags": "no_repair",
                        "fwd126": 0.12,
                        "adverse126": -0.04,
                        "duplicateFormalCount": 0,
                    },
                    {
                        "symbol": "AAPL",
                        "date": "2024-08-05",
                        "observationType": "OBS-D",
                        "riskFlags": "",
                        "fwd126": 0.20,
                        "adverse126": -0.03,
                        "duplicateFormalCount": 0,
                    },
                    {
                        "symbol": "AMD",
                        "date": "2024-08-06",
                        "observationType": "OBS-S",
                        "riskFlags": "trend_damage,no_repair",
                        "fwd126": -0.10,
                        "adverse126": -0.20,
                        "duplicateFormalCount": 0,
                    },
                ],
            },
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "rsTickerSummary": [
                        {"symbol": "AVGO", "actionTier": "Priority", "selectionScore": 92.4, "qualifiedCount": 2, "actionReason": "clean"},
                        {"symbol": "META", "actionTier": "Priority", "selectionScore": 92.1, "qualifiedCount": 2, "actionReason": "clean"},
                        {"symbol": "CRM", "actionTier": "Watch", "selectionScore": 79.7, "qualifiedCount": 2, "actionReason": "risk flags"},
                        {"symbol": "CAT", "actionTier": "Avoid", "selectionScore": 50.9, "qualifiedCount": 0, "actionReason": "no qualified RS candidates"},
                    ],
                }
            },
            "results": [
                {
                    "config": {"name": "seed_previous_rs_higher_low_best"},
                    "signals": [
                        {"symbol": "META", "date": "2024-06-01", "fwd126": 0.50, "adverse126": -0.02},
                        {"symbol": "AVGO", "date": "2024-07-01", "fwd126": 0.40, "adverse126": -0.03},
                    ],
                    "recentValidation": {
                        "recentValidationStart": "2024-05-01",
                        "recentValidationEnd": "2026-04-30",
                        "recentValidationSignalCount": 7,
                        "recentValidationMatureCount": 7,
                        "recentValidationWinRate126": 1.0,
                        "recentValidationAvgFwd126": 0.7579,
                        "recentValidationStatus": "Pass",
                    },
                }
            ],
        }

        report = generate_strategy_iteration_review_report(payload)

        self.assertIn("# Strategy Iteration Review", report)
        self.assertIn("Formal strategy: `seed_previous_rs_higher_low_best` stays frozen", report)
        self.assertIn("Full-pool artifact: yes", report)
        self.assertIn("Entry threshold: `82`", report)
        self.assertIn("Recent mature signals: 7", report)
        self.assertIn("risk=none: count=1, avg6m=20.00%, win6m=100.00%, adverse6m=-3.00%", report)
        self.assertIn("risk=no_repair: count=2, avg6m=1.00%, win6m=50.00%, adverse6m=-12.00%", report)
        self.assertIn("risk=trend_damage: count=1, avg6m=-10.00%, win6m=0.00%, adverse6m=-20.00%", report)
        self.assertIn("Monitor: AVGO, META", report)
        self.assertIn("Review: CRM", report)
        self.assertIn("Skip: CAT", report)
        self.assertIn("QQQ 2026-03-27 OBS-S", report)
        self.assertIn("Do not promote OBS/RS into formal entries", report)

    def test_strategy_iteration_review_csv_exports_ordered_research_steps(self) -> None:
        payload = {
            "symbols": ["QQQ", "SPY", "AAPL"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {
                "metrics": {"signalCount": 48, "duplicateFormalCount": 0},
                "signals": [
                    {"symbol": "QQQ", "date": "2026-03-27", "observationType": "OBS-S", "riskFlags": "no_repair", "duplicateFormalCount": 0},
                    {"symbol": "AAPL", "date": "2024-08-05", "observationType": "OBS-D", "riskFlags": "", "duplicateFormalCount": 0},
                ],
            },
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "rsTickerSummary": [
                        {"symbol": "AVGO", "actionTier": "Priority", "selectionScore": 92.4, "qualifiedCount": 2},
                        {"symbol": "CRM", "actionTier": "Watch", "selectionScore": 79.7, "qualifiedCount": 2},
                        {"symbol": "CAT", "actionTier": "Avoid", "selectionScore": 50.9, "qualifiedCount": 0},
                    ],
                }
            },
            "results": [
                {
                    "config": {"name": "seed_previous_rs_higher_low_best"},
                    "signals": [{"symbol": "META", "date": "2024-06-01", "fwd126": 0.50, "adverse126": -0.02}],
                    "recentValidation": {
                        "recentValidationSignalCount": 7,
                        "recentValidationMatureCount": 7,
                        "recentValidationStatus": "Pass",
                    },
                }
            ],
        }

        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("step,section,role,target,action,evidence", csv_text)
        self.assertIn("1,Baseline,FormalStrategy,seed_previous_rs_higher_low_best,Freeze formal MB baseline", csv_text)
        self.assertIn("2,RecentValidation,FormalStrategy,META 2024-06-01,Review mature recent formal signal", csv_text)
        self.assertIn("3,ObservationRisk,Observation,risk=none,Keep observation-only bucket", csv_text)
        self.assertIn("3,ObservationRisk,Observation,risk=no_repair,Keep observation-only bucket", csv_text)
        self.assertIn("4,RSWatchlist,Observation,AVGO,Monitor", csv_text)
        self.assertIn("4,RSWatchlist,Observation,CRM,Review", csv_text)
        self.assertIn("4,RSWatchlist,Observation,CAT,Skip", csv_text)
        self.assertIn("5,MissedCase,Observation,QQQ 2026-03-27 OBS-S,Record formal-missed OBS candidate", csv_text)
        self.assertIn("6,CandidateRule,Validation,OBS/RS promotion,Open separate validation plan before promotion", csv_text)

    def test_strategy_iteration_review_summarizes_observation_bucket_quality(self) -> None:
        payload = {
            "symbols": ["QQQ", "AAPL"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {
                "metrics": {"signalCount": 3, "duplicateFormalCount": 0},
                "signals": [
                    {
                        "symbol": "AAPL",
                        "date": "2024-08-05",
                        "observationType": "OBS-D",
                        "riskFlags": "",
                        "fwd126": 0.20,
                        "adverse126": -0.03,
                        "duplicateFormalCount": 0,
                    },
                    {
                        "symbol": "QQQ",
                        "date": "2024-08-06",
                        "observationType": "OBS-S",
                        "riskFlags": "",
                        "fwd126": -0.10,
                        "adverse126": -0.07,
                        "duplicateFormalCount": 0,
                    },
                    {
                        "symbol": "AMD",
                        "date": "2024-08-07",
                        "observationType": "OBS-S",
                        "riskFlags": "trend_damage,no_repair",
                        "fwd126": -0.20,
                        "adverse126": -0.25,
                        "duplicateFormalCount": 0,
                    },
                ],
            },
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("risk=none: count=2, avg6m=5.00%, win6m=50.00%, adverse6m=-5.00%", report)
        self.assertIn("risk=no_repair: count=1, avg6m=-20.00%, win6m=0.00%, adverse6m=-25.00%", report)
        self.assertIn("risk=trend_damage: count=1, avg6m=-20.00%, win6m=0.00%, adverse6m=-25.00%", report)
        self.assertIn(
            "3,ObservationRisk,Observation,risk=none,Keep observation-only bucket,count=2; avgFwd126=5.00%; winRate126=50.00%; avgAdverse126=-5.00%",
            csv_text,
        )
        self.assertIn(
            "3,ObservationRisk,Observation,risk=trend_damage,Keep observation-only bucket,count=1; avgFwd126=-20.00%; winRate126=0.00%; avgAdverse126=-25.00%",
            csv_text,
        )

    def test_strategy_iteration_review_lists_recent_formal_signal_details(self) -> None:
        payload = {
            "symbols": ["META", "AVGO"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {"metrics": {"signalCount": 0}, "signals": []},
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [
                {
                    "config": {"name": "seed_previous_rs_higher_low_best"},
                    "signals": [
                        {
                            "symbol": "AVGO",
                            "date": "2024-07-01",
                            "channel": "RS",
                            "riskFlags": "no_repair",
                            "bottomScore": 82,
                            "rsSignalScore": 84,
                            "fwd126": 0.40,
                            "adverse126": -0.03,
                        },
                        {
                            "symbol": "META",
                            "date": "2024-06-01",
                            "channel": "MB",
                            "riskFlags": "",
                            "bottomScore": 83,
                            "rsSignalScore": 46,
                            "fwd126": 0.50,
                            "adverse126": -0.02,
                        },
                    ],
                    "recentValidation": {
                        "recentValidationStart": "2024-05-01",
                        "recentValidationEnd": "2026-04-30",
                        "recentValidationSignalCount": 2,
                        "recentValidationMatureCount": 2,
                        "recentValidationStatus": "Pass",
                    },
                }
            ],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("## Recent Formal Signal Details", report)
        self.assertIn(
            "- META 2024-06-01 channel=MB bottom=83 RS=46 risk=none fwd6m=50.00% adverse6m=-2.00%",
            report,
        )
        self.assertIn(
            "- AVGO 2024-07-01 channel=RS bottom=82 RS=84 risk=no_repair fwd6m=40.00% adverse6m=-3.00%",
            report,
        )
        self.assertIn(
            "status=Pass; fwd126=0.500000; adverse126=-0.020000; channel=MB; risk=none",
            csv_text,
        )

    def test_strategy_iteration_review_records_formal_missed_obs_case_details(self) -> None:
        payload = {
            "symbols": ["QQQ", "SPY"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {
                "metrics": {"signalCount": 2, "duplicateFormalCount": 1},
                "signals": [
                    {
                        "symbol": "QQQ",
                        "date": "2026-03-27",
                        "observationType": "OBS-S",
                        "riskFlags": "",
                        "bottomScore": 77,
                        "rsSignalScore": 58,
                        "fwd126": 0.12,
                        "adverse126": -0.04,
                        "duplicateFormalCount": 0,
                    },
                    {
                        "symbol": "SPY",
                        "date": "2026-03-27",
                        "observationType": "OBS-D",
                        "riskFlags": "no_repair",
                        "bottomScore": 83,
                        "rsSignalScore": 46,
                        "fwd126": 0.08,
                        "adverse126": -0.02,
                        "duplicateFormalCount": 1,
                    },
                ],
            },
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn(
            "- QQQ 2026-03-27 OBS-S risk=none bottom=77 RS=58 fwd6m=12.00% adverse6m=-4.00%",
            report,
        )
        self.assertNotIn("SPY 2026-03-27 OBS-D risk=no_repair", report)
        self.assertIn(
            "risk=none; duplicateFormalCount=0; fwd126=0.120000; adverse126=-0.040000; bottom=77; RS=58",
            csv_text,
        )
        self.assertNotIn("5,MissedCase,Observation,SPY 2026-03-27 OBS-D", csv_text)

    def test_strategy_iteration_review_lists_rs_watchlist_details(self) -> None:
        payload = {
            "symbols": ["AVGO", "CRM", "CAT"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {"metrics": {"signalCount": 0}, "signals": []},
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "rsTickerSummary": [
                        {
                            "symbol": "AVGO",
                            "actionTier": "Priority",
                            "selectionScore": 92.4,
                            "qualifiedCount": 2,
                            "actionReason": "clean leadership",
                        },
                        {
                            "symbol": "CRM",
                            "actionTier": "Watch",
                            "selectionScore": 79.7,
                            "qualifiedCount": 2,
                            "actionReason": "watch risk flags",
                        },
                        {
                            "symbol": "CAT",
                            "actionTier": "Avoid",
                            "selectionScore": 50.9,
                            "qualifiedCount": 0,
                            "actionReason": "no qualified RS candidates",
                        },
                    ],
                }
            },
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("- Monitor: AVGO", report)
        self.assertIn("  - AVGO: score=92.40, qualified=2, reason=clean leadership", report)
        self.assertIn("  - CRM: score=79.70, qualified=2, reason=watch risk flags", report)
        self.assertIn("  - CAT: score=50.90, qualified=0, reason=no qualified RS candidates", report)
        self.assertIn(
            "selectionScore=92.40; qualifiedCount=2; reason=clean leadership",
            csv_text,
        )

    def test_strategy_iteration_review_reports_plan_validation_gates(self) -> None:
        payload = {
            "symbols": [f"S{i:02d}" for i in range(20)] + ["QQQ"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {
                "metrics": {"signalCount": 48, "duplicateFormalCount": 0},
                "signals": [
                    {"symbol": "QQQ", "date": "2022-10-03", "observationType": "OBS-S"},
                    {"symbol": "QQQ", "date": "2026-03-27", "observationType": "OBS-S"},
                ],
            },
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("## Plan Validation Gates", report)
        self.assertIn("- PASS baselineName: seed_previous_rs_higher_low_best", report)
        self.assertIn("- PASS fullPool: symbols=21 sample=FULL_POOL", report)
        self.assertIn("- PASS entryThreshold: threshold=82", report)
        self.assertIn("- PASS formalSignalCap: signals=39 limit=40", report)
        self.assertIn("- PASS duplicateFormal: duplicateFormalCount=0", report)
        self.assertIn("- PASS qqq2022Q4Coverage: 2022-10-03", report)
        self.assertIn("- PASS qqq2026MarchCoverage: 2026-03-27", report)
        self.assertIn(
            "7,ValidationGate,Validation,baselineName,Pass,seed_previous_rs_higher_low_best",
            csv_text,
        )
        self.assertIn(
            "7,ValidationGate,Validation,qqq2026MarchCoverage,Pass,2026-03-27",
            csv_text,
        )

    def test_strategy_iteration_review_lists_promotion_preconditions(self) -> None:
        payload = {
            "symbols": ["QQQ"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {"metrics": {"signalCount": 48, "duplicateFormalCount": 0}, "signals": []},
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("## Promotion Preconditions", report)
        self.assertIn("- Required: OBS/RS ablation against frozen MB baseline.", report)
        self.assertIn("- Required: recent validation keeps formal signal count controlled.", report)
        self.assertIn("- Required: sample-out validation before formal promotion.", report)
        self.assertIn("- Required: Pine parity check before operator use.", report)
        self.assertIn(
            "8,PromotionPrecondition,Validation,OBS/RS promotion,Required,OBS/RS ablation against frozen MB baseline",
            csv_text,
        )
        self.assertIn(
            "8,PromotionPrecondition,Validation,OBS/RS promotion,Required,Pine parity check before operator use",
            csv_text,
        )

    def test_strategy_iteration_review_reports_retired_dual_track_artifact_guard(self) -> None:
        payload = {
            "symbols": ["QQQ"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {"metrics": {"signalCount": 48, "duplicateFormalCount": 0}, "signals": []},
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            retired_missing = tmp_path / "bottom_signal_results_dual_track_rs.json"
            retired_present = tmp_path / "bottom_signal_report_dual_track_rs.md"
            retired_present.write_text("old artifact", encoding="utf-8")

            with patch(
                "investigations.bottom_signal_search.RETIRED_ARTIFACT_PATHS",
                [retired_missing, retired_present],
            ):
                report = generate_strategy_iteration_review_report(payload)
                csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("## Retired Artifact Guard", report)
        self.assertIn(
            "- PASS retiredArtifact: bottom_signal_results_dual_track_rs.json absent",
            report,
        )
        self.assertIn(
            "- FAIL retiredArtifact: bottom_signal_report_dual_track_rs.md still exists",
            report,
        )
        self.assertIn(
            "9,RetiredArtifact,Validation,bottom_signal_results_dual_track_rs.json,Pass,absent",
            csv_text,
        )
        self.assertIn(
            "9,RetiredArtifact,Validation,bottom_signal_report_dual_track_rs.md,Fail,still exists",
            csv_text,
        )

    def test_strategy_iteration_review_lists_validation_command_checklist(self) -> None:
        payload = {
            "symbols": ["QQQ"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {"metrics": {"signalCount": 48, "duplicateFormalCount": 0}, "signals": []},
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("## Validation Command Checklist", report)
        self.assertIn(
            "- Minimum: `.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search`",
            report,
        )
        self.assertIn(
            "- Repo-wide: `.venv\\Scripts\\python.exe -m unittest discover -s tests -p \"test*.py\"`",
            report,
        )
        self.assertIn(
            "- Minimum: `.venv\\Scripts\\python.exe -m py_compile investigations\\bottom_signal_model.py investigations\\bottom_signal_paths.py investigations\\bottom_signal_search.py tests\\test_bottom_signal_search.py`",
            report,
        )
        self.assertIn(
            "- Full search only after search logic/config changes: `.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --max-configs 720 --workers 4`",
            report,
        )
        self.assertIn(
            "10,ValidationCommand,Operator,minimum,Run,.venv\\Scripts\\python.exe -m unittest tests.test_bottom_signal_search",
            csv_text,
        )
        self.assertIn(
            "10,ValidationCommand,Operator,repo-wide,Run,\".venv\\Scripts\\python.exe -m unittest discover -s tests -p \"\"test*.py\"\"\"",
            csv_text,
        )
        self.assertIn(
            "10,ValidationCommand,Operator,full-search,Run only after search logic/config changes,.venv\\Scripts\\python.exe investigations\\bottom_signal_search.py --symbol all --max-configs 720 --workers 4",
            csv_text,
        )

    def test_strategy_iteration_review_reports_main_artifact_manifest(self) -> None:
        payload = {
            "symbols": ["QQQ"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {"metrics": {"signalCount": 48, "duplicateFormalCount": 0}, "signals": []},
            "bestRsWatchlist": {"rsCandidateWatchlist": {"rsTickerSummary": []}},
            "results": [{"config": {"name": "seed_previous_rs_higher_low_best"}, "signals": [], "recentValidation": {}}],
        }
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            present = tmp_path / "bottom_signal_search.py"
            missing = tmp_path / "bottom_signal_results.json"
            present.write_text("# script", encoding="utf-8")

            with patch(
                "investigations.bottom_signal_search.MAIN_ARTIFACT_PATHS",
                [("script", present), ("results", missing)],
            ):
                report = generate_strategy_iteration_review_report(payload)
                csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("## Main Artifact Manifest", report)
        self.assertIn("- PASS script: bottom_signal_search.py exists", report)
        self.assertIn("- FAIL results: bottom_signal_results.json missing", report)
        self.assertIn(
            "11,MainArtifact,Validation,bottom_signal_search.py,Pass,script exists",
            csv_text,
        )
        self.assertIn(
            "11,MainArtifact,Validation,bottom_signal_results.json,Fail,results missing",
            csv_text,
        )

    def test_strategy_iteration_review_reports_strategy_plan_step_status(self) -> None:
        payload = {
            "symbols": [f"S{i:02d}" for i in range(20)] + ["QQQ"],
            "artifactScope": {"fullPool": True, "sampleKind": "FULL_POOL"},
            "bestConfig": {"name": "seed_previous_rs_higher_low_best", "entry_threshold": 82},
            "bestMetrics": {"signalCount": 39, "avgFwd126": 0.3924, "winRate126": 0.7436},
            "observationSearch": {
                "metrics": {"signalCount": 48, "duplicateFormalCount": 0},
                "signals": [
                    {"symbol": "QQQ", "date": "2026-03-27", "observationType": "OBS-S", "riskFlags": "no_repair", "duplicateFormalCount": 0}
                ],
            },
            "bestRsWatchlist": {
                "rsCandidateWatchlist": {
                    "rsTickerSummary": [
                        {"symbol": "AVGO", "actionTier": "Priority", "selectionScore": 92.4, "qualifiedCount": 2},
                        {"symbol": "CRM", "actionTier": "Watch", "selectionScore": 79.7, "qualifiedCount": 2},
                        {"symbol": "CAT", "actionTier": "Avoid", "selectionScore": 50.9, "qualifiedCount": 0},
                    ],
                }
            },
            "results": [
                {
                    "config": {"name": "seed_previous_rs_higher_low_best"},
                    "signals": [{"symbol": "META", "date": "2024-06-01", "fwd126": 0.50, "adverse126": -0.02}],
                    "recentValidation": {
                        "recentValidationStart": "2024-05-01",
                        "recentValidationEnd": "2026-04-30",
                        "recentValidationMatureCount": 7,
                        "recentValidationStatus": "Pass",
                    },
                }
            ],
        }

        report = generate_strategy_iteration_review_report(payload)
        csv_text = generate_strategy_iteration_review_csv(payload)

        self.assertIn("## Strategy Plan Step Status", report)
        self.assertIn("- DONE 1 Baseline confirmation: seed_previous_rs_higher_low_best; symbols=21; signals=39", report)
        self.assertIn("- DONE 2 Recent sample review: mature=7; status=Pass", report)
        self.assertIn("- DONE 3 OBS candidate segmentation: signals=48; riskBuckets=1", report)
        self.assertIn("- DONE 4 RS watchlist review: monitor=1; review=1; skip=1", report)
        self.assertIn("- DONE 5 Formal-missed OBS cases: cases=1", report)
        self.assertIn("- DONE 6 Promotion validation plan: preconditions=4", report)
        self.assertIn(
            "12,PlanStepStatus,Validation,1 Baseline confirmation,Done,seed_previous_rs_higher_low_best; symbols=21; signals=39",
            csv_text,
        )
        self.assertIn(
            "12,PlanStepStatus,Validation,6 Promotion validation plan,Done,preconditions=4",
            csv_text,
        )

    def test_relative_strength_score_rewards_antidrawdown_and_repair(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_score",
            drawdown_window=42,
            rs_drawdown_advantage_threshold=5,
            rs_repair_advantage_threshold=5,
        )
        scored = pd.DataFrame(
            {
                "Open": [100.0, 100.0],
                "High": [101.0, 106.0],
                "Low": [89.0, 98.0],
                "Close": [90.0, 105.0],
                "Volume": [1_000_000, 1_000_000],
                "drawdown_42": [-10.0, -5.0],
                "dist_sma_150": [-12.0, 4.0],
                "bottom_score": [70, 82],
            },
            index=pd.date_range("2024-01-01", periods=2, freq="D"),
        )
        market_drawdown = pd.Series([-8.0, -18.0], index=scored.index)
        market_repair = pd.Series([4.0, 2.0], index=scored.index)

        enriched = add_relative_strength_scores(scored, market_drawdown, market_repair, cfg)

        self.assertTrue(enriched["relative_strength_score"].between(1, 100).all())
        self.assertGreater(
            enriched["relative_strength_score"].iloc[-1],
            enriched["relative_strength_score"].iloc[0],
        )
        self.assertGreater(enriched["rs_signal_score"].iloc[-1], enriched["bottom_score"].iloc[-1])

    def test_rs_higher_low_structure_boosts_rs_signal_score(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_structure",
            drawdown_window=42,
            rs_window=5,
            experimental_signal_set="rs_higher_low_structure",
        )
        index = pd.date_range("2024-01-01", periods=7, freq="D")
        base = pd.DataFrame(
            {
                "Open": [100, 96, 92, 94, 96, 97, 99],
                "High": [101, 97, 93, 95, 97, 98, 101],
                "Low": [99, 90, 88, 91, 93, 94, 96],
                "Close": [100, 92, 90, 94, 96, 97, 100],
                "Volume": [1_000_000] * 7,
                "drawdown_42": [-1, -8, -12, -9, -7, -6, -4],
                "dist_sma_150": [-5, -8, -10, -6, -2, 1, 4],
                "bottom_score": [65, 70, 72, 78, 80, 82, 84],
            },
            index=index,
        )
        market_drawdown = pd.Series([-12, -12, -12, -12, -12, -12, -12], index=index)
        market_repair = pd.Series([1, 1, 1, 1, 1, 1, 1], index=index)

        scored = add_relative_strength_scores(base, market_drawdown, market_repair, cfg)

        self.assertIn("rs_structure_score", scored.columns)
        self.assertGreater(scored["rs_structure_score"].iloc[-1], scored["rs_structure_score"].iloc[2])
        self.assertGreater(scored["rs_signal_score"].iloc[-1], scored["bottom_score"].iloc[-1])

    def test_rs_repair_trend_confirm_boosts_repaired_rs_signal(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_confirm",
            drawdown_window=42,
            ma_period=150,
            macd_fast=8,
            macd_slow=21,
            macd_signal=5,
            rs_window=5,
            experimental_signal_set="rs_repair_trend_confirm",
        )
        index = pd.date_range("2024-01-01", periods=7, freq="D")
        base = pd.DataFrame(
            {
                "Open": [100, 96, 92, 94, 97, 99, 101],
                "High": [101, 97, 93, 96, 99, 102, 104],
                "Low": [99, 90, 88, 91, 94, 96, 99],
                "Close": [100, 92, 90, 95, 98, 101, 103],
                "Volume": [1_000_000] * 7,
                "drawdown_42": [-1, -8, -12, -9, -6, -4, -3],
                "dist_sma_150": [-9, -12, -14, -8, -2, 1, 4],
                "macd_diff_8_21_5": [-2.0, -2.4, -2.2, -1.0, -0.2, 0.4, 0.9],
                "bottom_score": [65, 70, 72, 76, 80, 82, 84],
            },
            index=index,
        )
        market_drawdown = pd.Series([-10, -10, -10, -10, -10, -10, -10], index=index)
        market_repair = pd.Series([1, 1, 1, 1, 1, 1, 1], index=index)

        scored = add_relative_strength_scores(base, market_drawdown, market_repair, cfg)

        self.assertIn("rs_confirmation_score", scored.columns)
        self.assertGreater(scored["rs_confirmation_score"].iloc[-1], scored["rs_confirmation_score"].iloc[2])
        self.assertGreater(scored["rs_signal_score"].iloc[-1], scored["bottom_score"].iloc[-1])

    def test_rs_market_divergence_boosts_stock_holding_up_against_weak_market(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_divergence",
            drawdown_window=42,
            ma_period=150,
            rs_window=5,
            experimental_signal_set="rs_market_divergence",
        )
        index = pd.date_range("2024-01-01", periods=7, freq="D")
        base = pd.DataFrame(
            {
                "Open": [100, 97, 94, 95, 96, 98, 100],
                "High": [101, 98, 95, 97, 99, 101, 103],
                "Low": [98, 91, 89, 92, 94, 96, 98],
                "Close": [100, 93, 91, 95, 97, 100, 102],
                "Volume": [1_000_000] * 7,
                "drawdown_42": [-1, -7, -10, -8, -6, -4, -3],
                "dist_sma_150": [-5, -8, -10, -6, -2, 2, 5],
                "bottom_score": [64, 68, 72, 76, 80, 82, 84],
            },
            index=index,
        )
        market_drawdown = pd.Series([-6, -8, -10, -12, -14, -16, -18], index=index)
        market_repair = pd.Series([1, 1, 1, 1, 1, 1, 1], index=index)

        scored = add_relative_strength_scores(base, market_drawdown, market_repair, cfg)

        self.assertIn("rs_market_divergence_score", scored.columns)
        self.assertGreater(
            scored["rs_market_divergence_score"].iloc[-1],
            scored["rs_market_divergence_score"].iloc[2],
        )
        self.assertGreater(scored["rs_signal_score"].iloc[-1], scored["bottom_score"].iloc[-1])

    def test_rs_post_crash_ma_reclaim_boosts_recovered_stock(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_reclaim",
            drawdown_window=42,
            ma_period=150,
            rs_window=6,
            experimental_signal_set="rs_post_crash_ma_reclaim",
        )
        index = pd.date_range("2024-01-01", periods=10, freq="D")
        base = pd.DataFrame(
            {
                "Open": [100, 96, 91, 86, 88, 91, 94, 97, 100, 103],
                "High": [101, 97, 92, 88, 90, 93, 96, 99, 102, 105],
                "Low": [99, 94, 88, 82, 85, 88, 91, 94, 97, 100],
                "Close": [100, 95, 90, 84, 88, 92, 95, 98, 101, 104],
                "Volume": [1_000_000] * 10,
                "drawdown_42": [-1, -6, -11, -18, -15, -11, -8, -5, -3, -1],
                "dist_sma_150": [-4, -8, -13, -20, -16, -10, -5, 0, 3, 6],
                "bottom_score": [62, 68, 74, 80, 78, 80, 82, 84, 86, 88],
            },
            index=index,
        )
        market_drawdown = pd.Series([-12] * len(index), index=index)
        market_repair = pd.Series([1] * len(index), index=index)

        scored = add_relative_strength_scores(base, market_drawdown, market_repair, cfg)

        self.assertIn("rs_ma_reclaim_score", scored.columns)
        self.assertGreater(scored["rs_ma_reclaim_score"].iloc[-1], scored["rs_ma_reclaim_score"].iloc[3])
        self.assertGreater(scored["rs_signal_score"].iloc[-1], scored["rs_signal_score"].iloc[3])

    def test_rs_volatility_compression_boosts_post_panic_stabilization(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_vol_compress",
            drawdown_window=42,
            atr_period=10,
            ma_period=150,
            rs_window=6,
            experimental_signal_set="rs_volatility_compression",
        )
        index = pd.date_range("2024-01-01", periods=10, freq="D")
        base = pd.DataFrame(
            {
                "Open": [100, 95, 90, 84, 86, 89, 92, 95, 98, 101],
                "High": [101, 97, 93, 88, 89, 92, 95, 98, 101, 104],
                "Low": [98, 91, 85, 79, 82, 86, 89, 92, 95, 98],
                "Close": [100, 94, 88, 82, 86, 90, 93, 96, 99, 102],
                "Volume": [1_000_000] * 10,
                "drawdown_42": [-1, -7, -13, -22, -18, -14, -10, -7, -4, -2],
                "dist_sma_150": [-4, -8, -14, -22, -18, -12, -7, -2, 2, 5],
                "atr_10": [3.0, 4.0, 6.0, 9.0, 8.0, 6.0, 4.8, 4.0, 3.4, 3.0],
                "bottom_score": [62, 68, 74, 82, 80, 82, 84, 86, 88, 90],
            },
            index=index,
        )
        market_drawdown = pd.Series([-15] * len(index), index=index)
        market_repair = pd.Series([1] * len(index), index=index)

        scored = add_relative_strength_scores(base, market_drawdown, market_repair, cfg)

        self.assertIn("rs_volatility_compression_score", scored.columns)
        self.assertGreater(
            scored["rs_volatility_compression_score"].iloc[-1],
            scored["rs_volatility_compression_score"].iloc[3],
        )
        self.assertGreater(scored["rs_signal_score"].iloc[-1], scored["rs_signal_score"].iloc[3])

    def test_rs_pullback_repair_v2_rewards_strong_stock_pullback_repair(self) -> None:
        cfg = BottomSignalConfig(
            name="rs_pullback",
            drawdown_window=42,
            ma_period=100,
            rs_window=6,
            rs_pullback_window=6,
            rs_pullback_min_drawdown=5,
            rs_pullback_max_drawdown=18,
            experimental_signal_set="rs_pullback_repair_v2",
        )
        index = pd.date_range("2024-01-01", periods=10, freq="D")
        base = pd.DataFrame(
            {
                "Open": [100, 104, 108, 112, 110, 106, 103, 106, 109, 112],
                "High": [102, 106, 110, 114, 112, 108, 105, 108, 111, 115],
                "Low": [99, 103, 107, 110, 107, 102, 100, 104, 107, 110],
                "Close": [101, 105, 109, 113, 109, 104, 102, 107, 110, 114],
                "Volume": [1_000_000] * 10,
                "drawdown_42": [-1, -1, -1, -1, -4, -8, -10, -6, -3, -1],
                "dist_sma_100": [4, 6, 8, 10, 7, 3, 1, 4, 7, 10],
                "bottom_score": [55, 58, 60, 62, 68, 74, 78, 80, 82, 84],
            },
            index=index,
        )
        market_drawdown = pd.Series([-8, -8, -8, -9, -10, -12, -13, -12, -10, -9], index=index)
        market_repair = pd.Series([1] * len(index), index=index)

        scored = add_relative_strength_scores(base, market_drawdown, market_repair, cfg)

        self.assertIn("rs_pullback_score", scored.columns)
        self.assertGreater(scored["rs_pullback_score"].iloc[-1], scored["rs_pullback_score"].iloc[2])
        self.assertGreater(scored["rs_signal_score"].iloc[-1], scored["rs_signal_score"].iloc[2])

    def test_dual_track_positions_keep_mb_strict_and_rs_independent(self) -> None:
        cfg = BottomSignalConfig(
            name="dual_track",
            watch_threshold=65,
            medium_threshold=74,
            entry_threshold=82,
            min_signal_gap=1,
        )
        scored = pd.DataFrame(
            {
                "bottom_score": [84, 84, 84],
                "relative_strength_score": [40, 90, 90],
                "rs_signal_score": [64, 87, 87],
            },
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        market_context = pd.Series([-5.0, -5.0, -25.0], index=scored.index)
        validation = {"require_market_context": True, "market_drawdown_threshold": -20}

        positions = select_dual_track_positions(scored, cfg, market_context, validation)

        self.assertEqual(positions["mb_strong"], [2])
        self.assertEqual(positions["rs_strong"], [1, 2])

    def test_mb_entry_can_be_stricter_than_rs_entry(self) -> None:
        cfg = BottomSignalConfig(
            name="split_entry",
            watch_threshold=70,
            medium_threshold=80,
            entry_threshold=82,
            mb_entry_offset=3,
            min_signal_gap=1,
        )
        scored = pd.DataFrame(
            {
                "bottom_score": [84],
                "relative_strength_score": [95],
                "rs_signal_score": [84],
            },
            index=pd.date_range("2024-01-01", periods=1, freq="D"),
        )
        market_context = pd.Series([-25.0], index=scored.index)

        positions = select_dual_track_positions(
            scored,
            cfg,
            market_context,
            {"require_market_context": True, "market_drawdown_threshold": -20},
        )

        self.assertEqual(mb_entry_threshold(cfg), 85)
        self.assertEqual(rs_entry_threshold(cfg), 82)
        self.assertEqual(positions["mb_strong"], [])
        self.assertEqual(positions["rs_strong"], [0])

    def test_watch_medium_are_diagnostic_not_formal_strong(self) -> None:
        cfg = BottomSignalConfig(
            name="funnel",
            watch_threshold=65,
            medium_threshold=74,
            entry_threshold=82,
            min_signal_gap=1,
        )
        scored = pd.DataFrame(
            {
                "bottom_score": [66, 78, 84],
                "relative_strength_score": [70, 82, 88],
                "rs_signal_score": [68, 80, 86],
            },
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        market_context = pd.Series([-25.0, -25.0, -25.0], index=scored.index)

        positions = select_dual_track_positions(
            scored,
            cfg,
            market_context,
            {"require_market_context": True, "market_drawdown_threshold": -20},
        )
        summary = summarize_signal_funnel(
            [
                {"channel": "MB", "tier": "Strong"},
                {"channel": "RS", "tier": "Strong"},
            ],
            [
                {"channel": "MB", "tier": "Watch"},
                {"channel": "RS", "tier": "Medium"},
            ],
        )

        self.assertEqual(positions["mb_watch"], [0])
        self.assertEqual(positions["mb_medium"], [1])
        self.assertEqual(positions["mb_strong"], [2])
        self.assertEqual(summary["formalStrongCount"], 2)
        self.assertEqual(summary["diagnosticWatchMediumCount"], 2)

    def test_watch_medium_ratio_gate_penalizes_too_many_diagnostics(self) -> None:
        settings = {"watch_medium_target_multiplier": [2, 4]}

        self.assertEqual(apply_watch_medium_ratio_gate(80, 3.0, settings), 80)
        self.assertLess(apply_watch_medium_ratio_gate(80, 4.5, settings), 80)
        self.assertLess(apply_watch_medium_ratio_gate(80, 1.0, settings), 80)

    def test_relative_strength_capture_preference_rewards_missed_cases(self) -> None:
        settings = {"rs_missed_capture_target": 4}

        weak = apply_relative_strength_capture_preference(80, missed_count=0, settings=settings)
        strong = apply_relative_strength_capture_preference(80, missed_count=4, settings=settings)

        self.assertLess(weak, 80)
        self.assertEqual(strong, 80)

    def test_relative_strength_capture_can_be_required(self) -> None:
        settings = {"require_rs_missed_capture": True, "rs_missed_capture_target": 1}

        self.assertEqual(
            apply_relative_strength_capture_preference(80, missed_count=0, settings=settings),
            0,
        )
        self.assertEqual(
            apply_relative_strength_capture_preference(80, missed_count=1, settings=settings),
            80,
        )

    def test_refine_promoted_configs_adds_entry_threshold_variants(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)
        base = BottomSignalConfig(name="base_entry82", entry_threshold=82)
        stage_results = [{"config": {"name": "base_entry82"}, "metrics": {"compositeScore": 10}}]

        refined = refine_promoted_configs([base], stage_results, settings)
        thresholds = {config.entry_threshold for config in refined}

        self.assertIn(82, thresholds)
        self.assertIn(85, thresholds)
        self.assertTrue(any("_entry85" in config.name for config in refined))

    def test_baseline_quality_preference_penalizes_large_return_drop(self) -> None:
        metrics = {"compositeScore": 80, "avgFwd126": 0.35, "winRate126": 0.77}
        baseline = {"avgFwd126": 0.46, "winRate126": 0.80}
        settings = {"baseline_quality_min_ratio": 0.85}

        adjusted = apply_baseline_quality_preference(metrics, baseline, settings)

        self.assertLess(adjusted["compositeScore"], 80)
        self.assertIn("baselineQualityScore", adjusted)

    def test_recent_channel_activity_summarizes_recent_mb_and_rs(self) -> None:
        formal = [
            {"date": "2023-01-01", "channel": "RS", "tier": "Strong", "fwd126": 0.50},
            {"date": "2025-04-04", "channel": "MB", "tier": "Strong", "fwd126": 0.40},
            {"date": "2025-04-17", "channel": "RS", "tier": "Strong", "fwd126": 0.20},
        ]
        diagnostic = [
            {"date": "2025-03-10", "channel": "RS", "tier": "Watch", "fwd126": 0.10},
            {"date": "2025-04-07", "channel": "MB", "tier": "Medium", "fwd126": 0.30},
        ]

        summary = summarize_recent_channel_activity(
            formal,
            diagnostic,
            days=730,
            end_date="2026-04-30",
        )

        self.assertEqual(summary["recentStart"], "2024-05-01")
        self.assertEqual(summary["recentEnd"], "2026-04-30")
        self.assertEqual(summary["recentMbStrongCount"], 1)
        self.assertEqual(summary["recentRsStrongCount"], 1)
        self.assertEqual(summary["recentMbDiagnosticCount"], 1)
        self.assertEqual(summary["recentRsDiagnosticCount"], 1)
        self.assertEqual(summary["recentRsCandidateCount"], 2)
        self.assertAlmostEqual(summary["recentRsAvgFwd126"], 0.15)

    def test_recent_rs_activity_preference_penalizes_softly(self) -> None:
        metrics = {"compositeScore": 80.0}
        recent = {
            "recentRsCandidateCount": 0,
            "recentRsDiagnosticCount": 0,
            "recentRsAvgFwd126": 0.0,
        }
        settings = {
            "rs_recent_candidate_targets": [2, 8],
            "rs_recent_diagnostic_targets": [8, 20],
            "rs_recent_avg_fwd126_min": 0.15,
        }

        adjusted = apply_recent_rs_activity_preference(metrics, recent, settings)

        self.assertGreater(adjusted["compositeScore"], 0)
        self.assertLess(adjusted["compositeScore"], 80)
        self.assertEqual(adjusted["recentRsActivityScore"], 0)

    def test_qualified_rs_watchlist_preference_penalizes_low_coverage_softly(self) -> None:
        metrics = {"compositeScore": 80.0}
        watchlist = {
            "qualifiedRsCandidateCount": 2,
            "qualifiedRsCandidateAvgFwd126": 0.25,
            "qualifiedRsCandidateAvgAdverse126": -0.05,
        }
        settings = {
            "qualified_rs_candidate_targets": [4, 10],
            "qualified_rs_avg_fwd126_min": 0.15,
            "qualified_rs_avg_adverse126_min": -0.12,
        }

        adjusted = apply_qualified_rs_watchlist_preference(metrics, watchlist, settings)

        self.assertGreater(adjusted["compositeScore"], 0)
        self.assertLess(adjusted["compositeScore"], 80)
        self.assertEqual(adjusted["qualifiedRsWatchlistScore"], 50)

    def test_qualified_rs_watchlist_preference_keeps_score_when_coverage_and_quality_pass(self) -> None:
        metrics = {"compositeScore": 80.0}
        watchlist = {
            "qualifiedRsCandidateCount": 5,
            "qualifiedRsCandidateAvgFwd126": 0.25,
            "qualifiedRsCandidateAvgAdverse126": -0.05,
        }
        settings = {
            "qualified_rs_candidate_targets": [4, 10],
            "qualified_rs_avg_fwd126_min": 0.15,
            "qualified_rs_avg_adverse126_min": -0.12,
        }

        adjusted = apply_qualified_rs_watchlist_preference(metrics, watchlist, settings)

        self.assertEqual(adjusted["compositeScore"], 80)
        self.assertEqual(adjusted["qualifiedRsWatchlistScore"], 100)

    def test_top_rs_coverage_tradeoffs_prioritizes_qualified_coverage(self) -> None:
        results = [
            {
                "config": {"name": "low_coverage"},
                "metrics": {"compositeScore": 30, "signalCount": 20},
                "rsCandidateWatchlist": {
                    "qualifiedRsCandidateCount": 2,
                    "qualifiedRsCandidateAvgFwd126": 0.30,
                    "qualifiedRsCandidateAvgAdverse126": -0.05,
                },
            },
            {
                "config": {"name": "high_coverage"},
                "metrics": {"compositeScore": 0, "signalCount": 38},
                "rsCandidateWatchlist": {
                    "qualifiedRsCandidateCount": 8,
                    "qualifiedRsCandidateAvgFwd126": 0.25,
                    "qualifiedRsCandidateAvgAdverse126": -0.04,
                },
            },
        ]

        tradeoffs = top_rs_coverage_tradeoffs(results, limit=1)

        self.assertEqual(tradeoffs[0]["name"], "high_coverage")
        self.assertEqual(tradeoffs[0]["qualifiedRsCandidateCount"], 8)

    def test_select_best_rs_watchlist_result_is_separate_from_composite_best(self) -> None:
        results = [
            {
                "config": {"name": "mb_best", "experimental_signal_set": "rs_higher_low_structure"},
                "metrics": {"compositeScore": 30, "signalCount": 39, "avgFwd126": 0.39},
                "rsCandidateWatchlist": {
                    "qualifiedRsCandidateCount": 2,
                    "qualifiedRsCandidateAvgFwd126": 0.26,
                    "qualifiedRsCandidateAvgAdverse126": -0.05,
                },
            },
            {
                "config": {"name": "rs_best", "experimental_signal_set": "rs_antidrawdown_repair"},
                "metrics": {"compositeScore": 0, "signalCount": 38, "avgFwd126": 0.43},
                "rsCandidateWatchlist": {
                    "qualifiedRsCandidateCount": 12,
                    "qualifiedRsCandidateAvgFwd126": 0.72,
                    "qualifiedRsCandidateAvgAdverse126": -0.04,
                    "topRsCandidates": [{"symbol": "AAPL"}],
                },
            },
        ]

        selected = select_best_rs_watchlist_result(results)

        self.assertEqual(selected["config"]["name"], "rs_best")
        self.assertEqual(selected["role"], "rs_watchlist_only")
        self.assertEqual(selected["rsCandidateWatchlist"]["qualifiedRsCandidateCount"], 12)

    def test_refresh_best_rs_watchlist_scan_uses_single_existing_config(self) -> None:
        settings = SearchSettings(
            max_configs=1,
            cache_indicators=False,
            search_stages={},
            candidate_parameters={},
            seed_configs=[],
            thresholds={},
            weights={},
            weight_profiles=[],
            objective_weights={"bottom_quality": 0.7},
            validation={"rs_watchlist_quality_threshold": 70},
        )
        payload = {
            "bestConfig": {"name": "mb_formal"},
            "bestRsWatchlist": {
                "role": "rs_watchlist_only",
                "config": {"name": "rs_existing"},
            },
        }
        calls = []

        def fake_precomputer(symbols, configs, cache_enabled=True):
            calls.append((symbols, configs, cache_enabled))
            return {"AAPL": pd.DataFrame(), "MSFT": pd.DataFrame()}

        def fake_evaluator(
            symbols,
            config,
            indicator_frames=None,
            objective_weights=None,
            validation=None,
        ):
            self.assertEqual(symbols, ["AAPL", "MSFT"])
            self.assertEqual(config.name, "rs_existing")
            self.assertEqual(objective_weights, {"bottom_quality": 0.7})
            self.assertEqual(validation, {"rs_watchlist_quality_threshold": 70})
            return {
                "config": {"name": config.name},
                "metrics": {"compositeScore": 0.0},
                "rsCandidateWatchlist": {
                    "qualifiedRsCandidateCount": 3,
                    "topRsCandidates": [{"symbol": "AAPL"}],
                },
            }

        refreshed = refresh_best_rs_watchlist_scan(
            payload,
            ["AAPL", "MSFT"],
            settings,
            evaluator=fake_evaluator,
            indicator_precomputer=fake_precomputer,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], ["AAPL", "MSFT"])
        self.assertEqual(calls[0][1][0].name, "rs_existing")
        self.assertFalse(calls[0][2])
        self.assertEqual(refreshed["bestRsWatchlist"]["role"], "rs_watchlist_only")
        self.assertEqual(
            refreshed["bestRsWatchlist"]["rsCandidateWatchlist"]["qualifiedRsCandidateCount"],
            3,
        )
        self.assertEqual(refreshed["rsWatchlistRefresh"]["mode"], "single_config")

    def test_refresh_supplemental_analysis_rebuilds_ablation_and_recent_validation(self) -> None:
        settings = SearchSettings(
            max_configs=1,
            cache_indicators=False,
            search_stages={},
            candidate_parameters={},
            seed_configs=[],
            thresholds={},
            weights={},
            weight_profiles=[],
            objective_weights={"bottom_quality": 0.7},
            validation={
                "recent_activity_days": 730,
                "recent_activity_end_date": "2026-04-30",
            },
        )
        config = BottomSignalConfig(name="best")
        payload = {
            "bestConfig": dict(config.__dict__),
            "results": [
                {
                    "config": {"name": "best"},
                    "signals": [
                        {
                            "date": "2025-04-01",
                            "fwd126": 0.20,
                            "adverse126": -0.04,
                        }
                    ],
                }
            ],
        }

        def fake_precomputer(symbols, configs, cache_enabled=True):
            return {symbol: pd.DataFrame() for symbol in symbols}

        def fake_evaluator(
            symbols,
            config,
            indicator_frames=None,
            objective_weights=None,
            validation=None,
        ):
            return {
                "config": dict(config.__dict__),
                "metrics": {
                    "compositeScore": 10.0 if config.name == "best" else 8.0,
                    "signalCount": 2,
                    "avgFwd126": 0.12,
                    "avgAdverse126": -0.05,
                },
            }

        refreshed = refresh_supplemental_analysis(
            payload,
            ["AAPL"],
            settings,
            evaluator=fake_evaluator,
            indicator_precomputer=fake_precomputer,
        )

        self.assertEqual(len(refreshed["mbFactorAblation"]["rows"]), 6)
        self.assertEqual(refreshed["supplementalAnalysisRefresh"]["mode"], "supplemental_analysis")
        self.assertEqual(
            refreshed["results"][0]["recentValidation"]["recentValidationStatus"],
            "Watch",
        )

    def test_rs_candidate_watchlist_keeps_recent_highest_scored_candidates(self) -> None:
        formal = [
            {
                "symbol": "AAPL",
                "date": "2025-04-04",
                "channel": "MB",
                "tier": "Strong",
                "bottomScore": 90,
                "relativeStrengthScore": 40,
                "rsSignalScore": 50,
                "fwd126": 0.20,
                "adverse126": -0.05,
            },
            {
                "symbol": "MSFT",
                "date": "2025-04-10",
                "channel": "RS",
                "tier": "Strong",
                "bottomScore": 76,
                "relativeStrengthScore": 93,
                "rsSignalScore": 88,
                "riskFlags": "",
                "fwd126": 0.30,
                "adverse126": -0.06,
            },
        ]
        diagnostic = [
            {
                "symbol": "NVDA",
                "date": "2025-04-12",
                "channel": "RS",
                "tier": "Medium",
                "bottomScore": 70,
                "relativeStrengthScore": 96,
                "rsSignalScore": 86,
                "riskFlags": "",
                "fwd126": 0.50,
                "adverse126": -0.08,
            },
            {
                "symbol": "META",
                "date": "2023-01-01",
                "channel": "RS",
                "tier": "Watch",
                "bottomScore": 68,
                "relativeStrengthScore": 98,
                "rsSignalScore": 84,
                "riskFlags": "",
                "fwd126": 0.40,
                "adverse126": -0.04,
            },
        ]

        summary = summarize_rs_candidate_watchlist(
            formal,
            diagnostic,
            days=730,
            end_date="2026-04-30",
            limit=2,
        )

        self.assertEqual(summary["rsCandidateCount"], 2)
        self.assertAlmostEqual(summary["rsCandidateAvgFwd126"], 0.40)
        self.assertEqual([item["symbol"] for item in summary["topRsCandidates"]], ["NVDA", "MSFT"])
        self.assertNotIn("AAPL", [item["symbol"] for item in summary["topRsCandidates"]])
        self.assertNotIn("META", [item["symbol"] for item in summary["topRsCandidates"]])
        self.assertTrue(all("qualityScore" in item for item in summary["topRsCandidates"]))

    def test_rs_candidate_quality_score_penalizes_risky_candidates(self) -> None:
        clean = {
            "tier": "Medium",
            "bottomScore": 74,
            "relativeStrengthScore": 88,
            "rsSignalScore": 82,
            "riskFlags": "",
        }
        risky = {
            "tier": "Medium",
            "bottomScore": 74,
            "relativeStrengthScore": 98,
            "rsSignalScore": 90,
            "riskFlags": "trend_damage,no_repair,low_volume",
        }
        overextended = {
            "tier": "Medium",
            "bottomScore": 74,
            "relativeStrengthScore": 98,
            "rsSignalScore": 90,
            "riskFlags": "overextended_rebound",
        }

        self.assertGreater(rs_candidate_quality_score(clean), rs_candidate_quality_score(risky))
        self.assertGreater(rs_candidate_quality_score(clean), rs_candidate_quality_score(overextended))

    def test_rs_candidate_watchlist_reports_quality_filtered_subset(self) -> None:
        candidates = [
            {
                "symbol": "SAFE",
                "date": "2025-04-12",
                "channel": "RS",
                "tier": "Medium",
                "bottomScore": 74,
                "relativeStrengthScore": 90,
                "rsSignalScore": 84,
                "riskFlags": "",
                "fwd126": 0.30,
                "adverse126": -0.05,
            },
            {
                "symbol": "RISK",
                "date": "2025-04-13",
                "channel": "RS",
                "tier": "Medium",
                "bottomScore": 78,
                "relativeStrengthScore": 99,
                "rsSignalScore": 88,
                "riskFlags": "trend_damage,no_repair",
                "fwd126": -0.10,
                "adverse126": -0.25,
            },
        ]

        summary = summarize_rs_candidate_watchlist(
            [],
            candidates,
            days=730,
            end_date="2026-04-30",
            limit=2,
            quality_threshold=70,
        )

        self.assertEqual(summary["rsCandidateCount"], 2)
        self.assertEqual(summary["qualifiedRsCandidateCount"], 1)
        self.assertEqual(summary["topRsCandidates"][0]["symbol"], "SAFE")
        self.assertTrue(summary["topRsCandidates"][0]["qualityPassed"])
        self.assertFalse(summary["topRsCandidates"][1]["qualityPassed"])
        self.assertEqual(summary["rsTickerSummary"][0]["symbol"], "SAFE")
        self.assertEqual(summary["rsTickerSummary"][0]["qualifiedCount"], 1)

    def test_rs_ticker_watchlist_summary_groups_repeated_strong_stocks(self) -> None:
        candidates = [
            {
                "symbol": "NVDA",
                "date": "2025-04-07",
                "qualityScore": 72,
                "qualityPassed": True,
                "relativeStrengthScore": 88,
                "rsSignalScore": 78,
                "riskFlags": "",
                "fwd126": 0.30,
                "adverse126": -0.04,
            },
            {
                "symbol": "NVDA",
                "date": "2025-04-09",
                "qualityScore": 78,
                "qualityPassed": True,
                "relativeStrengthScore": 92,
                "rsSignalScore": 82,
                "riskFlags": "",
                "fwd126": 0.40,
                "adverse126": -0.02,
            },
            {
                "symbol": "RISK",
                "date": "2025-04-10",
                "qualityScore": 55,
                "qualityPassed": False,
                "relativeStrengthScore": 95,
                "rsSignalScore": 85,
                "riskFlags": "no_repair",
                "fwd126": -0.10,
                "adverse126": -0.20,
            },
        ]

        summary = summarize_rs_ticker_watchlist(candidates)

        self.assertEqual(summary[0]["symbol"], "NVDA")
        self.assertEqual(summary[0]["candidateCount"], 2)
        self.assertEqual(summary[0]["qualifiedCount"], 2)
        self.assertAlmostEqual(summary[0]["avgFwd126"], 0.35)
        self.assertEqual(summary[0]["bestDate"], "2025-04-09")
        self.assertEqual(summary[0]["actionTier"], "Priority")
        self.assertEqual(summary[0]["selectionRank"], 1)
        self.assertEqual(summary[1]["riskFlaggedCount"], 1)
        self.assertEqual(summary[1]["actionTier"], "Avoid")
        self.assertEqual(summary[1]["selectionRank"], 2)
        self.assertEqual(
            rs_ticker_action_counts(summary),
            {"Priority": 1, "Watch": 0, "Avoid": 1},
        )
        self.assertGreater(summary[0]["selectionScore"], summary[1]["selectionScore"])

    def test_rs_selection_score_rewards_quality_and_penalizes_risk(self) -> None:
        strong = rs_selection_score(
            qualified_count=2,
            candidate_count=2,
            avg_quality=76,
            best_quality=82,
            avg_adverse_126=-0.04,
            risk_count=0,
        )
        risky = rs_selection_score(
            qualified_count=2,
            candidate_count=2,
            avg_quality=76,
            best_quality=82,
            avg_adverse_126=-0.18,
            risk_count=2,
        )

        self.assertGreater(strong, risky)

    def test_rs_ticker_summary_rank_sorts_by_selection_score(self) -> None:
        summary = rank_rs_ticker_summary(
            [
                {
                    "symbol": "LOW",
                    "qualifiedCount": 0,
                    "candidateCount": 1,
                    "avgQualityScore": 55.0,
                    "bestQualityScore": 55,
                    "avgAdverse126": -0.20,
                    "riskFlaggedCount": 1,
                },
                {
                    "symbol": "HIGH",
                    "qualifiedCount": 2,
                    "candidateCount": 2,
                    "avgQualityScore": 80.0,
                    "bestQualityScore": 84,
                    "avgAdverse126": -0.04,
                    "riskFlaggedCount": 0,
                },
            ]
        )

        self.assertEqual(summary[0]["symbol"], "HIGH")
        self.assertEqual(summary[0]["selectionRank"], 1)
        self.assertEqual(summary[1]["selectionRank"], 2)

    def test_rs_ticker_action_tier_is_observation_only_priority_label(self) -> None:
        self.assertEqual(
            rs_ticker_action_tier(
                qualified_count=2,
                avg_quality=74,
                avg_adverse_126=-0.04,
                risk_count=0,
            ),
            "Priority",
        )
        self.assertEqual(
            rs_ticker_action_tier(
                qualified_count=1,
                avg_quality=66,
                avg_adverse_126=-0.08,
                risk_count=1,
            ),
            "Watch",
        )
        self.assertEqual(
            rs_ticker_action_tier(
                qualified_count=0,
                avg_quality=58,
                avg_adverse_126=-0.15,
                risk_count=2,
            ),
            "Avoid",
        )

    def test_rs_ticker_action_reason_explains_observation_label(self) -> None:
        self.assertEqual(
            rs_ticker_action_reason(
                action_tier="Priority",
                qualified_count=2,
                avg_quality=74,
                avg_adverse_126=-0.04,
                risk_count=0,
            ),
            "repeated qualified candidates with clean risk profile",
        )
        self.assertEqual(
            rs_ticker_action_reason(
                action_tier="Watch",
                qualified_count=1,
                avg_quality=66,
                avg_adverse_126=-0.08,
                risk_count=1,
            ),
            "qualified but has risk flags",
        )
        self.assertEqual(
            rs_ticker_action_reason(
                action_tier="Avoid",
                qualified_count=0,
                avg_quality=58,
                avg_adverse_126=-0.15,
                risk_count=2,
            ),
            "no qualified RS candidates",
        )

    def test_selected_signal_rows_uses_entry_threshold_not_watch(self) -> None:
        cfg = BottomSignalConfig(
            name="entry_threshold_test",
            watch_threshold=35,
            medium_threshold=55,
            strong_threshold=75,
            entry_threshold=55,
            min_signal_gap=1,
        )
        scored = pd.DataFrame(
            {
                "bottom_score": [40, 54, 55, 80],
                "signal_label": ["Watch", "Watch", "Medium", "Strong"],
            }
        )

        self.assertEqual(selected_signal_rows(scored, cfg), [2, 3])

    def test_load_search_settings_from_json_config(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)

        self.assertIn(252, settings.candidate_parameters["drawdown_windows"])
        self.assertIn([12, 26, 9], settings.candidate_parameters["macd_configs"])
        self.assertEqual(settings.thresholds["medium"], 55)
        self.assertAlmostEqual(settings.objective_weights["bottom_quality"], 0.70)
        self.assertTrue(settings.search_stages["enabled"])

    def test_collect_indicator_spec_unions_candidate_parameters(self) -> None:
        configs = [
            BottomSignalConfig(name="a", rsi_period=7, ma_period=100, volume_window=10),
            BottomSignalConfig(name="b", rsi_period=21, ma_period=200, volume_window=50),
        ]

        spec = collect_indicator_spec(configs)

        self.assertEqual(spec["rsi"], [7, 21])
        self.assertEqual(spec["sma"], [100, 200])
        self.assertEqual(spec["distance_to_sma"], [100, 200])
        self.assertEqual(spec["volume"], [10, 50])

    def test_candidate_configs_apply_weight_profiles_from_settings(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)

        configs = candidate_configs(20, settings=settings)

        self.assertTrue(any(config.drawdown_weight != 0.30 for config in configs))

    def test_candidate_configs_apply_signal_gap_candidates_from_settings(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)

        configs = candidate_configs(40, settings=settings)

        self.assertTrue(any(config.min_signal_gap != 21 for config in configs))

    def test_candidate_configs_apply_entry_threshold_candidates_from_settings(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)

        configs = candidate_configs(80, settings=settings)

        self.assertTrue(any(config.entry_threshold != 82 for config in configs))

    def test_candidate_configs_include_seed_configs_from_settings(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)

        configs = candidate_configs(5, settings=settings)

        self.assertTrue(any(config.name == "seed_previous_rs_higher_low_best" for config in configs))

    def test_seed_configs_are_always_promoted_after_stage_filter(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)
        stage_results = [{"config": {"name": "stage_winner"}, "metrics": {"compositeScore": 10}}]

        names = promoted_stage_names(stage_results, promote_top_n=1, settings=settings)

        self.assertIn("stage_winner", names)
        self.assertIn("seed_previous_rs_higher_low_best", names)

    def test_relaxed_stage_settings_removes_full_universe_hard_gates(self) -> None:
        settings = load_search_settings(DEFAULT_CONFIG_PATH)

        relaxed = relaxed_stage_settings(settings)

        self.assertFalse(relaxed.validation["require_validation_coverage"])
        self.assertFalse(relaxed.validation["require_validation_window_coverage"])
        self.assertFalse(relaxed.validation["require_signal_count_max"])
        self.assertFalse(relaxed.validation["require_bottom_capture_rate_limit"])

    def test_precompute_indicator_frames_builds_once_per_symbol(self) -> None:
        calls = []

        def fake_builder(frame: pd.DataFrame, spec: dict) -> pd.DataFrame:
            calls.append(spec)
            enriched = frame.copy()
            enriched["rsi_7"] = 50.0
            return enriched

        def fake_loader(symbol: str) -> pd.DataFrame:
            self.assertEqual(symbol, "QQQ")
            return indicator_frame()[["Open", "High", "Low", "Close", "Volume"]]

        with TemporaryDirectory() as temp_dir:
            frames = precompute_indicator_frames(
                ["QQQ"],
                [BottomSignalConfig(name="a", rsi_period=7)],
                cache_enabled=False,
                cache_dir=Path(temp_dir),
                data_loader=fake_loader,
                indicator_builder=fake_builder,
            )

        self.assertEqual(len(calls), 1)
        self.assertIn("QQQ", frames)
        self.assertIn("rsi_7", frames["QQQ"].columns)

    def test_sparse_count_score_penalizes_overtrading(self) -> None:
        settings = {"signal_count_min": 20, "signal_count_target": 80, "signal_count_max": 160}

        self.assertGreater(
            sparse_count_score(80, settings),
            sparse_count_score(400, settings),
        )
        self.assertGreater(
            sparse_count_score(80, settings),
            sparse_count_score(5, settings),
        )

    def test_summarize_validation_groups_separates_index_and_individuals(self) -> None:
        signals = [
            {"symbol": "QQQ", "fwd126": 0.20, "fwd252": 0.30},
            {"symbol": "SPY", "fwd126": 0.10, "fwd252": 0.20},
            {"symbol": "AAPL", "fwd126": 0.40, "fwd252": 0.60},
        ]

        summary = summarize_validation_groups(signals, ["QQQ", "SPY"])

        self.assertEqual(summary["indexSignalCount"], 2)
        self.assertEqual(summary["individualSignalCount"], 1)
        self.assertAlmostEqual(summary["indexAvgFwd126"], 0.15)
        self.assertAlmostEqual(summary["individualAvgFwd126"], 0.40)

    def test_validation_coverage_score_requires_index_and_individual_samples(self) -> None:
        settings = {"index_signal_min": 4, "individual_signal_min": 40}

        weak = validation_coverage_score(2, 80, settings)
        strong = validation_coverage_score(4, 80, settings)

        self.assertLess(weak, strong)
        self.assertEqual(strong, 100.0)

    def test_validation_coverage_gate_discounts_incomplete_cross_validation(self) -> None:
        settings = {"require_validation_coverage": True}

        self.assertEqual(apply_validation_coverage_gate(80, 100, settings), 80)
        self.assertEqual(apply_validation_coverage_gate(80, 50, settings), 40)

    def test_signal_count_gate_discounts_overactive_configs(self) -> None:
        settings = {"require_signal_count_max": True, "signal_count_max": 180}

        self.assertEqual(apply_signal_count_gate(80, 120, settings), 80)
        self.assertLess(apply_signal_count_gate(80, 360, settings), 80)

    def test_signal_count_gate_can_hard_reject_overactive_configs(self) -> None:
        settings = {
            "require_signal_count_max": True,
            "require_signal_count_hard_max": True,
            "signal_count_max": 40,
        }

        self.assertEqual(apply_signal_count_gate(80, 40, settings), 80)
        self.assertEqual(apply_signal_count_gate(80, 41, settings), 0)

    def test_market_context_filter_keeps_only_broad_drawdown_dates(self) -> None:
        scored = pd.DataFrame(
            {"bottom_score": [90, 90, 90]},
            index=pd.date_range("2024-01-01", periods=3, freq="D"),
        )
        market_context = pd.Series(
            [-4.0, -12.0, -20.0],
            index=scored.index,
        )
        settings = {"require_market_context": True, "market_drawdown_threshold": -10}

        positions = filter_positions_by_market_context([0, 1, 2], scored, market_context, settings)

        self.assertEqual(positions, [1, 2])

    def test_forward_win_rate_ignores_unmatured_signals(self) -> None:
        signals = [
            {"fwd126": 0.10},
            {"fwd126": -0.05},
            {"fwd126": None},
            {"fwd126": 0.20},
        ]

        self.assertAlmostEqual(forward_win_rate(signals, "fwd126"), 2 / 3)

    def test_adverse_tail_rate_counts_large_bad_drawdowns(self) -> None:
        signals = [
            {"adverse126": -0.10},
            {"adverse126": -0.25},
            {"adverse126": -0.40},
            {"adverse126": None},
        ]

        self.assertAlmostEqual(adverse_tail_rate(signals, threshold=-0.25), 2 / 3)

    def test_market_repair_score_rewards_repair_without_hard_filter(self) -> None:
        self.assertEqual(market_repair_score(0, target=3), 0)
        self.assertGreater(market_repair_score(2, target=3), 0)
        self.assertEqual(market_repair_score(4, target=3), 100)

    def test_summarize_date_split_validation_separates_holdout_groups(self) -> None:
        signals = [
            {"symbol": "QQQ", "date": "2020-03-20", "fwd126": 0.20, "adverse126": -0.10},
            {"symbol": "SPY", "date": "2023-03-13", "fwd126": 0.12, "adverse126": -0.06},
            {"symbol": "AAPL", "date": "2023-04-10", "fwd126": 0.32, "adverse126": -0.08},
            {"symbol": "MSFT", "date": "2024-08-05", "fwd126": None, "adverse126": None},
        ]

        summary = summarize_date_split_validation(
            signals,
            cutoff_date="2022-12-31",
            index_symbols=["QQQ", "SPY"],
        )

        self.assertEqual(summary["trainSignalCount"], 1)
        self.assertEqual(summary["holdoutSignalCount"], 3)
        self.assertEqual(summary["holdoutIndexSignalCount"], 1)
        self.assertEqual(summary["holdoutIndividualSignalCount"], 2)
        self.assertAlmostEqual(summary["holdoutAvgFwd126"], 0.22)
        self.assertAlmostEqual(summary["holdoutWinRate126"], 1.0)

    def test_date_split_gate_penalizes_missing_holdout_validation(self) -> None:
        settings = {
            "require_date_split_coverage": True,
            "holdout_index_signal_min": 2,
            "holdout_individual_signal_min": 8,
        }

        weak = date_split_coverage_score(1, 8, settings)
        strong = date_split_coverage_score(2, 8, settings)

        self.assertLess(weak, strong)
        self.assertEqual(strong, 100.0)
        self.assertEqual(apply_date_split_gate(80, 100, settings), 80)
        self.assertEqual(apply_date_split_gate(80, 50, settings), 40)

    def test_summarize_validation_windows_scores_each_market_phase(self) -> None:
        signals = [
            {"date": "2020-03-20", "fwd126": 0.30},
            {"date": "2020-04-01", "fwd126": 0.20},
            {"date": "2022-06-16", "fwd126": -0.05},
            {"date": "2022-10-13", "fwd126": 0.18},
            {"date": "2025-04-08", "fwd126": 0.40},
        ]
        windows = [
            {"name": "covid", "start": "2020-01-01", "end": "2020-12-31", "min_signals": 2},
            {"name": "inflation", "start": "2022-01-01", "end": "2022-12-31", "min_signals": 2},
            {"name": "recent", "start": "2023-01-01", "end": "2026-04-30", "min_signals": 2},
        ]

        summary = summarize_validation_windows(signals, windows)

        self.assertEqual(summary["validationWindowCount"], 3)
        self.assertEqual(summary["coveredValidationWindowCount"], 2)
        self.assertAlmostEqual(summary["validationWindowCoverageScore"], 2 / 3 * 100)
        self.assertAlmostEqual(summary["validationWindowWorstAvgFwd126"], 0.065)
        self.assertAlmostEqual(summary["validationWindowWorstWinRate126"], 0.50)

    def test_validation_window_quality_gate_rejects_weak_window_win_rate(self) -> None:
        settings = {
            "require_validation_window_min_win_rate": True,
            "validation_window_min_win_rate": 0.50,
        }

        self.assertEqual(apply_validation_window_quality_gate(80, 0.50, settings), 80)
        self.assertEqual(apply_validation_window_quality_gate(80, 0.49, settings), 0)

    def test_validation_window_gate_penalizes_missing_market_phases(self) -> None:
        settings = {"require_validation_window_coverage": True}

        self.assertEqual(validation_window_coverage_score(4, 4), 100)
        self.assertEqual(validation_window_coverage_score(2, 4), 50)
        self.assertEqual(apply_validation_window_gate(80, 100, settings), 80)
        self.assertEqual(apply_validation_window_gate(80, 50, settings), 40)

    def test_validation_window_gate_can_hard_reject_incomplete_market_phases(self) -> None:
        settings = {
            "require_validation_window_coverage": True,
            "require_validation_window_hard_coverage": True,
        }

        self.assertEqual(apply_validation_window_gate(80, 100, settings), 80)
        self.assertEqual(apply_validation_window_gate(80, 75, settings), 0)

    def test_recent_validation_summarizes_recent_formal_signals(self) -> None:
        signals = [
            {"date": "2024-05-01", "fwd126": 0.20, "adverse126": -0.05},
            {"date": "2025-04-01", "fwd126": -0.04, "adverse126": -0.11},
            {"date": "2025-05-01", "fwd126": None, "adverse126": None},
            {"date": "2021-01-01", "fwd126": 0.40, "adverse126": -0.08},
        ]

        summary = summarize_recent_validation(
            signals,
            days=730,
            end_date="2026-04-30",
            min_mature_signals=2,
            min_win_rate=0.50,
            min_avg_fwd126=0.05,
        )

        self.assertEqual(summary["recentValidationSignalCount"], 3)
        self.assertEqual(summary["recentValidationMatureCount"], 2)
        self.assertAlmostEqual(summary["recentValidationAvgFwd126"], 0.08)
        self.assertAlmostEqual(summary["recentValidationWinRate126"], 0.50)
        self.assertEqual(summary["recentValidationStatus"], "Pass")

    def test_mb_factor_ablation_configs_remove_one_weight_at_a_time(self) -> None:
        config = BottomSignalConfig(name="best")

        variants = build_mb_factor_ablation_configs(config)

        self.assertEqual(len(variants), 6)
        names = [item[0] for item in variants]
        self.assertIn("drawdown", names)
        drawdown_variant = dict(variants)["drawdown"]
        self.assertEqual(drawdown_variant.drawdown_weight, 0.0)
        self.assertEqual(drawdown_variant.momentum_weight, config.momentum_weight)

    def test_walk_forward_selects_on_train_then_scores_later_test_window(self) -> None:
        results = [
            {
                "config": {"name": "train_winner"},
                "signals": [
                    {"symbol": "QQQ", "date": "2020-03-20", "fwd126": 0.30, "adverse126": -0.05},
                    {"symbol": "AAPL", "date": "2020-04-01", "fwd126": 0.20, "adverse126": -0.08},
                    {"symbol": "AAPL", "date": "2022-06-16", "fwd126": 0.25, "adverse126": -0.07},
                    {"symbol": "SPY", "date": "2022-10-13", "fwd126": 0.10, "adverse126": -0.06},
                ],
            },
            {
                "config": {"name": "test_only"},
                "signals": [
                    {"symbol": "QQQ", "date": "2022-06-16", "fwd126": 0.80, "adverse126": -0.03},
                    {"symbol": "AAPL", "date": "2022-10-13", "fwd126": 0.70, "adverse126": -0.04},
                ],
            },
        ]
        settings = {
            "index_symbols": ["QQQ", "SPY"],
            "walk_forward_folds": [
                {
                    "name": "test_2022",
                    "train_end": "2021-12-31",
                    "test_start": "2022-01-01",
                    "test_end": "2022-12-31",
                    "min_train_signals": 2,
                    "min_test_signals": 2,
                }
            ],
        }

        diagnostic = run_walk_forward_diagnostics(results, settings)

        self.assertEqual(diagnostic["foldCount"], 1)
        self.assertEqual(diagnostic["testedFoldCount"], 1)
        self.assertEqual(diagnostic["positiveFoldCount"], 1)
        self.assertEqual(diagnostic["folds"][0]["selectedConfigName"], "train_winner")
        self.assertEqual(diagnostic["folds"][0]["testSignalCount"], 2)
        self.assertAlmostEqual(diagnostic["folds"][0]["testAvgFwd126"], 0.175)

    def test_local_bottom_gap_is_small_when_signal_is_near_phase_low(self) -> None:
        close = pd.Series([120.0, 110.0, 100.0, 101.0, 130.0])

        near_low = local_bottom_gap(close, position=2, before=2, after=2)
        far_from_low = local_bottom_gap(close, position=0, before=2, after=2)

        self.assertEqual(near_low, 0.0)
        self.assertAlmostEqual(far_from_low, 0.20)
        self.assertGreater(bottom_capture_score(near_low), bottom_capture_score(far_from_low))

    def test_bottom_capture_score_penalizes_entries_far_from_local_low(self) -> None:
        self.assertEqual(bottom_capture_score(None), 0.0)
        self.assertEqual(bottom_capture_score(0.0), 100.0)
        self.assertGreater(bottom_capture_score(0.04), bottom_capture_score(0.15))

    def test_bottom_capture_gate_can_reject_too_many_far_from_bottom_entries(self) -> None:
        settings = {"require_bottom_capture_rate_limit": True, "poor_bottom_capture_rate_limit": 0.35}

        self.assertEqual(apply_bottom_capture_gate(80, 0.30, settings), 80)
        self.assertEqual(apply_bottom_capture_gate(80, 0.40, settings), 0)


if __name__ == "__main__":
    unittest.main()
