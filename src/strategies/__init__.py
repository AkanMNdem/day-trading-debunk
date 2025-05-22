# src/strategies/__init__.py
from .base import Strategy
from .mean_reversion import RSIMeanReversionStrategy
from .benchmark import RandomStrategy, BuyAndHoldStrategy
from .trend_following import EMACrossoverStrategy
from .volatility import VWAPBounceStrategy

# Allow direct import from strategies package
__all__ = [
    'Strategy',
    'RSIMeanReversionStrategy',
    'RandomStrategy',
    'BuyAndHoldStrategy',
    'EMACrossoverStrategy',
    'VWAPBounceStrategy'
]