# Auto-Quant US Stocks

This is an experiment to have the LLM do its own quantitative research on US equities.

An autonomous research loop: modify strategy files, run a backtest, check if
results improved, keep or discard, and repeat. Over many iterations we're trying
to observe which patterns an LLM finds useful on US stocks, not to deploy a
profitable strategy.

## Architecture

| Layer         | Crypto (original)        | US Stocks (this repo)          |
|---------------|--------------------------|--------------------------------|
| Data          | FreqTrade + Binance API  | yfinance → local parquet       |
| Backtest      | FreqTrade Backtesting    | Backtesting.py                 |
| Strategy file | FreqTrade IStrategy      | Backtesting.py Strategy class  |
| Timeframe     | 1h candles               | 1d candles (daily)             |
| Assets        | BTC/USDT, ETH/USDT       | 3-tier US stock universe       |

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `apr29`).
   The branch `autoresearch/<tag>` must not already exist — this is a fresh run.

2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current main.

3. **Read the in-scope files**. The repo is small. Read these files for full context:
   * `README.md` — repository context
   * `config.py` — fixed config (tickers, timerange, cash, commission). Do not modify.
   * `prepare.py` — data download via yfinance. Do not modify.
   * `run.py` — the backtest oracle. Do not modify.
   * `strategies/` — **the directory you own**

4. **Verify data exists**: Check that parquet files exist under `data/`.
   If not, tell the user to run `uv run prepare.py`.

5. **Initialize results.tsv**: Create `results.tsv` with just the header row.
   The baseline will be recorded after the first run.

6. **Confirm and go**: Confirm setup looks good with the user.

Once you get confirmation, kick off the experimentation.

---

## Ticker Universe — 3-Tier Architecture

```python
DEV_TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "JPM", "WMT"]
VAL_AI      = ["NVDA", "AMD", "AVGO", "TSM", "PLTR", "CRM", "CRWD"]
VAL_CROSS   = ["TSLA", "XOM", "CAT", "LLY", "UNH", "META", "AMZN", "V"]
```

- **DEV**: 日常迭代用。指数 + 大盘稳定股，低波动，策略容易收敛。
- **VAL_AI**: AI/科技股验证。高波动，高相关性，测板块内泛化。
- **VAL_CROSS**: 跨板块验证。低相关性，测真正泛化能力。

---

## Experimentation

Each experiment runs a backtest on a **fixed timerange** and **fixed ticker universe**
defined in `config.py`. A single backtest takes roughly 5-30 seconds.

**What you CAN do:**

* Create / modify / delete files in `strategies/`. Everything inside is fair game:
  indicators, entry/exit logic, position sizing, stop-loss, take-profit, etc.
* Up to 3 active strategies at a time (files without `_` prefix).
* Use any indicator from TA-Lib, pandas, numpy.
* Test different paradigms: momentum, mean-reversion, factor-based, volatility,
  breakout, pairs trading, sector rotation, etc.

**What you CANNOT do:**

* Modify `prepare.py`, `run.py`, or `config.py`. These are the evaluation contract.
* `uv add` new dependencies. Use what's in `pyproject.toml`.
* Call any CLI tool other than `uv run run.py` for backtesting.
* Modify the timerange or ticker list.
* Use future data in indicators (Backtesting.py guards against this via `self.I()`).

**The goal**: get the highest cross-ticker `sharpe` on the `---` summary, subject
to common sense — a sharpe of 5 with 3 trades is not real signal. You should judge
the **full summary block** when deciding keep vs discard, not just sharpe.

**Simplicity criterion**: All else being equal, simpler is better.

**The first run**: Your very first run should always be to establish the baseline
using the template strategy as-is.

---

## Run Modes

```bash
uv run run.py                  # DEV_TICKERS only (DEFAULT — use this for daily loop)
uv run run.py --validate-ai    # VAL_AI only
uv run run.py --validate-cross # VAL_CROSS only
uv run run.py --validate-all   # VAL_AI + VAL_CROSS
uv run run.py --all            # ALL_TICKERS
```

**Daily loop uses DEFAULT mode (no flags).** Validation runs are triggered by you
when a strategy looks promising.

---

## Output format

`run.py` prints one summary block per strategy:

