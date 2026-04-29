"""Buy on second bar if positive — ultra-fast entry."""
from backtesting import Strategy

class Day2Buy(Strategy):
    def init(self):
        pass

    def next(self):
        if not self.position and len(self.data) >= 2:
            if self.data.Close[-1] > self.data.Close[-2]:
                self.buy()
