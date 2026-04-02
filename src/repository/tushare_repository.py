"""
Tushare Repository - Tushare 数据源
"""

import os
from typing import List, Optional
import pandas as pd
import numpy as np

from ..model.market import Stock, Price


class TushareRepository:
    """
    Tushare 数据仓库
    
    职责：从 Tushare API 获取数据
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("TUSHARE_TOKEN", "")
        self._pro = None
    
    @property
    def pro(self):
        """获取 Tushare pro 接口"""
        if self._pro is None and self.token:
            try:
                import tushare as ts
                ts.set_token(self.token)
                self._pro = ts.pro_api()
            except ImportError:
                pass
        return self._pro
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.pro is not None
    
    # ========== 股票数据 ==========
    
    def get_stock_list(self, market: str = None, limit: int = None) -> List[Stock]:
        """获取股票列表"""
        if self.is_available():
            try:
                df = self.pro.stock_basic(
                    exchange='',
                    list_status='L',
                    fields='ts_code,symbol,name,area,industry,market,list_date'
                )
                if market:
                    df = df[df['market'] == market]
                if limit:
                    df = df.head(limit)
                return [Stock(**row) for row in df.to_dict('records')]
            except Exception as e:
                print(f"Tushare error: {e}")
        
        # Mock data
        return self._mock_stock_list(limit or 100)
    
    def _mock_stock_list(self, limit: int) -> List[Stock]:
        """生成模拟股票列表"""
        return [
            Stock(
                ts_code=f"{600000+i:06d}.SH",
                symbol=f"{600000+i:06d}",
                name=f"股票{i+1}",
                market="主板"
            )
            for i in range(limit)
        ]
    
    # ========== 价格数据 ==========
    
    def get_daily_prices(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> List[Price]:
        """获取日线数据"""
        if self.is_available():
            try:
                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                if not df.empty:
                    df = df.sort_values('trade_date')
                    return [Price(**row) for row in df.to_dict('records')]
            except Exception as e:
                print(f"Tushare error: {e}")
        
        return self._mock_prices(ts_code, start_date, end_date)
    
    def _mock_prices(self, ts_code: str, start_date: str, end_date: str) -> List[Price]:
        """生成模拟价格数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n = min(len(dates), 100)
        
        base = 10.0
        close = base * np.exp(np.cumsum(np.random.randn(n) * 0.02))
        
        return [
            Price(
                ts_code=ts_code,
                trade_date=dates[i].strftime('%Y%m%d'),
                open=float(close[i] * (1 + np.random.randn() * 0.01)),
                high=float(close[i] * 1.02),
                low=float(close[i] * 0.98),
                close=float(close[i]),
                pre_close=float(close[max(0, i-1)]),
                change=float(close[i] - close[max(0, i-1)]),
                pct_chg=float((close[i] / close[max(0, i-1)] - 1) * 100),
                vol=float(np.random.randint(1000000, 10000000)),
                amount=float(close[i] * np.random.randint(1000000, 10000000))
            )
            for i in range(n)
        ]
    
    # ========== 指数数据 ==========
    
    def get_index_daily(
        self,
        ts_code: str = "000001.SH",
        start_date: str = "20230101",
        end_date: str = None
    ) -> pd.DataFrame:
        """获取指数日线数据"""
        from datetime import datetime
        
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        
        if self.is_available():
            try:
                df = self.pro.index_daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                if not df.empty:
                    return df.sort_values('trade_date')
            except Exception as e:
                print(f"Tushare error: {e}")
        
        # Mock data
        return self._mock_index(ts_code, start_date, end_date)
    
    def _mock_index(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟指数数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n = min(len(dates), 100)
        
        base = 3000.0
        close = base * np.exp(np.cumsum(np.random.randn(n) * 0.01))
        
        return pd.DataFrame({
            'ts_code': ts_code,
            'trade_date': [d.strftime('%Y%m%d') for d in dates[:n]],
            'close': close,
            'open': close * (1 + np.random.randn(n) * 0.005),
            'high': close * 1.01,
            'low': close * 0.99,
            'vol': np.random.randint(1e8, 5e8, n),
        })
    
    # ========== 批量获取 ==========
    
    def get_daily_multiple(
        self,
        ts_codes: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """批量获取多只股票数据"""
        all_data = []
        for code in ts_codes[:20]:  # 限制数量避免超限
            try:
                prices = self.get_daily_prices(code, start_date, end_date)
                for p in prices:
                    all_data.append({
                        'ts_code': p.ts_code,
                        'trade_date': p.trade_date,
                        'close': p.close,
                        'open': p.open,
                        'high': p.high,
                        'low': p.low,
                        'vol': p.vol,
                    })
            except:
                continue
        
        return pd.DataFrame(all_data)
