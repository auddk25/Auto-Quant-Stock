# Bottom Signal 2022/2026 Research

## 一句话解释

这是针对 QQQ 2022 Q4 和 2026 March 缺失正式信号的研究目录，结论是单一正式参数替代会信号失控，当前可行形态是 `baseline_formal_plus_obs_addon_v1`。

单一正式参数替代失败，因为最低也有 319 个信号；当前组合形态是 `baseline_formal_plus_obs_addon_v1`。

## 使用场景

- 复盘为什么正式 MB Strong 没有触发。
- 比较单一正式替代和组合 add-on 的代价。
- 为未来 OBS/RS 升级计划提供证据。

## 当前推荐配置

- 不替换正式基线。
- 使用组合研究形态：`baseline_formal_plus_obs_addon_v1`。
- 规则：保留 39 个正式信号，再加 48 个 OBS 候选。

## 信号含义

- formal：当前正式 MB Strong。
- observation：OBS-D/OBS-S 候选。
- 组合策略是研究候选，不是正式上线策略。

## 不适用场景

- 不应把 expanded formal search 的低阈值配置直接上线。
- 不应忽略 319+ 信号数带来的过拟合和交易噪音。

## 当前验证结果

- 组合信号：87。
- 正式信号保留：39/39。
- OBS add-on：48。
- 组合 6 个月平均收益：28.23%。
- 组合 6 个月胜率：73.26%。
- QQQ 2022 Q4：覆盖 2022-10-03、2022-10-11、2022-12-28。
- QQQ 2026 March：覆盖 2026-03-27。

## Pine 文件怎么用

可查看 `bottom_signal_merged_observation_2022_2026_miss_search.pine`。这是研究用 Pine，不是正式策略替代。

## 主要文件

- `bottom_signal_2022_2026_composite_strategy_report.md`
- `bottom_signal_2022_2026_composite_strategy_signals.csv`
- `bottom_signal_results_2022_2026_miss_search.json`
- `bottom_signal_results_2022_2026_miss_expanded.json.gz`：expanded full JSON 的压缩归档；本地可解压为同名 `.json` 复查。
- `bottom_signal_2022_2026_plan_execution_audit.md`
