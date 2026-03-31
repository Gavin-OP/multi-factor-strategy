"""
Factor Library - Collection of volume-price factors
Inspired by WorldQuant 101 Alpha factors

All factors are purely based on price and volume data,
following professional quantitative research standards.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from scipy import stats
from src.factors.base import FactorBase, FactorRegistry


def rolling_rank(series: pd.Series, window: int) -> pd.Series:
    """Rank of last value in rolling window"""
    return series.rolling(window).apply(lambda x: stats.rankdata(x)[-1])


def rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    """Z-score in rolling window"""
    return (series - series.rolling(window).mean()) / series.rolling(window).std()


def ts_rank(series: pd.Series, window: int) -> pd.Series:
    """Time series rank (rank of last value in window)"""
    return series.rolling(window).apply(lambda x: pd.Series(x).rank().iloc[-1])


def ts_delta(series: pd.Series, period: int) -> pd.Series:
    """Change over period"""
    return series.diff(period)


def ts_delay(series: pd.Series, period: int) -> pd.Series:
    """Delayed series"""
    return series.shift(period)


def ts_mean(series: pd.Series, window: int) -> pd.Series:
    """Rolling mean"""
    return series.rolling(window).mean()


def ts_std(series: pd.Series, window: int) -> pd.Series:
    """Rolling standard deviation"""
    return series.rolling(window).std()


def ts_max(series: pd.Series, window: int) -> pd.Series:
    """Rolling max"""
    return series.rolling(window).max()


def ts_min(series: pd.Series, window: int) -> pd.Series:
    """Rolling min"""
    return series.rolling(window).min()


def ts_argmax(series: pd.Series, window: int) -> pd.Series:
    """Position of max in rolling window"""
    return series.rolling(window).apply(np.argmax)


def ts_argmin(series: pd.Series, window: int) -> pd.Series:
    """Position of min in rolling window"""
    return series.rolling(window).apply(np.argmin)


def ts_corr(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """Rolling correlation"""
    return x.rolling(window).corr(y)


def ts_cov(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """Rolling covariance"""
    return x.rolling(window).cov(y)


def scale(series: pd.Series) -> pd.Series:
    """Scale series to sum to 1"""
    return series / series.sum()


def rank(series: pd.Series) -> pd.Series:
    """Cross-sectional rank"""
    return series.rank()


def delay(series: pd.Series, d: int) -> pd.Series:
    """Delay by d periods"""
    return series.shift(d)


# ============================================================
# Volume-Price Factors (WorldQuant 101 Style)
# ============================================================

class Factor001(FactorBase):
    """
    Factor 001: Price-Volume Correlation
    
    (-1 * CORR(RANK(DELTA(LOG(VOLUME), 1)), RANK(((CLOSE - OPEN) / OPEN)), 6))
    
    Interpretation: 
    - Negative correlation between volume changes and price changes
    - Captures abnormal volume-price relationship
    """
    
    def __init__(self):
        super().__init__("Factor001")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        df["log_volume"] = np.log(df["volume"].replace(0, np.nan))
        df["delta_log_volume"] = df.groupby("symbol")["log_volume"].diff(1)
        df["price_change"] = (df["close"] - df["open"]) / df["open"]
        
        # Rolling correlation
        df["factor_value"] = df.groupby("symbol").apply(
            lambda g: -ts_corr(
                g["delta_log_volume"].rank(),
                g["price_change"].rank(),
                6
            )
        ).reset_index(level=0, drop=True)
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor001",
            "category": "volume_price",
            "description": "Price-Volume Correlation",
            "lookback_period": 6,
            "frequency": "daily"
        }


class Factor002(FactorBase):
    """
    Factor 002: Intraday Momentum
    
    (-1 * DELTA((((CLOSE - LOW) - (HIGH - CLOSE)) / (HIGH - LOW)), 1))
    
    Interpretation:
    - Captures intraday price momentum
    - Negative delta indicates momentum reversal
    """
    
    def __init__(self):
        super().__init__("Factor002")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        df["intraday_momentum"] = (
            (df["close"] - df["low"]) - (df["high"] - df["close"])
        ) / (df["high"] - df["low"] + 1e-8)
        
        df["factor_value"] = df.groupby("symbol")["intraday_momentum"].diff(1) * -1
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor002",
            "category": "momentum",
            "description": "Intraday Momentum Change",
            "lookback_period": 2,
            "frequency": "daily"
        }


class Factor003(FactorBase):
    """
    Factor 003: Volume Rank Sum
    
    (-1 * SUM(RANK(CORR(RANK(HIGH), RANK(VOLUME), 3)), 3))
    
    Interpretation:
    - High-volume at high prices indicates potential reversal
    - Sum smooths the signal
    """
    
    def __init__(self):
        super().__init__("Factor003")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Rolling correlation between high and volume ranks
        df["high_rank"] = df.groupby("symbol")["high"].transform(lambda x: x.rank())
        df["volume_rank"] = df.groupby("symbol")["volume"].transform(lambda x: x.rank())
        
        df["corr_rank"] = df.groupby("symbol").apply(
            lambda g: ts_corr(g["high_rank"], g["volume_rank"], 3)
        ).reset_index(level=0, drop=True)
        
        df["corr_rank_rank"] = df.groupby("date")["corr_rank"].transform(
            lambda x: x.rank()
        )
        
        df["factor_value"] = -df.groupby("symbol")["corr_rank_rank"].transform(
            lambda x: x.rolling(3).sum()
        )
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor003",
            "category": "volume_price",
            "description": "Volume Rank Sum",
            "lookback_period": 5,
            "frequency": "daily"
        }


class Factor004(FactorBase):
    """
    Factor 004: Volume Oscillator
    
    (-1 * TS_RANK(RANK(LOW), 4) * TS_RANK(RANK(VOLUME), 4))
    
    Interpretation:
    - Low rank times volume rank
    - Captures volume climax at low prices
    """
    
    def __init__(self):
        super().__init__("Factor004")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        df["low_rank"] = df.groupby("date")["low"].transform(lambda x: x.rank())
        df["volume_rank"] = df.groupby("date")["volume"].transform(lambda x: x.rank())
        
        df["low_ts_rank"] = df.groupby("symbol")["low_rank"].transform(
            lambda x: ts_rank(x, 4)
        )
        df["volume_ts_rank"] = df.groupby("symbol")["volume_rank"].transform(
            lambda x: ts_rank(x, 4)
        )
        
        df["factor_value"] = -df["low_ts_rank"] * df["volume_ts_rank"]
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor004",
            "category": "volume_price",
            "description": "Volume Oscillator",
            "lookback_period": 4,
            "frequency": "daily"
        }


class Factor005(FactorBase):
    """
    Factor 005: Volume-Weighted Price Momentum
    
    (RANK((OPEN - SUM(VWAP, 10)) / COUNT(CLOSE < VWAP, 10)))
    
    Interpretation:
    - Captures price deviation from VWAP
    - Weighted by frequency of closing below VWAP
    """
    
    def __init__(self):
        super().__init__("Factor005")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Calculate VWAP
        df["vwap"] = df["amount"] / df["volume"]
        df["vwap"] = df["vwap"].fillna(df["close"])
        
        # Sum of VWAP over 10 days
        df["vwap_sum"] = df.groupby("symbol")["vwap"].transform(
            lambda x: x.rolling(10).sum()
        )
        
        # Count of close < vwap
        df["close_lt_vwap"] = (df["close"] < df["vwap"]).astype(int)
        df["count_lt"] = df.groupby("symbol")["close_lt_vwap"].transform(
            lambda x: x.rolling(10).sum()
        )
        
        df["factor_value"] = (df["open"] - df["vwap_sum"]) / (df["count_lt"] + 1)
        df["factor_value"] = df.groupby("date")["factor_value"].transform(
            lambda x: x.rank()
        )
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor005",
            "category": "momentum",
            "description": "Volume-Weighted Price Momentum",
            "lookback_period": 10,
            "frequency": "daily"
        }


class Factor006(FactorBase):
    """
    Factor 006: Price Momentum with Volume Confirmation
    
    (-1 * CORR(OPEN, VOLUME, 10))
    
    Interpretation:
    - Negative correlation between open price and volume
    - Captures unusual volume at specific price levels
    """
    
    def __init__(self):
        super().__init__("Factor006")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        df["factor_value"] = df.groupby("symbol").apply(
            lambda g: -ts_corr(g["open"], g["volume"], 10)
        ).reset_index(level=0, drop=True)
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor006",
            "category": "volume_price",
            "description": "Open-Volume Correlation",
            "lookback_period": 10,
            "frequency": "daily"
        }


class Factor007(FactorBase):
    """
    Factor 007: Volume Breakout
    
    Advices: Volume surge indicates price movement direction
    
    ((RANK(TS_MAX(DELTA(CLOSE, 1), 5)) * RANK(DELTA(VOLUME, 1) / VOLUME)) * -1)
    """
    
    def __init__(self):
        super().__init__("Factor007")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Price change
        df["delta_close"] = df.groupby("symbol")["close"].diff(1)
        df["max_delta_close"] = df.groupby("symbol")["delta_close"].transform(
            lambda x: ts_max(x, 5)
        )
        
        # Volume change
        df["delta_volume"] = df.groupby("symbol")["volume"].diff(1)
        df["volume_change"] = df["delta_volume"] / df["volume"]
        
        df["factor_value"] = -(
            df.groupby("date")["max_delta_close"].transform(lambda x: x.rank()) *
            df.groupby("date")["volume_change"].transform(lambda x: x.rank())
        )
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor007",
            "category": "volume_price",
            "description": "Volume Breakout",
            "lookback_period": 5,
            "frequency": "daily"
        }


class Factor008(FactorBase):
    """
    Factor 008: Close Momentum
    
    (-1 * RANK(DELTA(CLOSE, 7) * (1 - RANK(DECAY(DELTA(VOLUME, 7), 7)))))
    
    Simplified: Price momentum adjusted by volume decay
    """
    
    def __init__(self):
        super().__init__("Factor008")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Price momentum
        df["delta_close_7"] = df.groupby("symbol")["close"].diff(7)
        
        # Volume change with decay
        df["delta_volume_7"] = df.groupby("symbol")["volume"].diff(7)
        df["volume_decay"] = df.groupby("symbol")["delta_volume_7"].transform(
            lambda x: x.rolling(7, min_periods=1).apply(
                lambda w: (w * np.exp(-0.5 * np.arange(len(w))[::-1])).sum()
            )
        )
        
        df["factor_value"] = -df.groupby("date")["delta_close_7"].transform(
            lambda x: x.rank()
        ) * (1 - df.groupby("date")["volume_decay"].transform(lambda x: x.rank()))
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor008",
            "category": "momentum",
            "description": "Close Momentum with Volume Decay",
            "lookback_period": 14,
            "frequency": "daily"
        }


class Factor009(FactorBase):
    """
    Factor 009: Volume Ratio
    
    ((RANK(VOLUME / TS_MEAN(VOLUME, 20))) * RANK(-1 * DELTA(CLOSE, 7)))
    
    Interpretation:
    - High volume relative to average times price decline
    - Captures volume climax during pullbacks
    """
    
    def __init__(self):
        super().__init__("Factor009")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Volume ratio
        df["avg_volume"] = df.groupby("symbol")["volume"].transform(
            lambda x: ts_mean(x, 20)
        )
        df["volume_ratio"] = df["volume"] / df["avg_volume"]
        
        # Price change
        df["delta_close"] = df.groupby("symbol")["close"].diff(7)
        
        df["factor_value"] = (
            df.groupby("date")["volume_ratio"].transform(lambda x: x.rank()) *
            df.groupby("date")["delta_close"].transform(lambda x: (-x).rank())
        )
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor009",
            "category": "volume_price",
            "description": "Volume Ratio with Price Change",
            "lookback_period": 20,
            "frequency": "daily"
        }


class Factor010(FactorBase):
    """
    Factor 010: Returns Correlation
    
    RANK(DELTA(CLOSE, 3) / CLOSE) * RANK(DELTA(VOLUME, 3) / VOLUME)
    
    Interpretation:
    - Correlation between price and volume changes
    - Captures coordinated movements
    """
    
    def __init__(self):
        super().__init__("Factor010")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Price returns
        df["price_ret"] = df.groupby("symbol")["close"].diff(3) / df["close"]
        
        # Volume change
        df["volume_change"] = df.groupby("symbol")["volume"].diff(3) / df["volume"]
        
        df["factor_value"] = (
            df.groupby("date")["price_ret"].transform(lambda x: x.rank()) *
            df.groupby("date")["volume_change"].transform(lambda x: x.rank())
        )
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Factor010",
            "category": "volume_price",
            "description": "Price-Volume Correlation",
            "lookback_period": 3,
            "frequency": "daily"
        }


# ============================================================
# Additional Professional Factors
# ============================================================

class VolumePriceFactor(FactorBase):
    """
    Volume Price Momentum Factor
    
    Combines volume trends with price momentum
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        super().__init__("VolumePriceMomentum")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Volume trend
        df["volume_ma"] = df.groupby("symbol")["volume"].transform(
            lambda x: x.rolling(self.lookback).mean()
        )
        df["volume_trend"] = df["volume"] / df["volume_ma"]
        
        # Price momentum
        df["price_momentum"] = df.groupby("symbol")["close"].transform(
            lambda x: x.pct_change(self.lookback)
        )
        
        # Combined factor
        df["factor_value"] = df["volume_trend"] * df["price_momentum"]
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "VolumePriceMomentum",
            "category": "volume_price",
            "description": "Volume Price Momentum",
            "lookback_period": self.lookback,
            "frequency": "daily"
        }


