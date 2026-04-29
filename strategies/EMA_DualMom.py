"""EMA crossover with dual momentum filter."""
from backtesting import Strategy
import pandas as pd

def ema(series, period):
    return pd.Series(series).ewm(span=period, adjust=False).mean().values

def momentum(series, period=10):
    return (pd.Series(series) / pd.Series(series).shift(period) - 1).values

class EMA_DualMom(Strategy):
    fast_period = 10
    slow_period = 30
    mom_short = 10
    mom_long = 20
    stop_loss_pct = 12

    def init(self):
        self.fast_ema = self.I(ema, self.data.Close, self.fast_period)
        self.slow_ema = self.I(ema, self.data.Close, self.slow_period)
        self.mom_s = self.I(momentum, self.data.Close, self.mom_short)
        self.mom_l = self.I(momentum, self.data.Close, self.mom_long)

    def next(self):
        if not self.position:
            if (self.fast_ema[-2] < self.slow_ema[-2] and
                self.fast_ema[-1] > self.slow_ema[-1] and
                self.mom_s[-1] > 0 and self.mom_l[-1] > 0):
                sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
                self.buy(sl=sl)
        else:
            if (self.fast_ema[-2] > self.slow_ema[-2] and
                self.fast_ema[-1] < self.slow_ema[-1]):
                self.position.close()
