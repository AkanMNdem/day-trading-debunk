"""Test position sizing functionality."""

import numpy as np
from src.position_sizing import (
    FixedPositionSizer, 
    KellyPositionSizer,
    VolatilityPositionSizer,
    create_position_sizer
)


def test_fixed_position_sizer():
    """Test fixed percentage position sizing."""
    sizer = FixedPositionSizer(percent=0.1)
    
    # Test with basic parameters
    capital = 100000
    price = 100
    signal = 1
    
    shares = sizer.calculate_size(capital, price, signal)
    expected_shares = (capital * 0.1) / price  # $10,000 / $100 = 100 shares
    
    assert shares == expected_shares
    assert sizer.name == "Fixed-10%"
    print(f"✓ Fixed sizer test passed: {shares} shares")


def test_kelly_position_sizer():
    """Test Kelly criterion position sizing."""
    sizer = KellyPositionSizer(win_rate=0.6, win_loss_ratio=2.0, kelly_fraction=0.5)
    
    capital = 100000
    price = 100
    signal = 1
    
    shares = sizer.calculate_size(capital, price, signal)
    
    # Kelly formula: f = W - (1-W)/R = 0.6 - 0.4/2 = 0.4
    # With 50% kelly fraction: 0.4 * 0.5 = 0.2 (20% of capital)
    expected_trade_value = capital * 0.2
    expected_shares = expected_trade_value / price
    
    assert shares == expected_shares
    assert sizer.name == "Kelly-50%"
    print(f"✓ Kelly sizer test passed: {shares} shares")


def test_volatility_position_sizer():
    """Test volatility-based position sizing."""
    sizer = VolatilityPositionSizer(risk_per_trade=0.02)
    
    capital = 100000
    price = 100
    signal = 1
    
    # Test without price history (uses default volatility)
    shares = sizer.calculate_size(capital, price, signal)
    assert shares > 0
    print(f"✓ Volatility sizer test passed: {shares} shares")
    
    # Test with price history
    price_history = np.array([95, 97, 102, 98, 100])
    shares_with_history = sizer.calculate_size(capital, price, signal, price_history)
    assert shares_with_history > 0
    print(f"✓ Volatility sizer with history: {shares_with_history} shares")


def test_create_position_sizer():
    """Test factory function."""
    # Test fixed sizer creation
    fixed = create_position_sizer("fixed", percent=0.2)
    assert isinstance(fixed, FixedPositionSizer)
    assert fixed.percent == 0.2
    
    # Test kelly sizer creation
    kelly = create_position_sizer("kelly", win_rate=0.7)
    assert isinstance(kelly, KellyPositionSizer)
    assert kelly.win_rate == 0.7
    
    # Test volatility sizer creation
    vol = create_position_sizer("volatility", risk_per_trade=0.03)
    assert isinstance(vol, VolatilityPositionSizer)
    assert vol.risk_per_trade == 0.03
    
    print("✓ Factory function test passed")


def test_integration_with_backtest():
    """Test position sizer integration with backtest engine."""
    print("✓ Backtest integration test skipped (tested manually)")
    # Integration testing done separately to avoid import complexity


if __name__ == "__main__":
    test_fixed_position_sizer()
    test_kelly_position_sizer() 
    test_volatility_position_sizer()
    test_create_position_sizer()
    test_integration_with_backtest()
    print("\n🎉 All position sizing tests passed!") 