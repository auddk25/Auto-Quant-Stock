# Long-Term Add-on Radar

## 一句话解释

Long-Term Add-on Radar 是长期加仓雷达，不是短线买卖策略。它寻找大回撤、多底结构、RSI 背离和恐慌成交量后的长期加仓点。

## 使用场景

- 想在 TradingView 上观察长期加仓机会。
- 想区分深底部、RSI 背离和指数浅回撤。
- 适合长期分批加仓，而不是日内或短线交易。

## 当前推荐配置

- Radar Mode：`bottom_reversal`
- Bottom Threshold：45
- Minimum Bars Between Signals：63

## 信号含义

- `BTM WATCH/MED/STRONG`：深回撤底部雷达。
- `RSI` 模式：独立 RSI 背离基线。
- `IDX` 模式：指数或 ETF 的浅回撤雷达。

## 不适用场景

- 不适合做短线买卖。
- 不应和 Uptrend Dip 的 buy/sell 状态指标混用成同一规则。

## 当前验证结果

QQQ/SPY combined score 为 96.86。Tech subset 12m 平均收益约 54.8%，2023+ holdout 仍为正。

## Pine 文件怎么用

使用 `long_term_addon_radar.pine`，复制到 TradingView Pine Editor。默认模式就是长期 add-on 读法。
