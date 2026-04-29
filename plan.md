# Plan: 搭建 Auto-Quant US Stocks 项目

你的任务是从零搭建一个美股量化回测项目，确保整个流程可以端到端跑通，数据是真实的。
完成后，这个项目将作为 LLM agent 自主研究循环的基础设施。

## 背景

这个项目是 https://github.com/TraderAlice/Auto-Quant 的美股版本。
原版用 FreqTrade 回测加密货币（BTC/USDT @ 1h）。
我们用 Backtesting.py 回测美股（多标的 @ 1d）。

核心设计原则：
- **本地优先**: 数据下载到本地，回测在本地跑，不依赖任何云平台
- **agent 友好**: 策略文件是普通 Python，run.py 输出结构化摘要，方便 agent 解析
- **评估合约**: config.py / prepare.py / run.py 是固定的，agent 只改 strategies/ 目录
- **先 C 再 B**: 在开发集上找策略 → 验证集测泛化 → 不通过再按波动特性分组独立优化

---

## 阶段 1: 项目骨架

创建以下文件结构：

```
Auto-Quant-Stocks/
├── pyproject.toml
├── .python-version
├── .gitignore
├── README.md
├── config.py
├── prepare.py
├── run.py
├── program.md           # 已提供，直接使用
├── strategies/
│   └── _template.py.example
├── data/                # gitignored
├── versions/
└── results.tsv          # gitignored
```

### 1.1 pyproject.toml

用 uv 管理依赖。需要的包：
- backtesting（Backtesting.py 库）
- yfinance
- pandas
- numpy
- TA-Lib（Python 绑定，需要系统先装 C 库）
- pyarrow（读写 parquet）

Python 版本 3.11+。

### 1.2 config.py

固定参数，agent 不可修改。**三层 ticker 架构**：

```python
# ═══════════════════════════════════════════════════════
# Ticker 分层架构
# ═══════════════════════════════════════════════════════

# 开发集：指数 + 大盘稳定股（低波动，策略容易收敛）
# agent 日常循环只跑这组，快速迭代
DEV_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "JPM", "WMT"]

# 验证集 1：AI/科技（高相关性，测板块内泛化）
VAL_AI = ["NVDA", "AMD", "AVGO", "TSM", "PLTR", "CRM", "CRWD"]

# 验证集 2：跨板块（低相关性，测真正泛化）
VAL_CROSS = ["TSLA", "XOM", "CAT", "LLY", "UNH", "META", "AMZN", "V"]

# 所有 ticker（prepare.py 下载用）
ALL_TICKERS = sorted(set(DEV_TICKERS + VAL_AI + VAL_CROSS))

# ═══════════════════════════════════════════════════════
# 回测参数
# ═══════════════════════════════════════════════════════
TIMERANGE_START = "2019-01-01"
TIMERANGE_END = "2025-12-31"
TIMEFRAME = "1d"
CASH = 100_000
COMMISSION = 0.001              # 0.1% round-trip
TRADE_ON_CLOSE = True
EXCLUSIVE_ORDERS = True
```

### 1.3 .gitignore

```
data/
results.tsv
__pycache__/
*.pyc
.venv/
run.log
```

### 1.4 README.md

简短说明：这是什么、怎么装、怎么跑。参考原版 Auto-Quant 的 README 风格。

**验收标准：**
- [ ] `uv sync` 成功安装所有依赖
- [ ] 项目结构完整

---

## 阶段 2: 数据下载 (prepare.py)

用 yfinance 下载 config.py 中 ALL_TICKERS 的日线 OHLCV 数据，存为 parquet。

要求：
- 下载范围: TIMERANGE_START 到 TIMERANGE_END
- 使用 `auto_adjust=True`（自动调整分红拆股）
- 每个 ticker 存为 `data/{TICKER}.parquet`
- 打印每个 ticker 下载了多少条数据
- 处理下载失败的情况（打印错误，继续下一个）

