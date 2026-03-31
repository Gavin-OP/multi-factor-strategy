"""
Weight Allocation - Different weighting schemes for portfolio construction
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from abc import ABC, abstractmethod


class WeightingScheme(ABC):
    """Abstract base class for weighting schemes"""
    
    @abstractmethod
    def calculate(
        self,
        df: pd.DataFrame,
        **kwargs
    ) -> pd.Series:
        """Calculate weights"""
        pass


class EqualWeight(WeightingScheme):
    """Equal weight allocation"""
    
    def calculate(
        self,
        df: pd.DataFrame,
        **kwargs
    ) -> pd.Series:
        n = len(df)
        return pd.Series(1.0 / n, index=df["symbol"])


class MarketCapWeight(WeightingScheme):
    """Market capitalization weighted"""
    
    def calculate(
        self,
        df: pd.DataFrame,
        market_cap_col: str = "market_cap",
        **kwargs
    ) -> pd.Series:
        if market_cap_col not in df.columns:
            logger.warning(f"Column {market_cap_col} not found, using equal weight")
            return EqualWeight().calculate(df)
        
        mc = df[market_cap_col]
        weights = mc / mc.sum()
        return weights


class SignalWeight(WeightingScheme):
    """Weight proportional to signal strength"""
    
    def calculate(
        self,
        df: pd.DataFrame,
        signal_col: str = "signal",
        **kwargs
    ) -> pd.Series:
        if signal_col not in df.columns:
            logger.warning(f"Column {signal_col} not found, using equal weight")
            return EqualWeight().calculate(df)
        
        # Ensure positive weights
        signal = df[signal_col] - df[signal_col].min() + 1e-8
        weights = signal / signal.sum()
        return weights


class RiskParityWeight(WeightingScheme):
    """Risk parity weighting (inverse volatility)"""
    
    def calculate(
        self,
        df: pd.DataFrame,
        returns_df: Optional[pd.DataFrame] = None,
        lookback: int = 20,
        **kwargs
    ) -> pd.Series:
        if returns_df is None or returns_df.empty:
            logger.warning("No returns data, using equal weight")
            return EqualWeight().calculate(df)
        
        # Calculate volatility for each stock
        vols = {}
        for symbol in df["symbol"]:
            stock_returns = returns_df[returns_df["symbol"] == symbol]["returns"]
            if len(stock_returns) >= lookback:
                vols[symbol] = stock_returns.iloc[-lookback:].std()
            else:
                vols[symbol] = stock_returns.std()
        
        # Inverse volatility weights
        inv_vols = pd.Series({k: 1/v for k, v in vols.items() if v > 0})
        weights = inv_vols / inv_vols.sum()
        
        return weights


class MeanVarianceWeight(WeightingScheme):
    """Mean-variance optimization (maximum Sharpe ratio)"""
    
    def __init__(
        self,
        risk_free_rate: float = 0.03,
        max_weight: float = 0.1,
        min_weight: float = 0.0
    ):
        self.risk_free_rate = risk_free_rate
        self.max_weight = max_weight
        self.min_weight = min_weight
    
    def calculate(
        self,
        df: pd.DataFrame,
        returns_df: Optional[pd.DataFrame] = None,
        lookback: int = 60,
        **kwargs
    ) -> pd.Series:
        if returns_df is None or returns_df.empty:
            logger.warning("No returns data, using equal weight")
            return EqualWeight().calculate(df)
        
        symbols = df["symbol"].tolist()
        n = len(symbols)
        
        # Build returns matrix
        returns_matrix = []
        for symbol in symbols:
            stock_returns = returns_df[returns_df["symbol"] == symbol]
            if len(stock_returns) >= lookback:
                returns_matrix.append(
                    stock_returns["returns"].iloc[-lookback:].values
                )
        
        if len(returns_matrix) < 2:
            return EqualWeight().calculate(df)
        
        returns_matrix = np.array(returns_matrix).T
        
        # Calculate expected returns and covariance
        expected_returns = returns_matrix.mean(axis=0) * 252
        cov_matrix = np.cov(returns_matrix.T) * 252
        
        # Optimize
        from scipy.optimize import minimize
        
        def objective(w):
            portfolio_return = np.dot(w, expected_returns)
            portfolio_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
            return -portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
        
        constraints = [
            {"type": "eq", "fun": lambda w: sum(w) - 1}
        ]
        bounds = [(self.min_weight, self.max_weight) for _ in range(n)]
        
        result = minimize(
            objective,
            x0=np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        
        weights = pd.Series(result.x, index=symbols)
        weights = weights.abs() / weights.abs().sum()  # Ensure positive and sum to 1
        
        return weights


class SmartBetaWeight(WeightingScheme):
    """
    Smart Beta weighting
    
    Combines multiple factors with specified tilts
    """
    
    def __init__(
        self,
        factor_tilts: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            factor_tilts: Dictionary mapping factor names to tilt weights
                         e.g., {"momentum": 0.3, "value": 0.3, "quality": 0.4}
        """
        self.factor_tilts = factor_tilts or {}
    
    def calculate(
        self,
        df: pd.DataFrame,
        **kwargs
    ) -> pd.Series:
        if not self.factor_tilts:
            return EqualWeight().calculate(df)
        
        # Combine factor tilts
        weights = pd.Series(0.0, index=df["symbol"])
        
        for factor, tilt in self.factor_tilts.items():
            if factor in df.columns:
                # Rank and weight
                factor_rank = df[factor].rank()
                factor_weight = factor_rank / factor_rank.sum()
                weights += tilt * factor_weight
        
        # Normalize
        if weights.sum() > 0:
            weights = weights / weights.sum()
        else:
            weights = EqualWeight().calculate(df)
        
        return weights


