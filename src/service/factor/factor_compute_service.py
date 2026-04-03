"""
Factor Compute Service - 因子计算服务
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from ...model.factor import FactorMeta, FactorValue
from ...model.market import Price


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
        
        自适应数据量：如果数据不足，自动调整周期
        
        Returns:
            {stock_code: factor_value}
        """
        values = {}
        
        if price_data.empty:
            print(f"[FactorCompute] No price data provided")
            return values
        
        # 获取数据日期范围
        unique_dates = sorted(price_data['trade_date'].unique())
        available_days = len(unique_dates)
        print(f"[FactorCompute] Available: {available_days} days, {price_data['ts_code'].nunique()} stocks")
        
        # 根据因子类型计算
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
            # 默认：计算期间收益
            values = self._compute_return(price_data, available_days)
        
        print(f"[FactorCompute] Computed for {len(values)} stocks")
        return values
    
    def _compute_momentum(self, price_data: pd.DataFrame, factor_type: str, available_days: int) -> Dict[str, float]:
        """计算动量因子"""
        values = {}
        
        # 解析目标周期
        try:
            period_str = factor_type.split('_')[1].replace('m', '')
            target_months = int(period_str)
            target_days = target_months * 20
        except:
            target_days = 20  # 默认1个月
        
        # 自适应：使用 min(目标天数, 可用天数-5)
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
            target_months = int(period_str)
            target_days = target_months * 20
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
        """计算价值因子（简化版，用价格倒数代理）"""
        values = {}
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 1:
                try:
                    # 用最新价格的倒数作为价值代理（价格越低越有价值）
                    close = stock_data['close'].iloc[-1]
                    values[ts_code] = float(1.0 / close) if close > 0 else 0
                except:
                    pass
        
        return values
    
    def _compute_quality(self, price_data: pd.DataFrame, factor_type: str, available_days: int) -> Dict[str, float]:
        """计算质量因子（简化版，用收益稳定性代理）"""
        values = {}
        
        for ts_code in price_data['ts_code'].unique():
            stock_data = price_data[price_data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                try:
                    # 用收益的稳定性（负波动率）作为质量代理
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
                    # 用平均成交量作为流动性代理
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
