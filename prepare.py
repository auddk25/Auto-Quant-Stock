"""One-time data download. Do not modify."""
import yfinance as yf
import pandas as pd
import os
from config import TICKERS, TIMERANGE_START, TIMERANGE_END

os.makedirs("data", exist_ok=True)

for ticker in TICKERS:
    print(f"Downloading {ticker}...")
    try:
        df = yf.download(ticker, start=TIMERANGE_START, end=TIMERANGE_END, auto_adjust=True)
        # Flatten multi-level columns from yfinance (e.g. ('Close', 'SPY') -> 'Close')
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.to_parquet(f"data/{ticker}.parquet")
        print(f"  {len(df)} bars saved")
    except Exception as e:
        print(f"  ERROR: {e}")

print("Done.")
