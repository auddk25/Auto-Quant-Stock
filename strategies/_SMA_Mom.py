"""SMA crossover with momentum filter — confirm trend direction."""
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

def momentum(series, period=10):
    return (pd.Series(series) / pd.Series(series).shift(period) - 1).values

class SMA_Mom(Strategy):
    fast_period = 10
    slow_period = 30
    mom_period = 10
    stop_loss_pct = 12

    def init(self):
        self.fast_ma = self.I(sma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(sma, self.data.Close, self.slow_period)
        self.mom = self.I(momentum, self.data.Close, self.mom_period)

    def next(self):
        if crossover(self.fast_ma, self.slow_ma) and self.mom[-1] > 0:
            sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
            self.buy(sl=sl)
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()
