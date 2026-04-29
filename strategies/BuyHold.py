"""Buy-and-hold baseline — buy on first bar, hold forever."""
from backtesting import Strategy

class BuyHold(Strategy):
    def init(self):
        pass

    def next(self):
        if not self.position:
            self.buy()
