"""
Tushare Repository - Tushare 数据源
"""

import os
from typing import List, Optional
import pandas as pd

from ..model.market import Stock, Price


class TushareRepository:
    """
    Tushare 数据仓库
    
    职责：从 Tushare API 获取数据
    
    注意：不提供 mock 数据，需要配置 TUSHARE_TOKEN
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
                raise ImportError("请安装 tushare: pip install tushare")
        return self._pro
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.token is not None and len(self.token) > 0
    
    # ========== 股票数据 ==========
    
    def search_stocks(self, keyword: str, limit: int = 20) -> List[Stock]:
        """搜索股票（根据代码或名称）"""
        stocks = self.get_stock_list(limit=5000)
        keyword = keyword.lower()
        
        results = [
            s for s in stocks
            if keyword in s.ts_code.lower() or keyword in s.name.lower()
        ]
        return results[:limit]
    
    def get_stock_list(self, market: str = None, limit: int = None) -> List[Stock]:
        """获取股票列表"""
        if not self.is_available():
            raise ValueError("TUSHARE_TOKEN 未配置，无法获取股票列表")
        
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
            raise RuntimeError(f"获取股票列表失败: {e}")
    
    # ========== 价格数据 ==========
    
    def get_daily_prices(
        self,
        ts_code: str,
        start_date: str,
        end_date: str
    ) -> List[Price]:
        """获取日线数据"""
        if not self.is_available():
            raise ValueError("TUSHARE_TOKEN 未配置，无法获取价格数据")
        
        try:
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            if df.empty:
                return []
            df = df.sort_values('trade_date')
            return [Price(**row) for row in df.to_dict('records')]
        except Exception as e:
            raise RuntimeError(f"获取价格数据失败: {e}")
    
    # ========== 指数数据 ==========
    
    def get_index_list(self) -> List[dict]:
        """获取主要指数列表"""
        return [
            {"ts_code": "000001.SH", "name": "上证指数", "market": "上海"},
            {"ts_code": "399001.SZ", "name": "深证成指", "market": "深圳"},
            {"ts_code": "399006.SZ", "name": "创业板指", "market": "深圳"},
            {"ts_code": "000688.SH", "name": "科创50", "market": "上海"},
            {"ts_code": "000300.SH", "name": "沪深300", "market": "上海"},
            {"ts_code": "000016.SH", "name": "上证50", "market": "上海"},
            {"ts_code": "000905.SH", "name": "中证500", "market": "上海"},
            {"ts_code": "000852.SH", "name": "中证1000", "market": "上海"},
        ]
    
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
        
        if not self.is_available():
            raise ValueError("TUSHARE_TOKEN 未配置，无法获取指数数据")
        
        try:
            df = self.pro.index_daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            if df.empty:
                return pd.DataFrame()
            return df.sort_values('trade_date')
        except Exception as e:
            raise RuntimeError(f"获取指数数据失败: {e}")
    
    # ========== 批量获取 ==========
    
    def get_daily_multiple(
        self,
        ts_codes: List[str],
        start_date: str,
        end_date: str,
        limit: int = 50
    ) -> pd.DataFrame:
        """批量获取多只股票数据"""
        if not self.is_available():
            raise ValueError("TUSHARE_TOKEN 未配置，无法获取数据")
        
        all_data = []
        success_count = 0
        
        for code in ts_codes[:limit]:
            try:
                prices = self.get_daily_prices(code, start_date, end_date)
                if prices:
                    for p in prices:
                        all_data.append({
                            'ts_code': p.ts_code,
                            'trade_date': p.trade_date,
                            'close': p.close,
                            'open': p.open,
                            'high': p.high,
                            'low': p.low,
                            'vol': p.vol,
                            'pct_chg': p.pct_chg,
                        })
                    success_count += 1
            except Exception as e:
                print(f"Failed to get data for {code}: {e}")
                continue
        
        print(f"Successfully fetched data for {success_count} stocks")
        return pd.DataFrame(all_data)
