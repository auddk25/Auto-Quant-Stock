"""SMA crossover with tighter 5% stop-loss."""
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

class SMA_SL5(Strategy):
    fast_period = 10
    slow_period = 30
    stop_loss_pct = 5

    def init(self):
        self.fast_ma = self.I(sma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(sma, self.data.Close, self.slow_period)

    def next(self):
        if crossover(self.fast_ma, self.slow_ma):
            sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
            self.buy(sl=sl)
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()
