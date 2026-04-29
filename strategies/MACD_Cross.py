"""MACD crossover strategy — momentum via moving average convergence."""
from backtesting import Strategy
import pandas as pd

def ema(series, period):
    return pd.Series(series).ewm(span=period, adjust=False).mean().values

def macd(close, fast=12, slow=26, signal=9):
    fast_ema = ema(close, fast)
    slow_ema = ema(close, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line

class MACD_Cross(Strategy):
    fast_period = 12
    slow_period = 26
    signal_period = 9
    stop_loss_pct = 8

    def init(self):
        self.macd_line, self.signal_line = self.I(
            macd, self.data.Close, self.fast_period, self.slow_period, self.signal_period
        )

    def next(self):
        if not self.position:
            # Buy when MACD crosses above signal
            if (self.macd_line[-2] < self.signal_line[-2] and
                self.macd_line[-1] > self.signal_line[-1]):
                sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
                self.buy(sl=sl)
        else:
            # Sell when MACD crosses below signal
            if (self.macd_line[-2] > self.signal_line[-2] and
                self.macd_line[-1] < self.signal_line[-1]):
                self.position.close()
