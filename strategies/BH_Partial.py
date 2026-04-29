"""Partial buy-and-hold — 50% immediate, 50% on momentum confirmation."""
from backtesting import Strategy
import pandas as pd

def ema(series, period):
    return pd.Series(series).ewm(span=period, adjust=False).mean().values

def momentum(series, period=10):
    return (pd.Series(series) / pd.Series(series).shift(period) - 1).values

class BH_Partial(Strategy):
    fast_period = 10
    slow_period = 30
    mom_period = 10
    initial_size = 0.5

    def init(self):
        self.fast_ema = self.I(ema, self.data.Close, self.fast_period)
        self.slow_ema = self.I(ema, self.data.Close, self.slow_period)
        self.mom = self.I(momentum, self.data.Close, self.mom_period)

    def next(self):
        if not self.position:
            # Buy 50% on first bar
            self.buy(size=self.initial_size)
        elif (self.fast_ema[-2] < self.slow_ema[-2] and
              self.fast_ema[-1] > self.slow_ema[-1] and
              self.mom[-1] > 0 and
              self.position.size < 1.0):
            # Add remaining 50% on golden cross with momentum
            self.buy(size=1.0 - self.position.size)
