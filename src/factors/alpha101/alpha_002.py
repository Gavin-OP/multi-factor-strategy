"""
Alpha#2: 价差反转因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha002(Factor):
    """Alpha#2: 价差反转因子"""
    id = "alpha_002"
    name = "Alpha#2"
    category = "alpha101"
    description = "价差反转因子"
    formula = "(-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))"
    parameters = {"window": 6}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                vol = stock_data['vol']
                close = stock_data['close']
                open_ = stock_data['open']
                delta_vol = delta(np.log(vol + 1), 2)
                price_change = (close - open_) / open_
                corr = correlation(rank(delta_vol), rank(price_change), 6).iloc[-1]
                result[ts_code] = float(-corr) if not np.isnan(corr) else 0
        return pd.Series(result)
