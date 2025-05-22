"""Tests for the Portfolio class."""
import unittest
import pandas as pd
from datetime import datetime, timedelta
import pytest

from src.backtest.portfolio import Portfolio


@pytest.mark.unit
class TestPortfolio(unittest.TestCase):
    """Tests for the Portfolio class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a portfolio with initial capital
        self.initial_capital = 10000.0
        self.portfolio = Portfolio(initial_capital=self.initial_capital)
        
        # Set up test timestamps
        self.current_time = datetime.now()
        self.timestamps = [
            self.current_time,
            self.current_time + timedelta(hours=1),
            self.current_time + timedelta(hours=2),
            self.current_time + timedelta(hours=3)
        ]
    
    def test_initialization(self):
        """Test that portfolio initializes with the correct capital."""
        self.assertEqual(self.portfolio.initial_capital, self.initial_capital)
        self.assertEqual(self.portfolio.current_capital, self.initial_capital)
        self.assertTrue(self.portfolio.position.is_flat())
        self.assertEqual(len(self.portfolio.equity_curve), 0)
        self.assertEqual(len(self.portfolio.trades), 0)
    
    def test_update_price(self):
        """Test updating the current market price."""
        price = 100.0
        time = self.timestamps[0]
        
        self.portfolio.update_price(price, time)
        
        self.assertEqual(self.portfolio.current_price, price)
        self.assertEqual(self.portfolio.current_time, time)
        self.assertEqual(self.portfolio.equity_curve[time], self.initial_capital)
    
    def test_enter_long_position(self):
        """Test entering a long position."""
        # Update price first
        price = 100.0
        time = self.timestamps[0]
        self.portfolio.update_price(price, time)
        
        # Enter long position
        self.portfolio.execute_signal(1, price, time)
        
        # Check that position is long
        self.assertTrue(self.portfolio.position.is_long())
        
        # Check that trade was recorded
        self.assertEqual(len(self.portfolio.trades), 1)
        self.assertEqual(self.portfolio.trades[0]['type'], 'ENTER LONG')
        self.assertEqual(self.portfolio.trades[0]['price'], price)
        self.assertEqual(self.portfolio.trades[0]['time'], time)
    
    def test_enter_short_position(self):
        """Test entering a short position."""
        # Update price first
        price = 100.0
        time = self.timestamps[0]
        self.portfolio.update_price(price, time)
        
        # Enter short position
        self.portfolio.execute_signal(-1, price, time)
        
        # Check that position is short
        self.assertTrue(self.portfolio.position.is_short())
        
        # Check that trade was recorded
        self.assertEqual(len(self.portfolio.trades), 1)
        self.assertEqual(self.portfolio.trades[0]['type'], 'ENTER SHORT')
        self.assertEqual(self.portfolio.trades[0]['price'], price)
        self.assertEqual(self.portfolio.trades[0]['time'], time)
    
    def test_close_long_position(self):
        """Test closing a long position."""
        # Set up initial position
        buy_price = 100.0
        sell_price = 110.0
        
        buy_time = self.timestamps[0]
        sell_time = self.timestamps[1]
        
        # Update price and enter long position
        self.portfolio.update_price(buy_price, buy_time)
        self.portfolio.execute_signal(1, buy_price, buy_time)
        
        # Update price and close position with a sell signal
        self.portfolio.update_price(sell_price, sell_time)
        self.portfolio.execute_signal(-1, sell_price, sell_time)
        
        # Check that position is now flat
        self.assertTrue(self.portfolio.position.is_flat())
        
        # Check that both trades were recorded
        self.assertEqual(len(self.portfolio.trades), 2)
        self.assertEqual(self.portfolio.trades[0]['type'], 'ENTER LONG')
        self.assertEqual(self.portfolio.trades[1]['type'], 'EXIT LONG')
        
        # Check that capital increased (profit)
        self.assertGreater(self.portfolio.current_capital, self.initial_capital)
    
    def test_close_short_position(self):
        """Test closing a short position."""
        # Set up initial position
        sell_price = 100.0
        buy_price = 90.0
        
        sell_time = self.timestamps[0]
        buy_time = self.timestamps[1]
        
        # Update price and enter short position
        self.portfolio.update_price(sell_price, sell_time)
        self.portfolio.execute_signal(-1, sell_price, sell_time)
        
        # Update price and close position with a buy signal
        self.portfolio.update_price(buy_price, buy_time)
        self.portfolio.execute_signal(1, buy_price, buy_time)
        
        # Check that position is now flat
        self.assertTrue(self.portfolio.position.is_flat())
        
        # Check that both trades were recorded
        self.assertEqual(len(self.portfolio.trades), 2)
        self.assertEqual(self.portfolio.trades[0]['type'], 'ENTER SHORT')
        self.assertEqual(self.portfolio.trades[1]['type'], 'EXIT SHORT')
        
        # Check that capital increased (profit)
        self.assertGreater(self.portfolio.current_capital, self.initial_capital)
    
    def test_get_equity_curve(self):
        """Test getting the equity curve."""
        # Set up a simple trade sequence
        prices = [100.0, 105.0, 110.0, 105.0]
        
        # Update prices
        for i, price in enumerate(prices):
            self.portfolio.update_price(price, self.timestamps[i])
        
        # Get equity curve
        equity_curve = self.portfolio.get_equity_curve()
        
        # Check that it's a pandas Series
        self.assertIsInstance(equity_curve, pd.Series)
        
        # Check that it has the correct length
        self.assertEqual(len(equity_curve), len(prices))
    
    def test_get_trades(self):
        """Test getting the trades history."""
        # Set up a simple trade sequence
        self.portfolio.update_price(100.0, self.timestamps[0])
        self.portfolio.execute_signal(1, 100.0, self.timestamps[0])
        
        self.portfolio.update_price(110.0, self.timestamps[1])
        self.portfolio.execute_signal(-1, 110.0, self.timestamps[1])
        
        # Get trades
        trades = self.portfolio.get_trades()
        
        # Check that it's a pandas DataFrame
        self.assertIsInstance(trades, pd.DataFrame)
        
        # Check that it has the correct length
        self.assertEqual(len(trades), 2)


if __name__ == '__main__':
    unittest.main() 