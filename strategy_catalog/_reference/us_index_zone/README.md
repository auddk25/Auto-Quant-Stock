# US Index Zone Reference

## 一句话解释

US Index Zone 是市场区间研究，用来判断指数处于 bottom、pullback、heat 或 hold 区域。

## 为什么没有 Pine

本研究依赖 Fear & Greed、估值、VIX 和当前 PE gate 等外部数据。TradingView Pine 不能等价复现这些外部数据和历史抓取逻辑，所以本轮只作为参考归档，不强行生成 Pine。

## 使用场景

- 理解 SPY/QQQ 的市场环境。
- 辅助解释 Bottom Signal 或 Buy Dip 信号出现时的大盘背景。
- 作为 Web 策略或人工复盘参考。

## 当前推荐配置

- Joint default：`f0.30_v0.15_t0.40_r0.15_b50_p50_pb34_h52_g5`
- 角色：市场区间参考，不是独立 TradingView Pine 策略。

## 主要文件

- `us_index_zone_report.md`
- `us_index_zone_results.json`
