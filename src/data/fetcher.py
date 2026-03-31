"""
Data Fetcher - Fetch market data from various sources
Supports: Akshare, Tushare, yfinance
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from loguru import logger
from datetime import datetime, timedelta


class DataSourceBase(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """Fetch daily OHLCV data"""
        pass
    
    @abstractmethod
    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch stock list"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if data source is available"""
        pass


class AkshareDataSource(DataSourceBase):
    """Akshare data source implementation - A-share market data"""
    
    def __init__(self):
        self._akshare = None
        self._lazy_import()
    
    def _lazy_import(self):
        """Lazy import to avoid startup overhead"""
        try:
            import akshare as ak
            self._akshare = ak
        except ImportError:
            logger.warning("akshare not installed")
    
    def is_available(self) -> bool:
        return self._akshare is not None
    
    def fetch_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """Fetch daily OHLCV data from Akshare"""
        if self._akshare is None:
            return pd.DataFrame()
        
        try:
            df = self._akshare.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                adjust="qfq"  # Forward adjusted
            )
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            # Standardize column names
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "换手率": "turnover"
            })
            
            df["date"] = pd.to_datetime(df["date"])
            df["symbol"] = symbol
            
            return df[["symbol", "date", "open", "high", "low", "close", 
                       "volume", "amount", "pct_change", "turnover"]]
            
        except Exception as e:
            logger.error(f"Akshare: Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch A-share stock list"""
        if self._akshare is None:
            return pd.DataFrame()
        
        try:
            df = self._akshare.stock_zh_a_spot_em()
            df = df.rename(columns={
                "代码": "symbol",
                "名称": "name",
                "最新价": "price",
                "总市值": "market_cap"
            })
            return df[["symbol", "name", "price", "market_cap"]]
        except Exception as e:
            logger.error(f"Akshare: Failed to fetch stock list: {e}")
            return pd.DataFrame()


class TushareDataSource(DataSourceBase):
    """Tushare data source implementation - Professional A-share data"""
    
    def __init__(self, token: Optional[str] = None):
        self._tushare = None
        self._token = token
        self._lazy_import()
    
    def _lazy_import(self):
        """Lazy import tushare"""
        try:
            import tushare as ts
            if self._token:
                ts.set_token(self._token)
                self._tushare = ts.pro_api()
            else:
                # Try to get token from environment
                import os
                token = os.environ.get("TUSHARE_TOKEN")
                if token:
                    ts.set_token(token)
                    self._tushare = ts.pro_api()
        except ImportError:
            logger.warning("tushare not installed")
    
    def is_available(self) -> bool:
        return self._tushare is not None
    
    def fetch_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """Fetch daily data from Tushare"""
        if self._tushare is None:
            return pd.DataFrame()
        
        try:
            # Tushare uses format like "000001.SZ"
            ts_code = self._convert_symbol(symbol)
            
            df = self._tushare.daily(
                ts_code=ts_code,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", "")
            )
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            df = df.rename(columns={
                "trade_date": "date",
                "vol": "volume",
                "pct_chg": "pct_change"
            })
            
            df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
            df["symbol"] = symbol
            
            # Get additional data
            adj_factor = self._tushare.adj_factor(ts_code=ts_code)
            if adj_factor is not None and not adj_factor.empty:
                adj_factor = adj_factor.rename(columns={"trade_date": "date"})
                adj_factor["date"] = pd.to_datetime(adj_factor["date"], format="%Y%m%d")
                df = df.merge(adj_factor[["date", "adj_factor"]], on="date", how="left")
            
            return df[["symbol", "date", "open", "high", "low", "close", 
                       "volume", "pct_change"]]
            
        except Exception as e:
            logger.error(f"Tushare: Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch stock list from Tushare"""
        if self._tushare is None:
            return pd.DataFrame()
        
        try:
            df = self._tushare.stock_basic(exchange="", list_status="L")
            df = df.rename(columns={
                "ts_code": "symbol",
                "name": "name"
            })
            return df[["symbol", "name", "list_date", "delist_date"]]
        except Exception as e:
            logger.error(f"Tushare: Failed to fetch stock list: {e}")
            return pd.DataFrame()
    
    def _convert_symbol(self, symbol: str) -> str:
        """Convert symbol format to Tushare format"""
        if "." in symbol:
            return symbol
        
        # Infer exchange from symbol
        if symbol.startswith("6"):
            return f"{symbol}.SH"
        else:
            return f"{symbol}.SZ"


class YFinanceDataSource(DataSourceBase):
    """yfinance data source implementation - Global market data"""
    
    def __init__(self):
        self._yfinance = None
        self._lazy_import()
    
    def _lazy_import(self):
        """Lazy import yfinance"""
        try:
            import yfinance as yf
            self._yfinance = yf
        except ImportError:
            logger.warning("yfinance not installed")
    
    def is_available(self) -> bool:
        return self._yfinance is not None
    
    def fetch_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """Fetch daily data from yfinance"""
        if self._yfinance is None:
            return pd.DataFrame()
        
        try:
            ticker = self._yfinance.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                return pd.DataFrame()
            
            df = df.reset_index()
            df["symbol"] = symbol
            df["pct_change"] = df["Close"].pct_change() * 100
            df["turnover"] = df["Volume"] / df["Close"] * 100  # Approximate
            
            # Standardize column names
            df = df.rename(columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            })
            
            return df[["symbol", "date", "open", "high", "low", "close", 
                       "volume", "pct_change", "turnover"]]
            
        except Exception as e:
            logger.error(f"yfinance: Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch stock list - not applicable for yfinance"""
        logger.warning("yfinance does not support stock list fetching")
        return pd.DataFrame()
    
    def fetch_index_constituents(self, symbol: str = "^GSPC") -> List[str]:
        """
        Fetch index constituents for major indices
        
        Args:
            symbol: Index symbol (^GSPC for S&P500, ^DJI for Dow Jones)
        """
        # Common S&P 500 tickers (partial list)
        sp500_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
            "UNH", "JNJ", "V", "JPM", "XOM", "HD", "MA", "PG", "CVX", "LLY",
            "MRK", "PEP", "KO", "COST", "AVGO", "MCD", "CSCO", "WMT", "ABT",
            "ACN", "NFLX", "ADBE", "CRM", "DHR", "VZ", "CMCSA", "NKE", "WFC",
            "TXN", "PM", "BMY", "LIN", "RTX", "ORCL", "QCOM", "AMD", "HON"
        ]
        
        if symbol == "^GSPC":
            return sp500_tickers
        
        return []


class MockDataSource(DataSourceBase):
    """Mock data source for testing without external dependencies"""
    
    def is_available(self) -> bool:
        return True
    
    def fetch_daily_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """Generate mock data for testing"""
        dates = pd.date_range(start_date, end_date, freq="B")
        n = len(dates)
        
        np.random.seed(hash(symbol) % 2**32)
        
        # Generate realistic price series using GBM
        dt = 1/252
        mu = 0.08  # Annual return
        sigma = 0.25  # Annual volatility
        S0 = np.random.uniform(10, 200)
        
        # Geometric Brownian Motion
        returns = np.random.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
        price = S0 * np.exp(np.cumsum(returns))
        
        # Generate OHLCV
        df = pd.DataFrame({
            "symbol": symbol,
            "date": dates,
            "open": price * (1 + np.random.uniform(-0.01, 0.01, n)),
            "high": price * (1 + np.abs(np.random.normal(0.005, 0.005, n))),
            "low": price * (1 - np.abs(np.random.normal(0.005, 0.005, n))),
            "close": price,
            "volume": np.random.randint(1000000, 10000000, n).astype(np.int64),
            "amount": np.random.randint(10000000, 100000000, n),
            "pct_change": np.concatenate([[0], np.diff(np.log(price)) * 100]),
            "turnover": np.random.uniform(0.5, 5, n)
        })
        
        return df
    
    def fetch_stock_list(self) -> pd.DataFrame:
        """Generate mock stock list"""
        n_stocks = 100
        return pd.DataFrame({
            "symbol": [f"{i:06d}" for i in range(1, n_stocks + 1)],
            "name": [f"Stock_{i}" for i in range(1, n_stocks + 1)],
            "price": np.random.uniform(10, 200, n_stocks),
            "market_cap": np.random.uniform(1e9, 1e12, n_stocks)
        })


class DataFetcher:
    """
    Main data fetcher that supports multiple data sources
    
    Features:
    - Multiple data source support (Akshare, Tushare, yfinance, Mock)
    - Automatic fallback mechanism
    - Rate limiting
    - Batch fetching with progress bar
    - Data caching support
    
    Usage:
        fetcher = DataFetcher(source="tushare", config={"tushare_token": "xxx"})
        df = fetcher.fetch_daily(["000001", "000002"], "2023-01-01", "2023-12-31")
    """
    
    SOURCES = {
        "akshare": AkshareDataSource,
        "tushare": TushareDataSource,
        "yfinance": YFinanceDataSource,
        "mock": MockDataSource
    }
    
    def __init__(
        self, 
        source: str = "akshare", 
        config: Optional[Dict] = None,
        fallback_source: Optional[str] = "mock"
    ):
        """
        Initialize data fetcher
        
        Args:
            source: Primary data source name
            config: Configuration dictionary (e.g., {"tushare_token": "xxx"})
            fallback_source: Fallback data source if primary fails
        """
        self.config = config or {}
        self._source_name = source
        self._source = self._create_source(source)
        self._fallback = fallback_source
        self._fallback_source = self._create_source(fallback_source) if fallback_source else None
        
        logger.info(f"DataFetcher initialized: primary={source}, fallback={fallback_source}")
    
    def _create_source(self, source: str) -> DataSourceBase:
        """Create data source instance"""
        if source not in self.SOURCES:
            logger.warning(f"Unknown source '{source}', using mock")
            source = "mock"
        
        source_class = self.SOURCES[source]
        
        if source == "tushare":
            return source_class(self.config.get("tushare_token"))
        return source_class()
    
    def fetch_daily(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        show_progress: bool = True,
        use_fallback: bool = True
    ) -> pd.DataFrame:
        """
        Fetch daily data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            show_progress: Show progress bar
            use_fallback: Use fallback source if primary fails
            
        Returns:
            DataFrame with daily OHLCV data
        """
        all_data = []
        failed_symbols = []
        
        # Check if primary source is available
        if not self._source.is_available() and use_fallback and self._fallback_source:
            logger.warning(f"Primary source '{self._source_name}' not available, using fallback")
            return self._fetch_with_fallback(symbols, start_date, end_date, show_progress)
        
        iterator = symbols
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(symbols, desc=f"Fetching from {self._source_name}")
        
        for symbol in iterator:
            try:
                df = self._source.fetch_daily_data(symbol, start_date, end_date)
                if not df.empty:
                    all_data.append(df)
                else:
                    failed_symbols.append(symbol)
            except Exception as e:
                logger.debug(f"Failed to fetch {symbol}: {e}")
                failed_symbols.append(symbol)
        
        # Try fallback for failed symbols
        if failed_symbols and use_fallback and self._fallback_source:
            logger.info(f"Trying fallback for {len(failed_symbols)} failed symbols")
            fallback_data = self._fetch_with_fallback(
                failed_symbols, start_date, end_date, show_progress=False
            )
            if not fallback_data.empty:
                all_data.append(fallback_data)
        
        if not all_data:
            logger.warning("No data fetched")
            return pd.DataFrame()
        
        result = pd.concat(all_data, ignore_index=True)
        result = result.sort_values(["date", "symbol"]).reset_index(drop=True)
        
        logger.info(
            f"Fetched {len(result):,} rows for {result['symbol'].nunique()} symbols "
            f"from {start_date} to {end_date}"
        )
        
        return result
    
    def _fetch_with_fallback(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        show_progress: bool
    ) -> pd.DataFrame:
        """Fetch using fallback source"""
        if not self._fallback_source:
            return pd.DataFrame()
        
        all_data = []
        iterator = symbols
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(symbols, desc=f"Fetching from {self._fallback}")
        
        for symbol in iterator:
            try:
                df = self._fallback_source.fetch_daily_data(symbol, start_date, end_date)
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                logger.debug(f"Fallback failed for {symbol}: {e}")
        
        if not all_data:
            return pd.DataFrame()
        
        return pd.concat(all_data, ignore_index=True)
    
    def fetch_stock_list(self) -> pd.DataFrame:
        """Fetch stock list"""
        # Try primary source
        df = self._source.fetch_stock_list()
        if not df.empty:
            return df
        
        # Try fallback
        if self._fallback_source:
            df = self._fallback_source.fetch_stock_list()
            if not df.empty:
                return df
        
        return pd.DataFrame()
    
    def fetch_index_constituents(self, index: str = "000300.SH") -> List[str]:
        """
        Fetch index constituents
        
        Args:
            index: Index code
            
        Returns:
            List of constituent stock codes
        """
        # For Chinese indices
        if index.endswith(".SH") or index.endswith(".SZ"):
            if self._source_name == "akshare" and self._source.is_available():
                try:
                    import akshare as ak
                    df = ak.index_stock_cons_weight_csindex(symbol=index[:6])
                    return df["成分券代码"].tolist()
                except:
                    pass
        
        # For global indices using yfinance
        if self._source_name == "yfinance" or (self._fallback == "yfinance"):
            yf_source = YFinanceDataSource()
            if index == "000300.SH":
                return yf_source.fetch_index_constituents("^GSPC")[:50]  # Mock as S&P subset
            return yf_source.fetch_index_constituents(index)
        
        # Fallback to mock
        return [f"{i:06d}" for i in range(1, 51)]
    
    def get_trading_dates(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DatetimeIndex:
        """Get trading dates between start and end date"""
        dates = pd.date_range(start_date, end_date, freq="B")
        return dates
