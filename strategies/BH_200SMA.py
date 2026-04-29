"""Buy-and-hold with 200-day SMA filter — avoid bear markets."""
from backtesting import Strategy
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

class BH_200SMA(Strategy):
    sma_period = 200

    def init(self):
        self.sma200 = self.I(sma, self.data.Close, self.sma_period)

    def next(self):
        if not self.position:
            # Buy when price is above 200-day SMA
            if len(self.data) >= self.sma_period and self.data.Close[-1] > self.sma200[-1]:
                self.buy()
        else:
            # Sell when price drops below 200-day SMA
            if self.data.Close[-1] < self.sma200[-1]:
                self.position.close()