```
---
strategy:         MyStrategy
mode:             dev
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

Extract key metrics: `grep "^sharpe:\|^total_trades:\|^worst_drawdown:\|^avg_return_pct:" run.log`

Full block: `grep "^---" -A 20 run.log`

---

## Logging results

Log every experiment to `results.tsv` (**tab**-separated).

Header and columns:

```
commit	sharpe	max_dd	status	description
```

1. git commit hash (short, 7 chars)
2. sharpe (e.g. 1.2340) — use 0.0000 for crashes
3. worst drawdown as positive number (e.g. 15.3)
4. status: `keep`, `discard`, or `crash`
5. short description of what was tried **and why you kept or discarded**

Do NOT commit `results.tsv` — leave it untracked.

---

## The experiment loop

LOOP FOREVER:

1. Look at the git state: current branch, current commit
2. Choose an experiment: modify an existing strategy or create a new one in `strategies/`
3. `git commit -am "<short description>"`
4. Run the backtest: `uv run run.py > run.log 2>&1`
5. Read the summary: `grep "^---" -A 20 run.log`
6. If the summary is empty or malformed, the run crashed. Run `tail -n 50 run.log`
   to read the stack trace and attempt a fix.
7. **Decide keep or discard** by reading the full summary:
   * Is the sharpe improvement real or noise?
   * Is the trade count reasonable? (< 5 total trades = not interpretable)
   * Does it generalize across DEV tickers? (Good on SPY but terrible on JPM = suspect)
   * Is the drawdown acceptable?
   * Does the change make conceptual sense for equities?
8. Record the results in `results.tsv`
9. If kept: branch advances. If discarded: `git reset --hard HEAD~1`

---

## Validation Protocol — When and How

### When to validate

Run validation when **any** of these are true:
- A strategy has sharpe > 1.0 on DEV set
- A strategy has been kept for 5+ consecutive rounds
- You've completed 20+ experiments and want to check the best one
- You're about to fork or kill a strategy and want final confirmation

### How to validate

```bash
# Step 1: Record DEV performance
uv run run.py > run_dev.log 2>&1
grep "^sharpe:" run_dev.log
# → e.g. sharpe: 1.2340

# Step 2: AI/tech validation
uv run run.py --validate-ai > run_vai.log 2>&1
grep "^sharpe:" run_vai.log
# → e.g. sharpe: 0.8100

# Step 3: Cross-sector validation
uv run run.py --validate-cross > run_vcross.log 2>&1
grep "^sharpe:" run_vcross.log
# → e.g. sharpe: 0.6500
```

### Validation pass/fail criteria

**PASS** (strategy generalizes):
- VAL sharpe ≥ DEV sharpe × 0.5 (allow 50% decay)
- No single VAL ticker drawdown worse than -60%
- VAL total_trades > 0 (strategy actually triggers)

**FAIL** (strategy is overfit to DEV):
- VAL sharpe < DEV sharpe × 0.3 (>70% decay)
- Multiple VAL tickers with zero trades
- VAL worst_drawdown much worse than DEV

### What to do when validation fails

If validation fails consistently (3+ strategies fail), switch to **方案 B**:
create separate strategy files optimized for different volatility profiles.

- **Index strategy** (`strategies/Index_*.py`): optimized for SPY, QQQ — slower signals,
  mean-reversion friendly, tighter stops
- **Growth strategy** (`strategies/Growth_*.py`): optimized for high-vol individual stocks —
  faster signals, wider stops, momentum-oriented

Each group gets its own DEV/validation cycle. This is the fallback, not the default.

---

## Multi-strategy management

Up to 3 slots. Events:

* `create`: copy `_template.py.example` → new `.py`, implement a fresh idea
* `evolve`: modify an existing strategy (tweak params, change logic)
* `fork`: copy a working strategy, diverge it in a new direction
* `kill`: delete a strategy that's consistently underperforming
* `stable`: a strategy is good enough, don't touch it this round

**Stagnation rule**: A strategy cannot stay `stable` for more than 3 consecutive
rounds — you must evolve, fork, or kill it.

**Timeout**: Each backtest should take under 2 minutes. If a run exceeds 5 minutes,
kill it and treat as failure.

---

## NEVER STOP

Once the experiment loop has begun, do NOT pause to ask the human if you should
continue. The human may be asleep. You are autonomous. If you run out of ideas,
think harder:

* Indicators you haven't tried: ATR, ADX, CCI, Williams %R, Ichimoku, Keltner,
  Donchian channels, VWAP proxy, OBV, MFI
* Paradigms: momentum, mean-reversion, breakout, volatility contraction,
  sector-relative strength, gap strategies
* Regime filters: VIX proxy (via ATR), 200-day SMA, breadth approximation
* Position sizing: volatility-weighted, equal-risk, Kelly criterion
* Multi-timeframe: compute weekly indicators on daily data
* Combine near-misses from previous experiments
* Try the opposite of what's been working (if momentum keeps winning, test
  mean-reversion; if everything is trend-following, try counter-trend)

The loop runs until the human interrupts you, period.

---

## Stock-specific research hints

Starting points, not constraints. Free to ignore.

* **SPY/QQQ are index ETFs** — smoother trends than individual stocks.
* **Earnings create gaps** — strategies sensitive to overnight gaps may struggle.
* **MAG7 are highly correlated** — all long simultaneously = one bet.
* **Volatility regimes** — ATR can distinguish trending vs choppy markets.
* **Daily bars = less noise** — RSI(14), SMA(50/200) calibrated for daily by default.
* **Buy-and-hold is a strong baseline** — SPY ~15% annualized 2019-2025. Beating it is hard.
* **2022 was a bear market** — strategies must survive it, not just thrive in 2023-2024 bull.
* **Sector rotation happened in 2026** — energy/industrials beat tech. Good strategies adapt.