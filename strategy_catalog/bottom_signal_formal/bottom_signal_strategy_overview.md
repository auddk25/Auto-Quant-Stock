# Bottom Signal Strategy Overview

## 一句话结论

当前研究已经形成了一个正式的底部入场策略候选：
`seed_previous_rs_higher_low_best`。

它的核心不是“看到股票跌了就买”，而是先要求大盘进入足够深的回撤环境，再用价格位置、动量修复、结构、成交量和均线关系打分。只有分数达到正式入场线，才算 Strong 信号。

RS 选股增强目前只是观察名单，用来告诉我们哪些股票值得优先盯盘或复盘，不能直接当成正式买入规则。

## 策略探索流程

1. 明确目标
   - 目标是找“阶段性底部或回撤后的入场信号”。
   - 总评分目标是：70% 看底部信号质量，20% 看交易结果，10% 看退出信号质量。
   - 这意味着策略更重视“买点是否像底部”，而不是单纯追求短期收益最高。

2. 生成候选策略
   - 参数从 `bottom_signal_config.json` 读取。
   - 搜索范围包括回撤窗口、回撤阈值、RSI、随机指标、MACD、均线、成交量窗口、入场分数、最小信号间隔和 RS 相关参数。
   - 当前最多测试 720 个配置。

3. 先小范围筛，再全市场验证
   - 先在 DEV 股票池中快速测试。
   - 表现靠前的配置再晋级到完整股票池。
   - 这样做是为了避免每次都跑完整慢回测。

4. 用硬门槛防止过拟合
   - 策略不能只在一两只股票上有效。
   - 必须覆盖 QQQ/SPY 和个股。
   - 必须覆盖不同市场阶段，例如 2008-2010、2020、2022、2023 以后。
   - 必须控制信号数量，当前正式候选要求全市场 Strong 信号不超过 40 个。
   - 必须检查买点是否真的靠近局部底部，而不是普通回调。

5. 选出当前正式候选
   - 当前最佳配置是 `seed_previous_rs_higher_low_best`。
   - 主 Pine 文件是 `bottom_signal_pine.pine`，现在整合显示 `BUY-MB`、`BUY-D`、`BUY-S`。
   - 当前正式候选有 39 个 Strong 信号。

6. 做 MB 因子消融
   - 消融的意思是：一次拿掉一个因子，看策略是否明显变差。
   - 如果拿掉后策略崩掉，这个因子就是关键因子。
   - 如果拿掉后信号暴增、质量下降，这个因子就是刹车因子。

7. 做 RS 选股增强
   - RS 不是替换正式策略。
   - 它用于发现“相对强、可能更值得观察”的股票。
   - 输出结果按 Priority、Watch、Avoid 分层。

8. 做近期验证
   - 最近窗口是 2024-05-01 到 2026-04-30。
   - 只看已经有 6 个月结果的信号。
   - 当前近期验证状态是 Pass。

## 当前正式策略

正式策略角色：`FormalStrategy`。

当前最佳配置：

- 名称：`seed_previous_rs_higher_low_best`
- 实验信号集：`rs_higher_low_structure`
- 回撤窗口：126 个交易日
- 个股回撤阈值：-8%
- 大盘过滤：QQQ/SPY 的 126 日回撤必须 <= -20%
- RSI 周期：10
- 随机指标：21 / 5
- MACD：16 / 35 / 9
- 均线周期：100
- ATR 周期：14
- 成交量窗口：20
- Watch 分数线：76
- Medium 分数线：80
- 正式入场分数线：82
- MB 入场分数线：82
- RS 入场分数线：82
- 最小信号间隔：42 个交易日

正式策略表现：

- 综合分数：27.95
- Strong 信号数：39
- 平均 6 个月收益：39.24%
- 6 个月胜率：74.36%
- 平均 6 个月不利回撤：-13.80%
- QQQ/SPY 信号：4
- 个股信号：35
- 训练期信号：32
- 样本外/近期持出信号：7

## MB 因子内容

MB 可以理解成“市场底部主线”。它是当前正式策略的核心。

当前 6 个评分因子：

