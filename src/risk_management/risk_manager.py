"""Risk manager implementation."""
from typing import Dict, Any, Optional, Union, Tuple, List
from enum import Enum

from .stop_loss import StopLoss
from .take_profit import TakeProfit
from .trailing_stop import TrailingStop


class ExitReason(Enum):
    """Reasons for exiting a position."""
    NONE = "none"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    SIGNAL = "signal"
    OTHER = "other"


class RiskManager:
    """
    Risk manager that integrates stop loss, take profit, and trailing stop.
    
    This class provides a unified interface for managing risk in a position.
    """
    
    def __init__(self, stop_loss: Optional[StopLoss] = None,
                take_profit: Optional[TakeProfit] = None,
                trailing_stop: Optional[TrailingStop] = None):
        """
        Initialize the risk manager.
        
        Parameters:
        -----------
        stop_loss : StopLoss, optional
            Stop loss configuration
        take_profit : TakeProfit, optional
            Take profit configuration
        trailing_stop : TrailingStop, optional
            Trailing stop configuration
        """
        self.stop_loss = stop_loss or StopLoss()
        self.take_profit = take_profit or TakeProfit()
        self.trailing_stop = trailing_stop or TrailingStop()
        
        # Position state
        self.entry_price = 0.0
        self.position_type = 0  # 0 = flat, 1 = long, -1 = short
        self.stop_price = 0.0
        self.take_profit_price = 0.0
        self.trailing_stop_price = 0.0
    
    def on_enter_position(self, price: float, position_type: int,
                         data: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Handle position entry and calculate risk levels.
        
        Parameters:
        -----------
        price : float
            Entry price
        position_type : int
            Position type (1 for long, -1 for short)
        data : dict, optional
            Additional data for calculations (ATR, volatility, etc.)
            
        Returns:
        --------
        dict
            Dictionary with calculated risk levels
        """
        self.entry_price = price
        self.position_type = position_type
        
        # Calculate stop loss
        self.stop_price = self.stop_loss.calculate_stop_price(price, position_type, data)
        
        # Calculate take profit
        self.take_profit_price = self.take_profit.calculate_take_profit_price(
            price, position_type, self.stop_price)
        
        # Reset and initialize trailing stop
        self.trailing_stop.reset()
        self.trailing_stop_price = self.trailing_stop.update(price, price, position_type, data)
        
        return {
            'entry_price': self.entry_price,
            'stop_loss': self.stop_price,
            'take_profit': self.take_profit_price,
            'trailing_stop': self.trailing_stop_price
        }
    
    def on_price_update(self, price: float, data: Optional[Dict[str, Any]] = None) -> Tuple[bool, ExitReason]:
        """
        Handle price updates and check if any exit conditions are met.
        
        Parameters:
        -----------
        price : float
            Current price
        data : dict, optional
            Additional data for calculations
            
        Returns:
        --------
        tuple
            (should_exit, exit_reason)
        """
        if self.position_type == 0:
            return False, ExitReason.NONE
        
        # Update trailing stop
        self.trailing_stop_price = self.trailing_stop.update(
            self.entry_price, price, self.position_type, data)
        
        # Check exit conditions
        if self.stop_loss.is_triggered(self.stop_price, price, self.position_type):
            return True, ExitReason.STOP_LOSS
        
        if self.take_profit.is_triggered(self.take_profit_price, price, self.position_type):
            return True, ExitReason.TAKE_PROFIT
        
        if self.trailing_stop.is_triggered(price, self.position_type):
            return True, ExitReason.TRAILING_STOP
        
        return False, ExitReason.NONE
    
    def on_exit_position(self) -> None:
        """Reset state when position is exited."""
        self.entry_price = 0.0
        self.position_type = 0
        self.stop_price = 0.0
        self.take_profit_price = 0.0
        self.trailing_stop.reset()
        self.trailing_stop_price = 0.0
    
    def get_risk_reward_ratio(self) -> float:
        """
        Calculate the risk-reward ratio of the current position.
        
        Returns:
        --------
        float
            Risk-reward ratio (potential reward / potential risk)
        """
        if self.position_type == 0 or self.entry_price == 0:
            return 0.0
        
        # Calculate risk and reward
        risk = abs(self.entry_price - self.stop_price)
        reward = abs(self.entry_price - self.take_profit_price)
        
        if risk == 0:
            return float('inf')
            
        return reward / risk
    
    def get_risk_percentage(self) -> float:
        """
        Calculate the risk as a percentage of entry price.
        
        Returns:
        --------
        float
            Risk percentage
        """
        if self.position_type == 0 or self.entry_price == 0:
            return 0.0
            
        risk = abs(self.entry_price - self.stop_price)
        return (risk / self.entry_price) * 100.0
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get the current status of the risk management.
        
        Returns:
        --------
        dict
            Dictionary with current risk management status
        """
        return {
            'entry_price': self.entry_price,
            'position_type': self.position_type,
            'stop_loss': self.stop_price,
            'take_profit': self.take_profit_price,
            'trailing_stop': self.trailing_stop_price,
            'risk_reward_ratio': self.get_risk_reward_ratio(),
            'risk_percentage': self.get_risk_percentage()
        } 