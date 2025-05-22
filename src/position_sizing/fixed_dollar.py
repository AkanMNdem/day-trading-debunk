"""Fixed dollar amount position sizing strategy."""
from typing import Dict, Any, Optional
from .base import PositionSizer


class FixedDollarSizer(PositionSizer):
    """
    Position sizer that allocates a fixed dollar amount to each trade.
    """
    
    def __init__(self, amount: float = 1000.0):
        """
        Initialize the fixed dollar amount position sizer.
        
        Parameters:
        -----------
        amount : float
            Dollar amount to allocate per trade
        """
        super().__init__(name=f"FixedDollar-${amount:.0f}")
        
        # Validate amount is positive
        if amount <= 0:
            raise ValueError("Dollar amount must be positive")
            
        self.amount = amount
    
    def calculate_position_size(self, capital: float, price: float, 
                               signal: int, **kwargs) -> float:
        """
        Calculate position size based on a fixed dollar amount.
        
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
            
        # Ensure we don't allocate more than available capital
        dollar_amount = min(self.amount, capital)
        
        # Calculate units
        units = dollar_amount / price
        
        return units 