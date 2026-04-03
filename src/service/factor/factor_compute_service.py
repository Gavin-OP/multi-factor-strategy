"""
Factor Compute Service - 因子计算服务
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from ...factors import FactorRegistry


class FactorComputeService:
    """因子计算服务"""
    
    def compute_factor_values(
        self,
        price_data: pd.DataFrame,
        factor_type: str,
        **kwargs
    ) -> Dict[str, float]:
        """
        批量计算因子值
        
        Args:
            price_data: 包含 OHLCV 数据的 DataFrame
            factor_type: 因子 ID
            
        Returns:
            {stock_code: factor_value}
        """
        values = {}
        
        if price_data.empty:
            print(f"[FactorCompute] No price data provided")
            return values
        
        # 获取可用数据量
        unique_dates = sorted(price_data['trade_date'].unique())
        available_days = len(unique_dates)
        print(f"[FactorCompute] Available: {available_days} days, {price_data['ts_code'].nunique()} stocks")
        
        # 从注册中心获取因子
        factor = FactorRegistry.get(factor_type)
        
        if factor:
            # 使用因子类计算
            try:
                series = factor.compute(price_data)
                values = series.to_dict()
            except Exception as e:
                print(f"[FactorCompute] Factor {factor_type} compute error: {e}")
                # 回退到内置计算
                values = self._compute_builtin(price_data, factor_type, available_days)
        else:
            # 使用内置计算方法
            values = self._compute_builtin(price_data, factor_type, available_days)
        
        print(f"[FactorCompute] Computed for {len(values)} stocks")
        return values
    
    def _compute_builtin(
        self, 
        price_data: pd.DataFrame, 
        factor_type: str, 
        available_days: int
    ) -> Dict[str, float]:
        """内置因子计算方法（兼容旧代码）"""
        values = {}
        
        if factor_type.startswith('momentum'):
            values = self._compute_momentum(price_data, factor_type, available_days)
        elif factor_type.startswith('volatility'):
            values = self._compute_volatility(price_data, factor_type, available_days)
        elif factor_type.startswith('value'):
            values = self._compute_value(price_data, factor_type, available_days)
        elif factor_type.startswith('quality'):
            values = self._compute_quality(price_data, factor_type, available_days)
        elif factor_type.startswith('liquidity'):
            values = self._compute_liquidity(price_data, factor_type, available_days)
        else:
            values = self._compute_return(price_data, available_days)
        
        return values
    
    def _compute_momentum(self, price_data: pd.DataFrame, factor_type: str, available_days: int) -> Dict[str, float]:
        """计算动量因子"""
        values = {}
        
        try:
            period_str = factor_type.split('_')[1].replace('m', '')
            target_months = int(period_str)
            target_days = target_months * 20
        except:
            target_days = 20
        
        actual_period = min(target_days, max(available_days - 5, 5))
        
        if actual_period < target_days:
            print(f"[FactorCompute] Momentum: adjusted period from {target_days} to {actual_period} days")
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= actual_period:
                try:
                    ret = stock_data['close'].iloc[-1] / stock_data['close'].iloc[-actual_period] - 1
                    values[ts_code] = float(ret)
                except:
                    pass
        
        return values
    
    def _compute_volatility(self, price_data: pd.DataFrame, factor_type: str, available_days: int) -> Dict[str, float]:
        """计算波动率因子"""
        values = {}
        
        try:
            period_str = factor_type.split('_')[1].replace('m', '')
            target_days = int(period_str) * 20
        except:
            target_days = 20
        
        actual_period = min(target_days, max(available_days - 5, 5))
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= actual_period:
                try:
                    std = stock_data['pct_chg'].iloc[-actual_period:].std()
                    values[ts_code] = float(std) if not np.isnan(std) else 0
                except:
                    pass
        
        return values
    
    def _compute_value(self, price_data: pd.DataFrame, factor_type: str, available_days: int) -> Dict[str, float]:
        """计算价值因子"""
        values = {}
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 1:
                try:
                    close = stock_data['close'].iloc[-1]
                    values[ts_code] = float(1.0 / close) if close > 0 else 0
                except:
                    pass
        
        return values
    
    def _compute_quality(self, price_data: pd.DataFrame, factor_type: str, available_days: int) -> Dict[str, float]:
        """计算质量因子"""
        values = {}
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                try:
                    std = stock_data['pct_chg'].iloc[-10:].std()
                    values[ts_code] = float(-std) if not np.isnan(std) else 0
                except:
                    pass
        
        return values
    
    def _compute_liquidity(self, price_data: pd.DataFrame, factor_type: str, available_days: int) -> Dict[str, float]:
        """计算流动性因子"""
        values = {}
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 5:
                try:
                    avg_vol = stock_data['vol'].iloc[-5:].mean()
                    values[ts_code] = float(avg_vol) if not np.isnan(avg_vol) else 0
                except:
                    pass
        
        return values
    
    def _compute_return(self, price_data: pd.DataFrame, available_days: int) -> Dict[str, float]:
        """计算简单收益"""
        values = {}
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 2:
                try:
                    ret = stock_data['close'].iloc[-1] / stock_data['close'].iloc[0] - 1
                    values[ts_code] = float(ret)
                except:
                    pass
        
        return values
