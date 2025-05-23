"""Test risk management functionality."""

from src.risk_management import (
    SimpleRiskManager,
    FixedStopLoss,
    FixedTakeProfit,
    ExitReason,
    create_risk_manager
)


def test_simple_risk_manager():
    """Test basic risk manager functionality."""
    rm = SimpleRiskManager(stop_loss_pct=0.02, take_profit_pct=0.04)
    
    # Test long position
    levels = rm.enter_position(100.0, 1)
    
    assert levels['entry_price'] == 100.0
    assert levels['stop_loss'] == 98.0  # 2% below entry
    assert levels['take_profit'] == 104.0  # 4% above entry
    assert levels['position_type'] == 1
    
    # Test risk/reward ratio
    rr_ratio = rm.get_risk_reward_ratio()
    assert rr_ratio == 2.0  # 4% profit / 2% risk
    
    print("✓ Basic risk manager test passed")


def test_stop_loss_trigger():
    """Test stop loss triggering."""
    rm = SimpleRiskManager(stop_loss_pct=0.02, take_profit_pct=0.04)
    rm.enter_position(100.0, 1)
    
    # Price moves down to stop loss
    should_exit, reason = rm.update_price(98.0)
    assert should_exit
    assert reason == ExitReason.STOP_LOSS
    
    # Price above stop loss - no exit
    rm.enter_position(100.0, 1)
    should_exit, reason = rm.update_price(99.0)
    assert not should_exit
    assert reason == ExitReason.NONE
    
    print("✓ Stop loss trigger test passed")


def test_take_profit_trigger():
    """Test take profit triggering."""
    rm = SimpleRiskManager(stop_loss_pct=0.02, take_profit_pct=0.04)
    rm.enter_position(100.0, 1)
    
    # Price moves up to take profit
    should_exit, reason = rm.update_price(104.0)
    assert should_exit
    assert reason == ExitReason.TAKE_PROFIT
    
    print("✓ Take profit trigger test passed")


def test_short_position():
    """Test risk management for short positions."""
    rm = SimpleRiskManager(stop_loss_pct=0.02, take_profit_pct=0.04)
    
    # Enter short position
    levels = rm.enter_position(100.0, -1)
    
    assert levels['stop_loss'] == 102.0  # 2% above entry (stop for short)
    assert levels['take_profit'] == 96.0  # 4% below entry (profit for short)
    
    # Test stop loss for short
    should_exit, reason = rm.update_price(102.0)
    assert should_exit
    assert reason == ExitReason.STOP_LOSS
    
    # Test take profit for short
    rm.enter_position(100.0, -1)
    should_exit, reason = rm.update_price(96.0)
    assert should_exit
    assert reason == ExitReason.TAKE_PROFIT
    
    print("✓ Short position test passed")


def test_trailing_stop():
    """Test trailing stop functionality."""
    rm = SimpleRiskManager(stop_loss_pct=0.02, take_profit_pct=0.04, 
                          trailing_stop_pct=0.02, use_trailing=True)
    
    rm.enter_position(100.0, 1)
    initial_stop = rm.stop_price
    
    # Price moves up - trailing stop should update
    rm.update_price(105.0)
    new_stop = rm.stop_price
    
    # Stop should have moved up
    assert new_stop > initial_stop
    assert new_stop == 105.0 * 0.98  # 2% below new high
    
    print("✓ Trailing stop test passed")


def test_fixed_stop_loss():
    """Test standalone fixed stop loss."""
    stop = FixedStopLoss(stop_pct=0.03)
    
    # Test long position
    stop_price = stop.calculate_stop(100.0, 1)
    assert stop_price == 97.0  # 3% below entry
    
    # Test triggering
    assert stop.is_triggered(97.0, 96.0, 1)  # Price below stop
    assert not stop.is_triggered(97.0, 98.0, 1)  # Price above stop
    
    print("✓ Fixed stop loss test passed")


def test_fixed_take_profit():
    """Test standalone fixed take profit."""
    tp = FixedTakeProfit(profit_pct=0.05)
    
    # Test long position
    target_price = tp.calculate_target(100.0, 1)
    assert target_price == 105.0  # 5% above entry
    
    # Test triggering
    assert tp.is_triggered(105.0, 106.0, 1)  # Price above target
    assert not tp.is_triggered(105.0, 104.0, 1)  # Price below target
    
    print("✓ Fixed take profit test passed")


def test_create_risk_manager():
    """Test factory function."""
    # Test basic creation
    rm1 = create_risk_manager(stop_loss=0.03, take_profit=0.06)
    assert rm1.stop_loss_pct == 0.03
    assert rm1.take_profit_pct == 0.06
    assert not rm1.use_trailing
    
    # Test with trailing stop
    rm2 = create_risk_manager(trailing_stop=0.025, use_trailing=True)
    assert rm2.trailing_stop_pct == 0.025
    assert rm2.use_trailing
    
    print("✓ Factory function test passed")


def test_unrealized_pnl():
    """Test unrealized P&L calculation."""
    rm = SimpleRiskManager()
    rm.enter_position(100.0, 1)
    
    # Price moves up 5%
    pnl = rm.get_unrealized_pnl(105.0)
    assert pnl == 0.05  # 5% profit
    
    # Price moves down 3%
    pnl = rm.get_unrealized_pnl(97.0)
    assert pnl == -0.03  # 3% loss
    
    print("✓ Unrealized P&L test passed")


def test_risk_manager_integration():
    """Test integration capabilities."""
    rm = SimpleRiskManager(stop_loss_pct=0.02, take_profit_pct=0.04)
    
    # Test status reporting
    status = rm.get_status()
    assert 'entry_price' in status
    assert 'risk_reward_ratio' in status
    
    # Test position lifecycle
    rm.enter_position(100.0, 1)
    assert rm.position_type == 1
    
    rm.exit_position()
    assert rm.position_type == 0
    assert rm.entry_price == 0.0
    
    print("✓ Integration test passed")


if __name__ == "__main__":
    test_simple_risk_manager()
    test_stop_loss_trigger()
    test_take_profit_trigger()
    test_short_position()
    test_trailing_stop()
    test_fixed_stop_loss()
    test_fixed_take_profit()
    test_create_risk_manager()
    test_unrealized_pnl()
    test_risk_manager_integration()
    print("\n🎉 All risk management tests passed!") 