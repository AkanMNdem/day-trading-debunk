# Technical Overview: Day Trading Debunk (Simplified)

This document explains what each file and module does in the current simplified project structure.

## Current Project Structure

```
day-trading-debunk/
├── data/                    # Simple data handling
│   ├── simple_data.py       # All data functions in one file
│   └── __init__.py          # Module exports
├── src/                     # Core simplified modules
│   ├── backtest/
│   │   ├── simple_backtest.py    # Single file backtesting engine
│   │   └── __init__.py           # Exports SimpleBacktest
│   ├── strategies/
│   │   ├── base.py               # Abstract Strategy class
│   │   ├── rsi_strategy.py       # RSI mean reversion
│   │   ├── ema_strategy.py       # EMA crossover
│   │   ├── vwap_strategy.py      # VWAP bounce
│   │   ├── buy_hold.py           # Buy and hold benchmark
│   │   ├── random_strategy.py    # Random signal baseline
│   │   └── __init__.py           # Strategy exports
│   ├── position_sizing/
│   │   ├── simple_position_sizing.py  # All sizing methods
│   │   └── __init__.py                # Position sizing exports
│   ├── risk_management/
│   │   ├── simple_risk_management.py  # All risk controls
│   │   └── __init__.py                # Risk management exports
│   └── statistical_analysis/
│       ├── advanced_stats.py          # CROWN JEWEL - All statistical methods
│       └── __init__.py                # Statistical exports
├── tests/                   # Working test suite
├── run_backtest.py          # Main demo script - strategy comparison
├── run_tests.py             # Test runner with coverage
├── Makefile                 # Easy commands (make test, make backtest)
├── build.sh                 # Complete build script
├── requirements.txt         # Dependencies (fixed version conflicts)
└── pytest.ini              # Test configuration
```

## Key Files Explained

### Entry Points

**run_backtest.py** - Main demo script that:
- Gets data (real from Alpaca or fake if no API keys)
- Tests RSI, Random, and Buy-Hold strategies
- Generates beautiful comparison charts
- Shows strategy performance summary table
- Dependencies: `src.backtest.SimpleBacktest`, `src.strategies`, `data.simple_data`

**run_tests.py** - Test runner that:
- Runs pytest with coverage reporting
- Supports unit/integration test filtering
- Generates HTML coverage reports
- Dependencies: `pytest`, `pytest-cov`

**Makefile** - Easy commands:
- `make test` - Run all tests with coverage
- `make backtest` - Run strategy comparison demo  
- `make clean` - Clean up generated files
- `make help` - Show all available commands

### Data Module (data/)

**simple_data.py** - Single file for all data needs:
- `create_fake_stock_data()` - Generates realistic synthetic price data
- `get_real_data()` - Fetches real data from Alpaca API
- `add_simple_indicators()` - Calculates SMA, RSI, VWAP
- `get_data_for_backtesting()` - One-stop function with fallback to fake data
- Dependencies: `alpaca-py`, `pandas`, `numpy`, `python-dotenv`

### Core Modules (src/)

#### Backtesting (src/backtest/)

**simple_backtest.py** - Complete backtesting engine in one file:
- `SimpleBacktest` class handles everything: trades, costs, metrics
- `run()` method executes strategy and returns full results
- `compare_strategies()` runs multiple strategies and compares
- `plot_equity_curves()` generates comparison charts
- Handles commission, slippage, position management
- Returns equity curves, trade details, and performance metrics
- Dependencies: `pandas`, `numpy`, `matplotlib`

#### Strategies (src/strategies/)

**base.py** - Abstract Strategy class:
- Defines interface all strategies must implement
- `generate_signals()` method returns DataFrame with 'signal' column
- Simple inheritance pattern

**rsi_strategy.py** - RSI Mean Reversion:
- Buys when RSI < oversold threshold (default 30)
- Sells when RSI > overbought threshold (default 70)
- Uses `ta` library for RSI calculation
- Shifts signals to avoid look-ahead bias

