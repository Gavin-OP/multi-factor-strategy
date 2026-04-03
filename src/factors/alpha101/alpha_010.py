"""
Alpha#10: 收益波动因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha010(Factor):
    """Alpha#10: 收益波动因子"""
    id = "alpha_010"
    name = "Alpha#10"
    category = "alpha101"
    description = "收益波动因子"
    formula = "rank(((0 < ts_min(delta(close, 1), 4)) ? sign(delta(close, 1)) : sign(ts_min(delta(close, 1), 4))))"
    parameters = {"window": 4}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 5:
                close = stock_data['close']
                d = delta(close, 1)
                min_d = ts_min(d, 4)
                current_d = d.iloc[-1]
                if min_d.iloc[-1] > 0:
                    factor_val = np.sign(current_d)
                else:
                    factor_val = np.sign(min_d.iloc[-1])
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)
