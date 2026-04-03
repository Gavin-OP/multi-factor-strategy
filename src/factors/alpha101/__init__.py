"""
Alpha101 Factors - WorldQuant 101 Formulaic Alphas

基于 "101 Formulaic Alphas" by Zura Kakushadze
实现来源: https://github.com/yli188/WorldQuant_alpha101_code

注意: 部分因子需要 IndNeutralize 函数(行业中性化)，这些因子未实现
"""

from ..base import Factor
from ..registry import register_factor
import pandas as pd
import numpy as np
from scipy.stats import rankdata


# ============ 辅助函数 ============

def ts_sum(df, window=10):
    """滚动求和"""
    return df.rolling(window).sum()

def sma(df, window=10):
    """简单移动平均"""
    return df.rolling(window).mean()

def stddev(df, window=10):
    """滚动标准差"""
    return df.rolling(window).std()

def correlation(x, y, window=10):
    """滚动相关系数"""
    return x.rolling(window).corr(y)

def ts_rank(df, window=10):
    """滚动排名"""
    return df.rolling(window).apply(lambda x: rankdata(x)[-1])

def delta(df, period=1):
    """差分"""
    return df.diff(period)

def delay(df, period=1):
    """滞后"""
    return df.shift(period)

def rank(df):
    """截面排名"""
    return df.rank(pct=True)

def scale(df, k=1):
    """缩放时间序列"""
    return df.mul(k).div(np.abs(df).sum())

def ts_argmax(df, window=10):
    """滚动最大值出现的位置"""
    return df.rolling(window).apply(np.argmax) + 1

def ts_argmin(df, window=10):
    """滚动最小值出现的位置"""
    return df.rolling(window).apply(np.argmin) + 1

def sign(df):
    """符号函数"""
    return np.sign(df)

def decay_linear(df, period=10):
    """线性加权移动平均"""
    if df.isnull().values.any():
        df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
    na_lwma = np.zeros(len(df))
    na_lwma[:period] = df.iloc[:period]
    na_series = df.values
    divisor = period * (period + 1) / 2
    y = (np.arange(period) + 1) * 1.0 / divisor
    for row in range(period - 1, len(df)):
        x = na_series[row - period + 1: row + 1]
        na_lwma[row] = np.dot(x, y)
    return pd.Series(na_lwma, index=df.index)


# ============ Alpha101 因子类 ============

class Alpha101Factor(Factor):
    """Alpha101 因子基类"""
    category = "alpha101"
    references = ["Kakushadze, Z. (2015). 101 Formulaic Alphas"]


@register_factor
class Alpha001(Alpha101Factor):
    """Alpha#1: 波动率加权动量"""
    id = "alpha_001"
    name = "Alpha#1"
    description = "波动率加权动量因子"
    formula = "(rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) -0.5)"
    parameters = {"window": 20}
    
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


@register_factor
class Alpha002(Alpha101Factor):
    """Alpha#2: 价差反转因子"""
    id = "alpha_002"
    name = "Alpha#2"
    description = "价差反转因子"
    formula = "(-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))"
    parameters = {"window": 6}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                vol = stock_data['vol']
                close = stock_data['close']
                open_ = stock_data['open']
                delta_vol = delta(np.log(vol + 1), 2)
                price_change = (close - open_) / open_
                corr = correlation(rank(delta_vol), rank(price_change), 6).iloc[-1]
                result[ts_code] = float(-corr) if not np.isnan(corr) else 0
        return pd.Series(result)


@register_factor
class Alpha003(Alpha101Factor):
    """Alpha#3: 价格排序因子"""
    id = "alpha_003"
    name = "Alpha#3"
    description = "价格排序因子"
    formula = "(-1 * correlation(rank(open), rank(delay(volume, 1)), 10))"
    parameters = {"window": 10}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 12:
                open_ = stock_data['open']
                vol = stock_data['vol']
                corr = correlation(rank(open_), rank(delay(vol, 1)), 10).iloc[-1]
                result[ts_code] = float(-corr) if not np.isnan(corr) else 0
        return pd.Series(result)


@register_factor
class Alpha004(Alpha101Factor):
    """Alpha#4: 收益排序因子"""
    id = "alpha_004"
    name = "Alpha#4"
    description = "收益排序因子"
    formula = "(-1 * Ts_Rank(rank(low), 10))"
    parameters = {"window": 10}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                low = stock_data['low']
                factor_val = -ts_rank(rank(low), 10).iloc[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)