**验收标准：**
- [ ] `uv run prepare.py` 成功运行
- [ ] `data/` 目录下有 21 个 parquet 文件（ALL_TICKERS 去重后的数量）
- [ ] 每个文件有 ~1500+ 条日线数据（2019-2025 约 1750 个交易日）
- [ ] 数据包含 Open, High, Low, Close, Volume 列
- [ ] 用 pandas 读取验证：无 NaN，日期范围正确，价格合理

验证命令（完成后运行）：
```bash
uv run python -c "
import pandas as pd
from config import ALL_TICKERS
for t in ALL_TICKERS:
    df = pd.read_parquet(f'data/{t}.parquet')
    print(f'{t}: {len(df)} bars, {df.index[0].date()} → {df.index[-1].date()}, Close range: {df.Close.min():.2f} - {df.Close.max():.2f}')
"
```

---

## 阶段 3: 回测引擎 (run.py)

这是最关键的文件。支持三层验证模式。

### 3.1 运行模式

```bash
uv run run.py                  # 默认：只跑 DEV_TICKERS（日常迭代用）
uv run run.py --validate-ai    # 跑 VAL_AI（AI/科技股验证）
uv run run.py --validate-cross # 跑 VAL_CROSS（跨板块验证）
uv run run.py --validate-all   # 跑 VAL_AI + VAL_CROSS（完整验证）
uv run run.py --all            # 跑 ALL_TICKERS（全量回测）
```

根据参数选择不同的 ticker 列表，其他逻辑完全相同。

### 3.2 策略加载

- 扫描 `strategies/*.py`，跳过 `_` 开头的文件
- 用 `importlib` 动态加载，找到继承 `backtesting.Strategy` 的类
- 如果找不到策略类，报错退出（exit code 2）

### 3.3 回测执行

对每个策略 × 每个 ticker：
- 读取 `data/{ticker}.parquet`
- 创建 `Backtest` 实例，传入 config.py 的参数
- 运行 `bt.run()`
- 收集统计数据

### 3.4 输出格式

**必须严格按这个格式输出**（agent 会 grep 解析）：

```
---
strategy:         StrategyName
mode:             dev              # 或 validate-ai / validate-cross / all
commit:           abc1234
tickers:          SPY,QQQ,AAPL,MSFT,JPM,WMT
avg_return_pct:   12.34
total_return_pct: 98.72
sharpe:           1.2340
worst_drawdown:   -15.3
total_trades:     142
win_rate_pct:     54.2
per_ticker:
  SPY: +18.32% | 21 trades | DD -8.1%
  QQQ: +22.15% | 19 trades | DD -12.3%
  ...
```

关键指标说明：
- `mode`: 当前运行的 ticker 集（dev / validate-ai / validate-cross / all）
- `avg_return_pct`: 所有 ticker 收益率的平均值
- `sharpe`: mean(各 ticker 收益) / std(各 ticker 收益)，std=0 时返回 0
- `worst_drawdown`: 所有 ticker 中最大回撤（负数）
- `total_trades`: 所有 ticker 交易次数之和
- `win_rate_pct`: 总赢的次数 / 总交易次数

### 3.5 错误处理

- 单个 ticker 回测失败不应该终止整个运行
- 失败的 ticker 在 per_ticker 中显示 ERROR 和原因
- 失败的 ticker 收益按 0 计入平均

**验收标准：**
- [ ] `uv run run.py` 在没有策略时打印 "no strategies found" 并 exit 2
- [ ] 放入模板策略后，`uv run run.py` 成功输出 DEV_TICKERS 的摘要
- [ ] `uv run run.py --validate-ai` 输出 VAL_AI 的摘要
- [ ] `uv run run.py --validate-cross` 输出 VAL_CROSS 的摘要
- [ ] `uv run run.py --validate-all` 输出 VAL_AI + VAL_CROSS 的摘要
- [ ] 输出格式可被 `grep "^---" -A 20 run.log` 正确提取
- [ ] mode 字段正确反映当前运行模式

---

## 阶段 4: 策略模板 (strategies/_template.py.example)

一个最简单的 SMA 交叉策略作为起点：

