"""SMA crossover with volume filter — confirm trend with volume."""
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

class SMA_Vol(Strategy):
    fast_period = 10
    slow_period = 30
    vol_period = 20
    vol_mult = 1.0  # volume must be > avg * mult
    stop_loss_pct = 8

    def init(self):
        self.fast_ma = self.I(sma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(sma, self.data.Close, self.slow_period)
        self.vol_avg = self.I(sma, self.data.Volume, self.vol_period)

    def next(self):
        if crossover(self.fast_ma, self.slow_ma) and self.data.Volume[-1] > self.vol_avg[-1] * self.vol_mult:
            sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
            self.buy(sl=sl)
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()
