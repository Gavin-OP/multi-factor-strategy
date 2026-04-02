"""
Factor Compute Service - 因子计算服务
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from ..model.factor import FactorMeta, FactorValue
from ..model.market import Price


class FactorComputeService:
    """因子计算服务"""
    
    def compute_momentum(
        self,
        prices: List[Price],
        period: int = 20
    ) -> float:
        """计算动量因子"""
        if len(prices) < period:
            return 0.0
        
        close_prices = [p.close for p in prices[-period:]]
        return (close_prices[-1] / close_prices[0]) - 1
    
    def compute_volatility(
        self,
        prices: List[Price],
        period: int = 20
    ) -> float:
        """计算波动率因子"""
        if len(prices) < period:
            return 0.0
        
        returns = pd.Series([p.pct_chg for p in prices[-period:]])
        return float(returns.std())
    
    def compute_turnover(
        self,
        prices: List[Price],
        period: int = 20
    ) -> float:
        """计算换手率因子"""
        if len(prices) < period:
            return 0.0
        
        vols = [p.vol for p in prices[-period:]]
        return float(np.mean(vols))
    
    def compute_factor_values(
        self,
        price_data: pd.DataFrame,
        factor_type: str,
        **kwargs
    ) -> Dict[str, float]:
        """
        批量计算因子值
        
        Returns:
            {stock_code: factor_value}
        """
        values = {}
        
        if factor_type.startswith('momentum'):
            period = int(factor_type.split('_')[1].replace('m', '')) * 20
            for ts_code in price_data['ts_code'].unique():
                stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
                if len(stock_data) >= period:
                    values[ts_code] = float(
                        stock_data['close'].iloc[-1] / stock_data['close'].iloc[-period] - 1
                    )
        
        elif factor_type.startswith('volatility'):
            period = int(factor_type.split('_')[1].replace('m', '')) * 20
            for ts_code in price_data['ts_code'].unique():
                stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
                if len(stock_data) >= period:
                    values[ts_code] = float(stock_data['pct_chg'].iloc[-period:].std())
        
        return values
