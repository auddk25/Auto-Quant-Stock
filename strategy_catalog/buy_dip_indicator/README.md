# Buy-the-Dip Indicator

## 一句话解释

Buy-the-Dip Indicator 是一个纯 OHLCV 指标搜索策略，用 RSI、Keltner、SMA200、drawdown、ATR 和 Stochastic 寻找买跌信号。

## 使用场景

- 想用简单价格和成交量指标寻找指数或个股回撤买点。
- 想要可直接转成 TradingView Pine 的指标。
- 适合作为历史对照策略。

## 当前推荐配置

- Joint config：`r0.20_k0.15_s0.15_d0.10_a0.25_st0.15_t50`
- Buy threshold：50

## 信号含义

Buy signal 表示价格和动量进入回撤买入候选区，不包含完整卖出系统。

## 不适用场景

- 不适合直接和 Bottom Signal 正式策略混为一谈。
- DCA 结果不一定跑赢 buy-and-hold。

## 当前验证结果

QQQ avg 3m return 16.00%，SPY avg 3m return 15.61%。多只个股有 per-symbol optimal config，但这些更容易过拟合。

## Pine 文件怎么用

使用 `buy_dip_pine.pine`，复制到 TradingView Pine Editor。权重和阈值可在输入面板调整。