class MomentumFactor(FactorBase):
    """
    Classic Momentum Factor
    
    Price momentum with adjustment for volatility
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        super().__init__("Momentum")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Momentum (past return)
        df["momentum"] = df.groupby("symbol")["close"].transform(
            lambda x: x.shift(1) / x.shift(self.lookback + 1) - 1
        )
        
        # Volatility adjustment
        df["volatility"] = df.groupby("symbol")["close"].transform(
            lambda x: x.pct_change().rolling(self.lookback).std()
        )
        
        # Risk-adjusted momentum
        df["factor_value"] = df["momentum"] / (df["volatility"] + 1e-8)
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Momentum",
            "category": "momentum",
            "description": "Risk-Adjusted Momentum",
            "lookback_period": self.lookback,
            "frequency": "daily"
        }


class VolatilityFactor(FactorBase):
    """
    Volatility Factor
    
    Low volatility anomaly - lower volatility stocks tend to outperform
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        super().__init__("Volatility")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Historical volatility
        df["returns"] = df.groupby("symbol")["close"].pct_change()
        df["volatility"] = df.groupby("symbol")["returns"].transform(
            lambda x: x.rolling(self.lookback).std() * np.sqrt(252)
        )
        
        # Inverse volatility (low vol anomaly)
        df["factor_value"] = -df["volatility"]  # Negative for low vol preference
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Volatility",
            "category": "risk",
            "description": "Low Volatility Factor",
            "lookback_period": self.lookback,
            "frequency": "daily"
        }


