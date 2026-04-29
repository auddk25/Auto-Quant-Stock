"""50% buy-hold + 50% on trend confirmation — never sell."""
from backtesting import Strategy
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

class BH_50_50(Strategy):
    sma_period = 10
    initial_size = 0.5

    def init(self):
        self.sma10 = self.I(sma, self.data.Close, self.sma_period)

    def next(self):
        if not self.position:
            self.buy(size=self.initial_size)
        elif (self.position.size < 1.0 and
              self.data.Close[-1] > self.sma10[-1]):
            self.buy(size=1.0 - self.position.size)
