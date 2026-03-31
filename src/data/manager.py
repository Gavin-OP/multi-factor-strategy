"""
Data Manager - Unified data management interface
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from datetime import datetime
from pathlib import Path

from src.data.fetcher import DataFetcher
from src.data.storage import DataStorage
from src.data.cache import DataCache


class DataManager:
    """
    Unified data management interface
    
    Features:
    - Single interface for all data operations
    - Automatic caching
    - Data validation
    - Data alignment
    - Missing data handling
    
    Usage:
        dm = DataManager(config_path="config/config.ini")
        df = dm.get_daily_data(["000001", "000002"], "2023-01-01", "2023-12-31")
    """
    
    def __init__(
        self,
        config_path: str = "config/config.ini",
        data_source: str = "akshare",
        use_cache: bool = True
    ):
        """
        Initialize data manager
        
        Args:
            config_path: Path to configuration file
            data_source: Data source name
            use_cache: Enable caching
        """
        import configparser
        
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding="utf-8")
        
        # Initialize components
        self.fetcher = DataFetcher(
            source=data_source,
            config={"tushare_token": self.config.get("data_source", "tushare_token", fallback="")}
        )
        
        self.storage = DataStorage(config_path)
        
        cache_dir = self.config.get("data_source", "cache_dir", fallback="./outputs/cache")
        self.cache = DataCache(cache_dir) if use_cache else None
        
        self.use_cache = use_cache
        
        logger.info(f"DataManager initialized: source={data_source}, cache={use_cache}")
    
    def get_daily_data(
        self,
        symbols: Optional[List[str]] = None,
        start_date: str = "2020-01-01",
        end_date: str = "2023-12-31",
        use_cache: bool = True,
        save_to_db: bool = False,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Get daily price data
        
        Args:
            symbols: List of stock symbols (None for all active stocks)
            start_date: Start date
            end_date: End date
            use_cache: Use cached data if available
            save_to_db: Save fetched data to database
            show_progress: Show progress bar
            
        Returns:
            DataFrame with daily OHLCV data
        """
        cache_key = f"daily:{','.join(symbols or [])}:{start_date}:{end_date}"
        
        # Try cache
        if use_cache and self.use_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Using cached data: {len(cached)} rows")
                return cached
        
        # Try database
        if symbols and len(symbols) <= 100:
            df = self.storage.load_daily_data(
                start_date=start_date,
                end_date=end_date
            )
            
            if not df.empty:
                df = df[df["symbol"].isin(symbols)]
                if len(df) > 0:
                    logger.info(f"Loaded from database: {len(df)} rows")
                    return df
        
        # Fetch from data source
        if symbols is None:
            symbols = self.get_stock_list()["symbol"].tolist()[:50]
        
        df = self.fetcher.fetch_daily(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            show_progress=show_progress
        )
        
        if df.empty:
            logger.warning("No data fetched")
            return df
        
        # Validate data
        df = self._validate_data(df)
        
        # Save to database
        if save_to_db:
            self.storage.save_daily_data(df)
        
        # Cache data
        if use_cache and self.use_cache and self.cache:
            self.cache.set(cache_key, df, ttl=86400)
        
        return df
    
    def get_stock_list(self, use_cache: bool = True) -> pd.DataFrame:
        """Get stock list"""
        cache_key = "stock_list"
        
        if use_cache and self.use_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        df = self.fetcher.fetch_stock_list()
        
        if not df.empty and self.use_cache and self.cache:
            self.cache.set(cache_key, df, ttl=86400)
        
        return df
    
    def get_index_constituents(self, index: str = "000300.SH") -> List[str]:
        """Get index constituents"""
        return self.fetcher.fetch_index_constituents(index)
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean data"""
        if df.empty:
            return df
        
        # Remove duplicates
        df = df.drop_duplicates(subset=["symbol", "date"])
        
        # Remove rows with missing essential data
        essential_cols = ["open", "high", "low", "close", "volume"]
        df = df.dropna(subset=essential_cols)
        
        # Remove rows with zero or negative prices
        df = df[(df["open"] > 0) & (df["high"] > 0) & 
                (df["low"] > 0) & (df["close"] > 0)]
        
        # Remove rows with zero volume (optional)
        # df = df[df["volume"] > 0]
        
        # Ensure high >= low
        df = df[df["high"] >= df["low"]]
        
        # Sort
        df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
        
        return df
    
    def align_data(
        self,
        df: pd.DataFrame,
        freq: str = "D"
    ) -> pd.DataFrame:
        """
        Align data to common trading dates
        
        Args:
            df: DataFrame with date column
            freq: Frequency ("D" for daily, "W" for weekly)
        """
        # Get all trading dates
        all_dates = df["date"].unique()
        all_dates = pd.DatetimeIndex(all_dates).sort_values()
        
        # Get all symbols
        all_symbols = df["symbol"].unique()
        
        # Create complete date-symbol combinations
        multi_index = pd.MultiIndex.from_product(
            [all_symbols, all_dates],
            names=["symbol", "date"]
        )
        
        # Reindex
        df = df.set_index(["symbol", "date"])
        df = df.reindex(multi_index)
        
        # Forward fill missing values
        df = df.groupby(level=0).ffill()
        
        return df.reset_index()
    
    def calculate_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived features"""
        df = df.copy()
        
        # VWAP
        df["vwap"] = (df["amount"] / df["volume"]).replace([np.inf, -np.inf], np.nan)
        
        # Price range
        df["price_range"] = (df["high"] - df["low"]) / df["close"]
        
        # Overnight return
        df["overnight_return"] = df.groupby("symbol")["open"].pct_change()
        
        # Intraday return
        df["intraday_return"] = (df["close"] - df["open"]) / df["open"]
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get data summary statistics"""
        return {
            "n_symbols": df["symbol"].nunique(),
            "n_dates": df["date"].nunique(),
            "date_range": f"{df['date'].min()} to {df['date'].max()}",
            "n_rows": len(df),
            "missing_pct": df.isnull().mean().mean() * 100,
            "memory_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
    
    def close(self):
        """Close connections"""
        self.storage.engine.dispose()
        logger.info("DataManager closed")
