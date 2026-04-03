"""
Alpha#9: 波动率因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha009(Factor):
    """Alpha#9: 波动率因子"""
    id = "alpha_009"
    name = "Alpha#9"
    category = "alpha101"
    description = "波动率因子"
    formula = "((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1))))"
    parameters = {"window": 5}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 6:
                close = stock_data['close']
                d = delta(close, 1)
                min_d = ts_min(d, 5)
                max_d = ts_max(d, 5)
                current_d = d.iloc[-1]
                if min_d.iloc[-1] > 0:
                    factor_val = current_d
                elif max_d.iloc[-1] < 0:
                    factor_val = current_d
                else:
                    factor_val = -current_d
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)
