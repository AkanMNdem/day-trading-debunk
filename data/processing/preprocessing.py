"""Data preprocessing utilities."""
import pandas as pd
from typing import Dict, Any


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
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
    df = standardize_column_names(df)
    
    # Filter for market hours (9:30 AM to 4:00 PM ET)
    # Only apply if we're working with intraday data
    if df.index.to_series().diff().median().total_seconds() < 24*60*60:
        df = filter_market_hours(df)
    
    # Add useful derived columns
    df = add_derived_columns(df)
    
    return df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names to consistent format.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with possibly non-standard column names
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with standardized column names
    """
    column_mapping = {
        'open': 'Open', 
        'high': 'High', 
        'low': 'Low', 
        'close': 'Close',
        'volume': 'Volume',
        'trade_count': 'TradeCount',
        'vwap': 'VWAP'
    }
    
    return df.rename(columns={k: v for k, v in column_mapping.items() 
                             if k in df.columns and v not in df.columns})


def filter_market_hours(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter DataFrame to include only market hours (9:30 AM to 4:00 PM ET).
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with datetime index
        
    Returns:
    --------
    pd.DataFrame
        Filtered DataFrame
    """
    return df.between_time('9:30', '16:00')


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived columns like returns, moving averages, etc.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with price data
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with additional derived columns
    """
    # Add returns
    if 'Close' in df.columns:
        df['Returns'] = df['Close'].pct_change()
        
        # Add log returns
        df['LogReturns'] = df['Returns'].apply(lambda x: 0 if x <= -1 else pd.np.log1p(x))
    
    return df


def calculate_technical_indicators(df: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Calculate technical indicators based on the provided configuration.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with price data
    config : dict, optional
        Configuration for which indicators to calculate and their parameters
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with technical indicators added
    """
    if config is None:
        config = {
            'sma': [20, 50, 200],
            'ema': [12, 26],
            'rsi': [14],
            'macd': [{'fast': 12, 'slow': 26, 'signal': 9}],
            'bbands': [{'period': 20, 'std_dev': 2}]
        }
    
    result = df.copy()
    
    # Simple Moving Averages
    if 'sma' in config and 'Close' in result.columns:
        for period in config['sma']:
            result[f'SMA_{period}'] = result['Close'].rolling(window=period).mean()
    
    # Exponential Moving Averages
    if 'ema' in config and 'Close' in result.columns:
        for period in config['ema']:
            result[f'EMA_{period}'] = result['Close'].ewm(span=period, adjust=False).mean()
    
    # Relative Strength Index
    if 'rsi' in config and 'Close' in result.columns:
        for period in config['rsi']:
            delta = result['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            result[f'RSI_{period}'] = 100 - (100 / (1 + rs))
    
    # Add more indicator calculations as needed
    
    return result 