class LiquidityFactor(FactorBase):
    """
    Liquidity Factor
    
    Amihud illiquidity measure
    """
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        super().__init__("Liquidity")
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.validate(df):
            return pd.DataFrame()
        
        df = df.copy()
        
        # Daily illiquidity: |return| / volume
        df["returns"] = df.groupby("symbol")["close"].pct_change()
        df["illiq_daily"] = df["returns"].abs() / (df["volume"] + 1)
        
        # Average illiquidity
        df["factor_value"] = df.groupby("symbol")["illiq_daily"].transform(
            lambda x: x.rolling(self.lookback).mean()
        )
        
        return df[["symbol", "date", "factor_value"]]
    
    def _init_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Liquidity",
            "category": "liquidity",
            "description": "Amihud Illiquidity Factor",
            "lookback_period": self.lookback,
            "frequency": "daily"
        }


# ============================================================
# Factor Registration
# ============================================================

def get_all_factors() -> list:
    """Get all factor instances"""
    factors = [
        Factor001(),
        Factor002(),
        Factor003(),
        Factor004(),
        Factor005(),
        Factor006(),
        Factor007(),
        Factor008(),
        Factor009(),
        Factor010(),
        VolumePriceFactor(),
        MomentumFactor(),
        VolatilityFactor(),
        LiquidityFactor(),
    ]
    
    # Register all factors
    for factor in factors:
        FactorRegistry.register(factor)
    
    return factors


# Initialize factors when module is loaded
ALL_FACTORS = get_all_factors()
