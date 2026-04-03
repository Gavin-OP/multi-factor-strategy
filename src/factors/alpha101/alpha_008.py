"""
Alpha#8: 收益动量因子
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha008(Factor):
    """Alpha#8: 收益动量因子"""
    id = "alpha_008"
    name = "Alpha#8"
    category = "alpha101"
    description = "收益动量因子"
    formula = "(-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)), 10))))"
    parameters = {"window1": 5, "window2": 10}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 15:
                open_ = stock_data['open']
                returns = stock_data['pct_chg'] / 100
                sum_open_ret = sma(open_, 5) * sma(returns, 5)
                factor_val = -rank(sum_open_ret - delay(sum_open_ret, 10)).iloc[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)