要求：
- 继承 `backtesting.Strategy`
- 使用 `self.I()` 包装所有指标（防止前瞻偏差）
- 快线 SMA(10) 上穿慢线 SMA(30) → 买入
- 快线下穿慢线 → 平仓
- 类属性定义参数（fast_period, slow_period），方便后续调参
- 可以用 talib 也可以用 pandas，但 talib 优先（更快更准）

**验收标准：**
- [ ] 复制为 `strategies/SMA_Cross.py`
- [ ] `uv run run.py > run.log 2>&1` 成功
- [ ] 输出中 total_trades > 0（策略确实产生了交易）
- [ ] 结果合理：SPY 上 SMA 交叉策略通常 sharpe 在 0.3-1.5 之间

---

## 阶段 5: 端到端验证

这是最终验收。模拟一次完整的 agent 研究循环，包括三层验证。

### 5.1 建立基线（DEV 集）

```bash
cp strategies/_template.py.example strategies/Baseline.py
git add -A && git commit -m "baseline: SMA 10/30 crossover"
uv run run.py > run.log 2>&1
grep "^---" -A 20 run.log
```

记录基线结果到 results.tsv。

### 5.2 做一次改进实验

修改 Baseline.py（比如改参数、加 RSI 过滤、加止损），然后：

```bash
git commit -am "experiment: add RSI filter"
uv run run.py > run.log 2>&1
grep "^---" -A 20 run.log
```

与基线对比，决定 keep 或 discard。

### 5.3 测试 discard 流程

```bash
# 如果 discard:
git reset --hard HEAD~1
# 确认代码回到基线状态
```

### 5.4 测试多策略

创建第二个策略文件，验证 run.py 能同时输出两个策略的摘要。

### 5.5 三层验证流程测试

选一个在 DEV 集上表现最好的策略，依次跑验证：

```bash
# 第一层：DEV 集上开发（已完成）
uv run run.py > run_dev.log 2>&1
grep "^sharpe:" run_dev.log

# 第二层：AI/科技股验证
uv run run.py --validate-ai > run_vai.log 2>&1
grep "^sharpe:" run_vai.log

# 第三层：跨板块验证
uv run run.py --validate-cross > run_vcross.log 2>&1
grep "^sharpe:" run_vcross.log
```

记录三层结果，观察 sharpe 衰减情况。预期：
- DEV → VAL_AI: sharpe 可能下降（高波动股票更难）
- DEV → VAL_CROSS: sharpe 可能进一步下降（完全不同的板块）
- 如果 VAL 层 sharpe 衰减超过 50%，说明策略对 DEV 集过拟合

**验收标准：**
- [ ] 基线结果已记录到 results.tsv
- [ ] 一次改进实验完成（keep 或 discard 都行）
- [ ] `git reset --hard HEAD~1` 后代码正确回退
- [ ] 两个策略同时运行时，输出两个独立的 `---` 摘要块
- [ ] results.tsv 至少有 2 行数据（基线 + 一次实验）
- [ ] `--validate-ai` 和 `--validate-cross` 都能正常输出
- [ ] 三层验证结果已记录并打印对比
- [ ] 整个流程无需人工干预

---

## 阶段 6: 收尾

- [ ] 确认 .gitignore 正确（data/、results.tsv、run.log 不被提交）
- [ ] 确认 program.md 已放入项目根目录
- [ ] 写一个简短的 README.md
- [ ] 做一次 `git status` 确认工作区干净
- [ ] 报告最终项目状态，包括：
  - DEV 集基线 sharpe
  - VAL_AI 基线 sharpe
  - VAL_CROSS 基线 sharpe
  - 数据覆盖的 ticker 总数和日期范围

---

## 三层验证策略说明（给 agent 的上下文）

这个项目采用 **先 C 再 B** 的验证策略：

### 方案 C：DEV 集开发 → VAL 集验证

1. **日常迭代**只在 DEV_TICKERS 上跑（`uv run run.py`，无参数）
   - 快：6 个 ticker 几秒钟
   - 指数 + 大盘股波动适中，策略容易收敛
   - 这是 agent 循环的默认模式

