import pandas as pd
from ta.trend import EMAIndicator
from .base import Strategy

class EMACrossoverStrategy(Strategy):
    """EMA crossover strategy - buy when fast EMA crosses above slow EMA."""
    
    def __init__(self, fast_period=12, slow_period=26):
        """Initialize EMA crossover strategy."""
        super().__init__(name=f"EMA-{fast_period}-{slow_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data):
        """Generate EMA crossover signals."""
        df = data.copy()
        
        # Ensure we have the right column names
        if 'close' in df.columns and 'Close' not in df.columns:
            df['Close'] = df['close']
        
        # Calculate fast and slow EMAs
        df['fast_ema'] = EMAIndicator(
            close=df['Close'], 
            window=self.fast_period
        ).ema_indicator()
        
        df['fast_ema'] = EMAIndicator(
            close=df['Close'], 
            window=self.fast_period
        ).ema_indicator()
        
        # Initialize signals DataFrame
        signals = pd.DataFrame(index=df.index)
        signals['fast_ema'] = df['fast_ema']
        signals['slow_ema'] = df['slow_ema']
        signals['signal'] = 0
        
        # Generate crossover signals
        signals['ema_diff'] = signals['fast_ema'] - signals['slow_ema']
        signals['ema_diff_prev'] = signals['ema_diff'].shift(1)
        
        # Buy when fast EMA crosses above slow EMA
        signals.loc[(signals['ema_diff'] > 0) & 
                   (signals['ema_diff_prev'] < 0), 'signal'] = 1
        
        # Sell when fast EMA crosses below slow EMA
        signals.loc[(signals['ema_diff'] < 0) & 
                   (signals['ema_diff_prev'] > 0), 'signal'] = -1
        
        # Shift signals to avoid look-ahead bias
        signals['signal'] = signals['signal'].shift(1).fillna(0)
        
        return signals