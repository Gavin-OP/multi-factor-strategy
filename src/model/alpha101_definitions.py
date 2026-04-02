"""
WorldQuant Alpha101 因子定义
基于 "101 Formulaic Alphas" by Zura Kakushadze
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class AlphaDefinition:
    """Alpha因子定义"""
    id: str
    name: str
    formula: str           # 原始公式
    code: str              # Python实现
    description: str
    category: str
    parameters: Dict
    references: List[str]


# WorldQuant Alpha101 因子定义
ALPHA101_DEFINITIONS: Dict[str, AlphaDefinition] = {
    "alpha_001": AlphaDefinition(
        id="alpha_001",
        name="Alpha#1",
        formula="(rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5)",
        code="""def alpha_001(close: pd.Series, returns: pd.Series, window: int = 20) -> pd.Series:
    \"\"\"
    Alpha#1: 波动率加权动量
    
    公式: (rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5)
    
    逻辑: 当收益为负时使用波动率，否则使用收盘价，找出过去5天中最大的位置
    \"\"\"
    # 计算条件值
    volatility = returns.rolling(window).std()
    condition = np.where(returns < 0, volatility, close)
    
    # SignedPower
    signed_power = np.sign(condition) * (np.abs(condition) ** 2)
    
    # Ts_ArgMax: 找过去5天最大值的位置
    result = pd.Series(index=close.index, dtype=float)
    for i in range(5, len(close)):
        window_vals = signed_power.iloc[i-5:i]
        result.iloc[i] = window_vals.idxmax() - i + 5 if len(window_vals) > 0 else np.nan
    
    # Rank并减去0.5
    return result.rank(pct=True) - 0.5


import numpy as np
import pandas as pd
""",
        description="波动率加权动量因子，下跌时关注波动率，上涨时关注价格",
        category="动量因子",
        parameters={"window": 20},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_002": AlphaDefinition(
        id="alpha_002",
        name="Alpha#2",
        formula="(-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))",
        code="""def alpha_002(open_price: pd.Series, close: pd.Series, volume: pd.Series, window: int = 6) -> pd.Series:
    \"\"\"
    Alpha#2: 成交量变化与日内收益的相关性
    
    公式: (-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))
    
    逻辑: 成交量对数变化与日内收益的相关性取反
    \"\"\"
    # 计算日内收益
    intraday_return = (close - open_price) / open_price
    
    # 成交量对数变化
    log_vol_delta = np.log(volume + 1).diff(2)
    
    # 排名
    ranked_vol = log_vol_delta.rank(pct=True)
    ranked_ret = intraday_return.rank(pct=True)
    
    # 滚动相关
    correlation = ranked_vol.rolling(window).corr(ranked_ret)
    
    return -1 * correlation


import numpy as np
import pandas as pd
""",
        description="成交量变化与日内收益的负相关因子",
        category="量价因子",
        parameters={"window": 6},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_003": AlphaDefinition(
        id="alpha_003",
        name="Alpha#3",
        formula="(-1 * correlation(rank(open), rank(volume), 10))",
        code="""def alpha_003(open_price: pd.Series, volume: pd.Series, window: int = 10) -> pd.Series:
    \"\"\"
    Alpha#3: 开盘价与成交量的相关性
    
    公式: (-1 * correlation(rank(open), rank(volume), 10))
    
    逻辑: 开盘价排名与成交量排名的负相关
    \"\"\"
    # 排名
    ranked_open = open_price.rank(pct=True)
    ranked_vol = volume.rank(pct=True)
    
    # 滚动相关
    correlation = ranked_open.rolling(window).corr(ranked_vol)
    
    return -1 * correlation


import numpy as np
import pandas as pd
""",
        description="开盘价与成交量的负相关因子，捕捉异常开盘行为",
        category="量价因子",
        parameters={"window": 10},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_004": AlphaDefinition(
        id="alpha_004",
        name="Alpha#4",
        formula="(-1 * Ts_Rank(rank(low), 9))",
        code="""def alpha_004(low: pd.Series, window: int = 9) -> pd.Series:
    \"\"\"
    Alpha#4: 最低价时序排名
    
    公式: (-1 * Ts_Rank(rank(low), 9))
    
    逻辑: 最低价在过去9天的时序排名取反
    \"\"\"
    # 先截面排名
    ranked_low = low.rank(pct=True)
    
    # 时序排名
    ts_rank = ranked_low.rolling(window).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1] if len(x) > 0 else np.nan
    )
    
    return -1 * ts_rank


