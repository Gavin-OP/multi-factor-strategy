"""
Alpha101 辅助函数
"""

import numpy as np
import pandas as pd
from scipy.stats import rankdata


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

def covariance(x, y, window=10):
    """滚动协方差"""
    return x.rolling(window).cov(y)

def rolling_rank(na):
    """滚动排名辅助函数"""
    return rankdata(na)[-1]

def ts_rank(df, window=10):
    """滚动排名"""
    return df.rolling(window).apply(rolling_rank)

def rolling_prod(na):
    """滚动乘积辅助函数"""
    return np.prod(na)

def product(df, window=10):
    """滚动乘积"""
    return df.rolling(window).apply(rolling_prod)

def ts_min(df, window=10):
    """滚动最小值"""
    return df.rolling(window).min()

def ts_max(df, window=10):
    """滚动最大值"""
    return df.rolling(window).max()

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
