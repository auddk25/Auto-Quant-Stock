"""Fast momentum entry, never exit — minimize entry lag."""
from backtesting import Strategy
import pandas as pd

def momentum(series, period=3):
    return (pd.Series(series) / pd.Series(series).shift(period) - 1).values

class FastEntry(Strategy):
    mom_period = 3
    mom_threshold = 0.02  # 2% gain in 3 days

    def init(self):
        self.mom = self.I(momentum, self.data.Close, self.mom_period)

    def next(self):
        if not self.position and self.mom[-1] > self.mom_threshold:
            self.buy()
