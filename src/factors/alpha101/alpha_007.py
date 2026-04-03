"""
Alpha#7: 量价动量因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha007(Factor):
    """Alpha#7: 量价动量因子"""
    id = "alpha_007"
    name = "Alpha#7"
    category = "alpha101"
    description = "量价动量因子"
    formula = "((adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : (-1 * 1))"
    parameters = {"window1": 20, "window2": 60}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 70:
                close = stock_data['close']
                vol = stock_data['vol']
                adv20 = sma(vol, 20)
                delta_close = delta(close, 7)
                factor_val = np.where(
                    adv20 < vol,
                    -ts_rank(abs(delta_close), 60) * sign(delta_close),
                    -1
                )[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)
