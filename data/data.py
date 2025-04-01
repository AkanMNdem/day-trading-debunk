import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import Alpaca's latest SDK
from alpaca.data.historical import StockHistoricalDataClient
# from platformdirs.unix import Unix
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Load environment variables from .env file
load_dotenv()

class DataCollector:
    def __init__(self):
        """Initialize the data collector with Alpaca API credentials."""
        # Get API credentials from environment variables
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        # Check if API keys are available
        if not self.api_key or not self.secret_key:
            raise ValueError("API keys not found. Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file.")
        
        # Initialize Alpaca Historical Data client
        self.client = StockHistoricalDataClient(self.api_key, self.secret_key)
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
    
    def fetch_intraday_data(self, symbol, days_back=10, interval='1Min'):
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
        """
        # Calculate start and end dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Ensure symbol is a list even if a single string is provided
        symbols = [symbol] if isinstance(symbol, str) else symbol
        
        # Convert interval string to TimeFrame object
        if interval == '1Min':
            timeframe = TimeFrame.Minute
        elif interval == '5Min':
            timeframe = TimeFrame(5, TimeFrame.Minute)
        elif interval == '15Min':
            timeframe = TimeFrame(15, TimeFrame.Minute)
        elif interval == '1Hour':
            timeframe = TimeFrame.Hour
        elif interval == '1Day':
            timeframe = TimeFrame.Day
        else:
            raise ValueError(f"Unsupported interval: {interval}")
        
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
    
    def save_data(self, data, symbol, interval):
        """
        Save the fetched data to a CSV file.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Data to save
        symbol : str
            Symbol of the data (or 'multi' for multiple symbols)
        interval : str
            Interval of the data
            
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
        filename = f"data/{symbol_str}_{interval}_{today}.csv"
        
        # Save to CSV
        data.to_csv(filename)
        print(f"Data saved to {filename}")
        
        return filename
    
    def load_data(self, file_path):
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
    
    def preprocess_data(self, data):
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
        if data.empty:
            return data
            
        # Make a copy to avoid modifying the original
        df = data.copy()
        
        # Ensure datetime index
        df.index = pd.to_datetime(df.index)
        
        # Handle missing values (forward fill)
        df = df.ffill()
        
        # Standardize column names if needed
        column_mapping = {
            'open': 'Open', 
            'high': 'High', 
            'low': 'Low', 
            'close': 'Close',
            'volume': 'Volume',
            'trade_count': 'TradeCount',
            'vwap': 'VWAP'
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() 
                               if k in df.columns and v not in df.columns})
        
        # Filter for market hours (9:30 AM to 4:00 PM ET)
        # Only apply if we're working with intraday data
        if df.index.to_series().diff().median().total_seconds() < 24*60*60:
            df = df.between_time('9:30', '16:00')
        
        # Add useful derived columns
        if 'Close' in df.columns:
            df['Returns'] = df['Close'].pct_change()
        
        return df

    def get_multi_stock_data(self, symbols, days_back=10, interval='1Min'):
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


# Example usage (when run as a script)
if __name__ == "__main__":
    # Create .env file with your API keys before running
    collector = DataCollector()
    
    # Fetch SPY data for the last 5 days at 1-minute intervals
    try:
        spy_data = collector.fetch_intraday_data('SPY', days_back=5)
        
        # Save to CSV
        if not spy_data.empty:
            collector.save_data(spy_data, 'SPY', '1Min')
            
            # Preprocess the data
            processed_data = collector.preprocess_data(spy_data)
            print(f"Processed data shape: {processed_data.shape}")
            print(processed_data.head())
    except Exception as e:
        print(f"Error in example: {e}")