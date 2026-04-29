"""Breakout strategy — buy on 20-day high, sell on 10-day low."""
from backtesting import Strategy
import pandas as pd

def highest(series, period):
    return pd.Series(series).rolling(period).max().values

def lowest(series, period):
    return pd.Series(series).rolling(period).min().values

class Breakout(Strategy):
    entry_period = 20
    exit_period = 10
    stop_loss_pct = 8

    def init(self):
        self.high_channel = self.I(highest, self.data.High, self.entry_period)
        self.low_channel = self.I(lowest, self.data.Low, self.exit_period)

    def next(self):
        if not self.position:
            if self.data.Close[-1] > self.high_channel[-2]:
                sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
                self.buy(sl=sl)
        else:
            if self.data.Close[-1] < self.low_channel[-2]:
                self.position.close()
