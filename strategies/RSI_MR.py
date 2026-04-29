"""RSI mean-reversion — buy oversold, sell overbought."""
from backtesting import Strategy
import pandas as pd

def rsi(series, period=14):
    delta = pd.Series(series).diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).values

class RSI_MR(Strategy):
    rsi_period = 14
    buy_threshold = 30
    sell_threshold = 70
    stop_loss_pct = 8

    def init(self):
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self):
        if not self.position and self.rsi[-1] < self.buy_threshold:
            sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
            self.buy(sl=sl)
        elif self.position and self.rsi[-1] > self.sell_threshold:
            self.position.close()
