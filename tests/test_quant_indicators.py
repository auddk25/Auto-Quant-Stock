import unittest
from pathlib import Path

import pandas as pd

from quant_indicators import (
    add_macd,
    add_rsi,
    build_indicators,
    validate_ohlcv,
)


def spy_sample() -> pd.DataFrame:
    return pd.read_parquet(Path("data") / "SPY.parquet").tail(360)


class QuantIndicatorsTest(unittest.TestCase):
    def test_validate_ohlcv_requires_standard_columns(self) -> None:
        frame = pd.DataFrame(
            {
                "Open": [10.0, 11.0],
                "High": [12.0, 12.5],
                "Low": [9.5, 10.5],
                "Close": [11.0, 12.0],
            }
        )

        with self.assertRaisesRegex(ValueError, "Volume"):
            validate_ohlcv(frame)

    def test_add_rsi_only_generates_requested_periods(self) -> None:
        enriched = add_rsi(spy_sample(), periods=[7, 21])

        self.assertIn("rsi_7", enriched.columns)
        self.assertIn("rsi_21", enriched.columns)
        self.assertNotIn("rsi_14", enriched.columns)
        self.assertFalse(enriched["rsi_7"].dropna().empty)
        self.assertFalse(enriched["rsi_21"].dropna().empty)

    def test_add_macd_names_each_parameter_combination(self) -> None:
        enriched = add_macd(spy_sample(), configs=[(8, 21, 5), (12, 26, 9)])

        expected_columns = [
            "macd_8_21_5",
            "macd_signal_8_21_5",
            "macd_diff_8_21_5",
            "macd_12_26_9",
            "macd_signal_12_26_9",
            "macd_diff_12_26_9",
        ]
        for column in expected_columns:
            self.assertIn(column, enriched.columns)
            self.assertFalse(enriched[column].dropna().empty, column)

    def test_build_indicators_combines_requested_specs_without_changing_ohlcv(self) -> None:
        source = spy_sample()
        original_ohlcv = source[["Open", "High", "Low", "Close", "Volume"]].copy()
        spec = {
            "sma": [50, 200],
            "ema": [21],
            "rsi": [10],
            "macd": [(8, 21, 5)],
            "atr": [10, 20],
            "adx": [14],
            "bollinger": [(20, 2.0)],
            "stochastic": [(14, 3)],
            "volume": [20],
            "drawdown": [63, 252],
            "distance_to_sma": [50, 200],
            "atr_ratio": [(10, 50)],
        }

        enriched = build_indicators(source, spec)

        self.assertEqual(len(enriched), len(source))
        pd.testing.assert_frame_equal(
            enriched[["Open", "High", "Low", "Close", "Volume"]],
            original_ohlcv,
        )
        for column in [
            "sma_50",
            "sma_200",
            "ema_21",
            "rsi_10",
            "macd_8_21_5",
            "atr_10",
            "atr_20",
            "adx_14",
            "bb_upper_20_2",
            "stoch_14_3",
            "volume_ratio_20",
            "drawdown_63",
            "drawdown_252",
            "dist_sma_50",
            "dist_sma_200",
            "atr_ratio_10_50",
        ]:
            self.assertIn(column, enriched.columns)
            self.assertFalse(enriched[column].dropna().empty, column)


if __name__ == "__main__":
    unittest.main()
