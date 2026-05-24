# Bottom Signal 中文学习版 README

这份文档不是给机器看的配置说明，而是给人学习用的策略推理笔记。它解释当前 `bottom_signal_pine.pine` 为什么成为主 TradingView 文件、搜索过程是怎么一步步收敛的，以及 `BUY-MB`、`BUY-D`、`BUY-S` 各自代表什么。

相关产物：

- 主 Pine：`bottom_signal_pine.pine`
- 严格 MB 归档 Pine：`bottom_signal_strict_formal.pine`
- 主结果：`bottom_signal_results.json`
- 主报告：`bottom_signal_report.md`
- OBS 报告：`../bottom_signal_observation_addon/bottom_signal_observation_report.md`

## 1. 当前结论

当前主策略不是一个单纯的“最低点预测器”。它更像一个分层筛选器：先确认市场处在值得关注的深回撤环境，再用多个技术因子判断个股或指数是否进入高质量底部区域。

现在 TradingView 里最应该使用的是：

```text
strategy_catalog/bottom_signal_formal/bottom_signal_pine.pine
```

这个 Pine 已经把三类买点整合到一个文件里：

- `BUY-MB`：严格 MB Strong 买点，是原始正式基线。
- `BUY-D`：来自 OBS-D，表示深回撤后的二次确认观察买点。
- `BUY-S`：来自 OBS-S，表示浅回撤后的观察买点。

为什么说它已经接近当前阶段的最优使用形态？因为它同时满足两个目标：

- 保留严格 MB 的历史验证结果，不把原来的正式基线弄乱。
- 解决 TradingView 使用时看不到 2022/2026 OBS 覆盖窗口的问题，让用户只导入一个主 Pine 就能看到完整买点显示。

注意：这不是说 OBS 的收益统计已经自动变成新的正式回测结果。当前正式收益统计仍来自严格 MB Strong；`BUY-D` 和 `BUY-S` 是整合显示后的观察来源。

## 2. 策略目标

这个策略要解决的问题不是“哪一天一定是最低点”。这种目标太容易过拟合，也不现实。

更合理的目标是：

```text
在市场明显回撤后，找到风险收益比更好的入场窗口。
```

所以策略的思路是：

1. 先看大盘是否真的跌得够深。
2. 再看目标股票或 ETF 是否也进入低位。
3. 再看价格有没有修复、结构、成交量和均线位置上的支持。
4. 最后控制信号数量，避免一个策略到处乱喊买入。

这也是为什么当前策略不会每天给信号。信号少是设计目标的一部分。

## 3. 数据来源和样本池

当前主结果来自 full-pool 数据，不是只看 QQQ 的小样本。

主结果文件 `bottom_signal_results.json` 记录了：

- `sampleKind=FULL_POOL`
- full-pool 共 21 个 symbol
- 当前最佳配置名：`seed_previous_rs_higher_low_best`

样本池包括大型科技股、指数 ETF、传统行业股票和防御性股票，例如 AAPL、AMZN、AVGO、META、MSFT、NVDA、QQQ、SPY、TSLA、V、JPM、XOM 等。

这里使用的是日线 OHLCV 数据。简单说：

- O：开盘价
- H：最高价
- L：最低价
- C：收盘价
- V：成交量

市场过滤使用 QQQ 和 SPY。原因很直接：如果整个市场没有进入回撤环境，只靠单个股票局部下跌去判断“底部”，误判概率会高很多。

## 4. MB 主策略的核心推理

MB 可以理解成 Market Bottom，也就是“市场底部环境下的买点”。它不是只看一个指标，而是把几个因素合成一个 `bottomScore`。

### drawdown：有没有真的跌下来

`drawdown` 看的是当前价格相对近期高点跌了多少。

它解决的问题是：避免在高位或者普通小回调里误判底部。

如果价格离高点只跌了一点，策略不会轻易认为这是底部。

### momentum：下跌动能有没有缓和

这里主要看 RSI、Stochastic 等动量指标。

它解决的问题是：价格虽然跌了，但是否已经从极端弱势里开始缓和。

单纯跌得深不够，因为有些股票会继续跌。动量缓和是一个必要的确认。

### structure：价格结构是否接近低位区域

结构不是预测形态，而是看价格是不是还在近期低点附近、有没有形成二次确认的可能。

它解决的问题是：避免价格已经大幅反弹后才追进去。

