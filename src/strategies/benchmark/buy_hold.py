import pandas as pd
from .base import Strategy

class BuyAndHoldStrategy(Strategy):
    """Simple buy and hold strategy."""
    
    def __init__(self):
        super().__init__(name="Buy-and-Hold")
    
    def generate_signals(self, data):
        """Generate buy-and-hold signals (buy at start, hold forever)."""
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Buy at the first opportunity
        signals.iloc[0, signals.columns.get_loc('signal')] = 1
        
        return signals