import numpy as np
import pandas as pd
""",
        description="最低价的时序排名反转因子",
        category="价格因子",
        parameters={"window": 9},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_005": AlphaDefinition(
        id="alpha_005",
        name="Alpha#5",
        formula="(rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - open)))))",
        code="""def alpha_005(open_price: pd.Series, close: pd.Series, vwap: pd.Series, window: int = 10) -> pd.Series:
    \"\"\"
    Alpha#5: 开盘价与均价偏离度
    
    公式: (rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - open)))))
    
    逻辑: 开盘价相对均价的偏离与日内振幅的交互
    \"\"\"
    # 均价均值
    avg_vwap = vwap.rolling(window).mean()
    
    # 开盘价偏离
    open_deviation = open_price - avg_vwap
    
    # 日内振幅排名
    intraday_range = abs(close - open_price)
    
    # 组合
    result = open_deviation.rank(pct=True) * (-1 * intraday_range.rank(pct=True))
    
    return result


import numpy as np
import pandas as pd
""",
        description="开盘价与均价偏离度因子",
        category="价格因子",
        parameters={"window": 10},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_006": AlphaDefinition(
        id="alpha_006",
        name="Alpha#6",
        formula="(-1 * correlation(open, volume, 10))",
        code="""def alpha_006(open_price: pd.Series, volume: pd.Series, window: int = 10) -> pd.Series:
    \"\"\"
    Alpha#6: 开盘价与成交量相关性
    
    公式: (-1 * correlation(open, volume, 10))
    
    逻辑: 开盘价与成交量的负相关
    \"\"\"
    correlation = open_price.rolling(window).corr(volume)
    return -1 * correlation


import numpy as np
import pandas as pd
""",
        description="开盘价与成交量的简单负相关因子",
        category="量价因子",
        parameters={"window": 10},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_007": AlphaDefinition(
        id="alpha_007",
        name="Alpha#7",
        formula="((adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : (-1 * 1))",
        code="""def alpha_007(close: pd.Series, volume: pd.Series, adv_window: int = 20, delta_window: int = 7, ts_window: int = 60) -> pd.Series:
    \"\"\"
    Alpha#7: 条件性价格动量
    
    公式: ((adv20 < volume) ? ((-1 * ts_rank(abs(delta(close, 7)), 60)) * sign(delta(close, 7))) : (-1 * 1))
    
    逻辑: 成交量放大时，考虑价格变化的时序排名方向
    \"\"\"
    # 20日平均成交量
    adv20 = volume.rolling(adv_window).mean()
    
    # 价格变化
    delta_close = close.diff(delta_window)
    
    # 条件判断
    high_volume = volume > adv20
    
    # 时序排名
    ts_rank = delta_close.abs().rolling(ts_window).rank(pct=True)
    
    # 结果
    result = np.where(
        high_volume,
        -1 * ts_rank * np.sign(delta_close),
        -1
    )
    
    return pd.Series(result, index=close.index)


import numpy as np
import pandas as pd
""",
        description="成交量放大时的条件性价格动量因子",
        category="量价因子",
        parameters={"adv_window": 20, "delta_window": 7, "ts_window": 60},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_008": AlphaDefinition(
        id="alpha_008",
        name="Alpha#8",
        formula="(-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)), 10))))",
        code="""def alpha_008(open_price: pd.Series, returns: pd.Series, sum_window: int = 5, delay_window: int = 10) -> pd.Series:
    \"\"\"
    Alpha#8: 开盘价与收益的滞后差异
    
    公式: (-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)), 10))))
    
    逻辑: 开盘价与收益乘积的变化排名取反
    \"\"\"
    # 5日开盘价之和与收益之和的乘积
    sum_open = open_price.rolling(sum_window).sum()
    sum_returns = returns.rolling(sum_window).sum()
    product = sum_open * sum_returns
    
    # 滞后差异
    diff = product - product.shift(delay_window)
    
    # 排名取反
    return -1 * diff.rank(pct=True)


import numpy as np
import pandas as pd
""",
        description="开盘价与收益乘积的滞后差异因子",
        category="动量因子",
        parameters={"sum_window": 5, "delay_window": 10},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_009": AlphaDefinition(
        id="alpha_009",
        name="Alpha#9",
        formula="((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1))))",
        code="""def alpha_009(close: pd.Series, window: int = 5) -> pd.Series:
    \"\"\"
    Alpha#9: 条件性日收益
    
    公式: ((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ? delta(close, 1) : (-1 * delta(close, 1))))
    
    逻辑: 如果过去5天最小日收益为正，则取当日收益；
         如果过去5天最大日收益为负，则取当日收益；
         否则取当日收益的反
    \"\"\"
    # 日收益
    delta_close = close.diff(1)
    
    # 过去5天最小/最大
    ts_min = delta_close.rolling(window).min()
    ts_max = delta_close.rolling(window).max()
    
    # 条件判断
    result = np.where(
        ts_min > 0,
        delta_close,
        np.where(
            ts_max < 0,
            delta_close,
            -1 * delta_close
        )
    )
    
    return pd.Series(result, index=close.index)


