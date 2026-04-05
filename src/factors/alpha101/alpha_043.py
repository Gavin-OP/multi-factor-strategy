"""
Alpha#43因子
成交量相对位置与价格变化因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha043(Factor):
    """Alpha#43: 成交量相对位置与价格变化因子"""
    id = "alpha_043"
    name = "Alpha#43"
    description = "成交量相对位置与价格变化因子"
    category = "量价因子"
    formula = "(ts_rank((volume / adv20), 20) * ts_rank((-1 * delta(close, 7)), 8))"
    required_fields = ['close', 'vol']
    min_data_periods = 25
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
        
        # Alpha#043 公式实现
        # (ts_rank((volume / adv20), 20) * ts_rank((-1 * delta(close, 7)), 8))
        
        # ============ 实现具体公式 ============
        factor_val = self._calculate_factor(
            close=close, open_price=open_price, high=high, 
            low=low, vol=vol, pct_chg=pct_chg, vwap=vwap, adv20=adv20
        )
        
        return float(factor_val) if not np.isnan(factor_val) else 0
    
    
    def _calculate_factor(self, close, open_price, high, low, vol, pct_chg, vwap, adv20):
        """Alpha#43: 成交量相对位置与价格变化"""
        return ts_rank(vol / adv20, 20).iloc[-1] * ts_rank(-1 * delta(close, 7), 8).iloc[-1]