- `drawdown`：价格是否已经经历足够回撤。
- `momentum`：下跌后的动量是否开始修复。
- `repair`：市场或个股是否有修复迹象。
- `structure`：价格结构是否更像底部或高低点改善。
- `volume`：成交量是否支持底部修复。
- `ma`：价格和均线关系是否合理。

消融结论：

- 必须保留：`drawdown`、`momentum`、`structure`、`volume`、`ma`。
- 作为刹车保留：`repair`。
- 暂无支持删除的冗余因子。

简单解释：

- `drawdown` 拿掉后只剩 2 个信号，策略失去主要识别能力。
- `repair` 拿掉后信号暴增到 125 个，说明它在防止策略过度出手。
- 所以当前不应该删 MB 因子，也不应该只因为 RS 名单好看就改正式入场逻辑。

## RS 选股增强

RS 可以理解成“相对强度观察通道”。它回答的问题是：在底部环境附近，哪些股票比其他股票更值得优先盯？

当前 RS 角色：`Observation`。

这不是正式买入规则。RS 名单只用于观察、复盘和后续验证。

当前分层：

- Monitor：AVGO、META
- Review：CRM、PLTR、AMZN、TSLA、AAPL、V、JPM
- Skip：CAT、NVDA、CRWD

重点说明：

- AVGO 和 META 排名最高，是因为它们有重复合格候选，并且风险标记较干净。
- CRM、AAPL、V、JPM 虽然在 Watch 层，但带有风险标记，需要复盘原因。
- CAT、NVDA、CRWD 当前没有合格 RS 候选，所以先跳过。

## 近期验证

近期窗口：2024-05-01 到 2026-04-30。

当前结果：

- 近期正式信号：7
- 已成熟 6 个月检查：7
- 近期平均 6 个月收益：75.79%
- 近期 6 个月胜率：100.00%
- 近期平均 6 个月不利回撤：-3.23%
- 状态：Pass

这说明当前正式策略在最近一段成熟样本上表现很好。但样本只有 7 个，所以它是正面证据，不是最终结论。

## 当前行动规则

1. 保留正式 MB 策略。
   - 不删除当前关键因子。
   - 不降低正式入场门槛。

2. 保留 `repair` 作为刹车。
   - 它不是最高收益因子，但能防止信号过多。

3. RS 名单只做观察。
   - AVGO、META 优先监控。
   - Review 层股票复盘风险标记。
   - Avoid 层暂不进入重点观察。

4. 不从这份 RS 观察名单直接升级正式买点。
   - 任何升级都需要单独消融、近期验证和样本外验证。

5. 继续看近期验证。
   - 当前状态是 Pass，可以继续观察。
   - 如果未来新样本明显恶化，再考虑调低权重或增加过滤。

## 主要产物

- 完整报告：`strategy_catalog/bottom_signal_formal/bottom_signal_report.md`
- 一页摘要：`strategy_catalog/bottom_signal_formal/bottom_signal_plan_summary.md`
- 下一步清单：`strategy_catalog/bottom_signal_formal/bottom_signal_next_actions.csv`
- MB 因子消融：`strategy_catalog/bottom_signal_formal/bottom_signal_mb_factor_ablation.csv`
- 近期验证：`strategy_catalog/bottom_signal_formal/bottom_signal_recent_validation.csv`
- RS 股票分层：`strategy_catalog/bottom_signal_observation_addon/bottom_signal_rs_watchlist_tickers.csv`
- 主 Pine：`strategy_catalog/bottom_signal_formal/bottom_signal_pine.pine`
- 严格 MB 归档 Pine：`strategy_catalog/bottom_signal_formal/bottom_signal_strict_formal.pine`
- RS 观察 Pine：`strategy_catalog/bottom_signal_observation_addon/bottom_signal_rs_watchlist_pine.pine`

## 非技术版理解

现在的策略像一个分三层的流程：

1. 先看大盘有没有进入值得找底部的环境。
2. 再看个股本身是否满足底部、修复、结构和成交量条件。
3. 最后用 RS 名单决定哪些股票更值得优先观察，但不让 RS 直接替代正式买入条件。

当前最重要的原则是：正式策略和观察名单分开。正式策略负责“能不能买”，RS 观察名单负责“先看谁”。
