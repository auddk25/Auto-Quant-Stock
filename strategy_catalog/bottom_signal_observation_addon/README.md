# Bottom Signal Observation Add-on

## 一句话解释

OBS-D / OBS-S 是 Bottom Signal 的观察候选层，用来补捉正式 MB Strong 没覆盖但值得复盘的底部候选。

OBS/RS 仍是观察或研究 add-on。当前主 TradingView 买点已经整合到 `bottom_signal_formal/bottom_signal_pine.pine`，本目录文件主要用于诊断来源。

## 使用场景

- 用于观察和复盘漏掉的底部窗口。
- 用于生成 TradingView 候选提醒和对照主 Pine 的信号来源。
- 用于未来研究“是否能升级为正式策略”的证据收集。

## 当前推荐配置

- OBS-D：深回撤 retest 候选。
- OBS-S：浅回撤 pullback 候选。
- OBS 最大 bottom score：75。
- 当前 OBS 候选数：48。
- 与正式信号重复数：0。

## 信号含义

- `OBS-D`：深回撤候选，不是正式买点。
- `OBS-S`：浅回撤候选，不是正式买点。
- `RS Watchlist`：优先观察谁，不回答“能不能买”。

## 不适用场景

- 不能把 OBS/RS 自动当正式买点。
- 不能用 OBS 替代 `entry_threshold=82` 的正式规则。
- 不能未经消融、样本外验证和 Pine parity 就上线。

## 当前验证结果

- OBS 信号：48。
- 6 个月平均收益：19.10%。
- 6 个月胜率：72.34%。
- OBS/Formal 比例：1.23x。
- QQQ 2022 Q4 和 2026 March 均被 OBS 覆盖。

## Pine 文件怎么用

主图买点优先使用 `strategy_catalog/bottom_signal_formal/bottom_signal_pine.pine`。

`bottom_signal_merged_observation.pine` 只作为观察诊断文件，用来看 OBS-D/OBS-S 与 RS 观察层的原始来源。

## 主要文件

- `bottom_signal_merged_observation.pine`
- `bottom_signal_observation_report.md`
- `bottom_signal_observation_signals.csv`
- `bottom_signal_rs_watchlist_pine.pine`
- `bottom_signal_rs_watchlist_report.md`
