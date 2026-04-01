"""
Tushare Data Provider
Implements data fetching using Tushare API
"""

import os
import pandas as pd
import numpy as np
from typing import Optional, List
from datetime import datetime, timedelta

# Try to import tushare, provide helpful message if not available
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("Warning: tushare not installed. Run: pip install tushare")


class TushareProvider:
    """
    Tushare 数据提供者
    
    使用前需要设置 TUSHARE_TOKEN 环境变量或直接传入 token
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("TUSHARE_TOKEN")
        self._pro = None
        
        if not self.token:
            print("Warning: TUSHARE_TOKEN not set. Using mock data.")
    
    @property
    def pro(self):
        """获取 Tushare pro 接口"""
        if self._pro is None and TUSHARE_AVAILABLE and self.token:
            ts.set_token(self.token)
            self._pro = ts.pro_api()
        return self._pro
    
    def is_available(self) -> bool:
        """检查 Tushare 是否可用"""
        return TUSHARE_AVAILABLE and self.token is not None and self.pro is not None
    
    # ==================== 股票基础数据 ====================
    
    def get_stock_list(self, market: str = "主板") -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            market: 市场类型 (主板, 创业板, 科创板, 北交所)
        
        Returns:
            DataFrame with columns: ts_code, symbol, name, area, industry, market, list_date
        """
        if self.is_available():
            try:
                df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
                if market:
                    df = df[df['market'] == market]
                return df
            except Exception as e:
                print(f"Error fetching stock list: {e}")
        
        # Return mock data
        return self._mock_stock_list(market)
    
    def _mock_stock_list(self, market: str) -> pd.DataFrame:
        """生成模拟股票列表"""
        stocks = []
        for i in range(100):
            stocks.append({
                'ts_code': f"{600000 + i:06d}.SH",
                'symbol': f"{600000 + i:06d}",
                'name': f"股票{i+1}",
                'area': '上海',
                'industry': np.random.choice(['银行', '房地产', '医药', '科技', '消费']),
                'market': market,
                'list_date': '20200101'
            })
        return pd.DataFrame(stocks)
    
    # ==================== 日线数据 ====================
    
    def get_daily(
        self, 
        ts_code: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        获取日线行情数据
        
        Args:
            ts_code: 股票代码 (如 000001.SZ)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            DataFrame with OHLCV data
        """
        if self.is_available():
            try:
                df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                if df.empty:
                    return pd.DataFrame()
                
                # 添加均线等指标
                df = df.sort_values('trade_date')
                df['ma5'] = df['close'].rolling(5).mean()
                df['ma10'] = df['close'].rolling(10).mean()
                df['ma20'] = df['close'].rolling(20).mean()
                
                return df
            except Exception as e:
                print(f"Error fetching daily data: {e}")
        
        return self._mock_daily_data(ts_code, start_date, end_date)
    
    def _mock_daily_data(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟日线数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n = len(dates)
        
        base_price = 10.0
        returns = np.random.randn(n) * 0.02
        close = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'ts_code': ts_code,
            'trade_date': [d.strftime('%Y%m%d') for d in dates],
            'open': close * (1 + np.random.randn(n) * 0.01),
            'high': close * (1 + np.abs(np.random.randn(n) * 0.015)),
            'low': close * (1 - np.abs(np.random.randn(n) * 0.015)),
            'close': close,
            'pre_close': np.roll(close, 1),
            'change': close - np.roll(close, 1),
            'pct_chg': (close - np.roll(close, 1)) / np.roll(close, 1) * 100,
            'vol': np.random.randint(1000000, 10000000, n),
            'amount': close * np.random.randint(1000000, 10000000, n),
        })
        df.loc[0, 'pre_close'] = base_price
        df.loc[0, 'change'] = 0
        df.loc[0, 'pct_chg'] = 0
        
        # Add moving averages
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        return df
    
    def get_daily_multiple(
        self,
        ts_codes: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """获取多只股票的日线数据"""
        all_data = []
        for code in ts_codes:
            df = self.get_daily(code, start_date, end_date)
            if not df.empty:
                all_data.append(df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    # ==================== 指数数据 ====================
    
    def get_index_daily(
        self,
        ts_code: str = "000001.SH",  # 上证指数
        start_date: str = "20200101",
        end_date: str = None
    ) -> pd.DataFrame:
        """获取指数日线数据"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        
        if self.is_available():
            try:
                df = self.pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                return df.sort_values('trade_date')
            except Exception as e:
                print(f"Error fetching index data: {e}")
        
        return self._mock_index_daily(ts_code, start_date, end_date)
    
    def _mock_index_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟指数数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n = len(dates)
        
        base_price = 3000.0
        returns = np.random.randn(n) * 0.01
        close = base_price * np.exp(np.cumsum(returns))
        
        return pd.DataFrame({
            'ts_code': ts_code,
            'trade_date': [d.strftime('%Y%m%d') for d in dates],
            'close': close,
            'open': close * (1 + np.random.randn(n) * 0.005),
            'high': close * (1 + np.abs(np.random.randn(n) * 0.007)),
            'low': close * (1 - np.abs(np.random.randn(n) * 0.007)),
            'vol': np.random.randint(100000000, 500000000, n),
            'amount': close * np.random.randint(100000000, 500000000, n) * 10,
            'pct_chg': np.roll(close, 1) / close - 1,
        })
    
    # ==================== 财务数据 ====================
    
    def get_financial_indicator(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取财务指标数据
        
        包括 ROE, ROA, 净利率, 毛利率等
        """
        if self.is_available():
            try:
                df = self.pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date)
                return df
            except Exception as e:
                print(f"Error fetching financial data: {e}")
        
        return self._mock_financial_data(ts_code, start_date, end_date)
    
    def _mock_financial_data(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟财务数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='QE')
        
        return pd.DataFrame({
            'ts_code': ts_code,
            'ann_date': [d.strftime('%Y%m%d') for d in dates],
            'end_date': [d.strftime('%Y%m%d') for d in dates],
            'roe': np.random.uniform(0.05, 0.25, len(dates)),
            'roa': np.random.uniform(0.03, 0.15, len(dates)),
            'netprofit_margin': np.random.uniform(0.05, 0.20, len(dates)),
            'grossprofit_margin': np.random.uniform(0.20, 0.50, len(dates)),
            'debt_to_assets': np.random.uniform(0.30, 0.70, len(dates)),
            'current_ratio': np.random.uniform(0.8, 2.0, len(dates)),
        })
    
    # ==================== 复权数据 ====================
    
    def get_adj_factor(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """获取复权因子"""
        if self.is_available():
            try:
                df = self.pro.adj_factor(ts_code=ts_code, start_date=start_date, end_date=end_date)
                return df
            except Exception as e:
                print(f"Error fetching adj_factor: {e}")
        
        # Mock
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        return pd.DataFrame({
            'ts_code': ts_code,
            'trade_date': [d.strftime('%Y%m%d') for d in dates],
            'adj_factor': np.ones(len(dates)),  # Mock: no adjustment
        })
    
    # ==================== 行业分类 ====================
    
    def get_industry_classified(self) -> pd.DataFrame:
        """获取行业分类数据"""
        if self.is_available():
            try:
                df = self.pro.index_classify(level='L1', src='SW')
                return df
            except Exception as e:
                print(f"Error fetching industry data: {e}")
        
        # Mock
        industries = ['银行', '房地产', '医药生物', '电子', '计算机', '传媒', '通信', 
                      '电气设备', '机械设备', '化工', '建筑材料', '建筑装饰', '钢铁',
                      '采掘', '有色金属', '汽车', '家用电器', '食品饮料', '纺织服装',
                      '轻工制造', '商业贸易', '休闲服务', '综合', '国防军工', '公用事业',
                      '交通运输', '非银金融', '农林牧渔']
        
        return pd.DataFrame({
            'index_code': [f"801{i:03d}" for i in range(len(industries))],
            'industry_name': industries,
            'level': 'L1',
            'src': 'SW',
        })
    
    # ==================== 停复牌信息 ====================
    
    def get_suspend(self, trade_date: str) -> pd.DataFrame:
        """获取某日停牌股票"""
        if self.is_available():
            try:
                df = self.pro.suspend(trade_date=trade_date)
                return df
            except Exception as e:
                print(f"Error fetching suspend data: {e}")
        
        return pd.DataFrame()