### volume：成交量是否支持

成交量用于判断当前低位是否有足够交易活动。

低成交量下的价格变化可能不可靠，所以成交量是一个质量过滤。

### ma：相对均线的位置

均线距离用来衡量价格是否处在折价区间。

如果价格远高于均线，通常不符合底部买点的语境。

### repair：刹车，而不是油门

`repair` 是当前策略里很重要的概念。它不是为了制造更多信号，而是为了过滤掉“跌得很深但完全没有修复迹象”的情况。

换句话说：

```text
跌得深只是候选，开始修复才更接近可操作。
```

这也是为什么有些 2022/2026 的位置严格 MB 没有触发。它们可能跌得够深，但 repair 或正式门槛不够。

## 5. 搜索过程是怎么推进的

搜索不是凭感觉调一个参数，而是批量测试很多配置，再用统一规则打分。

搜索范围包括：

- 回撤窗口和回撤阈值
- RSI、Stochastic、MACD 参数
- 均线周期
- ATR 和成交量窗口
- 入场分数
- 信号间隔
- RS 相关结构参数

主搜索命令记录在 `docs/策略目录.md` 和 `bottom_signal_report.md`：

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4
```

搜索的重点不是“找收益最高的配置”。只追求最高收益很危险，因为它可能只是刚好适配历史数据。

当前搜索更重视：

- 底部质量
- 交易结果
- 退出质量
- 信号数量是否受控
- 是否覆盖不同年份和不同股票
- 是否覆盖 QQQ/SPY 和个股

简单说，就是不能只在一个年份、一个股票、一个特殊行情里有效。

## 6. 为什么选 `seed_previous_rs_higher_low_best`

当前最佳配置是：

```text
seed_previous_rs_higher_low_best
```

它的核心结果在 `bottom_signal_results.json` 和 `bottom_signal_report.md` 里可以查到：

- 严格 Strong 信号：39 个
- 6 个月平均收益：39.24%
- 6 个月胜率：74.36%
- full-pool：21 个 symbol
- 当前正式入场门槛：82

这里最重要的不是“收益数字看起来高”，而是它在信号数量、覆盖范围和历史表现之间比较平衡。

如果一个配置收益更高但信号极少，可能只是运气。

如果一个配置覆盖更多年份但发出几百个信号，那就太宽松，实盘意义会下降。

所以当前选择的逻辑是：

```text
宁可少发高质量信号，也不为了覆盖所有低点而让信号泛滥。
```

## 7. 2022/2026 问题是怎么处理的

之前最大的问题是：严格 MB Strong 没有覆盖 QQQ 的两个关键窗口：

- 2022 Q4
- 2026 March

但 OBS 层覆盖了它们：

- QQQ 2022 Q4：2022-10-03、2022-10-11、2022-12-28
- QQQ 2026 March：2026-03-27

其中 `2026-03-27` 在 OBS 信号 CSV 里是 `OBS-S`。

为什么不直接把严格 MB 门槛降低？因为全量探索发现，能覆盖这些窗口的单一正式参数会让信号数量膨胀。之前的研究结论是：单一正式参数替代失败，因为最低也有 319 个信号。

这说明问题不是“把门槛调低一点就好”，而是需要分层：

- 严格 MB 继续作为历史统计基线。
- OBS 作为补充观察来源。
- TradingView 主 Pine 把二者整合显示，解决实际使用时看不到信号的问题。

这就是现在 `BUY-MB`、`BUY-D`、`BUY-S` 共存的原因。

## 8. 当前 Pine 信号怎么读

主 Pine 文件是：

```text
bottom_signal_pine.pine
```

导入 TradingView 后，主要看三类买点。

### BUY-MB

`BUY-MB` 是原严格 MB Strong。

它对应当前回测统计里的正式基线。你可以把它理解成最严格、最保守的一类买点。

### BUY-D

`BUY-D` 来自 OBS-D。

它通常代表深回撤环境下，价格处于低位附近，但没有完全满足严格 MB Strong 的情况。

它的意义是：值得看，不等于原始 MB Strong。

### BUY-S

`BUY-S` 来自 OBS-S。

它通常代表浅一些的市场回撤或修复窗口。2026-03-27 的 QQQ 覆盖就来自这一类。

它解决的是：严格 MB 没触发，但观察层认为这个位置仍值得复盘。

### RS

RS 是相对强度观察。

它回答的是“谁更值得优先看”，不是“现在能不能买”。

所以 RS 不能替代 `BUY-MB`、`BUY-D`、`BUY-S`。

### Exit

Exit 是退出或风险提示层。

它不是本轮策略的核心买点，但可以辅助判断持仓是否过热。

## 9. 过拟合防线

策略研究里最大的敌人不是“收益不够高”，而是过拟合。

过拟合的意思是：一个规则在历史数据里看起来很好，但只是刚好贴合过去，未来不一定有效。

当前用了几道防线。

### 信号数量不能失控

严格 MB 当前只有 39 个 Strong 信号。

如果某个配置为了覆盖 2022/2026，把信号扩到几百个，就不再是稀缺底部信号。

### 必须跨市场阶段

策略不能只在 2020 或 2022 这种特殊年份有效。

搜索会检查不同市场阶段，包括金融危机后、疫情行情、通胀加息阶段和近期样本。

### 必须跨股票

只在一个股票上有效不够。

所以当前使用 full-pool 21 个 symbol，而不是只看 QQQ。

### OBS 不伪装成 MB

现在主 Pine 会显示 `BUY-D` 和 `BUY-S`，但文档和表格仍保留来源。

这很重要：显示上整合，不等于统计上混同。

如果未来要把 OBS 正式升级为独立策略，需要重新做消融、样本外验证和 Pine parity 检查。

## 10. 如何自己继续研究

如果你想从结果开始看，建议顺序是：

1. 先看本文件，理解策略思想。
2. 再看 `README.md`，确认主 Pine 和核心文件。
3. 再看 `bottom_signal_report.md`，了解搜索结果。
4. 再看 `../bottom_signal_observation_addon/bottom_signal_observation_report.md`，理解 OBS 来源。
5. 再看 `bottom_signal_results.json`，查原始 JSON 结果。

如果你想重新跑最小验证：

```powershell
.venv\Scripts\python.exe -m unittest tests.test_bottom_signal_search
.venv\Scripts\python.exe -m py_compile investigations\bottom_signal_model.py investigations\bottom_signal_paths.py investigations\bottom_signal_search.py tests\test_bottom_signal_search.py
.venv\Scripts\python.exe -m json.tool strategy_catalog\bottom_signal_formal\bottom_signal_results.json > $null
git diff --check
```

如果你想重新跑完整搜索：

```powershell
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --max-configs 720 --workers 4
.venv\Scripts\python.exe investigations\bottom_signal_search.py --symbol all --refresh-observation-search
```

不建议直接改这些文件：

- `config.py`
- `prepare.py`
- `run.py`
- `versions/`

这些文件不是当前 Bottom Signal 策略研究的主入口。当前主入口是 `investigations/bottom_signal_search.py`，主输出在 `strategy_catalog/bottom_signal_formal/`。

## 11. 术语表

### score

分数。策略把多个指标压缩成 1 到 100 的分数，方便比较。

### threshold

门槛。比如入场门槛 82，意思是分数达到 82 才允许触发严格买点。

### validation

验证。不是看一个信号赚没赚钱，而是检查一组规则在不同股票、不同年份、不同市场环境里是否稳定。

### MB

Market Bottom。这里指市场深回撤背景下的底部买点主逻辑。

### OBS

Observation。观察层。它用于捕捉严格 MB 没覆盖、但值得复盘的位置。

### RS

Relative Strength。相对强度。它帮助排序“谁更值得看”，但不单独决定买入。

### repair

修复因子。它判断价格有没有从极弱状态中恢复一点。它更像刹车，防止策略在完全没有修复迹象时过早入场。

### Pine parity

Pine 一致性。意思是 TradingView 里的 Pine 逻辑要尽量和 Python 研究逻辑一致，避免 Python 里有信号、TradingView 里看不到。

## 12. 最后怎么理解当前策略

当前策略可以用一句话理解：

```text
严格 MB 负责保守基线，OBS 负责补足关键漏掉窗口，主 Pine 负责把它们合并成一个可用的 TradingView 入口。
```

所以你现在看到的 `bottom_signal_pine.pine`，不是随便把两个脚本拼起来，而是一次策略研究后的压缩结果：

- 保留严格基线。
- 保留 2022/2026 问题的研究证据。
- 避免降低门槛导致信号爆炸。
- 把实际使用入口统一到一个 Pine 文件。

这就是它目前最有价值的地方。
