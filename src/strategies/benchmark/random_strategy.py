import pandas as pd
import numpy as np
from .base import Strategy

class RandomStrategy(Strategy):
    """Random trading strategy - generates random signals."""
    
    def __init__(self, signal_freq=0.1, seed=None):
        """Initialize random strategy."""
        super().__init__(name="Random")
        self.signal_freq = signal_freq
        
        # Set random seed if provided
        if seed is not None:
            np.random.seed(seed)
    
    def generate_signals(self, data, match_strategy=None):
        """Generate random trading signals."""
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        if match_strategy is not None:
            # Match the signals from the provided strategy
            matched_signals = match_strategy.generate_signals(data)
            
            # Count the number of buy and sell signals
            buy_count = (matched_signals['signal'] == 1).sum()
            sell_count = (matched_signals['signal'] == -1).sum()
            
            # Generate the same number of random signals
            if buy_count > 0:
                buy_indices = np.random.choice(
                    range(len(signals)), 
                    size=int(buy_count), 
                    replace=False
                )
                signals.iloc[buy_indices, signals.columns.get_loc('signal')] = 1
            
            if sell_count > 0:
                # Ensure we don't select indices that already have buy signals
                current_signals = np.array(signals['signal'].values)
                available_indices = np.where(current_signals == 0)[0]
                
                if len(available_indices) >= sell_count:
                    sell_indices = np.random.choice(
                        available_indices, 
                        size=int(sell_count), 
                        replace=False
                    )
                    signals.iloc[sell_indices, signals.columns.get_loc('signal')] = -1
        else:
            # Generate random signals based on frequency
            random_values = np.random.random(len(signals))
            signals.loc[random_values < self.signal_freq/2, 'signal'] = 1
            signals.loc[(random_values >= self.signal_freq/2) & 
                        (random_values < self.signal_freq), 'signal'] = -1
        
        return signals