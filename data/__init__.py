"""Simple data collection for day trading analysis."""

from .simple_data import (
    get_data_for_backtesting,
    create_fake_stock_data,
    get_real_data,
    add_simple_indicators,
    save_data,
    load_data
)

__all__ = [
    'get_data_for_backtesting',
    'create_fake_stock_data', 
    'get_real_data',
    'add_simple_indicators',
    'save_data',
    'load_data'
] 