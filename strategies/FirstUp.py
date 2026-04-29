"""Buy on first positive day, never sell — ultra-fast entry."""
from backtesting import Strategy

class FirstUp(Strategy):
    def init(self):
        pass

    def next(self):
        if not self.position and len(self.data) >= 2:
            if self.data.Close[-1] > self.data.Open[-1]:
                self.buy()
