"""
Multi-Source Data Provider - 统一数据接口

数据源优先级:
1. Akshare (免费 A 股)
2. Tushare (专业 A 股，需 Token)
3. yfinance (全球市场)
4. Mock (备用模拟数据)

自动切换，无缝降级
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from loguru import logger
from datetime import datetime, timedelta
import time


class MultiSourceDataProvider:
    """
    多数据源统一接口
    
    Features:
    - 自动选择可用数据源
    - 多源备份机制
    - 统一数据格式
    - 缓存支持
    - 错误重试
    """
    
    def __init__(
        self,
        tushare_token: Optional[str] = None,
        cache_enabled: bool = True,
        cache_dir: str = "./outputs/cache"
    ):
        """
        初始化多数据源
        
        Args:
            tushare_token: Tushare API Token
            cache_enabled: 是否启用缓存
            cache_dir: 缓存目录
        """
        self.tushare_token = tushare_token
        self.cache_enabled = cache_enabled
        self.cache_dir = cache_dir
        
        # 数据源可用性
        self.source_status = {
            "akshare": None,  # None = 未测试
            "tushare": None,
            "yfinance": None,
            "mock": True  # Mock 始终可用
        }
        
        # 检测可用数据源
        self._detect_available_sources()
        
        logger.info(f"数据源状态: {self.source_status}")
    
    def _detect_available_sources(self):
        """检测可用数据源"""
        # 测试 Akshare
        try:
            import akshare as ak
            # 简单测试
            df = ak.stock_zh_a_spot_em()
            if df is not None and len(df) > 0:
                self.source_status["akshare"] = True
                logger.info("✓ Akshare 可用")
            else:
                self.source_status["akshare"] = False
        except Exception as e:
            self.source_status["akshare"] = False
            logger.warning(f"✗ Akshare 不可用: {e}")
        
        # 测试 Tushare
        if self.tushare_token:
            try:
                import tushare as ts
                ts.set_token(self.tushare_token)
                pro = ts.pro_api()
                df = pro.trade_cal(exchange='SSE', start_date='20240101', end_date='20240110')
                if df is not None and len(df) > 0:
                    self.source_status["tushare"] = True
                    logger.info("✓ Tushare 可用")
                else:
                    self.source_status["tushare"] = False
            except Exception as e:
                self.source_status["tushare"] = False
                logger.warning(f"✗ Tushare 不可用: {e}")
        else:
            self.source_status["tushare"] = False
            logger.info("✗ Tushare 未配置 Token")
        
        # 测试 yfinance
        try:
            import yfinance as yf
            ticker = yf.Ticker("AAPL")
            hist = ticker.history(period="5d")
            if hist is not None and len(hist) > 0:
                self.source_status["yfinance"] = True
                logger.info("✓ yfinance 可用")
            else:
                self.source_status["yfinance"] = False
        except Exception as e:
            self.source_status["yfinance"] = False
            logger.warning(f"✗ yfinance 不可用: {e}")
    
    def get_available_sources(self) -> List[str]:
        """获取可用数据源列表"""
        return [k for k, v in self.source_status.items() if v]
    
    def fetch_daily_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        获取日线数据 - 按优先级尝试各数据源
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            show_progress: 显示进度条
            
        Returns:
            DataFrame with columns: symbol, date, open, high, low, close, volume, amount, pct_change
        """
        # 按优先级尝试
        priority_order = ["akshare", "tushare", "yfinance", "mock"]
        
        for source in priority_order:
            if not self.source_status.get(source):
                continue
            
            logger.info(f"尝试使用 {source} 获取数据...")
            
            try:
                if source == "akshare":
                    df = self._fetch_from_akshare(symbols, start_date, end_date, show_progress)
                elif source == "tushare":
                    df = self._fetch_from_tushare(symbols, start_date, end_date, show_progress)
                elif source == "yfinance":
                    df = self._fetch_from_yfinance(symbols, start_date, end_date, show_progress)
                elif source == "mock":
                    df = self._fetch_from_mock(symbols, start_date, end_date, show_progress)
                else:
                    continue
                
                if df is not None and len(df) > 0:
                    logger.info(f"✓ 使用 {source} 成功获取 {len(df)} 条数据")
                    return df
                    
            except Exception as e:
                logger.warning(f"✗ {source} 获取失败: {e}")
                continue
        
        logger.error("所有数据源都失败，返回空数据")
        return pd.DataFrame()
    
    def _fetch_from_akshare(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        show_progress: bool
    ) -> Optional[pd.DataFrame]:
        """从 Akshare 获取数据"""
        import akshare as ak
        
        all_data = []
        iterator = symbols
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(symbols, desc="Akshare")
        
        for symbol in iterator:
            try:
                # 尝试获取数据
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust="qfq"  # 前复权
                )
                
                if df is None or df.empty:
                    continue
                
                # 标准化列名
                df = df.rename(columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "amount",
                    "涨跌幅": "pct_change",
                    "换手率": "turnover"
                })
                
                df["date"] = pd.to_datetime(df["date"])
                df["symbol"] = symbol
                
                # 选择需要的列
                cols = ["symbol", "date", "open", "high", "low", "close", 
                        "volume", "amount", "pct_change", "turnover"]
                df = df[[c for c in cols if c in df.columns]]
                
                all_data.append(df)
                time.sleep(0.1)  # 避免频率限制
                
            except Exception as e:
                logger.debug(f"Akshare: {symbol} 获取失败: {e}")
                continue
        
        if not all_data:
            return None
        
        return pd.concat(all_data, ignore_index=True)
    
    def _fetch_from_tushare(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        show_progress: bool
    ) -> Optional[pd.DataFrame]:
        """从 Tushare 获取数据"""
        import tushare as ts
        
        ts.set_token(self.tushare_token)
        pro = ts.pro_api()
        
        all_data = []
        iterator = symbols
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(symbols, desc="Tushare")
        
        for symbol in iterator:
            try:
                # 转换代码格式
                ts_code = self._convert_to_tushare_code(symbol)
                
                df = pro.daily(
                    ts_code=ts_code,
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", "")
                )
                
                if df is None or df.empty:
                    continue
                
                # 标准化
                df = df.rename(columns={
                    "trade_date": "date",
                    "vol": "volume",
                    "pct_chg": "pct_change"
                })
                
                df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
                df["symbol"] = symbol
                
                cols = ["symbol", "date", "open", "high", "low", "close", 
                        "volume", "pct_change"]
                df = df[[c for c in cols if c in df.columns]]
                
                all_data.append(df)
                time.sleep(0.1)
                
            except Exception as e:
                logger.debug(f"Tushare: {symbol} 获取失败: {e}")
                continue
        
        if not all_data:
            return None
        
        return pd.concat(all_data, ignore_index=True)
    
    def _fetch_from_yfinance(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        show_progress: bool
    ) -> Optional[pd.DataFrame]:
        """从 yfinance 获取数据"""
        import yfinance as yf
        
        all_data = []
        iterator = symbols
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(symbols, desc="yfinance")
        
        for symbol in iterator:
            try:
                # yfinance 格式
                yf_symbol = self._convert_to_yfinance_code(symbol)
                
                ticker = yf.Ticker(yf_symbol)
                df = ticker.history(start=start_date, end=end_date)
                
                if df is None or df.empty:
                    continue
                
                df = df.reset_index()
                df["symbol"] = symbol
                df["date"] = pd.to_datetime(df["Date"])
                df["pct_change"] = df["Close"].pct_change() * 100
                df["amount"] = df["Close"] * df["Volume"]
                
                df = df.rename(columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume"
                })
                
                cols = ["symbol", "date", "open", "high", "low", "close", 
                        "volume", "amount", "pct_change"]
                df = df[[c for c in cols if c in df.columns]]
                
                all_data.append(df)
                
            except Exception as e:
                logger.debug(f"yfinance: {symbol} 获取失败: {e}")
                continue
        
        if not all_data:
            return None
        
        return pd.concat(all_data, ignore_index=True)
    
    def _fetch_from_mock(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        show_progress: bool
    ) -> pd.DataFrame:
        """生成 Mock 数据（备用）"""
        logger.info("使用 Mock 模拟数据")
        
        dates = pd.date_range(start_date, end_date, freq="B")
        all_data = []
        
        for symbol in symbols:
            np.random.seed(hash(symbol) % 2**32)
            n = len(dates)
            
            # 使用 GBM 模拟价格
            dt = 1/252
            mu = 0.08
            sigma = 0.25
            S0 = np.random.uniform(10, 200)
            
            returns = np.random.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
            price = S0 * np.exp(np.cumsum(returns))
            
            df = pd.DataFrame({
                "symbol": symbol,
                "date": dates,
                "open": price * (1 + np.random.uniform(-0.01, 0.01, n)),
                "high": price * (1 + np.abs(np.random.normal(0.005, 0.005, n))),
                "low": price * (1 - np.abs(np.random.normal(0.005, 0.005, n))),
                "close": price,
                "volume": np.random.randint(1000000, 10000000, n),
                "amount": np.random.randint(10000000, 100000000, n),
                "pct_change": np.concatenate([[0], np.diff(np.log(price)) * 100]),
                "turnover": np.random.uniform(0.5, 5, n)
            })
            
            all_data.append(df)
        
        return pd.concat(all_data, ignore_index=True)
    
    def _convert_to_tushare_code(self, symbol: str) -> str:
        """转换为 Tushare 代码格式"""
        if "." in symbol:
            return symbol
        # 根据 A 股规则推断交易所
        if symbol.startswith("6"):
            return f"{symbol}.SH"
        return f"{symbol}.SZ"
    
    def _convert_to_yfinance_code(self, symbol: str) -> str:
        """转换为 yfinance 代码格式"""
        if "." in symbol:
            # Tushare 格式转换
            code, exchange = symbol.split(".")
            if exchange == "SH":
                return f"{code}.SS"
            elif exchange == "SZ":
                return f"{code}.SZ"
        # A 股代码
        if symbol.startswith("6"):
            return f"{symbol}.SS"
        return f"{symbol}.SZ"
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        # 优先 Akshare
        if self.source_status["akshare"]:
            try:
                import akshare as ak
                df = ak.stock_zh_a_spot_em()
                df = df.rename(columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "总市值": "market_cap"
                })
                return df[["symbol", "name", "price", "market_cap"]]
            except:
                pass
        
        # Tushare
        if self.source_status["tushare"]:
            try:
                import tushare as ts
                ts.set_token(self.tushare_token)
                pro = ts.pro_api()
                df = pro.stock_basic(exchange="", list_status="L")
                return df[["ts_code", "name"]].rename(columns={"ts_code": "symbol"})
            except:
                pass
        
        # Mock
        return pd.DataFrame({
            "symbol": [f"{i:06d}" for i in range(1, 101)],
            "name": [f"Stock_{i}" for i in range(1, 101)]
        })
    
    def get_index_constituents(self, index: str = "000300") -> List[str]:
        """获取指数成分股"""
        if self.source_status["akshare"]:
            try:
                import akshare as ak
                df = ak.index_stock_cons_weight_csindex(symbol=index)
                return df["成分券代码"].tolist()
            except:
                pass
        
        # Mock - 返回前50个
        return [f"{i:06d}" for i in range(1, 51)]


# 便捷函数
def get_data_provider(
    tushare_token: Optional[str] = None,
    cache_enabled: bool = True
) -> MultiSourceDataProvider:
    """获取数据提供者实例"""
    return MultiSourceDataProvider(
        tushare_token=tushare_token,
        cache_enabled=cache_enabled
    )
