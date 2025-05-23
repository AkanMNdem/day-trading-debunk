"""
Simple backtesting engine for trading strategy analysis.

Clean, professional implementation focused on core functionality
without over-engineering. Perfect for demonstrating both software
engineering and quantitative finance skills.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any


class SimpleBacktest:
    """Simple, clean backtesting engine."""
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 100000, 
                 commission: float = 0.001, slippage: float = 0.0005):
        """Initialize backtest engine.
        
        Args:
            data: DataFrame with OHLCV price data
            initial_capital: Starting capital
            commission: Commission rate (e.g., 0.001 = 0.1%)
            slippage: Slippage rate (e.g., 0.0005 = 0.05%)
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # Standardize column names
        if 'close' in self.data.columns:
            self.data['Close'] = self.data['close']
        
    def run(self, strategy, position_size: float = 1.0, position_sizer=None) -> Dict[str, Any]:
        """Run backtest for a strategy.
        
        Args:
            strategy: Strategy object with generate_signals method
            position_size: Fraction of capital to use per trade (0-1) - ignored if position_sizer provided
            position_sizer: Optional position sizer object with calculate_size method
            
        Returns:
            Dictionary with backtest results
        """
        # Generate signals
        signals = strategy.generate_signals(self.data)
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0  # Current position (shares)
        equity_curve = []
        trades = []
        
        # Run backtest
        for i, (timestamp, row) in enumerate(self.data.iterrows()):
            price = row['Close']
            signal = signals.loc[timestamp, 'signal'] if timestamp in signals.index else 0
            
            # Calculate current equity (cash + position value)
            portfolio_value = capital + (position * price)
            equity_curve.append(portfolio_value)
            
            # Execute trades based on signals
            if signal != 0 and i > 0:  # Skip first row to avoid look-ahead bias
                # Close existing position if signal is opposite
                if (signal > 0 and position < 0) or (signal < 0 and position > 0):
                    capital += self._execute_trade(position, price, "CLOSE")
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'CLOSE',
                        'price': price,
                        'shares': -position,
                        'capital': capital
                    })
                    position = 0
                
                # Open new position if currently flat
                if position == 0:
                    if position_sizer:
                        shares = position_sizer.calculate_size(capital, price, signal)
                    else:
                        trade_value = capital * position_size
                        shares = self._calculate_shares(trade_value, price, signal)
                    
                    if shares != 0:
                        cost = self._execute_trade(shares, price, "OPEN")
                        capital -= cost
                        position += shares
                        
                        trades.append({
                            'timestamp': timestamp,
                            'type': 'OPEN',
                            'price': price,
                            'shares': shares,
                            'capital': capital
                        })
        
        # Close final position if open
        if position != 0:
            final_price = self.data['Close'].iloc[-1]
            capital += self._execute_trade(position, final_price, "CLOSE")
        
        # Calculate metrics
        equity_series = pd.Series(equity_curve, index=self.data.index)
        metrics = self._calculate_metrics(equity_series, trades)
        
        return {
            'strategy_name': strategy.name,
            'equity_curve': equity_series,
            'trades': pd.DataFrame(trades) if trades else pd.DataFrame(),
            'metrics': metrics,
            'final_capital': capital
        }
    
    def _calculate_shares(self, trade_value: float, price: float, signal: int) -> int:
        """Calculate number of shares to trade."""
        # Apply slippage
        effective_price = price * (1 + self.slippage * np.sign(signal))
        
        # Calculate shares (positive for long, negative for short)
        shares = int((trade_value / effective_price) * np.sign(signal))
        
        return shares
    
    def _execute_trade(self, shares: int, price: float, trade_type: str) -> float:
        """Execute trade and return cost/proceeds."""
        gross_value = abs(shares) * price
        
        # Apply slippage
        if trade_type == "OPEN":
            slippage_cost = gross_value * self.slippage
        else:  # CLOSE
            slippage_cost = gross_value * self.slippage
        
        # Apply commission
        commission_cost = gross_value * self.commission
        
        # Calculate net proceeds (positive means money received)
        if shares > 0:  # Buying (long) or closing short
            net_cost = gross_value + slippage_cost + commission_cost
            return net_cost if trade_type == "OPEN" else -net_cost
        else:  # Selling (short) or closing long
            net_proceeds = gross_value - slippage_cost - commission_cost
            return -net_proceeds if trade_type == "OPEN" else net_proceeds
    
    def _calculate_metrics(self, equity_curve: pd.Series, trades: list) -> Dict[str, float]:
        """Calculate performance metrics."""
        returns = equity_curve.pct_change().dropna()
        
        # Basic metrics
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        
        # Volatility and Sharpe ratio
        if len(returns) > 1:
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)
            if total_return > -1:  # Avoid invalid power calculation
                annual_return = (1 + total_return) ** (252 / len(returns)) - 1
            else:
                annual_return = -1  # Complete loss
            sharpe_ratio = annual_return / annual_vol if annual_vol > 0 else 0
        else:
            annual_vol = 0
            annual_return = 0
            sharpe_ratio = 0
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Trade statistics
        if trades:
            trade_df = pd.DataFrame(trades)
            num_trades = len(trade_df[trade_df['type'] == 'OPEN'])
        else:
            num_trades = 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': num_trades,
            'final_value': equity_curve.iloc[-1]
        }
    
    def compare_strategies(self, strategies: list) -> pd.DataFrame:
        """Compare multiple strategies."""
        results = {}
        
        for strategy in strategies:
            result = self.run(strategy)
            results[strategy.name] = result['metrics']
        
        return pd.DataFrame(results).T
    
    def plot_equity_curves(self, strategies: list, title: str = "Strategy Comparison"):
        """Plot equity curves for multiple strategies."""
        plt.figure(figsize=(12, 6))
        
        for strategy in strategies:
            result = self.run(strategy)
            plt.plot(result['equity_curve'], label=strategy.name)
        
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt.gcf()


def quick_backtest(strategy, data, initial_capital=100000):
    """Quick backtest function for simple analysis."""
    backtest = SimpleBacktest(data, initial_capital)
    result = backtest.run(strategy)
    
    print(f"Strategy: {result['strategy_name']}")
    print(f"Total Return: {result['metrics']['total_return']:.2%}")
    print(f"Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {result['metrics']['max_drawdown']:.2%}")
    print(f"Number of Trades: {result['metrics']['num_trades']}")
    
    return result


# Example usage
if __name__ == "__main__":
    # This would normally be in a separate test file
    print("SimpleBacktest module loaded successfully!")
    print("Use: from src.backtest.simple_backtest import SimpleBacktest") 