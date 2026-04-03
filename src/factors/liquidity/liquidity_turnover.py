"""
换手率因子
"""

from ..base import Factor
from ..registry import register_factor
import pandas as pd
import numpy as np


@register_factor
class LiquidityTurnover(Factor):
    """换手率因子"""
    id = "liquidity_turnover"
    name = "换手率因子"
    category = "流动性因子"
    description = "平均成交量因子，反映流动性"
    formula = "mean(volume, 5)"
    parameters = {"period": 5}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        period = self.parameters["period"]
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= period:
                avg_vol = stock_data['vol'].iloc[-period:].mean()
                result[ts_code] = float(avg_vol) if not np.isnan(avg_vol) else 0
        return pd.Series(result)
