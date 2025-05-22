import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_metrics(equity_curve, trades=None, risk_free_rate=0.0):
    """
    Calculate performance metrics from an equity curve.

    Parameters:
    -----------
    equity_curve : pd.Series
        Series of portfolio equity values over time
    trades : pd.DataFrame, optional
        DataFrame of trade details
    risk_free_rate : float
        Annual risk-free rate (e.g., 0.02 for 2%)

    Returns:
    --------
    dict
        Dictionary of performance metrics
    """
    # Convert to pandas Series if it's not already
    if not isinstance(equity_curve, pd.Series):
        equity_curve = pd.Series(equity_curve)

    # Calculate returns
    returns = equity_curve.pct_change().dropna()

    # Calculate metrics
    total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1

    # Annualized return
    if isinstance(equity_curve.index, pd.DatetimeIndex):
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
    else:
        # Handle non-datetime indices
        days = 0
        print("Warning: equity_curve index is not a DatetimeIndex. Cannot calculate annualized return.")
    if days > 0:
        years = days / 365
        annualized_return = (1 + total_return) ** (1 / years) - 1
    else:
        # For intraday data
        annualized_return = total_return  # Not annualized for very short periods

    # Volatility
    if len(returns) > 1:
        daily_volatility = returns.std()
        annualized_volatility = daily_volatility * np.sqrt(252)
    else:
        daily_volatility = 0
        annualized_volatility = 0

    # Sharpe ratio
    if annualized_volatility > 0:
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    else:
        sharpe_ratio = 0

    # Max drawdown
    cumulative_returns = (1 + returns).cumprod()
    drawdown = 1 - cumulative_returns / cumulative_returns.cummax()
    max_drawdown = drawdown.max()

    # Trade metrics
    if trades is not None and len(trades) > 0:
        winning_trades = trades[trades['pnl'] > 0]
        losing_trades = trades[trades['pnl'] < 0]

        win_rate = len(winning_trades) / len(trades) if len(trades) > 0 else 0
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else float('inf')
    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        profit_factor = 0

    return {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'daily_volatility': daily_volatility,
        'annualized_volatility': annualized_volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'number_of_trades': len(trades) if trades is not None else 0
    }

def plot_equity_curve(equity_curve, title="Equity Curve"):
    """Plot the equity curve."""
    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.grid(True, alpha=0.3)
    return plt.gcf()

def plot_drawdown(equity_curve, title="Drawdown"):
    """Plot the drawdown curve."""
    if not isinstance(equity_curve, pd.Series):
        equity_curve = pd.Series(equity_curve)

    returns = equity_curve.pct_change().dropna()
    cumulative_returns = (1 + returns).cumprod()
    drawdown = 1 - cumulative_returns / cumulative_returns.cummax()

    plt.figure(figsize=(12, 6))
    plt.plot(drawdown)
    plt.fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.grid(True, alpha=0.3)
    return plt.gcf()
