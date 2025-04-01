# test_strategies.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Import your strategies
from src.strategies import (
    RSIMeanReversionStrategy,
    RandomStrategy,
    BuyAndHoldStrategy,
    EMACrossoverStrategy,
    VWAPBounceStrategy
)

def create_test_data(days=5, freq='1min'):
    """Create synthetic price data for testing."""
    # Create date range (market hours only: 9:30 AM to 4:00 PM)
    start_date = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0) - timedelta(days=days)
    
    # Generate timestamps for market hours only
    timestamps = []
    for day in range(days):
        day_start = start_date + timedelta(days=day)
        if day_start.weekday() < 5:  # Weekdays only
            for hour in range(9, 16):  # 9 AM to 4 PM
                for minute in range(0, 60):
                    if (hour == 9 and minute < 30) or hour > 15:
                        continue
                    timestamps.append(day_start.replace(hour=hour, minute=minute))
    
    # Create price data with some randomness and trend
    n = len(timestamps)
    base_price = 100
    
    # Start with a random walk
    random_changes = np.random.normal(0, 0.1, n).cumsum()
    
    # Add a sine wave pattern for some cyclicality
    t = np.linspace(0, 4*np.pi, n)
    sine_pattern = np.sin(t) * 2
    
    # Combine into price series
    close_prices = base_price + random_changes + sine_pattern
    
    # Create OHLCV data
    data = pd.DataFrame(index=pd.DatetimeIndex(timestamps))
    data['Open'] = close_prices - np.random.uniform(0, 0.5, n)
    data['High'] = close_prices + np.random.uniform(0, 0.5, n)
    data['Low'] = close_prices - np.random.uniform(0, 0.5, n)
    data['Close'] = close_prices
    data['Volume'] = np.random.randint(1000, 10000, n)
    
    # Add vwap column to simulate Alpaca data
    data['vwap'] = (data['High'] + data['Low'] + data['Close'])/3
    
    return data

def test_strategy(strategy, data):
    """Test a strategy with the provided data."""
    print(f"\nTesting {strategy.name} strategy:")
    
    signals = strategy.generate_signals(data)
    
    # Calculate basic statistics
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    hold_signals = (signals['signal'] == 0).sum()
    
    print(f"  Data points: {len(data)}")
    print(f"  Buy signals: {buy_signals} ({buy_signals/len(data)*100:.1f}%)")
    print(f"  Sell signals: {sell_signals} ({sell_signals/len(data)*100:.1f}%)")
    print(f"  Hold signals: {hold_signals} ({hold_signals/len(data)*100:.1f}%)")
    
    # Check if signals include strategy-specific columns
    strategy_columns = [col for col in signals.columns if col != 'signal']
    if strategy_columns:
        print(f"  Strategy outputs additional columns: {', '.join(strategy_columns)}")
    
    return signals

def plot_strategy_signals(data, signals, strategy_name):
    """Plot price data with buy/sell signals."""
    plt.figure(figsize=(12, 6))
    
    # Plot price
    plt.plot(data.index, data['Close'], label='Close Price', color='blue', alpha=0.6)
    
    # Plot buy signals
    buy_points = signals.index[signals['signal'] == 1]
    if len(buy_points) > 0:
        plt.scatter(buy_points, data.loc[buy_points, 'Close'], 
                   color='green', label='Buy Signal', marker='^', s=100)
    
    # Plot sell signals
    sell_points = signals.index[signals['signal'] == -1]
    if len(sell_points) > 0:
        plt.scatter(sell_points, data.loc[sell_points, 'Close'], 
                   color='red', label='Sell Signal', marker='v', s=100)
    
    # Add title and legend
    plt.title(f'{strategy_name} Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    plt.savefig(f'{strategy_name}_signals.png')
    print(f"  Plot saved as {strategy_name}_signals.png")

def main():
    """Main test function."""
    print("Creating test data...")
    data = create_test_data(days=5)
    print(f"Test data created with {len(data)} data points")
    
    # Test each strategy
    strategies = [
        RSIMeanReversionStrategy(rsi_period=14, oversold=30, overbought=70),
        RandomStrategy(signal_freq=0.05),
        BuyAndHoldStrategy(),
        EMACrossoverStrategy(fast_period=12, slow_period=26),
        VWAPBounceStrategy(vwap_period=20, threshold=0.005)
    ]
    
    for strategy in strategies:
        signals = test_strategy(strategy, data)
        plot_strategy_signals(data, signals, strategy.name)
        
    print("\nAll strategies tested successfully!")

if __name__ == "__main__":
    main()