"""
Alpha#5: 量价相关性因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha005(Factor):
    """Alpha#5: 量价相关性因子"""
    id = "alpha_005"
    name = "Alpha#5"
    category = "alpha101"
    description = "量价相关性因子"
    formula = "(rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap)))))"
    parameters = {"window": 10}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                open_ = stock_data['open']
                close = stock_data['close']
                vwap = stock_data.get('vwap', (stock_data['high'] + stock_data['low'] + close) / 3)
                avg_vwap = sma(vwap, 10)
                factor_val = rank(open_ - avg_vwap).iloc[-1] * (-abs(rank(close - vwap))).iloc[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)
