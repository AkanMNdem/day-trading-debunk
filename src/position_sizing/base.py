"""Base position sizing class."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PositionSizer(ABC):
    """Abstract base class for position sizing strategies."""
    
    def __init__(self, name: str = "BaseSizer"):
        """
        Initialize the position sizer.
        
        Parameters:
        -----------
        name : str
            Name of the position sizer
        """
        self.name = name
    
    @abstractmethod
    def calculate_position_size(self, capital: float, price: float, 
                               signal: int, **kwargs) -> float:
        """
        Calculate the position size.
        
        Parameters:
        -----------
        capital : float
            Available capital
        price : float
            Current asset price
        signal : int
            Signal direction (1 for long, -1 for short, 0 for no position)
        **kwargs
            Additional keyword arguments for specific sizers
            
        Returns:
        --------
        float
            Number of units/shares to trade
        """
        pass
    
    def __str__(self) -> str:
        """Return string representation of the position sizer."""
        return self.name 