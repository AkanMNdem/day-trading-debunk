import matplotlib.pyplot as plt
from src.backtest import BacktestEngine
from src.strategies import RSIMeanReversionStrategy, RandomStrategy, BuyAndHoldStrategy
from data.data import DataCollector

def main():
    # 1. Get data
    collector = DataCollector()
    try:
        spy_data = collector.fetch_intraday_data('SPY', days_back=30)
        preprocessed_data = collector.preprocess_data(spy_data)

        if preprocessed_data.empty:
            print("No data available. Check your API connection.")
            return

        print(f"Data loaded: {len(preprocessed_data)} data points")

        # 2. Setup strategies
        rsi_strategy = RSIMeanReversionStrategy(rsi_period=14, oversold=30, overbought=70)
        random_strategy = RandomStrategy(signal_freq=0.05)
        buyhold_strategy = BuyAndHoldStrategy()

        # 3. Run backtests
        backtest = BacktestEngine(
            preprocessed_data,
            initial_capital=10000.0,
            commission=0.001,
            slippage=0.0005
        )

        # Compare all strategies
        comparison = backtest.compare_strategies([
            rsi_strategy,
            random_strategy,
            buyhold_strategy
        ])

        print("\nStrategy Performance Comparison:")
        print(comparison)

        # 4. Plot results
        print("\nGenerating plots...")
        backtest.plot_equity_curves()
        plt.savefig('equity_curves.png')
        print("Saved equity curves to 'equity_curves.png'")

        backtest.plot_drawdowns()
        plt.savefig('drawdowns.png')
        print("Saved drawdown charts to 'drawdowns.png'")

    except Exception as e:
        print(f"Error in backtest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
