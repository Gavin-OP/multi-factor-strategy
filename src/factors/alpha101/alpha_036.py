"""
Alpha#36因子
多因子加权组合因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha036(Factor):
    """Alpha#36: 多因子加权组合因子"""
    id = "alpha_036"
    name = "Alpha#36"
    description = "多因子加权组合因子"
    category = "综合因子"
    formula = "(((((2.21 * rank(correlation((close - open), delay(volume, 1), 15))) + (0.7 * rank((open - close)))) + (0.73 * rank(Ts_Rank(delay((-1 * returns), 6), 5)))) + rank(abs(correlation(vwap, adv20, 6)))) + (0.6 * rank((((sum(close, 200) / 200) - open) * (close - open)))))"
    required_fields = ['open', 'high', 'low', 'close', 'pct_chg', 'vol']
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
        
        # Alpha#036 公式实现
        # (((((2.21 * rank(correlation((close - open), delay(volume, 1), 15))) + (0.7 * rank((open - close)))) + (0.73 * rank(Ts_Rank(delay((-1 * returns), 6), 5)))) + rank(abs(correlation(vwap, adv20, 6)))) + (0.6 * rank((((sum(close, 200) / 200) - open) * (close - open)))))
        
        # ============ 实现具体公式 ============
        factor_val = self._calculate_factor(
            close=close, open_price=open_price, high=high, 
            low=low, vol=vol, pct_chg=pct_chg, vwap=vwap, adv20=adv20
        )
        
        return float(factor_val) if not np.isnan(factor_val) else 0
    
    
    def _calculate_factor(self, close, open_price, high, low, vol, pct_chg, vwap, adv20):
        """Alpha#36: 多因子加权组合"""
        returns = pct_chg / 100
        p1 = 2.21 * rank(correlation(close - open_price, delay(vol, 1), 15)).iloc[-1]
        p2 = 0.7 * rank(open_price - close).iloc[-1]
        p3 = 0.73 * rank(ts_rank(delay(-1 * returns, 6), 5)).iloc[-1]
        p4 = rank(abs(correlation(vwap, adv20, 6))).iloc[-1]
        p5 = 0.6 * rank((sma(close, 200) - open_price) * (close - open_price)).iloc[-1]
        return p1 + p2 + p3 + p4 + p5



