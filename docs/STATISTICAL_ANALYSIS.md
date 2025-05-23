# Statistical Analysis Methodology

## 🔬 **Overview**

This document outlines the statistical methods and analytical framework used to rigorously test day trading strategies promoted by social media influencers. Our goal is to provide objective, statistically sound evidence about strategy performance.

## 📊 **Core Statistical Framework**

### **1. Hypothesis Testing Structure**

#### **Primary Null Hypotheses:**
- **H₀₁**: Mean strategy returns ≤ 0 (after transaction costs)
- **H₀₂**: Strategy Sharpe ratio ≤ Random strategy Sharpe ratio  
- **H₀₃**: Strategy returns ≤ Buy-and-hold returns (risk-adjusted)
- **H₀₄**: Transaction costs have no significant impact on returns

#### **Significance Level:**
- **α = 0.05** for individual tests
- **Bonferroni correction** for multiple comparisons: α/n where n = number of strategies tested

### **2. Performance Metrics Calculation**

#### **Return Metrics:**
```python
# Total Return
total_return = (final_value - initial_value) / initial_value

# Annualized Return  
annualized_return = (total_return + 1) ** (252 / trading_days) - 1

# Excess Return (vs benchmark)
excess_return = strategy_return - benchmark_return
```

#### **Risk Metrics:**
```python
# Sharpe Ratio
sharpe_ratio = (mean_return - risk_free_rate) / std_return

# Sortino Ratio (downside deviation)
sortino_ratio = (mean_return - risk_free_rate) / downside_std

# Maximum Drawdown
max_drawdown = max((peak - trough) / peak)

# Value at Risk (95% confidence)
var_95 = np.percentile(returns, 5)
```

#### **Trade-Level Metrics:**
```python
# Win Rate
win_rate = profitable_trades / total_trades

# Profit Factor
profit_factor = gross_profit / abs(gross_loss)

# Average Trade
avg_trade = total_pnl / total_trades
```

## 🧪 **Statistical Tests**

### **1. One-Sample Tests (Strategy vs Zero)**

**Test**: One-sample t-test for mean returns
```python
from scipy import stats

# Test if mean return significantly different from 0
t_stat, p_value = stats.ttest_1samp(strategy_returns, 0)

# Effect size (Cohen's d)
cohens_d = mean_return / std_return
```

**Interpretation**:
- p < 0.05: Strategy has statistically significant returns
- Effect size: Small (0.2), Medium (0.5), Large (0.8)

### **2. Two-Sample Tests (Strategy vs Benchmark)**

**Test**: Two-sample t-test for comparing strategies
```python
# Welch's t-test (unequal variances)
t_stat, p_value = stats.ttest_ind(strategy_returns, benchmark_returns, equal_var=False)

# Mann-Whitney U test (non-parametric alternative)
u_stat, p_value = stats.mannwhitneyu(strategy_returns, benchmark_returns, alternative='two-sided')
```

### **3. Bootstrap Confidence Intervals**

**Purpose**: Robust confidence intervals for performance metrics
```python
from scipy.stats import bootstrap

def bootstrap_metric(data, metric_func, n_bootstrap=10000):
    """Bootstrap confidence interval for any metric"""
    bootstrap_samples = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_samples.append(metric_func(sample))
    
    ci_lower = np.percentile(bootstrap_samples, 2.5)
    ci_upper = np.percentile(bootstrap_samples, 97.5)
    return ci_lower, ci_upper
```

### **4. Monte Carlo Simulation**

**Purpose**: Assess probability of observed results occurring by chance
```python
def monte_carlo_simulation(n_simulations=10000):
    """Simulate random trading results"""
    simulated_returns = []
    
    for _ in range(n_simulations):
        # Generate random trades with same frequency as strategy
        random_signals = generate_random_signals(trade_frequency)
        sim_returns = backtest_strategy(random_signals, data)
        simulated_returns.append(sim_returns)
    
    return simulated_returns

# Calculate p-value: probability of random achieving observed return
p_value_mc = np.mean(simulated_returns >= observed_return)
```

## 📈 **Advanced Statistical Analysis**

### **1. Survival Analysis (Time to Ruin)**

**Purpose**: Calculate probability and expected time until account depletion
```python
def calculate_time_to_ruin(returns, initial_capital, ruin_threshold=0.1):
    """Calculate time until account drops below threshold"""
    equity_curve = np.cumprod(1 + returns) * initial_capital
    
    # Find first time equity drops below threshold
    ruin_times = []
    for threshold in [0.5, 0.3, 0.1]:  # 50%, 70%, 90% loss
        ruin_idx = np.where(equity_curve <= initial_capital * threshold)[0]
        if len(ruin_idx) > 0:
            ruin_times.append(ruin_idx[0])
    
    return ruin_times
```

### **2. Regime Analysis**

