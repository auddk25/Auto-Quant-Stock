# Uptrend Dip Buy/Sell Search Flow

## 为什么研究

该研究用于比较多种买点和卖点家族，判断哪类信号适合长期加仓、短线买卖或指数浅回撤。

## 搜索参数

搜索七类买入策略、两类卖出策略、权重、阈值和止损。

## 数据和指标

数据来自 OHLCV 和 yfinance/cache。指标包括 EMA stack、RSI、Stochastic、range compression、breakout distance、relative strength、drawdown、volume 和 ATR。

## 打分方式

分别评估 forward return、交易结果、长期持有回报、drawdown、walk-forward 和 multi-window coverage。

## 过拟合过滤

使用 date split、full-grid walk-forward、multi-window validation 和 tech subset holdout。

## 为什么选当前结果

bottom_reversal 在长期 add-on 评价里更稳定，且能覆盖 2020、2022 等大回撤窗口。

## 已知限制和下一步

生产使用前仍需要 paper-trading 和新样本验证。per-symbol optimal config 更容易过拟合。
