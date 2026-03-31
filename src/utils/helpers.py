"""
Helper Functions - Common utility functions for data processing
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, List
from loguru import logger


def calculate_returns(
    prices: pd.Series,
    method: str = "simple"
) -> pd.Series:
    """
    Calculate returns from price series
    
    Args:
        prices: Price series
        method: Return calculation method ("simple", "log")
        
    Returns:
        Returns series
    """
    if method == "simple":
        return prices.pct_change()
    elif method == "log":
        return np.log(prices / prices.shift(1))
    else:
        raise ValueError(f"Unknown method: {method}")


def align_dataframes(
    dfs: List[pd.DataFrame],
    on: str = "date",
    how: str = "inner"
) -> List[pd.DataFrame]:
    """
    Align multiple DataFrames on a common column
    
    Args:
        dfs: List of DataFrames to align
        on: Column to align on
        how: Join method ("inner", "outer", "left", "right")
        
    Returns:
        List of aligned DataFrames
    """
    if len(dfs) < 2:
        return dfs
    
    # Get common index
    common_index = dfs[0][on]
    for df in dfs[1:]:
        common_index = pd.Index(
            set(common_index) & set(df[on]) if how == "inner"
            else set(common_index) | set(df[on]) if how == "outer"
            else set(common_index)
        )
    
    # Filter all DataFrames
    return [df[df[on].isin(common_index)] for df in dfs]


def winsorize(
    series: pd.Series,
    limits: tuple = (0.01, 0.01),
    method: str = "quantile"
) -> pd.Series:
    """
    Winsorize series to remove outliers
    
    Args:
        series: Input series
        limits: Lower and upper limits
        method: Method ("quantile" or "mad")
        
    Returns:
        Winsorized series
    """
    series = series.copy()
    
    if method == "quantile":
        lower = series.quantile(limits[0])
        upper = series.quantile(1 - limits[1])
        series = series.clip(lower, upper)
    
    elif method == "mad":
        median = series.median()
        mad = np.median(np.abs(series - median))
        threshold = 3 * mad * 1.4826
        lower = median - threshold
        upper = median + threshold
        series = series.clip(lower, upper)
    
    return series


def standardize(
    series: pd.Series,
    method: str = "zscore"
) -> pd.Series:
    """
    Standardize series
    
    Args:
        series: Input series
        method: Standardization method ("zscore", "minmax", "rank")
        
    Returns:
        Standardized series
    """
    if method == "zscore":
        return (series - series.mean()) / series.std()
    
    elif method == "minmax":
        return (series - series.min()) / (series.max() - series.min())
    
    elif method == "rank":
        return series.rank(pct=True)
    
    else:
        raise ValueError(f"Unknown method: {method}")


def calculate_rolling_metric(
    series: pd.Series,
    window: int,
    metric: str = "mean"
) -> pd.Series:
    """
    Calculate rolling metric
    
    Args:
        series: Input series
        window: Rolling window
        metric: Metric to calculate ("mean", "std", "max", "min", "median")
        
    Returns:
        Rolling metric series
    """
    rolling = series.rolling(window)
    
    if metric == "mean":
        return rolling.mean()
    elif metric == "std":
        return rolling.std()
    elif metric == "max":
        return rolling.max()
    elif metric == "min":
        return rolling.min()
    elif metric == "median":
        return rolling.median()
    else:
        raise ValueError(f"Unknown metric: {metric}")


def resample_returns(
    returns: pd.Series,
    freq: str = "M"
) -> pd.Series:
    """
    Resample returns to lower frequency
    
    Args:
        returns: Daily returns series
        freq: Target frequency ("W", "M", "Q", "Y")
        
    Returns:
        Resampled returns
    """
    return (1 + returns).resample(freq).prod() - 1


def calculate_downside_deviation(
    returns: pd.Series,
    target: float = 0
) -> float:
    """
    Calculate downside deviation
    
    Args:
        returns: Returns series
        target: Target return
        
    Returns:
        Downside deviation
    """
    downside = returns[returns < target]
    if len(downside) == 0:
        return 0
    
    return np.sqrt(((downside - target) ** 2).mean())


def calculate_max_drawdown_duration(
    equity_curve: pd.Series
) -> int:
    """
    Calculate maximum drawdown duration in days
    
    Args:
        equity_curve: Equity curve series
        
    Returns:
        Maximum drawdown duration
    """
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    
    in_drawdown = False
    duration = 0
    max_duration = 0
    
    for dd in drawdown:
        if dd < 0:
            if not in_drawdown:
                in_drawdown = True
                duration = 0
            duration += 1
        else:
            if in_drawdown:
                max_duration = max(max_duration, duration)
                in_drawdown = False
    
    return max_duration
