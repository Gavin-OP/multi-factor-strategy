"""
API Schemas - 请求/响应格式
"""

from pydantic import BaseModel
from typing import List, Optional, Dict


# ========== Factor Schemas ==========

class FactorTestRequest(BaseModel):
    """因子测试请求"""
    factor_type: str
    start_date: str = "20230101"
    end_date: str = "20231231"
    quantiles: int = 5
    forward_period: int = 5
    industry_neutral: bool = False
    market_cap_neutral: bool = False


class FactorTestResponse(BaseModel):
    """因子测试响应"""
    name: str
    category: str
    icMean: float
    icStd: float
    icir: float
    icTStat: float
    icPositiveRatio: float
    icSignificantRatio: float
    spreadReturn: float
    spreadSharpe: float
    monotonicity: float
    halfLife: int
    turnover: float
    grade: str
    score: float
    isEffective: bool
    strengths: List[str]
    weaknesses: List[str]
    quantileReturns: List[Dict]
    icSeries: List[Dict]
    decayCurve: List[Dict]
    dataSource: str = "tushare"


# ========== Backtest Schemas ==========

class BacktestRequest(BaseModel):
    """回测请求"""
    factors: List[str]
    weight_method: str = "equal"
    rebalance_freq: str = "monthly"
    top_n: int = 50
    commission: float = 0.001
    slippage: float = 0.001
    start_date: str = "20230101"
    end_date: str = "20231231"


class BacktestResponse(BaseModel):
    """回测响应"""
    totalReturn: float
    annualReturn: float
    excessReturn: float
    annualVolatility: float
    sharpeRatio: float
    informationRatio: float
    maxDrawdown: float
    winRate: float
    profitLossRatio: float
    beta: float
    alpha: float
    trackingError: float
    downsideRisk: float
    avgHoldingPeriod: int
    turnoverRate: float
    navCurve: List[Dict]
    drawdownCurve: List[Dict]
    monthlyReturns: List[Dict]
    yearlyReturns: List[Dict]
    holdings: List[Dict]
    dataSource: str = "tushare"


# ========== Data Schemas ==========

class StockListResponse(BaseModel):
    """股票列表响应"""
    data: List[Dict]
    total: int
    source: str
