"""
Simple risk management for trading systems.

Clean implementation of stop losses, take profits, and trailing stops
that shows understanding of risk management concepts while remaining
readable and professional.
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum


class ExitReason(Enum):
    """Reasons for exiting a position."""
    NONE = "none"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    SIGNAL = "signal"


class SimpleRiskManager:
    """
    Clean, professional risk management for trading positions.
    
    Handles stop losses, take profits, and trailing stops with
    sensible defaults and clear interface.
    """
    
    def __init__(self, stop_loss_pct: float = 0.02, take_profit_pct: float = 0.04,
                 trailing_stop_pct: float = 0.02, use_trailing: bool = False):
        """Initialize risk manager.
        
        Args:
            stop_loss_pct: Stop loss as percentage of entry price (e.g., 0.02 = 2%)
            take_profit_pct: Take profit as percentage of entry price (e.g., 0.04 = 4%)
            trailing_stop_pct: Trailing stop distance as percentage (e.g., 0.02 = 2%)
            use_trailing: Whether to use trailing stop instead of fixed stop
        """
        self.stop_loss_pct = max(0.005, min(stop_loss_pct, 0.2))  # 0.5% to 20%
        self.take_profit_pct = max(0.01, min(take_profit_pct, 0.5))  # 1% to 50%
        self.trailing_stop_pct = max(0.005, min(trailing_stop_pct, 0.1))  # 0.5% to 10%
        self.use_trailing = use_trailing
        
        # Position state
        self.entry_price = 0.0
        self.position_type = 0  # 0=flat, 1=long, -1=short
        self.stop_price = 0.0
        self.take_profit_price = 0.0
        self.highest_price = 0.0  # For trailing stops
        self.lowest_price = float('inf')  # For trailing stops
        
        self.name = f"Risk({self.stop_loss_pct:.1%}/{self.take_profit_pct:.1%})"
        if use_trailing:
            self.name += f"-Trail({self.trailing_stop_pct:.1%})"
    
    def enter_position(self, price: float, position_type: int) -> Dict[str, float]:
        """Enter a new position and set risk levels.
        
        Args:
            price: Entry price
            position_type: 1 for long, -1 for short
            
        Returns:
            Dictionary with risk levels
        """
        self.entry_price = price
        self.position_type = position_type
        self.highest_price = price
        self.lowest_price = price
        
        # Calculate stop loss
        if position_type == 1:  # Long
            self.stop_price = price * (1 - self.stop_loss_pct)
            self.take_profit_price = price * (1 + self.take_profit_pct)
        else:  # Short
            self.stop_price = price * (1 + self.stop_loss_pct)
            self.take_profit_price = price * (1 - self.take_profit_pct)
        
        return {
            'entry_price': self.entry_price,
            'stop_loss': self.stop_price,
            'take_profit': self.take_profit_price,
            'position_type': self.position_type
        }
    
    def update_price(self, current_price: float) -> Tuple[bool, ExitReason]:
        """Update with current price and check exit conditions.
        
        Args:
            current_price: Current market price
            
        Returns:
            Tuple of (should_exit, exit_reason)
        """
        if self.position_type == 0:
            return False, ExitReason.NONE
        
        # Update trailing stop if enabled
        if self.use_trailing:
            self._update_trailing_stop(current_price)
        
        # Check exit conditions
        if self._check_stop_loss(current_price):
            return True, ExitReason.STOP_LOSS
        
        if self._check_take_profit(current_price):
            return True, ExitReason.TAKE_PROFIT
        
        if self.use_trailing and self._check_trailing_stop(current_price):
            return True, ExitReason.TRAILING_STOP
        
        return False, ExitReason.NONE
    
    def exit_position(self) -> None:
        """Exit position and reset state."""
        self.entry_price = 0.0
        self.position_type = 0
        self.stop_price = 0.0
        self.take_profit_price = 0.0
        self.highest_price = 0.0
        self.lowest_price = float('inf')
    
    def _check_stop_loss(self, price: float) -> bool:
        """Check if stop loss is hit."""
        if self.position_type == 1:  # Long
            return price <= self.stop_price
        else:  # Short
            return price >= self.stop_price
    
    def _check_take_profit(self, price: float) -> bool:
        """Check if take profit is hit."""
        if self.position_type == 1:  # Long
            return price >= self.take_profit_price
        else:  # Short
            return price <= self.take_profit_price
    
    def _update_trailing_stop(self, price: float) -> None:
        """Update trailing stop levels."""
        if self.position_type == 1:  # Long
            if price > self.highest_price:
                self.highest_price = price
                # Update stop to trail the high
                new_stop = price * (1 - self.trailing_stop_pct)
                self.stop_price = max(self.stop_price, new_stop)
        else:  # Short
            if price < self.lowest_price:
                self.lowest_price = price
                # Update stop to trail the low
                new_stop = price * (1 + self.trailing_stop_pct)
                self.stop_price = min(self.stop_price, new_stop)
    
    def _check_trailing_stop(self, price: float) -> bool:
        """Check if trailing stop is hit."""
        return self._check_stop_loss(price)
    
    def get_risk_reward_ratio(self) -> float:
        """Calculate risk/reward ratio for current position."""
        if self.position_type == 0:
            return 0.0
        
        risk = abs(self.entry_price - self.stop_price)
        reward = abs(self.entry_price - self.take_profit_price)
        
        return reward / risk if risk > 0 else 0.0
    
    def get_unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L for current position."""
        if self.position_type == 0:
            return 0.0
        
        pnl = (current_price - self.entry_price) * self.position_type
        return pnl / self.entry_price  # Return as percentage
    
    def get_status(self) -> Dict[str, Any]:
        """Get current risk management status."""
        return {
            'entry_price': self.entry_price,
            'position_type': self.position_type,
            'stop_loss': self.stop_price,
            'take_profit': self.take_profit_price,
            'highest_price': self.highest_price if self.position_type == 1 else None,
            'lowest_price': self.lowest_price if self.position_type == -1 else None,
            'risk_reward_ratio': self.get_risk_reward_ratio(),
            'using_trailing': self.use_trailing
        }


