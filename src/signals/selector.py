"""
Stock Selector - Select stocks based on signals
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from abc import ABC, abstractmethod


class SelectionStrategy(ABC):
    """Abstract base class for selection strategies"""
    
    @abstractmethod
    def select(
        self,
        signal_df: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """Select stocks based on signals"""
        pass


class TopNSelection(SelectionStrategy):
    """Select top N stocks by signal"""
    
    def __init__(self, n_stocks: int = 50):
        self.n_stocks = n_stocks
    
    def select(
        self,
        signal_df: pd.DataFrame,
        date: Optional[str] = None
    ) -> pd.DataFrame:
        """Select top N stocks"""
        if date:
            df = signal_df[signal_df["date"] == date].copy()
        else:
            df = signal_df.copy()
        
        # Rank by signal
        df = df.sort_values("signal", ascending=False)
        
        # Select top N
        df = df.head(self.n_stocks)
        df["selected"] = True
        
        return df[["symbol", "date", "signal", "selected"]]


class QuantileSelection(SelectionStrategy):
    """Select stocks in top quantile"""
    
    def __init__(self, quantile: float = 0.2):
        self.quantile = quantile
    
    def select(
        self,
        signal_df: pd.DataFrame,
        date: Optional[str] = None
    ) -> pd.DataFrame:
        """Select stocks in top quantile"""
        df = signal_df.copy()
        
        if date:
            df = df[df["date"] == date]
        
        # Calculate quantile threshold
        df["threshold"] = df.groupby("date")["signal"].transform(
            lambda x: x.quantile(1 - self.quantile)
        )
        
        # Select stocks above threshold
        df["selected"] = df["signal"] >= df["threshold"]
        
        return df[["symbol", "date", "signal", "selected"]]


class ThresholdSelection(SelectionStrategy):
    """Select stocks above signal threshold"""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
    
    def select(
        self,
        signal_df: pd.DataFrame,
        date: Optional[str] = None
    ) -> pd.DataFrame:
        """Select stocks above threshold"""
        df = signal_df.copy()
        
        if date:
            df = df[df["date"] == date]
        
        df["selected"] = df["signal"] >= self.threshold
        
        return df[["symbol", "date", "signal", "selected"]]


class StockSelector:
    """
    Stock Selection Manager
    
    Features:
    - Multiple selection strategies
    - Signal filtering
    - Industry/sector constraints
    - Turnover control
    """
    
    def __init__(
        self,
        strategy: str = "top_n",
        n_stocks: int = 50,
        quantile: float = 0.2,
        threshold: float = 0.5
    ):
        """
        Initialize stock selector
        
        Args:
            strategy: Selection strategy ("top_n", "quantile", "threshold")
            n_stocks: Number of stocks for top_n strategy
            quantile: Quantile for quantile strategy
            threshold: Threshold for threshold strategy
        """
        self.strategy = self._create_strategy(
            strategy, n_stocks, quantile, threshold
        )
        
        logger.info(f"StockSelector initialized with {strategy} strategy")
    
    def _create_strategy(
        self,
        strategy: str,
        n_stocks: int,
        quantile: float,
        threshold: float
    ) -> SelectionStrategy:
        """Create selection strategy"""
        if strategy == "top_n":
            return TopNSelection(n_stocks)
        elif strategy == "quantile":
            return QuantileSelection(quantile)
        elif strategy == "threshold":
            return ThresholdSelection(threshold)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def select(
        self,
        signal_df: pd.DataFrame,
        date: Optional[str] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Select stocks based on signals
        
        Args:
            signal_df: DataFrame with signal column
            date: Specific date (None for all dates)
            filter_conditions: Additional filter conditions
            
        Returns:
            DataFrame with selected stocks
        """
        # Apply filters
        if filter_conditions:
            signal_df = self._apply_filters(signal_df, filter_conditions)
        
        # Select stocks
        selected_df = self.strategy.select(signal_df, date)
        
        logger.info(
            f"Selected {selected_df['selected'].sum()} stocks "
            f"from {len(signal_df)} candidates"
        )
        
        return selected_df
    
    def _apply_filters(
        self,
        df: pd.DataFrame,
        conditions: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply filter conditions"""
        for col, condition in conditions.items():
            if col not in df.columns:
                continue
            
            if isinstance(condition, dict):
                # Range condition
                if "min" in condition:
                    df = df[df[col] >= condition["min"]]
                if "max" in condition:
                    df = df[df[col] <= condition["max"]]
            elif isinstance(condition, list):
                # In-list condition
                df = df[df[col].isin(condition)]
            else:
                # Equality condition
                df = df[df[col] == condition]
        
        return df
    
    def apply_turnover_constraint(
        self,
        current_selection: pd.DataFrame,
        previous_selection: pd.DataFrame,
        max_turnover: float = 0.3
    ) -> pd.DataFrame:
        """
        Apply turnover constraint
        
        Args:
            current_selection: Current selected stocks
            previous_selection: Previously selected stocks
            max_turnover: Maximum turnover ratio
            
        Returns:
            Adjusted selection
        """
        current_stocks = set(current_selection[current_selection["selected"]]["symbol"])
        previous_stocks = set(previous_selection[previous_selection["selected"]]["symbol"])
        
        # Calculate current turnover
        if len(previous_stocks) > 0:
            turnover = 1 - len(current_stocks & previous_stocks) / len(previous_stocks)
            
            if turnover > max_turnover:
                # Need to reduce turnover
                # Keep some stocks from previous selection
                n_keep = int(len(previous_stocks) * (1 - max_turnover))
                
                # Keep top performing previous stocks
                kept_stocks = previous_selection.nlargest(
                    n_keep, "signal"
                )["symbol"].tolist()
                
                # Combine with current selection
                current_stocks = kept_stocks + list(current_stocks)[:len(current_stocks) - n_keep]
                
                # Update selection
                current_selection = current_selection.copy()
                current_selection["selected"] = current_selection["symbol"].isin(current_stocks)
        
        return current_selection
    
    def get_selection_summary(
        self,
        selected_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Get selection summary statistics"""
        selected = selected_df[selected_df["selected"]]
        
        return {
            "n_selected": len(selected),
            "signal_mean": selected["signal"].mean(),
            "signal_std": selected["signal"].std(),
            "signal_min": selected["signal"].min(),
            "signal_max": selected["signal"].max(),
            "dates": selected["date"].unique().tolist()
        }
