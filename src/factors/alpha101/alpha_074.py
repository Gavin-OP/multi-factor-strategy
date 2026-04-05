"""
Alpha#74因子
收盘价成交量相关性与均价成交量排名比较因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha074(Factor):
    """Alpha#74: 收盘价成交量相关性与均价成交量排名比较因子"""
    id = "alpha_074"
    name = "Alpha#74"
    description = "收盘价成交量相关性与均价成交量排名比较因子"
    category = "量价因子"
    formula = "((rank(correlation(close, sum(adv30, 37.4843), 15.1365)) < rank(correlation(rank(((high + low) / 2)), rank(volume), 12.1098))) * -1)"
    required_fields = ['high', 'low', 'close', 'vol']
    min_data_periods = 50
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= self.min_data_periods:
                try:
                    factor_value = self._compute_single_stock(stock_data)
                    result[ts_code] = factor_value
                except Exception:
                    result[ts_code] = 0
        return pd.Series(result)
    
    def _compute_single_stock(self, stock_data: pd.DataFrame) -> float:
        """计算单个股票的因子值"""
        close = stock_data['close']
        open_price = stock_data.get('open', close)
        high = stock_data.get('high', close)
        low = stock_data.get('low', close)
        vol = stock_data.get('vol', stock_data.get('volume', pd.Series(0, index=stock_data.index)))
        pct_chg = stock_data.get('pct_chg', pd.Series(0, index=stock_data.index))
        
        # 计算VWAP
        vwap = (high + low + close) / 3
        
        # 计算ADV20
        adv20 = sma(vol, 20)
        
        # Alpha#074 公式实现
        # ((rank(correlation(close, sum(adv30, 37.4843), 15.1365)) < rank(correlation(rank(((high + low) / 2)), rank(volume), 12.1098))) * -1)
        
        # ============ 实现具体公式 ============
        factor_val = self._calculate_factor(
            close=close, open_price=open_price, high=high, 
            low=low, vol=vol, pct_chg=pct_chg, vwap=vwap, adv20=adv20
        )
        
        return float(factor_val) if not np.isnan(factor_val) else 0
    
    
    def _calculate_factor(self, close, open_price, high, low, vol, pct_chg, vwap, adv20):
        """Alpha#74: 收盘价成交量相关性与均价成交量排名比较"""
        adv30 = sma(vol, 30)
        p1 = rank(correlation(close, sma(adv30, 37), 15)).iloc[-1]
        p2 = rank(correlation(rank((high + low) / 2), rank(vol), 12)).iloc[-1]
        return (p1 < p2) * -1



