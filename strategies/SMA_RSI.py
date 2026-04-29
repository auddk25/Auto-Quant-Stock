"""SMA crossover with RSI filter — avoid buying in overbought conditions."""
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

def rsi(series, period=14):
    delta = pd.Series(series).diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).values

class SMA_RSI(Strategy):
    fast_period = 10
    slow_period = 30
    rsi_period = 14
    rsi_buy_threshold = 70

    def init(self):
        self.fast_ma = self.I(sma, self.data.Close, self.fast_period)
        self.slow_ma = self.I(sma, self.data.Close, self.slow_period)
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self):
        if crossover(self.fast_ma, self.slow_ma) and self.rsi[-1] < self.rsi_buy_threshold:
            self.buy()
        elif crossover(self.slow_ma, self.fast_ma):
            self.position.close()
