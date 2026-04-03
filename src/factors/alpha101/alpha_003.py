"""
Alpha#3: 价格排序因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha003(Factor):
    """Alpha#3: 价格排序因子"""
    id = "alpha_003"
    name = "Alpha#3"
    category = "alpha101"
    description = "价格排序因子"
    formula = "(-1 * correlation(rank(open), rank(delay(volume, 1)), 10))"
    parameters = {"window": 10}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 12:
                open_ = stock_data['open']
                vol = stock_data['vol']
                corr = correlation(rank(open_), rank(delay(vol, 1)), 10).iloc[-1]
                result[ts_code] = float(-corr) if not np.isnan(corr) else 0
        return pd.Series(result)
