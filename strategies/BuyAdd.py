"""Buy immediately, add on momentum — maximize time in market."""
from backtesting import Strategy
import pandas as pd

def ema(series, period):
    return pd.Series(series).ewm(span=period, adjust=False).mean().values

def momentum(series, period=10):
    return (pd.Series(series) / pd.Series(series).shift(period) - 1).values

class BuyAdd(Strategy):
    fast_period = 10
    slow_period = 30
    mom_period = 10

    def init(self):
        self.fast_ema = self.I(ema, self.data.Close, self.fast_period)
        self.slow_ema = self.I(ema, self.data.Close, self.slow_period)
        self.mom = self.I(momentum, self.data.Close, self.mom_period)

    def next(self):
        if not self.position:
            # Buy on first bar
            self.buy()
        elif (self.fast_ema[-2] < self.slow_ema[-2] and
              self.fast_ema[-1] > self.slow_ema[-1] and
              self.mom[-1] > 0):
            # Add on golden cross with momentum
            self.buy()
