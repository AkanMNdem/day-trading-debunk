"""Kelly criterion position sizing strategy."""
from typing import Dict, Any, Optional, List
import numpy as np

from .base import PositionSizer


class KellySizer(PositionSizer):
    """
    Position sizer based on the Kelly criterion formula:
    Kelly % = W - [(1 - W) / R]
    Where:
    - W is the win rate (probability of winning)
    - R is the win/loss ratio (average win / average loss)
    """
    
    def __init__(self, win_rate: float = 0.5, win_loss_ratio: float = 2.0,
                fraction: float = 0.5, lookback: int = 20):
        """
        Initialize the Kelly criterion position sizer.
        
        Parameters:
        -----------
        win_rate : float
            Expected win rate (0.0 to 1.0)
        win_loss_ratio : float
            Ratio of average win to average loss
        fraction : float
            Fraction of the Kelly criterion to use (0.0 to 1.0)
            Using full Kelly (1.0) is often too aggressive
        lookback : int
            Number of trades to consider for calculating actual win rate and ratios
        """
        super().__init__(name=f"Kelly-{fraction*100:.0f}%")
        
        # Validate inputs
        if win_rate <= 0 or win_rate >= 1:
            raise ValueError("Win rate must be between 0 and 1")
        if win_loss_ratio <= 0:
            raise ValueError("Win/loss ratio must be positive")
        if fraction <= 0 or fraction > 1:
            raise ValueError("Kelly fraction must be between 0 and 1")
        
        self.win_rate = win_rate
        self.win_loss_ratio = win_loss_ratio
        self.fraction = fraction
        self.lookback = lookback
        
        # Historical trades for dynamic calculation
        self.historical_trades: List[Dict[str, Any]] = []
    
    def calculate_position_size(self, capital: float, price: float, 
                               signal: int, **kwargs) -> float:
        """
        Calculate position size based on the Kelly criterion.
        
        Parameters:
        -----------
        capital : float
            Available capital
        price : float
            Current asset price
        signal : int
            Signal direction (1 for long, -1 for short, 0 for no position)
        **kwargs
            Additional keyword arguments:
            - 'trade_history': List of trade dictionaries with 'pnl' key
            
        Returns:
        --------
        float
            Number of units/shares to trade
        """
        if signal == 0 or price <= 0:
            return 0.0
        
        # Get trade history if provided
        trade_history = kwargs.get('trade_history', self.historical_trades)
        
        # Use dynamic win rate and ratio if we have enough historical trades
        if len(trade_history) >= self.lookback:
            win_rate, win_loss_ratio = self._calculate_from_history(trade_history)
        else:
            # Use default parameters if not enough history
            win_rate, win_loss_ratio = self.win_rate, self.win_loss_ratio
        
        # Calculate Kelly percentage
        kelly_pct = self._calculate_kelly(win_rate, win_loss_ratio)
        
        # Apply the fraction to avoid over-betting
        allocation_pct = kelly_pct * self.fraction
        
        # Cap the allocation at 100% of capital
        allocation_pct = min(allocation_pct, 1.0)
        
        # Ensure the allocation is non-negative
        allocation_pct = max(allocation_pct, 0.0)
        
        # Calculate dollar amount
        dollar_amount = capital * allocation_pct
        
        # Calculate units
        units = dollar_amount / price
        
        return units
    
    def _calculate_kelly(self, win_rate: float, win_loss_ratio: float) -> float:
        """
        Calculate the Kelly criterion percentage.
        
        Parameters:
        -----------
        win_rate : float
            Probability of winning
        win_loss_ratio : float
            Ratio of average win to average loss
            
        Returns:
        --------
        float
            Kelly percentage (between 0 and 1)
        """
        # Kelly formula: f* = W - [(1 - W) / R]
        # where f* is the optimal fraction, W is win rate, R is win/loss ratio
        kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        # Ensure the kelly value is between 0 and 1
        return max(0.0, min(kelly, 1.0))
    
    def _calculate_from_history(self, trade_history: List[Dict[str, Any]]) -> tuple:
        """
        Calculate win rate and win/loss ratio from trade history.
        
        Parameters:
        -----------
        trade_history : list
            List of trade dictionaries with 'pnl' key
            
        Returns:
        --------
        tuple
            (win_rate, win_loss_ratio)
        """
        # Get the most recent trades up to lookback
        recent_trades = trade_history[-self.lookback:]
        
        # Extract PnL values (assuming 'pnl' key in each trade dict)
        pnls = [trade.get('pnl', 0) for trade in recent_trades if 'pnl' in trade]
        
        if not pnls:
            return self.win_rate, self.win_loss_ratio
        
        # Calculate wins and losses
        wins = [pnl for pnl in pnls if pnl > 0]
        losses = [abs(pnl) for pnl in pnls if pnl < 0]
        
        # Calculate win rate
        if pnls:
            win_rate = len(wins) / len(pnls)
        else:
            win_rate = self.win_rate
        
        # Calculate win/loss ratio
        if wins and losses:
            avg_win = sum(wins) / len(wins)
            avg_loss = sum(losses) / len(losses)
            win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else self.win_loss_ratio
        else:
            win_loss_ratio = self.win_loss_ratio
        
        return win_rate, win_loss_ratio
    
    def update_trade_history(self, trade: Dict[str, Any]) -> None:
        """
        Update the internal trade history.
        
        Parameters:
        -----------
        trade : dict
            Trade dictionary with at least a 'pnl' key
        """
        if 'pnl' in trade:
            self.historical_trades.append(trade) 