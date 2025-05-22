"""Stop loss implementation."""
from typing import Dict, Any, Optional, Union, Tuple
from enum import Enum


class StopLossType(Enum):
    """Types of stop loss."""
    PERCENT = "percent"
    FIXED = "fixed"
    ATR = "atr"
    VOLATILITY = "volatility"


class StopLoss:
    """
    Stop loss implementation for risk management.
    
    A stop loss is triggered when the price moves against the position
    by a certain amount, limiting the potential loss.
    """
    
    def __init__(self, stop_type: Union[StopLossType, str] = StopLossType.PERCENT,
                value: float = 0.02, atr_multiplier: float = 2.0):
        """
        Initialize the stop loss.
        
        Parameters:
        -----------
        stop_type : StopLossType or str
            Type of stop loss (percent, fixed, atr, volatility)
        value : float
            Value for the stop loss:
            - For percent: 0.02 = 2% below entry price
            - For fixed: absolute price movement
            - For ATR: multiplier for the ATR value
            - For volatility: multiplier for standard deviation
        atr_multiplier : float
            Multiplier for ATR when using ATR-based stops
        """
        # Convert string to enum if needed
        if isinstance(stop_type, str):
            try:
                stop_type = StopLossType(stop_type.lower())
            except ValueError:
                raise ValueError(f"Invalid stop loss type: {stop_type}. "
                                f"Must be one of {[t.value for t in StopLossType]}")
        
        self.stop_type = stop_type
        self.value = value
        self.atr_multiplier = atr_multiplier
    
    def calculate_stop_price(self, entry_price: float, position_type: int,
                            data: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate the stop loss price.
        
        Parameters:
        -----------
        entry_price : float
            Entry price of the position
        position_type : int
            Position type (1 for long, -1 for short)
        data : dict, optional
            Additional data for stop calculation (ATR, volatility, etc.)
            
        Returns:
        --------
        float
            Stop loss price
        """
        if position_type == 0:
            return 0.0
        
        if self.stop_type == StopLossType.PERCENT:
            # For long positions, stop is below entry price
            # For short positions, stop is above entry price
            if position_type == 1:  # Long
                return entry_price * (1 - self.value)
            else:  # Short
                return entry_price * (1 + self.value)
                
        elif self.stop_type == StopLossType.FIXED:
            # For long positions, stop is below entry price
            # For short positions, stop is above entry price
            if position_type == 1:  # Long
                return entry_price - self.value
            else:  # Short
                return entry_price + self.value
                
        elif self.stop_type == StopLossType.ATR:
            # Use Average True Range for dynamic stop loss
            atr = data.get('atr', 0.0) if data else 0.0
            
            if atr == 0.0:
                # Fall back to percent-based if ATR not available
                return self.calculate_stop_price(entry_price, position_type)
            
            if position_type == 1:  # Long
                return entry_price - (atr * self.atr_multiplier)
            else:  # Short
                return entry_price + (atr * self.atr_multiplier)
                
        elif self.stop_type == StopLossType.VOLATILITY:
            # Use price volatility (standard deviation) for dynamic stop loss
            volatility = data.get('volatility', 0.0) if data else 0.0
            
            if volatility == 0.0:
                # Fall back to percent-based if volatility not available
                return self.calculate_stop_price(entry_price, position_type)
            
            if position_type == 1:  # Long
                return entry_price - (volatility * self.value)
            else:  # Short
                return entry_price + (volatility * self.value)
        
        # Default fallback
        return entry_price * (1 - self.value * position_type)
    
    def is_triggered(self, stop_price: float, current_price: float, 
                    position_type: int) -> bool:
        """
        Check if the stop loss is triggered.
        
        Parameters:
        -----------
        stop_price : float
            Stop loss price
        current_price : float
            Current market price
        position_type : int
            Position type (1 for long, -1 for short)
            
        Returns:
        --------
        bool
            True if the stop loss is triggered, False otherwise
        """
        if position_type == 0:
            return False
            
        if position_type == 1:  # Long
            # For long positions, stop is triggered when price falls below stop price
            return current_price <= stop_price
        else:  # Short
            # For short positions, stop is triggered when price rises above stop price
            return current_price >= stop_price 