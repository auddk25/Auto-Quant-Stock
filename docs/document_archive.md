# Document Archive

生成日期：2026-05-19

## 用途

这个文件是当前仓库的文档归档入口。

它说明每份文档和策略产物放在哪里、主要讲什么、什么时候该看。Pine 策略产物已经统一移动到 `strategy_catalog/`，研究脚本仍保留在 `investigations/`。

## 阅读顺序

1. 先看 `README.md`，了解项目是什么。
2. 再看 `docs/project_context.md`，了解项目背景。
3. 如果要找策略入口，看 `docs/策略目录.md`。
4. 如果要看当前正式策略研究，看 `strategy_catalog/bottom_signal_formal/bottom_signal_strategy_overview.md`。
5. 如果要看最新执行动作，看 `strategy_catalog/bottom_signal_formal/bottom_signal_plan_summary.md` 和 `strategy_catalog/bottom_signal_formal/bottom_signal_next_actions.csv`。
6. 如果要追踪开发过程，看 `claude-progress.md`。

## 根目录文档

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `README.md` | 项目入口说明。 | 保留 |
| `AGENTS.md` | 给自动化编码代理的仓库规则。 | 保留 |
| `CLAUDE.md` | Claude/代理相关的项目说明。 | 保留 |
| `plan.md` | 早期项目搭建计划。 | 归档参考 |
| `program.md` | 早期项目程序/策略说明。 | 归档参考 |
| `claude-progress.md` | 长期会话进度和交接记录。 | 持续更新 |

## docs 文档

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `docs/project_context.md` | 项目背景、目标和整体上下文。 | 保留 |
| `docs/策略目录.md` | 当前 Pine 策略目录总入口。 | 当前入口 |
| `docs/analysis_report_apr29.md` | 2026-04-29 的 38 组实验分析报告。 | 归档参考 |
| `docs/plans/uptrend_dip_baseline_2026-05-17.md` | Uptrend Dip 基线归档。 | 归档参考 |
| `docs/plans/bottom_signal_iteration_2026-05-17.md` | Bottom Signal 迭代计划。 | 当前研究计划参考 |
| `docs/document_archive.md` | 当前文档归档入口。 | 新增 |

## strategy_catalog 策略目录

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `strategy_catalog/bottom_signal_formal/` | Bottom Signal 正式 MB Strong 主买点。 | 当前正式策略 |
| `strategy_catalog/bottom_signal_observation_addon/` | OBS/RS 观察层和候选名单。 | 观察 add-on |
| `strategy_catalog/bottom_signal_2022_2026_research/` | 2022/2026 缺失正式信号研究。 | 研究候选 |
| `strategy_catalog/uptrend_dip_buy_sell/` | Uptrend Dip 历史买卖策略。 | 历史/对照策略 |
| `strategy_catalog/long_term_addon_radar/` | 长期加仓雷达。 | 观察雷达 |
| `strategy_catalog/buy_dip_indicator/` | Buy-the-Dip 指标搜索。 | 历史/对照研究 |
| `strategy_catalog/_reference/us_index_zone/` | 美股指数区间研究参考。 | 市场环境参考 |

## investigations 研究脚本

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `investigations/bottom_signal_search.py` | Bottom Signal 搜索、报告、Pine 生成入口。 | 保留 |
| `investigations/uptrend_dip_search.py` | Uptrend Dip 和长期雷达生成入口。 | 保留 |
| `investigations/buy_dip_search.py` | Buy-the-Dip 指标生成入口。 | 保留 |
| `investigations/us_index_zone_research.py` | 美股指数区间研究入口。 | 保留 |

## versions 文档

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `versions/README.md` | 版本目录说明。 | 保留 |
| `versions/0.1.0/retrospective.md` | v0.1.0 回顾。 | 归档参考 |
| `versions/0.2.0/retrospective.md` | v0.2.0 回顾。 | 归档参考 |
| `versions/0.3.0/retrospective.md` | v0.3.0 回顾。 | 归档参考 |

## 非 Markdown 研究产物归档说明

这些文件不是文档，但需要知道从哪里理解它们：

| 文件类型 | 说明 | 对应文档 |
| --- | --- | --- |
| `*.csv` | 研究输出表，例如 MB 消融、RS 股票分层、下一步动作清单。 | `strategy_catalog/` 对应策略文件夹 |
| `*.json` | 回测和搜索结果机器可读版本。 | `strategy_catalog/` 对应策略文件夹 |
| `*.pine` | TradingView Pine 脚本。 | `strategy_catalog/` 对应策略文件夹 |
| `*.log` | 历史运行日志。 | 仅排查问题时查看 |
| `*.tsv` | 早期实验结果表。 | `docs/analysis_report_apr29.md` |
| `*.png` | 图像产物。 | 对应报告或历史分析 |

## 当前缺口

- 根目录的 `plan.md` 和 `program.md` 是早期文档，内容可能和当前 Bottom Signal 研究不完全一致。阅读当前策略时优先看 `docs/策略目录.md`。
- `investigations/` 现在主要放研究脚本。策略产物优先从 `strategy_catalog/` 查找。
- 旧的 `bottom_signal_report_dual_track_rs.md` 和 `bottom_signal_results_dual_track_rs.json` 已经与当前主报告/主 JSON 完全重复，因此主线只保留 `bottom_signal_report.md` 和 `bottom_signal_results.json`。
- 如果以后新增新的研究主题，应该同时新增一份 Markdown 说明，并把它登记到本归档。

## 当前主线

当前主线是 Bottom Signal 策略研究：

- 正式策略说明：`strategy_catalog/bottom_signal_formal/bottom_signal_strategy_overview.md`
- 完整报告：`strategy_catalog/bottom_signal_formal/bottom_signal_report.md`
- 策略迭代复盘：`strategy_catalog/bottom_signal_formal/bottom_signal_strategy_iteration_review.md`
- 一页摘要：`strategy_catalog/bottom_signal_formal/bottom_signal_plan_summary.md`
- 行动清单：`strategy_catalog/bottom_signal_formal/bottom_signal_next_actions.csv`

简短理解：

- MB 是正式策略主线，负责判断“能不能买”。
- RS 是观察名单，负责判断“先看谁”。
- 近期验证目前是 Pass，但样本数量不大，仍然需要继续观察。
