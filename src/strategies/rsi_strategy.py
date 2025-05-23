import pandas as pd
from ta.momentum import RSIIndicator
from .base import Strategy


class RSIMeanReversionStrategy(Strategy):
    """RSI Mean Reversion Strategy.
    
    Buys when RSI < oversold threshold, sells when RSI > overbought threshold.
    """
    
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        """Initialize RSI strategy.
        
        Args:
            rsi_period: Lookback period for RSI calculation
            oversold: RSI threshold for buy signals  
            overbought: RSI threshold for sell signals
        """
        super().__init__(name=f"RSI-{rsi_period}")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data):
        """Generate RSI-based trading signals.
        
        Args:
            data: DataFrame with OHLCV price data
            
        Returns:
            DataFrame with RSI values and trading signals
        """
        df = data.copy()
        
        # Handle column naming
        if 'close' in df.columns and 'Close' not in df.columns:
            df['Close'] = df['close']
        
        # Calculate RSI
        rsi = RSIIndicator(close=df['Close'], window=self.rsi_period)
        df['RSI'] = rsi.rsi()
        
        # Generate signals
        signals = pd.DataFrame(index=df.index)
        signals['RSI'] = df['RSI']
        signals['signal'] = 0
        
        # Buy when oversold, sell when overbought
        signals.loc[df['RSI'] < self.oversold, 'signal'] = 1
        signals.loc[df['RSI'] > self.overbought, 'signal'] = -1
        
        # Avoid look-ahead bias
        signals['signal'] = signals['signal'].shift(1).fillna(0)
        
        return signals
