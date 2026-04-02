"""
Pydantic Models for API
"""

from pydantic import BaseModel
from typing import List, Optional


class FactorTestRequest(BaseModel):
    """因子测试请求"""
    factor_type: str
    start_date: str
    end_date: str
    quantiles: int = 5
    forward_period: int = 5
    industry_neutral: bool = False
    market_cap_neutral: bool = False


class BacktestRequest(BaseModel):
    """回测请求"""
    factors: List[str]
    weight_method: str = "equal"
    rebalance_freq: str = "monthly"
    top_n: int = 50
    commission: float = 0.001
    slippage: float = 0.001
    start_date: str
    end_date: str
