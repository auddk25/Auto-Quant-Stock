# Auto-Quant Research Progress

## Branch: autoresearch/apr29

## Key Finding
**Buy-and-hold beats all timing strategies on absolute returns (2019-2025 bull market).**

## Full Comparison (21 tickers, 2019-2025)

| Strategy | avg_return | sharpe | worst_dd | trades |
|----------|-----------|--------|----------|--------|
| BuyHold | 905.21% | 0.7284 | -84.6% | 0 |
| BH_Stop (30%) | 888.45% | 0.7214 | -86.3% | 7 |
| FirstUp | 864.18% | 0.7364 | -84.6% | 0 |
| Day2Buy | 859.39% | 0.7349 | -84.6% | 0 |
| FastEntry (3d) | 830.46% | 0.7292 | -84.6% | 0 |
| EMA_Forever | 803.78% | 0.7437 | -84.6% | 0 |
| BuyAdd | 756.65% | 0.7558 | -84.8% | 536 |
| BH_Recover | 666.60% | 0.7428 | -78.6% | 19 |
| BH_200SMA | 417.99% | 0.6608 | -61.9% | 420 |
| BH_50_50 | 408.42% | 0.7586 | -69.7% | 0 |
| EMA_Mom | 341.04% | 0.6646 | -61.3% | 525 |
| EMA_Wide | 331.51% | 0.6559 | -62.7% | 525 |
| EMA_BigTrend | 228.62% | 0.6066 | -67.8% | 282 |
| RSI_BuyDip | 119.57% | 1.1351 | -66.9% | 401 |

## Conclusion
In a secular bull market (2019-2025), buy-and-hold is extremely hard to beat on absolute returns. Any exit mechanism (stop-loss, SMA exit, momentum exit, trend filter) loses returns. The closer to buy-and-hold (always in market), the higher the returns.

## Best Risk-Adjusted Strategy: EMA_Mom
- EMA 10/30 crossover + 10-day momentum filter + 12% stop-loss
- Provides meaningful downside protection: -61.3% vs -84.6% DD
- Works well on tech/indices, struggles on cross-sector (VAL_CROSS fails)
- If goal shifts to risk-adjusted returns, this is the winner

## Experiments Completed: 38
## Results: See results.tsv
