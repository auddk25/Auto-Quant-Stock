"""SMA crossover with trend filter — only buy above 200-day SMA."""
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

class SMA_Trend(Strategy):
    fast_period = 10
    slow_period = 30
    trend_period = 200
    stop_loss_pct = 8

    def init(self):
        self.fast_ma = self.I(sma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(sma, self.data.Close, self.slow_period)
        self.trend_ma = self.I(sma, self.data.Close, self.trend_period)

    def next(self):
        if crossover(self.fast_ma, self.slow_ma) and self.data.Close[-1] > self.trend_ma[-1]:
            sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
            self.buy(sl=sl)
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()
