"""Data collector for fetching and processing stock data."""
import os
import pandas as pd
from datetime import datetime
from typing import Union, List, Dict, Optional, Any

from dotenv import load_dotenv

from .api.client import AlpacaClient
from .processing.preprocessing import preprocess_data, calculate_technical_indicators

# Load environment variables from .env file
load_dotenv()


class DataCollector:
    """Main class for collecting and processing stock data."""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize the data collector.
        
        Parameters:
        -----------
        api_key : str, optional
            Alpaca API key (if not provided, will look for ALPACA_API_KEY environment variable)
        secret_key : str, optional
            Alpaca Secret key (if not provided, will look for ALPACA_SECRET_KEY environment variable)
        """
        # Initialize the API client
        self.api_client = AlpacaClient(api_key, secret_key)
        
        # Get API keys for convenience
        self.api_key = self.api_client.api_key
        self.secret_key = self.api_client.secret_key
        
        # Direct access to the client for advanced usage
        self.client = self.api_client.client
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('data/processed', exist_ok=True)
    
    def fetch_intraday_data(self, symbol: Union[str, List[str]], 
                           days_back: int = 10, 
                           interval: str = '1Min') -> pd.DataFrame:
        """
        Fetch intraday price data from Alpaca API.
        
        Parameters:
        -----------
        symbol : str or list
            Stock symbol(s) to fetch (e.g., 'SPY' or ['SPY', 'QQQ'])
        days_back : int
            Number of calendar days to look back
        interval : str
            Data timeframe ('1Min', '5Min', '15Min', '1Hour', '1Day')
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with OHLCV data
            
        Raises:
        -------
        ValueError
            If an unsupported interval is provided
        Exception
            For API errors or connection issues
        """
        # Use the API client to fetch data
        return self.api_client.fetch_intraday_data(symbol, days_back, interval)
    
    def save_data(self, data: pd.DataFrame, symbol: Union[str, List[str]], 
                 interval: str, processed: bool = False) -> Optional[str]:
        """
        Save the fetched data to a CSV file.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Data to save
        symbol : str or list
            Symbol of the data (or 'multi' for multiple symbols)
        interval : str
            Interval of the data
        processed : bool
            Whether the data is raw or processed
            
        Returns:
        --------
        str
            Path to the saved file
        """
        if data.empty:
            print("No data to save")
            return None
            
        # Generate filename with current date
        today = datetime.now().strftime('%Y-%m-%d')
        symbol_str = symbol if isinstance(symbol, str) else 'multi'
        
        # Choose the directory based on whether the data is processed
        directory = 'data/processed' if processed else 'data/raw'
        filename = f"{directory}/{symbol_str}_{interval}_{today}.csv"
        
        # Save to CSV
        data.to_csv(filename)
        print(f"Data saved to {filename}")
        
        return filename
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from a CSV file.
        
        Parameters:
        -----------
        file_path : str
            Path to the CSV file
            
        Returns:
        --------
        pd.DataFrame
            Loaded data
        """
        try:
            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for analysis.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Raw data
            
        Returns:
        --------
        pd.DataFrame
            Preprocessed data
        """
        # Use the preprocessing module
        return preprocess_data(data)
    
    def get_multi_stock_data(self, symbols: List[str], days_back: int = 10, 
                            interval: str = '1Min') -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks.
        
        Parameters:
        -----------
        symbols : list
            List of stock symbols
        days_back : int
            Number of calendar days to look back
        interval : str
            Data timeframe
            
        Returns:
        --------
        dict
            Dictionary of DataFrames with stock symbols as keys
        """
        # Fetch multiple symbols at once
        data = self.fetch_intraday_data(symbols, days_back, interval)
        
        if data.empty:
            return {}
        
        # Process data for each symbol
        result = {}
        
        # If multi-index with 'symbol' level, split into separate DataFrames
        if isinstance(data.index, pd.MultiIndex) and 'symbol' in data.index.names:
            for symbol in symbols:
                if symbol in data.index.get_level_values('symbol'):
                    symbol_data = data.xs(symbol, level='symbol')
                    result[symbol] = self.preprocess_data(symbol_data)
        else:
            # If only one symbol was requested, handle it differently
            result[symbols[0]] = self.preprocess_data(data)
        
        return result
    
    def get_data_with_indicators(self, symbol: str, days_back: int = 10,
                               interval: str = '1Min', 
                               indicators_config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Fetch data and calculate technical indicators.
        
        Parameters:
        -----------
        symbol : str
            Stock symbol
        days_back : int
            Number of calendar days to look back
        interval : str
            Data timeframe
        indicators_config : dict, optional
            Configuration for technical indicators
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with price data and technical indicators
        """
        # Fetch data
        data = self.fetch_intraday_data(symbol, days_back, interval)
        
        if data.empty:
            return data
        
        # Preprocess data
        processed_data = self.preprocess_data(data)
        
        # Calculate technical indicators
        return calculate_technical_indicators(processed_data, indicators_config) 