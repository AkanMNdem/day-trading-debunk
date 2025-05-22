# Day Trading Debunk

A backtesting framework for analyzing the effectiveness of common day trading strategies on historical stock data.

## Project Overview

This project aims to empirically test various day trading strategies to evaluate their performance against simple benchmarks like buy-and-hold. The framework allows for:

- Fetching historical intraday stock data from Alpaca
- Implementing and testing various trading strategies
- Backtesting strategies with realistic trading costs (commission, slippage)
- Calculating performance metrics (returns, drawdowns, Sharpe ratio, etc.)
- Visualizing results with equity curves and trade signals

## Setup

### Prerequisites

- Python 3.8+
- Alpaca API keys (for live data)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/day-trading-debunk.git
cd day-trading-debunk
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your Alpaca API keys:
```
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
```

## Usage

### Run a backtest

To run a backtest with the pre-configured strategies:

```bash
python run_backtest.py
```

This will:
1. Fetch recent SPY data
2. Run backtests with multiple strategies
3. Generate performance comparison metrics
4. Save equity curves and drawdown charts as PNG files

### Test strategies with synthetic data

To test strategies on synthetic data (without API calls):

```bash
python test_strategies.py
```

This will generate synthetic price data and test all available strategies, saving signal charts as PNG files.

## Available Strategies

The project includes several common day trading strategies:

- **RSI Mean Reversion**: Buys oversold conditions and sells overbought conditions based on the RSI indicator
- **EMA Crossover**: Generates signals based on fast and slow exponential moving average crossovers
- **VWAP Bounce**: Trades based on price deviations from the Volume Weighted Average Price
- **Buy and Hold**: Simple benchmark strategy that buys and holds
- **Random**: Random signal generation as a statistical benchmark

## Project Structure

- `src/backtest/`: Core backtesting engine components
- `src/strategies/`: Trading strategy implementations
- `data/`: Data handling and API connection
- `tests/`: Unit and integration tests
- `notebooks/`: Jupyter notebooks for analysis (optional)
- `results/`: Output directory for backtest results

## Extending the Framework

### Creating a New Strategy

To implement a new trading strategy:

1. Create a new file in `src/strategies/`
2. Extend the base `Strategy` class
3. Implement the `generate_signals` method
4. Add your strategy to the imports in `src/strategies/__init__.py`

Example:

```python
from .base import Strategy

class MyNewStrategy(Strategy):
    def __init__(self, param1=10, param2=20):
        super().__init__(name="MyStrategy")
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data):
        # Your signal generation logic here
        signals = data.copy()
        signals['signal'] = 0  # Default: no signal
        
        # Your conditions for buy/sell signals
        # signals.loc[condition_for_buy, 'signal'] = 1
        # signals.loc[condition_for_sell, 'signal'] = -1
        
        return signals
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
