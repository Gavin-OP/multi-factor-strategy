"""
Volatility Factors - 波动率因子族
"""

from ..base import Factor
from ..registry import register_factor
import pandas as pd
import numpy as np


@register_factor
class Volatility1M(Factor):
    """1月波动率因子"""
    id = "volatility_1m"
    name = "1月波动率因子"
    category = "波动因子"
    description = "过去1个月收益率标准差"
    formula = "std(returns, 20)"
    parameters = {"period": 20}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        period = self.parameters["period"]
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= period:
                std = stock_data['pct_chg'].iloc[-period:].std()
                result[ts_code] = float(std) if not np.isnan(std) else 0
        return pd.Series(result)


__all__ = ['Volatility1M']
