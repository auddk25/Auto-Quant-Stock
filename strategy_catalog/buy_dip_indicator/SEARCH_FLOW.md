# Buy-the-Dip Indicator Search Flow

## 为什么研究

为了建立一个只依赖 OHLCV 的买跌指标基线，方便翻译成 Pine，也方便与更复杂的 Bottom Signal 比较。

## 搜索参数

搜索 RSI、Keltner、SMA200、drawdown、ATR volatility、Stochastic 权重和 buy threshold。

## 数据和指标

数据来自 yfinance cache 和本地 parquet。指标只使用价格和成交量，不依赖 VIX、估值或外部情绪。

## 打分方式

评估 3/6/12 个月 forward return、3 个月胜率、DCA return、相对 buy-and-hold 和 crash phase coverage。

## 过拟合过滤

使用 QQQ/SPY joint config 和 all-ticker validation，对 per-symbol optimal config 保持谨慎。

## 为什么选当前结果

`r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50` 在 QQQ/SPY 综合排名中表现较均衡。

## 已知限制和下一步

该策略是指标基线，不是完整交易系统。未来如继续使用，应增加卖出、持仓和样本外验证。
