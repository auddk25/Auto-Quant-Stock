"""Buy-and-hold with 30% stop-loss — crash protection only."""
from backtesting import Strategy

class BH_Stop(Strategy):
    stop_loss_pct = 30

    def init(self):
        pass

    def next(self):
        if not self.position:
            sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
            self.buy(sl=sl)
