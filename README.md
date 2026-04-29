# Auto-Quant US Stocks

LLM-native autonomous quant research loop for US equities. Based on
[Auto-Quant](https://github.com/TraderAlice/Auto-Quant) (crypto version),
re-adapted for US stocks using Backtesting.py + yfinance.

## How it works

- **`config.py`** — fixed config: tickers, timerange, cash, commission. Agent does not touch.
- **`prepare.py`** — one-time data download via yfinance → `data/*.parquet`. Agent does not touch.
- **`run.py`** — batch backtest runner. Discovers strategies in `strategies/`, runs Backtesting.py
  for each on every ticker, prints structured summary. Agent does not touch.
- **`strategies/`** — **the directory the agent owns.** Each `.py` is one strategy.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Install

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install deps
uv sync

# 3. Download data (~1 min)
uv run prepare.py

# 4. Verify — should print "no strategies found" and exit 2
uv run run.py
```

## Running

```bash
# Run all strategies
uv run run.py > run.log 2>&1
grep "^---" -A 20 run.log
```

## Project structure

```
Auto-Quant-Stock/
├── README.md
├── pyproject.toml
├── config.py              # FIXED — tickers, timerange, cash, commission
├── prepare.py             # FIXED — downloads OHLCV → data/*.parquet
├── run.py                 # FIXED — backtest + summary
├── program.md             # agent instructions
├── strategies/
│   └── _template.py.example
├── data/                  # gitignored — downloaded OHLCV
├── results.tsv            # gitignored — agent event log
└── versions/              # frozen snapshots of past runs
```

## License

MIT.
