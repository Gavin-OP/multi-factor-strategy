"""
Factor Base - Abstract base class for all factors
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from loguru import logger


class FactorBase(ABC):
    """
    Abstract base class for all factors
    
    All factors must implement:
    - calculate(): Calculate factor values
    - get_metadata(): Return factor metadata
    
    Optional methods:
    - validate(): Validate factor values
    - transform(): Transform factor values (e.g., standardization)
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize factor
        
        Args:
            name: Factor name (defaults to class name)
        """
        self.name = name or self.__class__.__name__
        self._metadata = self._init_metadata()
    
    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate factor values
        
        Args:
            df: DataFrame with OHLCV data (columns: symbol, date, open, high, low, close, volume, etc.)
            
        Returns:
            DataFrame with columns: symbol, date, factor_value
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get factor metadata
        
        Returns:
            Dictionary with factor metadata
        """
        return self._metadata
    
    def _init_metadata(self) -> Dict[str, Any]:
        """Initialize default metadata (override in subclass)"""
        return {
            "name": self.name,
            "category": "unknown",
            "description": "",
            "lookback_period": None,
            "frequency": "daily",
            "author": "",
            "version": "1.0"
        }
    
    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validate input data has required columns
        
        Args:
            df: Input DataFrame
            
        Returns:
            True if valid
        """
        required_cols = ["symbol", "date", "close", "volume"]
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            logger.warning(f"{self.name}: Missing required columns: {missing}")
            return False
        
        return True
    
    def transform(
        self,
        df: pd.DataFrame,
        method: str = "standardize",
        **kwargs
    ) -> pd.DataFrame:
        """
        Transform factor values
        
        Args:
            df: DataFrame with factor_value column
            method: Transformation method
                - "standardize": Z-score standardization
                - "rank": Rank transformation
                - "quantile": Quantile transformation
                - "winsorize": Winsorization
            
        Returns:
            DataFrame with transformed factor values
        """
        if "factor_value" not in df.columns:
            return df
        
        df = df.copy()
        
        if method == "standardize":
            # Cross-sectional standardization
            df["factor_value"] = df.groupby("date")["factor_value"].transform(
                lambda x: (x - x.mean()) / x.std() if x.std() > 0 else x - x.mean()
            )
        
        elif method == "rank":
            # Cross-sectional rank
            df["factor_value"] = df.groupby("date")["factor_value"].transform(
                lambda x: x.rank(pct=True)
            )
        
        elif method == "quantile":
            n_bins = kwargs.get("n_bins", 10)
            df["factor_value"] = df.groupby("date")["factor_value"].transform(
                lambda x: pd.qcut(x, n_bins, labels=False, duplicates="drop") / n_bins
            )
        
        elif method == "winsorize":
            threshold = kwargs.get("threshold", 3)
            df["factor_value"] = df.groupby("date")["factor_value"].transform(
                lambda x: self._winsorize(x, threshold)
            )
        
        return df
    
    @staticmethod
    def _winsorize(series: pd.Series, threshold: float = 3) -> pd.Series:
        """Winsorize using MAD (Median Absolute Deviation)"""
        median = series.median()
        mad = np.median(np.abs(series - median))
        
        if mad == 0:
            return series
        
        upper = median + threshold * mad * 1.4826  # Scale factor for normal distribution
        lower = median - threshold * mad * 1.4826
        
        return series.clip(lower, upper)
    
    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        """Make factor callable"""
        return self.calculate(df)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"


class FactorRegistry:
    """
    Factor registry for managing all available factors
    
    Features:
    - Register factors
    - List available factors
    - Get factor by name
    """
    
    _factors: Dict[str, FactorBase] = {}
    
    @classmethod
    def register(cls, factor: FactorBase):
        """Register a factor"""
        cls._factors[factor.name] = factor
        logger.debug(f"Registered factor: {factor.name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[FactorBase]:
        """Get factor by name"""
        return cls._factors.get(name)
    
    @classmethod
    def list(cls) -> List[str]:
        """List all registered factors"""
        return list(cls._factors.keys())
    
    @classmethod
    def get_all(cls) -> Dict[str, FactorBase]:
        """Get all registered factors"""
        return cls._factors.copy()
    
    @classmethod
    def clear(cls):
        """Clear all registered factors"""
        cls._factors.clear()
