"""
Alpha#30因子
价格趋势与成交量因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha030(Factor):
    """Alpha#30: 价格趋势与成交量因子"""
    id = "alpha_030"
    name = "Alpha#30"
    description = "价格趋势与成交量因子"
    category = "量价因子"
    formula = "(((1.0 - rank(((sign((close - delay(close, 1))) + sign((delay(close, 1) - delay(close, 2)))) + sign((delay(close, 2) - delay(close, 3)))))) * sum(volume, 5)) / sum(volume, 20))"
    required_fields = ['close', 'vol']
    min_data_periods = 20
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
        
        # Alpha#030 公式实现
        # (((1.0 - rank(((sign((close - delay(close, 1))) + sign((delay(close, 1) - delay(close, 2)))) + sign((delay(close, 2) - delay(close, 3)))))) * sum(volume, 5)) / sum(volume, 20))
        
        # ============ 实现具体公式 ============
        factor_val = self._calculate_factor(
            close=close, open_price=open_price, high=high, 
            low=low, vol=vol, pct_chg=pct_chg, vwap=vwap, adv20=adv20
        )
        
        return float(factor_val) if not np.isnan(factor_val) else 0
    
    
    def _calculate_factor(self, close, open_price, high, low, vol, pct_chg, vwap, adv20):
        """Alpha#30: 价格趋势与成交量"""
        delta_close = delta(close, 1)
        inner = sign(delta_close) + sign(delay(delta_close, 1)) + sign(delay(delta_close, 2))
        return ((1.0 - rank(inner).iloc[-1]) * ts_sum(vol, 5).iloc[-1]) / ts_sum(vol, 20).iloc[-1]



