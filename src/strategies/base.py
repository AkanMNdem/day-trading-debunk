import pandas as pd
import numpy as np
import ta

class Strategy:
    """Base class for all trading strategies."""
    
    def __init__(self, name="BaseStrategy"):
        """Initialize the strategy."""
        self.name = name
    
    def generate_signals(self, data):
        """
        Generate trading signals from data.
        
        Parameters:
        -----------
        data : pd.DataFrame
            OHLCV data with datetime index
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with signal column (1=buy, -1=sell, 0=hold)
        """
        # Base class doesn't generate any signals
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        return signals
    
    def __str__(self):
        return self.name