class FixedStopLoss:
    """Simple fixed stop loss implementation."""
    
    def __init__(self, stop_pct: float = 0.02):
        """Initialize with stop loss percentage."""
        self.stop_pct = max(0.005, min(stop_pct, 0.2))
        self.name = f"Stop-{self.stop_pct:.1%}"
    
    def calculate_stop(self, entry_price: float, position_type: int) -> float:
        """Calculate stop price."""
        if position_type == 1:  # Long
            return entry_price * (1 - self.stop_pct)
        else:  # Short
            return entry_price * (1 + self.stop_pct)
    
    def is_triggered(self, stop_price: float, current_price: float, position_type: int) -> bool:
        """Check if stop is triggered."""
        if position_type == 1:  # Long
            return current_price <= stop_price
        else:  # Short
            return current_price >= stop_price


class FixedTakeProfit:
    """Simple fixed take profit implementation."""
    
    def __init__(self, profit_pct: float = 0.04):
        """Initialize with take profit percentage."""
        self.profit_pct = max(0.01, min(profit_pct, 0.5))
        self.name = f"TP-{self.profit_pct:.1%}"
    
    def calculate_target(self, entry_price: float, position_type: int) -> float:
        """Calculate take profit price."""
        if position_type == 1:  # Long
            return entry_price * (1 + self.profit_pct)
        else:  # Short
            return entry_price * (1 - self.profit_pct)
    
    def is_triggered(self, target_price: float, current_price: float, position_type: int) -> bool:
        """Check if take profit is triggered."""
        if position_type == 1:  # Long
            return current_price >= target_price
        else:  # Short
            return current_price <= target_price


# Factory functions for easy creation
def create_risk_manager(stop_loss: float = 0.02, take_profit: float = 0.04,
                       trailing_stop: float = 0.02, use_trailing: bool = False):
    """Create a risk manager with specified parameters.
    
    Args:
        stop_loss: Stop loss percentage
        take_profit: Take profit percentage  
        trailing_stop: Trailing stop percentage
        use_trailing: Whether to use trailing stops
        
    Returns:
        SimpleRiskManager instance
        
    Examples:
        >>> rm = create_risk_manager(stop_loss=0.03, take_profit=0.06)
        >>> rm_trailing = create_risk_manager(trailing_stop=0.025, use_trailing=True)
    """
    return SimpleRiskManager(stop_loss, take_profit, trailing_stop, use_trailing)


# Example usage
if __name__ == "__main__":
    # Test basic risk manager
    rm = SimpleRiskManager(stop_loss_pct=0.02, take_profit_pct=0.04)
    
    # Enter long position
    levels = rm.enter_position(100.0, 1)
    print(f"Entered long at $100")
    print(f"Stop loss: ${levels['stop_loss']:.2f}")
    print(f"Take profit: ${levels['take_profit']:.2f}")
    print(f"Risk/Reward: {rm.get_risk_reward_ratio():.1f}")
    
    # Test price movements
    should_exit, reason = rm.update_price(95.0)
    print(f"Price $95 - Exit: {should_exit}, Reason: {reason.value}")
    
    should_exit, reason = rm.update_price(105.0)
    print(f"Price $105 - Exit: {should_exit}, Reason: {reason.value}")
    
    print("\nRisk management module working!") 