@register_factor
class Alpha005(Alpha101Factor):
    """Alpha#5: 量价相关性因子"""
    id = "alpha_005"
    name = "Alpha#5"
    description = "量价相关性因子"
    formula = "(rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap)))))"
    parameters = {"window": 10}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                open_ = stock_data['open']
                close = stock_data['close']
                vwap = stock_data.get('vwap', (stock_data['high'] + stock_data['low'] + close) / 3)
                avg_vwap = sma(vwap, 10)
                factor_val = rank(open_ - avg_vwap).iloc[-1] * (-abs(rank(close - vwap))).iloc[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)


@register_factor
class Alpha006(Alpha101Factor):
    """Alpha#6: 开盘价排序因子"""
    id = "alpha_006"
    name = "Alpha#6"
    description = "开盘价排序因子"
    formula = "(-1 * correlation(open, volume, 10))"
    parameters = {"window": 10}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 10:
                corr = correlation(stock_data['open'], stock_data['vol'], 10).iloc[-1]
                result[ts_code] = float(-corr) if not np.isnan(corr) else 0
        return pd.Series(result)


@register_factor
class Alpha007(Alpha101Factor):
    """Alpha#7: 量价动量因子"""
    id = "alpha_007"
    name = "Alpha#7"
    description = "量价动量因子"
    formula = "((adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : (-1 * 1))"
    parameters = {"window1": 20, "window2": 60}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 70:
                close = stock_data['close']
                vol = stock_data['vol']
                adv20 = sma(vol, 20)
                delta_close = delta(close, 7)
                factor_val = np.where(
                    adv20 < vol,
                    -ts_rank(abs(delta_close), 60) * sign(delta_close),
                    -1
                )[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)


@register_factor
class Alpha008(Alpha101Factor):
    """Alpha#8: 收益动量因子"""
    id = "alpha_008"
    name = "Alpha#8"
    description = "收益动量因子"
    formula = "(-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)), 10))))"
    parameters = {"window1": 5, "window2": 10}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 15:
                open_ = stock_data['open']
                returns = stock_data['pct_chg'] / 100
                sum_open_ret = sma(open_, 5) * sma(returns, 5)
                factor_val = -rank(sum_open_ret - delay(sum_open_ret, 10)).iloc[-1]
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)


@register_factor
class Alpha009(Alpha101Factor):
    """Alpha#9: 波动率因子"""
    id = "alpha_009"
    name = "Alpha#9"
    description = "波动率因子"
    formula = "((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1))))"
    parameters = {"window": 5}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 6:
                close = stock_data['close']
                d = delta(close, 1)
                min_d = ts_min(d, 5)
                max_d = ts_max(d, 5)
                current_d = d.iloc[-1]
                if min_d.iloc[-1] > 0:
                    factor_val = current_d
                elif max_d.iloc[-1] < 0:
                    factor_val = current_d
                else:
                    factor_val = -current_d
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)


@register_factor
class Alpha010(Alpha101Factor):
    """Alpha#10: 收益波动因子"""
    id = "alpha_010"
    name = "Alpha#10"
    description = "收益波动因子"
    formula = "rank(((0 < ts_min(delta(close, 1), 4)) ? sign(delta(close, 1)) : sign(ts_min(delta(close, 1), 4))))"
    parameters = {"window": 4}
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        result = {}
        for ts_code in data['ts_code'].unique():
            stock_data = data[data['ts_code'] == ts_code].sort_values('trade_date')
            if len(stock_data) >= 5:
                close = stock_data['close']
                d = delta(close, 1)
                min_d = ts_min(d, 4)
                current_d = d.iloc[-1]
                if min_d.iloc[-1] > 0:
                    factor_val = np.sign(current_d)
                else:
                    factor_val = np.sign(min_d.iloc[-1])
                result[ts_code] = float(factor_val) if not np.isnan(factor_val) else 0
        return pd.Series(result)


# 注册更多 Alpha101 因子...
# 由于篇幅限制，这里只展示前10个，完整实现见原 alpha101_definitions.py


__all__ = [
    'Alpha001', 'Alpha002', 'Alpha003', 'Alpha004', 'Alpha005',
    'Alpha006', 'Alpha007', 'Alpha008', 'Alpha009', 'Alpha010',
]
