"""
Alpha#71因子
双重时序排名最大值因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha071(Factor):
    """Alpha#71: 双重时序排名最大值因子"""
    id = "alpha_071"
    name = "Alpha#71"
    description = "双重时序排名最大值因子"
    category = "综合因子"
    formula = "max(Ts_Rank(decay_linear(correlation(Ts_Rank(close, 3), Ts_Rank(adv180, 12), 18), 4), 16), Ts_Rank(decay_linear((rank(((low + open) - (vwap + vwap))).pow(2)), 16), 4))"
    required_fields = ['open', 'low', 'close', 'vol']
    min_data_periods = 200
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
        
        # Alpha#071 公式实现
        # max(Ts_Rank(decay_linear(correlation(Ts_Rank(close, 3), Ts_Rank(adv180, 12), 18), 4), 16), Ts_Rank(decay_linear((rank(((low + open) - (vwap + vwap))).pow(2)), 16), 4))
        
        # ============ 实现具体公式 ============
        factor_val = self._calculate_factor(
            close=close, open_price=open_price, high=high, 
            low=low, vol=vol, pct_chg=pct_chg, vwap=vwap, adv20=adv20
        )
        
        return float(factor_val) if not np.isnan(factor_val) else 0
    
    
    def _calculate_factor(self, close, open_price, high, low, vol, pct_chg, vwap, adv20):
        """Alpha#71: 双重时序排名最大值"""
        adv180 = sma(vol, 180)
        p1 = ts_rank(decay_linear(correlation(ts_rank(close, 3), ts_rank(adv180, 12), 18), 4), 16).iloc[-1]
        p2 = ts_rank(decay_linear((rank((low + open_price - vwap - vwap)) ** 2), 16), 4).iloc[-1]
        return max(p1, p2)



