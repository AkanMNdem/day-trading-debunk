"""
Advanced Statistical Analysis for Trading Strategy Research.

This module provides graduate-level statistical analysis tools to rigorously 
evaluate trading strategy performance. Includes hypothesis testing, bootstrap 
analysis, effect size calculations, and Monte Carlo simulations.

Perfect for demonstrating quantitative finance knowledge in interviews.
"""

from .advanced_stats import (
    HypothesisTests,
    BootstrapAnalysis,
    EffectSizeAnalysis,
    MonteCarloSimulation,
    quick_profitability_test,
    quick_strategy_comparison,
    quick_bootstrap_sharpe
)

__all__ = [
    'HypothesisTests',
    'BootstrapAnalysis', 
    'EffectSizeAnalysis',
    'MonteCarloSimulation',
    'quick_profitability_test',
    'quick_strategy_comparison',
    'quick_bootstrap_sharpe'
] 