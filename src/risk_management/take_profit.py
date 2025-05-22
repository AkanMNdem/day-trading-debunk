"""Take profit implementation."""
from typing import Dict, Any, Optional, Union, Tuple
from enum import Enum


class TakeProfitType(Enum):
    """Types of take profit."""
    PERCENT = "percent"
    FIXED = "fixed"
    RISK_REWARD = "risk_reward"


class TakeProfit:
    """
    Take profit implementation for risk management.
    
    A take profit is triggered when the price moves in favor of the position
    by a certain amount, locking in profits.
    """
    
    def __init__(self, tp_type: Union[TakeProfitType, str] = TakeProfitType.PERCENT,
                value: float = 0.05, risk_reward_ratio: float = 2.0):
        """
        Initialize the take profit.
        
        Parameters:
        -----------
        tp_type : TakeProfitType or str
            Type of take profit (percent, fixed, risk_reward)
        value : float
            Value for the take profit:
            - For percent: 0.05 = 5% above entry price for long positions
            - For fixed: absolute price movement
            - For risk_reward: ignored (uses risk_reward_ratio instead)
        risk_reward_ratio : float
            Risk to reward ratio when using risk_reward type
            (e.g., 2.0 means take profit is 2x the distance of stop loss)
        """
        # Convert string to enum if needed
        if isinstance(tp_type, str):
            try:
                tp_type = TakeProfitType(tp_type.lower())
            except ValueError:
                raise ValueError(f"Invalid take profit type: {tp_type}. "
                                f"Must be one of {[t.value for t in TakeProfitType]}")
        
        self.tp_type = tp_type
        self.value = value
        self.risk_reward_ratio = risk_reward_ratio
    
    def calculate_take_profit_price(self, entry_price: float, position_type: int,
                                  stop_loss_price: Optional[float] = None) -> float:
        """
        Calculate the take profit price.
        
        Parameters:
        -----------
        entry_price : float
            Entry price of the position
        position_type : int
            Position type (1 for long, -1 for short)
        stop_loss_price : float, optional
            Stop loss price (required for risk_reward type)
            
        Returns:
        --------
        float
            Take profit price
        """
        if position_type == 0:
            return 0.0
        
        if self.tp_type == TakeProfitType.PERCENT:
            # For long positions, take profit is above entry price
            # For short positions, take profit is below entry price
            if position_type == 1:  # Long
                return entry_price * (1 + self.value)
            else:  # Short
                return entry_price * (1 - self.value)
                
        elif self.tp_type == TakeProfitType.FIXED:
            # For long positions, take profit is above entry price
            # For short positions, take profit is below entry price
            if position_type == 1:  # Long
                return entry_price + self.value
            else:  # Short
                return entry_price - self.value
                
        elif self.tp_type == TakeProfitType.RISK_REWARD:
            # Take profit is based on risk-reward ratio from stop loss
            if stop_loss_price is None:
                # Fall back to percent-based if stop loss not available
                return self.calculate_take_profit_price(entry_price, position_type)
            
            # Calculate the risk (distance from entry to stop)
            risk = abs(entry_price - stop_loss_price)
            
            # Calculate take profit as risk * risk_reward_ratio
            if position_type == 1:  # Long
                return entry_price + (risk * self.risk_reward_ratio)
            else:  # Short
                return entry_price - (risk * self.risk_reward_ratio)
        
        # Default fallback
        return entry_price * (1 + self.value * position_type)
    
    def is_triggered(self, take_profit_price: float, current_price: float, 
                    position_type: int) -> bool:
        """
        Check if the take profit is triggered.
        
        Parameters:
        -----------
        take_profit_price : float
            Take profit price
        current_price : float
            Current market price
        position_type : int
            Position type (1 for long, -1 for short)
            
        Returns:
        --------
        bool
            True if the take profit is triggered, False otherwise
        """
        if position_type == 0:
            return False
            
        if position_type == 1:  # Long
            # For long positions, take profit is triggered when price rises above take profit price
            return current_price >= take_profit_price
        else:  # Short
            # For short positions, take profit is triggered when price falls below take profit price
            return current_price <= take_profit_price 