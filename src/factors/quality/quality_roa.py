"""
ROA因子
"""

from ..base import Factor
from ..registry import register_factor
import pandas as pd
import numpy as np


@register_factor
class QualityROA(Factor):
    """ROA因子"""
    id = "quality_roa"
    name = "ROA因子"
    category = "质量因子"
    description = "总资产收益率因子"
    formula = "ROA"
    parameters = {}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                std = stock_data['pct_chg'].iloc[-10:].std()
                result[ts_code] = float(-std) if not np.isnan(std) else 0
        return pd.Series(result)
