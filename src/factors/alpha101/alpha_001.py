"""
Alpha#1: 波动率加权动量
"""

from ..base import Factor
from ..registry import register_factor
from .helpers import *
import pandas as pd
import numpy as np


@register_factor
class Alpha001(Factor):
    """Alpha#1: 波动率加权动量"""
    id = "alpha_001"
    name = "Alpha#1"
    category = "alpha101"
    description = "波动率加权动量因子"
    formula = "(rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) -0.5)"
    parameters = {"window": 20}
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 25:
                close = stock_data['close']
                returns = stock_data['pct_chg'] / 100
                std_ret = stddev(returns, 20)
                inner = close.copy()
                inner[returns < 0] = std_ret[returns < 0]
                factor_val = rank(ts_argmax(inner ** 2, 5)).iloc[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)
