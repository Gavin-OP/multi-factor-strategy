"""
Momentum Factors - 动量因子族
"""

from ..base import Factor
from ..registry import register_factor
import pandas as pd
import numpy as np


@register_factor
class Momentum1M(Factor):
    """1月动量因子"""
    id = "momentum_1m"
    name = "1月动量因子"
    category = "动量因子"
    description = "过去1个月的收益率，反映短期价格动量"
    formula = "close_t / close_{t-20} - 1"
    parameters = {"period": 20}
    
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


@register_factor
class Momentum3M(Factor):
    """3月动量因子"""
    id = "momentum_3m"
    name = "3月动量因子"
    category = "动量因子"
    description = "过去3个月的收益率"
    formula = "close_t / close_{t-60} - 1"
    parameters = {"period": 60}
    
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


@register_factor
class Momentum6M(Factor):
    """6月动量因子"""
    id = "momentum_6m"
    name = "6月动量因子"
    category = "动量因子"
    description = "过去6个月的收益率"
    formula = "close_t / close_{t-120} - 1"
    parameters = {"period": 120}
    
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


__all__ = ['Momentum1M', 'Momentum3M', 'Momentum6M', 'Momentum12M']