class WeightAllocator:
    """
    Weight Allocation Manager
    
    Features:
    - Multiple weighting schemes
    - Weight constraints
    - Turnover control
    - Position limits
    """
    
    WEIGHTING_SCHEMES = {
        "equal": EqualWeight,
        "market_cap": MarketCapWeight,
        "signal": SignalWeight,
        "risk_parity": RiskParityWeight,
        "mean_variance": MeanVarianceWeight,
        "smart_beta": SmartBetaWeight
    }
    
    def __init__(
        self,
        scheme: str = "equal",
        max_position: float = 0.05,
        min_position: float = 0.01,
        max_turnover: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize weight allocator
        
        Args:
            scheme: Weighting scheme name
            max_position: Maximum position size
            min_position: Minimum position size
            max_turnover: Maximum turnover constraint
            **kwargs: Additional parameters for weighting scheme
        """
        if scheme not in self.WEIGHTING_SCHEMES:
            raise ValueError(f"Unknown scheme: {scheme}")
        
        self.scheme_name = scheme
        self.scheme = self.WEIGHTING_SCHEMES[scheme](**kwargs)
        self.max_position = max_position
        self.min_position = min_position
        self.max_turnover = max_turnover
        
        logger.info(f"WeightAllocator initialized: scheme={scheme}")
    
    def allocate(
        self,
        df: pd.DataFrame,
        previous_weights: Optional[pd.Series] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Allocate portfolio weights
        
        Args:
            df: DataFrame with stock information
            previous_weights: Previous period weights (for turnover control)
            **kwargs: Additional arguments for weighting scheme
            
        Returns:
            DataFrame with weight column
        """
        if df.empty:
            return df
        
        # Calculate raw weights
        weights = self.scheme.calculate(df, **kwargs)
        
        # Apply constraints
        weights = self._apply_constraints(weights, previous_weights)
        
        # Create result DataFrame
        result = df.copy()
        result["weight"] = result["symbol"].map(weights)
        result["weight"] = result["weight"].fillna(0)
        
        # Normalize to sum to 1
        if result["weight"].sum() > 0:
            result["weight"] = result["weight"] / result["weight"].sum()
        
        logger.info(f"Allocated weights for {len(result)} positions")
        
        return result[["symbol", "weight"]]
    
    def _apply_constraints(
        self,
        weights: pd.Series,
        previous_weights: Optional[pd.Series] = None
    ) -> pd.Series:
        """Apply weight constraints"""
        # Max position constraint
        weights = weights.clip(upper=self.max_position)
        
        # Min position constraint (remove small positions)
        weights[weights < self.min_position] = 0
        
        # Normalize
        if weights.sum() > 0:
            weights = weights / weights.sum()
        
        # Turnover constraint
        if previous_weights is not None and self.max_turnover is not None:
            weights = self._apply_turnover_constraint(weights, previous_weights)
        
        return weights
    
    def _apply_turnover_constraint(
        self,
        new_weights: pd.Series,
        old_weights: pd.Series
    ) -> pd.Series:
        """Apply turnover constraint"""
        # Align indices
        all_symbols = new_weights.index.union(old_weights.index)
        new_weights = new_weights.reindex(all_symbols, fill_value=0)
        old_weights = old_weights.reindex(all_symbols, fill_value=0)
        
        # Calculate turnover
        turnover = (new_weights - old_weights).abs().sum() / 2
        
        if turnover <= self.max_turnover:
            return new_weights
        
        # Scale down changes
        scale = self.max_turnover / turnover
        adjusted_weights = old_weights + scale * (new_weights - old_weights)
        
        # Re-normalize
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        return adjusted_weights
    
    def get_weight_summary(
        self,
        weights: pd.DataFrame
    ) -> Dict[str, Any]:
        """Get weight summary statistics"""
        return {
            "n_positions": (weights["weight"] > 0).sum(),
            "max_weight": weights["weight"].max(),
            "min_weight": weights[weights["weight"] > 0]["weight"].min(),
            "mean_weight": weights[weights["weight"] > 0]["weight"].mean(),
            "weight_concentration": (weights["weight"] ** 2).sum(),  # HHI
            "effective_n": 1 / (weights["weight"] ** 2).sum()  # Effective number of positions
        }
