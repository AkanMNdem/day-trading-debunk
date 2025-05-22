"""Tests for the base Strategy class."""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest

from src.strategies.base import Strategy


@pytest.mark.unit
class TestBaseStrategy(unittest.TestCase):
    """Tests for the base Strategy class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data with a datetime index
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=5),
            end=datetime.now(),
            freq='1H'
        )
        
        # Create a sample price DataFrame
        self.test_data = pd.DataFrame(
            index=dates,
            data={
                'Open': np.random.normal(100, 1, len(dates)),
                'High': np.random.normal(101, 1, len(dates)),
                'Low': np.random.normal(99, 1, len(dates)),
                'Close': np.random.normal(100, 1, len(dates)),
                'Volume': np.random.randint(1000, 10000, len(dates))
            }
        )
        
        # Create a base strategy instance
        self.strategy = Strategy(name="TestStrategy")
    
    def test_initialization(self):
        """Test that strategy initializes with the correct name."""
        self.assertEqual(self.strategy.name, "TestStrategy")
    
    def test_generate_signals(self):
        """Test that the base strategy generates a signals DataFrame with zeros."""
        signals = self.strategy.generate_signals(self.test_data)
        
        # Check that signals is a DataFrame
        self.assertIsInstance(signals, pd.DataFrame)
        
        # Check that it has the same index as the input data
        self.assertTrue(signals.index.equals(self.test_data.index))
        
        # Check that it has a 'signal' column
        self.assertIn('signal', signals.columns)
        
        # Check that all signals are 0 (no action)
        self.assertTrue((signals['signal'] == 0).all())
    
    def test_string_representation(self):
        """Test the string representation of the strategy."""
        self.assertEqual(str(self.strategy), "TestStrategy")


if __name__ == '__main__':
    unittest.main() 