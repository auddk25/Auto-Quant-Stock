# Long-Term Add-on Radar Search Flow

## 为什么研究

为了把 Uptrend Dip 研究中更适合长期持有的底部信号单独抽出来，避免用户误用短线买卖版本。

## 搜索参数

搜索 bottom_reversal、rsi_divergence 和 index_shallow_pullback 的权重、阈值、间隔和 re-signal 条件。

## 数据和指标

复用 Uptrend Dip 的 OHLCV 指标，包括 drawdown、multi-bottom/retest、RSI divergence、crash pressure、capitulation volume 和 index trend health。

## 打分方式

更重视 12 个月和 24 个月 forward return，drawdown 是惩罚项，胜率不是主要目标。

## 过拟合过滤

使用 date split、tech subset、multi-window validation 和 signal-level holdout。

## 为什么选当前结果

`bottom_reversal` 在 QQQ/SPY 和 tech subset 上长期回报更强，适合作为默认长期加仓雷达。

## 已知限制和下一步

需要未来新样本和 paper-tracking。它给出“值得加仓观察”的时间点，不等于完整仓位管理系统。
