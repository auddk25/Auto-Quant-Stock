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