2. **找到好策略后**跑验证（agent 自主判断时机）
   - `--validate-ai`: 测 AI/科技股适配性（NVDA, AMD, AVGO 等高波动）
   - `--validate-cross`: 测跨板块泛化（XOM, CAT, LLY 等完全不同的行业）
   - 如果策略在低波动 SPY 上有效，在高波动 NVDA 上也不崩溃 → 有真实 edge

3. **验证通过标准**
   - VAL 集 sharpe ≥ DEV 集 sharpe × 0.5（允许 50% 衰减）
   - VAL 集无单标的回撤超过 -60%
   - VAL 集 total_trades > 0（策略不能在验证集上完全不触发）

### 方案 B（fallback）：按波动特性分组

如果发现 DEV 集策略在 VAL 集上严重失效（sharpe 衰减 > 70%），说明不同波动特性的股票需要不同策略。此时切换到方案 B：

- **指数组策略**：专门针对 SPY、QQQ 优化（低波动、均值回归倾向）
- **个股组策略**：专门针对高波动个股优化（需要更快信号和更激进止损）

方案 B 是 fallback，不是默认路径。先跑 C。

---

## Ticker 分层详情

### DEV_TICKERS（开发集 — 6 只）

| Ticker | 公司 | 板块 | 选择原因 |
|--------|------|------|----------|
| SPY | S&P 500 ETF | 指数 | 大盘基准，最低波动 |
| QQQ | 纳斯达克 100 ETF | 指数 | 科技基准 |
| AAPL | Apple | 科技 | 大盘科技，波动适中 |
| MSFT | Microsoft | 科技 | 稳定增长，AI+云 |
| JPM | JPMorgan | 金融 | 银行龙头，与科技低相关 |
| WMT | Walmart | 消费必需 | 防御性，与科技负相关 |

### VAL_AI（验证集 1：AI/科技 — 7 只）

| Ticker | 公司 | 细分 | 选择原因 |
|--------|------|------|----------|
| NVDA | Nvidia | AI 芯片 | GPU 垄断，极高波动 |
| AMD | AMD | AI 芯片 | GPU 第二，数据中心 |
| AVGO | Broadcom | AI 网络 | AI 网络芯片 + 定制 ASIC |
| TSM | 台积电 ADR | 代工 | 芯片代工垄断 |
| PLTR | Palantir | AI 软件 | 政企 AI，2024-2025 涨 10 倍 |
| CRM | Salesforce | AI 应用 | 企业 AI agent 平台 |
| CRWD | CrowdStrike | 网络安全 | 安全龙头 |

### VAL_CROSS（验证集 2：跨板块 — 8 只）

| Ticker | 公司 | 板块 | 选择原因 |
|--------|------|------|----------|
| TSLA | Tesla | 消费可选 | 极高波动，事件驱动 |
| XOM | ExxonMobil | 能源 | 石油龙头，与科技负相关 |
| CAT | Caterpillar | 工业 | 重工龙头，周期性 |
| LLY | Eli Lilly | 医疗 | 减肥药，近年暴涨 |
| UNH | UnitedHealth | 医疗 | 保险龙头，稳定 |
| META | Meta | 通信 | 社交广告，高波动 |
| AMZN | Amazon | 消费可选 | 电商+云 |
| V | Visa | 金融 | 支付网络，稳增长 |

---

## 执行规则

1. **按阶段顺序执行**，每个阶段完成后运行验收标准中的检查
2. **验收失败就修**，不要跳到下一阶段
3. **数据必须是真实的**: yfinance 下载的真实市场数据，不是模拟的
4. **遇到依赖问题（特别是 TA-Lib C 库）**: 先尝试安装，如果装不了就改用 pandas 实现指标（SMA 用 `df.Close.rolling(n).mean()` 即可），不要卡在依赖上
5. **每完成一个阶段，打印当前进度**，例如 "阶段 3/6 完成"
6. **不要问我问题**，自己判断，遇到问题自己解决

## 完成标志

当你完成阶段 5 的端到端验证（包括三层验证流程）后，这个项目就可以交给另一个 agent 按 program.md 跑自主研究循环了。打印 "DONE: 项目搭建完成，可以开始自主研究" 表示结束。