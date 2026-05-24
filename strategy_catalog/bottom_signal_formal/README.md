# Bottom Signal Formal Strategy

## 一句话解释

`seed_previous_rs_higher_low_best` 是当前底部买点主策略。TradingView 主文件现在是整合显示版：严格 MB Strong 和 OBS-D/OBS-S 都会在同一个 Pine 里显示成买入信号。

严格 MB Strong 仍是历史收益统计里的正式基线；OBS-D/OBS-S 是为解决 2022/2026 缺失显示窗口加入的整合买入来源。

想从头学习完整搜索和推理过程，先读 `README_中文学习版.md`。

## 使用场景

- 用于识别阶段性底部或深回撤后的入场点。
- 适合先看 QQQ/SPY 市场环境，再看个股是否出现高质量底部信号。
- 适合在 TradingView 里只导入一个主 Pine，看 `BUY-MB`、`BUY-D`、`BUY-S` 三类买入显示。

## 当前推荐配置

- 策略名：`seed_previous_rs_higher_low_best`
- 严格 MB 入场分数：82
- 大盘过滤：QQQ/SPY 126 日回撤必须足够深
- 最小信号间隔：42 个交易日
- 核心因子：drawdown、momentum、structure、volume、ma
- repair：作为刹车，不直接追求更多信号
- OBS 配置：`deepBottomMin=66`、`shallowBottomMin=68`、`bottomMax=75`、`nearLowWindow=63`、`nearLowMax=0.06`

## 信号含义

- `BUY-MB`：原严格 MB Strong 买点。
- `BUY-D`：原 OBS-D 深度二次确认买点。
- `BUY-S`：原 OBS-S 浅回撤买点。
- `Watch` / `Medium`：观察或诊断，不是正式买点。
- `RS`：辅助观察，不替代正式入场。

## 不适用场景

- 不适合追涨。
- 不适合把普通浅回调都当底部。
- 不应把 `BUY-D` / `BUY-S` 误读成原始 MB Strong；它们是整合显示后的 OBS 来源。

## 当前验证结果

- Full-pool：21 个 symbol。
- 正式 Strong 信号：39。
- 6 个月平均收益：39.24%。
- 6 个月胜率：74.36%。
- 近期成熟信号胜率：100%。

## Pine 文件怎么用

打开 `bottom_signal_pine.pine`，复制到 TradingView Pine Editor。现在这个文件已经整合 `BUY-MB`、`BUY-D`、`BUY-S`，不需要再同时导入 `bottom_signal_merged_observation.pine`。

如果只想看旧的严格 MB Strong 基线，用 `bottom_signal_strict_formal.pine`。

## 主要文件

- `bottom_signal_pine.pine`
- `bottom_signal_strict_formal.pine`
- `README_中文学习版.md`
- `bottom_signal_report.md`
- `bottom_signal_results.json`
- `bottom_signal_config.json`
- `bottom_signal_strategy_overview.md`
