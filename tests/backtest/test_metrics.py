"""Tests for the metrics calculation module."""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest

from src.backtest.metrics import calculate_metrics


@pytest.mark.unit
class TestMetrics(unittest.TestCase):
    """Tests for the metrics calculation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test equity curve
        self.dates = pd.date_range(
            start=datetime.now() - timedelta(days=100),
            end=datetime.now(),
            freq='1D'
        )
        
        # Create an upward trending equity curve
        initial_equity = 10000.0
        returns = np.random.normal(0.001, 0.01, len(self.dates))  # Mean 0.1%, SD 1%
        
        # Make cumulative returns to create equity curve
        cumulative_returns = (1 + returns).cumprod()
        self.equity_curve = pd.Series(
            initial_equity * cumulative_returns,
            index=self.dates
        )
        
        # Create some sample trades
        self.trades = pd.DataFrame({
            'type': ['ENTER LONG', 'EXIT LONG', 'ENTER SHORT', 'EXIT SHORT', 'ENTER LONG', 'EXIT LONG'],
            'time': self.dates[::20],  # Every 20th day
            'price': [100, 110, 110, 100, 100, 120],
            'units': [10, 10, 10, 10, 10, 10],
            'pnl': [0, 100, 0, 100, 0, 200],
            'capital': [10000, 10100, 10100, 10200, 10200, 10400]
        })
    
    def test_calculate_metrics_returns(self):
        """Test that basic return metrics are calculated correctly."""
        metrics = calculate_metrics(self.equity_curve, self.trades)
        
        # Check that we have the expected metrics
        self.assertIn('total_return', metrics)
        self.assertIn('annualized_return', metrics)
        self.assertIn('daily_volatility', metrics)
        self.assertIn('annualized_volatility', metrics)
        
        # Check that total return is calculated correctly
        expected_total_return = (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]) - 1
        self.assertAlmostEqual(metrics['total_return'], expected_total_return)
        
        # Check that volatility is positive
        self.assertGreater(metrics['daily_volatility'], 0)
        self.assertGreater(metrics['annualized_volatility'], 0)
    
    def test_calculate_metrics_risk(self):
        """Test that risk metrics are calculated correctly."""
        metrics = calculate_metrics(self.equity_curve, self.trades, risk_free_rate=0.02)
        
        # Check that we have the expected metrics
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        
        # Check that Sharpe ratio is calculated
        self.assertIsInstance(metrics['sharpe_ratio'], float)
        
        # Check that max drawdown is between 0 and 1
        self.assertGreaterEqual(metrics['max_drawdown'], 0)
        self.assertLessEqual(metrics['max_drawdown'], 1)
    
    def test_calculate_metrics_trades(self):
        """Test that trade metrics are calculated correctly."""
        metrics = calculate_metrics(self.equity_curve, self.trades)
        
        # Check that we have the expected metrics
        self.assertIn('win_rate', metrics)
        self.assertIn('avg_win', metrics)
        self.assertIn('avg_loss', metrics)
        self.assertIn('profit_factor', metrics)
        self.assertIn('number_of_trades', metrics)
        
        # Check win rate calculation
        # In our test data, all trades are winning
        self.assertEqual(metrics['win_rate'], 1.0)
        
        # Check number of trades (3 round trips)
        self.assertEqual(metrics['number_of_trades'], 3)
        
        # Check average win
        expected_avg_win = np.mean([100, 100, 200])
        self.assertEqual(metrics['avg_win'], expected_avg_win)
    
    def test_calculate_metrics_without_trades(self):
        """Test that metrics work without trade data."""
        metrics = calculate_metrics(self.equity_curve)
        
        # Check that we still have return and risk metrics
        self.assertIn('total_return', metrics)
        self.assertIn('annualized_return', metrics)
        self.assertIn('max_drawdown', metrics)
        
        # Check that trade metrics have default values
        self.assertEqual(metrics['win_rate'], 0)
        self.assertEqual(metrics['avg_win'], 0)
        self.assertEqual(metrics['avg_loss'], 0)
        self.assertEqual(metrics['number_of_trades'], 0)


if __name__ == '__main__':
    unittest.main() 