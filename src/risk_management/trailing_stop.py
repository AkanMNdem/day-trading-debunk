"""Trailing stop implementation."""
from typing import Dict, Any, Optional, Union, Tuple
from enum import Enum


class TrailingStopType(Enum):
    """Types of trailing stop."""
    PERCENT = "percent"
    FIXED = "fixed"
    ATR = "atr"


class TrailingStop:
    """
    Trailing stop implementation for risk management.
    
    A trailing stop follows the price as it moves in favor of the position,
    but stays fixed when price moves against the position. This helps lock in
    profits while still allowing for upside potential.
    """
    
    def __init__(self, stop_type: Union[TrailingStopType, str] = TrailingStopType.PERCENT,
                value: float = 0.02, activation_percent: float = 0.01,
                atr_multiplier: float = 2.0):
        """
        Initialize the trailing stop.
        
        Parameters:
        -----------
        stop_type : TrailingStopType or str
            Type of trailing stop (percent, fixed, atr)
        value : float
            Value for the trailing stop:
            - For percent: 0.02 = 2% below highest price
            - For fixed: absolute price movement
            - For ATR: multiplier for the ATR value
        activation_percent : float
            Percentage move in favor of position required to activate trailing stop
            (0.01 = 1% move from entry price)
        atr_multiplier : float
            Multiplier for ATR when using ATR-based stops
        """
        # Convert string to enum if needed
        if isinstance(stop_type, str):
            try:
                stop_type = TrailingStopType(stop_type.lower())
            except ValueError:
                raise ValueError(f"Invalid trailing stop type: {stop_type}. "
                                f"Must be one of {[t.value for t in TrailingStopType]}")
        
        self.stop_type = stop_type
        self.value = value
        self.activation_percent = activation_percent
        self.atr_multiplier = atr_multiplier
        
        # State variables
        self.is_active = False
        self.highest_price = 0.0
        self.lowest_price = float('inf')
        self.current_stop_price = 0.0
    
    def reset(self):
        """Reset the trailing stop state."""
        self.is_active = False
        self.highest_price = 0.0
        self.lowest_price = float('inf')
        self.current_stop_price = 0.0
    
    def update(self, entry_price: float, current_price: float, position_type: int,
              data: Optional[Dict[str, Any]] = None) -> float:
        """
        Update the trailing stop based on the current price.
        
        Parameters:
        -----------
        entry_price : float
            Entry price of the position
        current_price : float
            Current market price
        position_type : int
            Position type (1 for long, -1 for short)
        data : dict, optional
            Additional data for stop calculation (ATR, etc.)
            
        Returns:
        --------
        float
            Current trailing stop price
        """
        if position_type == 0:
            self.reset()
            return 0.0
        
        # Check if trailing stop should be activated
        activation_threshold = entry_price * (1 + self.activation_percent * position_type)
        
        if position_type == 1:  # Long position
            # Check if price has moved enough to activate trailing stop
            if not self.is_active:
                if current_price >= activation_threshold:
                    self.is_active = True
                    self.highest_price = current_price
                    self.current_stop_price = self._calculate_stop_price(current_price, position_type, data)
                else:
                    # Not activated yet, use initial stop based on entry price
                    self.current_stop_price = self._calculate_stop_price(entry_price, position_type, data)
            else:
                # Already active, update highest price and recalculate stop if necessary
                if current_price > self.highest_price:
                    self.highest_price = current_price
                    new_stop = self._calculate_stop_price(current_price, position_type, data)
                    # Only update stop if it's higher than the current stop
                    if new_stop > self.current_stop_price:
                        self.current_stop_price = new_stop
        
        else:  # Short position
            # Check if price has moved enough to activate trailing stop
            if not self.is_active:
                if current_price <= activation_threshold:
                    self.is_active = True
                    self.lowest_price = current_price
                    self.current_stop_price = self._calculate_stop_price(current_price, position_type, data)
                else:
                    # Not activated yet, use initial stop based on entry price
                    self.current_stop_price = self._calculate_stop_price(entry_price, position_type, data)
            else:
                # Already active, update lowest price and recalculate stop if necessary
                if current_price < self.lowest_price:
                    self.lowest_price = current_price
                    new_stop = self._calculate_stop_price(current_price, position_type, data)
                    # Only update stop if it's lower than the current stop
                    if new_stop < self.current_stop_price:
                        self.current_stop_price = new_stop
        
        return self.current_stop_price
    
    def _calculate_stop_price(self, reference_price: float, position_type: int,
                             data: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate the stop price based on the reference price.
        
        Parameters:
        -----------
        reference_price : float
            Reference price (highest/lowest since activation)
        position_type : int
            Position type (1 for long, -1 for short)
        data : dict, optional
            Additional data for stop calculation (ATR, etc.)
            
        Returns:
        --------
        float
            Stop price
        """
        if self.stop_type == TrailingStopType.PERCENT:
            # For long positions, stop is below reference price
            # For short positions, stop is above reference price
            if position_type == 1:  # Long
                return reference_price * (1 - self.value)
            else:  # Short
                return reference_price * (1 + self.value)
                
        elif self.stop_type == TrailingStopType.FIXED:
            # For long positions, stop is below reference price
            # For short positions, stop is above reference price
            if position_type == 1:  # Long
                return reference_price - self.value
            else:  # Short
                return reference_price + self.value
                
        elif self.stop_type == TrailingStopType.ATR:
            # Use Average True Range for dynamic stop
            atr = data.get('atr', 0.0) if data else 0.0
            
            if atr == 0.0:
                # Fall back to percent-based if ATR not available
                return self._calculate_stop_price(reference_price, position_type)
            
            if position_type == 1:  # Long
                return reference_price - (atr * self.atr_multiplier)
            else:  # Short
                return reference_price + (atr * self.atr_multiplier)
        
        # Default fallback
        return reference_price * (1 - self.value * position_type)
    
    def is_triggered(self, current_price: float, position_type: int) -> bool:
        """
        Check if the trailing stop is triggered.
        
        Parameters:
        -----------
        current_price : float
            Current market price
        position_type : int
            Position type (1 for long, -1 for short)
            
        Returns:
        --------
        bool
            True if the trailing stop is triggered, False otherwise
        """
        if position_type == 0 or not self.is_active:
            return False
            
        if position_type == 1:  # Long
            # For long positions, stop is triggered when price falls below stop price
            return current_price <= self.current_stop_price
        else:  # Short
            # For short positions, stop is triggered when price rises above stop price
            return current_price >= self.current_stop_price 