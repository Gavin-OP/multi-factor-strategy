"""
Risk Models
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RiskMetric:
    """风险指标"""
    var_95: float = 0.0            # 95% VaR
    cvar_95: float = 0.0           # 95% CVaR
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown: float = 0.0
    volatility: float = 0.0
    downside_volatility: float = 0.0


@dataclass
class Exposure:
    """敞口"""
    category: str                  # industry/style
    name: str                      # 名称
    value: float                   # 敞口值
    benchmark_value: float = 0.0  # 基准值
    active_value: float = 0.0     # 主动敞口


@dataclass
class RiskReport:
    """风险报告"""
    date: str
    metrics: RiskMetric = field(default_factory=RiskMetric)
    industry_exposures: List[Exposure] = field(default_factory=list)
    style_exposures: List[Exposure] = field(default_factory=list)
