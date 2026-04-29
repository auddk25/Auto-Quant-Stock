"""A deliberately bad strategy for testing discard flow."""
from backtesting import Strategy

class BadStrategy(Strategy):
    def init(self):
        pass

    def next(self):
        if not self.position:
            self.buy()