**ema_strategy.py** - EMA Crossover:
- Buys when fast EMA crosses above slow EMA
- Sells when fast EMA crosses below slow EMA
- Calculates EMA difference and previous difference

**vwap_strategy.py** - VWAP Bounce:
- Buys when price is below VWAP by threshold
- Sells when price is above VWAP by threshold
- Calculates VWAP over rolling window

**buy_hold.py** - Buy and Hold benchmark:
- Buys on first day, holds forever
- Simple baseline strategy

**random_strategy.py** - Random signal generator:
- Generates random buy/sell signals with configurable frequency
- Important baseline for statistical testing

#### Position Sizing (src/position_sizing/)

**simple_position_sizing.py** - All position sizing methods:
- `FixedPercentageSizer` - Fixed percentage of capital
- `FixedDollarSizer` - Fixed dollar amount per trade
- `VolatilityAdjustedSizer` - Adjusts based on price volatility
- `KellyCriterionSizer` - Optimal sizing based on win rate and avg returns
- Factory function `create_position_sizer()` for easy creation
- Dependencies: `numpy`, `pandas`

#### Risk Management (src/risk_management/)

**simple_risk_management.py** - All risk controls:
- `SimpleRiskManager` class handles multiple risk types
- Stop losses: fixed price, percentage, trailing
- Take profits: fixed price, percentage
- Position limits and risk/reward ratios
- Can be integrated with backtesting engine
- Dependencies: `numpy`, `pandas`

#### Statistical Analysis (src/statistical_analysis/)

**advanced_stats.py** - CROWN JEWEL with graduate-level methods:
- Hypothesis testing (t-tests, paired tests, multiple testing correction)
- Bootstrap analysis with bias-corrected confidence intervals
- Effect size analysis (Cohen's d, Cliff's delta)
- Monte Carlo simulation and permutation tests
- Sharpe ratio testing (Jobson-Korkie test)
- All methods needed for rigorous strategy evaluation
- Dependencies: `scipy`, `numpy`, `pandas`, `statsmodels`

### Testing (tests/)

**test_statistical_analysis.py** - Tests for statistical methods
**test_risk_management.py** - Tests for risk controls
**test_position_sizing.py** - Tests for position sizing
**test_integration.py** - End-to-end workflow tests
**strategies/** - Unit tests for each strategy

All tests use `pytest` with coverage reporting.

## Dependencies Summary

### Core Data Science Stack:
- `numpy` (1.26.4) - Numerical computing
- `pandas` (>=2.0.0) - Data manipulation
- `scipy` (>=1.10.0) - Scientific computing
- `statsmodels` (>=0.14.0) - Advanced statistics
- `matplotlib` (>=3.8.0) - Plotting

### Financial Data:
- `alpaca-py` (0.39.1) - Market data API
- `ta` (0.11.0) - Technical indicators

### Development:
- `pytest` (>=8.0.0) - Testing framework
- `pytest-cov` (>=4.0.0) - Coverage reporting

## Personal Run Instructions

### Quick Start:
```bash
# Install and test everything
make install && make quick-demo

# Run backtest with charts
make backtest

# Run just tests
make test
```

### Development Workflow:
```bash
# Edit strategies in src/strategies/
# Edit statistical analysis in src/statistical_analysis/advanced_stats.py
# Test changes with: make test
# See results with: make backtest
```

### Adding Real Data:
1. Get free Alpaca API keys from alpaca.markets
2. Add to `.env` file:
   ```
   ALPACA_API_KEY=your_key
   ALPACA_SECRET_KEY=your_secret
   ```
3. Change `use_real_data=True` in `run_backtest.py`

### Key Performance Notes:
- Statistical analysis can take time with large datasets
- Monte Carlo simulations are CPU intensive
- Fake data is instant, real data requires API calls
- Charts are saved as PNG files automatically

## Code Quality Features

- **Type hints** throughout for better IDE support
- **Docstrings** with Google-style formatting
- **Error handling** with graceful degradation
- **Modular design** - easy to extend or modify
- **Comprehensive testing** with good coverage
- **Clean imports** - no circular dependencies
- **Professional structure** suitable for interviews/portfolio 