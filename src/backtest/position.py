import pandas as pd
import numpy as np

class Position:
    """Tracks a single position (long, short, or flat)."""

    def __init__(self):
        """Initialize position tracking."""
        self.units = 0  # Number of units (positive=long, negative=short, 0=flat)
        self.entry_price = 0.0  # Average entry price
        self.entry_time = None  # When position was entered

    def enter_long(self, units, price, time):
        """Enter a long position."""
        self.units = units
        self.entry_price = price
        self.entry_time = time

    def enter_short(self, units, price, time):
        """Enter a short position."""
        self.units = -units
        self.entry_price = price
        self.entry_time = time

    def exit_position(self):
        """Exit the current position."""
        self.units = 0
        self.entry_price = 0.0
        # Keep entry_time for analysis purposes

    def get_pnl(self, current_price):
        """Calculate unrealized profit/loss."""
        if self.units == 0:
            return 0.0
        elif self.units > 0:  # Long position
            return self.units * (current_price - self.entry_price)
        else:  # Short position
            return -self.units * (self.entry_price - current_price)

    def is_long(self):
        """Check if position is long."""
        return self.units > 0

    def is_short(self):
        """Check if position is short."""
        return self.units < 0

    def is_flat(self):
        """Check if no position is held."""
        return self.units == 0
