import pandas as pd
# import numpy as np
from .base import Strategy

class VWAPBounceStrategy(Strategy):
    """VWAP bounce strategy - buy when price bounces off VWAP."""
    
    def __init__(self, vwap_period=30, threshold=0.005):
        """Initialize VWAP bounce strategy."""
        super().__init__(name=f"VWAP-{vwap_period}")
        self.vwap_period = vwap_period
        self.threshold = threshold
    
    def generate_signals(self, data):
        """Generate VWAP bounce signals."""
        df = data.copy()
        
        # Ensure we have the right column names
        if 'close' in df.columns and 'Close' not in df.columns:
            df['Close'] = df['close']
        if 'high' in df.columns and 'High' not in df.columns:
            df['High'] = df['high']
        if 'low' in df.columns and 'Low' not in df.columns:
            df['Low'] = df['low']
        if 'volume' in df.columns and 'Volume' not in df.columns:
            df['Volume'] = df['volume']
        
        # Check if VWAP is already in the data (from Alpaca)
        if 'vwap' in df.columns:
            df['VWAP'] = df['vwap']
        else:
            # Calculate VWAP
            df['VWAP'] = self._calculate_vwap(df, self.vwap_period)
        
        # Calculate distance from VWAP
        df['vwap_dist'] = (df['Close'] - df['VWAP']) / df['VWAP']
        
        # Initialize signals DataFrame
        signals = pd.DataFrame(index=df.index)
        signals['VWAP'] = df['VWAP']
        signals['vwap_dist'] = df['vwap_dist']
        signals['signal'] = 0
        
        # Buy signal: price bounces up from below VWAP
        signals.loc[(df['vwap_dist'] < -self.threshold) & 
                   (df['vwap_dist'].shift(1) < -self.threshold) &
                   (df['Close'] > df['Close'].shift(1)), 'signal'] = 1
        
        # Sell signal: price bounces down from above VWAP
        signals.loc[(df['vwap_dist'] > self.threshold) & 
                   (df['vwap_dist'].shift(1) > self.threshold) &
                   (df['Close'] < df['Close'].shift(1)), 'signal'] = -1
        
        # Shift signals to avoid look-ahead bias
        signals['signal'] = signals['signal'].shift(1).fillna(0)
        
        return signals
    
    def _calculate_vwap(self, df, period):
        """Calculate VWAP for the specified period."""
        # Calculate typical price
        df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
        
        # Calculate price * volume
        df['price_volume'] = df['typical_price'] * df['Volume']
        
        # Calculate cumulative price * volume and cumulative volume
        df['cum_price_volume'] = df['price_volume'].rolling(window=period).sum()
        df['cum_volume'] = df['Volume'].rolling(window=period).sum()
        
        # Calculate VWAP
        vwap = df['cum_price_volume'] / df['cum_volume']
        
        return vwap