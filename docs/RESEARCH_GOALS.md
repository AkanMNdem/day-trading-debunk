# Research Goals: Day Trading Strategy Analysis

## Primary Research Objective

**Prove through statistical analysis that common day trading strategies promoted by TikTok gurus and social media influencers are unprofitable and perform no better than random chance.**

## Research Questions

### Primary Questions
1. Do popular day trading strategies (RSI, EMA crossover, VWAP bounce) generate statistically significant positive returns after transaction costs?
2. How do these strategies perform compared to random trading and buy-and-hold?
3. What is the probability that apparent "success" stories are due to random chance rather than skill?

### Secondary Questions
4. How do transaction costs impact strategy profitability?
5. What are the risk-adjusted returns (Sharpe ratio) of these strategies?
6. How frequently do these strategies experience significant drawdowns?

## Strategies to Analyze

### "TikTok Guru" Strategies (Implemented)
- **RSI Mean Reversion** - "Buy when RSI < 30, sell when RSI > 70"
- **EMA Crossover** - "Golden cross" and "death cross" signals
- **VWAP Bounce** - "Price bounces off VWAP support/resistance"

### Additional Strategies (To Add)
- **Support/Resistance Strategy** - "Buy at support, sell at resistance"
- **Breakout Strategy** - "Buy breakouts above resistance with volume"
- **Moving Average Bounce** - "Price respects the 50/200 MA"
- **Fibonacci Retracement** - "Buy at 61.8% retracement levels"

### Baseline Comparisons (Implemented)
- **Random Strategy** - Random buy/sell decisions with same frequency
- **Buy and Hold** - Simple benchmark

## Statistical Analysis Framework

### Performance Metrics
- **Returns**: Total return, annualized return
- **Risk Metrics**: Volatility, maximum drawdown, Sharpe ratio
- **Trade Metrics**: Win rate, profit factor, total trades

### Statistical Tests
- **Hypothesis Testing**: t-tests for mean returns vs. zero
- **Bootstrap Analysis**: Confidence intervals for performance metrics
- **Monte Carlo Simulation**: Probability distributions of outcomes
- **Comparison Analysis**: Strategy vs. random, strategy vs. benchmark

### Key Hypotheses to Test

**H1: Strategy Profitability**
- Null: Strategy returns = 0 (after costs)
- Expected Result: Fail to reject null (no significant profit)

**H2: Strategy vs. Random**
- Null: Strategy returns = Random strategy returns
- Expected Result: Fail to reject null (no better than random)

**H3: Strategy vs. Benchmark**
- Null: Strategy risk-adjusted returns >= Benchmark returns
- Expected Result: Reject null (underperform benchmark)

## Data Requirements

### Market Data
- **Timeframes**: 1-minute, 5-minute, 1-hour, daily
- **Duration**: Minimum 2-3 years of historical data
- **Assets**: Focus on liquid ETFs (SPY, QQQ) and major stocks
- **Quality**: High-quality data with volume information

### Transaction Cost Modeling
- **Commission**: $0-1 per trade (various broker models)
- **Slippage**: 0.01-0.1% depending on market conditions
- **Bid-Ask Spread**: Asset-specific spread modeling

## Expected Deliverables

1. **Statistical Report**: Comprehensive analysis of strategy performance with clear conclusions
2. **Interactive Charts**: Strategy comparison visualizations
3. **Research Summary**: Professional document debunking specific claims
4. **Reproducible Code**: Open-source implementation for verification

## Success Criteria

The project will be successful if we demonstrate:

1. **No Statistical Edge**: Popular strategies show no significant positive returns after costs
2. **Random Performance**: Strategies perform no better than random trading
3. **High Transaction Costs**: Small costs eliminate any potential edge
4. **High Risk**: Strategies carry unacceptable drawdown risk

## Personal Instructions for Running Real Analysis

### Step 1: Set Up Real Data
```bash
# Get free Alpaca API keys from alpaca.markets
# Add to .env file:
echo "ALPACA_API_KEY=your_key" > .env
echo "ALPACA_SECRET_KEY=your_secret" >> .env

# Test data collection
python -c "from data.simple_data import get_real_data; print(get_real_data('SPY', 30).head())"
```

### Step 2: Run Extended Analysis
```bash
# Edit run_backtest.py:
# - Change use_real_data=True
# - Change days=252 (1 year of data)
# - Add more symbols: ['SPY', 'QQQ', 'AAPL']

# Run comprehensive backtest
make backtest
```

### Step 3: Statistical Analysis
```python
# In Python interpreter or notebook:
from src.statistical_analysis.advanced_stats import AdvancedStatistics
import pandas as pd

# Load your backtest results
results = pd.read_csv('backtest_results.csv')  # Save results first

# Run full statistical battery
stats = AdvancedStatistics()
hypothesis_test = stats.hypothesis_test(results['returns'])
bootstrap_ci = stats.bootstrap_confidence_interval(results['returns'])
monte_carlo = stats.monte_carlo_simulation(results, n_simulations=10000)

print("Full Statistical Report:")
print(f"P-value: {hypothesis_test['p_value']:.4f}")
print(f"95% CI: {bootstrap_ci}")
print(f"Monte Carlo p-value: {monte_carlo['p_value']:.4f}")
```

### Step 4: Generate Report
```bash
# Create comprehensive analysis
python -c "
from src.statistical_analysis.advanced_stats import *
# Run full analysis and save results
# This will take 10-30 minutes for comprehensive testing
"

# Generate charts and save results
make backtest > analysis_results.txt
```

### Quick Testing Commands
```bash
# Test with fake data (instant)
make backtest

# Test with 1 week real data
python -c "
from data.simple_data import get_data_for_backtesting
data = get_data_for_backtesting('SPY', days=7, use_real_data=True)
print(f'Got {len(data)} days of data')
"

# Test statistical functions
python -c "
from src.statistical_analysis.advanced_stats import AdvancedStatistics
import numpy as np
stats = AdvancedStatistics()
fake_returns = np.random.normal(0, 0.02, 100)
result = stats.hypothesis_test(fake_returns)
print(f'Test result: {result}')
"
```

## Research Timeline

### Short-term (1-2 weeks)
- Improve Alpaca API integration
- Add 2-3 more TikTok strategies
- Run analysis on 1-2 years of SPY data

### Medium-term (1-2 months)
- Extend to multiple symbols and timeframes
- Generate comprehensive statistical report
- Create publication-ready visualizations

### Long-term Goals
- Academic paper or blog post
- Interactive web dashboard
- Extended strategy library 