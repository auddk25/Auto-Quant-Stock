"""Buy-hold with 10% stop, re-buy immediately after stop-out."""
from backtesting import Strategy

class BH_QuickRe(Strategy):
    stop_loss_pct = 10

    def init(self):
        pass

    def next(self):
        sl = self.data.Close[-1] * (1 - self.stop_loss_pct / 100)
        self.buy(sl=sl)
