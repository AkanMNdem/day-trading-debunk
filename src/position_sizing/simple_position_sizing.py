"""
Simple position sizing strategies for trading systems.

Clean implementations of key position sizing methods including
Kelly criterion and fixed sizing approaches.
"""

import numpy as np
from typing import Dict, Any, Optional


class FixedPositionSizer:
    """Fixed percentage position sizing."""
    
    def __init__(self, percent: float = 0.1):
        """Initialize with fixed percentage of capital per trade.
        
        Args:
            percent: Fraction of capital to risk per trade (e.g., 0.1 = 10%)
        """
        self.percent = max(0.01, min(percent, 1.0))  # Clamp between 1% and 100%
        self.name = f"Fixed-{self.percent:.0%}"
    
    def calculate_size(self, capital: float, price: float, signal: int) -> float:
        """Calculate position size as fixed percentage of capital.
        
        Args:
            capital: Available capital
            price: Current asset price
            signal: Trade signal (1=buy, -1=sell, 0=hold)
            
        Returns:
            Number of shares to trade
        """
        if signal == 0 or price <= 0:
            return 0.0
        
        trade_value = capital * self.percent
        return trade_value / price


class KellyPositionSizer:
    """Kelly criterion position sizing.
    
    Uses the Kelly formula: f = (bp - q) / b
    Where: f = fraction to bet, b = odds, p = win probability, q = loss probability
    """
    
    def __init__(self, win_rate: float = 0.55, win_loss_ratio: float = 1.5, 
                 kelly_fraction: float = 0.25):
        """Initialize Kelly criterion position sizer.
        
        Args:
            win_rate: Probability of winning trades (0-1)
            win_loss_ratio: Average win / average loss ratio
            kelly_fraction: Fraction of Kelly criterion to use (0.25 = 25% Kelly)
        """
        self.win_rate = max(0.01, min(win_rate, 0.99))
        self.win_loss_ratio = max(0.1, win_loss_ratio)
        self.kelly_fraction = max(0.01, min(kelly_fraction, 1.0))
        self.name = f"Kelly-{self.kelly_fraction:.0%}"
    
    def calculate_size(self, capital: float, price: float, signal: int) -> float:
        """Calculate position size using Kelly criterion.
        
        Args:
            capital: Available capital
            price: Current asset price
            signal: Trade signal
            
        Returns:
            Number of shares to trade
        """
        if signal == 0 or price <= 0:
            return 0.0
        
        # Kelly formula: f = W - (1-W)/R
        # Where W = win rate, R = win/loss ratio
        kelly_pct = self.win_rate - ((1 - self.win_rate) / self.win_loss_ratio)
        kelly_pct = max(0.0, kelly_pct)  # Never go negative
        
        # Apply kelly fraction to reduce risk
        allocation_pct = kelly_pct * self.kelly_fraction
        allocation_pct = min(allocation_pct, 0.5)  # Cap at 50% of capital
        
        trade_value = capital * allocation_pct
        return trade_value / price


class VolatilityPositionSizer:
    """Position sizing based on price volatility."""
    
    def __init__(self, risk_per_trade: float = 0.02, volatility_lookback: int = 20):
        """Initialize volatility-based position sizer.
        
        Args:
            risk_per_trade: Maximum risk per trade as fraction of capital
            volatility_lookback: Number of periods to calculate volatility
        """
        self.risk_per_trade = max(0.005, min(risk_per_trade, 0.1))  # 0.5% to 10%
        self.volatility_lookback = max(5, volatility_lookback)
        self.name = f"Vol-{self.risk_per_trade:.1%}"
    
    def calculate_size(self, capital: float, price: float, signal: int, 
                      price_history: Optional[np.ndarray] = None) -> float:
        """Calculate position size based on volatility.
        
        Args:
            capital: Available capital
            price: Current asset price
            signal: Trade signal
            price_history: Array of recent prices for volatility calculation
            
        Returns:
            Number of shares to trade
        """
        if signal == 0 or price <= 0:
            return 0.0
        
        # Calculate volatility if price history provided
        if price_history is not None and len(price_history) >= self.volatility_lookback:
            returns = np.diff(price_history) / price_history[:-1]
            volatility = np.std(returns[-self.volatility_lookback:])
            volatility = max(0.01, volatility)  # Minimum volatility
        else:
            volatility = 0.02  # Default 2% daily volatility
        
        # Risk amount based on capital
        risk_amount = capital * self.risk_per_trade
        
        # Position size = risk amount / (price * volatility)
        # This gives smaller positions for more volatile assets
        position_value = risk_amount / volatility
        return position_value / price


def create_position_sizer(sizer_type: str = "fixed", **kwargs):
    """Factory function to create position sizers.
    
    Args:
        sizer_type: Type of sizer ("fixed", "kelly", "volatility")
        **kwargs: Arguments passed to the sizer constructor
        
    Returns:
        Position sizer object
        
    Examples:
        >>> sizer = create_position_sizer("fixed", percent=0.1)
        >>> sizer = create_position_sizer("kelly", win_rate=0.6, win_loss_ratio=2.0)
        >>> sizer = create_position_sizer("volatility", risk_per_trade=0.02)
    """
    sizers = {
        "fixed": FixedPositionSizer,
        "kelly": KellyPositionSizer,
        "volatility": VolatilityPositionSizer
    }
    
    if sizer_type not in sizers:
        raise ValueError(f"Unknown sizer type: {sizer_type}. Use: {list(sizers.keys())}")
    
    return sizers[sizer_type](**kwargs)


# Example usage for testing
if __name__ == "__main__":
    # Test different position sizers
    capital = 100000
    price = 100
    signal = 1
    
    # Fixed sizing
    fixed_sizer = FixedPositionSizer(percent=0.1)
    shares = fixed_sizer.calculate_size(capital, price, signal)
    print(f"Fixed sizer: {shares:.0f} shares (${shares*price:,.0f})")
    
    # Kelly sizing
    kelly_sizer = KellyPositionSizer(win_rate=0.6, win_loss_ratio=2.0)
    shares = kelly_sizer.calculate_size(capital, price, signal)
    print(f"Kelly sizer: {shares:.0f} shares (${shares*price:,.0f})")
    
    # Volatility sizing
    vol_sizer = VolatilityPositionSizer(risk_per_trade=0.02)
    shares = vol_sizer.calculate_size(capital, price, signal)
    print(f"Volatility sizer: {shares:.0f} shares (${shares*price:,.0f})") 