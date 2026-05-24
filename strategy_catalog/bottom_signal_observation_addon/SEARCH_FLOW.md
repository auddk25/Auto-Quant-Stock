# Bottom Signal Observation Add-on Search Flow

## 为什么研究

正式 MB Strong 保守且稀疏，可能漏掉一些收益不错的底部窗口。OBS 层用于记录这些候选，而不是直接改变正式买点。

## 搜索参数

观察层搜索 deep/shallow market band、bottom score 区间、near-low window、near-low gap、cluster window 和 sparse target。

## 数据和指标

复用 Bottom Signal 的 OHLCV 指标、bottom score、market drawdown、near-low 位置和 risk flags。

## 打分方式

OBS 评分关注 anchor 覆盖、收益质量、稀疏度和与正式信号不重复。

## 过拟合过滤

- OBS/Formal 比例不能过高。
- `duplicateFormalCount` 必须为 0。
- anchor 覆盖只是候选证据，不是正式升级证据。

## 为什么选当前结果

当前 OBS 配置同时覆盖 QQQ 2022 Q4 和 QQQ 2026 March，且保持 48 个信号和 0 个正式重复。

## 已知限制和下一步

OBS 信号中不少带 `no_repair`，说明它们比正式 MB Strong 更冒险。未来若要升级，必须单独做消融、样本外验证和 Pine parity。
