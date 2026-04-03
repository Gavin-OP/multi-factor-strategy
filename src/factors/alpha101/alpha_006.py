"""
Alpha#6: 开盘价排序因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha006(Factor):
    """Alpha#6: 开盘价排序因子"""
    id = "alpha_006"
    name = "Alpha#6"
    category = "alpha101"
    description = "开盘价排序因子"
    formula = "(-1 * correlation(open, volume, 10))"
    parameters = {"window": 10}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                corr = correlation(stock_data['open'], stock_data['vol'], 10).iloc[-1]
                result[ts_code] = float(-corr) if not np.isnan(corr) else 0
        return pd.Series(result)
