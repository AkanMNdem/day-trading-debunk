"""
Advanced Statistical Analysis for Trading Strategy Evaluation.

This module provides rigorous statistical methods to evaluate the performance 
of trading strategies, including hypothesis testing, bootstrap analysis, 
effect size calculations, and Monte Carlo simulations.

Perfect for demonstrating quantitative finance and statistical knowledge
in interviews and academic/professional settings.
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from typing import Dict, List, Tuple, Optional, Union, Callable
import warnings


class HypothesisTests:
    """Statistical hypothesis testing for trading strategy analysis."""
    
    def __init__(self, alpha: float = 0.05):
        """Initialize with significance level."""
        self.alpha = alpha
    
    def test_profitability(self, returns: np.ndarray) -> Dict[str, float]:
        """Test if strategy returns are significantly greater than zero.
        
        H₀: Mean return ≤ 0 (not profitable)
        H₁: Mean return > 0 (profitable)
        """
        returns = np.array(returns)[~np.isnan(returns)]
        
        if len(returns) == 0:
            raise ValueError("No valid returns provided")
        
        # One-sample t-test
        t_stat, p_value = stats.ttest_1samp(returns, 0)
        p_value_one_tailed = p_value / 2 if t_stat > 0 else 1 - p_value / 2
        
        # Effect size (Cohen's d)
        cohens_d = np.mean(returns) / np.std(returns, ddof=1) if np.std(returns) > 0 else 0
        
        return {
            't_statistic': t_stat,
            'p_value': p_value_one_tailed,
            'cohens_d': cohens_d,
            'mean_return': np.mean(returns),
            'std_return': np.std(returns, ddof=1),
            'significant': p_value_one_tailed < self.alpha,
            'interpretation': self._interpret_effect_size(cohens_d)
        }
    
    def compare_strategies(self, strategy_returns: np.ndarray, benchmark_returns: np.ndarray,
                          paired: bool = True) -> Dict[str, float]:
        """Compare two strategies statistically."""
        strategy_returns = np.array(strategy_returns)
        benchmark_returns = np.array(benchmark_returns)
        
        # Handle missing values
        if paired:
            valid_mask = ~(np.isnan(strategy_returns) | np.isnan(benchmark_returns))
            strategy_returns = strategy_returns[valid_mask]
            benchmark_returns = benchmark_returns[valid_mask]
        else:
            strategy_returns = strategy_returns[~np.isnan(strategy_returns)]
            benchmark_returns = benchmark_returns[~np.isnan(benchmark_returns)]
        
        if len(strategy_returns) == 0 or len(benchmark_returns) == 0:
            raise ValueError("No valid returns for comparison")
        
        # Statistical test
        if paired:
            differences = strategy_returns - benchmark_returns
            t_stat, p_value = stats.ttest_1samp(differences, 0)
            cohens_d = np.mean(differences) / np.std(differences, ddof=1) if np.std(differences) > 0 else 0
        else:
            t_stat, p_value = stats.ttest_ind(strategy_returns, benchmark_returns, equal_var=False)
            pooled_std = np.sqrt(((len(strategy_returns) - 1) * np.var(strategy_returns, ddof=1) + 
                                 (len(benchmark_returns) - 1) * np.var(benchmark_returns, ddof=1)) / 
                                (len(strategy_returns) + len(benchmark_returns) - 2))
            cohens_d = (np.mean(strategy_returns) - np.mean(benchmark_returns)) / pooled_std if pooled_std > 0 else 0
        
        p_value_one_tailed = p_value / 2 if t_stat > 0 else 1 - p_value / 2
        
        # Non-parametric test
        if not paired and len(strategy_returns) > 5 and len(benchmark_returns) > 5:
            u_stat, p_mann_whitney = stats.mannwhitneyu(strategy_returns, benchmark_returns, alternative='greater')
        else:
            u_stat, p_mann_whitney = None, None
        
        return {
            't_statistic': t_stat,
            'p_value': p_value_one_tailed,
            'cohens_d': cohens_d,
            'mann_whitney_p': p_mann_whitney,
            'strategy_mean': np.mean(strategy_returns),
            'benchmark_mean': np.mean(benchmark_returns),
            'significant': p_value_one_tailed < self.alpha,
            'test_type': 'paired' if paired else 'independent'
        }
    
    def sharpe_ratio_test(self, strategy_returns: np.ndarray, benchmark_returns: np.ndarray,
                         risk_free_rate: float = 0.0) -> Dict[str, float]:
        """Test if strategy Sharpe ratio significantly exceeds benchmark (Jobson-Korkie test)."""
        strategy_returns = np.array(strategy_returns)
        benchmark_returns = np.array(benchmark_returns)
        
        # Remove missing values
        valid_mask = ~(np.isnan(strategy_returns) | np.isnan(benchmark_returns))
        strategy_returns = strategy_returns[valid_mask]
        benchmark_returns = benchmark_returns[valid_mask]
        
        if len(strategy_returns) < 2:
            raise ValueError("Insufficient data for Sharpe ratio test")
        
        # Calculate excess returns and Sharpe ratios
        strategy_excess = strategy_returns - risk_free_rate
        benchmark_excess = benchmark_returns - risk_free_rate
        
        strategy_sharpe = np.mean(strategy_excess) / np.std(strategy_excess, ddof=1) if np.std(strategy_excess) > 0 else 0
        benchmark_sharpe = np.mean(benchmark_excess) / np.std(benchmark_excess, ddof=1) if np.std(benchmark_excess) > 0 else 0
        
        # Jobson-Korkie test statistic
        n = len(strategy_returns)
        sigma_s = np.std(strategy_excess, ddof=1)
        sigma_b = np.std(benchmark_excess, ddof=1)
        rho = np.corrcoef(strategy_excess, benchmark_excess)[0, 1] if sigma_s > 0 and sigma_b > 0 else 0
        
        if sigma_s > 0 and sigma_b > 0:
            numerator = strategy_sharpe - benchmark_sharpe
            denominator = np.sqrt((2 - 2 * rho) / n)
            jk_statistic = numerator / denominator if denominator > 0 else 0
            p_value = 1 - stats.norm.cdf(jk_statistic)
        else:
            jk_statistic = 0
            p_value = 1.0
        
        return {
            'strategy_sharpe': strategy_sharpe,
            'benchmark_sharpe': benchmark_sharpe,
            'jk_statistic': jk_statistic,
            'p_value': p_value,
            'correlation': rho,
            'significant': p_value < self.alpha
        }
    
    def multiple_testing_correction(self, p_values: List[float], 
                                  method: str = 'bonferroni') -> Dict[str, List]:
        """Apply multiple testing correction to p-values."""
        rejected, p_corrected, _, _ = multipletests(p_values, alpha=self.alpha, method=method)
        return {
            'p_values_corrected': p_corrected.tolist(),
            'significant_corrected': rejected.tolist(),
            'method': method
        }
    
    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"


class BootstrapAnalysis:
    """Bootstrap methods for robust statistical inference."""
    
    def __init__(self, n_bootstrap: int = 10000, random_seed: int = 42):
        """Initialize bootstrap framework."""
        self.n_bootstrap = n_bootstrap
        self.random_seed = random_seed
    
    def bootstrap_metric(self, data: np.ndarray, metric_func: Callable,
                        confidence_level: float = 0.95) -> Dict[str, float]:
        """Calculate bootstrap confidence interval for any metric."""
        data = np.array(data)[~np.isnan(data)]
        
        if len(data) == 0:
            raise ValueError("No valid data provided")
        
        # Original statistic
        original_stat = metric_func(data)
        
        # Bootstrap samples
        np.random.seed(self.random_seed)
        bootstrap_stats = []
        
        for i in range(self.n_bootstrap):
            bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
            try:
                bootstrap_stat = metric_func(bootstrap_sample)
                bootstrap_stats.append(bootstrap_stat)
            except:
                continue
        
        bootstrap_stats = np.array(bootstrap_stats)
        
        # Confidence interval
        alpha = (1 - confidence_level) / 2
        ci_lower = np.percentile(bootstrap_stats, alpha * 100)
        ci_upper = np.percentile(bootstrap_stats, (1 - alpha) * 100)
        
        return {
            'original_statistic': original_stat,
            'bootstrap_mean': np.mean(bootstrap_stats),
            'bootstrap_std': np.std(bootstrap_stats),
            'bootstrap_bias': np.mean(bootstrap_stats) - original_stat,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'confidence_level': confidence_level
        }
    
    def bootstrap_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.0,
                              confidence_level: float = 0.95) -> Dict[str, float]:
        """Bootstrap confidence interval for Sharpe ratio."""
        def sharpe_func(data):
            excess_returns = data - risk_free_rate
            return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0
        
        return self.bootstrap_metric(returns, sharpe_func, confidence_level)
    
    def bootstrap_difference(self, data1: np.ndarray, data2: np.ndarray, metric_func: Callable,
                           confidence_level: float = 0.95) -> Dict[str, float]:
        """Bootstrap confidence interval for difference between two metrics."""
        data1 = np.array(data1)[~np.isnan(data1)]
        data2 = np.array(data2)[~np.isnan(data2)]
        
        original_stat1 = metric_func(data1)
        original_stat2 = metric_func(data2)
        original_difference = original_stat1 - original_stat2
        
        # Bootstrap differences
        np.random.seed(self.random_seed)
        bootstrap_differences = []
        
        for i in range(self.n_bootstrap):
            bootstrap_sample1 = np.random.choice(data1, size=len(data1), replace=True)
            bootstrap_sample2 = np.random.choice(data2, size=len(data2), replace=True)
            
            try:
                diff = metric_func(bootstrap_sample1) - metric_func(bootstrap_sample2)
                bootstrap_differences.append(diff)
            except:
                continue
        
        bootstrap_differences = np.array(bootstrap_differences)
        
        # Confidence interval
        alpha = (1 - confidence_level) / 2
        ci_lower = np.percentile(bootstrap_differences, alpha * 100)
        ci_upper = np.percentile(bootstrap_differences, (1 - alpha) * 100)
        
        return {
            'original_difference': original_difference,
            'bootstrap_mean_difference': np.mean(bootstrap_differences),
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'significant': not (ci_lower <= 0 <= ci_upper),
            'confidence_level': confidence_level
        }


class EffectSizeAnalysis:
    """Effect size calculations for practical significance assessment."""
    
    def cohens_d(self, group1: np.ndarray, group2: np.ndarray, pooled: bool = True) -> Dict[str, float]:
        """Calculate Cohen's d effect size."""
        group1 = np.array(group1)[~np.isnan(group1)]
        group2 = np.array(group2)[~np.isnan(group2)]
        
        mean1, mean2 = np.mean(group1), np.mean(group2)
        
        if pooled:
            n1, n2 = len(group1), len(group2)
            pooled_std = np.sqrt(((n1 - 1) * np.var(group1, ddof=1) + 
                                 (n2 - 1) * np.var(group2, ddof=1)) / (n1 + n2 - 2))
            denominator = pooled_std
        else:
            denominator = np.std(group2, ddof=1)
        
        cohens_d_value = (mean1 - mean2) / denominator if denominator > 0 else 0
        
        return {
            'cohens_d': cohens_d_value,
            'interpretation': self._interpret_cohens_d(cohens_d_value),
            'mean_difference': mean1 - mean2
        }
    
    def cliff_delta(self, group1: np.ndarray, group2: np.ndarray) -> Dict[str, float]:
        """Calculate Cliff's Delta (non-parametric effect size)."""
        group1 = np.array(group1)[~np.isnan(group1)]
        group2 = np.array(group2)[~np.isnan(group2)]
        
        # Count comparisons
        greater_count = sum(1 for x1 in group1 for x2 in group2 if x1 > x2)
        less_count = sum(1 for x1 in group1 for x2 in group2 if x1 < x2)
        total_comparisons = len(group1) * len(group2)
        
        cliff_delta_value = (greater_count - less_count) / total_comparisons if total_comparisons > 0 else 0
        
        return {
            'cliff_delta': cliff_delta_value,
            'interpretation': self._interpret_cliff_delta(cliff_delta_value),
            'dominance': greater_count / total_comparisons if total_comparisons > 0 else 0
        }
    
    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d magnitude."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
    
    def _interpret_cliff_delta(self, delta: float) -> str:
        """Interpret Cliff's delta magnitude."""
        abs_delta = abs(delta)
        if abs_delta < 0.11:
            return "negligible"
        elif abs_delta < 0.28:
            return "small"
        elif abs_delta < 0.43:
            return "medium"
        else:
            return "large"


