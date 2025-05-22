import pandas as pd
import numpy as np
from datetime import datetime
from .portfolio import Portfolio
from .metrics import calculate_metrics, plot_equity_curve, plot_drawdown

class BacktestEngine:
    """Main backtesting engine."""

    def __init__(self, data, initial_capital=10000.0, commission=0.001, slippage=0.0):
        """
        Initialize the backtest engine.

        Parameters:
        -----------
        data : pd.DataFrame
            OHLCV price data with datetime index
        initial_capital : float
            Starting capital
        commission : float
            Commission as a percentage (e.g., 0.001 = 0.1%)
        slippage : float
            Slippage as a percentage (e.g., 0.0005 = 0.05%)
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        # Ensure standard column names
        if 'close' in self.data.columns and 'Close' not in self.data.columns:
            self.data['Close'] = self.data['close']
        if 'open' in self.data.columns and 'Open' not in self.data.columns:
            self.data['Open'] = self.data['open']

        # Initialize results container
        self.results = {}

    def run(self, strategy, name=None):
        """
        Run a backtest for a strategy.

        Parameters:
        -----------
        strategy : Strategy
            The trading strategy to test
        name : str, optional
            Name for this backtest run

        Returns:
        --------
        dict
            Dictionary of backtest results
        """
        # Use strategy name if no name provided
        if name is None:
            name = strategy.name

        # Generate trading signals
        signals = strategy.generate_signals(self.data)

        # Initialize portfolio
        portfolio = Portfolio(initial_capital=self.initial_capital)

        # Iterate through data and apply signals
        for i, timestamp in enumerate(self.data.index):
            # Get current price
            current_price = self.data.loc[timestamp, 'Close']

            # Apply slippage to price if we have a signal
            if i > 0 and signals.loc[timestamp, 'signal'] != 0:
                # Apply slippage in the direction of the trade
                slippage_adjustment = 1 + (self.slippage * np.sign(signals.loc[timestamp, 'signal']))
                adjusted_price = current_price * slippage_adjustment
            else:
                adjusted_price = current_price

            # Update portfolio with current price
            portfolio.update_price(adjusted_price, timestamp)

            # Execute any trading signals
            if i > 0:  # Skip first row to avoid look-ahead bias
                signal = signals.loc[timestamp, 'signal']
                if signal != 0:
                    # Apply commission
                    effective_commission = 1 - self.commission if signal > 0 else 1 + self.commission
                    portfolio.execute_signal(signal, adjusted_price * effective_commission, timestamp)

        # Calculate final equity and get trade history
        equity_curve = portfolio.get_equity_curve()
        trades = portfolio.get_trades()

        # Calculate performance metrics
        metrics = calculate_metrics(equity_curve, trades)

        # Store results
        self.results[name] = {
            'equity_curve': equity_curve,
            'trades': trades,
            'metrics': metrics
        }

        return self.results[name]

    def compare_strategies(self, strategies):
        """
        Run backtest for multiple strategies and compare.

        Parameters:
        -----------
        strategies : list
            List of strategy objects

        Returns:
        --------
        pd.DataFrame
            DataFrame comparing performance metrics
        """
        # Run backtest for each strategy
        for strategy in strategies:
            self.run(strategy)

        # Compile metrics for comparison
        metrics_comparison = {}

        for name, results in self.results.items():
            metrics_comparison[name] = results['metrics']

        return pd.DataFrame(metrics_comparison).T

    def plot_equity_curves(self, strategy_names=None):
        """Plot equity curves for selected strategies."""
        if strategy_names is None:
            strategy_names = list(self.results.keys())

        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))

        for name in strategy_names:
            if name in self.results:
                plt.plot(self.results[name]['equity_curve'], label=name)

        plt.title('Strategy Comparison - Equity Curves')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')
        plt.legend()
        plt.grid(True, alpha=0.3)

        return plt.gcf()

    def plot_drawdowns(self, strategy_names=None):
        """Plot drawdown curves for selected strategies."""
        if strategy_names is None:
            strategy_names = list(self.results.keys())

        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))

        for name in strategy_names:
            if name in self.results:
                equity = self.results[name]['equity_curve']
                returns = equity.pct_change().dropna()
                cum_returns = (1 + returns).cumprod()
                drawdown = 1 - cum_returns / cum_returns.cummax()

                plt.plot(drawdown, label=name)

        plt.title('Strategy Comparison - Drawdowns')
        plt.xlabel('Date')
        plt.ylabel('Drawdown')
        plt.legend()
        plt.grid(True, alpha=0.3)

        return plt.gcf()
