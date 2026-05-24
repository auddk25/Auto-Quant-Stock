# Bottom Signal Formal Search Flow

## 为什么研究

目标是找到一个能识别阶段性底部、又不会频繁乱发信号的底部买点策略。严格 MB Strong 用来保留历史基线，OBS-D/OBS-S 用来补足 2022/2026 没有显示买点的窗口。

## 搜索参数

搜索范围包括回撤窗口、回撤阈值、RSI、随机指标、MACD、均线周期、ATR、成交量窗口、入场分数、信号间隔和 RS 相关参数。

## 数据和指标

- 数据：本地 OHLCV 日线数据。
- 指标：drawdown、RSI、Stochastic、MACD、SMA 距离、ATR、成交量比率。
- 市场过滤：QQQ/SPY 回撤环境。

## 打分方式

严格 MB 搜索总评分更重视底部质量：底部质量 70%，交易结果 20%，退出质量 10%。OBS 层不改这个评分，只作为同一 Pine 里的额外买入来源显示。

## 过拟合过滤

- 信号数必须受控。
- 必须覆盖指数和个股。
- 必须覆盖 2008-2010、2020、2022、2023+ 等市场阶段。
- 检查买点是否靠近局部底部。

## 为什么选当前结果

`seed_previous_rs_higher_low_best` 在收益、胜率、信号稀疏度和阶段覆盖之间最平衡，并且当前严格 MB 信号不超过 40。

TradingView 主 Pine 选择整合显示版，是因为用户实际使用时需要一个文件直接看到 `BUY-MB`、`BUY-D`、`BUY-S`。严格版保存在 `bottom_signal_strict_formal.pine`，用于复查历史基线。

## 已知限制和下一步

- 2022 Q4 和 2026 March 的 QQQ 深跌窗口没有严格 MB Strong，但 OBS 有覆盖。
- 当前主 Pine 已把 OBS-D/OBS-S 合并为 `BUY-D` / `BUY-S` 显示。
- 如果未来要把 OBS 作为独立收益统计里的正式策略，需要另开验证计划。