class MonteCarloSimulation:
    """Monte Carlo methods for strategy evaluation."""
    
    def __init__(self, n_simulations: int = 10000, random_seed: int = 42):
        """Initialize Monte Carlo framework."""
        self.n_simulations = n_simulations
        self.random_seed = random_seed
    
    def random_trading_simulation(self, returns_data: np.ndarray, 
                                 strategy_trades: int) -> Dict[str, np.ndarray]:
        """Simulate random trading to create null distribution."""
        returns_data = np.array(returns_data)[~np.isnan(returns_data)]
        
        np.random.seed(self.random_seed)
        simulated_returns = []
        simulated_sharpe_ratios = []
        simulated_max_drawdowns = []
        
        for _ in range(self.n_simulations):
            # Random selection of returns
            random_indices = np.random.choice(len(returns_data), size=strategy_trades, replace=True)
            random_returns = returns_data[random_indices]
            
            # Calculate metrics
            total_return = np.prod(1 + random_returns) - 1 if len(random_returns) > 0 else 0
            sharpe_ratio = np.mean(random_returns) / np.std(random_returns) if np.std(random_returns) > 0 else 0
            max_drawdown = self._calculate_max_drawdown(random_returns)
            
            simulated_returns.append(total_return)
            simulated_sharpe_ratios.append(sharpe_ratio)
            simulated_max_drawdowns.append(max_drawdown)
        
        return {
            'total_returns': np.array(simulated_returns),
            'sharpe_ratios': np.array(simulated_sharpe_ratios),
            'max_drawdowns': np.array(simulated_max_drawdowns)
        }
    
    def permutation_test(self, group1: np.ndarray, group2: np.ndarray,
                        test_statistic: Callable = None, n_permutations: int = 10000) -> Dict[str, float]:
        """Permutation test for comparing two groups."""
        if test_statistic is None:
            test_statistic = lambda x, y: np.mean(x) - np.mean(y)
        
        # Observed statistic
        observed_stat = test_statistic(group1, group2)
        
        # Permutation distribution
        combined_data = np.concatenate([group1, group2])
        n1 = len(group1)
        
        np.random.seed(self.random_seed)
        permuted_stats = []
        
        for _ in range(n_permutations):
            permuted_data = np.random.permutation(combined_data)
            perm_group1 = permuted_data[:n1]
            perm_group2 = permuted_data[n1:]
            permuted_stats.append(test_statistic(perm_group1, perm_group2))
        
        permuted_stats = np.array(permuted_stats)
        
        # Calculate p-values
        p_value_greater = np.mean(permuted_stats >= observed_stat)
        p_value_two_sided = 2 * min(p_value_greater, 1 - p_value_greater)
        
        return {
            'observed_statistic': observed_stat,
            'p_value_greater': p_value_greater,
            'p_value_two_sided': p_value_two_sided,
            'permutation_mean': np.mean(permuted_stats),
            'permutation_std': np.std(permuted_stats)
        }
    
    def strategy_significance_test(self, strategy_metric: float, 
                                  simulated_distribution: np.ndarray) -> Dict[str, float]:
        """Test if strategy metric is significantly different from random."""
        p_value_greater = np.mean(simulated_distribution >= strategy_metric)
        p_value_less = np.mean(simulated_distribution <= strategy_metric)
        percentile_rank = (np.sum(simulated_distribution <= strategy_metric) / len(simulated_distribution)) * 100
        
        z_score = ((strategy_metric - np.mean(simulated_distribution)) / 
                  np.std(simulated_distribution) if np.std(simulated_distribution) > 0 else 0)
        
        return {
            'strategy_value': strategy_metric,
            'random_mean': np.mean(simulated_distribution),
            'random_std': np.std(simulated_distribution),
            'p_value_greater': p_value_greater,
            'p_value_less': p_value_less,
            'percentile_rank': percentile_rank,
            'z_score': z_score,
            'significant_at_5pct': min(p_value_greater, p_value_less) < 0.05
        }
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown from returns."""
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return abs(np.min(drawdown))


# Factory functions for easy usage
def quick_profitability_test(returns: np.ndarray, alpha: float = 0.05) -> Dict[str, float]:
    """Quick test if strategy is profitable."""
    tester = HypothesisTests(alpha)
    return tester.test_profitability(returns)


def quick_strategy_comparison(strategy_returns: np.ndarray, benchmark_returns: np.ndarray,
                             alpha: float = 0.05) -> Dict[str, float]:
    """Quick comparison between strategy and benchmark."""
    tester = HypothesisTests(alpha)
    return tester.compare_strategies(strategy_returns, benchmark_returns)


def quick_bootstrap_sharpe(returns: np.ndarray, confidence_level: float = 0.95) -> Dict[str, float]:
    """Quick bootstrap confidence interval for Sharpe ratio."""
    bootstrap = BootstrapAnalysis()
    return bootstrap.bootstrap_sharpe_ratio(returns, confidence_level=confidence_level)


# Example usage and testing
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    strategy_returns = np.random.normal(0.001, 0.02, 100)  # Slightly positive mean
    benchmark_returns = np.random.normal(0.0005, 0.015, 100)  # Lower mean, lower vol
    
    print("=== Advanced Statistical Analysis Demo ===\n")
    
    # Test profitability
    profit_test = quick_profitability_test(strategy_returns)
    print(f"Profitability Test:")
    print(f"  Mean Return: {profit_test['mean_return']:.4f}")
    print(f"  t-statistic: {profit_test['t_statistic']:.3f}")
    print(f"  p-value: {profit_test['p_value']:.4f}")
    print(f"  Significant: {profit_test['significant']}")
    print(f"  Effect Size: {profit_test['interpretation']}\n")
    
    # Compare strategies
    comparison = quick_strategy_comparison(strategy_returns, benchmark_returns)
    print(f"Strategy Comparison:")
    print(f"  Strategy Mean: {comparison['strategy_mean']:.4f}")
    print(f"  Benchmark Mean: {comparison['benchmark_mean']:.4f}")
    print(f"  p-value: {comparison['p_value']:.4f}")
    print(f"  Significant: {comparison['significant']}\n")
    
    # Bootstrap Sharpe ratio
    sharpe_bootstrap = quick_bootstrap_sharpe(strategy_returns)
    print(f"Bootstrap Sharpe Ratio:")
    print(f"  Original: {sharpe_bootstrap['original_statistic']:.3f}")
    print(f"  95% CI: [{sharpe_bootstrap['ci_lower']:.3f}, {sharpe_bootstrap['ci_upper']:.3f}]")
    
    print("\n🎯 Advanced statistical analysis complete!")
    print("This demonstrates graduate-level quantitative finance knowledge!") 