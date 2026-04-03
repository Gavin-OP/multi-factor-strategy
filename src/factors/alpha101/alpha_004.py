"""
Alpha#4: 收益排序因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha004(Factor):
    """Alpha#4: 收益排序因子"""
    id = "alpha_004"
    name = "Alpha#4"
    category = "alpha101"
    description = "收益排序因子"
    formula = "(-1 * Ts_Rank(rank(low), 10))"
    parameters = {"window": 10}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                low = stock_data['low']
                factor_val = -ts_rank(rank(low), 10).iloc[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)
