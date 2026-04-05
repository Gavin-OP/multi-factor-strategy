"""
Alpha#94因子
VWAP最小值与相关性排名幂次因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha094(Factor):
    """Alpha#94: VWAP最小值与相关性排名幂次因子"""
    id = "alpha_094"
    name = "Alpha#94"
    description = "VWAP最小值与相关性排名幂次因子"
    category = "量价因子"
    formula = "((rank((vwap - ts_min(vwap, 11.5783))^Ts_Rank(correlation(Ts_Rank(vwap, 19.6462), Ts_Rank(adv60, 4.02992), 18.0926), 2.70756)) * -1)"
    required_fields = ['vol', 'high', 'low', 'close']
    min_data_periods = 70
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
        
        # Alpha#094 公式实现
        # ((rank((vwap - ts_min(vwap, 11.5783))^Ts_Rank(correlation(Ts_Rank(vwap, 19.6462), Ts_Rank(adv60, 4.02992), 18.0926), 2.70756)) * -1)
        
        # ============ 实现具体公式 ============
        factor_val = self._calculate_factor(
            close=close, open_price=open_price, high=high, 
            low=low, vol=vol, pct_chg=pct_chg, vwap=vwap, adv20=adv20
        )
        
        return float(factor_val) if not np.isnan(factor_val) else 0
    
    
    def _calculate_factor(self, close, open_price, high, low, vol, pct_chg, vwap, adv20):
        """Alpha#94: VWAP最小值与相关性排名幂次"""
        adv60 = sma(vol, 60)
        p1 = rank(vwap - ts_min(vwap, 12)).iloc[-1]
        p2 = ts_rank(correlation(ts_rank(vwap, 20), ts_rank(adv60, 4), 18), 3).iloc[-1]
        return (p1 ** p2) * -1



