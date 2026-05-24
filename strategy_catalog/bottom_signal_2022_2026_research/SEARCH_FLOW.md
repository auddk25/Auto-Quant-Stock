# Bottom Signal 2022/2026 Research Flow

## 为什么研究

正式 MB Strong 没有覆盖 QQQ 2022 Q4 和 2026 March，但 OBS 候选覆盖了这些窗口，需要判断是否能找到更好的正式策略。

## 搜索参数

先跑标准 720 配置隔离搜索，再跑 research-only expanded 搜索。expanded 搜索测试更低 entry threshold、更低 MB offset 和更宽浅回撤市场条件。

## 数据和指标

复用 Bottom Signal full-pool 21 个 symbol、OHLCV 指标、formal signals、diagnostic signals 和 OBS signals。

## 打分方式

比较 best config、正式信号数、6 个月收益、胜率、验证窗口覆盖和是否覆盖 2022/2026 anchor。

## 过拟合过滤

信号数是关键过滤项。expanded 搜索虽然找到覆盖两个窗口的正式配置，但最低仍有 319 个信号，因此不能替换 39 信号正式基线。

## 为什么选当前结果

`baseline_formal_plus_obs_addon_v1` 是当前唯一同时保留全部现有正式信号、又覆盖 2022/2026 的形态。

## 已知限制和下一步

这只是研究候选。正式推广前必须做独立 promotion plan，包括 OBS add-on 消融、近期验证、样本外验证、信号数约束和 Pine parity。
