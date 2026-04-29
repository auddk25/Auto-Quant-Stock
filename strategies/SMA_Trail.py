"""SMA crossover with ATR trailing stop — lock in profits."""
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

def atr(high, low, close, period=14):
    h = pd.Series(high)
    l = pd.Series(low)
    c = pd.Series(close)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean().values

class SMA_Trail(Strategy):
    fast_period = 10
    slow_period = 30
    atr_period = 14
    atr_mult = 3.0

    def init(self):
        self.fast_ma = self.I(sma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(sma, self.data.Close, self.slow_period)
        self.atr = self.I(atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)

    def next(self):
        if self.position:
            # Trail: move stop up as price rises
            new_sl = self.data.Close[-1] - self.atr[-1] * self.atr_mult
            if new_sl > self.position.sl:
                self.position.sl = new_sl

        if crossover(self.fast_ma, self.slow_ma) and not self.position:
            sl = self.data.Close[-1] - self.atr[-1] * self.atr_mult
            self.buy(sl=sl)
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()
