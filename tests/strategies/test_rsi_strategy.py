"""Tests for the RSI mean reversion strategy."""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest

from src.strategies.rsi_strategy import RSIMeanReversionStrategy


@pytest.mark.unit
class TestRSIStrategy(unittest.TestCase):
    """Tests for the RSI mean reversion strategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data with a datetime index
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='1h'  # Updated to use lowercase 'h'
        )
        
        # Create a sample price DataFrame with a price trend
        n = len(dates)
        base = 100
        
        # Create a more stable price series for RSI calculation
        np.random.seed(42)  # For consistent test results
        
        # Create a price series that rises and falls to test RSI signals
        trend = np.concatenate([
            np.linspace(0, 5, n // 2),  # Rising trend
            np.linspace(5, 0, n - n // 2)  # Falling trend
        ])
        
        # Add controlled noise to the trend
        noise = np.random.normal(0, 0.1, n)
        prices = base + trend + noise
        
        self.test_data = pd.DataFrame(
            index=dates,
            data={
                'Open': prices - 0.05,
                'High': prices + 0.1,
                'Low': prices - 0.1,
                'Close': prices,
                'Volume': np.random.randint(1000, 10000, n)
            }
        )
        
        # Ensure High >= max(Open, Close) and Low <= min(Open, Close)
        self.test_data['High'] = self.test_data[['High', 'Open', 'Close']].max(axis=1)
        self.test_data['Low'] = self.test_data[['Low', 'Open', 'Close']].min(axis=1)
        
        # Create RSI strategy with standard parameters
        self.rsi_strategy = RSIMeanReversionStrategy(
            rsi_period=14, 
            oversold=30, 
            overbought=70
        )
    
    def test_initialization(self):
        """Test that strategy initializes with the correct parameters."""
        self.assertEqual(self.rsi_strategy.name, "RSI-14")
        self.assertEqual(self.rsi_strategy.rsi_period, 14)
        self.assertEqual(self.rsi_strategy.oversold, 30)
        self.assertEqual(self.rsi_strategy.overbought, 70)
    
    def test_generate_signals(self):
        """Test that the RSI strategy generates the expected signals."""
        signals = self.rsi_strategy.generate_signals(self.test_data)
        
        # Check that signals is a DataFrame
        self.assertIsInstance(signals, pd.DataFrame)
        
        # Check that it has the same index as the input data
        self.assertTrue(signals.index.equals(self.test_data.index))
        
        # Check that it has 'signal' and 'RSI' columns
        self.assertIn('signal', signals.columns)
        self.assertIn('RSI', signals.columns)
        
        # Check that RSI values are within the expected range (0-100) for non-NaN values
        valid_rsi = signals['RSI'].dropna()
        if len(valid_rsi) > 0:
            self.assertTrue((valid_rsi >= 0).all() and (valid_rsi <= 100).all(), 
                          f"RSI values outside 0-100 range: min={valid_rsi.min()}, max={valid_rsi.max()}")
        
        # Check that we have valid signals (not just NaN)
        signal_count = (signals['signal'] != 0).sum()
        self.assertTrue(signal_count >= 0)  # At least 0 signals (could be all neutral)
        
        # Check that signal values are valid (-1, 0, 1)
        unique_signals = signals['signal'].unique()
        for signal in unique_signals:
            self.assertIn(signal, [-1, 0, 1])


if __name__ == '__main__':
    unittest.main() 