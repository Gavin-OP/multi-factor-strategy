"""
Factor Combiner - Combine multiple factors into a single signal

Methods:
- Equal weight
- ICIR weight
- Maximum Sharpe weight
- Machine learning based
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from scipy.optimize import minimize


class FactorCombiner:
    """
    Factor combination methods
    
    Features:
    - Multiple weighting schemes
    - Factor correlation consideration
    - Dynamic weighting
    - Regularization
    """
    
    def __init__(self, method: str = "icir_weight"):
        """
        Initialize factor combiner
        
        Args:
            method: Combination method
                - "equal_weight": Equal weight for all factors
                - "icir_weight": Weight by ICIR
                - "ic_weight": Weight by IC mean
                - "max_sharpe": Maximum Sharpe ratio optimization
                - "pca": PCA-based combination
        """
        self.method = method
        self.weights: Dict[str, float] = {}
    
    def fit(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        factor_names: Optional[List[str]] = None
    ):
        """
        Fit factor weights
        
        Args:
            factor_df: DataFrame with factor values
            returns_df: DataFrame with forward returns
            factor_names: List of factor names to use
        """
        if factor_names is None:
            factor_names = [col for col in factor_df.columns 
                           if col not in ["symbol", "date"]]
        
        if self.method == "equal_weight":
            self.weights = self._equal_weight(factor_names)
        
        elif self.method == "icir_weight":
            self.weights = self._icir_weight(factor_df, returns_df, factor_names)
        
        elif self.method == "ic_weight":
            self.weights = self._ic_weight(factor_df, returns_df, factor_names)
        
        elif self.method == "max_sharpe":
            self.weights = self._max_sharpe_weight(factor_df, returns_df, factor_names)
        
        elif self.method == "pca":
            self.weights = self._pca_weight(factor_df, factor_names)
        
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        logger.info(f"Factor weights fitted using {self.method}: {self.weights}")
    
    def _equal_weight(self, factor_names: List[str]) -> Dict[str, float]:
        """Equal weight combination"""
        weight = 1.0 / len(factor_names)
        return {name: weight for name in factor_names}
    
    def _icir_weight(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        factor_names: List[str]
    ) -> Dict[str, float]:
        """ICIR-based weighting"""
        from scipy import stats
        
        icirs = {}
        
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        for factor in factor_names:
            # Calculate IC time series
            ics = merged.groupby("date").apply(
                lambda g: stats.spearmanr(g[factor], g["forward_return"])[0]
            )
            
            ic_mean = ics.mean()
            ic_std = ics.std()
            icir = ic_mean / ic_std if ic_std > 0 else 0
            
            # Use absolute ICIR
            icirs[factor] = abs(icir)
        
        # Normalize weights
        total = sum(icirs.values())
        if total > 0:
            return {k: v / total for k, v in icirs.items()}
        return self._equal_weight(factor_names)
    
    def _ic_weight(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        factor_names: List[str]
    ) -> Dict[str, float]:
        """IC-based weighting"""
        from scipy import stats
        
        ics = {}
        
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        for factor in factor_names:
            ic = merged.groupby("date").apply(
                lambda g: stats.spearmanr(g[factor], g["forward_return"])[0]
            ).mean()
            ics[factor] = abs(ic)
        
        total = sum(ics.values())
        if total > 0:
            return {k: v / total for k, v in ics.items()}
        return self._equal_weight(factor_names)
    
    def _max_sharpe_weight(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        factor_names: List[str]
    ) -> Dict[str, float]:
        """Maximum Sharpe ratio optimization"""
        from scipy import stats
        
        # Calculate factor returns (IC series)
        merged = pd.merge(
            factor_df,
            returns_df[["symbol", "date", "forward_return"]],
            on=["symbol", "date"],
            how="inner"
        )
        
        ic_series = {}
        for factor in factor_names:
            ic_series[factor] = merged.groupby("date").apply(
                lambda g: stats.spearmanr(g[factor], g["forward_return"])[0]
            )
        
        ic_df = pd.DataFrame(ic_series).fillna(0)
        
        # Optimize
        n = len(factor_names)
        
        def objective(w):
            portfolio_return = ic_df.dot(w).mean() * 252
            portfolio_vol = ic_df.dot(w).std() * np.sqrt(252)
            return -portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
        
        # Constraints
        constraints = [
            {"type": "eq", "fun": lambda w: sum(w) - 1}  # Sum to 1
        ]
        bounds = [(0, 1) for _ in range(n)]  # Long only
        
        result = minimize(
            objective,
            x0=np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        
        weights = result.x
        return {name: w for name, w in zip(factor_names, weights)}
    
    def _pca_weight(
        self,
        factor_df: pd.DataFrame,
        factor_names: List[str]
    ) -> Dict[str, float]:
        """PCA-based combination"""
        from sklearn.decomposition import PCA
        
        # Prepare data
        factor_matrix = factor_df[factor_names].fillna(0)
        
        # Standardize
        factor_matrix = (factor_matrix - factor_matrix.mean()) / factor_matrix.std()
        
        # PCA
        pca = PCA(n_components=1)
        pca.fit(factor_matrix)
        
        # First principal component loadings as weights
        loadings = pca.components_[0]
        loadings = np.abs(loadings)  # Use absolute values
        loadings = loadings / loadings.sum()  # Normalize
        
        return {name: w for name, w in zip(factor_names, loadings)}
    
    def transform(
        self,
        factor_df: pd.DataFrame,
        factor_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Transform factor values into combined signal
        
        Args:
            factor_df: DataFrame with factor values
            factor_names: Factor names to use (None for all in weights)
            
        Returns:
            DataFrame with signal column
        """
        if not self.weights:
            raise ValueError("Weights not fitted. Call fit() first.")
        
        factor_names = factor_names or list(self.weights.keys())
        
        df = factor_df.copy()
        df["signal"] = 0
        
        for factor in factor_names:
            if factor in self.weights and factor in df.columns:
                df["signal"] += df[factor].fillna(0) * self.weights[factor]
        
        return df[["symbol", "date", "signal"]]
    
    def get_weights(self) -> Dict[str, float]:
        """Get current weights"""
        return self.weights.copy()