**Purpose**: Test strategy performance across different market conditions
```python
def regime_analysis(returns, market_returns):
    """Analyze performance in different market regimes"""
    # Define regimes based on market performance
    bull_market = market_returns > np.percentile(market_returns, 66)
    bear_market = market_returns < np.percentile(market_returns, 33)
    
    bull_performance = returns[bull_market]
    bear_performance = returns[bear_market]
    
    return {
        'bull_mean': np.mean(bull_performance),
        'bear_mean': np.mean(bear_performance),
        'bull_vol': np.std(bull_performance),
        'bear_vol': np.std(bear_performance)
    }
```

### **3. Transaction Cost Sensitivity Analysis**

**Purpose**: Measure how transaction costs impact strategy viability
```python
def transaction_cost_analysis(base_returns, trade_frequency, cost_range):
    """Analyze performance across different transaction cost levels"""
    results = {}
    
    for cost in cost_range:  # e.g., [0, 0.001, 0.005, 0.01]
        # Apply transaction costs
        cost_per_trade = cost * trade_frequency
        adjusted_returns = base_returns - cost_per_trade
        
        results[cost] = {
            'total_return': np.prod(1 + adjusted_returns) - 1,
            'sharpe_ratio': np.mean(adjusted_returns) / np.std(adjusted_returns),
            'max_drawdown': calculate_max_drawdown(adjusted_returns)
        }
    
    return results
```

## 🎯 **Multiple Hypothesis Testing Correction**

When testing multiple strategies, we need to correct for multiple comparisons:

```python
from statsmodels.stats.multitest import multipletests

def correct_p_values(p_values, method='bonferroni'):
    """Apply multiple testing correction"""
    rejected, p_corrected, alpha_sidak, alpha_bonf = multipletests(
        p_values, alpha=0.05, method=method
    )
    return p_corrected, rejected
```

**Methods**:
- **Bonferroni**: Most conservative, p_adj = p × n
- **FDR (Benjamini-Hochberg)**: Less conservative, controls false discovery rate
- **Holm**: Step-down method, more powerful than Bonferroni

## 📊 **Effect Size and Practical Significance**

Beyond statistical significance, we measure practical significance:

```python
def effect_size_analysis(strategy_returns, benchmark_returns):
    """Calculate various effect size measures"""
    
    # Cohen's d
    pooled_std = np.sqrt(((len(strategy_returns) - 1) * np.var(strategy_returns) + 
                         (len(benchmark_returns) - 1) * np.var(benchmark_returns)) / 
                        (len(strategy_returns) + len(benchmark_returns) - 2))
    cohens_d = (np.mean(strategy_returns) - np.mean(benchmark_returns)) / pooled_std
    
    # Common Language Effect Size (probability strategy > benchmark)
    cles = np.mean(strategy_returns[:, None] > benchmark_returns[None, :])
    
    return {'cohens_d': cohens_d, 'cles': cles}
```

## 🔍 **Robustness Checks**

### **1. Out-of-Sample Testing**
- **Training Period**: First 70% of data for parameter optimization
- **Test Period**: Last 30% for unbiased performance evaluation
- **Walk-Forward Analysis**: Rolling window optimization and testing

### **2. Sensitivity Analysis**
- **Parameter Robustness**: Test strategy across parameter ranges
- **Data Robustness**: Test on different assets and time periods
- **Cost Robustness**: Vary transaction cost assumptions

### **3. Simulation Validation**
```python
def validate_results(strategy_func, data, n_simulations=1000):
    """Validate results through repeated random sampling"""
    performance_dist = []
    
    for _ in range(n_simulations):
        # Random subsample of data
        sample_data = data.sample(frac=0.8, replace=False)
        perf = backtest_strategy(strategy_func, sample_data)
        performance_dist.append(perf)
    
    # Check consistency of results
    return {
        'mean_performance': np.mean(performance_dist),
        'std_performance': np.std(performance_dist),
        'ci_95': np.percentile(performance_dist, [2.5, 97.5])
    }
```

## 📝 **Reporting Standards**

### **Statistical Report Requirements:**
1. **Descriptive Statistics**: Mean, median, std dev, skewness, kurtosis
2. **Test Statistics**: t-statistics, p-values, confidence intervals
3. **Effect Sizes**: Cohen's d, Common Language Effect Size
4. **Robustness**: Out-of-sample results, sensitivity analysis
5. **Visualizations**: Distribution plots, equity curves, drawdown charts

### **P-Hacking Prevention:**
- **Pre-registered hypotheses**: Document all tests before running analysis
- **Multiple testing correction**: Adjust for multiple comparisons
- **Full disclosure**: Report all tests performed, not just significant ones
- **Replication data**: Provide code and data for independent verification

---

*This methodology ensures our analysis meets academic standards for statistical rigor while providing clear, actionable insights about day trading strategy performance.* 