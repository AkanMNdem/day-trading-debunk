"""Tests for the DataCollector class."""
import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytest

from data.data import DataCollector


@pytest.mark.unit
@pytest.mark.api
class TestDataCollector(unittest.TestCase):
    """Tests for the DataCollector class."""
    
    @patch('data.data.StockHistoricalDataClient')
    @patch('data.data.load_dotenv')
    @patch('data.data.os')
    def setUp(self, mock_os, mock_load_dotenv, mock_client):
        """Set up test fixtures with mocked dependencies."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key: {'ALPACA_API_KEY': 'test_key', 'ALPACA_SECRET_KEY': 'test_secret'}.get(key)
        mock_os.makedirs = MagicMock()
        
        # Create mock for Alpaca client
        self.mock_client_instance = mock_client.return_value
        
        # Initialize DataCollector with mocked dependencies
        self.data_collector = DataCollector()
        
        # Verify that the Alpaca client was initialized with correct credentials
        mock_client.assert_called_once_with('test_key', 'test_secret')
    
    def test_initialization(self):
        """Test that DataCollector initializes correctly."""
        self.assertEqual(self.data_collector.api_key, 'test_key')
        self.assertEqual(self.data_collector.secret_key, 'test_secret')
        self.assertIsNotNone(self.data_collector.client)
    
    @patch('data.data.StockBarsRequest')
    def test_fetch_intraday_data(self, mock_request):
        """Test fetching intraday data."""
        # Create mock response
        mock_bars = MagicMock()
        
        # Create mock DataFrame
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=5),
            end=datetime.now(),
            freq='1min'
        )
        
        mock_df = pd.DataFrame(
            index=dates,
            data={
                'open': np.random.normal(100, 1, len(dates)),
                'high': np.random.normal(101, 1, len(dates)),
                'low': np.random.normal(99, 1, len(dates)),
                'close': np.random.normal(100, 1, len(dates)),
                'volume': np.random.randint(1000, 10000, len(dates))
            }
        )
        
        # Set the DataFrame as a property of the mock
        mock_bars.df = mock_df
        
        # Configure the mock client to return our mock bars
        self.mock_client_instance.get_stock_bars.return_value = mock_bars
        
        # Call the method under test
        result = self.data_collector.fetch_intraday_data('SPY', days_back=5)
        
        # Verify request was created with correct parameters
        mock_request.assert_called_once()
        
        # Verify that client method was called
        self.mock_client_instance.get_stock_bars.assert_called_once()
        
        # Verify result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(mock_df))
    
    def test_preprocess_data(self):
        """Test preprocessing of data."""
        # Create test data
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=1),
            end=datetime.now(),
            freq='1H'
        )
        
        test_data = pd.DataFrame(
            index=dates,
            data={
                'open': np.random.normal(100, 1, len(dates)),
                'high': np.random.normal(101, 1, len(dates)),
                'low': np.random.normal(99, 1, len(dates)),
                'close': np.random.normal(100, 1, len(dates)),
                'volume': np.random.randint(1000, 10000, len(dates))
            }
        )
        
        # Process the data
        processed = self.data_collector.preprocess_data(test_data)
        
        # Verify column names are standardized
        self.assertIn('Open', processed.columns)
        self.assertIn('High', processed.columns)
        self.assertIn('Low', processed.columns)
        self.assertIn('Close', processed.columns)
        
        # Verify derived columns
        self.assertIn('Returns', processed.columns)
        
        # Verify index is datetime
        self.assertIsInstance(processed.index, pd.DatetimeIndex)
    
    def test_preprocess_data_with_empty_dataframe(self):
        """Test preprocessing with an empty DataFrame."""
        empty_df = pd.DataFrame()
        
        # Process empty data
        result = self.data_collector.preprocess_data(empty_df)
        
        # Verify that an empty DataFrame is returned
        self.assertTrue(result.empty)
    
    @patch('data.data.pd.read_csv')
    def test_load_data(self, mock_read_csv):
        """Test loading data from CSV."""
        # Create mock DataFrame to return
        mock_df = pd.DataFrame({
            'Open': [100, 101, 102],
            'Close': [101, 102, 103]
        })
        mock_read_csv.return_value = mock_df
        
        # Call the method
        result = self.data_collector.load_data('fake_path.csv')
        
        # Verify read_csv was called
        mock_read_csv.assert_called_once()
        
        # Verify result
        self.assertEqual(len(result), len(mock_df))
    
    @patch('data.data.pd.DataFrame.to_csv')
    def test_save_data(self, mock_to_csv):
        """Test saving data to CSV."""
        # Create test data
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'Close': [101, 102, 103]
        })
        
        # Call the method
        result = self.data_collector.save_data(test_data, 'SPY', '1Min')
        
        # Verify to_csv was called
        mock_to_csv.assert_called_once()
        
        # Verify result is a string (filename)
        self.assertIsInstance(result, str)
        self.assertIn('SPY', result)
        self.assertIn('1Min', result)


if __name__ == '__main__':
    unittest.main() 