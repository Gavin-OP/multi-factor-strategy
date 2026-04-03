"""
PE因子
"""

from ..base import Factor
from ..registry import register_factor
import pandas as pd


@register_factor
class ValuePE(Factor):
    """PE因子"""
    id = "value_pe"
    name = "PE因子"
    category = "价值因子"
    description = "市盈率因子，PE越低越有价值"
    formula = "1 / PE"
    parameters = {}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code]
            if len(stock_data) > 0:
                close = stock_data['close'].iloc[-1]
                result[ts_code] = float(1.0 / close) if close > 0 else 0
        return pd.Series(result)
