"""Fixed percentage position sizing strategy."""
from typing import Dict, Any, Optional
from .base import PositionSizer


class FixedPercentSizer(PositionSizer):
    """
    Position sizer that allocates a fixed percentage of capital to each trade.
    """
    
    def __init__(self, percent: float = 0.02):
        """
        Initialize the fixed percentage position sizer.
        
        Parameters:
        -----------
        percent : float
            Percentage of capital to allocate (0.02 = 2%)
        """
        super().__init__(name=f"FixedPercent-{percent*100:.0f}%")
        
        # Validate percentage is within reasonable bounds
        if percent <= 0 or percent > 1:
            raise ValueError("Percentage must be between 0 and 1")
            
        self.percent = percent
    
    def calculate_position_size(self, capital: float, price: float, 
                               signal: int, **kwargs) -> float:
        """
        Calculate position size based on a fixed percentage of capital.
        
        Parameters:
        -----------
        capital : float
            Available capital
        price : float
            Current asset price
        signal : int
            Signal direction (1 for long, -1 for short, 0 for no position)
        **kwargs
            Additional keyword arguments (ignored for this sizer)
            
        Returns:
        --------
        float
            Number of units/shares to trade
        """
        if signal == 0 or price <= 0:
            return 0.0
            
        # Calculate dollar amount to allocate
        dollar_amount = capital * self.percent
        
        # Calculate units
        units = dollar_amount / price
        
        return units 