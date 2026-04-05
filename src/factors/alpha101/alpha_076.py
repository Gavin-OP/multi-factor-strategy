"""
Alpha#76因子
VWAP变化与低价相关性因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha076(Factor):
    """Alpha#76: VWAP变化与低价相关性因子"""
    id = "alpha_076"
    name = "Alpha#76"
    description = "VWAP变化与低价相关性因子"
    category = "量价因子"
    formula = "(max(rank(decay_linear(delta(vwap, 1.24283), 11.8907)), Ts_Rank(decay_linear(Ts_Rank(correlation(IndNeutralize(low, IndClass.sector), adv81, 8.38822), 19.297), 15.7763), 18.4619)) * -1)"
    required_fields = ['low', 'vol', 'high', 'low', 'close']
    min_data_periods = 100
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
        
        # Alpha#076 公式实现
        # (max(rank(decay_linear(delta(vwap, 1.24283), 11.8907)), Ts_Rank(decay_linear(Ts_Rank(correlation(IndNeutralize(low, IndClass.sector), adv81, 8.38822), 19.297), 15.7763), 18.4619)) * -1)
        
        # ============ 实现具体公式 ============
        factor_val = self._calculate_factor(
            close=close, open_price=open_price, high=high, 
            low=low, vol=vol, pct_chg=pct_chg, vwap=vwap, adv20=adv20
        )
        
        return float(factor_val) if not np.isnan(factor_val) else 0
    
    
    def _calculate_factor(self, close, open_price, high, low, vol, pct_chg, vwap, adv20):
        """Alpha#76: VWAP变化与低价相关性"""
        adv81 = sma(vol, 81)
        p1 = rank(decay_linear(delta(vwap, 1), 12)).iloc[-1]
        p2 = ts_rank(decay_linear(ts_rank(correlation(low, adv81, 8), 19), 16), 18).iloc[-1]
        return -max(p1, p2)



