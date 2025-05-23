import pandas as pd
import numpy as np
from .base import Strategy


class RandomStrategy(Strategy):
    """Random trading strategy for statistical comparison."""
    
    def __init__(self, signal_freq=0.1, seed=42):
        """Initialize random strategy.
        
        Args:
            signal_freq: Probability of generating a signal per period
            seed: Random seed for reproducible results
        """
        super().__init__(name="Random")
        self.signal_freq = signal_freq
        self.seed = seed
    
    def generate_signals(self, data):
        """Generate random trading signals."""
        np.random.seed(self.seed)  # Ensure reproducible results
        
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # Generate random signals based on frequency
        random_values = np.random.random(len(signals))
        signals.loc[random_values < self.signal_freq/2, 'signal'] = 1  # Buy
        signals.loc[(random_values >= self.signal_freq/2) & 
                   (random_values < self.signal_freq), 'signal'] = -1  # Sell
        
        return signals