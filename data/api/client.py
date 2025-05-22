"""Alpaca API client for fetching stock data."""
import os
from datetime import datetime, timedelta
import pandas as pd
from typing import Union, List, Optional

# Import Alpaca's latest SDK
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame


class AlpacaClient:
    """Client for interacting with the Alpaca API for stock data."""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize the Alpaca API client.
        
        Parameters:
        -----------
        api_key : str, optional
            Alpaca API key (if not provided, will look for ALPACA_API_KEY environment variable)
        secret_key : str, optional
            Alpaca Secret key (if not provided, will look for ALPACA_SECRET_KEY environment variable)
        """
        # Get API credentials from parameters or environment variables
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        
        # Check if API keys are available
        if not self.api_key or not self.secret_key:
            raise ValueError("API keys not found. Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file or pass them directly.")
        
        # Initialize Alpaca Historical Data client
        self.client = StockHistoricalDataClient(self.api_key, self.secret_key)
    
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
        # Calculate start and end dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Ensure symbol is a list even if a single string is provided
        symbols = [symbol] if isinstance(symbol, str) else symbol
        
        # Convert interval string to TimeFrame object
        try:
            timeframe = self._get_timeframe(interval)
        except ValueError as e:
            raise ValueError(f"Error with interval: {str(e)}")
        
        print(f"Fetching {interval} data for {symbols} from {start_date.date()} to {end_date.date()}")
        
        # Create request parameters
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=timeframe, # type: ignore
            start=start_date,
            end=end_date
        )
        
        try:
            # Get the bars data
            bars_data = self.client.get_stock_bars(request_params)
            
            # Check if data was returned
            if hasattr(bars_data, 'df'):
                df = bars_data.df # type: ignore
                
                # If fetching multiple symbols, return multi-index DataFrame
                # Otherwise, return a single-level DataFrame for the symbol
                if isinstance(symbol, str):
                    if len(df) > 0:
                        # Remove the symbol level if only one symbol
                        df = df.droplevel('symbol')
                
                return df
            else:
                print(f"No data returned for {symbols}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def _get_timeframe(self, interval: str) -> TimeFrame:
        """
        Convert string interval to Alpaca TimeFrame object.
        
        Parameters:
        -----------
        interval : str
            Data timeframe as a string ('1Min', '5Min', '15Min', '1Hour', '1Day')
            
        Returns:
        --------
        TimeFrame
            Alpaca TimeFrame object
            
        Raises:
        -------
        ValueError
            If an unsupported interval is provided
        """
        if interval == '1Min':
            return TimeFrame.Minute
        elif interval == '5Min':
            return TimeFrame(5, TimeFrame.Minute)
        elif interval == '15Min':
            return TimeFrame(15, TimeFrame.Minute)
        elif interval == '1Hour':
            return TimeFrame.Hour
        elif interval == '1Day':
            return TimeFrame.Day
        else:
            raise ValueError(f"Unsupported interval: {interval}. Supported intervals: 1Min, 5Min, 15Min, 1Hour, 1Day") 