# Uptrend Dip Buy/Sell Strategy

## 一句话解释

Uptrend Dip Buy/Sell 是一个多策略买卖信号研究器，比较 pullback、breakout、bottom reversal、RSI divergence 和 index shallow pullback，并生成带买卖状态的 Pine 指标。

## 使用场景

- 想比较不同买点家族和卖出规则。
- 想在 TradingView 里观察买卖信号、持仓状态和退出逻辑。
- 适合研究，不是当前 Bottom Signal 正式主线。

## 当前推荐配置

- 长期 add-on 默认：`btm_d0.30_b0.20_r0.20_c0.20_v0.10_t45`。
- 买卖组合推荐：`btm_d0.30_b0.20_r0.20_c0.20_v0.10_t50_s15_sl3`。
- 主信号家族：bottom_reversal。

## 信号含义

- Buy：候选买点。
- Sell：退出或风险控制信号。
- Stop loss：交易模拟里的止损退出。

## 不适用场景

- 不应把每个 per-symbol optimal config 当通用配置。
- 不适合未经 paper-tracking 就作为生产交易系统。

## 当前验证结果

报告包含 date-split、walk-forward 和 multi-window validation。最新 tech 信号示例为 CRM 2026-02-19 Deep Bottom - Strong。

## Pine 文件怎么用

使用 `uptrend_dip_pine.pine`。如果只要长期加仓雷达，应改用 `../long_term_addon_radar/long_term_addon_radar.pine`。