import numpy as np
import pandas as pd
""",
        description="基于历史日收益的条件性因子",
        category="动量因子",
        parameters={"window": 5},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_010": AlphaDefinition(
        id="alpha_010",
        name="Alpha#10",
        formula="rank(((0 < ts_min(delta(close, 1), 4)) ? delta(close, 1) : ((ts_max(delta(close, 1), 4) < 0) ? delta(close, 1) : (-1 * delta(close, 1)))))",
        code="""def alpha_010(close: pd.Series, window: int = 4) -> pd.Series:
    \"\"\"
    Alpha#10: 条件性日收益排名
    
    公式: rank(((0 < ts_min(delta(close, 1), 4)) ? delta(close, 1) : ((ts_max(delta(close, 1), 4) < 0) ? delta(close, 1) : (-1 * delta(close, 1)))))
    
    逻辑: 类似Alpha#9，但窗口为4天，最后做排名
    \"\"\"
    # 日收益
    delta_close = close.diff(1)
    
    # 过去4天最小/最大
    ts_min = delta_close.rolling(window).min()
    ts_max = delta_close.rolling(window).max()
    
    # 条件判断
    conditional = np.where(
        ts_min > 0,
        delta_close,
        np.where(
            ts_max < 0,
            delta_close,
            -1 * delta_close
        )
    )
    
    # 排名
    return pd.Series(conditional, index=close.index).rank(pct=True)


import numpy as np
import pandas as pd
""",
        description="基于历史日收益的条件性排名因子",
        category="动量因子",
        parameters={"window": 4},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    # 添加更多经典因子
    "alpha_053": AlphaDefinition(
        id="alpha_053",
        name="Alpha#53",
        formula="(-1 * delta((((close - low) - (high - close)) / (close - low)), 9))",
        code="""def alpha_053(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 9) -> pd.Series:
    \"\"\"
    Alpha#53: 日内位置变化
    
    公式: (-1 * delta((((close - low) - (high - close)) / (close - low)), 9))
    
    逻辑: 收盘价在日内高低点之间的位置变化
    \"\"\"
    # 日内位置
    intraday_position = ((close - low) - (high - close)) / (close - low + 1e-10)
    
    # 变化
    delta = intraday_position.diff(window)
    
    return -1 * delta


import numpy as np
import pandas as pd
""",
        description="收盘价在日内高低点位置的变化因子",
        category="价格因子",
        parameters={"window": 9},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_054": AlphaDefinition(
        id="alpha_054",
        name="Alpha#54",
        formula="((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5))))",
        code="""def alpha_054(open_price: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    \"\"\"
    Alpha#54: 日内价格结构
    
    公式: ((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5))))
    
    逻辑: 复杂的日内价格结构因子
    \"\"\"
    # 避免除零
    denominator = (low - high) * (close ** 5)
    numerator = (low - close) * (open_price ** 5)
    
    result = -1 * numerator / (denominator + 1e-10)
    
    # 处理极端值
    result = result.clip(-1e6, 1e6)
    
    return result


import numpy as np
import pandas as pd
""",
        description="日内价格结构因子",
        category="价格因子",
        parameters={},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_083": AlphaDefinition(
        id="alpha_083",
        name="Alpha#83",
        formula="(-1 * correlation(high, rank(volume), 5))",
        code="""def alpha_083(high: pd.Series, volume: pd.Series, window: int = 5) -> pd.Series:
    \"\"\"
    Alpha#83: 最高价与成交量排名相关性
    
    公式: (-1 * correlation(high, rank(volume), 5))
    
    逻辑: 最高价与成交量排名的负相关
    \"\"\"
    # 成交量排名
    ranked_vol = volume.rank(pct=True)
    
    # 滚动相关
    correlation = high.rolling(window).corr(ranked_vol)
    
    return -1 * correlation


import numpy as np
import pandas as pd
""",
        description="最高价与成交量排名的负相关因子",
        category="量价因子",
        parameters={"window": 5},
        references=["Kakushadze, Z. (2015). 101 Formulaic Alphas"]
    ),
    
    "alpha_101": AlphaDefinition(
        id="alpha_101",
        name="Alpha#101",
        formula="((close - open) / ((high - low) + 0.001))",
        code="""def alpha_101(open_price: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    \"\"\"
    Alpha#101: 日内收益占比
    
    公式: ((close - open) / ((high - low) + 0.001))
    
    逻辑: 日内收益占日内振幅的比例,衡量收盘位置
    
    日内收益为正表示收盘高于开盘,为负表示收盘低于开盘.
    这个因子反映了当天的价格走势方向和强度.
    
    取值范围: 通常在 -1 到 1 之间
    - 接近 1: 收盘接近最高点,强势上涨
    - 接近 -1: 收盘接近最低点,弱势下跌
    - 接近 0: 收盘接近开盘,震荡
    \"\"\"
    # 日内收益
    intraday_return = close - open_price
    
    # 日内振幅
    daily_range = high - low
    
    # 计算比例,避免除零
    result = intraday_return / (daily_range + 0.001)
    
    return result


import numpy as np
import pandas as pd
""",
        description="日内收益占振幅比例因子，衡量收盘位置的强度",
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
