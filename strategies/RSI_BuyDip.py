"""RSI mean-reversion — buy dips, sell rallies."""
from backtesting import Strategy
import pandas as pd

def rsi(series, period=14):
    delta = pd.Series(series).diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).values

class RSI_BuyDip(Strategy):
    rsi_period = 14
    buy_threshold = 30
    sell_threshold = 70

    def init(self):
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self):
        if not self.position and self.rsi[-1] < self.buy_threshold:
            self.buy()
        elif self.position and self.rsi[-1] > self.sell_threshold:
            self.position.close()
