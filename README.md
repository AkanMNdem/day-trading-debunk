# 🧠 Day Trading Debunk

A work-in-progress data-driven project that explores, tests, and visualizes the performance of **popular day trading strategies** using real market data — to investigate whether they're actually profitable or just noise.

---

## 📈 Project Objective

This project is a critical analysis of day trading strategies. It aims to **debunk or validate** the efficacy of commonly-used technical indicators and strategies by:
- Backtesting them on historical market data.
- Comparing performance against randomized strategies and passive investing.
- Visualizing signal outputs and trade behavior.
- Laying the foundation for more robust financial research tools.

---

## ✅ Current Features (MVP Phase)

### ✔️ Strategies Implemented
- **EMA (Exponential Moving Average)**
- **RSI (Relative Strength Index)**
- **VWAP (Volume Weighted Average Price)**
- **Buy-and-Hold** (baseline)
- **Random Signals** (control)

### ✔️ Signals Visualized
Each strategy generates signals that are visualized and saved as `.png` images:
```
📈 RSI-14_signals.png
📈 VWAP-20_signals.png
📈 Buy-and-Hold_signals.png
...
```

### ✔️ Strategy Testing
```bash
python test_strategies.py
```
- Runs tests on each strategy.
- Outputs buy/sell signals and saves plots.
- Logs insights into `test_data_signals.txt`.

---

## 🛠️ Setup

### 1. Clone and Create Virtual Environment
```bash
git clone https://github.com/AkanMNdem/day-trading-debunk.git
cd day-trading-debunk
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Keys
If using Alpaca or other live market data:
- Create a `.env` file with:
  ```
  API_KEY=your_api_key
  API_SECRET=your_secret
  ```

---

## 🔭 Planned Enhancements

- 📦 **Strategy modularization** via `src/strategies/`
- ⚙️ Add metrics: Sharpe Ratio, Win %, Drawdown
- 📈 CLI or Jupyter-based report view
- 🧪 Monte Carlo or Walk-Forward simulations
- ⚡ Explore porting performance-sensitive logic to C++
- 📚 Add references to academic finance literature

---

## 💡 Vision

This project is meant to grow into a **quantitative sandbox** to test, measure, and simulate trading algorithms—eventually expanding to:
- **Portfolio construction**
- **Machine learning signal generation**
- **High-frequency trading patterns**
- **Academic-driven task scheduling models**

---

## 🧪 Disclaimers

> This project is for research and learning purposes only. It is not financial advice and should not be used for live trading.

---

## 📂 Project Structure

```
.
📆 data/               # Market data collection logic
📆 src/                # Core strategy logic (WIP)
🔒 .env                # Local API keys (not committed)
📅 *.png               # Signal plots per strategy
📆 test_strategies.py  # Runner for strategy testing
📁 requirements.txt
📁 README.md
```

---

## 📬 Contributing

Contributions and suggestions are welcome! Feel free to open issues or PRs.

---

## 🧠 Author

**AkanMNdem**  
Exploring trading, programming, and how systems really work.

