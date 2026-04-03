"""
WorldQuant Alpha101 因子定义 - 完整版
基于 "101 Formulaic Alphas" by Zura Kakushadze
实现来源: https://github.com/yli188/WorldQuant_alpha101_code

注意: 部分因子需要 IndNeutralize 函数(行业中性化),这些因子在此未实现
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AlphaDefinition:
    """Alpha因子定义"""
    id: str
    name: str
    formula: str
    code: str
    description: str
    category: str
    parameters: Dict
    references: List[str]


# 辅助函数定义
HELPER_FUNCTIONS = '''
import numpy as np
import pandas as pd
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

'''


# Alpha101 因子定义
ALPHA101_DEFINITIONS: Dict[str, AlphaDefinition] = {
    "alpha_001": AlphaDefinition(
        id="alpha_001",
        name="Alpha#1",
        formula="(rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) -0.5)",
        code=HELPER_FUNCTIONS + '''
def alpha_001(close, returns, window=20):
    """
    Alpha#1: 波动率加权动量
    
    逻辑: 当收益为负时使用波动率，否则使用收盘价，
         找出过去5天中最大值的位置并排名
    """
    inner = close.copy()
    inner[returns < 0] = stddev(returns, window)
    return rank(ts_argmax(inner ** 2, 5))
''',
        description="波动率加权动量因子，下跌时关注波动率，上涨时关注价格",
        category="动量因子",
        parameters={"window": 20},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_002": AlphaDefinition(
        id="alpha_002",
        name="Alpha#2",
        formula="(-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))",
        code=HELPER_FUNCTIONS + '''
def alpha_002(open_price, close, volume):
    """
    Alpha#2: 成交量变化与日内收益的相关性
    
    逻辑: 成交量对数变化与日内收益的相关性取反
    """
    log_vol_delta = np.log(volume + 1).diff(2)
    intraday_return = (close - open_price) / open_price
    df = -1 * correlation(rank(log_vol_delta), rank(intraday_return), 6)
    return df.replace([-np.inf, np.inf], 0).fillna(0)
''',
        description="成交量变化与日内收益的负相关因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_003": AlphaDefinition(
        id="alpha_003",
        name="Alpha#3",
        formula="(-1 * correlation(rank(open), rank(volume), 10))",
        code=HELPER_FUNCTIONS + '''
def alpha_003(open_price, volume):
    """
    Alpha#3: 开盘价与成交量的相关性
    
    逻辑: 开盘价排名与成交量排名的负相关
    """
    df = -1 * correlation(rank(open_price), rank(volume), 10)
    return df.replace([-np.inf, np.inf], 0).fillna(0)
''',
        description="开盘价与成交量的负相关因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_004": AlphaDefinition(
        id="alpha_004",
        name="Alpha#4",
        formula="(-1 * Ts_Rank(rank(low), 9))",
        code=HELPER_FUNCTIONS + '''
def alpha_004(low):
    """
    Alpha#4: 最低价时序排名
    
    逻辑: 最低价排名的时序排名取反
    """
    return -1 * ts_rank(rank(low), 9)
''',
        description="最低价的时序排名反转因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_005": AlphaDefinition(
        id="alpha_005",
        name="Alpha#5",
        formula="(rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap)))))",
        code=HELPER_FUNCTIONS + '''
def alpha_005(open_price, close, vwap):
    """
    Alpha#5: 开盘价与均价偏离度
    
    逻辑: 开盘价相对均价的偏离与日内振幅的交互
    """
    avg_vwap = sma(vwap, 10)
    open_deviation = rank(open_price - avg_vwap)
    close_deviation = -1 * abs(rank(close - vwap))
    return open_deviation * close_deviation
''',
        description="开盘价与均价偏离度因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_006": AlphaDefinition(
        id="alpha_006",
        name="Alpha#6",
        formula="(-1 * correlation(open, volume, 10))",
        code=HELPER_FUNCTIONS + '''
def alpha_006(open_price, volume):
    """
    Alpha#6: 开盘价与成交量相关性
    """
    df = -1 * correlation(open_price, volume, 10)
    return df.replace([-np.inf, np.inf], 0).fillna(0)
''',
        description="开盘价与成交量的简单负相关因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_007": AlphaDefinition(
        id="alpha_007",
        name="Alpha#7",
        formula="((adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : (-1* 1))",
        code=HELPER_FUNCTIONS + '''
def alpha_007(close, volume):
    """
    Alpha#7: 条件性价格动量
    
    逻辑: 成交量放大时，考虑价格变化的时序排名方向
    """
    adv20 = sma(volume, 20)
    alpha = -1 * ts_rank(abs(delta(close, 7)), 60) * sign(delta(close, 7))
    alpha[adv20 >= volume] = -1
    return alpha
''',
        description="成交量放大时的条件性价格动量因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_008": AlphaDefinition(
        id="alpha_008",
        name="Alpha#8",
        formula="(-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)),10))))",
        code=HELPER_FUNCTIONS + '''
def alpha_008(open_price, returns):
    """
    Alpha#8: 开盘价与收益的滞后差异
    """
    product = ts_sum(open_price, 5) * ts_sum(returns, 5)
    diff = product - delay(product, 10)
    return -1 * rank(diff)
''',
        description="开盘价与收益乘积的滞后差异因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_009": AlphaDefinition(
        id="alpha_009",
        name="Alpha#9",
        formula="((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1))))",
        code=HELPER_FUNCTIONS + '''
def alpha_009(close):
    """
    Alpha#9: 条件性日收益
    
    逻辑: 如果过去5天最小日收益为正，则取当日收益；
         如果过去5天最大日收益为负，则取当日收益；
         否则取当日收益的反
    """
    delta_close = delta(close, 1)
    cond_1 = ts_min(delta_close, 5) > 0
    cond_2 = ts_max(delta_close, 5) < 0
    alpha = -1 * delta_close
    alpha[cond_1 | cond_2] = delta_close[cond_1 | cond_2]
    return alpha
''',
        description="基于历史日收益的条件性因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_010": AlphaDefinition(
        id="alpha_010",
        name="Alpha#10",
        formula="rank(((0 < ts_min(delta(close, 1), 4)) ? delta(close, 1) : ((ts_max(delta(close, 1), 4) < 0)? delta(close, 1) : (-1 * delta(close, 1)))))",
        code=HELPER_FUNCTIONS + '''
def alpha_010(close):
    """
    Alpha#10: 条件性日收益排名
    """
    delta_close = delta(close, 1)
    cond_1 = ts_min(delta_close, 4) > 0
    cond_2 = ts_max(delta_close, 4) < 0
    alpha = -1 * delta_close
    alpha[cond_1 | cond_2] = delta_close[cond_1 | cond_2]
    return rank(alpha)
''',
        description="基于历史日收益的条件性排名因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_011": AlphaDefinition(
        id="alpha_011",
        name="Alpha#11",
        formula="((rank(ts_max((vwap - close), 3)) + rank(ts_min((vwap - close), 3))) * rank(delta(volume, 3)))",
        code=HELPER_FUNCTIONS + '''
def alpha_011(close, volume, vwap):
    """
    Alpha#11: VWAP偏离与成交量变化
    """
    vwap_diff = vwap - close
    return (rank(ts_max(vwap_diff, 3)) + rank(ts_min(vwap_diff, 3))) * rank(delta(volume, 3))
''',
        description="VWAP偏离与成交量变化组合因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_012": AlphaDefinition(
        id="alpha_012",
        name="Alpha#12",
        formula="(sign(delta(volume, 1)) * (-1 * delta(close, 1)))",
        code=HELPER_FUNCTIONS + '''
def alpha_012(close, volume):
    """
    Alpha#12: 成交量方向与价格变化
    """
    return sign(delta(volume, 1)) * (-1 * delta(close, 1))
''',
        description="成交量方向与价格变化因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_013": AlphaDefinition(
        id="alpha_013",
        name="Alpha#13",
        formula="(-1 * rank(covariance(rank(close), rank(volume), 5)))",
        code=HELPER_FUNCTIONS + '''
def alpha_013(close, volume):
    """
    Alpha#13: 收盘价与成交量的协方差排名
    """
    return -1 * rank(covariance(rank(close), rank(volume), 5))
''',
        description="收盘价与成交量的协方差排名因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_014": AlphaDefinition(
        id="alpha_014",
        name="Alpha#14",
        formula="((-1 * rank(delta(returns, 3))) * correlation(open, volume, 10))",
        code=HELPER_FUNCTIONS + '''
def alpha_014(open_price, returns, volume):
    """
    Alpha#14: 收益变化与开仓量相关性
    """
    df = correlation(open_price, volume, 10)
    df = df.replace([-np.inf, np.inf], 0).fillna(0)
    return -1 * rank(delta(returns, 3)) * df
''',
        description="收益变化与开仓量相关性因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_015": AlphaDefinition(
        id="alpha_015",
        name="Alpha#15",
        formula="(-1 * sum(rank(correlation(rank(high), rank(volume), 3)), 3))",
        code=HELPER_FUNCTIONS + '''
def alpha_015(high, volume):
    """
    Alpha#15: 高价与成交量相关性之和
    """
    df = correlation(rank(high), rank(volume), 3)
    df = df.replace([-np.inf, np.inf], 0).fillna(0)
    return -1 * ts_sum(rank(df), 3)
''',
        description="高价与成交量相关性之和因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_016": AlphaDefinition(
        id="alpha_016",
        name="Alpha#16",
        formula="(-1 * rank(covariance(rank(high), rank(volume), 5)))",
        code=HELPER_FUNCTIONS + '''
def alpha_016(high, volume):
    """
    Alpha#16: 高价与成交量协方差排名
    """
    return -1 * rank(covariance(rank(high), rank(volume), 5))
''',
        description="高价与成交量协方差排名因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_017": AlphaDefinition(
        id="alpha_017",
        name="Alpha#17",
        formula="(((-1 * rank(ts_rank(close, 10))) * rank(delta(delta(close, 1), 1))) * rank(ts_rank((volume / adv20), 5)))",
        code=HELPER_FUNCTIONS + '''
def alpha_017(close, volume):
    """
    Alpha#17: 多重排名组合因子
    """
    adv20 = sma(volume, 20)
    return -1 * (rank(ts_rank(close, 10)) * rank(delta(delta(close, 1), 1)) * rank(ts_rank(volume / adv20, 5)))
''',
        description="多重排名组合因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_018": AlphaDefinition(
        id="alpha_018",
        name="Alpha#18",
        formula="(-1 * rank(((stddev(abs((close - open)), 5) + (close - open)) + correlation(close, open,10))))",
        code=HELPER_FUNCTIONS + '''
def alpha_018(open_price, close):
    """
    Alpha#18: 日内波动与相关性组合
    """
    df = correlation(close, open_price, 10)
    df = df.replace([-np.inf, np.inf], 0).fillna(0)
    return -1 * rank((stddev(abs(close - open_price), 5) + (close - open_price)) + df)
''',
        description="日内波动与相关性组合因子",
        category="波动因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_019": AlphaDefinition(
        id="alpha_019",
        name="Alpha#19",
        formula="((-1 * sign(((close - delay(close, 7)) + delta(close, 7)))) * (1 + rank((1 + sum(returns,250)))))",
        code=HELPER_FUNCTIONS + '''
def alpha_019(close, returns):
    """
    Alpha#19: 长期收益趋势因子
    """
    sign_val = sign((close - delay(close, 7)) + delta(close, 7))
    rank_val = 1 + rank(1 + ts_sum(returns, 250))
    return -1 * sign_val * rank_val
''',
        description="长期收益趋势因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_020": AlphaDefinition(
        id="alpha_020",
        name="Alpha#20",
        formula="(((-1 * rank((open - delay(high, 1)))) * rank((open - delay(close, 1)))) * rank((open - delay(low, 1))))",
        code=HELPER_FUNCTIONS + '''
def alpha_020(open_price, high, low, close):
    """
    Alpha#20: 开盘价与历史价格关系
    """
    return -1 * (rank(open_price - delay(high, 1)) * rank(open_price - delay(close, 1)) * rank(open_price - delay(low, 1)))
''',
        description="开盘价与历史价格关系因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_021": AlphaDefinition(
        id="alpha_021",
        name="Alpha#21",
        formula="((((sum(close, 8) / 8) + stddev(close, 8)) < (sum(close, 2) / 2)) ? (-1 * 1) : (((sum(close,2) / 2) < ((sum(close, 8) / 8) - stddev(close, 8))) ? 1 : (((1 < (volume / adv20)) || ((volume /adv20) == 1)) ? 1 : (-1 * 1))))",
        code=HELPER_FUNCTIONS + '''
def alpha_021(close, volume):
    """
    Alpha#21: 均值偏离与成交量组合
    """
    adv20 = sma(volume, 20)
    cond_1 = sma(close, 8) + stddev(close, 8) < sma(close, 2)
    cond_2 = sma(volume, 20) / volume < 1
    alpha = pd.Series(np.ones(len(close)), index=close.index)
    alpha[cond_1 | cond_2] = -1
    return alpha
''',
        description="均值偏离与成交量组合因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_022": AlphaDefinition(
        id="alpha_022",
        name="Alpha#22",
        formula="(-1 * (delta(correlation(high, volume, 5), 5) * rank(stddev(close, 20))))",
        code=HELPER_FUNCTIONS + '''
def alpha_022(high, close, volume):
    """
    Alpha#22: 高价成交量相关性变化
    """
    df = correlation(high, volume, 5)
    df = df.replace([-np.inf, np.inf], 0).fillna(0)
    return -1 * delta(df, 5) * rank(stddev(close, 20))
''',
        description="高价成交量相关性变化因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_023": AlphaDefinition(
        id="alpha_023",
        name="Alpha#23",
        formula="(((sum(high, 20) / 20) < high) ? (-1 * delta(high, 2)) : 0)",
        code=HELPER_FUNCTIONS + '''
def alpha_023(high):
    """
    Alpha#23: 高价突破因子
    """
    cond = sma(high, 20) < high
    alpha = pd.Series(0.0, index=high.index)
    alpha[cond] = -1 * delta(high, 2)[cond].fillna(0)
    return alpha
''',
        description="高价突破因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_024": AlphaDefinition(
        id="alpha_024",
        name="Alpha#24",
        formula="((((delta((sum(close, 100) / 100), 100) / delay(close, 100)) < 0.05) || ((delta((sum(close, 100) / 100), 100) / delay(close, 100)) == 0.05)) ? (-1 * (close - ts_min(close,100))) : (-1 * delta(close, 3)))",
        code=HELPER_FUNCTIONS + '''
def alpha_024(close):
    """
    Alpha#24: 长期趋势判断因子
    """
    cond = delta(sma(close, 100), 100) / delay(close, 100) <= 0.05
    alpha = -1 * delta(close, 3)
    alpha[cond] = -1 * (close - ts_min(close, 100))
    return alpha
''',
        description="长期趋势判断因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_025": AlphaDefinition(
        id="alpha_025",
        name="Alpha#25",
        formula="rank(((((-1 * returns) * adv20) * vwap) * (high - close)))",
        code=HELPER_FUNCTIONS + '''
def alpha_025(close, high, returns, volume, vwap):
    """
    Alpha#25: 收益与成交额组合
    """
    adv20 = sma(volume, 20)
    return rank((((-1 * returns) * adv20) * vwap) * (high - close))
''',
        description="收益与成交额组合因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_026": AlphaDefinition(
        id="alpha_026",
        name="Alpha#26",
        formula="(-1 * ts_max(correlation(ts_rank(volume, 5), ts_rank(high, 5), 5), 3))",
        code=HELPER_FUNCTIONS + '''
def alpha_026(high, volume):
    """
    Alpha#26: 成交量高价相关性最大值
    """
    df = correlation(ts_rank(volume, 5), ts_rank(high, 5), 5)
    df = df.replace([-np.inf, np.inf], 0).fillna(0)
    return -1 * ts_max(df, 3)
''',
        description="成交量高价相关性最大值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_027": AlphaDefinition(
        id="alpha_027",
        name="Alpha#27",
        formula="((0.5 < rank((sum(correlation(rank(volume), rank(vwap), 6), 2) / 2.0))) ? (-1 * 1) : 1)",
        code=HELPER_FUNCTIONS + '''
def alpha_027(volume, vwap):
    """
    Alpha#27: 成交量VWAP相关性阈值
    """
    corr_val = correlation(rank(volume), rank(vwap), 6)
    alpha = rank(sma(corr_val, 2))
    alpha[alpha > 0.5] = -1
    alpha[alpha <= 0.5] = 1
    return alpha
''',
        description="成交量VWAP相关性阈值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_028": AlphaDefinition(
        id="alpha_028",
        name="Alpha#28",
        formula="scale(((correlation(adv20, low, 5) + ((high + low) / 2)) - close))",
        code=HELPER_FUNCTIONS + '''
def alpha_028(high, low, close, volume):
    """
    Alpha#28: 均价与相关性组合
    """
    adv20 = sma(volume, 20)
    df = correlation(adv20, low, 5)
    df = df.replace([-np.inf, np.inf], 0).fillna(0)
    return scale(((df + ((high + low) / 2)) - close))
''',
        description="均价与相关性组合因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_029": AlphaDefinition(
        id="alpha_029",
        name="Alpha#29",
        formula="(min(product(rank(rank(scale(log(sum(ts_min(rank(rank((-1 * rank(delta((close - 1),5))))), 2), 1))))), 1), 5) + ts_rank(delay((-1 * returns), 6), 5))",
        code=HELPER_FUNCTIONS + '''
def alpha_029(close, returns):
    """
    Alpha#29: 复杂排名组合因子
    """
    inner = -1 * rank(delta(close - 1, 5))
    p1 = ts_min(rank(rank(scale(np.log(ts_sum(rank(rank(inner)), 2))))), 5)
    p2 = ts_rank(delay(-1 * returns, 6), 5)
    return p1 + p2
''',
        description="复杂排名组合因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_030": AlphaDefinition(
        id="alpha_030",
        name="Alpha#30",
        formula="(((1.0 - rank(((sign((close - delay(close, 1))) + sign((delay(close, 1) - delay(close, 2)))) + sign((delay(close, 2) - delay(close, 3)))))) * sum(volume, 5)) / sum(volume, 20))",
        code=HELPER_FUNCTIONS + '''
def alpha_030(close, volume):
    """
    Alpha#30: 价格趋势与成交量
    """
    delta_close = delta(close, 1)
    inner = sign(delta_close) + sign(delay(delta_close, 1)) + sign(delay(delta_close, 2))
    return ((1.0 - rank(inner)) * ts_sum(volume, 5)) / ts_sum(volume, 20)
''',
        description="价格趋势与成交量因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_031": AlphaDefinition(
        id="alpha_031",
        name="Alpha#31",
        formula="((rank(rank(rank(decay_linear((-1 * rank(rank(delta(close, 10)))), 10)))) + rank((-1 * delta(close, 3)))) + sign(scale(correlation(adv20, low, 12))))",
        code=HELPER_FUNCTIONS + '''
def alpha_031(close, low, volume):
    """
    Alpha#31: 多重组合因子
    """
    adv20 = sma(volume, 20)
    df = correlation(adv20, low, 12).replace([-np.inf, np.inf], 0).fillna(0)
    p1 = rank(rank(rank(decay_linear((-1 * rank(rank(delta(close, 10)))), 10))))
    p2 = rank(-1 * delta(close, 3))
    p3 = sign(scale(df))
    return p1 + p2 + p3
''',
        description="多重组合因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_032": AlphaDefinition(
        id="alpha_032",
        name="Alpha#32",
        formula="scale(((sum(close, 7) / 7) - close)) + (20 * scale(correlation(vwap, delay(close, 5), 230)))",
        code=HELPER_FUNCTIONS + '''
def alpha_032(close, vwap):
    """
    Alpha#32: 均值偏离与长期相关性
    """
    return scale(sma(close, 7) - close) + (20 * scale(correlation(vwap, delay(close, 5), 230)))
''',
        description="均值偏离与长期相关性因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_033": AlphaDefinition(
        id="alpha_033",
        name="Alpha#33",
        formula="rank((-1 * ((1 - (open / close))^1)))",
        code=HELPER_FUNCTIONS + '''
def alpha_033(open_price, close):
    """
    Alpha#33: 日内收益排名
    """
    return rank(-1 + (open_price / close))
''',
        description="日内收益排名因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_034": AlphaDefinition(
        id="alpha_034",
        name="Alpha#34",
        formula="rank(((1 - rank((stddev(returns, 2) / stddev(returns, 5)))) + (1 - rank(delta(close, 1)))))",
        code=HELPER_FUNCTIONS + '''
def alpha_034(close, returns):
    """
    Alpha#34: 波动率比率与价格变化
    """
    inner = stddev(returns, 2) / stddev(returns, 5)
    inner = inner.replace([-np.inf, np.inf], 1).fillna(1)
    return rank(2 - rank(inner) - rank(delta(close, 1)))
''',
        description="波动率比率与价格变化因子",
        category="波动因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_035": AlphaDefinition(
        id="alpha_035",
        name="Alpha#35",
        formula="((Ts_Rank(volume, 32) * (1 - Ts_Rank(((close + high) - low), 16))) * (1 - Ts_Rank(returns, 32)))",
        code=HELPER_FUNCTIONS + '''
def alpha_035(high, low, close, returns, volume):
    """
    Alpha#35: 多重时序排名组合
    """
    return ((ts_rank(volume, 32) * (1 - ts_rank(close + high - low, 16))) * (1 - ts_rank(returns, 32)))
''',
        description="多重时序排名组合因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_036": AlphaDefinition(
        id="alpha_036",
        name="Alpha#36",
        formula="(((((2.21 * rank(correlation((close - open), delay(volume, 1), 15))) + (0.7 * rank((open - close)))) + (0.73 * rank(Ts_Rank(delay((-1 * returns), 6), 5)))) + rank(abs(correlation(vwap, adv20, 6)))) + (0.6 * rank((((sum(close, 200) / 200) - open) * (close - open)))))",
        code=HELPER_FUNCTIONS + '''
def alpha_036(open_price, high, low, close, returns, volume, vwap):
    """
    Alpha#36: 多因子加权组合
    """
    adv20 = sma(volume, 20)
    p1 = 2.21 * rank(correlation(close - open_price, delay(volume, 1), 15))
    p2 = 0.7 * rank(open_price - close)
    p3 = 0.73 * rank(ts_rank(delay(-1 * returns, 6), 5))
    p4 = rank(abs(correlation(vwap, adv20, 6)))
    p5 = 0.6 * rank((sma(close, 200) - open_price) * (close - open_price))
    return p1 + p2 + p3 + p4 + p5
''',
        description="多因子加权组合因子",
        category="综合因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_037": AlphaDefinition(
        id="alpha_037",
        name="Alpha#37",
        formula="(rank(correlation(delay((open - close), 1), close, 200)) + rank((open - close)))",
        code=HELPER_FUNCTIONS + '''
def alpha_037(open_price, close):
    """
    Alpha#37: 开盘收盘差相关性
    """
    return rank(correlation(delay(open_price - close, 1), close, 200)) + rank(open_price - close)
''',
        description="开盘收盘差相关性因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_038": AlphaDefinition(
        id="alpha_038",
        name="Alpha#38",
        formula="((-1 * rank(Ts_Rank(close, 10))) * rank((close / open)))",
        code=HELPER_FUNCTIONS + '''
def alpha_038(open_price, close):
    """
    Alpha#38: 收盘价时序排名与日内收益
    """
    inner = close / open_price
    inner = inner.replace([-np.inf, np.inf], 1).fillna(1)
    return -1 * rank(ts_rank(close, 10)) * rank(inner)
''',
        description="收盘价时序排名与日内收益因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_039": AlphaDefinition(
        id="alpha_039",
        name="Alpha#39",
        formula="((-1 * rank((delta(close, 7) * (1 - rank(decay_linear((volume / adv20), 9)))))) * (1 + rank(sum(returns, 250))))",
        code=HELPER_FUNCTIONS + '''
def alpha_039(close, returns, volume):
    """
    Alpha#39: 价格变化与成交量衰减
    """
    adv20 = sma(volume, 20)
    decay_val = decay_linear((volume / adv20), 9)
    return -1 * rank(delta(close, 7) * (1 - rank(decay_val))) * (1 + rank(sma(returns, 250)))
''',
        description="价格变化与成交量衰减因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_040": AlphaDefinition(
        id="alpha_040",
        name="Alpha#40",
        formula="((-1 * rank(stddev(high, 10))) * correlation(high, volume, 10))",
        code=HELPER_FUNCTIONS + '''
def alpha_040(high, volume):
    """
    Alpha#40: 高价波动与成交量相关性
    """
    return -1 * rank(stddev(high, 10)) * correlation(high, volume, 10)
''',
        description="高价波动与成交量相关性因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_041": AlphaDefinition(
        id="alpha_041",
        name="Alpha#41",
        formula="(((high * low)^0.5) - vwap)",
        code=HELPER_FUNCTIONS + '''
def alpha_041(high, low, vwap):
    """
    Alpha#41: 高低价几何平均与VWAP差
    """
    return np.sqrt(high * low) - vwap
''',
        description="高低价几何平均与VWAP差因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_042": AlphaDefinition(
        id="alpha_042",
        name="Alpha#42",
        formula="(rank((vwap - close)) / rank((vwap + close)))",
        code=HELPER_FUNCTIONS + '''
def alpha_042(close, vwap):
    """
    Alpha#42: VWAP与收盘价的比值排名
    """
    return rank(vwap - close) / rank(vwap + close)
''',
        description="VWAP与收盘价的比值排名因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_043": AlphaDefinition(
        id="alpha_043",
        name="Alpha#43",
        formula="(ts_rank((volume / adv20), 20) * ts_rank((-1 * delta(close, 7)), 8))",
        code=HELPER_FUNCTIONS + '''
def alpha_043(close, volume):
    """
    Alpha#43: 成交量相对位置与价格变化
    """
    adv20 = sma(volume, 20)
    return ts_rank(volume / adv20, 20) * ts_rank(-1 * delta(close, 7), 8)
''',
        description="成交量相对位置与价格变化因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_044": AlphaDefinition(
        id="alpha_044",
        name="Alpha#44",
        formula="(-1 * correlation(high, rank(volume), 5))",
        code=HELPER_FUNCTIONS + '''
def alpha_044(high, volume):
    """
    Alpha#44: 高价与成交量排名相关性
    """
    df = correlation(high, rank(volume), 5)
    return -1 * df.replace([-np.inf, np.inf], 0).fillna(0)
''',
        description="高价与成交量排名相关性因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_045": AlphaDefinition(
        id="alpha_045",
        name="Alpha#45",
        formula="(-1 * ((rank((sum(delay(close, 5), 20) / 20)) * correlation(close, volume, 2)) * rank(correlation(sum(close, 5), sum(close, 20), 2))))",
        code=HELPER_FUNCTIONS + '''
def alpha_045(close, volume):
    """
    Alpha#45: 多重相关性组合
    """
    df = correlation(close, volume, 2)
    df = df.replace([-np.inf, np.inf], 0).fillna(0)
    return -1 * (rank(sma(delay(close, 5), 20)) * df * rank(correlation(ts_sum(close, 5), ts_sum(close, 20), 2)))
''',
        description="多重相关性组合因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_046": AlphaDefinition(
        id="alpha_046",
        name="Alpha#46",
        formula="((0.25 < (((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10))) ? (-1 * 1) : (((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < 0) ? 1 : ((-1 * 1) * (close - delay(close, 1)))))",
        code=HELPER_FUNCTIONS + '''
def alpha_046(close):
    """
    Alpha#46: 价格趋势变化判断
    """
    inner = ((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)
    alpha = -1 * delta(close)
    alpha[inner < 0] = 1
    alpha[inner > 0.25] = -1
    return alpha
''',
        description="价格趋势变化判断因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_047": AlphaDefinition(
        id="alpha_047",
        name="Alpha#47",
        formula="((((rank((1 / close)) * volume) / adv20) * ((high * rank((high - close))) / (sum(high, 5) / 5))) - rank((vwap - delay(vwap, 5))))",
        code=HELPER_FUNCTIONS + '''
def alpha_047(high, close, volume, vwap):
    """
    Alpha#47: 多因素组合因子
    """
    adv20 = sma(volume, 20)
    p1 = (rank(1 / close) * volume) / adv20
    p2 = (high * rank(high - close)) / (sma(high, 5) / 5)
    return (p1 * p2) - rank(vwap - delay(vwap, 5))
''',
        description="多因素组合因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_049": AlphaDefinition(
        id="alpha_049",
        name="Alpha#49",
        formula="(((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < (-1 * 0.1)) ? 1 : ((-1 * 1) * (close - delay(close, 1))))",
        code=HELPER_FUNCTIONS + '''
def alpha_049(close):
    """
    Alpha#49: 趋势加速因子
    """
    inner = ((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)
    alpha = -1 * delta(close)
    alpha[inner < -0.1] = 1
    return alpha
''',
        description="趋势加速因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_050": AlphaDefinition(
        id="alpha_050",
        name="Alpha#50",
        formula="(-1 * ts_max(rank(correlation(rank(volume), rank(vwap), 5)), 5))",
        code=HELPER_FUNCTIONS + '''
def alpha_050(volume, vwap):
    """
    Alpha#50: 成交量VWAP相关性最大值
    """
    return -1 * ts_max(rank(correlation(rank(volume), rank(vwap), 5)), 5)
''',
        description="成交量VWAP相关性最大值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_051": AlphaDefinition(
        id="alpha_051",
        name="Alpha#51",
        formula="(((((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)) < (-1 * 0.05)) ? 1 : ((-1 * 1) * (close - delay(close, 1))))",
        code=HELPER_FUNCTIONS + '''
def alpha_051(close):
    """
    Alpha#51: 趋势加速因子(阈值不同)
    """
    inner = ((delay(close, 20) - delay(close, 10)) / 10) - ((delay(close, 10) - close) / 10)
    alpha = -1 * delta(close)
    alpha[inner < -0.05] = 1
    return alpha
''',
        description="趋势加速因子(阈值不同)",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_052": AlphaDefinition(
        id="alpha_052",
        name="Alpha#52",
        formula="(((-1 * ts_min(low, 5)) + delay(ts_min(low, 5), 5)) * rank(((sum(returns, 240) - sum(returns, 20)) / 220))) * ts_rank(volume, 5))",
        code=HELPER_FUNCTIONS + '''
def alpha_052(low, returns, volume):
    """
    Alpha#52: 低价变化与长期收益
    """
    return ((-1 * delta(ts_min(low, 5), 5)) * rank(((ts_sum(returns, 240) - ts_sum(returns, 20)) / 220))) * ts_rank(volume, 5)
''',
        description="低价变化与长期收益因子",
        category="动量因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_053": AlphaDefinition(
        id="alpha_053",
        name="Alpha#53",
        formula="(-1 * delta((((close - low) - (high - close)) / (close - low)), 9))",
        code=HELPER_FUNCTIONS + '''
def alpha_053(high, low, close):
    """
    Alpha#53: 日内位置变化
    """
    inner = (close - low).replace(0, 0.0001)
    return -1 * delta((((close - low) - (high - close)) / inner), 9)
''',
        description="收盘价在日内高低点位置的变化因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_054": AlphaDefinition(
        id="alpha_054",
        name="Alpha#54",
        formula="((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)))",
        code=HELPER_FUNCTIONS + '''
def alpha_054(open_price, high, low, close):
    """
    Alpha#54: 日内价格结构因子
    """
    inner = (low - high).replace(0, -0.0001)
    return -1 * (low - close) * (open_price ** 5) / (inner * (close ** 5))
''',
        description="日内价格结构因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_055": AlphaDefinition(
        id="alpha_055",
        name="Alpha#55",
        formula="(-1 * correlation(rank(((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12)))), rank(volume), 6))",
        code=HELPER_FUNCTIONS + '''
def alpha_055(high, low, close, volume):
    """
    Alpha#55: 日内位置与成交量相关性
    """
    divisor = (ts_max(high, 12) - ts_min(low, 12)).replace(0, 0.0001)
    inner = (close - ts_min(low, 12)) / divisor
    df = correlation(rank(inner), rank(volume), 6)
    return -1 * df.replace([-np.inf, np.inf], 0).fillna(0)
''',
        description="日内位置与成交量相关性因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_057": AlphaDefinition(
        id="alpha_057",
        name="Alpha#57",
        formula="(0 - (1 * ((close - vwap) / decay_linear(rank(ts_argmax(close, 30)), 2))))",
        code=HELPER_FUNCTIONS + '''
def alpha_057(close, vwap):
    """
    Alpha#57: 收盘价与VWAP偏离
    """
    return (0 - (1 * ((close - vwap) / decay_linear(rank(ts_argmax(close, 30)), 2))))
''',
        description="收盘价与VWAP偏离因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_060": AlphaDefinition(
        id="alpha_060",
        name="Alpha#60",
        formula="(0 - (1 * ((2 * scale(rank(((((close - low) - (high - close)) / (high - low)) * volume)))) - scale(rank(ts_argmax(close, 10))))))",
        code=HELPER_FUNCTIONS + '''
def alpha_060(high, low, close, volume):
    """
    Alpha#60: 日内位置与成交量加权
    """
    divisor = (high - low).replace(0, 0.0001)
    inner = ((close - low) - (high - close)) * volume / divisor
    return -((2 * scale(rank(inner))) - scale(rank(ts_argmax(close, 10))))
''',
        description="日内位置与成交量加权因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_061": AlphaDefinition(
        id="alpha_061",
        name="Alpha#61",
        formula="(rank((vwap - ts_min(vwap, 16.1219))) < rank(correlation(vwap, adv180, 17.9282)))",
        code=HELPER_FUNCTIONS + '''
def alpha_061(volume, vwap):
    """
    Alpha#61: VWAP最小值与长期相关性比较
    """
    adv180 = sma(volume, 180)
    return rank(vwap - ts_min(vwap, 16)) < rank(correlation(vwap, adv180, 18))
''',
        description="VWAP最小值与长期相关性比较因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_062": AlphaDefinition(
        id="alpha_062",
        name="Alpha#62",
        formula="((rank(correlation(vwap, sum(adv20, 22.4101), 9.91009)) < rank(((rank(open) + rank(open)) < (rank(((high + low) / 2)) + rank(high))))) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_062(open_price, high, low, volume, vwap):
    """
    Alpha#62: 多重排名比较
    """
    adv20 = sma(volume, 20)
    p1 = rank(correlation(vwap, sma(adv20, 22), 10))
    p2 = (rank(open_price) + rank(open_price)) < (rank((high + low) / 2) + rank(high))
    return (p1 < rank(p2)) * -1
''',
        description="多重排名比较因子",
        category="综合因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_064": AlphaDefinition(
        id="alpha_064",
        name="Alpha#64",
        formula="((rank(correlation(sum(((open * 0.178404) + (low * (1 - 0.178404))), 12.7054), sum(adv120, 12.7054), 16.6208)) < rank(delta(((((high + low) / 2) * 0.178404) + (vwap * (1 - 0.178404))), 3.69741))) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_064(open_price, high, low, volume, vwap):
    """
    Alpha#64: 加权价格与成交量相关性
    """
    adv120 = sma(volume, 120)
    w1 = (open_price * 0.178404) + (low * (1 - 0.178404))
    w2 = ((high + low) / 2 * 0.178404) + (vwap * (1 - 0.178404))
    p1 = rank(correlation(sma(w1, 13), sma(adv120, 13), 17))
    p2 = rank(delta(w2, 4))
    return (p1 < p2) * -1
''',
        description="加权价格与成交量相关性因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_065": AlphaDefinition(
        id="alpha_065",
        name="Alpha#65",
        formula="((rank(correlation(((open * 0.00817205) + (vwap * (1 - 0.00817205))), sum(adv60, 8.6911), 6.40374)) < rank((open - ts_min(open, 13.635)))) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_065(open_price, volume, vwap):
    """
    Alpha#65: 开盘价与VWAP加权相关性
    """
    adv60 = sma(volume, 60)
    w = (open_price * 0.00817205) + (vwap * (1 - 0.00817205))
    p1 = rank(correlation(w, sma(adv60, 9), 6))
    p2 = rank(open_price - ts_min(open_price, 14))
    return (p1 < p2) * -1
''',
        description="开盘价与VWAP加权相关性因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_066": AlphaDefinition(
        id="alpha_066",
        name="Alpha#66",
        formula="((rank(decay_linear(delta(vwap, 3.51013), 7.23052)) + Ts_Rank(decay_linear(((((low * 0.96633) + (low * (1 - 0.96633))) - vwap) / (open - ((high + low) / 2))), 11.4157), 6.72611)) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_066(open_price, high, low, vwap):
    """
    Alpha#66: VWAP变化与低价偏离
    """
    w = (low * 0.96633 + low * (1 - 0.96633) - vwap) / (open_price - (high + low) / 2)
    return (rank(decay_linear(delta(vwap, 4), 7)) + ts_rank(decay_linear(w, 11), 7)) * -1
''',
        description="VWAP变化与低价偏离因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_068": AlphaDefinition(
        id="alpha_068",
        name="Alpha#68",
        formula="((Ts_Rank(correlation(rank(high), rank(adv15), 8.91644), 13.9333) < rank(delta(((close - low) / (high - low)))) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_068(high, low, close, volume):
    """
    Alpha#68: 高价成交量相关性与日内位置
    """
    adv15 = sma(volume, 15)
    p1 = ts_rank(correlation(rank(high), rank(adv15), 9), 14)
    divisor = (high - low).replace(0, 0.0001)
    inner = (close - low) / divisor
    p2 = rank(delta(inner, 5))
    return (p1 < p2) * -1
''',
        description="高价成交量相关性与日内位置因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_071": AlphaDefinition(
        id="alpha_071",
        name="Alpha#71",
        formula="max(Ts_Rank(decay_linear(correlation(Ts_Rank(close, 3), Ts_Rank(adv180, 12), 18), 4), 16), Ts_Rank(decay_linear((rank(((low + open) - (vwap + vwap))).pow(2)), 16), 4))",
        code=HELPER_FUNCTIONS + '''
def alpha_071(open_price, low, close, volume, vwap):
    """
    Alpha#71: 双重时序排名最大值
    """
    adv180 = sma(volume, 180)
    p1 = ts_rank(decay_linear(correlation(ts_rank(close, 3), ts_rank(adv180, 12), 18), 4), 16)
    p2 = ts_rank(decay_linear((rank((low + open_price - vwap - vwap)) ** 2), 16), 4)
    return np.maximum(p1, p2)
''',
        description="双重时序排名最大值因子",
        category="综合因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_072": AlphaDefinition(
        id="alpha_072",
        name="Alpha#72",
        formula="(rank(decay_linear(correlation(((high + low) / 2), adv40, 8.93345), 10.1519)) / rank(decay_linear(correlation(Ts_Rank(vwap, 3.72469), Ts_Rank(volume, 18.5188), 6.86671), 2.95011)))",
        code=HELPER_FUNCTIONS + '''
def alpha_072(high, low, volume, vwap):
    """
    Alpha#72: 均价与成交量衰减相关性比值
    """
    adv40 = sma(volume, 40)
    p1 = rank(decay_linear(correlation((high + low) / 2, adv40, 9), 10))
    p2 = rank(decay_linear(correlation(ts_rank(vwap, 4), ts_rank(volume, 19), 7), 3))
    return p1 / p2
''',
        description="均价与成交量衰减相关性比值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_073": AlphaDefinition(
        id="alpha_073",
        name="Alpha#73",
        formula="(max(rank(decay_linear(delta(vwap, 4.72775), 2.91864)), Ts_Rank(decay_linear(((delta(((open * 0.147155) + (low * (1 - 0.147155))), 2.03608) / ((open * 0.147155) + (low * (1 - 0.147155)))) * -1), 3.33829), 16.7411)) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_073(open_price, low, vwap):
    """
    Alpha#73: VWAP变化与加权价格变化
    """
    p1 = rank(decay_linear(delta(vwap, 5), 3))
    w = (open_price * 0.147155) + (low * (1 - 0.147155))
    p2 = ts_rank(decay_linear(-1 * delta(w, 2) / w, 3), 17)
    return -1 * np.maximum(p1, p2)
''',
        description="VWAP变化与加权价格变化因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_074": AlphaDefinition(
        id="alpha_074",
        name="Alpha#74",
        formula="((rank(correlation(close, sum(adv30, 37.4843), 15.1365)) < rank(correlation(rank(((high + low) / 2)), rank(volume), 12.1098))) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_074(high, low, close, volume):
    """
    Alpha#74: 收盘价成交量相关性与均价成交量排名比较
    """
    adv30 = sma(volume, 30)
    p1 = rank(correlation(close, sma(adv30, 37), 15))
    p2 = rank(correlation(rank((high + low) / 2), rank(volume), 12))
    return (p1 < p2) * -1
''',
        description="收盘价成交量相关性与均价成交量排名比较因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_075": AlphaDefinition(
        id="alpha_075",
        name="Alpha#75",
        formula="(rank(correlation(vwap, volume, 4.24304)) < rank(correlation(rank(low), rank(adv50), 12.4443)))",
        code=HELPER_FUNCTIONS + '''
def alpha_075(low, volume, vwap):
    """
    Alpha#75: VWAP成交量与低价成交量排名比较
    """
    adv50 = sma(volume, 50)
    return rank(correlation(vwap, volume, 4)) < rank(correlation(rank(low), rank(adv50), 12))
''',
        description="VWAP成交量与低价成交量排名比较因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_076": AlphaDefinition(
        id="alpha_076",
        name="Alpha#76",
        formula="(max(rank(decay_linear(delta(vwap, 1.24283), 11.8907)), Ts_Rank(decay_linear(Ts_Rank(correlation(IndNeutralize(low, IndClass.sector), adv81, 8.38822), 19.297), 15.7763), 18.4619)) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_076(low, volume, vwap):
    """
    Alpha#76: VWAP变化与低价相关性
    """
    adv81 = sma(volume, 81)
    p1 = rank(decay_linear(delta(vwap, 1), 12))
    p2 = ts_rank(decay_linear(ts_rank(correlation(low, adv81, 8), 19), 16), 18)
    return -1 * np.maximum(p1, p2)
''',
        description="VWAP变化与低价相关性因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_077": AlphaDefinition(
        id="alpha_077",
        name="Alpha#77",
        formula="min(rank(decay_linear(((((high + low) / 2) + high) - (vwap + high)), 20.0553)), rank(decay_linear(correlation(((high + low) / 2), adv40, 3), 6)))",
        code=HELPER_FUNCTIONS + '''
def alpha_077(high, low, volume, vwap):
    """
    Alpha#77: 高价偏离与均价相关性最小值
    """
    adv40 = sma(volume, 40)
    p1 = rank(decay_linear(((high + low) / 2 + high) - (vwap + high), 20))
    p2 = rank(decay_linear(correlation((high + low) / 2, adv40, 3), 6))
    return np.minimum(p1, p2)
''',
        description="高价偏离与均价相关性最小值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_078": AlphaDefinition(
        id="alpha_078",
        name="Alpha#78",
        formula="(rank(correlation(sum(((low * 0.352233) + (vwap * (1 - 0.352233))), 19.7428), sum(adv40, 19.7428), 6.83313))^rank(correlation(rank(vwap), rank(volume), 5.77492)))",
        code=HELPER_FUNCTIONS + '''
def alpha_078(low, volume, vwap):
    """
    Alpha#78: 加权低价与成交量相关性幂次
    """
    adv40 = sma(volume, 40)
    w = (low * 0.352233) + (vwap * (1 - 0.352233))
    p1 = rank(correlation(ts_sum(w, 20), ts_sum(adv40, 20), 7))
    p2 = rank(correlation(rank(vwap), rank(volume), 6))
    return p1 ** p2
''',
        description="加权低价与成交量相关性幂次因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_081": AlphaDefinition(
        id="alpha_081",
        name="Alpha#81",
        formula="((rank(Log(product(rank((rank(correlation(vwap, sum(adv10, 49.6054), 8.47743))^4)), 14.9655))) < rank(correlation(rank(vwap), rank(volume), 5.07914))) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_081(volume, vwap):
    """
    Alpha#81: VWAP成交量相关性对数积比较
    """
    adv10 = sma(volume, 10)
    p1 = rank(np.log(product(rank(rank(correlation(vwap, ts_sum(adv10, 50), 8)) ** 4), 15)))
    p2 = rank(correlation(rank(vwap), rank(volume), 5))
    return (p1 < p2) * -1
''',
        description="VWAP成交量相关性对数积比较因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_083": AlphaDefinition(
        id="alpha_083",
        name="Alpha#83",
        formula="((rank(delay(((high - low) / (sum(close, 5) / 5)), 2)) * rank(rank(volume))) / (((high - low) / (sum(close, 5) / 5)) / (vwap - close)))",
        code=HELPER_FUNCTIONS + '''
def alpha_083(high, low, close, volume, vwap):
    """
    Alpha#83: 波动率与成交量排名比值
    """
    range_ratio = (high - low) / (ts_sum(close, 5) / 5)
    return (rank(delay(range_ratio, 2)) * rank(rank(volume))) / (range_ratio / (vwap - close))
''',
        description="波动率与成交量排名比值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_084": AlphaDefinition(
        id="alpha_084",
        name="Alpha#84",
        formula="SignedPower(Ts_Rank((vwap - ts_max(vwap, 15.3217)), 20.7127), delta(close, 4.96796))",
        code=HELPER_FUNCTIONS + '''
def alpha_084(close, vwap):
    """
    Alpha#84: VWAP排名与价格变化幂次
    """
    return np.sign(ts_rank(vwap - ts_max(vwap, 15), 21)) * np.abs(ts_rank(vwap - ts_max(vwap, 15), 21)) ** delta(close, 5)
''',
        description="VWAP排名与价格变化幂次因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_085": AlphaDefinition(
        id="alpha_085",
        name="Alpha#85",
        formula="(rank(correlation(((high * 0.876703) + (close * (1 - 0.876703))), adv30, 9.61331))^rank(correlation(Ts_Rank(((high + low) / 2), 3.70596), Ts_Rank(volume, 10.1595), 7.11408)))",
        code=HELPER_FUNCTIONS + '''
def alpha_085(high, low, close, volume):
    """
    Alpha#85: 加权高价与成交量相关性幂次
    """
    adv30 = sma(volume, 30)
    w = (high * 0.876703) + (close * (1 - 0.876703))
    p1 = rank(correlation(w, adv30, 10))
    p2 = rank(correlation(ts_rank((high + low) / 2, 4), ts_rank(volume, 10), 7))
    return p1 ** p2
''',
        description="加权高价与成交量相关性幂次因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_086": AlphaDefinition(
        id="alpha_086",
        name="Alpha#86",
        formula="((Ts_Rank(correlation(close, sum(adv20, 14.7444), 6.00049), 20.4195) < rank(((open + close) - (vwap + open)))) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_086(open_price, close, volume, vwap):
    """
    Alpha#86: 收盘价成交量相关性与日内位置比较
    """
    adv20 = sma(volume, 20)
    p1 = ts_rank(correlation(close, sma(adv20, 15), 6), 20)
    p2 = rank((open_price + close) - (vwap + open_price))
    return (p1 < p2) * -1
''',
        description="收盘价成交量相关性与日内位置比较因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_088": AlphaDefinition(
        id="alpha_088",
        name="Alpha#88",
        formula="min(rank(decay_linear(((rank(open) + rank(low)) - (rank(high) + rank(close))), 8.06882)), Ts_Rank(decay_linear(correlation(Ts_Rank(close, 8.44728), Ts_Rank(adv60, 20.6966), 8.01266), 6.65053), 2.61957))",
        code=HELPER_FUNCTIONS + '''
def alpha_088(open_price, high, low, close, volume):
    """
    Alpha#88: 开盘低价与高价收盘排名差最小值
    """
    adv60 = sma(volume, 60)
    p1 = rank(decay_linear((rank(open_price) + rank(low)) - (rank(high) + rank(close)), 8))
    p2 = ts_rank(decay_linear(correlation(ts_rank(close, 8), ts_rank(adv60, 21), 8), 7), 3)
    return np.minimum(p1, p2)
''',
        description="开盘低价与高价收盘排名差最小值因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_092": AlphaDefinition(
        id="alpha_092",
        name="Alpha#92",
        formula="min(Ts_Rank(decay_linear(((((high + low) / 2) + close) < (low + open)), 14.7221), 18.8683), Ts_Rank(decay_linear(correlation(rank(low), rank(adv30), 7.58555), 6.94024), 6.80584))",
        code=HELPER_FUNCTIONS + '''
def alpha_092(open_price, high, low, close, volume):
    """
    Alpha#92: 日内位置条件与低价成交量相关性最小值
    """
    adv30 = sma(volume, 30)
    p1 = ts_rank(decay_linear(((high + low) / 2 + close) < (low + open_price), 15), 19)
    p2 = ts_rank(decay_linear(correlation(rank(low), rank(adv30), 8), 7), 7)
    return np.minimum(p1, p2)
''',
        description="日内位置条件与低价成交量相关性最小值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_094": AlphaDefinition(
        id="alpha_094",
        name="Alpha#94",
        formula="((rank((vwap - ts_min(vwap, 11.5783))^Ts_Rank(correlation(Ts_Rank(vwap, 19.6462), Ts_Rank(adv60, 4.02992), 18.0926), 2.70756)) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_094(volume, vwap):
    """
    Alpha#94: VWAP最小值与相关性排名幂次
    """
    adv60 = sma(volume, 60)
    p1 = rank(vwap - ts_min(vwap, 12))
    p2 = ts_rank(correlation(ts_rank(vwap, 20), ts_rank(adv60, 4), 18), 3)
    return (p1 ** p2) * -1
''',
        description="VWAP最小值与相关性排名幂次因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_095": AlphaDefinition(
        id="alpha_095",
        name="Alpha#95",
        formula="(rank((open - ts_min(open, 12.4105))) < Ts_Rank((rank(correlation(sum(((high + low) / 2), 19.1351), sum(adv40, 19.1351), 12.8742))^5), 11.7584))",
        code=HELPER_FUNCTIONS + '''
def alpha_095(open_price, high, low, volume):
    """
    Alpha#95: 开盘价最小值与均价成交量相关性比较
    """
    adv40 = sma(volume, 40)
    p1 = rank(open_price - ts_min(open_price, 12))
    p2 = ts_rank(rank(correlation(sma((high + low) / 2, 19), sma(adv40, 19), 13)) ** 5, 12)
    return p1 < p2
''',
        description="开盘价最小值与均价成交量相关性比较因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_096": AlphaDefinition(
        id="alpha_096",
        name="Alpha#96",
        formula="(max(Ts_Rank(decay_linear(correlation(rank(vwap), rank(volume), 3.83878), 4.16783), 8.38151), Ts_Rank(decay_linear(Ts_ArgMax(correlation(Ts_Rank(close, 7.45404), Ts_Rank(adv60, 4.13242), 3.65459), 12.6556), 14.0365), 13.4143)) * -1)",
        code=HELPER_FUNCTIONS + '''
def alpha_096(close, volume, vwap):
    """
    Alpha#96: VWAP成交量相关性与收盘价成交量相关性最大值
    """
    adv60 = sma(volume, 60)
    p1 = ts_rank(decay_linear(correlation(rank(vwap), rank(volume), 4), 4), 8)
    p2 = ts_rank(decay_linear(ts_argmax(correlation(ts_rank(close, 7), ts_rank(adv60, 4), 4), 13), 14), 13)
    return -1 * np.maximum(p1, p2)
''',
        description="VWAP成交量相关性与收盘价成交量相关性最大值因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_098": AlphaDefinition(
        id="alpha_098",
        name="Alpha#98",
        formula="(rank(decay_linear(correlation(vwap, sum(adv5, 26.4719), 4.58418), 7.18088)) - rank(decay_linear(Ts_Rank(Ts_ArgMin(correlation(rank(open), rank(adv15), 20.8187), 8.62571), 6.95668), 8.07206)))",
        code=HELPER_FUNCTIONS + '''
def alpha_098(open_price, volume, vwap):
    """
    Alpha#98: VWAP成交量相关性与开盘价成交量相关性差
    """
    adv5 = sma(volume, 5)
    adv15 = sma(volume, 15)
    p1 = rank(decay_linear(correlation(vwap, sma(adv5, 26), 5), 7))
    p2 = rank(decay_linear(ts_rank(ts_argmin(correlation(rank(open_price), rank(adv15), 21), 9), 7), 8))
    return p1 - p2
''',
        description="VWAP成交量相关性与开盘价成交量相关性差因子",
        category="量价因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),

    "alpha_101": AlphaDefinition(
        id="alpha_101",
        name="Alpha#101",
        formula="((close - open) / ((high - low) + 0.001))",
        code=HELPER_FUNCTIONS + '''
def alpha_101(open_price, high, low, close):
    """
    Alpha#101: 日内收益占比
    
    日内收益占日内振幅的比例,衡量收盘位置
    
    取值范围: 通常在 -1 到 1 之间
    - 接近 1: 收盘接近最高点,强势上涨
    - 接近 -1: 收盘接近最低点,弱势下跌
    - 接近 0: 收盘接近开盘,震荡
    """
    intraday_return = close - open_price
    daily_range = high - low
    return intraday_return / (daily_range + 0.001)
''',
        description="日内收益占振幅比例因子,衡量收盘位置的强度",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
}


def get_alpha101_definition(alpha_id: str) -> Optional[AlphaDefinition]:
    """获取 Alpha101 因子定义"""
    return ALPHA101_DEFINITIONS.get(alpha_id)


def list_alpha101_definitions() -> List[AlphaDefinition]:
    """列出所有 Alpha101 因子"""
    return list(ALPHA101_DEFINITIONS.values())


# 未实现的因子列表 (需要行业中性化函数 IndNeutralize)
NOT_IMPLEMENTED_ALPHAS = [
    "alpha_048",  # 需要 IndNeutralize 和 IndClass.subindustry
    "alpha_056",  # 需要 cap (市值)
    "alpha_058",  # 需要 IndNeutralize 和 IndClass.sector
    "alpha_059",  # 需要 IndNeutralize 和 IndClass.industry
    "alpha_063",  # 需要 IndNeutralize
    "alpha_067",  # 需要 IndNeutralize
    "alpha_069",  # 未在源代码中
    "alpha_070",  # 未在源代码中
    "alpha_079",  # 需要 IndNeutralize
    "alpha_080",  # 需要 IndNeutralize
    "alpha_082",  # 需要 IndNeutralize
    "alpha_087",  # 需要 IndNeutralize
    "alpha_089",  # 需要 IndNeutralize
    "alpha_090",  # 需要 IndNeutralize
    "alpha_091",  # 需要 IndNeutralize
    "alpha_093",  # 需要 IndNeutralize
    "alpha_097",  # 需要 IndNeutralize
    "alpha_099",  # 代码截断
    "alpha_100",  # 未在源代码中
]
