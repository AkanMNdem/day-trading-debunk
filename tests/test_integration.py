"""Integration tests for the day trading debunk project."""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest

from src.backtest import BacktestEngine
from src.strategies import (
    RSIMeanReversionStrategy,
    RandomStrategy,
    BuyAndHoldStrategy,
    EMACrossoverStrategy,
    VWAPBounceStrategy
)


@pytest.mark.integration
class TestBacktestIntegration(unittest.TestCase):
    """Integration tests for the backtesting framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create synthetic test data
        self.test_data = self.create_test_data(days=10)
        
        # Initialize backtest engine
        self.backtest = BacktestEngine(
            self.test_data,
            initial_capital=10000.0,
            commission=0.001,
            slippage=0.0005
        )
    
    def create_test_data(self, days=10):
        """Create synthetic price data for testing."""
        # Create date range (market hours only: 9:30 AM to 4:00 PM)
        start_date = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0) - timedelta(days=days)
        
        # Generate timestamps for market hours only
        timestamps = []
        for day in range(days):
            day_start = start_date + timedelta(days=day)
            if day_start.weekday() < 5:  # Weekdays only
                for hour in range(9, 16):  # 9 AM to 4 PM
                    for minute in range(0, 60):
                        if (hour == 9 and minute < 30) or hour > 15:
                            continue
                        timestamps.append(day_start.replace(hour=hour, minute=minute))
        
        # Create price data with some randomness and trend
        n = len(timestamps)
        base_price = 100
        
        # Start with a random walk
        random_changes = np.random.normal(0, 0.1, n).cumsum()
        
        # Add a sine wave pattern for some cyclicality
        t = np.linspace(0, 4*np.pi, n)
        sine_pattern = np.sin(t) * 2
        
        # Combine into price series
        close_prices = base_price + random_changes + sine_pattern
        
        # Create OHLCV data
        data = pd.DataFrame(index=pd.DatetimeIndex(timestamps))
        data['Open'] = close_prices - np.random.uniform(0, 0.5, n)
        data['High'] = close_prices + np.random.uniform(0, 0.5, n)
        data['Low'] = close_prices - np.random.uniform(0, 0.5, n)
        data['Close'] = close_prices
        data['Volume'] = np.random.randint(1000, 10000, n)
        
        # Add vwap column to simulate Alpaca data
        data['vwap'] = (data['High'] + data['Low'] + data['Close'])/3
        
        return data
    
    def test_run_single_strategy(self):
        """Test running a single strategy through the backtest engine."""
        # Create strategy
        strategy = RSIMeanReversionStrategy(rsi_period=14, oversold=30, overbought=70)
        
        # Run backtest
        results = self.backtest.run(strategy)
        
        # Check that we have all the expected results
        self.assertIn('equity_curve', results)
        self.assertIn('trades', results)
        self.assertIn('metrics', results)
        
        # Check that the equity curve is a pandas Series
        self.assertIsInstance(results['equity_curve'], pd.Series)
        
        # Check that we have metrics
        metrics = results['metrics']
        self.assertIn('total_return', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('sharpe_ratio', metrics)
    
    def test_compare_strategies(self):
        """Test comparing multiple strategies."""
        # Create strategies
        strategies = [
            RSIMeanReversionStrategy(rsi_period=14, oversold=30, overbought=70),
            RandomStrategy(signal_freq=0.05),
            BuyAndHoldStrategy()
        ]
        
        # Compare strategies
        comparison = self.backtest.compare_strategies(strategies)
        
        # Check that we have a comparison DataFrame
        self.assertIsInstance(comparison, pd.DataFrame)
        
        # Check that all strategies are in the comparison
        self.assertEqual(len(comparison), len(strategies))
        
        # Check that we have the expected metrics for each strategy
        for strategy in strategies:
            self.assertIn(strategy.name, comparison.index)
            
        # Check that we have key metrics in the comparison
        self.assertIn('total_return', comparison.columns)
        self.assertIn('max_drawdown', comparison.columns)
        self.assertIn('sharpe_ratio', comparison.columns)
    
    def test_plotting_functions(self):
        """Test that plotting functions work without errors."""
        # First run some strategies
        strategies = [
            RSIMeanReversionStrategy(rsi_period=14, oversold=30, overbought=70),
            RandomStrategy(signal_freq=0.05),
            BuyAndHoldStrategy()
        ]
        
        for strategy in strategies:
            self.backtest.run(strategy)
        
        # Test equity curve plotting
        try:
            self.backtest.plot_equity_curves()
            plot_successful = True
        except Exception as e:
            plot_successful = False
            print(f"Error plotting equity curves: {e}")
        
        self.assertTrue(plot_successful)
        
        # Test drawdown plotting
        try:
            self.backtest.plot_drawdowns()
            plot_successful = True
        except Exception as e:
            plot_successful = False
            print(f"Error plotting drawdowns: {e}")
        
        self.assertTrue(plot_successful)


if __name__ == '__main__':
    unittest.main() 