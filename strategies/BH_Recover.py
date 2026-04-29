"""Buy-and-hold with crash recovery — stop out, re-enter on recovery."""
from backtesting import Strategy
import pandas as pd

def sma(series, period):
    return pd.Series(series).rolling(period).mean().values

class BH_Recover(Strategy):
    stop_loss_pct = 20
    recovery_period = 50  # re-enter when price > 50-day SMA

    def init(self):
        self.recovery_sma = self.I(sma, self.data.Close, self.recovery_period)

    def next(self):
        if not self.position:
            # Buy on first bar, or when price recovers above SMA
            if len(self.data) <= 1 or self.data.Close[-1] > self.recovery_sma[-1]:
                sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
                self.buy(sl=sl)
