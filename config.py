# DO NOT MODIFY — this is the evaluation contract

TICKERS = ["SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]
TIMERANGE_START = "2019-01-01"
TIMERANGE_END = "2025-12-31"
TIMEFRAME = "1d"                # daily candles
CASH = 100_000                  # starting capital
COMMISSION = 0.001              # 0.1% round-trip (Interactive Brokers ballpark)
TRADE_ON_CLOSE = True           # execute on close price (avoid look-ahead)
EXCLUSIVE_ORDERS = True         # one position per ticker at a time
