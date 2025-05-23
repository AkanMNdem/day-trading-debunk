import matplotlib.pyplot as plt
from src.backtest import SimpleBacktest
from src.strategies import RSIMeanReversionStrategy, RandomStrategy, BuyAndHoldStrategy
from data.simple_data import get_data_for_backtesting

def main():
    print("🚀 Running simplified day trading backtest...")
    
    # 1. Get data (fake data by default, real data if you have API keys)
    try:
        data = get_data_for_backtesting(
            symbol="SPY", 
            days=60, 
            use_real_data=True  # Will fall back to fake data if no API keys
        )
        
        if data.empty:
            print("❌ No data available.")
            return
            
        print(f"✅ Data loaded: {len(data)} trading days")
        print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")

        # 2. Setup strategies to test
        strategies = [
            RSIMeanReversionStrategy(rsi_period=14, oversold=30, overbought=70),
            RandomStrategy(signal_freq=0.05),
            BuyAndHoldStrategy()
        ]

        # 3. Run backtests for each strategy
        results = {}
        for strategy in strategies:
            print(f"\n📊 Testing {strategy.name}...")
            
            backtest = SimpleBacktest(
                data=data,
                initial_capital=10000.0,
                commission=0.001,  # 0.1% commission
                slippage=0.0005    # 0.05% slippage
            )
            
            result = backtest.run(strategy)
            results[strategy.name] = result
            
            # Print key metrics (access from metrics dict)
            metrics = result['metrics']
            print(f"   Total Return: {metrics['total_return']:.1%}")
            print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"   Max Drawdown: {metrics['max_drawdown']:.1%}")
            print(f"   Total Trades: {metrics['num_trades']}")

        # 4. Compare all strategies
        print("\n🏆 Strategy Performance Summary:")
        print("-" * 60)
        print(f"{'Strategy':<20} {'Return':<10} {'Sharpe':<8} {'Drawdown':<10} {'Trades':<8}")
        print("-" * 60)
        
        for name, result in results.items():
            metrics = result['metrics']
            print(f"{name:<20} {metrics['total_return']:>8.1%} "
                  f"{metrics['sharpe_ratio']:>7.2f} {metrics['max_drawdown']:>8.1%} "
                  f"{metrics['num_trades']:>7}")

        # 5. Generate plots
        print("\n📈 Generating performance plots...")
        
        # Plot equity curves
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 1, 1)
        for name, result in results.items():
            plt.plot(result['equity_curve'].index, result['equity_curve'], 
                    label=name, linewidth=2)
        plt.title('Strategy Equity Curves')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot drawdowns
        plt.subplot(2, 1, 2)
        for name, result in results.items():
            equity = result['equity_curve']
            drawdown = (equity / equity.expanding().max() - 1) * 100
            plt.fill_between(drawdown.index, drawdown, 0, alpha=0.3, label=f"{name} Drawdown")
        plt.title('Strategy Drawdowns')
        plt.ylabel('Drawdown (%)')
        plt.xlabel('Date')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('strategy_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ Saved performance chart as 'strategy_comparison.png'")
        
        # Show the plot
        plt.show()

    except Exception as e:
        print(f"❌ Error in backtest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
