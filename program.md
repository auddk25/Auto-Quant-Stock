# Auto-Quant US Stocks

This is an experiment to have the LLM do its own quantitative research on US equities.

An autonomous research loop: modify strategy files, run a backtest, check if
results improved, keep or discard, and repeat. Over many iterations we're trying
to observe which patterns an LLM finds useful on US stocks, not to deploy a
profitable strategy.

## Architecture

This project replaces the crypto-focused FreqTrade stack with a generic,
local-first setup:

| Layer         | Crypto (original)        | US Stocks (this repo)          |
|---------------|--------------------------|--------------------------------|
| Data          | FreqTrade + Binance API  | yfinance → local parquet       |
| Backtest      | FreqTrade Backtesting    | Backtesting.py                 |
| Strategy file | FreqTrade IStrategy      | Backtesting.py Strategy class  |
| Timeframe     | 1h candles               | 1d candles (daily)             |
| Assets        | BTC/USDT, ETH/USDT       | Configurable ticker universe   |

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

## Project Structure

```
Auto-Quant-Stocks/
├── README.md
├── pyproject.toml              # deps: backtesting, yfinance, pandas, ta-lib, numpy
├── config.py                   # FIXED — tickers, timerange, cash, commission
├── prepare.py                  # FIXED — downloads OHLCV → data/*.parquet
├── run.py                      # FIXED — discovers strategies, runs backtest, prints summary
├── strategies/
│   ├── _template.py.example    # skeleton strategy — copy to start new ones
│   └── <agent-created>.py      # up to 3 active strategies at a time
├── data/                       # gitignored — downloaded OHLCV parquet files
├── results.tsv                 # gitignored — agent event log
└── versions/                   # frozen snapshots of past runs
```

---

## config.py — Evaluation Contract

```python
# DO NOT MODIFY — this is the evaluation contract

TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]
TIMERANGE_START = "2019-01-01"
TIMERANGE_END = "2025-12-31"
TIMEFRAME = "1d"                # daily candles
CASH = 100_000                  # starting capital
COMMISSION = 0.001              # 0.1% round-trip (Interactive Brokers ballpark)
TRADE_ON_CLOSE = True           # execute on close price (avoid look-ahead)
EXCLUSIVE_ORDERS = True         # one position per ticker at a time
```

The user may customize the ticker universe before starting. Once the experiment
begins, config.py is frozen.

---

## prepare.py — Data Download

```python
"""One-time data download. Do not modify."""
import yfinance as yf
import os
from config import TICKERS, TIMERANGE_START, TIMERANGE_END

os.makedirs("data", exist_ok=True)

for ticker in TICKERS:
    print(f"Downloading {ticker}...")
    df = yf.download(ticker, start=TIMERANGE_START, end=TIMERANGE_END, auto_adjust=True)
    df.to_parquet(f"data/{ticker}.parquet")
    print(f"  {len(df)} bars saved")

print("Done.")
```

---

## run.py — Backtest Oracle

```python
"""
Batch backtest runner. Discovers all .py files in strategies/ (skipping _ prefix),
runs Backtesting.py for each on every ticker, prints summary block.
Do not modify.
"""
import importlib.util
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from backtesting import Backtest
from config import TICKERS, CASH, COMMISSION, TRADE_ON_CLOSE, EXCLUSIVE_ORDERS

def load_strategy(path):
    """Dynamically load a strategy class from a .py file."""
    spec = importlib.util.spec_from_file_location("strategy", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Find the first class that inherits from backtesting.Strategy
    from backtesting import Strategy
    for attr in dir(mod):
        obj = getattr(mod, attr)
        if isinstance(obj, type) and issubclass(obj, Strategy) and obj is not Strategy:
            return obj
    raise ValueError(f"No Strategy subclass found in {path}")

def run_one(strategy_cls, ticker):
    """Run backtest on one ticker, return stats dict."""
    df = pd.read_parquet(f"data/{ticker}.parquet")
    bt = Backtest(
        df, strategy_cls,
        cash=CASH,
        commission=COMMISSION,
        trade_on_close=TRADE_ON_CLOSE,
        exclusive_orders=EXCLUSIVE_ORDERS,
    )
    stats = bt.run()
    return stats

def main():
    strat_dir = Path("strategies")
    strat_files = sorted([
        f for f in strat_dir.glob("*.py")
        if not f.name.startswith("_")
    ])

    if not strat_files:
        print("no strategies found — create at least one .py in strategies/")
        sys.exit(2)

    commit = os.popen("git rev-parse --short HEAD 2>/dev/null").read().strip() or "unknown"

    for sf in strat_files:
        strategy_cls = load_strategy(sf)
        all_returns = []
        all_trades = 0
        all_wins = 0
        worst_dd = 0
        ticker_results = []

        for ticker in TICKERS:
            try:
                stats = run_one(strategy_cls, ticker)
                ret = stats["Return [%]"]
                dd = stats["Max. Drawdown [%]"]
                trades = stats["# Trades"]
                win_rate = stats["Win Rate [%]"] if trades > 0 else 0

                all_returns.append(ret)
                all_trades += trades
                all_wins += int(trades * win_rate / 100)
                worst_dd = min(worst_dd, dd)

                ticker_results.append(f"  {ticker}: {ret:+.2f}% | {trades} trades | DD {dd:.1f}%")
            except Exception as e:
                ticker_results.append(f"  {ticker}: ERROR — {e}")
                all_returns.append(0)

        avg_return = np.mean(all_returns)
        total_return = np.sum(all_returns)
        overall_win_rate = (all_wins / all_trades * 100) if all_trades > 0 else 0

        # Simplified sharpe: mean(returns) / std(returns) if std > 0
        sharpe = (np.mean(all_returns) / np.std(all_returns)) if np.std(all_returns) > 0 else 0

        print(f"---")
        print(f"strategy:         {sf.stem}")
        print(f"commit:           {commit}")
        print(f"tickers:          {','.join(TICKERS)}")
        print(f"avg_return_pct:   {avg_return:.2f}")
        print(f"total_return_pct: {total_return:.2f}")
        print(f"sharpe:           {sharpe:.4f}")
        print(f"worst_drawdown:   {worst_dd:.1f}")
        print(f"total_trades:     {all_trades}")
        print(f"win_rate_pct:     {overall_win_rate:.1f}")
        print(f"per_ticker:")
        for line in ticker_results:
            print(line)
        print()

if __name__ == "__main__":
    main()
```

