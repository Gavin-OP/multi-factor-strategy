"""
Signal Generator - Generate trading signals from factors
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from dataclasses import dataclass

from src.signals.combiner import FactorCombiner
from src.signals.selector import StockSelector


@dataclass
class SignalConfig:
    """Signal generation configuration"""
    combination_method: str = "icir_weight"
    selection_strategy: str = "top_n"
    n_stocks: int = 50
    rebalance_freq: int = 5
    neutralize_industry: bool = False
    standardize: bool = True


class SignalGenerator:
    """
    Signal Generation Pipeline
    
    Features:
    - Factor combination
    - Signal generation
    - Stock selection
    - Signal validation
    - Performance tracking
    
    Pipeline:
    1. Load/Calculate factors
    2. Combine factors into signal
    3. Select stocks based on signal
    4. Generate trading signals
    """
    
    def __init__(
        self,
        config: Optional[SignalConfig] = None,
        combiner: Optional[FactorCombiner] = None,
        selector: Optional[StockSelector] = None
    ):
        """
        Initialize signal generator
        
        Args:
            config: Signal configuration
            combiner: Factor combiner instance
            selector: Stock selector instance
        """
        self.config = config or SignalConfig()
        self.combiner = combiner or FactorCombiner(self.config.combination_method)
        self.selector = selector or StockSelector(
            strategy=self.config.selection_strategy,
            n_stocks=self.config.n_stocks
        )
        
        self._is_fitted = False
        self._signal_history: List[pd.DataFrame] = []
        
        logger.info(f"SignalGenerator initialized: {self.config}")
    
    def fit(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame,
        factor_names: Optional[List[str]] = None
    ):
        """
        Fit the signal generator
        
        Args:
            factor_df: DataFrame with factor values
            returns_df: DataFrame with forward returns
            factor_names: Factor names to use
        """
        logger.info("Fitting signal generator...")
        
        # Fit factor combiner
        self.combiner.fit(factor_df, returns_df, factor_names)
        
        self._is_fitted = True
        logger.info("Signal generator fitted successfully")
    
    def generate(
        self,
        factor_df: pd.DataFrame,
        returns_df: Optional[pd.DataFrame] = None,
        fit: bool = False,
        factor_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Generate trading signals
        
        Args:
            factor_df: DataFrame with factor values
            returns_df: DataFrame with forward returns (for fitting)
            fit: Whether to fit the model
            factor_names: Factor names to use
            
        Returns:
            DataFrame with signals and stock selection
        """
        # Fit if needed
        if fit and returns_df is not None:
            self.fit(factor_df, returns_df, factor_names)
        
        if not self._is_fitted:
            # Use default equal weights
            self.combiner.weights = self.combiner._equal_weight(
                factor_names or [col for col in factor_df.columns 
                                if col not in ["symbol", "date"]]
            )
            self._is_fitted = True
        
        # Combine factors
        signal_df = self.combiner.transform(factor_df, factor_names)
        
        # Standardize if configured
        if self.config.standardize:
            signal_df["signal"] = signal_df.groupby("date")["signal"].transform(
                lambda x: (x - x.mean()) / x.std() if x.std() > 0 else x - x.mean()
            )
        
        # Select stocks
        selected_df = self.selector.select(signal_df)
        
        # Merge signals and selection
        result = signal_df.merge(
            selected_df[["symbol", "date", "selected"]],
            on=["symbol", "date"],
            how="left"
        )
        result["selected"] = result["selected"].fillna(False)
        
        logger.info(f"Generated signals for {result['date'].nunique()} dates")
        
        return result
    
    def generate_rebalance_schedule(
        self,
        signal_df: pd.DataFrame,
        freq: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate rebalance schedule
        
        Args:
            signal_df: DataFrame with signals
            freq: Rebalance frequency in days
            
        Returns:
            DataFrame with rebalance dates
        """
        freq = freq or self.config.rebalance_freq
        
        dates = sorted(signal_df["date"].unique())
        rebalance_dates = dates[::freq]
        
        schedule = pd.DataFrame({
            "date": dates,
            "rebalance": [d in rebalance_dates for d in dates]
        })
        
        logger.info(f"Generated {len(rebalance_dates)} rebalance dates")
        
        return schedule
    
    def calculate_signal_strength(
        self,
        signal_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate signal strength metrics
        
        Args:
            signal_df: DataFrame with signals
            
        Returns:
            DataFrame with signal strength metrics
        """
        df = signal_df.copy()
        
        # Signal rank
        df["signal_rank"] = df.groupby("date")["signal"].transform(
            lambda x: x.rank(pct=True)
        )
        
        # Signal z-score
        df["signal_zscore"] = df.groupby("date")["signal"].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )
        
        # Signal percentile
        df["signal_percentile"] = df.groupby("date")["signal"].transform(
            lambda x: x.rank() / len(x)
        )
        
        return df
    
    def get_signal_summary(
        self,
        signal_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Get signal summary statistics"""
        selected = signal_df[signal_df["selected"]]
        
        return {
            "n_dates": signal_df["date"].nunique(),
            "n_symbols": signal_df["symbol"].nunique(),
            "avg_selected_per_date": selected.groupby("date").size().mean(),
            "signal_mean": signal_df["signal"].mean(),
            "signal_std": signal_df["signal"].std(),
            "signal_skew": signal_df["signal"].skew(),
            "signal_kurt": signal_df["signal"].kurtosis(),
            "combination_method": self.config.combination_method,
            "factor_weights": self.combiner.get_weights()
        }
    
    def save_signals(
        self,
        signal_df: pd.DataFrame,
        path: str
    ):
        """Save signals to file"""
        signal_df.to_csv(path, index=False)
        logger.info(f"Saved signals to {path}")
    
    def load_signals(
        self,
        path: str
    ) -> pd.DataFrame:
        """Load signals from file"""
        signal_df = pd.read_csv(path)
        signal_df["date"] = pd.to_datetime(signal_df["date"])
        logger.info(f"Loaded signals from {path}")
        return signal_df
