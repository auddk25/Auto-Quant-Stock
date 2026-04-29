"""EMA crossover with momentum and RSI filter."""
from backtesting import Strategy
import pandas as pd

def ema(series, period):
    return pd.Series(series).ewm(span=period, adjust=False).mean().values

def momentum(series, period=10):
    return (pd.Series(series) / pd.Series(series).shift(period) - 1).values

def rsi(series, period=14):
    delta = pd.Series(series).diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).values

class EMA_Mom_RSI(Strategy):
    fast_period = 10
    slow_period = 30
    mom_period = 10
    rsi_period = 14
    rsi_max = 70
    stop_loss_pct = 12

    def init(self):
        self.fast_ema = self.I(ema, self.data.Close, self.fast_period)
        self.slow_ema = self.I(ema, self.data.Close, self.slow_period)
        self.mom = self.I(momentum, self.data.Close, self.mom_period)
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self):
        if not self.position:
            if (self.fast_ema[-2] < self.slow_ema[-2] and
                self.fast_ema[-1] > self.slow_ema[-1] and
                self.mom[-1] > 0 and self.rsi[-1] < self.rsi_max):
                sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
                self.buy(sl=sl)
        else:
            if (self.fast_ema[-2] > self.slow_ema[-2] and
                self.fast_ema[-1] < self.slow_ema[-1]):
                self.position.close()