---

## Strategy Template

`strategies/_template.py.example`:

```python
"""
Strategy template for Auto-Quant US Stocks.
Copy this file, rename it (without _ prefix), and modify.

Rules:
- Must define exactly one class that inherits from backtesting.Strategy
- Must implement init() and next()
- Timeframe is daily (1d) — set by data, not by strategy
- Use self.I() to wrap indicators (avoids look-ahead bias)
- Use self.buy() / self.sell() / self.position.close() for trades
"""
from backtesting import Strategy
from backtesting.lib import crossover
import talib

class MyStrategy(Strategy):
    # Parameters — agent can tune these
    fast_period = 10
    slow_period = 30

    def init(self):
        close = self.data.Close
        self.fast_ma = self.I(talib.SMA, close, timeperiod=self.fast_period)
        self.slow_ma = self.I(talib.SMA, close, timeperiod=self.slow_period)

    def next(self):
        if crossover(self.fast_ma, self.slow_ma):
            self.buy()
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()
```

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

**Key differences from crypto version:**

* Daily bars, not hourly. Indicators need different period tuning.
* Multiple tickers — strategy must generalize across the universe, not overfit to one.
* Stocks have different microstructure: dividends (auto-adjusted), market hours,
  sector correlations, earnings events.
* Mean-reversion tends to work better on stocks than crypto. Momentum also works
  but at different timescales.

**The goal**: get the highest cross-ticker `sharpe` on the `---` summary, subject
to common sense — a sharpe of 5 with 3 trades is not real signal. You should judge
the **full summary block** when deciding keep vs discard, not just sharpe.

**Simplicity criterion**: All else being equal, simpler is better. A small
improvement that adds ugly complexity is not worth it.

**The first run**: Your very first run should always be to establish the baseline
using the template strategy as-is.

---

## Output format

`run.py` prints one summary block per strategy:

```
---
strategy:         MyStrategy
commit:           abc1234
tickers:          SPY,QQQ,AAPL,MSFT,GOOGL,AMZN,NVDA,META
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

For a richer read, `grep "^---" -A 20 run.log` dumps the whole block.

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
   * Does it generalize? (Good on 1 ticker but terrible on 7 others = overfit)
   * Is the drawdown acceptable?
   * Does the change make conceptual sense for equities?
8. Record the results in `results.tsv`
9. If kept: branch advances. If discarded: `git reset --hard HEAD~1`

**Multi-strategy management** (up to 3 slots):

* `create`: copy `_template.py.example` → new `.py`, implement a fresh idea
* `evolve`: modify an existing strategy (tweak params, change logic)
* `fork`: copy a working strategy, diverge it in a new direction
* `kill`: delete a strategy that's consistently underperforming
* `stable`: a strategy is good enough, don't touch it this round

**Stagnation rule**: A strategy cannot stay `stable` for more than 3 consecutive
rounds — you must evolve, fork, or kill it.

**Timeout**: Each backtest should take under 2 minutes. If a run exceeds 5 minutes,
kill it and treat as failure.

**NEVER STOP**: Once the experiment loop has begun, do NOT pause to ask the human
if you should continue. The human may be asleep. You are autonomous. If you run out
of ideas, think harder:

* Indicators you haven't tried: ATR, ADX, CCI, Williams %R, Ichimoku, Keltner
* Paradigms: momentum, mean-reversion, breakout, volatility contraction,
  sector-relative strength, gap strategies, earnings avoidance
* Regime filters: VIX-based, 200-day SMA, breadth indicators
* Position sizing: volatility-weighted, equal-risk, Kelly criterion
* Multi-timeframe: compute weekly indicators on daily data
* Combine near-misses from previous experiments

The loop runs until the human interrupts you, period.

---

## Stock-specific research hints

These are starting points, not constraints. The agent is free to ignore all of them.

* **SPY/QQQ are index ETFs** — they trend more smoothly than individual stocks.
  A strategy that works on SPY might fail on NVDA (higher vol) and vice versa.
* **Earnings create gaps** — strategies sensitive to overnight gaps may struggle
  around earnings dates. Consider an earnings-avoidance filter.
* **Sector rotation** — tech stocks (AAPL, MSFT, GOOGL, AMZN, NVDA, META) are
  highly correlated. If all 6 are long simultaneously, it's basically one bet.
* **Volatility regimes** — the VIX (or ATR) can distinguish trending vs choppy
  markets. Many strategies only work in one regime.
* **Daily bars mean less noise** — crypto 1h has massive whipsaw. Daily stock
  bars are smoother. Indicators like RSI(14) are calibrated for daily by default.
* **Buy-and-hold is a strong baseline** — SPY returned ~15% annualized 2019-2025.
  Beating it consistently is hard.