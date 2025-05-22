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
            freq='1H'
        )
        
        # Create a sample price DataFrame with a price trend
        n = len(dates)
        base = 100
        
        # Create a price series that rises and falls to test RSI signals
        # First half: rising prices for overbought conditions
        # Second half: falling prices for oversold conditions
        trend = np.concatenate([
            np.linspace(0, 10, n // 2),  # Rising trend
            np.linspace(10, 0, n - n // 2)  # Falling trend
        ])
        
        # Add noise to the trend
        noise = np.random.normal(0, 0.2, n)
        prices = base + trend + noise
        
        self.test_data = pd.DataFrame(
            index=dates,
            data={
                'Open': prices - 0.1,
                'High': prices + 0.2,
                'Low': prices - 0.2,
                'Close': prices,
                'Volume': np.random.randint(1000, 10000, n)
            }
        )
        
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
        
        # Check that RSI values are within the expected range (0-100)
        self.assertTrue((signals['RSI'] >= 0).all() and (signals['RSI'] <= 100).all())
        
        # Check that we have some buy and sell signals (may not always be true with random data)
        self.assertTrue(len(signals[signals['signal'] == 1]) > 0 or len(signals[signals['signal'] == -1]) > 0)
        
        # Verify signal logic (buy when RSI < oversold, sell when RSI > overbought)
        # Note: We need to check the previous period's RSI due to signal shifting
        for i in range(1, len(signals)):
            if signals['RSI'].iloc[i-1] < self.rsi_strategy.oversold:
                self.assertEqual(signals['signal'].iloc[i], 1)
            elif signals['RSI'].iloc[i-1] > self.rsi_strategy.overbought:
                self.assertEqual(signals['signal'].iloc[i], -1)


if __name__ == '__main__':
    unittest.main() 