"""
12月动量因子
"""

from ..base import Factor
from ..registry import register_factor
import pandas as pd


@register_factor
class Momentum12M(Factor):
    """12月动量因子"""
    id = "momentum_12m"
    name = "12月动量因子"
    category = "动量因子"
    description = "过去12个月的收益率，经典动量因子"
    formula = "close_t / close_{t-240} - 1"
    parameters = {"period": 240}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        period = self.parameters["period"]
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= period:
                result[ts_code] = float(
                    stock_data['close'].iloc[-1] / stock_data['close'].iloc[-period] - 1
                )
        return pd.Series(result)
