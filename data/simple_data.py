"""
Simple data collection for day trading analysis.

Just the basics - get some stock data and make it ready for backtesting.
No fancy abstractions, just straightforward functions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

# Load API keys if available
load_dotenv()


def create_fake_stock_data(symbol: str = "SPY", days: int = 30, 
                          start_price: float = 100.0) -> pd.DataFrame:
    """
    Create realistic fake stock data for testing strategies.
    
    Perfect for when you don't have API keys or just want to play around.
    
    Args:
        symbol: Stock symbol name
        days: Number of days of data
        start_price: Starting price
        
    Returns:
        DataFrame with OHLCV data
    """
    # Create dates (skip weekends)
    dates = []
    current_date = datetime.now() - timedelta(days=days)
    
    while len(dates) < days:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Generate realistic price movements
    np.random.seed(42)  # So results are consistent
    
    # Daily returns that look somewhat realistic
    daily_returns = np.random.normal(0.0005, 0.02, days)  # Small positive drift, realistic volatility
    
    prices = [start_price]
    for ret in daily_returns[:-1]:
        prices.append(prices[-1] * (1 + ret))
    
    # Create OHLCV data
    data = []
    for i, (date, close_price) in enumerate(zip(dates, prices)):
        # Make realistic OHLC from close price
        daily_volatility = abs(np.random.normal(0, 0.01))
        
        high = close_price * (1 + daily_volatility)
        low = close_price * (1 - daily_volatility)
        open_price = low + (high - low) * np.random.random()
        
        # Make sure OHLC makes sense
        high = max(high, open_price, close_price)
        low = min(low, open_price, close_price)
        
        volume = int(np.random.normal(1000000, 300000))  # Realistic volume
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': max(volume, 100000)  # Ensure positive volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df


def get_real_data(symbol: str = "SPY", days: int = 30) -> pd.DataFrame:
    """
    Get real stock data using Alpaca API.
    
    You need API keys in a .env file:
    ALPACA_API_KEY=your_key
    ALPACA_SECRET_KEY=your_secret
    
    Args:
        symbol: Stock symbol (like SPY, AAPL, etc.)
        days: Number of days back to get
        
    Returns:
        DataFrame with OHLCV data, or empty DataFrame if it fails
    """
    try:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame
        
        # Get API keys
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            print("No API keys found. Use create_fake_stock_data() instead!")
            return pd.DataFrame()
        
        # Create client
        client = StockHistoricalDataClient(api_key, secret_key)
        
        # Get data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Day,  # Daily data is fine for most analysis
            start=start_date,
            end=end_date
        )
        
        bars = client.get_stock_bars(request)
        df = bars.df
        
        # Clean up the data
        if not df.empty:
            df = df.reset_index()
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)  # Remove timezone
            df = df.set_index('timestamp')
            df = df.drop('symbol', axis=1, errors='ignore')  # Remove symbol column if it exists
            
            return df
        else:
            print(f"No data found for {symbol}")
            return pd.DataFrame()
            
    except ImportError:
        print("alpaca-py not installed. Install with: pip install alpaca-py")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting real data: {e}")
        return pd.DataFrame()


def add_simple_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add basic technical indicators that trading strategies need.
    
    Args:
        data: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added indicators
    """
    df = data.copy()
    
    # Simple moving averages
    df['sma_20'] = df['close'].rolling(20).mean()
    df['sma_50'] = df['close'].rolling(50).mean()
    
    # RSI (Relative Strength Index)
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    df['rsi'] = calculate_rsi(df['close'])
    
    # VWAP (Volume Weighted Average Price) - simple version
    if len(df) > 0:
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    
    return df


def get_data_for_backtesting(symbol: str = "SPY", days: int = 60, 
                           use_real_data: bool = False) -> pd.DataFrame:
    """
    One-stop function to get data ready for backtesting.
    
    Args:
        symbol: Stock symbol
        days: Number of days of data (minimum 60 recommended for indicators)
        use_real_data: Try to use real API data, otherwise use fake data
        
    Returns:
        DataFrame ready for strategy testing
    """
    # Make sure we have enough days for indicators
    min_days = max(days, 60)
    
    if use_real_data:
        data = get_real_data(symbol, min_days)
        if data.empty:
            data = create_fake_stock_data(symbol, min_days)
    else:
        data = create_fake_stock_data(symbol, min_days)
    
    # Add indicators
    data = add_simple_indicators(data)
    
    # Only drop rows where ALL indicators are NaN (keep some NaN for early periods)
    data = data.dropna(subset=['close'])  # Just make sure we have price data
    
    return data


def save_data(data: pd.DataFrame, filename: str = None):
    """Save data to a CSV file."""
    if filename is None:
        filename = f"stock_data_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Create data directory if needed
    os.makedirs('data', exist_ok=True)
    filepath = f"data/{filename}"
    
    data.to_csv(filepath)
    print(f"Data saved to {filepath}")


def load_data(filename: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    try:
        data = pd.read_csv(f"data/{filename}", index_col=0, parse_dates=True)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()


# Example usage if running this file directly
if __name__ == "__main__":
    print("Testing simple data collection...")
    
    # Get some fake data
    fake_data = get_data_for_backtesting("SPY", days=30, use_real_data=False)
    print(f"Fake data shape: {fake_data.shape}")
    print(fake_data.head())
    
    # Try real data (will fall back to fake if no API keys)
    real_data = get_data_for_backtesting("SPY", days=10, use_real_data=True)
    print(f"Real/fallback data shape: {real_data.shape}") 