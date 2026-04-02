"""
Factor Definitions - 因子定义
包含每个因子的计算逻辑和 Python 代码
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FactorDefinition:
    """因子定义"""
    id: str
    name: str
    category: str
    description: str
    code: str
    parameters: Dict
    references: List[str]


# 因子定义字典
FACTOR_DEFINITIONS: Dict[str, FactorDefinition] = {
    "momentum_1m": FactorDefinition(
        id="momentum_1m",
        name="1月动量因子",
        category="动量因子",
        description="过去1个月的股价涨跌幅，反映短期价格趋势",
        code="""def compute_momentum_1m(close_prices: pd.Series) -> float:
    \"\"\"
    计算1月动量因子
    
    参数:
        close_prices: 收盘价序列 (需至少20个交易日)
    
    返回:
        动量值 = 收盘价_N / 收盘价_N-20 - 1
    \"\"\"
    period = 20  # 1个月约20个交易日
    if len(close_prices) < period:
        return np.nan
    
    return close_prices.iloc[-1] / close_prices.iloc[-period] - 1


def compute_momentum_1m_batch(price_df: pd.DataFrame) -> pd.Series:
    \"\"\"
    批量计算所有股票的1月动量
    
    参数:
        price_df: 包含 ts_code, trade_date, close 的DataFrame
    
    返回:
        Series: {ts_code: momentum_value}
    \"\"\"
    period = 20
    results = {}
    
    for ts_code in price_df['ts_code'].unique():
        stock_data = price_df[price_df['ts_code'] == ts_code]
        stock_data = stock_data.sort_values('trade_date')
        
        if len(stock_data) >= period:
            results[ts_code] = (
                stock_data['close'].iloc[-1] / 
                stock_data['close'].iloc[-period] - 1
            )
    
    return pd.Series(results)
""",
        parameters={"period": 20},
        references=["Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers"]
    ),
    
    "momentum_3m": FactorDefinition(
        id="momentum_3m",
        name="3月动量因子",
        category="动量因子",
        description="过去3个月的股价涨跌幅",
        code="""def compute_momentum_3m(close_prices: pd.Series) -> float:
    \"\"\"
    计算3月动量因子
    
    参数:
        close_prices: 收盘价序列 (需至少60个交易日)
    
    返回:
        动量值 = 收盘价_N / 收盘价_N-60 - 1
    \"\"\"
    period = 60  # 3个月约60个交易日
    if len(close_prices) < period:
        return np.nan
    
    return close_prices.iloc[-1] / close_prices.iloc[-period] - 1
""",
        parameters={"period": 60},
        references=["Jegadeesh, N., & Titman, S. (1993)"]
    ),
    
    "momentum_6m": FactorDefinition(
        id="momentum_6m",
        name="6月动量因子",
        category="动量因子",
        description="过去6个月的股价涨跌幅",
        code="""def compute_momentum_6m(close_prices: pd.Series) -> float:
    \"\"\"
    计算6月动量因子
    
    参数:
        close_prices: 收盘价序列 (需至少120个交易日)
    
    返回:
        动量值 = 收盘价_N / 收盘价_N-120 - 1
    \"\"\"
    period = 120  # 6个月约120个交易日
    if len(close_prices) < period:
        return np.nan
    
    return close_prices.iloc[-1] / close_prices.iloc[-period] - 1
""",
        parameters={"period": 120},
        references=["Jegadeesh, N., & Titman, S. (1993)"]
    ),
    
    "momentum_12m": FactorDefinition(
        id="momentum_12m",
        name="12月动量因子",
        category="动量因子",
        description="过去12个月的股价涨跌幅（剔除最近1月）",
        code="""def compute_momentum_12m(close_prices: pd.Series) -> float:
    \"\"\"
    计算12月动量因子（剔除最近1月，避免短期反转）
    
    参数:
        close_prices: 收盘价序列 (需至少240个交易日)
    
    返回:
        动量值 = 收盘价_N-20 / 收盘价_N-240 - 1
    \"\"\"
    lookback = 240  # 12个月
    skip = 20  # 剔除最近1个月
    
    if len(close_prices) < lookback:
        return np.nan
    
    return close_prices.iloc[-skip] / close_prices.iloc[-lookback] - 1
""",
        parameters={"period": 240, "skip": 20},
        references=["Jegadeesh, N., & Titman, S. (1993)", "Novy-Marx, R. (2012)"]
    ),
    
    "value_pe": FactorDefinition(
        id="value_pe",
        name="PE因子",
        category="价值因子",
        description="市盈率的倒数，反映估值水平",
        code="""def compute_pe_factor(pe_ratio: float) -> float:
    \"\"\"
    计算PE因子（EP = 1/PE）
    
    参数:
        pe_ratio: 市盈率 P/E
    
    返回:
        EP值 = 1 / PE
        PE为负或零时返回 NaN
    \"\"\"
    if pe_ratio is None or pe_ratio <= 0:
        return np.nan
    
    return 1.0 / pe_ratio


def compute_ep_rank(pe_series: pd.Series) -> pd.Series:
    \"\"\"
    计算EP因子的截面排名
    
    参数:
        pe_series: {ts_code: PE} 的Series
    
    返回:
        排名标准化后的因子值 [0, 1]
    \"\"\"
    ep = 1.0 / pe_series[pe_series > 0]
    # 截面排名标准化
    rank = ep.rank(pct=True)
    return rank
