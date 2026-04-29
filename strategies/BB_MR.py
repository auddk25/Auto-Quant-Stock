"""Bollinger Bands mean-reversion — buy at lower band, sell at middle."""
from backtesting import Strategy
import pandas as pd
import numpy as np

def bb_upper(close, period=20, std_dev=2):
    c = pd.Series(close)
    mid = c.rolling(period).mean()
    std = c.rolling(period).std()
    return (mid + std_dev * std).values

def bb_middle(close, period=20):
    return pd.Series(close).rolling(period).mean().values

def bb_lower(close, period=20, std_dev=2):
    c = pd.Series(close)
    mid = c.rolling(period).mean()
    std = c.rolling(period).std()
    return (mid - std_dev * std).values

class BB_MR(Strategy):
    bb_period = 20
    std_dev = 2.0
    stop_loss_pct = 8

    def init(self):
        self.upper = self.I(bb_upper, self.data.Close, self.bb_period, self.std_dev)
        self.middle = self.I(bb_middle, self.data.Close, self.bb_period)
        self.lower = self.I(bb_lower, self.data.Close, self.bb_period, self.std_dev)

    def next(self):
        if not self.position and self.data.Close[-1] < self.lower[-1]:
            sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
            self.buy(sl=sl)
        elif self.position and self.data.Close[-1] > self.middle[-1]:
            self.position.close()
