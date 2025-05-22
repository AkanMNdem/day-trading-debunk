import pandas as pd
import numpy as np
from datetime import datetime
from .position import Position

class Portfolio:
    """Tracks overall portfolio performance."""

    def __init__(self, initial_capital=10000.0):
        """Initialize portfolio with starting capital."""
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.position = Position()

        # Performance tracking
        self.equity_curve = {}
        self.trades = []

        # Current market data
        self.current_price = 0.0
        self.current_time = None

    def update_price(self, price, time):
        """Update the current market price."""
        self.current_price = price
        self.current_time = time

        # Update equity
        unrealized_pnl = self.position.get_pnl(price)
        total_equity = self.current_capital + unrealized_pnl

        # Record in equity curve
        self.equity_curve[time] = total_equity

    def execute_signal(self, signal, price, time, size=1.0):
        """Execute a trade based on a signal."""
        # First, close any existing opposite position
        if signal == 1 and self.position.is_short():  # Buy signal but short position
            self._close_position(price, time)
        elif signal == -1 and self.position.is_long():  # Sell signal but long position
            self._close_position(price, time)

        # Then enter new position if signal is not a close signal
        if signal == 1 and self.position.is_flat():  # Buy signal
            self._enter_long(price, time, size)
        elif signal == -1 and self.position.is_flat():  # Sell signal
            self._enter_short(price, time, size)

    def _enter_long(self, price, time, size=1.0):
        """Enter a long position."""
        # Calculate position size based on capital
        units = (self.current_capital * size) / price
        self.position.enter_long(units, price, time)

        # Record trade
        self.trades.append({
            'type': 'ENTER LONG',
            'time': time,
            'price': price,
            'units': units,
            'capital': self.current_capital
        })

    def _enter_short(self, price, time, size=1.0):
        """Enter a short position."""
        # Calculate position size based on capital
        units = (self.current_capital * size) / price
        self.position.enter_short(units, price, time)

        # Record trade
        self.trades.append({
            'type': 'ENTER SHORT',
            'time': time,
            'price': price,
            'units': units,
            'capital': self.current_capital
        })

    def _close_position(self, price, time):
        """Close any existing position."""
        if self.position.is_flat():
            return

        # Calculate realized P&L
        pnl = self.position.get_pnl(price)
        self.current_capital += pnl

        # Record trade
        position_type = 'LONG' if self.position.is_long() else 'SHORT'
        self.trades.append({
            'type': f'EXIT {position_type}',
            'time': time,
            'price': price,
            'units': abs(self.position.units),
            'pnl': pnl,
            'capital': self.current_capital
        })

        # Clear position
        self.position.exit_position()

    def get_equity_curve(self):
        """Return the equity curve as a pandas Series."""
        return pd.Series(self.equity_curve)

    def get_trades(self):
        """Return the trade history as a DataFrame."""
        return pd.DataFrame(self.trades)