""",
        parameters={},
        references=["Fama, E. F., & French, K. R. (1992). The Cross-Section of Expected Stock Returns"]
    ),
    
    "value_pb": FactorDefinition(
        id="value_pb",
        name="PB因子",
        category="价值因子",
        description="市净率的倒数，反映账面价值折扣",
        code="""def compute_pb_factor(pb_ratio: float) -> float:
    \"\"\"
    计算PB因子（BP = 1/PB）
    
    参数:
        pb_ratio: 市净率 P/B
    
    返回:
        BP值 = 1 / PB
    \"\"\"
    if pb_ratio is None or pb_ratio <= 0:
        return np.nan
    
    return 1.0 / pb_ratio
""",
        parameters={},
        references=["Fama, E. F., & French, K. R. (1992)"]
    ),
    
    "quality_roe": FactorDefinition(
        id="quality_roe",
        name="ROE因子",
        category="质量因子",
        description="净资产收益率，反映公司盈利能力",
        code="""def compute_roe_factor(
    net_income: float,
    total_equity: float
) -> float:
    \"\"\"
    计算ROE因子
    
    参数:
        net_income: 净利润
        total_equity: 净资产
    
    返回:
        ROE = 净利润 / 净资产
    \"\"\"
    if total_equity is None or total_equity == 0:
        return np.nan
    
    if net_income is None:
        return np.nan
    
    return net_income / total_equity


def compute_roe_rank(
    net_income_series: pd.Series,
    equity_series: pd.Series
) -> pd.Series:
    \"\"\"
    批量计算ROE并排名
    
    参数:
        net_income_series: {ts_code: net_income}
        equity_series: {ts_code: total_equity}
    
    返回:
        排名标准化后的ROE因子
    \"\"\"
    roe = net_income_series / equity_series
    roe = roe.replace([np.inf, -np.inf], np.nan)
    
    # 截面排名
    rank = roe.rank(pct=True)
    return rank
""",
        parameters={},
        references=["Novy-Marx, R. (2013). The Other Side of Value"]
    ),
    
    "quality_roa": FactorDefinition(
        id="quality_roa",
        name="ROA因子",
        category="质量因子",
        description="总资产收益率，反映资产利用效率",
        code="""def compute_roa_factor(
    net_income: float,
    total_assets: float
) -> float:
    \"\"\"
    计算ROA因子
    
    参数:
        net_income: 净利润
        total_assets: 总资产
    
    返回:
        ROA = 净利润 / 总资产
    \"\"\"
    if total_assets is None or total_assets == 0:
        return np.nan
    
    if net_income is None:
        return np.nan
    
    return net_income / total_assets
""",
        parameters={},
        references=["Novy-Marx, R. (2013)"]
    ),
    
    "volatility_1m": FactorDefinition(
        id="volatility_1m",
        name="1月波动率因子",
        category="波动率因子",
        description="过去1个月日收益率的标准差",
        code="""def compute_volatility_1m(
    daily_returns: pd.Series
) -> float:
    \"\"\"
    计算1月波动率因子
    
    参数:
        daily_returns: 日收益率序列 (需至少20个交易日)
    
    返回:
        年化波动率 = std(daily_returns) * sqrt(252)
    \"\"\"
    period = 20
    
    if len(daily_returns) < period:
        return np.nan
    
    recent_returns = daily_returns.iloc[-period:]
    
    # 计算标准差
    std = recent_returns.std()
    
    # 年化
    annualized_vol = std * np.sqrt(252)
    
    return annualized_vol


def compute_vol_from_prices(
    close_prices: pd.Series,
    period: int = 20
) -> float:
    \"\"\"
    从价格序列计算波动率
    
    参数:
        close_prices: 收盘价序列
        period: 计算周期
    
    返回:
        年化波动率
    \"\"\"
    if len(close_prices) < period + 1:
        return np.nan
    
    # 计算日收益率
    returns = close_prices.pct_change().iloc[-period:]
    
    # 年化波动率
    return returns.std() * np.sqrt(252)
""",
        parameters={"period": 20},
        references=["Ang, A., et al. (2006). The Cross-Section of Volatility and Expected Returns"]
    ),
    
    "liquidity_turnover": FactorDefinition(
        id="liquidity_turnover",
        name="换手率因子",
        category="流动性因子",
        description="平均换手率，反映股票流动性",
        code="""def compute_turnover_factor(
    volume: pd.Series,
    shares_outstanding: float
) -> float:
    \"\"\"
    计算换手率因子
    
    参数:
        volume: 成交量序列
        shares_outstanding: 流通股本
    
    返回:
        平均换手率 = mean(volume / shares_outstanding)
    \"\"\"
    if shares_outstanding is None or shares_outstanding == 0:
        return np.nan
    
    turnover = volume / shares_outstanding
    return turnover.mean()


def compute_amihud_illiquidity(
    daily_returns: pd.Series,
    daily_amount: pd.Series,
    period: int = 20
) -> float:
    \"\"\"
    计算Amihud非流动性指标
    
    参数:
        daily_returns: 日收益率
        daily_amount: 日成交额
        period: 计算周期
    
    返回:
        |r| / amount 的均值
    \"\"\"
    if len(daily_returns) < period:
        return np.nan
    
    illiq = abs(daily_returns.iloc[-period:]) / (daily_amount.iloc[-period:] + 1)
    return illiq.mean()
""",
        parameters={"period": 20},
        references=["Amihud, Y. (2002). Illiquidity and Stock Returns"]
    ),
}


def get_factor_definition(factor_id: str) -> Optional[FactorDefinition]:
    """获取因子定义"""
    return FACTOR_DEFINITIONS.get(factor_id)


def list_factor_definitions() -> List[FactorDefinition]:
    """列出所有因子定义"""
    return list(FACTOR_DEFINITIONS.values())
