import pandas as pd
from ta.momentum import RSIIndicator
from .base import Strategy

class RSIMeanReversionStrategy(Strategy):
    """RSI mean reversion strategy - buy oversold, sell overbought."""
    
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        """Initialize RSI mean reversion strategy."""
        super().__init__(name=f"RSI-{rsi_period}")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data):
        """Generate RSI-based trading signals."""
        # Make a copy of data to avoid modifying original
        df = data.copy()
        
        # Ensure we have the right column names
        if 'close' in df.columns and 'Close' not in df.columns:
            df['Close'] = df['close']
        
        # Calculate RSI
        rsi = RSIIndicator(
            close=df['Close'], 
            window=self.rsi_period
        )
        df['RSI'] = rsi.rsi()
        
        # Initialize signals DataFrame
        signals = pd.DataFrame(index=df.index)
        signals['RSI'] = df['RSI']
        signals['signal'] = 0  # Default signal: do nothing
        
        # Buy signal: RSI crosses below oversold level
        signals.loc[df['RSI'] < self.oversold, 'signal'] = 1
        
        # Sell signal: RSI crosses above overbought level
        signals.loc[df['RSI'] > self.overbought, 'signal'] = -1
        
        # Shift signals by 1 period to avoid look-ahead bias
        signals['signal'] = signals['signal'].shift(1).fillna(0)
        
        return signals
